#!/usr/bin/env python3
"""Retrieval-eval harness for the memory-v2 golden set (10-evaluation.md §1).

RETRIEVAL-ONLY: no LLM answers are generated. Each strategy returns a ranked
list of fixture-relative paths (top-k=5) and is scored on whether the right
FILES surface — recall@5, precision@5, contamination, abstention, token cost.

Strategies (H2 in 11-hypotheses.md — agentic+lexical vs semantic index):
  catalog   — catalog.sqlite FTS5 (+ scope/status/valid-window filters) merged
              with a ripgrep-style lexical fallback over fixture bodies
  hindsight — hindsight_recall on the DEDICATED bank `eval-fixture` (AcervoIndex
              pointers), same scope filter applied post-hoc
  hybrid    — union of both; exact-path agreement first, then catalog rank,
              then hindsight rank
  production— the Phase 3 library (acervo_retrieve.retrieve): routed hybrid
              retrieval per 07-retrieval-policy, called in-process with each
              question's scope; abstention == found=False

The catalog is built over a COPY of the fixture acervo inside --workdir so no
derived state ever lands inside the fixture. The Hindsight bank `eval-fixture`
is dropped and re-created on --reindex-hindsight; the production bank
`exocortex` is never written.

Abstention floors (operationalization):
  catalog   — a candidate is above the relevance floor iff it matches >= 2
              distinct query terms OR >= 1 rare term (document frequency in
              the fixture <= RARE_DF_MAX files). Below-floor candidates are
              dropped; abstention is correct iff nothing survives the floor
              plus scope/status/validity filters. This covers both FTS5 and
              the ripgrep fallback (an OR-match on common terms alone is not
              evidence).
  hindsight — the recall API returns no per-result score; anything returned at
              the default budget is treated as above ITS default floor.
              Abstention is correct iff zero AcervoIndex pointers resolve to a
              fixture path after the scope filter.
  hybrid    — abstains iff both components abstain.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import re
import shutil
import sqlite3
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception as exc:  # pragma: no cover
    raise SystemExit(f"PyYAML is required: {exc}")

EVAL_DIR = Path(__file__).resolve().parent
REPO = EVAL_DIR.parents[1]
TOOLS = REPO / "acervo" / "global" / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from acervo_catalog import build_catalog, catalog_path  # noqa: E402
from acervo_hindsight_index import (  # noqa: E402
    build_summary,
    load_hindsight_config,
    make_client,
    microverso_from_path,
    nature_from_path,
    sha256_file,
    split_frontmatter,
    tags_from_frontmatter,
    utc_now,
)

FIXTURE_ACERVO = EVAL_DIR / "fixture" / "acervo"
GOLDEN = EVAL_DIR / "golden" / "questions.yaml"
REPORT_DIR = EVAL_DIR / "report"

EVAL_BANK = "eval-fixture"
FORBIDDEN_BANK = "exocortex"  # never written by this harness
DOC_ID_PREFIX = "acervo-eval:"

TOP_K = 5
RARE_DF_MAX = 5  # a query term is "rare" if it appears in <= 5 fixture files
MIN_DISTINCT_TERMS = 2  # non-rare floor: at least 2 distinct term hits
H2_THRESHOLD_PTS = 5.0  # hybrid must beat catalog recall by > +5pts

# --- CI regression gate (10-evaluation.md §4) --------------------------------
# The gate runs the CATALOG strategy only: deterministic, offline (no Hindsight
# container, no LLM), so it is safe to block a merge on. Each overall metric is
# compared to a committed baseline; a drop of more than REGRESSION_PTS points in
# the "good" direction blocks the change (the spec's "any metric dropping > 10
# points blocks" rule). Contamination carries an extra HARD ceiling: the planted
# cross-scope traps must never leak, so any non-zero rate fails outright.
BASELINE_PATH = EVAL_DIR / "baseline.json"
REGRESSION_PTS = 10.0
GATE_STRATEGY = "catalog"
# (metric, direction, hard_max) — direction is which way is "better";
# hard_max (or None) is an absolute ceiling checked independently of the baseline.
GATE_METRICS = (
    ("recall", "higher", None),
    ("precision", "higher", None),
    ("abstention_accuracy", "higher", None),
    ("contamination_rate", "lower", 0.0),
)

CATEGORIES = (
    "factual", "decision_rationale", "temporal", "entity", "cross_scope_allowed",
    "cross_scope_trap", "prospective", "continuity", "literal", "absent",
)

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
TODAY_RE = re.compile(r"\b(hoje|vigente|atualmente|atual)\b", re.IGNORECASE)
TOKEN_RE = re.compile(r"[0-9A-Za-zÀ-ÖØ-öø-ÿ][0-9A-Za-zÀ-ÖØ-öø-ÿ-]*")


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
    """ISO date carried by the question ('em março de 2026' → mid-month; 'hoje' → today)."""
    m = MONTH_RE.search(query)
    if m:
        return date(int(m.group(2)), PT_MONTHS[m.group(1).lower()], 15).isoformat()
    if TODAY_RE.search(query):
        return date.today().isoformat()
    return None


# ---------------------------------------------------------------- questions

@dataclass
class Question:
    id: str
    category: str
    scope: str
    query: str
    expected_paths: list[str]
    forbidden_paths: list[str]
    forbidden_content: list[str]
    expected_answer_fragments: list[str]
    expects_abstention: bool


def load_questions(path: Path = GOLDEN) -> list[Question]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [Question(**q) for q in data["questions"]]


def allowed_prefixes(scope: str) -> tuple[str, ...]:
    """Scope filter: the question's microverso + shared + global (P6)."""
    if scope == "global":
        return ("global/", "shared/")
    return (f"micro/{scope}/", "shared/", "global/")


