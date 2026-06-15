# Fontes controladas — Hermes Agent e Web UI/Studio

Esta pasta registra a política local de fontes controladas para a trilha barebone da Hermes Web UI.

Objetivo:

- evitar consumo direto de upstream flutuante em produção;
- manter proveniência explícita de cada código-base crítico;
- separar estudo de upstream de promoção para runtime da instância;
- preservar alerta de licença da Web UI/Studio.

## Regras operacionais

1. Nunca consumir `main`, `master`, `HEAD` ou equivalente upstream como produção.
2. Toda promoção deve partir de `provision/sources/sources.lock.yaml`.
3. `sync-upstreams.sh` é `dry-run` por padrão.
4. Qualquer clone/fetch local exige flags explícitas.
5. O script nunca faz `push`, `merge`, `rebase`, criação de PR ou mutação remota.
6. `sudo` é fora de escopo.
7. Telegram, CLI e Web UI devem convergir para o mesmo plano de execução da instância; a camada de fontes controladas existe para reduzir drift entre superfícies.

## Fontes registradas

### hermes-agent
- upstream oficial: `NousResearch/hermes-agent`
- URL: `https://github.com/NousResearch/hermes-agent.git`
- licença: `MIT`
- política: consumir apenas ref controlada e revisada localmente

### hermes-web-ui / hermes-studio
- upstream observado: `EKKOLearnAI/hermes-web-ui`
- redirecionamento observado: `EKKOLearnAI/hermes-studio`
- licença observada: `BSL 1.1`
- `Change Date`: `2029-05-10`
- `Change License`: `Apache-2.0`
- alerta: `commercial_use_requires_license: true`

Implicação: este componente não deve ser tratado como base liberada para uso comercial/SaaS do Exocórtex antes da revisão jurídica/comercial ou licença apropriada.

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

O lock já contém refs auditadas por commit SHA completo para as duas fontes. O provisionador da Web UI consome o lock quando `EXOCORTEX_HERMES_WEB_UI_REPO_URL` e `EXOCORTEX_HERMES_WEB_UI_REF` ficam em branco no env.

A camada criada aqui serve para:

- registrar proveniência;
- bloquear uso casual de upstream flutuante;
- preparar futuros smokes e diffs locais antes de qualquer promoção para runtime barebone;
- manter explícito que os mirrors/forks remotos controlados ainda não foram criados.