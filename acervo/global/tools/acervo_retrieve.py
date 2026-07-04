#!/usr/bin/env python3
"""Acervo hybrid retrieval + context packing (07-retrieval-policy.md, Phase 3).

Implements `retrieve_context`/`pack_context` per 07 §3 with the routing table
of 07 §2, catalog-primary per H2 (11-hypotheses.md, resolved 2026-07-04):
catalog metadata filters + FTS5-backed lexical search are the primary surface;
the semantic index (Hindsight) is an OPTIONAL supplement (`with_hindsight`),
always post-filtered by scope, never over `sensitivity: restricted`, and its
hits never outrank an exact metadata or lexical hit.

Reads only Plane 2 (catalog.sqlite, disposable — `acervoctl reindex`) plus the
canonical files of the packed items (Plane 1 always wins over index text).

Scope doctrine (P6, H5): every query runs scoped to
`micro/<scope>/ + shared/ + global/`; extra scopes only via `allow_scopes`
(explicit cross-scope request). `sensitivity: restricted` objects surface only
in queries whose PRIMARY scope is their home scope — never via allow_scopes,
never via bridges, never via Hindsight. Cross-scope synthesis happens through
declared bridges: `relates_to`/`canonical_from` links of `shared/` objects are
expanded one hop (never to restricted targets).

Abstention (EX-49 applied to recall): a lexical candidate must match >= 2
distinct query terms OR 1 rare non-numeric term (document frequency <=
RARE_DF_MAX); if nothing survives the floors and filters, retrieve() returns
`{"found": false, "message": "não há registro no Acervo sobre..."}` instead of
improvising.

CLI: exposed as `acervoctl retrieve` (scripts/acervoctl.py); a minimal
argparse main lives here for direct use.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sqlite3
import sys
import unicodedata
from datetime import date, timedelta
from pathlib import Path
from typing import Any

_TOOLS_DIR = Path(__file__).resolve().parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

from acervo_catalog import catalog_path, resolve_acervo_root  # noqa: E402
from acervo_hindsight_index import split_frontmatter  # noqa: E402

ROUTES = (
    "literal", "entity", "temporal", "prospective",
    "factual", "semantic", "procedural", "continuity",
)

DEFAULT_BUDGET_TOKENS = 6000   # drafting/execution tier (07 §4)
DEFAULT_K = 5                  # pointers before payloads: 1–5 canonical files
CHARS_PER_TOKEN = 4            # token estimate = chars/4 (07 §3 contract)

RARE_DF_MAX = 5                # term is "rare" if it appears in <= 5 files
MIN_DISTINCT_TERMS = 2         # non-rare floor: >= 2 distinct term hits
STALE_VOLATIL_DAYS = 90        # volátil older than 90d => staleness flag

# Authority ladder (07 §3): contract > decision > knowledge > episode > reflection.
AUTHORITY_BONUS: dict[str | None, float] = {
    "contract": 1.5, "decision": 1.0, "knowledge": 0.5, "context": 0.5,
    "workflow": 0.5, "intention": 0.5, "conflict": 0.5, "template": 0.25,
    "episode": 0.25, "entity": 0.0, "persona": 0.0, "reflection": 0.0,
}
RARE_TERM_BONUS = 0.25

# Route-anchored scores: metadata hits outrank lexical scores (which top out
# around len(terms) + bonuses), and Hindsight never outranks either.
SCORE_ENTITY_PAGE = 10.0
SCORE_CONTEXT_HEAD = 10.0
SCORE_INTENTION_ACTIVE = 10.0
SCORE_EPISODE_CONTINUITY = 9.0
SCORE_INTENTION_ARCHIVED = 8.0
SCORE_CONFLICT_OPEN = 7.0
SCORE_INTENTION_CONTINUITY = 7.0
SCORE_EPISODE_OF_ENTITY = 6.0
SCORE_HINDSIGHT = 0.5
RANK_DECAY = 0.1               # ordering decrement inside a metadata series
BRIDGE_DECAY = 0.1             # one-hop bridge target ranks just below source

STOPWORDS = {
    "a", "à", "às", "ao", "aos", "as", "com", "como", "da", "das", "de", "diga",
    "do", "dos", "e", "é", "ela", "ele", "em", "entre", "era", "essa", "esse",
    "esta", "está", "estão", "eu", "foi", "for", "hoje", "isso", "isto", "já",
    "mais", "mas", "me", "na", "nas", "não", "no", "nos", "nós", "nossa",
    "nosso", "o", "onde", "os", "ou", "para", "pela", "pelo", "por", "porque",
    "qual", "quais", "quando", "quanto", "quantos", "que", "quem", "se", "sem",
    "ser", "seu", "sua", "sim", "só", "sobre", "são", "também", "tem", "têm",
    "um", "uma", "vez",
}

PT_MONTHS = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3, "abril": 4, "maio": 5,
    "junho": 6, "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10,
    "novembro": 11, "dezembro": 12,
}
MONTH_RE = re.compile(
    r"\b(" + "|".join(PT_MONTHS) + r")\b(?:\s+de)?\s+(\d{4})", re.IGNORECASE
)
ISO_DATE_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
TOKEN_RE = re.compile(r"[0-9A-Za-zÀ-ÖØ-öø-ÿ][0-9A-Za-zÀ-ÖØ-öø-ÿ-]*")

# --- route heuristics -------------------------------------------------------
QUOTED_RE = re.compile(r"[\"'“‘]([^\"'“”‘’\n]{3,80})[\"'”’]")
LITERAL_HINT_RE = re.compile(r"termo exato|exatamente como|literalmente", re.IGNORECASE)
CONTINUITY_RE = re.compile(
    r"onde (paramos|estávamos|estavamos|parei)|em que pé|o que aconteceu por último"
    r"|retomar (o|a|de onde)|continuar de onde", re.IGNORECASE)
PROSPECTIVE_RE = re.compile(
    r"promet|pendênc|pendenc|\bprazo\b|compromisso|combinamos|deadline"
    r"|até quando|o que (devo|preciso) (enviar|entregar|fazer)", re.IGNORECASE)
# Completion questions ("o seguro foi renovado?") are prospective — they ask
# after the fate of a commitment — unless the query asks for rationale.
DONE_QUESTION_RE = re.compile(r"\bfoi\s+\w+[ai]d[oa]s?\b.*\?", re.IGNORECASE | re.DOTALL)
RATIONALE_RE = re.compile(r"\bpor\s*qu[eê]\b", re.IGNORECASE)
TEMPORAL_RE = re.compile(
    r"\bas of\b|acreditávamos|acreditavamos|naquela época|naquela epoca"
    r"|\b(era|eram|custava|valia|cobrávamos|cobravamos|praticávamos|praticavamos)\b"
    r"|antes d[aeo]", re.IGNORECASE)
PROCEDURAL_RE = re.compile(
    r"como (se )?(fazer|faço|faco|fazemos|executar|rodar)|passo a passo"
    r"|procedimento|checklist|\bsop\b|workflow", re.IGNORECASE)
ENTITY_RE = re.compile(r"\bquem\b|\bde quem\b|\bcom quem\b", re.IGNORECASE)


# ---------------------------------------------------------------- text utils

def fold(text: str) -> str:
    """Lowercase + strip diacritics (mirrors FTS5 unicode61 folding)."""
    norm = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in norm if not unicodedata.combining(c))


def query_terms(query: str) -> list[str]:
    terms: list[str] = []
    for token in TOKEN_RE.findall(query):
        token = token.strip("-")
        if len(token) < 3 or token.lower() in STOPWORDS or fold(token) in STOPWORDS:
            continue
        folded = fold(token)
        if folded not in terms:
            terms.append(folded)
    return terms


def term_pattern(term: str) -> re.Pattern[str]:
    return re.compile(r"(?<![0-9a-z])" + re.escape(term) + r"(?![0-9a-z])")


def query_date(query: str) -> str | None:
    """ISO date referenced by the query ('em março de 2026' → mid-month)."""
    m = MONTH_RE.search(query)
    if m:
        return date(int(m.group(2)), PT_MONTHS[m.group(1).lower()], 15).isoformat()
    m = ISO_DATE_RE.search(query)
    if m:
        return m.group(0)
    return None


def estimate_tokens(text: str) -> int:
    return max(1, math.ceil(len(text) / CHARS_PER_TOKEN))


# ---------------------------------------------------------------- classifier

def classify_query(task_text: str, hints: dict[str, Any] | None = None,
                   aliases: dict[str, str] | None = None) -> str:
    """Route a task by its shape (07 §2). `aliases` maps folded entity alias →
    slug (see Retriever.aliases); `hints` may force a route via {"route": ...}."""
    if hints and hints.get("route") in ROUTES:
        return str(hints["route"])
    text = task_text.strip()
    folded = fold(text)

    if QUOTED_RE.search(text) or LITERAL_HINT_RE.search(text):
        return "literal"
    if CONTINUITY_RE.search(text):
        return "continuity"
    rationale = bool(RATIONALE_RE.search(text))
    if not rationale and (PROSPECTIVE_RE.search(text) or DONE_QUESTION_RE.search(text)):
        return "prospective"
    if MONTH_RE.search(text) or ISO_DATE_RE.search(text) or TEMPORAL_RE.search(text):
        return "temporal"
    if PROCEDURAL_RE.search(text):
        return "procedural"
    if ENTITY_RE.search(text):
        return "entity"
    if aliases and _alias_hits(folded, aliases):
        return "entity"
    if len(query_terms(text)) <= 1:
        return "semantic"  # vague/associative: no lexical anchor to grip
    return "factual"


def _alias_hits(folded_query: str, aliases: dict[str, str]) -> list[str]:
    slugs: list[str] = []
    for alias, slug in aliases.items():
        if len(alias) < 4:
            continue
        if term_pattern(alias).search(folded_query) and slug not in slugs:
            slugs.append(slug)
    return slugs


# ---------------------------------------------------------------- retriever

class Retriever:
    """Catalog-primary retrieval over one Acervo root (catalog must exist)."""

    def __init__(self, acervo_root: str | Path | None = None, today: date | None = None) -> None:
        self.acervo = resolve_acervo_root(acervo_root)
        self.today = today or date.today()
        db = catalog_path(self.acervo)
        if not db.exists():
            raise RuntimeError(f"Catalog not found: {db} (run `acervoctl reindex` first)")
        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        try:
            self.objects: dict[str, dict[str, Any]] = {
                row["path"]: dict(row) for row in conn.execute("SELECT * FROM objects")
            }
            self.searchable: dict[str, str] = {}
            for row in conn.execute("SELECT path, title, description, body FROM fts"):
                self.searchable[row["path"]] = fold(
                    " ".join(x or "" for x in (row["title"], row["description"], row["body"]))
                )
            self.links: list[dict[str, str]] = [
                dict(row) for row in conn.execute("SELECT src_path, kind, target FROM links")
            ]
        finally:
            conn.close()
        self._df_cache: dict[str, int] = {}
        self.aliases = self._load_aliases()

    # -------------------------------------------------------------- corpus

    def _load_aliases(self) -> dict[str, str]:
        """Folded alias → entity slug, from catalog entities + their frontmatter."""
        aliases: dict[str, str] = {}
        for rel, row in self.objects.items():
            if row.get("type") != "entity":
                continue
            slug = Path(rel).stem
            title = str(row.get("title") or "")
            name = title.split("—")[0].strip()
            candidates = [name] if name else []
            path = self.acervo / rel
            if path.is_file():
                try:
                    fm, _ = split_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
                    candidates.extend(str(a) for a in (fm.get("aliases") or []))
                except Exception:
                    pass
            for alias in candidates:
                folded = fold(alias.strip())
                if len(folded) >= 4:
                    aliases.setdefault(folded, slug)
        return aliases

    def doc_frequency(self, term: str) -> int:
        if term not in self._df_cache:
            pat = term_pattern(term)
            self._df_cache[term] = sum(1 for text in self.searchable.values() if pat.search(text))
        return self._df_cache[term]

    def matched_terms(self, rel: str, terms: list[str]) -> list[str]:
        text = self.searchable.get(rel, "")
        return [t for t in terms if term_pattern(t).search(text)]

    def _is_rare(self, term: str) -> bool:
        # Bare numbers (years) are too weak to count as rare evidence.
        return not term.isdigit() and 0 < self.doc_frequency(term) <= RARE_DF_MAX

    def above_floor(self, matched: list[str]) -> bool:
        if len(matched) >= MIN_DISTINCT_TERMS:
            return True
        return any(self._is_rare(t) for t in matched)

    # -------------------------------------------------------------- scoping

    @staticmethod
    def allowed_prefixes(scope: str, allow_scopes: list[str] | None = None) -> tuple[str, ...]:
        """Scope resolution (P6): the microverso + shared + global; extra
        microversos only via explicit allow_scopes."""
        prefixes = ["shared/", "global/"] if scope == "global" else [f"micro/{scope}/", "shared/", "global/"]
        for extra in allow_scopes or []:
            prefix = f"micro/{extra}/"
            if prefix not in prefixes:
                prefixes.append(prefix)
        return tuple(prefixes)

    def _visible(self, rel: str, scope: str, allow_scopes: list[str] | None,
                 via_bridge: bool = False) -> bool:
        row = self.objects.get(rel)
        if row is None:
            return False
        if not via_bridge and not rel.startswith(self.allowed_prefixes(scope, allow_scopes)):
            return False
        if (row.get("sensitivity") or "").strip() == "restricted":
            # Restricted objects never leave their home scope — not via
            # allow_scopes, not via bridges (H2 leak finding; H5).
            home_ok = rel.startswith(f"micro/{scope}/") or (
                scope == "global" and row.get("layer") == "global"
            )
            return home_ok and not via_bridge
        return True

    def _passes_lifecycle(self, row: dict[str, Any], statuses: set[str], as_of: str | None) -> bool:
        if (row.get("status") or "active") not in statuses:
            return False
        if as_of:
            if row.get("valid_from") and as_of < row["valid_from"]:
                return False
            if row.get("valid_until") and as_of > row["valid_until"]:
                return False
        return True

    # -------------------------------------------------------------- surfaces

    def _lexical_search(self, terms: list[str], scope: str, allow_scopes: list[str] | None,
                        statuses: set[str], as_of: str | None) -> dict[str, float]:
        """FTS5-backed lexical scan (catalog rung fused with the grep rung: the
        fts table carries title/description/body). Floors applied here."""
        scored: dict[str, float] = {}
        for rel in self.searchable:
            if not self._visible(rel, scope, allow_scopes):
                continue
            row = self.objects[rel]
            if not self._passes_lifecycle(row, statuses, as_of):
                continue
            matched = self.matched_terms(rel, terms)
            if not matched or not self.above_floor(matched):
                continue
            rare = sum(1 for t in matched if self._is_rare(t))
            hits = sum(len(term_pattern(t).findall(self.searchable[rel])) for t in matched)
            scored[rel] = (
                len(matched) + RARE_TERM_BONUS * rare + 0.01 * min(hits, 8)
                + AUTHORITY_BONUS.get(row.get("type"), 0.0)
            )
        return scored

    def _bridge_expansion(self, scored: dict[str, float], scope: str,
                          allow_scopes: list[str] | None, statuses: set[str],
                          as_of: str | None) -> dict[str, float]:
        """One hop through declared bridges: relates_to/canonical_from links of
        shared/ candidates (06 §6 cross-refs). Never to restricted targets."""
        extra: dict[str, float] = {}
        shared_srcs = {rel for rel in scored if rel.startswith("shared/")}
        for link in self.links:
            if link["src_path"] not in shared_srcs or link["kind"] not in ("relates_to", "canonical_from"):
                continue
            target = link["target"].strip()
            if target not in self.objects or target in scored:
                continue
            row = self.objects[target]
            if not self._visible(target, scope, allow_scopes, via_bridge=True):
                continue
            if not self._passes_lifecycle(row, statuses, as_of):
                continue
            score = scored[link["src_path"]] - BRIDGE_DECAY
            if score > extra.get(target, 0.0):
                extra[target] = score
        return extra

    def _entities_of(self, rel: str) -> list[str]:
        return [l["target"] for l in self.links if l["src_path"] == rel and l["kind"] == "entity"]

    def _entity_page(self, slug: str) -> str | None:
        for rel, row in self.objects.items():
            if row.get("type") == "entity" and Path(rel).stem == slug:
                return rel
        return None

    def _episodes_of_entity(self, slug: str, scope: str, allow_scopes: list[str] | None) -> list[str]:
        episodes = []
        for link in self.links:
            if link["kind"] != "entity" or link["target"] != slug:
                continue
            rel = link["src_path"]
            row = self.objects.get(rel)
            if row and row.get("type") == "episode" and self._visible(rel, scope, allow_scopes):
                episodes.append(rel)
        return self._time_desc(episodes)

    def _time_desc(self, rels: list[str]) -> list[str]:
        def key(rel: str) -> str:
            row = self.objects[rel]
            return str(row.get("observed_at") or row.get("created_at") or "")
        return sorted(set(rels), key=key, reverse=True)

    def _intentions(self, scope: str, allow_scopes: list[str] | None,
                    statuses: set[str]) -> list[str]:
        rels = [
            rel for rel, row in self.objects.items()
            if row.get("type") == "intention"
            and (row.get("status") or "active") in statuses
            and self._visible(rel, scope, allow_scopes)
        ]
        return sorted(rels, key=lambda r: str(self.objects[r].get("valid_until") or "") or self._due(r) or "9999")

    def _due(self, rel: str) -> str | None:
        """`due` is not a catalog column; read it lazily from frontmatter."""
        path = self.acervo / rel
        try:
            fm, _ = split_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
            value = fm.get("due")
            return str(value) if value else None
        except Exception:
            return None

    def _hindsight_supplement(self, query: str, scope: str, allow_scopes: list[str] | None,
                              notes: list[str]) -> dict[str, float]:
        """Optional semantic rung (H2: supplement only, default OFF). Post-
        filtered by scope; restricted objects are never surfaced through it."""
        try:
            from acervo_hindsight_index import load_hindsight_config, make_client
            config = load_hindsight_config()
            client = make_client(config)
            bank_id = os.environ.get("HINDSIGHT_BANK_ID") or config.get("bank_id") or "exocortex"
            response = client.recall(bank_id=bank_id, query=query)
        except Exception as exc:
            notes.append(f"hindsight indisponível (rung degradado para catalog/grep): {exc}")
            return {}
        scored: dict[str, float] = {}
        rank = 0
        for result in getattr(response, "results", []) or []:
            rel = None
            metadata = getattr(result, "metadata", None) or {}
            if metadata.get("path"):
                rel = metadata["path"]
            else:
                doc_id = getattr(result, "document_id", "") or ""
                if doc_id.startswith("acervo:"):
                    rel = doc_id[len("acervo:"):]
                else:
                    m = re.search(r"path:\s*(\S+\.md)", getattr(result, "text", "") or "")
                    rel = m.group(1) if m else None
            if not rel or rel in scored:
                continue
            row = self.objects.get(rel)
            if row is None or (row.get("sensitivity") or "").strip() == "restricted":
                continue
            if not self._visible(rel, scope, allow_scopes):
                continue
            scored[rel] = SCORE_HINDSIGHT - RANK_DECAY * 0.1 * rank
            rank += 1
        notes.append(f"hindsight supplement: {len(scored)} ponteiro(s) pós-filtrados por escopo")
        return scored

    # -------------------------------------------------------------- routes

    def _route_candidates(self, route: str, query: str, scope: str,
                          allow_scopes: list[str] | None, with_hindsight: bool,
                          notes: list[str]) -> tuple[dict[str, float], dict[str, str], str | None]:
        """Returns (path → score, path → source rung, as_of)."""
        terms = query_terms(query)
        today_iso = self.today.isoformat()
        scored: dict[str, float] = {}
        source: dict[str, str] = {}
        as_of: str | None = None

        def merge(extra: dict[str, float], rung: str) -> None:
            for rel, score in extra.items():
                if score > scored.get(rel, float("-inf")):
                    scored[rel] = score
                    source[rel] = rung

        if route == "literal":
            m = QUOTED_RE.search(query)
            phrase = fold(m.group(1)) if m else " ".join(terms)
            for rel, text in self.searchable.items():
                if phrase and phrase in text and self._visible(rel, scope, allow_scopes):
                    merge({rel: 5.0 + 0.1 * min(text.count(phrase), 5)}, "grep-exact")
            return scored, source, None

        if route == "temporal":
            as_of = query_date(query)
            statuses = {"active", "superseded"}  # results labeled HISTORICAL in pack
            merge(self._lexical_search(terms, scope, allow_scopes, statuses, as_of), "catalog+fts")
            merge(self._bridge_expansion(scored, scope, allow_scopes, statuses, as_of), "shared-bridge")
            return scored, source, as_of

        if route == "prospective":
            for i, rel in enumerate(self._intentions(scope, allow_scopes, {"active"})):
                merge({rel: SCORE_INTENTION_ACTIVE - RANK_DECAY * i}, "intention-open")
            for i, rel in enumerate(self._intentions(scope, allow_scopes, {"archived", "done"})):
                if self.matched_terms(rel, terms):  # closed commitments only on topic match
                    merge({rel: SCORE_INTENTION_ARCHIVED - RANK_DECAY * i}, "intention-archived")
            # Open conflicts are the blockers of open commitments.
            for rel, row in self.objects.items():
                if (row.get("type") == "conflict" and (row.get("status") or "active") == "active"
                        and self._visible(rel, scope, allow_scopes) and self.matched_terms(rel, terms)):
                    merge({rel: SCORE_CONFLICT_OPEN}, "conflict-open")
            # NOTE: kanban (_tasks/) is not catalog-indexed yet — Phase 4 wires it in.
            merge(self._lexical_search(terms, scope, allow_scopes, {"active"}, today_iso), "catalog+fts")
            return scored, source, None

        if route == "continuity":
            head = f"micro/{scope}/context/current-state.md"
            if head in self.objects and self._visible(head, scope, allow_scopes):
                merge({head: SCORE_CONTEXT_HEAD}, "context-head")
            episodes = self._time_desc([
                rel for rel, row in self.objects.items()
                if row.get("type") == "episode" and self._visible(rel, scope, allow_scopes)
            ])
            for i, rel in enumerate(episodes):
                merge({rel: SCORE_EPISODE_CONTINUITY - RANK_DECAY * i}, "episode-recent")
            for i, rel in enumerate(self._intentions(scope, allow_scopes, {"active"})):
                merge({rel: SCORE_INTENTION_CONTINUITY - RANK_DECAY * i}, "intention-open")
            merge(self._lexical_search(terms, scope, allow_scopes, {"active"}, today_iso), "catalog+fts")
            return scored, source, None

        if route == "entity":
            slugs = _alias_hits(fold(query), self.aliases)
            lexical = self._lexical_search(terms, scope, allow_scopes, {"active"}, today_iso)
            merge(lexical, "catalog+fts")
            merge(self._bridge_expansion(scored, scope, allow_scopes, {"active"}, today_iso), "shared-bridge")
            if slugs:
                for slug in slugs:
                    page = self._entity_page(slug)
                    if page and self._visible(page, scope, allow_scopes):
                        merge({page: SCORE_ENTITY_PAGE}, "entity-page")
                    for i, rel in enumerate(self._episodes_of_entity(slug, scope, allow_scopes)):
                        merge({rel: SCORE_EPISODE_OF_ENTITY - RANK_DECAY * i}, "entity-episode")
            else:
                # "Quem ...?" without a known alias: pull the entity pages
                # linked (entities:) from the best lexical candidates.
                top = sorted(lexical, key=lambda r: -lexical[r])[:3]
                for rel in top:
                    for slug in self._entities_of(rel):
                        page = self._entity_page(slug)
                        if page and self._visible(page, scope, allow_scopes):
                            merge({page: lexical[rel] - BRIDGE_DECAY}, "entity-of-candidate")
            return scored, source, None

        # factual | semantic | procedural — catalog FTS + grep, active & valid-now
        merge(self._lexical_search(terms, scope, allow_scopes, {"active"}, today_iso), "catalog+fts")
        merge(self._bridge_expansion(scored, scope, allow_scopes, {"active"}, today_iso), "shared-bridge")
        if with_hindsight and (route == "semantic" or len(scored) < 2):
            merge(self._hindsight_supplement(query, scope, allow_scopes, notes), "hindsight")
        return scored, source, None

    # -------------------------------------------------------------- items

    def _flags(self, row: dict[str, Any]) -> list[str]:
        flags: list[str] = []
        today_iso = self.today.isoformat()
        review_after = row.get("review_after")
        stale_reasons = []
        if review_after and str(review_after) < today_iso:
            stale_reasons.append("review_after vencido")
        if (row.get("class") or "") == "volátil":
            anchor = str(row.get("observed_at") or row.get("created_at") or "")[:10]
            if anchor and anchor < (self.today - timedelta(days=STALE_VOLATIL_DAYS)).isoformat():
                stale_reasons.append(f"volátil há mais de {STALE_VOLATIL_DAYS}d")
        if stale_reasons:
            flags.append("⚠ STALE: " + "; ".join(stale_reasons))
        if (row.get("status") or "active") != "active":
            flags.append("⏳ HISTORICAL")
        disputes = [
            l["target"] for l in self.links
            if l["src_path"] == row["path"] and l["kind"] == "disputed_by"
        ]
        if disputes:
            flags.append("⚠ DISPUTED: ver " + ", ".join(disputes))
        return flags

    def _make_item(self, rel: str, score: float, rung: str, role: str) -> dict[str, Any]:
        row = self.objects[rel]
        scope_label = row.get("microverso") or row.get("layer") or "-"
        header = "[{}|{}|{}|{}|{}] {}".format(
            row.get("type") or "-", row.get("epistemic") or "-",
            row.get("confidence") or "-", row.get("status") or "active",
            scope_label, rel,
        )
        flags = self._flags(row)
        if flags:
            header += "  " + "  ".join(flags)
        path = self.acervo / rel
        try:  # Plane 1 always wins over index text (07 §3)
            _, content = split_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
            content = content.strip()
        except Exception:
            content = row.get("description") or ""
        return {
            "path": rel,
            "role": role,
            "header": header,
            "content": content,
            "description": row.get("description") or "",
            "score": round(score, 3),
            "source": rung,
            "stub": False,
            "tokens_est": estimate_tokens(header + "\n" + content),
        }

    # -------------------------------------------------------------- retrieve

    def retrieve(self, query: str, scope: str, budget_tokens: int = DEFAULT_BUDGET_TOKENS,
                 k: int = DEFAULT_K, allow_scopes: list[str] | None = None,
                 with_hindsight: bool = False, hints: dict[str, Any] | None = None) -> dict[str, Any]:
        notes: list[str] = []
        route = classify_query(query, hints=hints, aliases=self.aliases)
        scored, source, as_of = self._route_candidates(
            route, query, scope, allow_scopes, with_hindsight, notes
        )
        ranked = sorted(scored, key=lambda r: (-scored[r], r))[:k]

        result: dict[str, Any] = {
            "query": query,
            "route": route,
            "scope": scope,
            "allow_scopes": list(allow_scopes or []),
            "as_of": as_of,
            "k": k,
            "budget_tokens": budget_tokens,
            "with_hindsight": with_hindsight,
            "notes": notes,
        }
        if not ranked:
            result.update({
                "found": False,
                "message": f"não há registro no Acervo sobre: {query}",
                "view": [], "items": [], "citations": [], "total_tokens": 0,
            })
            return result

        items = [self._make_item(rel, scored[rel], source[rel], "result") for rel in ranked]

        # Scope view (07 doctrine 4): context head + index, charged to budget.
        view: list[dict[str, Any]] = []
        if scope != "global":
            for view_rel in (f"micro/{scope}/context/current-state.md", f"micro/{scope}/_meta/index.md"):
                if view_rel in self.objects and view_rel not in ranked:
                    view.append(self._make_item(view_rel, 0.0, "scope-view", "view"))

        packed, total = pack(view + items, budget_tokens)
        result.update({
            "found": True,
            "view": [it for it in packed if it["role"] == "view"],
            "items": [it for it in packed if it["role"] == "result"],
            "citations": [f"Acervo: {it['path']}" for it in packed if it["role"] == "result"],
            "total_tokens": total,
        })
        return result


# ---------------------------------------------------------------- packing

def pack(items: list[dict[str, Any]], budget_tokens: int) -> tuple[list[dict[str, Any]], int]:
    """pack_context per 07 §3: U-curve order (best first, runner-up last),
    budget overflow degrades the lowest-ranked items to pointer stubs (header +
    description) — never a silent drop, never over budget."""
    view = [it for it in items if it.get("role") == "view"]
    results = [it for it in items if it.get("role") != "view"]
    if len(results) >= 3:  # lost-in-the-middle: second-best goes last
        ordered = [results[0]] + results[2:] + [results[1]]
    else:
        ordered = results
    packed = view + ordered

    def total_tokens() -> int:
        return sum(it["tokens_est"] for it in packed)

    def degrade(item: dict[str, Any]) -> None:
        item["stub"] = True
        item["content"] = None
        item["tokens_est"] = estimate_tokens(
            item["header"] + "\n" + (item["description"] or "") + " [stub: ler arquivo sob demanda]"
        )

    # View items degrade last (they are the scope's orientation surface).
    degradable = sorted(
        [it for it in packed], key=lambda it: (it.get("role") == "view", it["score"])
    )
    for item in degradable:
        if total_tokens() <= budget_tokens:
            break
        if not item["stub"]:
            degrade(item)
    # Still over budget with everything stubbed: drop lowest-ranked stubs
    # (their paths remain retrievable next turn; budget is a hard ceiling).
    while total_tokens() > budget_tokens and len(packed) > 1:
        victim = min(packed, key=lambda it: (it.get("role") != "view", it["score"]))
        packed.remove(victim)
    return packed, total_tokens()


# ---------------------------------------------------------------- API

def retrieve(query: str, scope: str, budget_tokens: int = DEFAULT_BUDGET_TOKENS,
             acervo_root: str | Path | None = None, k: int = DEFAULT_K,
             allow_scopes: list[str] | None = None, with_hindsight: bool = False,
             hints: dict[str, Any] | None = None) -> dict[str, Any]:
    """One-shot convenience wrapper around Retriever.retrieve()."""
    return Retriever(acervo_root).retrieve(
        query, scope, budget_tokens=budget_tokens, k=k,
        allow_scopes=allow_scopes, with_hindsight=with_hindsight, hints=hints,
    )


# ---------------------------------------------------------------- CLI

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hybrid retrieval over the Acervo (07-retrieval-policy)")
    parser.add_argument("--acervo", help="Acervo root (default: $ACERVO or standard fallbacks)")
    parser.add_argument("--query", required=True)
    parser.add_argument("--scope", required=True, help="Microverso slug (or 'global')")
    parser.add_argument("--budget", type=int, default=DEFAULT_BUDGET_TOKENS)
    parser.add_argument("--k", type=int, default=DEFAULT_K)
    parser.add_argument("--allow-scope", action="append", default=[],
                        help="Extra microverso(s) for explicit cross-scope retrieval (repeatable)")
    parser.add_argument("--with-hindsight", action="store_true",
                        help="Enable the optional semantic supplement (H2: default OFF)")
    args = parser.parse_args(argv)

    payload = retrieve(
        args.query, args.scope, budget_tokens=args.budget, acervo_root=args.acervo,
        k=args.k, allow_scopes=args.allow_scope, with_hindsight=args.with_hindsight,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