# ---------------------------------------------------------------- fixture corpus

@dataclass
class Doc:
    rel: str            # acervo-root-relative, e.g. micro/operacoes/knowledge/x.md
    searchable: str     # folded title + description + body
    chars: int          # raw file size in chars (token-cost proxy)


class Corpus:
    """Fixture bodies + per-term document frequency (for rare-term floor)."""

    def __init__(self, acervo: Path) -> None:
        self.docs: dict[str, Doc] = {}
        for path in sorted(acervo.rglob("*.md")):
            rel = path.relative_to(acervo).as_posix()
            if rel.startswith("global/tools/"):
                continue  # derived state in the workdir copy
            text = path.read_text(encoding="utf-8", errors="replace")
            fm, body = split_frontmatter(text)
            searchable = fold(
                " ".join(str(x) for x in (fm.get("title", ""), fm.get("description", ""), body))
            )
            self.docs[rel] = Doc(rel=rel, searchable=searchable, chars=len(text))

    def matched_terms(self, rel: str, terms: list[str]) -> list[str]:
        doc = self.docs.get(rel)
        if doc is None:
            return []
        return [t for t in terms if term_pattern(t).search(doc.searchable)]

    def doc_frequency(self, term: str) -> int:
        pat = term_pattern(term)
        return sum(1 for d in self.docs.values() if pat.search(d.searchable))

    def above_floor(self, rel: str, terms: list[str]) -> bool:
        matched = self.matched_terms(rel, terms)
        if not matched:
            return False
        if len(matched) >= MIN_DISTINCT_TERMS:
            return True
        return any(0 < self.doc_frequency(t) <= RARE_DF_MAX for t in matched)


# ---------------------------------------------------------------- catalog strategy

def build_workdir_catalog(workdir: Path) -> Path:
    """Copy fixture acervo into workdir and build catalog.sqlite over the copy."""
    acervo = workdir / "acervo"
    if acervo.exists():
        shutil.rmtree(acervo)
    shutil.copytree(FIXTURE_ACERVO, acervo)
    build_catalog(acervo)
    return acervo


