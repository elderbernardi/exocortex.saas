# Changelog

All notable changes to Exocórtex.IA are documented here. Versions are git tags on
this repository (`elderbernardi/exocortex.saas`). The format is loosely based on
[Keep a Changelog](https://keepachangelog.com/).

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
