# Hermes Web UI — provisionador opinado do Exocórtex

Provisiona o `hermes-web-ui` como cockpit operacional do `exocortex.saas` com:

- container reproduzível
- runtime Hermes persistido em volume próprio
- bootstrap do setup do Exocórtex dentro do container
- hardening mínimo de credenciais, pin de upstream e bind local
- smoke suite e rotinas simples de backup/restore

## Estrutura

```text
provision/hermes-web-ui/
  docker/
    Dockerfile.ui
    compose.yml
  env/
    .env.example
    secrets.schema
  scripts/
    common.sh
    install.sh
    bootstrap-admin.sh
    bootstrap-profiles.sh
    bootstrap-exocortex.sh
    smoke.sh
    backup.sh
    restore.sh
  systemd/
    exocortex-hermes-ui.service
  patches/
    upstream/
    exocortex/
  manifests/
    caddy/
    k8s/
```

## Uso rápido

```bash
cd provision/hermes-web-ui
cp env/.env.example env/.env
bash scripts/install.sh
```

O instalador:

1. materializa `env/.env` se necessário
2. gera segredos locais se ainda estiverem em placeholder
3. sobe o container da UI
4. executa o `setup.sh` do Exocórtex dentro do container
5. fixa o admin da UI e perfis padrão
6. roda smoke tests

## Princípios de operação

- bind host publicado em `127.0.0.1` por padrão; `tailscale-auto` resolve o IPv4 atual da tailnet
- `AUTH_JWT_SECRET` sempre explícito
- senha default do upstream nunca é mantida
- repo/ref da Web UI resolvidos por `provision/sources/sources.lock.yaml` quando `env/.env` deixa `EXOCORTEX_HERMES_WEB_UI_REPO_URL` e `EXOCORTEX_HERMES_WEB_UI_REF` em branco
- refs auditadas usam commit SHA completo; `main`/`master`/`HEAD` não são refs de produção
- refs flutuantes (`main`/`master`/`HEAD`) só passam com `EXOCORTEX_ALLOW_FLOATING_UPSTREAM_REF=1`
- perfis elegíveis para autostart ficam limitados a `default,manut`
- `CORS_ORIGINS` é obrigatório quando `EXOCORTEX_UI_BIND_IP` sai de loopback; no modo `tailscale-auto` ele é derivado se estiver vazio
- `setup.sh` roda com `EXOCORTEX_SKIP_HERMES_WEB_UI_SETUP_STEP=1` para evitar recursão

## Fontes controladas

A trilha barebone usa `provision/sources/` como camada de proveniência. O lock atual registra:

- Hermes Agent oficial: `NousResearch/hermes-agent`, licença `MIT`;
- Web UI/Studio: `EKKOLearnAI/hermes-web-ui` com redirecionamento observado para `EKKOLearnAI/hermes-studio`;
- alerta de licença da Web UI/Studio: `BSL 1.1`, `Change Date 2029-05-10`, `Change License Apache-2.0`, `commercial_use_requires_license: true`.

O script `provision/sources/sync-upstreams.sh` é dry-run por padrão e nunca faz `push`, `merge`, `rebase`, tag, PR ou mutação remota.

## Limites desta primeira entrega

Esta camada ainda mantém o provisionador Docker legado como trilha operacional, mas já resolve repo/ref da Web UI a partir do lock de fontes quando o env deixa esses campos em branco. A migração barebone por usuário Unix, o hardening profundo de ownership, write-approval nativo e superfícies cognitivas próprias ficam na próxima rodada.

Política de fontes controladas da trilha barebone: `provision/sources/README.md`.
