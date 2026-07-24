# Design — `excrtx-produce-noticias` (produtor de notícias do Hermes)

> **Status:** spec aprovado (brainstorming 2026-07-24). Aguarda revisão do owner antes do plano de implementação.
> **Change mode:** COLLAB (skill Exocórtex consome o contrato do MCP `sales-ai` + principal `hermes-publisher`).
> **Escopo desta spec:** v1 = produtor **macro** autônomo (áreas + periodicidade parametrizáveis) **+ modo manual** (comercial/gestão). Micro (notícias de cliente) é **desenhado agora, construído na v2** (spec própria).

## 1. Contexto

A superfície de publicação de notícias está 100% em produção desde 2026-07-22 (contrato `databrain-to-sales-ai.md` v1.21): tabela canônica `noticias_publicas`, principal least-privilege `hermes-publisher`, MCP `sales-ai` v2.2.0 com `publish_noticia`/`expire_noticia`. O lado **produtor** foi parcialmente endereçado pela issue #56; o PR databrain#6 ("Route B") entregou um **harness validador na DataBrain** — mas não um produtor que publica de fato. Esta spec cobre o **produtor real**, executado pelo runtime Hermes/Exocórtex.

Decisões do owner (brainstorming 2026-07-24):
- **Escopo v1 = macro** (setor); micro vem depois.
- **Autonomia = cron** (publica sem revisão humana no modo automático).
- **Pesquisa = skills próprias do Exocórtex** (não reimplementar coleta).
- **Periodicidade e área macro monitorada = parametrizáveis**; idem para micro depois.
- **Publicar direto do comercial/gestão** = modo manual da skill, via agente (sem mudar o app).
- **A DataBrain NÃO precisa estar up para o agente publicar.**
- **A skill é uma "skill de skills"** — orquestra outras skills, reimplementa o mínimo.

## 2. Princípio central: skill de skills

O produtor **não reimplementa** coleta, síntese, controle de qualidade editorial nem transporte MCP. Ele contribui apenas: (a) **orquestração** dos passos, (b) **config** de áreas/periodicidade, (c) a **cola de publicação + ledger de não-reativação**. Tudo o mais é delegado a skills canônicas existentes:

| Responsabilidade | Skill delegada |
|---|---|
| Pesquisa setorial macro (multi-fonte PT-BR) | `excrtx-research-cpg-brasil` (que já compõe `crawler-brasil` + `last30days` + `integrate-agent-reach` + `integrate-docbrain`) |
| Qualidade editorial (headline sem slop) | `excrtx-quality-antislop` / `excrtx-quality-gate` |
| Canal de escrita (publish/expire) | `excrtx-integrate-mcp` → MCP `sales-ai` `publish_noticia`/`expire_noticia` |
| Governança de ação externa | `excrtx-govern-draftfirst` (mesmo no modo autônomo, para logging/gate na criação do cron) |
| Ledger no acervo (estado de urls) | `excrtx-memory-manager` |
| (v2 micro) pesquisa por empresa + resolução de cliente | `excrtx-crawler-brasil` + `excrtx-source-cnpj` (+ `source-reclameaqui`, `source-google-trends` como sinal) |

Regra de projeto: se um passo puder ser feito por uma skill existente, ele **é** feito por ela. Código novo só na orquestração e na cola de publish/ledger.

## 3. Arquitetura e fluxo de dados

Caminho de publicação **independente da DataBrain**:

```
cron despachante → sessão Hermes carrega excrtx-produce-noticias (modo auto) →
  para cada área monitorada vencida:
    1. PESQUISA    research-cpg-brasil --template <área> --output json  → itens (url/fonte reais)
    2. CURADORIA   DeepSeek + quality-antislop                          → inputs publish_noticia canônicos
    3. GUARD-LOCAL ledger de urls no acervo (memory-manager)            → descarta retired/duplicada
    4. PUBLICA     MCP sales-ai.publish_noticia (escopo=macro)          → noticias_publicas (idempotente via índice único Supabase)
    5. LEDGER      grava url + valido_ate + estado no acervo
    6. EXPIRA      itens vencidos → expire_noticia + ledger vira retired
```

O harness da DataBrain (`databrain news guard/receipt/expire-plan`) permanece como **reconciliação offline opcional** — executada só quando a DataBrain estiver up (ex.: pipeline manual), nunca no caminho de publicação.

## 4. Configuração (parametrização)

Arquivo de config versionado com a skill, sobreponível pelo acervo `exocortex-ops`. Shape proposto (`config/noticias.toml`):

