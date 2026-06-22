#!/usr/bin/env python3
"""Validate Acervo Cognitivo ``log.md`` files against the log-convention spec.

Enforces §1–§3 of ``docs/plans/2026-06-19_acervo-lifecycle-okf/log-convention.md``:

  §1  Format — single ``# Log`` H1, ``## YYYY-MM-DD`` date headings (chronological
      ascending), single-line top-level bullets, no free text.
  §2  Entry types — the seven typed bullets (CREATED/UPDATED/DEPRECATED/PROMOTED/
      QUARANTINED/PURGED/RESTORED) and their exact formats.
  §3  Location — logs live under ``micro/``, ``global/``, ``shared/`` (``_meta/``-first);
      ``macro/`` must NOT have a log.

Severities follow ``validate_frontmatter.py``: ERROR fails the file (exit 1), WARN is
reported but non-fatal. Legacy free-text logs (predating this spec) surface as WARN, so
the validator can be wired as a non-fatal gate without breaking installs over history.

Usage:
    python3 validate_log.py --file <path/to/log.md>
    python3 validate_log.py --dir  <acervo-root>
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

# ─── Patterns ─────────────────────────────────────────────────────────────────

H1_RE = re.compile(r"^#\s+(.*)$")
H1_CANONICAL_RE = re.compile(r"^#\s+Log(\s+—\s+\S.*)?$")
H2_RE = re.compile(r"^##\s+(.*)$")
STRICT_DATE_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2})$")
BULLET_RE = re.compile(r"^- (.+)$")
SUBBULLET_RE = re.compile(r"^(\s+[-*]\s+|\t)")
FENCE_RE = re.compile(r"^\s*```")

# §2 — the seven entry types, anchored to their exact formats.
DASH = "—"  # U+2014 em-dash separator " — "
ENTRY_RES = {
    "CREATED": re.compile(r"^CREATED: \S.* \((perene|volátil)\) — .+$"),
    "UPDATED": re.compile(r"^UPDATED: \S.* — .+$"),
    "DEPRECATED": re.compile(r"^DEPRECATED: \S.* — .+$"),
    "PROMOTED": re.compile(r"^PROMOTED: \S.* → perene$"),
    "QUARANTINED": re.compile(r"^QUARANTINED: \S.* — .+$"),
    "PURGED": re.compile(r"^PURGED: \S.* — quarantine expired \(30 days\)$"),
    "RESTORED": re.compile(r"^RESTORED: \S.* — restored from quarantine by executive$"),
}
ENTRY_KEYWORDS = tuple(ENTRY_RES.keys())


def _is_valid_date(value):
    try:
        y, m, d = (int(p) for p in value.split("-"))
        date(y, m, d)
        return True
    except (ValueError, TypeError):
        return False


# ─── Validation ───────────────────────────────────────────────────────────────


def validate_log(path):
    """Return ``(path, issues)`` where issues is a list of ``(rule, severity, msg)``."""
    issues = []
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    # Strip a leading UTF-8 BOM (parity with validate_frontmatter.py).
    if text.startswith("﻿"):
        text = text[1:]
    lines = text.splitlines()

    # §3.3 — macro/ must never host a log.
    parts = Path(path).parts
    if "macro" in parts:
        issues.append(("L-030", "ERROR",
                       "macro/ must NOT have a log.md (§3.3 — identity tracked in git only)"))

    # §1.1 — H1 title. Format violations are WARN, not ERROR: the convention
    # explicitly preserves legacy free-text logs verbatim (§4 step 2), so the
    # shipped/historical acervo legitimately contains pre-spec logs. Only the
    # §3.3 macro-log violation (L-030) is a hard ERROR.
    h1_indices = [i for i, ln in enumerate(lines) if H1_RE.match(ln)]
    first_content = next((ln for ln in lines if ln.strip()), "")
    if not H1_RE.match(first_content):
        issues.append(("L-001", "WARN", "file should start with an H1 '# Log' line (§1.1)"))
    if len(h1_indices) > 1:
        issues.append(("L-002", "WARN",
                       f"exactly one H1 expected, found {len(h1_indices)} (§1.1)"))
    if h1_indices and not H1_CANONICAL_RE.match(lines[h1_indices[0]]):
        issues.append(("L-003", "WARN",
                       "H1 should be '# Log' or '# Log — <name>' (§1.1)"))

    # Walk body: headings, ordering, bullets, free text.
    seen_dates = []
    has_legacy_heading = False
    current_date = None
    in_fence = False
    first_h1_seen = False

    for ln in lines:
        if FENCE_RE.match(ln):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not ln.strip():
            continue

        if H1_RE.match(ln):
            first_h1_seen = True
            continue

        h2 = H2_RE.match(ln)
        if h2:
            m = STRICT_DATE_RE.match(ln)
            if not m:
                has_legacy_heading = True
                issues.append(("L-010", "WARN",
                               f"date heading not '## YYYY-MM-DD' (legacy/free-text): {ln.strip()!r}"))
                current_date = None
                continue
            d = m.group(1)
            if not _is_valid_date(d):
                issues.append(("L-012", "WARN", f"invalid calendar date in heading: {d}"))
            if seen_dates and d < seen_dates[-1]:
                issues.append(("L-011", "WARN",
                               f"date headings must be ascending; {d} follows {seen_dates[-1]} (§1.2)"))
            seen_dates.append(d)
            current_date = d
            continue

        bullet = BULLET_RE.match(ln)
        if bullet:
            payload = bullet.group(1)
            # §2 entry-format check only on strict logs (avoid noise on legacy files).
            if not has_legacy_heading and first_h1_seen:
                keyword = payload.split(":", 1)[0].strip()
                if keyword in ENTRY_KEYWORDS:
                    if not ENTRY_RES[keyword].match(payload):
                        issues.append(("L-021", "WARN",
                                       f"{keyword} entry does not match its §2 format: {payload!r}"))
                else:
                    issues.append(("L-021", "WARN",
                                   f"bullet is not one of the 7 §2 entry types: {payload!r}"))
            continue

        if SUBBULLET_RE.match(ln):
            issues.append(("L-020", "WARN",
                           f"sub-bullets / continuation lines are not allowed (§1.1): {ln.strip()!r}"))
            continue

        # Anything else under the body is free text.
        if first_h1_seen:
            issues.append(("L-020", "WARN",
                           f"free text not allowed between/under headings (§1.1): {ln.strip()!r}"))

    return (str(path), issues)


# ─── Discovery ──────────────────────────────────────────────────────────────


def find_logs(root):
    """Find log.md files in the canonical containers (micro/, global/, shared/).

    Returns ``(logs, extra)`` where ``extra`` are log.md files found outside the
    three canonical containers (e.g. under macro/) — kept so they can be flagged.
    """
    base = Path(root)
    logs = []
    extra = []
    for log in sorted(base.rglob("log.md")):
        rel = log.relative_to(base).parts
        top = rel[0] if rel else ""
        if top in ("micro", "global", "shared"):
            logs.append(log)
        else:
            extra.append(log)
    return logs, extra


# ─── Output (mirrors validate_frontmatter.py) ─────────────────────────────────


def _has_errors(issues):
    return any(sev == "ERROR" for _r, sev, _m in issues)


def print_results(results):
    for path, issues in results:
        status = "FAIL" if _has_errors(issues) else ("WARN" if issues else "PASS")
        print(f"{status}  {path}")
        for rule_id, severity, message in issues:
            tag = "ERROR" if severity == "ERROR" else "WARN "
            print(f"      [{rule_id}] {tag}: {message}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate Acervo Cognitivo log.md files (log-convention §1–§3).",
    )
    parser.add_argument("--file", metavar="PATH", help="Validate a single log.md file.")
    parser.add_argument("--dir", metavar="PATH",
                        help="Find and validate all log.md files in a tree.")
    args = parser.parse_args(argv)

    if not args.file and not args.dir:
        parser.error("at least one of --file or --dir is required")

    results = []

    if args.file:
        fp = Path(args.file)
        if not fp.is_file():
            print(f"Error: file not found: {args.file}", file=sys.stderr)
            return 2
        results.append(validate_log(fp))

    if args.dir:
        dp = Path(args.dir)
        if not dp.is_dir():
            print(f"Error: directory not found: {args.dir}", file=sys.stderr)
            return 2
        logs, extra = find_logs(dp)
        for log in logs + extra:
            results.append(validate_log(log))

    print_results(results)

    total = len(results)
    failed = sum(1 for _p, iss in results if _has_errors(iss))
    warned = sum(1 for _p, iss in results if iss and not _has_errors(iss))
    print(f"# log.md: {total} scanned, {failed} error, {warned} warn, "
          f"{total - failed - warned} clean")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