class CatalogStrategy:
    """FTS5 over catalog.sqlite + ripgrep-style lexical fallback merge."""

    name = "catalog"

    def __init__(self, acervo: Path, corpus: Corpus) -> None:
        self.acervo = acervo
        self.corpus = corpus
        self.db = catalog_path(acervo)

    def _object_rows(self, conn: sqlite3.Connection) -> dict[str, dict[str, Any]]:
        return {
            row["path"]: dict(row)
            for row in conn.execute(
                "SELECT path, status, valid_from, valid_until FROM objects"
            ).fetchall()
        }

    def _fts_paths(self, conn: sqlite3.Connection, terms: list[str]) -> list[str]:
        if not terms:
            return []
        match = " OR ".join(f'"{t}"' for t in terms)
        rows = conn.execute(
            "SELECT path FROM fts WHERE fts MATCH ? ORDER BY rank LIMIT 50", (match,)
        ).fetchall()
        return [row["path"] for row in rows]

    def _rg_paths(self, terms: list[str]) -> list[str]:
        """Lexical fallback over fixture bodies: rank by distinct terms, then hits."""
        scored: list[tuple[int, int, str]] = []
        for rel, doc in self.corpus.docs.items():
            distinct = 0
            total = 0
            for term in terms:
                hits = len(term_pattern(term).findall(doc.searchable))
                if hits:
                    distinct += 1
                    total += hits
            if distinct:
                scored.append((-distinct, -total, rel))
        return [rel for _, _, rel in sorted(scored)]

    def retrieve(self, q: Question, k: int = TOP_K) -> list[str]:
        terms = query_terms(q.query)
        as_of = query_date(q.query)
        statuses = {"active", "superseded"} if q.category == "temporal" else {"active"}
        prefixes = allowed_prefixes(q.scope)

        conn = sqlite3.connect(self.db)
        conn.row_factory = sqlite3.Row
        try:
            objects = self._object_rows(conn)
            candidates = self._fts_paths(conn, terms)
        finally:
            conn.close()
        for rel in self._rg_paths(terms):  # fallback merge (P12 rung 3)
            if rel not in candidates:
                candidates.append(rel)

        out: list[str] = []
        for rel in candidates:
            row = objects.get(rel)
            if row is None or not rel.startswith(prefixes):
                continue
            if (row["status"] or "active") not in statuses:
                continue
            if as_of:
                if row["valid_from"] and as_of < row["valid_from"]:
                    continue
                if row["valid_until"] and as_of > row["valid_until"]:
                    continue
            if not self.corpus.above_floor(rel, terms):
                continue
            out.append(rel)
            if len(out) >= k:
                break
        return out


# ---------------------------------------------------------------- production strategy

class ProductionStrategy:
    """Phase 3 production path: acervo_retrieve.Retriever over the workdir
    catalog, one call per question with the question's scope (07 §3)."""

    name = "production"

    def __init__(self, acervo: Path) -> None:
        from acervo_retrieve import Retriever  # TOOLS already on sys.path

        self.retriever = Retriever(acervo)

    def retrieve(self, q: Question, k: int = TOP_K) -> list[str]:
        result = self.retriever.retrieve(q.query, scope=q.scope, k=k)
        if not result["found"]:
            return []  # explicit abstention ("não há registro no Acervo…")
        return [item["path"] for item in result["items"]][:k]


# ---------------------------------------------------------------- hindsight strategy