```toml
[publish]
default_escopo = "macro"
default_ttl_days = 45          # valido_ate = publicado_em + N
max_items_per_run = 4          # cap por área/run (anti-flood do feed)
relevance_threshold = 60       # 0-100; itens abaixo são descartados na curadoria

# --- áreas macro monitoradas (v1) ---
[[monitored_areas]]
slug = "varejo"                # template do research-cpg-brasil
cadence = "daily"              # periodicidade parametrizável (daily|weekly|"0 7 * * 1"…)
max_items = 3                  # override do cap por área (opcional)
relevance_threshold = 65       # override (opcional)

[[monitored_areas]]
slug = "limpeza"
cadence = "weekly"

# --- clientes monitorados (v2; shape já previsto, não usado na v1) ---
# [[monitored_clients]]
# cliente_id = "uuid"
# cnpj = "00000000000000"
# aliases = ["Nome Fantasia", "Razão Social"]
# cadence = "weekly"
```

- **`monitored_areas[].slug`** = template do `research-cpg-brasil` (`panorama`/`varejo`/`inovacao`/`limpeza`/`supply`) ou custom definido em `references/query-templates.md` daquela skill.
- **`cadence`** = periodicidade por área (o despachante decide o que está vencido).
- Overrides por área de `max_items`/`relevance_threshold`.
- Bloco `monitored_clients` fica comentado na v1, mas o shape e o ledger já suportam `cliente_id` (micro-ready).

## 5. Modo A — autônomo (cron)

Um **cron despachante único** registrado em `acervo/micro/exocortex-ops/knowledge/cron-registry.md`. A cada disparo, lê a config, calcula quais áreas estão vencidas pela `cadence` e roda o pipeline por área. O **último run por área** (`last_run_at`) é persistido no acervo (`exocortex-ops`, ao lado do ledger, via `memory-manager`); uma área está vencida quando `now − last_run_at ≥ cadence`. A criação do cron passa pelo gate normal de `excrtx-govern-draftfirst` (ação externa recorrente); uma vez vivo, publica autonomamente. A cadência do cron do SO deve ser ≤ a menor `cadence` configurada (ex.: cron horário serve áreas `daily`/`weekly`); o despachante é o árbitro real de quando cada área roda.

**Passo 2 (curadoria) — a rede de segurança da autonomia.** Sem revisão humana, a curadoria é estrita e é onde mora o julgamento do agente + DeepSeek:
- **Factualidade:** só sobrevive item com `url` + `fonte` reais retornados pela pesquisa. **Nunca inventar** notícia; nunca publicar item sem url verificável.
- **Relevância:** DeepSeek pontua cada item vs a área; descarta abaixo do `relevance_threshold`.
- **Dedup:** por `url_normalizada` + similaridade de título.
- **Impacto:** classifica `positivo|negativo|neutro`.
- **Headline:** ≤1 linha, passada por `excrtx-quality-antislop`.
- **Cap:** no máximo `max_items` por área/run.

Saída da curadoria = lista de inputs canônicos de `publish_noticia` (`titulo`, `headline?`, `fonte`, `url`, `publicado_em`, `tipo_fonte='noticia'`, `impacto`, `escopo='macro'`, `valido_ate`).

## 6. Modo B — manual (comercial/gestão via agente)

Disparado sob demanda quando comercial ou gestão pede ao Hermes ("publique esta notícia: …"). A skill:
1. Recebe o item (título, url, fonte, impacto; headline opcional).
2. **Valida** o formato canônico + factualidade (**url obrigatória**).
3. Passa a headline pelo `quality-gate`/`antislop`.
4. Publica pelo **mesmo canal MCP** `publish_noticia`.
5. Carimba `origem` (ex.: `comercial` / `gestao`) e registra quem pediu nos metadados/log (`govern-draftfirst`).
6. Grava no **mesmo ledger**.

Sem pesquisa nem curadoria automática — é publicação humana-no-loop pelo canal governado. Não altera o app; o pedido chega pelo agente.

## 7. Ledger de não-reativação (DataBrain-free)

⚠️ Regra do contrato: **re-publicar uma url expirada REATIVA a notícia** (`ativo=true` + novo TTL). Como o produtor não usa o ledger da DataBrain, ele mantém o **seu próprio ledger no acervo** (`exocortex-ops`, via `memory-manager`):

- Registra cada url publicada: `{ url_normalizada, cliente_id|null, noticia_id, estado: active|retired, valido_ate, publicado_em, origem }`.
- **Passo 3 (guard-local)** descarta candidato cuja url esteja `retired` (evita reativação) ou `active` e ainda não-expirada (evita churn).
- **Passo 6 (expira)** vira `retired` no ledger ao chamar `expire_noticia`.
- Idempotência de duplicata no update é garantida no servidor pelo índice único `(url, cliente_id) NULLS NOT DISTINCT` do Supabase; o ledger local cobre especificamente o hazard de reativação e serve de auditoria.
- Chave do ledger inclui `cliente_id` desde já (micro-ready).

