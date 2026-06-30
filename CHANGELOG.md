# Changelog

All notable changes to Exocórtex.IA are documented here. Versions are git tags on
this repository (`elderbernardi/exocortex.saas`). The format is loosely based on
[Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## [1.1.0] — 2026-06-29

General Availability release. Closes the GA surface: Codex removed, installer
hardened, 4 optional services promoted to first-class, catalog docs truth-up.

### Removed
- OpenAI Codex integration (EX-32/33/34) and all associated wiring (installer
  steps, bundle references, skill files). Codex was never part of the stable
  skill surface.

### Changed
- DocBrain provisioned from `elderbernardi/docbrain` (tracking `main`); deps
  are refreshed (`npm install`) before every build/start. Note: this trades
  reproducibility for always-latest; pin `EXOCORTEX_DOCBRAIN_DIR` to a local
  checkout to freeze the version.
- Durable setup logs: installer output now written to
  `$HERMES_HOME/logs/setup/` and survives reruns.
- `step-12-verify-keys.sh` now validates the model-id format (rejects IDs with
  uppercase, spaces, or unexpected characters) before writing `config.yaml`.
- Cron creation is idempotent: `create_cron_if_missing` skips the call if the
  named cron already exists, preventing duplicate síndico entries.

### Added
- First-class provisioning for 4 optional services: **Context7** (MCP for tech
  docs, `docs/setup-context7.md`), **Hindsight** (Docker operational memory,
  `docs/setup-hindsight.md`), **Hermes WebUI** (cockpit fork,
  `provision/hermes-webui/README.md`), and **Firecrawl** (tiered scraping,
  `docs/setup-firecrawl.md`). Each service ships a provisioning script, health
  check, and smoke test.
- Supporting-Skills and Serviços Opcionais catalog sections in `FEATURES.md`.
- `README.md` — Release Notes v1.1.0 and Known Limitations sections; 57-skill
  count (43 EX-IDs + 15 supporting) and 7-category framing.

### Fixed
- Unguarded `rm -rf` in `step-06b-google-auth.sh` (google-auth hardening).
- Silent `npm run build` failure in DocBrain provisioning now surfaces as an
  explicit error and aborts the step.
- `persist-env` helper now correctly persists the `EXOCORTEX_ENABLE_CONTEXT7`
  toggle to `.env.local`.

## [1.0.8] — 2026-06-23

Add Acervo MCP/CLI control plane documentation and scripts.

## [1.0.7] — 2026-06-23

Make Acervo MCP validation stricter (treat warnings as errors).

## [1.0.6] — 2026-06-23

Follow-up to the 1.0.5 maintenance-cron fix: the crons still failed to reach the live
`~/.hermes` because a test run had leaked a temp `HERMES_HOME` into `.env.local`, and the
weekly síndico cron duplicated the legacy `Acervo Syndic` job.

### Fixed
- The interactive-setup test suite (`tests/test_interactive_setup.sh`) operated on the
  real `$REPO_ROOT/.env.local`: `setup_test_env` exports a temp `HERMES_HOME` that
  `interactive.sh`'s `save_to_env_local` persisted into the repo file, and T10/T11
  `cp`+`rm` over it. A leaked temp `HERMES_HOME` silently redirected later setup steps
  (notably `step-17` cron creation) to a dead `/tmp` home, so maintenance crons never
  landed in the live `~/.hermes`. The suite now backs up the real `.env.local` and
  restores it via `trap … EXIT`, and points `ENV_LOCAL_FILE` at each test's temp dir.

### Changed
- `step-17` + `scripts/activate-maintenance-crons.sh` now skip `maintenance-weekly` when
  the legacy `Acervo Syndic` cron exists (same Sunday 03:00 slot / syndic scope), avoiding
  a double síndico run. On a fresh install `maintenance-weekly` attaches its skills via
  `--skill` (`excrtx-harness-maintenance`, `excrtx-memory-syndic`) instead of only naming
  them in the prompt; `create_cron_if_missing` forwards extra args to `hermes cron create`.

## [1.0.5] — 2026-06-23

Post-provisioning smoke-test hardening: fixes surfaced by running the EX-* smoke suite on a
fresh box — runtime memory writes, maintenance cron scheduling, and two memory-skill
documentation divergences.

### Fixed
- `exocortex_runtime_guard.py` resolved the Acervo write-scope root from its own
  **script location** (installer clone, `~/.exocortex-installer/acervo`) instead of the
  live Acervo (`$EXOCORTEX_HOME/acervo`), so every legitimate WRITE was denied as a
  false cross-microverso violation — leaving **EX-11 (excrtx-memory-manager)
  non-operational for writes** in production. The guard now resolves the root from the
  environment (`$ACERVO` > `$EXOCORTEX_HOME/acervo` > `$HERMES_HOME/acervo` > repo
  fallback) and `excrtx-memory-manager` passes `--acervo-root "$ACERVO"` explicitly.
- Maintenance cron creation (`step-17` + `scripts/activate-maintenance-crons.sh`) passed
  `--schedule`/`--prompt` flags, but `hermes cron create` takes `schedule` and `prompt` as
  **positional** args — so all 5 síndico crons failed with `unrecognized arguments` and the
  autonomous maintenance (ADR-018) never ran. Switched to positional args; `step-17` now also
  surfaces the real `hermes` error instead of swallowing stderr.

### Changed
- `excrtx-memory-opsmemory` (EX-16): the conflict-precedence table now mirrors the
  SOUL-injected memory-routing protocol — `SOUL > contratos > Acervo > session_search >
  provider (Hindsight) > memória rápida` — resolving a divergence where the skill ranked
  built-in memory above the Acervo and the provider dead-last while the runtime SOUL block
  placed Hindsight above fast memory. Clarifies that *usage* (Hindsight is recall-first)
  and *conflict authority* (provider stays below the Acervo) are distinct axes.
- `excrtx-memory-intake` (EX-17): `remediation_tip` now references the canonical 5-phase
  Standard Flow (Reception · Manifest · Extraction · Triage · Promotion) instead of a
  compressed 4-step list, removing the 4-vs-5 stage-count ambiguity. The EX-17 smoke prompt
  (`test-registry.sh`, `migrate_calibration_metadata.py`) was also asking for "4 estágios" —
  now aligned to the 5 phases so the check no longer reports a spurious count divergence.

## [1.0.4] — 2026-06-22

### Fixed
- `step-12-verify-keys.sh` now **persists the resolved `default` role API key** into
  `$HERMES_HOME/.env` under the provider's env var (from `providers.json`
  `legacy_key_env`). Hermes resolves the LLM credential from the environment
  (`PROVIDER_REGISTRY[provider].api_key_env_vars`), not `config.yaml`, so setting only
  `model.provider/default/base_url` left `hermes chat` with no `Authorization` header
  → **HTTP 401: Missing Authentication header** in the post-provisioning smoke tests.
  Idempotent upsert; preserves commented templates; `chmod 600`.
- `provision_memory_routing.py` now **probes Hindsight** (client module + API TCP reach)
  and skips the AcervoIndex scan with a clear `skipped` reason instead of crashing with
  `ModuleNotFoundError: hindsight_client` when Hindsight is not provisioned (it is opt-in
  via `EXOCORTEX_ENABLE_HINDSIGHT`). The provisioner no longer reports `ok:false` for
  absent optional infra.
- `step-06b-google-auth.sh` retries the Google Workspace pip install with
  `--user --break-system-packages` on **PEP 668** externally-managed environments
  (Debian/Ubuntu), where a bare `pip install` — and even `--user` — is rejected.

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
