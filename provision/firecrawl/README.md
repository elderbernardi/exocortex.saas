# Firecrawl — Provisioner do Exocórtex

Provisiona o [Firecrawl](https://github.com/firecrawl/firecrawl) self-hosted como
serviço de scraping/crawl/extract do Exocórtex (Tier 1 do modelo escalonado).

## Modelo escalonado (tiers)

O Firecrawl é resolvido pelo `setup/step-11c-integration-firecrawl.sh` em 3 tiers:

1. **Self-host (Tier 1)** — `EXOCORTEX_ENABLE_FIRECRAWL=1` → sobe a stack Docker
   deste diretório e aponta `FIRECRAWL_BASE_URL` para o endpoint local.
2. **Servidor existente (Tier 2)** — toggle desligado, mas `FIRECRAWL_BASE_URL`
   já aponta para um Firecrawl saudável → usa o existente (BYO endpoint).
3. **Degradação (Tier 3)** — nenhum dos dois → grava um lembrete e segue sem
   falhar. As skills que dependem de Firecrawl caem para fallback (browser/erro
   estruturado).

## Stack

| Serviço | Imagem (pinada) | Papel |
|---|---|---|
| `api` | `ghcr.io/firecrawl/firecrawl:2.10.4` | API + workers (harness orchestrator) |
| `playwright-service` | `ghcr.io/firecrawl/playwright-service` (por digest) | Renderização headless |
| `redis` | `redis:7-alpine` | Fila/cache |
| `nuq-postgres` | `ghcr.io/firecrawl/nuq-postgres` (por digest) | Backend da fila (Postgres) |

> Imagens pré-construídas oficiais. Tags PINADAS (sem `:latest`); imagens sem
> tag semver são pinadas por digest. O backend experimental FoundationDB do
> upstream foi omitido (nuq-postgres é o default estável).

## Estrutura

```
provision/firecrawl/
├── README.md           # Este arquivo
├── docker-compose.yml  # Stack vendorizada do upstream (image-based, pinada)
└── scripts/
    ├── install.sh      # docker compose up -d + health poll (idempotente)
    └── smoke.sh        # health probe + scrape mínimo
```

## Uso

### Provisionar durante o setup (Tier 1)

```bash
EXOCORTEX_ENABLE_FIRECRAWL=1 HERMES_HOME=~/.hermes bash setup.sh
```

### Provisionar standalone

```bash
EXOCORTEX_ENABLE_FIRECRAWL=1 bash provision/firecrawl/scripts/install.sh
```

### Verificar

```bash
bash provision/firecrawl/scripts/smoke.sh
```

### Parar

```bash
cd ~/.hermes/firecrawl && docker compose down
```

## Variáveis de ambiente

| Variável | Default | Descrição |
|---|---|---|
| `EXOCORTEX_ENABLE_FIRECRAWL` | `0` | Ativa o self-host (Tier 1) durante o setup |
| `FIRECRAWL_BASE_URL` | `http://127.0.0.1:3002` | Endpoint da API; deriva a porta do host |
| `FIRECRAWL_API_KEY` | — | Opcional; **não** exigida no self-host (auth bypass) |
| `EXOCORTEX_FIRECRAWL_DIR` | `$HERMES_HOME/firecrawl` | Diretório de runtime (compose + .env) |
| `FIRECRAWL_BULL_AUTH_KEY` | gerado | Segredo do painel de filas (`/admin/<key>/queues`) |
| `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `MODEL_NAME` | — | Opcional: habilita AI features (JSON/extract) |

## Notas

- **Self-hosted não exige API key.** A autenticação é bypassada no modo
  self-host (ver `SELF_HOST.md` do upstream). `BULL_AUTH_KEY` protege apenas o
  painel de filas.
- **Health endpoint.** O probe usa `GET /` (qualquer HTTP 2xx/3xx/4xx indica
  API no ar). O smoke faz ainda um `POST /v1/scrape` mínimo.
- **Re-pin de imagens.** Para atualizar: `cd ~/.hermes/firecrawl && docker
  compose pull`, re-resolva os digests e atualize o `docker-compose.yml`.
