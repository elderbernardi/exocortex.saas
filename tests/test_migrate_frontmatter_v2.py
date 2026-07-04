#!/usr/bin/env python3
"""
Tests for scripts/migrate_frontmatter_v2.py (v1.0.0 → schema v0.2, ADR-023).

Creates temporary directories with v1-schema content, runs the v2 migrator,
and verifies status derivation, epistemic defaults, nature handling,
idempotency, and dry-run safety.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
MIGRATOR = REPO_ROOT / "scripts" / "migrate_frontmatter_v2.py"

# Post-v1-migration content (OKF v0.1 superset schema, ADR-013)
_V1_KNOWLEDGE_CONTENT = """\
---
type: knowledge
title: Preço do Produto
description: Preço atual do produto
tags: [produto, preco]
timestamp: 2026-06-01
class: volátil
created_at: 2026-06-01T00:00:00Z
excrtx_type: fact
nature: knowledge
confidence: medium
---

# Preço do Produto

Preço atual: R$ 150,00.
"""

_V1_DEPRECATED_CONTENT = """\
---
type: knowledge
title: Modelo default antigo
description: Modelo anterior, substituído
tags: [model]
timestamp: 2026-05-01
class: volátil
created_at: 2026-05-01T00:00:00Z
deprecated: true
deprecated_at: 2026-06-19T10:30:00Z
deprecated_reason: "Superseded by knowledge/modelo-v2.md"
nature: knowledge
---

Modelo antigo.
"""

_V1_QUARANTINED_CONTENT = """\
---
type: context
title: Sprint status março
description: Snapshot de sprint, obsoleto
tags: [sprint]
timestamp: 2026-03-01
class: volátil
created_at: 2026-03-01T00:00:00Z
quarantined_at: 2026-06-19T03:00:00Z
quarantine_reason: "Not accessed in 92 days"
quarantine_expires_at: 2026-07-19T03:00:00Z
nature: context
---

Snapshot obsoleto.
"""

_V1_DECISION_CONTENT = """\
---
type: decision
title: Adotar Hermes como runtime
description: Decisão de arquitetura
tags: [architecture]
timestamp: 2026-06-11
class: perene
created_at: 2026-06-11T00:00:00Z
nature: decisions
---

# Decisão

Hermes é o runtime.
"""

_V1_ARTIFACT_CONTENT = """\
---
type: artifact
title: Template de proposta
description: Template reutilizável
tags: [template]
timestamp: 2026-06-11
class: volátil
created_at: 2026-06-11T00:00:00Z
nature: templates
---

Template.
"""

# nature says `context` but the file lives in knowledge/ → needs-review
_V1_NATURE_MISMATCH_CONTENT = """\
---
type: knowledge
title: Fato com nature errado
description: nature diverge do diretório
tags: []
timestamp: 2026-06-11
class: volátil
created_at: 2026-06-11T00:00:00Z
nature: context
---

Fato.
"""

# No nature at all → derived from directory
_V1_NO_NATURE_CONTENT = """\
---
type: knowledge
title: Fato sem nature
description: nature ausente
tags: []
timestamp: 2026-06-11
class: volátil
created_at: 2026-06-11T00:00:00Z
---

