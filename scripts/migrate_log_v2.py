#!/usr/bin/env python3
"""Migrate legacy free-text ``_meta/log.md`` files to the strict log-convention format.

Companion to ``validate_log.py``. The write pipeline (``acervoctl new-object`` and the
conflict verbs) appends a strict entry and then validates the *whole* log file; a scope
whose log still carries legacy free-text history therefore rejects every live write
(finding #1, memory-v2). This one-time migrator rewrites those legacy logs into the
strict format so live writes pass, while preserving all historical text.

Transform rules (see docs/plans/2026-06-19_acervo-lifecycle-okf/log-convention.md §1–§3):

  * Frontmatter block — preserved verbatim (the log-convention validator ignores it).
  * H1 — normalized to ``# Log`` or ``# Log — <name>`` (``# Global Log`` → ``# Log — Global``,
    ``# BI ... — Log`` → ``# Log — BI ...``). A canonical H1 is kept as-is.
  * Blockquote ``>`` header notes (format hints) — dropped; they carry no history.
  * Date headings — every legacy heading (``## YYYY-MM-DD | a | b``, ``## [YYYY-MM-DD] ...``,
    ``## YYYY-MM-DD — a | b``) collapses to a strict ``## YYYY-MM-DD``; already-strict
    headings pass through. Ordering is preserved (the source logs are already ascending;
    equal dates are legal under §1.2).
  * Entries — a bullet that already matches one of the nine §2 entry formats is kept
    verbatim. Every other content unit (legacy bullet, ONBOARDING-ACTIVATED, free-text
    paragraph, embedded-date bullet) becomes ONE ``UPDATED: <container>/ — <text>`` entry.
    Indented sub-bullets fold into their parent entry, joined with ``; ``. Legacy events
    are uniformly normalized to UPDATED — never a fabricated CREATED/class or a guessed
    file path; the original action word and full prose are preserved in the tail so no
    information is lost.

The migrator is idempotent: re-running it on migrated output produces no change (a strict
day whose bullets all pass §2 is emitted verbatim).

Usage:
    python3 migrate_log_v2.py --file <path/to/log.md> [--write]
    python3 migrate_log_v2.py --dir  <acervo-root>    [--write]

Without ``--write`` it is a dry run: prints a unified diff per file and changes nothing.
"""

import argparse
import difflib
import re
import sys
from pathlib import Path

# Directories whose logs must NOT be migrated — kept in sync with
# migrate_frontmatter_v2.EXCLUDED_DIRS. `_ops_snapshots` is frozen history,
# `_template` holds jinja placeholders, `_retired` is archived, etc.
EXCLUDED_DIRS = frozenset({
    "_artifacts", "raw", "_archive", ".quarantine",
    "_inbox", "_tasks", "_routines", "_automations",
    "_template", "_retired", "_ops_snapshots", "_fixture",
    "macro",
})

DASH = "—"  # em-dash, the " — " separator used by §2

# The nine strict entry types (validate_log.py §2), anchored to exact format.
ENTRY_RES = {
    "CREATED": re.compile(r"^CREATED: \S.* \((perene|volátil)\) — .+$"),
    "UPDATED": re.compile(r"^UPDATED: \S.* — .+$"),
    "DEPRECATED": re.compile(r"^DEPRECATED: \S.* — .+$"),
    "PROMOTED": re.compile(r"^PROMOTED: \S.* → perene$"),
    "QUARANTINED": re.compile(r"^QUARANTINED: \S.* — .+$"),
    "PURGED": re.compile(r"^PURGED: \S.* — quarantine expired \(30 days\)$"),
    "RESTORED": re.compile(r"^RESTORED: \S.* — restored from quarantine by executive$"),
    "SUPERSEDED": re.compile(r"^SUPERSEDED: \S.* — superseded by \S.*$"),
    "DISPUTED": re.compile(r"^DISPUTED: \S.* — disputed by \S.*$"),
}

H1_RE = re.compile(r"^#\s+(.*)$")
H1_CANONICAL_RE = re.compile(r"^#\s+Log(\s+—\s+\S.*)?$")
H2_RE = re.compile(r"^##\s+(.*)$")
# Date at the start of an H2 payload, optionally bracketed; rest is the descriptor.
HEAD_DATE_RE = re.compile(r"^\[?(\d{4}-\d{2}-\d{2})\]?[\s\]]*(.*)$")
BULLET_RE = re.compile(r"^- (.+)$")
SUBBULLET_RE = re.compile(r"^(?:\s+[-*]|\t)\s*(.+?)\s*$")
FENCE_RE = re.compile(r"^\s*```")


