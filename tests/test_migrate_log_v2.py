#!/usr/bin/env python3
"""Tests for scripts/migrate_log_v2.py — legacy log.md → strict log-convention.

Covers: H1 normalization, blockquote dropping, legacy heading → strict date,
same-date merge, verbatim pass-through of already-strict typed bullets,
non-canonical typed bullet (ONBOARDING-ACTIVATED) → UPDATED, sub-bullet folding,
bracketed/em-dash/pipe heading variants, idempotency, EXCLUDED_DIRS skipping, and
the end-to-end guarantee that migrated output passes validate_log.py.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MIGRATOR = REPO_ROOT / "scripts" / "migrate_log_v2.py"
VALIDATOR = REPO_ROOT / "scripts" / "validate_log.py"

_spec = importlib.util.spec_from_file_location("migrate_log_v2", MIGRATOR)
mig = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mig)

FM = """\
---
schema: acervo/v0.2
type: context
title: Log
class: perene
created_at: 2026-06-08T00:00:00Z
nature: _meta
---
"""


def _validate(path):
    r = subprocess.run([sys.executable, str(VALIDATOR), "--file", str(path)],
                       capture_output=True, text=True)
    return r.returncode, r.stdout


# ─── H1 normalization ────────────────────────────────────────────────────────

def test_h1_canonical_kept():
    assert mig._normalize_h1("# Log") == "# Log"
    assert mig._normalize_h1("# Log — Exocórtex Dev") == "# Log — Exocórtex Dev"


def test_h1_suffix_and_prefix_forms():
    assert mig._normalize_h1("# Global Log") == "# Log — Global"
    assert mig._normalize_h1("# Shared Log") == "# Log — Shared"
    assert mig._normalize_h1("# BI e Inteligência Comercial — Log") == "# Log — BI e Inteligência Comercial"


# ─── Body transforms ─────────────────────────────────────────────────────────

def test_blockquotes_dropped_and_legacy_heading_converted():
    src = FM + """
# Global Log

> Registro cronológico. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`

## [2026-05-26] create | Global layer initialized
- Structure created with SCHEMA.md
"""
    out = mig.migrate_text(src, "global")
    assert "# Log — Global" in out
    assert ">" not in out.split("---\n", 2)[-1]  # no blockquote lines in body
    assert "## 2026-05-26" in out
    assert "- UPDATED: global/ — [create | Global layer initialized] Structure created with SCHEMA.md" in out
    rc, _ = _run_and_validate(out)
    assert rc == 0


def test_strict_bullets_pass_verbatim():
    src = FM + """
# Log — Ops

## 2026-06-05
- CREATED: micro/ops/foo.md (perene) — a real created file
- UPDATED: micro/ops/bar.md — a real update
"""
    out = mig.migrate_text(src, "micro/ops")
    assert "- CREATED: micro/ops/foo.md (perene) — a real created file" in out
    assert "- UPDATED: micro/ops/bar.md — a real update" in out
    assert "UPDATED: micro/ops/ —" not in out  # nothing was rewritten


def test_onboarding_activated_becomes_updated():
    src = FM + """
# Log — X

## 2026-07-02
- ONBOARDING-ACTIVATED: micro/x/ (perene) — Microverso calibrado para o onboarding.
"""
    out = mig.migrate_text(src, "micro/x")
    # No longer a top-level non-canonical bullet; folded into an UPDATED entry
    # with the original text preserved in the tail.
    assert "\n- ONBOARDING-ACTIVATED:" not in out
    assert "- UPDATED: micro/x/ — ONBOARDING-ACTIVATED: micro/x/ (perene) — Microverso calibrado para o onboarding." in out


def test_subbullets_folded_into_parent():
    src = FM + """
# Log — X

## [2026-06-10] create | Ecossistema Visual
- [2026-06-10] create | Design System em `knowledge/ds.md`
  - promovido após issue #18
  - abrange formato Google DESIGN.md
"""
    out = mig.migrate_text(src, "global")
    line = [l for l in out.splitlines() if "Design System" in l][0]
    assert "promovido após issue #18" in line
    assert "abrange formato Google DESIGN.md" in line
    assert line.count("- UPDATED") == 1  # one entry, sub-bullets folded


def test_same_date_headings_merged():
    src = FM + """
# Log — X

## 2026-06-22 — estrutura | canônico
- item a

## 2026-06-22 — dependências | web
- item b
"""
    out = mig.migrate_text(src, "micro/x")
    assert out.count("## 2026-06-22") == 1
    assert "[estrutura | canônico] item a" in out
    assert "[dependências | web] item b" in out


def test_leading_emdash_stripped_from_descriptor():
    src = FM + "\n# Log — X\n\n## 2026-06-22 — estrutura | canônico\n- item\n"
    out = mig.migrate_text(src, "micro/x")
    assert "[estrutura | canônico]" in out
    assert "[— estrutura" not in out


def test_idempotent():
    src = FM + """
# Global Log

> hint line

## [2026-05-26] create | init
- Structure created
- [2026-06-10] update | later thing
  - detail folded
"""
    once = mig.migrate_text(src, "global")
    twice = mig.migrate_text(once, "global")
    assert once == twice


def test_frontmatter_preserved_verbatim():
    src = FM + "\n# Global Log\n\n## [2026-05-26] create | init\n- x\n"
    out = mig.migrate_text(src, "global")
    assert out.startswith(FM.rstrip() + "\n")


# ─── Discovery / exclusions ──────────────────────────────────────────────────

def test_find_logs_skips_excluded(tmp_path):
    for rel in [
        "micro/real/_meta/log.md",
        "global/_meta/log.md",
        "shared/_meta/log.md",
        "micro/_template/_meta/log.md",
        "micro/_retired/old/_meta/log.md",
        "global/_ops_snapshots/snap/_meta/log.md",
        "macro/log.md",
    ]:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# Log\n", encoding="utf-8")
    found = {str(p.relative_to(tmp_path)) for p in mig.find_logs(tmp_path)}
    assert found == {
        "micro/real/_meta/log.md",
        "global/_meta/log.md",
        "shared/_meta/log.md",
    }


def test_container_inference(tmp_path):
    assert mig._container_for(tmp_path / "global/_meta/log.md", tmp_path) == "global"
    assert mig._container_for(tmp_path / "micro/foo/_meta/log.md", tmp_path) == "micro/foo"
    assert mig._container_for(tmp_path / "shared/_meta/log.md", tmp_path) == "shared"


# ─── End-to-end helper ───────────────────────────────────────────────────────

def _run_and_validate(migrated_text, tmp_path=None):
    import tempfile
    d = Path(tempfile.mkdtemp())
    p = d / "log.md"
    p.write_text(migrated_text, encoding="utf-8")
    return _validate(p)


def test_migrated_output_validates(tmp_path):
    src = FM + """
# Shared Log

> Registro cronológico cross-domain. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`

## [2026-05-26] create | Shared layer restructured
- Added SCHEMA.md, index.md
- Created groups.md with aliases

## [2026-07-04] update | groups.md canonizado
- corrigido para 5 microversos ativos
- deprecado shared/knowledge/groups.md
"""
    out = mig.migrate_text(src, "shared")
    rc, report = _validate_via_tmp(out, tmp_path)
    assert rc == 0, report


def _validate_via_tmp(text, tmp_path):
    p = tmp_path / "log.md"
    p.write_text(text, encoding="utf-8")
    return _validate(p)
