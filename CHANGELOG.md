# Changelog

All notable changes to Exocórtex.IA are documented here. Versions are git tags on
this repository (`elderbernardi/exocortex.saas`). The format is loosely based on
[Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Changed
- **LLM key management consolidated into 3 roles** (`default` / `vision` / `auxiliar`).
  All LLM configuration is now a single source of truth: each role is a quad
  `EXOCORTEX_<ROLE>_{PROVIDER,MODEL,API_KEY,BASE_URL}`. `default` is always used;
  `vision` and `auxiliar` inherit `default` field-by-field when unset. This replaces
  the ~20 scattered keys (`OPENROUTER_API_KEY`, `DEEPSEEK_API_KEY`, `OPENCODE_API_KEY`,
  `DOCBRAIN_LLM_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, …) and the 3 independent
  provider-resolution implementations.

### Added
- `setup/providers.json` — single provider catalog (base URLs + capabilities), removing
  hardcoded endpoints from `skill_judge.py`, `calibrate-hermes.py` and `last30days`.
- `scripts/lib/llm_roles.py` (Python) and `setup/lib/llm-roles.sh` (shell) — the single
  role resolver, with field-by-field inheritance and catalog-derived base URLs. The
  shell wrapper delegates to the Python module for identical behavior.
- `scripts/migrate-env-roles.py` — idempotent one-shot migration of legacy LLM keys into
  the 3 roles (run automatically by `setup.sh`); preserves non-LLM service keys, comments
  the migrated legacy keys, and writes a `.env.local.pre-roles.bak` backup.
- `step-12-verify-keys.sh` now does a **real ping (1 call) per role** during install —
  catching invalid keys / wrong model ids / unreachable endpoints early with a specific
  message — and **writes `config.yaml`** from the `default` role (skippable via
  `--yes`/`EXOCORTEX_NO_PING=1`).

### Migration
- Existing installs: `setup.sh` migrates the old `.env.local` automatically. Manually:
  `python3 scripts/migrate-env-roles.py --dry-run`. DocBrain and the Hindsight LLM backend
  now derive their credentials from the `auxiliar` role (which inherits `default`).

## [1.0.3] — 2026-06-22

### Fixed
- `step-12-verify-keys.sh`: provider ids containing a hyphen (e.g. `opencode-go`)
  produced an invalid shell variable name (`OPENCODE-GO_API_KEY`), breaking the
  `${!var}` indirect expansion and **aborting `setup.sh` under `set -e`** before
  steps 13 (final verification), 14 (validators) and 17 (crons) could run. The
  provider name is now sanitized to a valid identifier (hyphen → underscore) and
  the indirect lookup is guarded by an identifier regex. Regression in v1.0.2.

## [1.0.2] — 2026-06-21

Production-grade hardening release: a reliable installer and agent docs on par with
the real provisioning state. Closes the remaining blockers from the 2026-06-19
acervo-harness stress test (`docs/audits/2026-06-19_acervo-harness-stress/findings.md`)
and folds in the memory-routing reform.

### Added
- `scripts/validate_log.py` — enforces the `log.md` convention (§1–§3): single `# Log`
  H1, `## YYYY-MM-DD` headings in ascending order, single-line typed bullets, and the
  `macro/`-has-no-log rule. Wired into `step-14` as a **non-fatal gate** — legacy
  free-text logs only WARN; a `log.md` under `macro/` is the sole ERROR. (**F-014**)
- Memory-routing reform: Hindsight tools-first routing + AcervoIndex write hook and
  daily reconciliation cron (`scripts/provision_memory_routing.py`,
  `scripts/smoke_memory_routing.py`, wired into `setup.sh` and `step-13`).
- INSTALL.md now documents **Step 10c** (Acervo workspace registration in the WebUI),
  the **`--imbroke`** OpenRouter-free contingency, and the canonical LLM model.

### Changed
- `step-12-verify-keys.sh` inspects `$HERMES_HOME/config.yaml` **non-destructively**:
  warns on a case-mismatched `model.default` (e.g. `MiniMax-M3` vs `minimax-m3`) and on
  provider/key gaps, and recommends the canonical tested model **`deepseek-v4-pro`**
  (via `DEEPSEEK_API_KEY`). It never rewrites the config. (**F-030 / F-031**)
- Provisioning-test outputs (report + repair manifests/patches) now write to
  `$HERMES_HOME/reports/provisioning` (override with `EXOCORTEX_REPORT_DIR`) instead of
  the canonical Acervo, so test runs no longer pollute semantic memory. Shared by
  `test-helpers.sh` and `sync-repairs-to-repo.sh`. (**F-003**)
- Docs reconciled to reality: skill count corrected to **50** `excrtx-*` skills
  (52 packages total) across `INSTALL.md`, `README.md`, `HARNESS.md`; feature catalog
  noted as 46 features (EX-01..EX-58). `step-13` final banner reflects production v1.0.2.

### Verified (already resolved in the seed; no change needed)
- **F-050** — the four pages that had malformed YAML frontmatter now pass
  `validate_frontmatter.py` (0 errors over the whole seed Acervo).
- **F-032** — memory-writing skills resolve an absolute `$ACERVO` (no cwd-relative
  writes remain).

### Notes
- Out of scope: the `last30days` integration test failures (**F-016**) are unrelated to
  the Exocórtex harness and are not release-gating.

## [1.0.1]
Prior candidate-release tag. See git history.

## [1.0.0] / [1.0.0-rc2]
Initial candidate releases.