Fato.
"""


def _make_acervo_file(base: Path, rel_path: str, content: str) -> Path:
    """Write content under base/micro/test-domain/<rel_path>."""
    target = base / "micro" / "test-domain" / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target


def _run_migrator(target_dir: Path, *extra_args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(MIGRATOR), "--dir", str(target_dir)] + list(extra_args),
        capture_output=True,
        text=True,
    )


def _frontmatter(text: str) -> str:
    """Return the raw frontmatter block (between the --- fences)."""
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match, "migrated file has no frontmatter block"
    return match.group(1)


# ─── Core migration rules ────────────────────────────────────────────────────

class TestCoreMigrationRules:
    def test_exits_0_on_success(self, tmp_path):
        _make_acervo_file(tmp_path, "knowledge/preco.md", _V1_KNOWLEDGE_CONTENT)
        result = _run_migrator(tmp_path)
        assert result.returncode == 0, result.stdout + result.stderr

    def test_schema_added_as_first_key(self, tmp_path):
        target = _make_acervo_file(tmp_path, "knowledge/preco.md", _V1_KNOWLEDGE_CONTENT)
        _run_migrator(tmp_path)
        migrated = target.read_text(encoding="utf-8")
        fm = _frontmatter(migrated)
        assert fm.split("\n")[0] == "schema: acervo/v0.2", (
            f"Expected 'schema: acervo/v0.2' as first frontmatter key, got:\n{fm}"
        )

    def test_existing_fields_preserved(self, tmp_path):
        target = _make_acervo_file(tmp_path, "knowledge/preco.md", _V1_KNOWLEDGE_CONTENT)
        _run_migrator(tmp_path)
        migrated = target.read_text(encoding="utf-8")
        for field in ("excrtx_type: fact", "timestamp: 2026-06-01",
                      "created_at: 2026-06-01T00:00:00Z", "nature: knowledge",
                      "class: volátil"):
            assert field in migrated, f"Expected {field!r} to be preserved"
        assert "Preço atual: R$ 150,00." in migrated, "Body must be preserved"

    def test_confidence_medium_remapped_to_likely(self, tmp_path):
        target = _make_acervo_file(tmp_path, "knowledge/preco.md", _V1_KNOWLEDGE_CONTENT)
        _run_migrator(tmp_path)
        migrated = target.read_text(encoding="utf-8")
        assert "confidence: likely" in migrated
        assert "confidence: medium" not in migrated


# ─── Status derivation ───────────────────────────────────────────────────────

class TestStatusDerivation:
    def test_plain_file_gets_status_active(self, tmp_path):
        target = _make_acervo_file(tmp_path, "knowledge/preco.md", _V1_KNOWLEDGE_CONTENT)
        _run_migrator(tmp_path)
        assert "status: active" in target.read_text(encoding="utf-8")

    def test_deprecated_file_gets_status_deprecated(self, tmp_path):
        target = _make_acervo_file(tmp_path, "knowledge/modelo.md", _V1_DEPRECATED_CONTENT)
        _run_migrator(tmp_path)
        migrated = target.read_text(encoding="utf-8")
        assert "status: deprecated" in migrated
        # deprecation trio preserved (V2-032 requires it alongside status)
        assert "deprecated: true" in migrated
        assert "deprecated_at: 2026-06-19T10:30:00Z" in migrated

    def test_quarantined_file_gets_status_quarantined(self, tmp_path):
        target = _make_acervo_file(tmp_path, "context/sprint.md", _V1_QUARANTINED_CONTENT)
        _run_migrator(tmp_path)
        migrated = target.read_text(encoding="utf-8")
        assert "status: quarantined" in migrated
        assert "quarantined_at: 2026-06-19T03:00:00Z" in migrated

    def test_superseded_by_gets_status_superseded(self, tmp_path):
        content = _V1_KNOWLEDGE_CONTENT.replace(
            "confidence: medium",
            "confidence: medium\nsuperseded_by: knowledge/preco-v2.md",
        )
        target = _make_acervo_file(tmp_path, "knowledge/preco.md", content)
        _run_migrator(tmp_path)
        assert "status: superseded" in target.read_text(encoding="utf-8")

    def test_status_inserted_after_class(self, tmp_path):
        target = _make_acervo_file(tmp_path, "knowledge/preco.md", _V1_KNOWLEDGE_CONTENT)
        _run_migrator(tmp_path)
        fm_lines = _frontmatter(target.read_text(encoding="utf-8")).split("\n")
        keys = [line.split(":")[0] for line in fm_lines if line and not line.startswith(" ")]
        assert keys.index("status") == keys.index("class") + 1, (
            f"Expected 'status' right after 'class', got key order: {keys}"
        )


# ─── Epistemic defaults ──────────────────────────────────────────────────────

class TestEpistemicDefaults:
    def test_knowledge_defaults_to_fact(self, tmp_path):
        target = _make_acervo_file(tmp_path, "knowledge/preco.md", _V1_KNOWLEDGE_CONTENT)
        _run_migrator(tmp_path)
        assert "epistemic: fact" in target.read_text(encoding="utf-8")

    def test_context_defaults_to_fact(self, tmp_path):
        target = _make_acervo_file(tmp_path, "context/sprint.md", _V1_QUARANTINED_CONTENT)
        _run_migrator(tmp_path)
        assert "epistemic: fact" in target.read_text(encoding="utf-8")

    def test_decision_defaults_to_decision(self, tmp_path):
        target = _make_acervo_file(tmp_path, "decisions/runtime.md", _V1_DECISION_CONTENT)
        _run_migrator(tmp_path)
        assert "epistemic: decision" in target.read_text(encoding="utf-8")

    def test_non_epistemic_type_gets_no_epistemic(self, tmp_path):
        target = _make_acervo_file(tmp_path, "templates/proposta.md", _V1_ARTIFACT_CONTENT)
        _run_migrator(tmp_path)
        assert "epistemic:" not in target.read_text(encoding="utf-8")

    def test_existing_epistemic_not_overwritten(self, tmp_path):
        content = _V1_KNOWLEDGE_CONTENT.replace(
            "confidence: medium", "confidence: medium\nepistemic: hypothesis"
        )
        target = _make_acervo_file(tmp_path, "knowledge/preco.md", content)
        _run_migrator(tmp_path)
        migrated = target.read_text(encoding="utf-8")
        assert "epistemic: hypothesis" in migrated
        assert migrated.count("epistemic:") == 1


# ─── Nature handling ─────────────────────────────────────────────────────────

class TestNatureHandling:
    def test_absent_nature_derived_from_directory(self, tmp_path):
        target = _make_acervo_file(tmp_path, "knowledge/fato.md", _V1_NO_NATURE_CONTENT)
        _run_migrator(tmp_path)
        assert "nature: knowledge" in target.read_text(encoding="utf-8")

    def test_mismatched_nature_not_changed_and_reported(self, tmp_path):
        target = _make_acervo_file(
            tmp_path, "knowledge/fato.md", _V1_NATURE_MISMATCH_CONTENT
        )
        result = _run_migrator(tmp_path, "--report")
        migrated = target.read_text(encoding="utf-8")
        assert "nature: context" in migrated, "Mismatched nature must not be changed"
        assert "nature: knowledge" not in migrated
        assert "needs-review" in result.stdout
        assert "Needs review:    1" in result.stdout


# ─── Idempotency & dry-run ───────────────────────────────────────────────────

class TestIdempotencyAndDryRun:
    def test_second_run_changes_nothing(self, tmp_path):
        targets = [
            _make_acervo_file(tmp_path, "knowledge/preco.md", _V1_KNOWLEDGE_CONTENT),
            _make_acervo_file(tmp_path, "knowledge/modelo.md", _V1_DEPRECATED_CONTENT),
            _make_acervo_file(tmp_path, "context/sprint.md", _V1_QUARANTINED_CONTENT),
            _make_acervo_file(tmp_path, "decisions/runtime.md", _V1_DECISION_CONTENT),
        ]
        _run_migrator(tmp_path)
        first_pass = [t.read_text(encoding="utf-8") for t in targets]
        result = _run_migrator(tmp_path)
        second_pass = [t.read_text(encoding="utf-8") for t in targets]
        assert first_pass == second_pass, "Second run must change nothing"
        assert f"Already v0.2:    {len(targets)}" in result.stdout
        assert "Migrated:        0" in result.stdout

    def test_dry_run_does_not_modify_files(self, tmp_path):
        target = _make_acervo_file(tmp_path, "knowledge/preco.md", _V1_KNOWLEDGE_CONTENT)
        result = _run_migrator(tmp_path, "--dry-run", "--report")
        assert target.read_text(encoding="utf-8") == _V1_KNOWLEDGE_CONTENT, (
            "Dry-run must not modify files on disk"
        )
        assert result.returncode == 0
        assert "WOULD MIGRATE" in result.stdout


# ─── Scope & edge cases ──────────────────────────────────────────────────────

class TestEdgeCases:
    def test_nonexistent_dir_exits_nonzero(self):
        result = subprocess.run(
            [sys.executable, str(MIGRATOR), "--dir", "/nonexistent/path/xyz"],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0

    def test_excluded_dirs_and_readme_not_touched(self, tmp_path):
        excluded = tmp_path / "_inbox" / "item.md"
        excluded.parent.mkdir(parents=True)
        excluded.write_text(_V1_KNOWLEDGE_CONTENT, encoding="utf-8")
        readme = tmp_path / "README.md"
        readme.write_text("# Readme\n", encoding="utf-8")
        result = _run_migrator(tmp_path)
        assert result.returncode == 0
        assert excluded.read_text(encoding="utf-8") == _V1_KNOWLEDGE_CONTENT
        assert readme.read_text(encoding="utf-8") == "# Readme\n"

    def test_file_without_frontmatter_skipped(self, tmp_path):
        target = _make_acervo_file(tmp_path, "knowledge/raw.md", "# Sem frontmatter\n")
        result = _run_migrator(tmp_path)
        assert result.returncode == 0
        assert target.read_text(encoding="utf-8") == "# Sem frontmatter\n"
        assert "Skipped:         1" in result.stdout

    def test_single_file_mode(self, tmp_path):
        target = _make_acervo_file(tmp_path, "knowledge/preco.md", _V1_KNOWLEDGE_CONTENT)
        result = subprocess.run(
            [sys.executable, str(MIGRATOR), "--file", str(target)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        migrated = target.read_text(encoding="utf-8")
        assert "schema: acervo/v0.2" in migrated
        assert "status: active" in migrated


# ── Type alignment & status normalization (V2-020 / V2-017 support) ─────────

def _mini(type_, extra=""):
    return f"""---
