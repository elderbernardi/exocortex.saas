# Report Format — Detailed Reference

Detailed reference for the syndic summary report and cron configuration.
Extracted from `SKILL.md` to keep the skill body compact. The format is
fixed by ADR-018. The executive communicates in PT-BR, so the report is
localized to PT-BR.

## Report Template (PT-BR)

```
[RELATÓRIO DO SÍNDICO] 2026-06-22
====================================
Escaneados: 127 arquivos em 10 microversos
Quarentenados: 3 arquivos
  - micro/exocortex-dev/knowledge/old-model-config.md (stale: 95 days)
  - micro/exocortex-ops/context/port-numbers-v1.md (stale: 102 days)
  - micro/exocortex-dev/knowledge/deprecated-api.md (deprecated: 185 days)
Purgados: 1 arquivo
  - micro/exocortex-ops/knowledge/old-pricing.md (quarantine expired)
Candidatos a consolidação: 2 (flagged for review)
  - micro/exocortex-dev/knowledge/ — 3 arquivos sobre model defaults
  - micro/exocortex-ops/context/ — 2 arquivos sobre port configuration
Ocupação da quarentena: 4 arquivos
Próxima janela de purga: 2026-07-22
```

> Note: file paths inside the report stay in their original filesystem form
> (English ASCII, `$ACERVO`-relative). Only the human-readable labels are
> translated.

## Field semantics

| Field | Source |
|-------|--------|
| `Escaneados` (Scanned) | Total `.md` files with frontmatter walked in Step 1 (including immune files). `em N microversos` = count of microverso directories under `micro/` that contributed at least one scanned file. |
| `Quarentenados` (Quarantined) | Count of files successfully quarantined in Step 4. Each file listed with `$ACERVO`-relative path and reason tag (`stale: N days` or `deprecated: N days`). |
| `Purgados` (Purged) | Count of files successfully purged in Step 5. Each file listed with original `$ACERVO`-relative path and `(quarantine expired)`. |
| `Candidatos a consolidação` (Consolidation candidates) | Count of consolidation groups flagged in Step 6. Each group listed with container path, file count, and shared topic. |
| `Ocupação da quarentena` (Quarantine occupancy) | Total files currently in `$ACERVO/.quarantine/` at end of cycle (after quarantines and purges). |
| `Próxima janela de purga` (Next purge window) | The earliest `quarantine_expires_at` among files still in `.quarantine/` at end of cycle. If quarantine is empty, print `(quarentena vazia)`. |

## Error section (conditional)

If any file failed to quarantine or purge (Step 4 or Step 5 fail-safe), append:

```
Erros: 1
  - micro/exocortex-dev/knowledge/locked-file.md (quarantine failed: permission denied)
```

The cycle is still considered complete — errors are reported, not hidden.

## Zero-action report

If the cycle found nothing to quarantine or purge, the report still runs:

```
[RELATÓRIO DO SÍNDICO] 2026-06-22
====================================
Escaneados: 127 arquivos em 10 microversos
Quarentenados: 0 arquivos
Purgados: 0 arquivos
Candidatos a consolidação: 0
Ocupação da quarentena: 0 arquivos
Próxima janela de purga: (quarentena vazia)
```

A zero-action report confirms the syndic ran and the Acervo is clean. No report
at all means the syndic did not run — that is the silent-failure signal
(ADR-018, Risk).

## Cron Configuration

The syndic runs as a weekly cron job under the `manut` profile.

### Schedule

```
Schedule: weekly (suggested: Sunday 03:00 UTC)
Profile: manut
Skill: excrtx-memory-syndic
Output: summary report → executive's home channel
```

### Hermes cron setup

In the Hermes cron configuration (under `~/.hermes/profiles/manut/cron/` or the
equivalent profile-scoped cron directory), create an entry that:

1. Activates the `manut` profile.
2. Invokes the `excrtx-memory-syndic` skill (full cycle).
3. Captures the summary report as stdout.
4. Delivers stdout to the executive's home channel (the channel configured as
   the executive's primary notification destination).

### Manual invocation

The executive can trigger the cycle on demand:

```bash
hermes -p manut  # then: "run syndic" or "clean the acervo"
```

The manual invocation runs the same six-step pipeline and produces the same
report. There is no "dry-run" mode — the syndic's safety net is the 30-day
quarantine window, not a preview step.

### Silent-failure detection

If the cron job fails to run (misconfiguration, profile error, system down),
**no report appears** in the executive's home channel. The absence of the
weekly report is the failure signal. The executive should expect a report
every week; if one does not arrive, investigate the cron configuration.