> Nota de correção epistêmica: quando a DataBrain estiver up, `databrain news receipt`/`expire-plan` podem reconciliar o ledger `ops` da DataBrain com este ledger local — auditoria secundária, opcional.

## 8. Credenciais e segurança

- Escrita exclusiva pelo principal **`hermes-publisher`** (JWT com claim `app_metadata.noticias_publisher`), via MCP em modo `password` (`SALES_AI_MCP_AUTH_MODE=password` + `SUPABASE_USER_EMAIL`/`SUPABASE_USER_PASSWORD`).
- **PROIBIDO** `service_role` no caminho de publicação (o least-privilege do principal é o ponto central do design).
- Credenciais só em env do runtime Hermes (arquivo gitignored; senha nunca versionada nem ecoada). Documentar as variáveis esperadas em `.env.example` da skill **sem valores**.

## 9. Fronteiras (o que a skill NÃO faz)

- Não reimplementa coleta/síntese (delega ao `research-cpg-brasil`).
- Não escreve direto no Postgres nem usa `service_role`.
- Não depende da DataBrain para publicar.
- Não resolve `cliente_id` nem publica micro na v1 (só macro).
- Não cria afordância no app Sales-AI (modo manual é via agente).

## 10. Micro (v2) — desenhado, não construído

Quando priorizado, a v2 reusa o mesmo esqueleto trocando só o passo de PESQUISA e adicionando resolução de cliente:
- `monitored_clients[]` na config (cliente_id + CNPJ + aliases + cadence).
- Pesquisa por empresa: `excrtx-crawler-brasil` (por-empresa) + `excrtx-source-cnpj` (resolver/validar cadastro) + `source-reclameaqui`/`source-google-trends` como sinal.
- Publica com `escopo='micro'` + `cliente_id` (coerência escopo⇔cliente_id garantida por CHECK no banco).
- Mesmo ledger (já chaveado por `cliente_id`), mesmo canal MCP, mesmas travas de factualidade/relevância.

## 11. Change mode e artefatos

- **COLLAB**: change record em `.harness/changes/` (umbrella) referenciando esta spec; contrato `databrain-to-sales-ai.md` é **consumido** (v1.21+), não alterado — sem nova superfície de contrato.
- Novos artefatos (branch `collab/noticias-producer-skill` em `exocortex.saas`):
  - `skills/excrtx-produce-noticias/SKILL.md` (runbook dos 2 modos, contrato de curadoria, segurança).
  - `skills/excrtx-produce-noticias/config/noticias.toml` (config default).
  - `skills/excrtx-produce-noticias/scripts/` (cola determinística: despachante de cadência, chamada MCP publish/expire, read/write do ledger; parser reutilizado quando aplicável).
  - `skills/excrtx-produce-noticias/.env.example` (variáveis, sem valores).
  - Registro do cron em `acervo/micro/exocortex-ops/knowledge/cron-registry.md`.

## 12. Verificação (critérios de aceite)

1. **Dry-run** (`--no-publish`): pesquisa→curadoria→guard-local produz candidatos, **todos com url/fonte reais** e `valido_ate` preenchido; nenhum item inventado.
2. **Publish macro live**: 1 item publicado via MCP aparece no feed "Notícias do Setor" do app; invisível a fluxo micro (não aplicável na v1).
3. **Idempotência**: re-run da mesma área não duplica (mesma `(url, cliente_id)` → update); url `retired` não é reativada (guard-local).
4. **Expiração**: item vencido → `expire_noticia` some do feed e vira `retired` no ledger.
5. **Modo manual**: publish de comercial/gestão pelo agente entra com `origem` correta e passa pelo quality-gate.
6. **Parametrização**: mudar `cadence`/`slug`/`max_items` na config altera o comportamento do despachante sem tocar em código.
7. **Segurança**: nenhuma referência a `service_role` no caminho de publicação; nenhum segredo em código/commits.
8. **Skill de skills**: a skill delega pesquisa/qualidade/transporte às skills canônicas (verificável no SKILL.md e nos scripts — sem coleta/síntese reimplementadas).

## 13. Riscos e mitigações

| Risco | Mitigação |
|---|---|
| Publicar notícia irrelevante/ruído (Copa, política nos feeds gerais) | `research-cpg-brasil` já prioriza crawler setorial; curadoria com `relevance_threshold` + atribuição de fonte obrigatória |
| Reativar url expirada | Ledger de não-reativação local (guard-local passo 3) |
| Alucinação factual | Trava de factualidade: só publica item com url real retornada pela pesquisa |
| Flood do feed | `max_items_per_run` por área |
| Deriva de credenciais entre hosts | Env-only no runtime Hermes; `.env.example` sem valores; principal least-privilege |
| `last30days` lento/flaky | `research-cpg-brasil` tem `--skip-l30d`; crawler BR é fonte primária |
