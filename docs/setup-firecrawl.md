## Setup Firecrawl — Scraping / Crawl / Extract

O Firecrawl é o serviço de scraping/crawl/extract do Exocórtex. É resolvido por
um **modelo escalonado (tiers)** em `setup/step-11c-integration-firecrawl.sh`, de
modo que o setup nunca falha por causa dele — apenas habilita o melhor caminho
disponível.

### Modelo escalonado (tiers)

| Tier | Condição | Ação |
|---|---|---|
| **1 — Self-host** | `EXOCORTEX_ENABLE_FIRECRAWL=1` | Sobe a stack Docker local (`provision/firecrawl`) e fixa `FIRECRAWL_BASE_URL` no endpoint local |
| **2 — BYO endpoint** | toggle desligado, mas `FIRECRAWL_BASE_URL` responde a um health probe | Usa o servidor existente |
| **3 — Degradação** | nenhum dos dois | Grava `~/.hermes/reminders/firecrawl.md` e segue; skills caem para fallback |

A ordem é estrita: o Tier 1 só dispara com o toggle ligado; o Tier 2 só quando
o toggle está desligado **e** a URL responde; caso contrário, Tier 3.

### Pré-requisitos

- **Tier 1:** Docker (com `docker compose` v2). Self-hosted **não** exige API key.
- **Tier 2:** um Firecrawl já no ar e alcançável em `FIRECRAWL_BASE_URL`.
- **Tier 3:** nada (degradação automática).

### Como habilitar

**Tier 1 — self-host via Docker:**

```bash
EXOCORTEX_ENABLE_FIRECRAWL=1 bash setup.sh
```

Ou, no modo interativo, responda **sim** a:
`Provisionar Firecrawl self-hosted via Docker?`

**Tier 2 — apontar para um Firecrawl existente:**

```bash
FIRECRAWL_BASE_URL=http://<host>:3002 bash setup.sh
# (mantenha EXOCORTEX_ENABLE_FIRECRAWL desligado)
```

### Variáveis de ambiente

| Variável | Default | Descrição |
|---|---|---|
| `EXOCORTEX_ENABLE_FIRECRAWL` | `0` | Liga o self-host (Tier 1) |
| `FIRECRAWL_BASE_URL` | `http://127.0.0.1:3002` | Endpoint da API; deriva a porta do host no self-host |
| `FIRECRAWL_API_KEY` | — | Opcional; usada apenas se você apontar para o Firecrawl cloud. Self-host dispensa. |
| `EXOCORTEX_FIRECRAWL_DIR` | `$HERMES_HOME/firecrawl` | Diretório de runtime (compose + `.env` com segredos) |
| `FIRECRAWL_BULL_AUTH_KEY` | gerado | Segredo do painel de filas (`/admin/<key>/queues`) |
| `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `MODEL_NAME` | — | Opcional: habilita AI features (JSON-mode scrape, `/extract`) |

### Stack self-hosted

A stack (`provision/firecrawl/docker-compose.yml`) é vendorizada do compose
**oficial** do upstream (`firecrawl/firecrawl`), com diferenças deliberadas:

- usa imagens pré-construídas oficiais (`ghcr.io/firecrawl/*`) em vez de `build:`;
- **tags pinadas** (`firecrawl:2.10.4`; playwright/nuq-postgres por digest);
- omite o backend experimental FoundationDB (usa `nuq-postgres`, default estável).

Serviços: `api` (+ workers in-process) · `playwright-service` · `redis` · `nuq-postgres`.

### Health check / Verificação

Após o provisionamento, o `install.sh` faz polling em `http://127.0.0.1:<porta>/`
(até 12 tentativas, 5 s cada). Qualquer resposta HTTP indica que a API subiu.

O `step-12-verify-keys.sh` também faz um health probe não-fatal de
`FIRECRAWL_BASE_URL` ao final do setup.

**Smoke test standalone:**

```bash
bash provision/firecrawl/scripts/smoke.sh
```

Verifica diretório, compose, estado do container `exocortex-firecrawl-api`, o
endpoint de saúde e faz um `POST /v1/scrape` mínimo. Exit 0 = checks críticos
OK; exit 1 = falha crítica (ver saída).

**Teste manual de scrape:**

```bash
curl -X POST http://127.0.0.1:3002/v1/scrape \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com","formats":["markdown"]}'
```

### Troubleshooting

| Sintoma | Causa provável | Ação |
|---|---|---|
| `docker não encontrado` no Tier 1 | Docker ausente | Instale Docker; ou use Tier 2 (`FIRECRAWL_BASE_URL`) |
| API sem resposta após setup | Cold start (baixa browsers no 1º boot) | Aguarde ~1 min; `docker logs exocortex-firecrawl-api` |
| Reminder `firecrawl.md` criado | Tier 3 (degradação) | Ligue o toggle ou aponte uma URL válida e re-rode |
| `Supabase client is not configured` nos logs | Esperado no self-host | Ignorável — scrape/crawl funcionam |
| `You're bypassing authentication` nos logs | Esperado no self-host (auth bypass) | Ignorável |

Re-provisionar é idempotente:

```bash
EXOCORTEX_ENABLE_FIRECRAWL=1 bash setup.sh
```

Parar a stack:

```bash
cd ~/.hermes/firecrawl && docker compose down
```

### Skills que dependem do Firecrawl

| Skill | Uso | Fallback quando ausente |
|---|---|---|
| `excrtx-integrate-mcp` | `web_extract` via Firecrawl para ler READMEs/páginas | `browser_navigate`/`browser_vision`, `git clone`, ou `curl` |
| `excrtx-source-reclameaqui` | Firecrawl MCP para contornar challenges Cloudflare | Envelope de erro estruturado (`cloudflare_challenge`) |

Ambas degradam sem erro fatal. O lembrete `~/.hermes/reminders/firecrawl.md`
explica o estado e como habilitar.

### Arquivos envolvidos

| Caminho | Função |
|---|---|
| `setup/step-11c-integration-firecrawl.sh` | Orquestrador dos 3 tiers + registro do MCP |
| `provision/firecrawl/docker-compose.yml` | Stack self-hosted (pinada) |
| `provision/firecrawl/scripts/install.sh` | `docker compose up -d` + health poll (idempotente) |
| `provision/firecrawl/scripts/smoke.sh` | Verificação (health + scrape mínimo) |
| `~/.hermes/firecrawl/` | Runtime (compose copiado + `.env` com segredos) |
| `~/.hermes/reminders/firecrawl.md` | Lembrete de degradação (Tier 3) |
| `~/.hermes/logs/setup/firecrawl-install.log` | Log durável do provisionamento |