def build_pointer_payload(acervo: Path, path: Path) -> tuple[str, dict[str, str], list[str]]:
    """AcervoIndex-style pointer entry (mirrors acervo_hindsight_index.build_entry,
    but keeps the file's real status so superseded chains stay visible)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    fm, body = split_frontmatter(text)
    rel = path.relative_to(acervo).as_posix()
    micro = microverso_from_path(acervo, path)
    nature = nature_from_path(acervo, path, fm)
    digest = sha256_file(path)
    status = str(fm.get("status") or "active").strip()
    tags = tags_from_frontmatter(fm)
    payload = (
        "AcervoIndex\n"
        f"path: {rel}\n"
        f"microverso: {micro}\n"
        f"nature: {nature}\n"
        f"title: {str(fm.get('title') or path.stem).strip()}\n"
        f"tags: [{', '.join(tags)}]\n"
        f"class: {str(fm.get('class') or '').strip()}\n"
        f"status: {status}\n"
        f"sha256: {digest}\n"
        f"summary: {build_summary(fm, body)}"
    )
    metadata = {"path": rel, "microverso": micro, "nature": nature, "sha256": digest}
    retain_tags = ["acervo", "AcervoIndex", "eval-fixture", f"micro:{micro}", f"nature:{nature}"]
    return payload, metadata, retain_tags


@contextlib.contextmanager
def quiet_aiohttp():
    """Suppress 'Unclosed client session' noise from the generated client."""
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        yield
    for line in buf.getvalue().splitlines():
        if "Unclosed" not in line and line.strip():
            print(line, file=sys.stderr)


class HindsightEval:
    """Dedicated eval bank wrapper. Refuses to write anywhere but EVAL_BANK."""

    def __init__(self) -> None:
        self.client = make_client(load_hindsight_config())

    def close(self) -> None:
        with quiet_aiohttp():
            with contextlib.suppress(Exception):
                self.client.close()

    def reachable(self) -> bool:
        try:
            self.client.get_version()
            return True
        except Exception:
            return False

    def refresh_bank(self, acervo: Path) -> dict[str, Any]:
        assert EVAL_BANK != FORBIDDEN_BANK  # hard guard: never touch production
        with quiet_aiohttp():
            with contextlib.suppress(Exception):  # first run: bank may not exist
                self.client.delete_bank(EVAL_BANK)
            self.client.create_bank(
                EVAL_BANK,
                name="memory-eval fixture (H2)",
                mission="Index of AcervoIndex pointers for the synthetic eval fixture. Disposable.",
            )
        retained = 0
        errors: list[dict[str, str]] = []
        for path in sorted(acervo.rglob("*.md")):
            rel = path.relative_to(acervo).as_posix()
            if rel.startswith("global/tools/"):
                continue
            payload, metadata, tags = build_pointer_payload(acervo, path)
            try:
                with quiet_aiohttp():
                    self.client.retain(
                        bank_id=EVAL_BANK,
                        content=payload,
                        context="AcervoIndex",
                        document_id=DOC_ID_PREFIX + rel,
                        metadata=metadata,
                        tags=tags,
                        update_mode="replace",
                        retain_async=False,
                    )
                retained += 1
            except Exception as exc:
                errors.append({"path": rel, "error": str(exc)})
        return {"bank": EVAL_BANK, "retained": retained, "errors": errors}

    def recall_paths(self, query: str, known: set[str]) -> list[str]:
        with quiet_aiohttp():
            response = self.client.recall(bank_id=EVAL_BANK, query=query)
        paths: list[str] = []
        for result in response.results:
            rel = None
            if result.metadata and result.metadata.get("path"):
                rel = result.metadata["path"]
            elif result.document_id and result.document_id.startswith(DOC_ID_PREFIX):
                rel = result.document_id[len(DOC_ID_PREFIX):]
            else:
                m = re.search(r"path:\s*(\S+\.md)", result.text or "")
                if m:
                    rel = m.group(1)
            if rel and rel in known and rel not in paths:
                paths.append(rel)
        return paths


class HindsightStrategy:
    name = "hindsight"

    def __init__(self, hs: HindsightEval, corpus: Corpus) -> None:
        self.hs = hs
        self.corpus = corpus

    def retrieve(self, q: Question, k: int = TOP_K) -> list[str]:
        paths = self.hs.recall_paths(q.query, set(self.corpus.docs))
        prefixes = allowed_prefixes(q.scope)  # same scope filter, post-hoc
        return [p for p in paths if p.startswith(prefixes)][:k]


class HybridStrategy:
    """Union: exact-path agreement first, then catalog rank, then hindsight rank."""

    name = "hybrid"

    def __init__(self, catalog: CatalogStrategy, hindsight: HindsightStrategy) -> None:
        self.catalog = catalog
        self.hindsight = hindsight

    def retrieve(self, q: Question, k: int = TOP_K) -> list[str]:
        cat = self.catalog.retrieve(q, k)
        hs = self.hindsight.retrieve(q, k)
        agreement = [p for p in cat if p in hs]
        merged = agreement + [p for p in cat if p not in agreement]
        merged += [p for p in hs if p not in merged]
        return merged[:k]


# ---------------------------------------------------------------- scoring

def rel_to_fixture(rel: str) -> str:
    return "acervo/" + rel


def score_question(q: Question, top: list[str], corpus: Corpus) -> dict[str, Any]:
    fixture_paths = [rel_to_fixture(p) for p in top]
    packed_text = "".join(
        (FIXTURE_ACERVO / p).read_text(encoding="utf-8", errors="replace")
        for p in top
    )
    token_cost = sum(corpus.docs[p].chars for p in top)

    row: dict[str, Any] = {
        "id": q.id,
        "category": q.category,
        "top": fixture_paths,
        "token_cost": token_cost,
        "recall": None,
        "precision": None,
        "contaminated": False,
        "abstention_correct": None,
    }
    if q.expects_abstention:
        row["abstention_correct"] = not top
    else:
        hits = [p for p in q.expected_paths if p in fixture_paths]
        row["recall"] = len(hits) / len(q.expected_paths) if q.expected_paths else None
        row["precision"] = len(hits) / len(fixture_paths) if fixture_paths else 0.0
    row["contaminated"] = bool(
        set(q.forbidden_paths) & set(fixture_paths)
        or any(s in packed_text for s in q.forbidden_content)
    )
    return row


def _mean(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 4) if values else None


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    recalls = [r["recall"] for r in rows if r["recall"] is not None]
    precisions = [r["precision"] for r in rows if r["precision"] is not None]
    abstentions = [r["abstention_correct"] for r in rows if r["abstention_correct"] is not None]
    return {
        "n": len(rows),
        "recall": _mean(recalls),
        "precision": _mean(precisions),
        "contamination_rate": _mean([1.0 if r["contaminated"] else 0.0 for r in rows]),
        "abstention_accuracy": _mean([1.0 if a else 0.0 for a in abstentions]),
        "avg_token_cost": round(sum(r["token_cost"] for r in rows) / len(rows)) if rows else None,
    }


def run_eval(
    questions: list[Question],
    strategies: dict[str, Any],
    corpus: Corpus,
    k: int = TOP_K,
) -> dict[str, Any]:
    results: dict[str, Any] = {"run_at": utc_now(), "k": k, "strategies": {}}
    for name, strategy in strategies.items():
        rows = [score_question(q, strategy.retrieve(q, k), corpus) for q in questions]
        by_category = {
            cat: aggregate([r for r in rows if r["category"] == cat])
            for cat in CATEGORIES
            if any(r["category"] == cat for r in rows)
        }
        results["strategies"][name] = {
            "overall": aggregate(rows),
            "by_category": by_category,
            "questions": rows,
        }
    if "catalog" in results["strategies"] and "hybrid" in results["strategies"]:
        cat_r = results["strategies"]["catalog"]["overall"]["recall"] or 0.0
        hyb_r = results["strategies"]["hybrid"]["overall"]["recall"] or 0.0
        delta = round((hyb_r - cat_r) * 100, 1)
        results["verdict"] = {
            "metric": "hybrid recall@5 minus catalog recall@5 (points)",
            "delta_pts": delta,
            "threshold_pts": H2_THRESHOLD_PTS,
            "decision": (
                "keep Hindsight as supplement (hybrid > catalog by more than +5pts)"
                if delta > H2_THRESHOLD_PTS
                else "demote Hindsight to optional (hybrid <= catalog + 5pts)"
            ),
        }
    return results


# ---------------------------------------------------------------- report

def _fmt(value: float | None, pct: bool = True) -> str:
    if value is None:
        return "—"
    return f"{value * 100:.1f}%" if pct else f"{value:,.0f}"


def render_markdown(results: dict[str, Any], notes: list[str]) -> str:
    lines = [
        f"# H2 — Agentic search vs semantic index (run {results['run_at']})",
        "",
        "Retrieval-only scorer over the synthetic fixture "
        "(`tests/memory-eval/fixture/`, 25 golden questions, top-k="
        f"{results['k']}). No LLM answers; measures which FILES surface.",
        "",
    ]
    for note in notes:
        lines.append(f"> {note}")
    lines += [
        "",
        "## Overall",
        "",
        "| Strategy | Recall@5 | Precision@5 | Contamination | Abstention acc. | Avg token cost (chars) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, data in results["strategies"].items():
        o = data["overall"]
        lines.append(
            f"| {name} | {_fmt(o['recall'])} | {_fmt(o['precision'])} | "
            f"{_fmt(o['contamination_rate'])} | {_fmt(o['abstention_accuracy'])} | "
            f"{_fmt(o['avg_token_cost'], pct=False)} |"
        )
    lines += ["", "## Per category (recall@5 · precision@5 · contamination · abstention)", ""]
    names = list(results["strategies"])
    header = "| Category | n | " + " | ".join(names) + " |"
    lines += [header, "|---|---:|" + "---|" * len(names)]
    categories = list(results["strategies"][names[0]]["by_category"])
    for cat in categories:
        cells = []
        for name in names:
            c = results["strategies"][name]["by_category"][cat]
            if cat == "absent":
                cells.append(f"abst {_fmt(c['abstention_accuracy'])} · cont {_fmt(c['contamination_rate'])}")
            else:
                cells.append(
                    f"R {_fmt(c['recall'])} · P {_fmt(c['precision'])} · cont {_fmt(c['contamination_rate'])}"
                )
        n = results["strategies"][names[0]]["by_category"][cat]["n"]
        lines.append(f"| {cat} | {n} | " + " | ".join(cells) + " |")
    if "verdict" in results:
        v = results["verdict"]
        lines += [
            "",
            "## Verdict (H2 decision metric)",
            "",
            f"**Δ recall (hybrid − catalog) = {v['delta_pts']:+.1f}pts** "
            f"(threshold: +{v['threshold_pts']:.0f}pts) → **{v['decision']}**",
        ]
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------- gate

def gate_overall(acervo: Path, corpus: Corpus, questions: list[Question], k: int = TOP_K) -> dict[str, Any]:
    """Deterministic catalog-only metrics used by the CI regression gate."""
    strategy = CatalogStrategy(acervo, corpus)
    results = run_eval(questions, {GATE_STRATEGY: strategy}, corpus, k=k)
    return results["strategies"][GATE_STRATEGY]["overall"]


def compare_to_baseline(current: dict[str, Any], baseline: dict[str, Any]) -> list[dict[str, Any]]:
    """Score current metrics against a baseline (10-evaluation.md §4).

    Returns one row per gate metric with the delta in points and a verdict.
    A row is a violation iff `blocked` is True (regression past REGRESSION_PTS
    in the good direction, or a hard-ceiling breach)."""
    base_metrics = baseline.get("metrics", {})
    rows: list[dict[str, Any]] = []
    for name, direction, hard_max in GATE_METRICS:
        cur = current.get(name)
        base = base_metrics.get(name)
        row: dict[str, Any] = {
            "metric": name, "baseline": base, "current": cur,
            "delta_pts": None, "blocked": False, "reason": "ok",
        }
        if cur is None or base is None:
            row["blocked"] = cur is None
            row["reason"] = "missing metric" if cur is None else "no baseline (advisory)"
            rows.append(row)
            continue
        row["delta_pts"] = round((cur - base) * 100, 1)
        if hard_max is not None and cur > hard_max + 1e-9:
            row["blocked"] = True
            row["reason"] = f"hard ceiling {hard_max:.0%} breached"
        elif direction == "higher" and (base - cur) * 100 > REGRESSION_PTS:
            row["blocked"] = True
            row["reason"] = f"regressed {(base - cur) * 100:.1f}pts (> {REGRESSION_PTS:.0f})"
        elif direction == "lower" and (cur - base) * 100 > REGRESSION_PTS:
            row["blocked"] = True
            row["reason"] = f"worsened {(cur - base) * 100:.1f}pts (> {REGRESSION_PTS:.0f})"
        rows.append(row)
    return rows


def build_baseline(current: dict[str, Any], k: int) -> dict[str, Any]:
    return {
        "strategy": GATE_STRATEGY,
        "k": k,
        "captured_at": utc_now(),
        "regression_pts": REGRESSION_PTS,
        "note": (
            "Deterministic catalog-only metrics for the CI regression gate "
            "(10-evaluation.md §4). Regenerate with `run_eval.py --update-baseline` "
            "after an INTENTIONAL, reviewed improvement."
        ),
        "metrics": {name: current.get(name) for name, _dir, _hm in GATE_METRICS},
    }


def render_gate(rows: list[dict[str, Any]]) -> str:
    def _p(v: float | None) -> str:
        return "—" if v is None else f"{v * 100:.1f}%"

    lines = [
        "Metric               | baseline | current  | Δpts   | verdict",
        "---------------------+----------+----------+--------+--------",
    ]
    for r in rows:
        d = "—" if r["delta_pts"] is None else f"{r['delta_pts']:+.1f}"
        verdict = "BLOCK" if r["blocked"] else "ok"
        lines.append(
            f"{r['metric']:<20} | {_p(r['baseline']):>8} | {_p(r['current']):>8} | "
            f"{d:>6} | {verdict}  {r['reason'] if r['blocked'] else ''}".rstrip()
        )
    return "\n".join(lines)


def run_gate(acervo: Path, corpus: Corpus, questions: list[Question], k: int,
             update: bool) -> int:
    current = gate_overall(acervo, corpus, questions, k=k)
    if update:
        baseline = build_baseline(current, k)
        BASELINE_PATH.write_text(
            json.dumps(baseline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"baseline written: {BASELINE_PATH}", file=sys.stderr)
        print(json.dumps(baseline, ensure_ascii=False, indent=2))
        return 0
    if not BASELINE_PATH.exists():
        print(f"ERROR: no baseline at {BASELINE_PATH} — run --update-baseline first.",
              file=sys.stderr)
        return 2
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    rows = compare_to_baseline(current, baseline)
    print(render_gate(rows), file=sys.stderr)
    blocked = [r for r in rows if r["blocked"]]
    print(json.dumps({"blocked": bool(blocked), "rows": rows}, ensure_ascii=False, indent=2))
    if blocked:
        names = ", ".join(r["metric"] for r in blocked)
        print(f"::error::memory-eval gate FAILED — regression in: {names}", file=sys.stderr)
        return 1
    print("memory-eval gate PASSED — no metric regressed beyond threshold.", file=sys.stderr)
    return 0


# ---------------------------------------------------------------- CLI

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Retrieval-eval harness (H2)")
    parser.add_argument("--workdir", type=Path,
                        help="Where the fixture copy + catalog.sqlite go (default: report/.workdir)")
    parser.add_argument("--strategies", default="catalog,hindsight,hybrid",
                        help="Comma-separated subset of: catalog,hindsight,hybrid,production")
    parser.add_argument("--questions", help="Comma-separated question ids (default: all 25)")
    parser.add_argument("--k", type=int, default=TOP_K)
    parser.add_argument("--skip-hindsight-index", action="store_true",
                        help="Reuse the existing eval-fixture bank instead of refreshing it")
    parser.add_argument("--no-report", action="store_true", help="Print JSON only")
    parser.add_argument("--gate", action="store_true",
                        help="CI regression gate: catalog-only, compare to baseline.json, "
                             "exit 1 if any metric regresses past the threshold (10-evaluation §4)")
    parser.add_argument("--update-baseline", action="store_true",
                        help="Recapture the catalog baseline into baseline.json (use after a "
                             "reviewed, intentional improvement) and exit")
    args = parser.parse_args(argv)

    workdir = (args.workdir or REPORT_DIR / ".workdir").resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    acervo = build_workdir_catalog(workdir)
    corpus = Corpus(acervo)

    questions = load_questions()
    if args.questions:
        wanted = {x.strip() for x in args.questions.split(",")}
        questions = [q for q in questions if q.id in wanted]

    if args.gate or args.update_baseline:
        return run_gate(acervo, corpus, questions, k=args.k, update=args.update_baseline)

    requested = [s.strip() for s in args.strategies.split(",") if s.strip()]
    strategies: dict[str, Any] = {}
    catalog = CatalogStrategy(acervo, corpus)
    if "catalog" in requested:
        strategies["catalog"] = catalog
    if "production" in requested:
        strategies["production"] = ProductionStrategy(acervo)

    hs: HindsightEval | None = None
    hindsight_note = None
    if {"hindsight", "hybrid"} & set(requested):
        hs = HindsightEval()
        if not hs.reachable():
            hindsight_note = "Hindsight unreachable — ran catalog-only."
            print(f"WARN: {hindsight_note}", file=sys.stderr)
            hs.close()
            hs = None
        else:
            if not args.skip_hindsight_index:
                summary = hs.refresh_bank(acervo)
                print(json.dumps({"hindsight_index": summary}, ensure_ascii=False), file=sys.stderr)
            hindsight_strategy = HindsightStrategy(hs, corpus)
            if "hindsight" in requested:
                strategies["hindsight"] = hindsight_strategy
            if "hybrid" in requested:
                strategies["hybrid"] = HybridStrategy(catalog, hindsight_strategy)

    try:
        results = run_eval(questions, strategies, corpus, k=args.k)
    finally:
        if hs is not None:
            hs.close()

    notes = [
        "Abstention floors — catalog: candidate must match >= 2 distinct query terms "
        f"or 1 rare term (doc-frequency <= {RARE_DF_MAX} fixture files); "
        "hindsight: any pointer returned at default recall budget counts (no per-result "
        "score is exposed) — abstention correct iff zero pointers survive the scope filter.",
        "Token cost proxy: total chars of the top-5 files' raw text (packed-context estimate).",
    ]
    if hindsight_note:
        notes.append(hindsight_note)
    results["notes"] = notes

    if not args.no_report:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = date.today().isoformat()
        json_path = REPORT_DIR / f"h2-{stamp}.json"
        md_path = REPORT_DIR / f"h2-{stamp}.md"
        json_path.write_text(
            json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        md_path.write_text(render_markdown(results, notes), encoding="utf-8")
        print(f"report: {md_path}", file=sys.stderr)

    print(json.dumps(
        {
            "strategies": {
                name: data["overall"] for name, data in results["strategies"].items()
            },
            "verdict": results.get("verdict"),
        },
        ensure_ascii=False, indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
