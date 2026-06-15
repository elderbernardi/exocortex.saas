# Fontes controladas — Hermes Agent e Hermes WebUI

Esta pasta registra a política local de fontes controladas para o runtime do Hermes Agent e a Web UI.

Objetivo:

- evitar consumo direto de upstream flutuante em produção;
- manter proveniência explícita de cada código-base crítico;
- separar estudo de upstream de promoção para runtime da instância.

## Regras operacionais

1. Nunca consumir `main`, `master`, `HEAD` ou equivalente upstream como produção.
2. Toda promoção deve partir de `provision/sources/sources.lock.yaml`.
3. `sync-upstreams.sh` é `dry-run` por padrão.
4. Qualquer clone/fetch local exige flags explícitas.
5. O script nunca faz `push`, `merge`, `rebase`, criação de PR ou mutação remota.
6. `sudo` é fora de escopo.

## Fontes registradas

### hermes-agent
- upstream oficial: `NousResearch/hermes-agent`
- URL: `https://github.com/NousResearch/hermes-agent.git`
- licença: `MIT`
- política: consumir apenas ref controlada e revisada localmente

### hermes-webui
- upstream comunitário: `nesquena/hermes-webui`
- URL: `https://github.com/nesquena/hermes-webui.git`
- licença: `MIT` — uso comercial irrestrito
- substitui: `EKKOLearnAI/hermes-web-ui` (BSL 1.1, removido em 2026-06-15)
- política: fork controlado com customizações do Exocórtex

## Arquivos desta pasta

- `provision/sources/sources.lock.yaml` — inventário pinado e política mínima por fonte
- `provision/sources/sync-upstreams.sh` — sincronização local segura, sem mutação remota

## Uso do script

Inspecionar sem mutar nada:

```bash
bash provision/sources/sync-upstreams.sh
```

Permitir apenas clonagem local de fontes ausentes:

```bash
bash provision/sources/sync-upstreams.sh --apply --clone-missing
```

Permitir apenas fetch local de fontes já clonadas:

```bash
bash provision/sources/sync-upstreams.sh --apply --fetch-existing
```

Definir outra raiz de worktrees locais:

```bash
bash provision/sources/sync-upstreams.sh --apply --clone-missing --workspace /tmp/exocortex-upstreams
```

## Notas de promoção

O lock contém refs auditadas por commit SHA completo para as duas fontes. A camada criada aqui serve para:

- registrar proveniência;
- bloquear uso casual de upstream flutuante;
- preparar futuros smokes e diffs locais antes de qualquer promoção para runtime;
- manter explícito que os forks controlados remotos ainda não foram criados.