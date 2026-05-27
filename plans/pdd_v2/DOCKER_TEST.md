# PDD v2 — Ambiente de Teste Docker

> **Propósito:** Validar a reprodutibilidade do PDD v2 em Hermes isolado.
> A golden image v1 (em `~/.hermes`) NÃO é tocada.

---

## Estratégia de Isolamentos

```
┌────────────────────────────────────┐
│  Host (produção)                   │
│  ~/.hermes  →  golden image v1     │
│  NÃO TOCADO                        │
└────────────────────────────────────┘
                │
                │ bind mount (read-only: .env + auth.json)
                ▼
┌────────────────────────────────────┐
│  Docker: exocortex-v2-test         │
│  /opt/data  →  Hermes limpo        │
│  /workspace →  exocortex.saas repo │
│                                    │
│  setup.sh copia skills do repo     │
│  para /opt/data/skills/            │
│                                    │
│  NENHUM acesso ao ~/.hermes host   │
└────────────────────────────────────┘
```

## Componentes

1. `docker/Dockerfile.test` — Imagem Hermes + workspace
2. `docker/docker-compose.test.yml` — Orquestração
3. `docker/test-entrypoint.sh` — Script de bootstrap
4. `docker/.env.test` — Variáveis de ambiente

## Como Usar

```bash
# 1. Build
docker compose -f docker/docker-compose.test.yml build

# 2. Run (modo interativo — executa setup.sh e abre shell)
docker compose -f docker/docker-compose.test.yml run --rm test

# 3. Dentro do container:
cd /workspace
bash plans/pdd_v2/artifacts/setup.sh  # P0: Foundation
hermes skills list                      # Verificar
hermes chat                             # Iniciar P1 via prompts
```
