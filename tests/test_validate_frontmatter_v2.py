#!/usr/bin/env python3
"""
Tests for schema v0.2 support in scripts/validate_frontmatter.py (ADR-023).

Covers: version dispatch (V2-000 migration WARN on v1 files, suppressible
with --no-migration-warn), the v0.2 Tier 0/1 rules, the cross-field rules
V2-020/030/032/033/040/041/050/051, and the V2-060 secret trust gate
(positive + masked-negative). Files are generated under tmp_path and the
validator is invoked via subprocess (as-invoked, not imported).
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = REPO_ROOT / "scripts" / "validate_frontmatter.py"

# A fully valid v0.2 knowledge object (Tier 0 + Tier 1 complete).
V2_KNOWLEDGE = """\
---
schema: acervo/v0.2
type: knowledge
title: Tabela de preços 2026-Q3 aprovada com reajuste de 8%
description: Reajuste aprovado em 2026-06-28; vigora o trimestre Q3
tags: [pricing, comercial]
created_at: 2026-07-03T14:00:00Z
class: perene
status: active
epistemic: fact
confidence: high
sources:
  - type: conversation
    ref: "session://tg-2026-06-28#dec-1"
observed_at: 2026-06-28
---

Corpo do objeto de conhecimento.
"""

# A valid v1 (pre-v0.2) file — mirrors tests/fixtures/frontmatter templates.
V1_VALID = """\
---
type: knowledge
title: Legacy v1 knowledge page
description: Still on the ADR-013 schema.
tags: [test]
timestamp: 2026-07-03
class: perene
created_at: 2026-07-03T10:00:00Z
---