type: {type_}
title: Teste
description: Teste
tags: []
timestamp: 2026-06-11
class: perene
created_at: 2026-06-11T00:00:00Z
{extra}---

Corpo.
"""


class TestTypeAndStatusAlignment:
    def test_type_aligned_to_directory(self, tmp_path):
        t = _make_acervo_file(tmp_path, "contracts/regra.md", _mini("knowledge"))
        _run_migrator(tmp_path)
        assert "type: contract" in _frontmatter(t.read_text(encoding="utf-8"))

    def test_conflict_type_not_realigned(self, tmp_path):
        t = _make_acervo_file(tmp_path, "knowledge/disputa.md", _mini("conflict"))
        _run_migrator(tmp_path)
        assert "type: conflict" in _frontmatter(t.read_text(encoding="utf-8"))

    def test_legacy_status_accepted_normalized(self, tmp_path):
        t = _make_acervo_file(tmp_path, "decisions/adr-x.md",
                              _mini("decision", "status: accepted\n"))
        _run_migrator(tmp_path)
        fm = _frontmatter(t.read_text(encoding="utf-8"))
        assert "status: active" in fm and "status: accepted" not in fm

    def test_unknown_status_left_and_flagged(self, tmp_path):
        t = _make_acervo_file(tmp_path, "decisions/adr-y.md",
                              _mini("decision", "status: em-analise\n"))
        r = _run_migrator(tmp_path, "--report")
        assert "status: em-analise" in _frontmatter(t.read_text(encoding="utf-8"))
        assert "not in v0.2 enum" in r.stdout
