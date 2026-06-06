# DRAFT Issue — Browser Automation bloqueada por ausência de uv e path divergente

## Feature

EX-30 — Browser Automation

## Prioridade

P1

## Comportamento observado

O wrapper existe e é executável:

`~/.hermes/skills/exocortex/excrtx-integrate-browser/scripts/browser-use.sh`

Mas aborta com:

`uv not found`

Também há divergência documental:

- FEATURES cita `.agent/skills/.../excrtx-integrate-browser.sh`.
- Skill real usa `scripts/browser-use.sh`.

## Impacto

Automação de browser não inicia em ambiente provisionado. O usuário recebe instrução de instalação em vez de feature operacional.

## Critérios de aceite

- [ ] Setup instala/valida `uv` para EX-30.
- [ ] FEATURES e skill usam o mesmo wrapper/path.
- [ ] Smoke abre `https://example.com`, lê título e fecha sessão.