def _split_frontmatter(text):
    """Return (frontmatter_str_including_fences_or_empty, body_str)."""
    if text.startswith("﻿"):
        text = text[1:]
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                fm = "\n".join(lines[: i + 1])
                body = "\n".join(lines[i + 1:])
                return fm, body
    return "", text


def _normalize_h1(h1_text):
    """Return a canonical H1 line for the given raw '# ...' text."""
    m = H1_RE.match(h1_text)
    if not m:
        return "# Log"
    if H1_CANONICAL_RE.match(h1_text):
        return h1_text.rstrip()
    name = m.group(1).strip()
    # Strip the word "Log" and any surrounding separators, in any position.
    name = re.sub(r"\s*—\s*Log\b", "", name)          # "X — Log" → "X"
    name = re.sub(r"\bLog\s*—\s*", "", name)          # "Log — X" → "X"
    name = re.sub(r"\bLog\b", "", name).strip()       # "Global Log" → "Global"
    name = name.strip(" —-").strip()
    return f"# Log — {name}" if name else "# Log"


def _is_valid_entry(payload):
    keyword = payload.split(":", 1)[0].strip()
    rx = ENTRY_RES.get(keyword)
    return bool(rx and rx.match(payload))


def _clean_descriptor(desc):
    """Trim a legacy heading descriptor to a compact ``action | subject`` tag."""
    return desc.strip().strip("|").strip(" —-|").strip()


def _fold(text):
    """Collapse internal whitespace/newlines to single spaces for one-line entries."""
    return re.sub(r"\s+", " ", text).strip()


def migrate_text(text, container):
    """Return the migrated file text for one log. ``container`` is the owning-root
    prefix used as the path token for generated entries (e.g. ``global`` , ``micro/foo``)."""
    fm, body = _split_frontmatter(text)
    body_lines = body.splitlines()

    # ---- Locate + normalize H1; everything before it (and blockquotes) is dropped.
    h1_line = "# Log"
    h1_idx = None
    for i, ln in enumerate(body_lines):
        if H1_RE.match(ln):
            h1_line = _normalize_h1(ln)
            h1_idx = i
            break

    # ---- Parse the body into day blocks. A block = (date, descriptor, [content lines]).
    blocks = []          # list of dicts: {date, desc, items}
    preamble_seen_h1 = h1_idx is not None
    current = None
    in_fence = False
    start = (h1_idx + 1) if h1_idx is not None else 0

    for ln in body_lines[start:]:
        if FENCE_RE.match(ln):
            in_fence = not in_fence
            if current is not None:
                current["items"].append(("raw", ln))
            continue
        if in_fence:
            if current is not None:
                current["items"].append(("raw", ln))
            continue
        if not ln.strip():
            continue
        if ln.lstrip().startswith(">"):
            continue  # drop blockquote header notes
        if H1_RE.match(ln):
            continue  # ignore any stray extra H1

        h2 = H2_RE.match(ln)
        if h2:
            dm = HEAD_DATE_RE.match(h2.group(1).strip())
            if dm:
                date = dm.group(1)
                desc = _clean_descriptor(dm.group(2))
            else:
                # Non-date heading (shouldn't happen in our corpus) — keep text as desc.
                date = None
                desc = h2.group(1).strip()
            current = {"date": date, "desc": desc, "items": []}
            blocks.append(current)
            continue

        # Content line under the current day.
        if current is None:
            continue  # content before any heading (besides blockquotes) — drop
        sub = SUBBULLET_RE.match(ln)
        if sub and not BULLET_RE.match(ln):
            current["items"].append(("sub", sub.group(1)))
            continue
        b = BULLET_RE.match(ln)
        if b:
            current["items"].append(("bullet", b.group(1)))
        else:
            current["items"].append(("free", ln.strip()))

    # ---- Emit. Bullets are accumulated per date so each day gets exactly one
    # heading (§1.1), even when several legacy sub-days share a date.
    cprefix = f"{container}/"
    by_date = {}      # date -> list[str] bullet lines
    date_order = []   # dates in first-seen order (source is already ascending)

    for blk in blocks:
        date = blk["date"]
        if date is None:
            continue
        if date not in by_date:
            by_date[date] = []
            date_order.append(date)

        # Fold sub-bullets into the preceding top-level item; keep verbatim strict
        # bullets separate.
        units = []  # list of (kind, text): kind in {"verbatim", "convert"}
        for kind, val in blk["items"]:
            if kind == "sub":
                if units:
                    units[-1] = (units[-1][0], units[-1][1] + "; " + _fold(val))
                else:
                    units.append(("convert", _fold(val)))
                continue
            if kind == "bullet" and _is_valid_entry(val):
                units.append(("verbatim", val))
            else:  # bullet (non-strict), free, or raw
                units.append(("convert", _fold(val)))

        desc = blk["desc"]
        generated = 0
        for kind, val in units:
            if kind == "verbatim":
                by_date[date].append(f"- {val}")
                continue
            tail = val
            # Prefix the day descriptor onto the first generated entry of the block.
            if desc and generated == 0:
                tail = f"[{desc}] {tail}".strip() if tail else f"[{desc}]"
            tail = _fold(tail)
            if not tail:
                tail = f"[{desc}]" if desc else "(sem descrição)"
            by_date[date].append(f"- UPDATED: {cprefix} {DASH} {tail}")
            generated += 1

        # A descriptor-only day (no content units) still records the event.
        if not units and desc:
            by_date[date].append(f"- UPDATED: {cprefix} {DASH} [{desc}]")

    out = [h1_line, ""]
    for date in date_order:
        out.append(f"## {date}")
        out.extend(by_date[date])
        out.append("")

    body_out = "\n".join(out).rstrip() + "\n"
    if fm:
        return fm + "\n\n" + body_out
    return body_out