Body content.
"""


def _write(tmp_path: Path, rel: str, content: str) -> Path:
    path = tmp_path / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _run(path: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--file", str(path), *extra],
        capture_output=True,
        text=True,
    )


def _knowledge_with(replacements: dict) -> str:
    """V2_KNOWLEDGE with 'field: old' lines replaced (or dropped if None)."""
    content = V2_KNOWLEDGE
    for old, new in replacements.items():
        content = content.replace(old, new if new is not None else "")
    return content


# ─── Version dispatch ───────────────────────────────────────────────────────

class TestVersionDispatch:
    def test_valid_v2_file_passes(self, tmp_path):
        md = _write(tmp_path, "micro/test/knowledge/precos.md", V2_KNOWLEDGE)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 0, out
        assert "ERROR" not in out, out
        assert "V2-000" not in out, out  # migrated files carry no migration WARN

    def test_v1_file_gets_migration_warn(self, tmp_path):
        md = _write(tmp_path, "micro/test/knowledge/legacy.md", V1_VALID)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 0, out  # V2-000 is WARN, not ERROR
        assert "V2-000" in out, out
        assert "not yet migrated" in out, out

    def test_no_migration_warn_flag_suppresses_v2_000(self, tmp_path):
        md = _write(tmp_path, "micro/test/knowledge/legacy.md", V1_VALID)
        result = _run(md, "--no-migration-warn")
        out = result.stdout + result.stderr
        assert result.returncode == 0, out
        assert "V2-000" not in out, out

    def test_v1_rules_still_error_on_v1_file(self, tmp_path):
        content = V1_VALID.replace("type: knowledge\n", "")
        md = _write(tmp_path, "micro/test/knowledge/broken.md", content)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 1, out
        assert "V-010" in out, out  # v1 rule set unchanged


# ─── Tier 0 (V2-010..V2-018) ────────────────────────────────────────────────

class TestV2Tier0:
    def test_missing_status_is_error(self, tmp_path):
        content = _knowledge_with({"status: active\n": None})
        md = _write(tmp_path, "micro/test/knowledge/x.md", content)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 1, out
        assert "V2-010" in out, out

    def test_bad_type_enum_is_error(self, tmp_path):
        # 'memory' is a valid v1 type but not part of the 16-value v0.2 vocab
        content = _knowledge_with({"type: knowledge": "type: memory"})
        md = _write(tmp_path, "micro/test/knowledge/x.md", content)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 1, out
        assert "V2-011" in out, out

    def test_bad_status_enum_is_error(self, tmp_path):
        content = _knowledge_with({"status: active": "status: retired"})
        md = _write(tmp_path, "micro/test/knowledge/x.md", content)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 1, out
        assert "V2-017" in out, out

    def test_long_description_is_warn_at_160(self, tmp_path):
        content = _knowledge_with({
            "description: Reajuste aprovado em 2026-06-28; vigora o trimestre Q3":
                "description: " + "x" * 170,
        })
        md = _write(tmp_path, "micro/test/knowledge/x.md", content)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 0, out  # WARN only
        assert "V2-013" in out and "WARN" in out, out

    def test_timestamp_optional_but_must_match_created_at(self, tmp_path):
        content = V2_KNOWLEDGE.replace(
            "status: active\n", "status: active\ntimestamp: 2026-01-01\n"
        )
        md = _write(tmp_path, "micro/test/knowledge/x.md", content)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 1, out
        assert "V-070" in out, out


# ─── V2-020 type ↔ directory ────────────────────────────────────────────────

class TestV2DirMatch:
    def test_type_directory_mismatch_is_error(self, tmp_path):
        md = _write(tmp_path, "micro/test/decisions/x.md", V2_KNOWLEDGE)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 1, out
        assert "V2-020" in out, out

    def test_conflict_type_in_knowledge_dir_is_exempt(self, tmp_path):
        content = _knowledge_with({"type: knowledge": "type: conflict"})
        md = _write(tmp_path, "micro/test/knowledge/disputa.md", content)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 0, out
        assert "V2-020" not in out, out

    def test_shared_entities_maps_to_entity(self, tmp_path):
        content = _knowledge_with({"type: knowledge": "type: entity"})
        content = content.replace("---\n\nCorpo",
                                  "aliases: [gpq, grupo-pq]\n---\n\nCorpo")
        md = _write(tmp_path, "shared/entities/gpq.md", content)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 0, out
        assert "V2-020" not in out, out

    def test_layer_root_file_is_exempt_with_warn(self, tmp_path):
        md = _write(tmp_path, "shared/groups.md", V2_KNOWLEDGE)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 0, out  # exempt: no ERROR
        assert "V2-020" in out and "WARN" in out, out


# ─── V2-030 / V2-032 / V2-033 status coherence ─────────────────────────────

class TestV2StatusCoherence:
    def test_superseded_without_superseded_by_is_error(self, tmp_path):
        content = _knowledge_with({"status: active": "status: superseded"})
        md = _write(tmp_path, "micro/test/knowledge/x.md", content)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 1, out
        assert "V2-030" in out, out

    def test_superseded_by_without_superseded_status_is_error(self, tmp_path):
        content = V2_KNOWLEDGE.replace(
            "status: active\n",
            "status: active\nsuperseded_by: knowledge/precos-2026-q4.md\n",
        )
        md = _write(tmp_path, "micro/test/knowledge/x.md", content)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 1, out
        assert "V2-030" in out, out

    def test_deprecated_status_without_trio_is_error(self, tmp_path):
        content = _knowledge_with({"status: active": "status: deprecated"})
        md = _write(tmp_path, "micro/test/knowledge/x.md", content)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 1, out
        assert "V2-032" in out, out

    def test_deprecated_status_with_trio_passes(self, tmp_path):
        content = V2_KNOWLEDGE.replace(
            "status: active\n",
            "status: deprecated\n"
            "deprecated: true\n"
            "deprecated_at: 2026-07-01T00:00:00Z\n"
            "deprecated_reason: superseded by Q4 pricing\n",
        )
        md = _write(tmp_path, "micro/test/knowledge/x.md", content)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 0, out

    def test_quarantined_status_without_trio_is_error(self, tmp_path):
        content = _knowledge_with({"status: active": "status: quarantined"})
        md = _write(tmp_path, "micro/test/knowledge/x.md", content)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 1, out
        assert "V2-033" in out, out


# ─── V2-040 Tier 1 / V2-041 / V2-050 / V2-051 ──────────────────────────────

class TestV2Tier1AndTypeRules:
    def test_knowledge_without_epistemic_is_error(self, tmp_path):
        content = _knowledge_with({"epistemic: fact\n": None})
        md = _write(tmp_path, "micro/test/knowledge/x.md", content)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 1, out
        assert "V2-040" in out, out

    def test_missing_confidence_is_only_warn(self, tmp_path):
        content = _knowledge_with({"confidence: high\n": None})
        md = _write(tmp_path, "micro/test/knowledge/x.md", content)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 0, out
        assert "V2-040" in out and "WARN" in out, out

    def test_bad_epistemic_value_is_error(self, tmp_path):
        content = _knowledge_with({"epistemic: fact": "epistemic: guess"})
        md = _write(tmp_path, "micro/test/knowledge/x.md", content)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 1, out
        assert "V2-040" in out, out

    def test_bad_confidence_value_is_error(self, tmp_path):
        # 'medium' was valid v1 confidence; v0.2 uses high|likely|possible|low
        content = _knowledge_with({"confidence: high": "confidence: medium"})
        md = _write(tmp_path, "micro/test/knowledge/x.md", content)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 1, out
        assert "V2-040" in out, out

    def test_valid_until_before_valid_from_is_error(self, tmp_path):
        content = V2_KNOWLEDGE.replace(
            "observed_at: 2026-06-28\n",
            "observed_at: 2026-06-28\n"
            "valid_from: 2026-07-01\n"
            "valid_until: 2026-01-01\n",
        )
        md = _write(tmp_path, "micro/test/knowledge/x.md", content)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 1, out
        assert "V2-041" in out, out

    def test_entity_without_aliases_is_error(self, tmp_path):
        content = _knowledge_with({"type: knowledge": "type: entity"})
        md = _write(tmp_path, "micro/test/entities/gpq.md", content)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 1, out
        assert "V2-050" in out, out

    def test_intention_without_due_or_trigger_is_warn(self, tmp_path):
        content = _knowledge_with({"type: knowledge": "type: intention"})
        md = _write(tmp_path, "micro/test/intentions/followup.md", content)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 0, out  # WARN only
        assert "V2-051" in out, out


# ─── V2-060 secret trust gate ───────────────────────────────────────────────

class TestV2SecretGate:
    def test_secret_in_body_is_error(self, tmp_path):
        content = V2_KNOWLEDGE + "\nToken: sk-abcdefghij0123456789XYZa\n"
        md = _write(tmp_path, "micro/test/knowledge/x.md", content)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 1, out
        assert "V2-060" in out, out

    def test_secret_in_frontmatter_is_error(self, tmp_path):
        content = V2_KNOWLEDGE.replace(
            'ref: "session://tg-2026-06-28#dec-1"',
            'ref: "AKIAABCDEFGHIJKLMNOP"',
        )
        md = _write(tmp_path, "micro/test/knowledge/x.md", content)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 1, out
        assert "V2-060" in out, out

    def test_telegram_token_is_error(self, tmp_path):
        token = "123456789:" + "A" * 35
        content = V2_KNOWLEDGE + f"\nBot token {token} leaked.\n"
        md = _write(tmp_path, "micro/test/knowledge/x.md", content)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 1, out
        assert "V2-060" in out, out

    def test_masked_secret_is_allowed(self, tmp_path):
        content = V2_KNOWLEDGE + (
            "\nToken: sk-abcdefghij0123456789***\n"
            "Old key REDACTED: sk-abcdefghij0123456789ABCD\n"
        )
        md = _write(tmp_path, "micro/test/knowledge/x.md", content)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 0, out
        assert "V2-060" not in out, out

    def test_ellipsis_masked_secret_is_allowed(self, tmp_path):
        content = V2_KNOWLEDGE + "\nToken: sk-abcdefghij0123456789...\n"
        md = _write(tmp_path, "micro/test/knowledge/x.md", content)
        result = _run(md)
        out = result.stdout + result.stderr
        assert result.returncode == 0, out
        assert "V2-060" not in out, out


# ─── --report counters ──────────────────────────────────────────────────────

class TestReportCounters:
    def test_report_shows_v1_and_v2_counts(self, tmp_path):
        _write(tmp_path, "micro/test/knowledge/v2.md", V2_KNOWLEDGE)
        _write(tmp_path, "micro/test/knowledge/v1.md", V1_VALID)
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "--dir", str(tmp_path), "--report"],
            capture_output=True, text=True,
        )
        out = result.stdout + result.stderr
        assert result.returncode == 0, out
        assert "Schema v1 (pre-v0.2): 1" in out, out
        assert "Schema acervo/v0.2:   1" in out, out