def _container_for(path, root):
    """Owning-root prefix for a log at ``path`` relative to acervo ``root``.

    ``global/_meta/log.md`` → ``global`` ; ``micro/foo/_meta/log.md`` → ``micro/foo`` ;
    ``shared/_meta/log.md`` → ``shared``.
    """
    rel = Path(path).resolve().relative_to(Path(root).resolve())
    parts = rel.parts
    if parts and parts[0] == "micro" and len(parts) >= 2:
        return "micro/" + parts[1]
    return parts[0] if parts else ""


def _is_excluded(path, root):
    rel = Path(path).resolve().relative_to(Path(root).resolve())
    return any(p in EXCLUDED_DIRS for p in rel.parts)


def find_logs(root):
    base = Path(root)
    logs = []
    for log in sorted(base.rglob("log.md")):
        rel = log.relative_to(base).parts
        if rel and rel[0] in ("micro", "global", "shared") and not _is_excluded(log, root):
            logs.append(log)
    return logs


def process(path, root, write):
    original = Path(path).read_text(encoding="utf-8")
    container = _container_for(path, root)
    migrated = migrate_text(original, container)
    changed = migrated != original
    if changed and write:
        Path(path).write_text(migrated, encoding="utf-8")
    return changed, original, migrated


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", metavar="PATH", help="Migrate a single log.md file.")
    ap.add_argument("--dir", metavar="PATH", help="Migrate all eligible log.md files in a tree.")
    ap.add_argument("--root", metavar="PATH", help="Acervo root for container inference (default: inferred).")
    ap.add_argument("--write", action="store_true", help="Write changes (default: dry-run diff).")
    args = ap.parse_args(argv)

    if not args.file and not args.dir:
        ap.error("at least one of --file or --dir is required")

    if args.dir:
        root = args.root or args.dir
        targets = find_logs(args.dir)
    else:
        fp = Path(args.file)
        # Infer root by walking up to the acervo top (parent of micro/global/shared).
        root = args.root
        if not root:
            for anc in fp.resolve().parents:
                if anc.name in ("micro", "global", "shared"):
                    root = str(anc.parent)
                    break
            root = root or str(fp.resolve().parent)
        targets = [fp]

    changed_count = 0
    for t in targets:
        changed, original, migrated = process(t, root, args.write)
        status = "CHANGED" if changed else "clean"
        if changed:
            changed_count += 1
        print(f"{status:8} {t}")
        if changed and not args.write:
            diff = difflib.unified_diff(
                original.splitlines(keepends=True),
                migrated.splitlines(keepends=True),
                fromfile=f"a/{t}", tofile=f"b/{t}",
            )
            sys.stdout.writelines(diff)
            print()

    verb = "written" if args.write else "would change"
    print(f"# {len(targets)} scanned, {changed_count} {verb}, {len(targets) - changed_count} clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
