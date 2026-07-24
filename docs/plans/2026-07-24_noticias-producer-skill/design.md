# Design — evolução da skill `excrtx-news-sales-ai` (produtor de notícias do Hermes)

> **Status:** spec revisado (brainstorming 2026-07-24). Aguarda revisão do owner antes do plano.
> **Change mode:** COLLAB (skill Exocórtex consome o contrato do MCP `sales-ai` + principal `hermes-publisher`).
> **Pivô (2026-07-24):** o Hermes já mesclou uma skill Route B — **`excrtx-news-sales-ai`** (exocortex #137: runbook + `build_dossier.py` + testes). Em vez de criar `excrtx-produce-noticias`, esta spec **evolui a skill existente sem regredir**: mantém o que ela faz (macro+micro, harness DataBrain sob demanda, DocBrain como contexto opcional) e **adiciona** as decisões do owner (default DataBrain-free, cron autônomo, config de áreas+periodicidade, modo manual comercial/gestão, sem DocBrain no padrão). Reusa `build_dossier.py`.
> **Já entregue nesta sessão (workstream do writer):** o hardening anti-reativação do `publish_noticia` — que o record #62 afirmava (v2.2.1) mas **nunca entrou** — foi **refeito via TDD**: MCP `sales-ai` **v3.1.0** (`resultado=skipped_retired`), contrato **v1.24**, COLLAB record `2026-07-24_collab_noticias-writer-antireactivation.md`. Ver §7.
> **Escopo desta spec:** v1 = produtor **macro** autônomo (áreas + periodicidade parametrizáveis) **+ modo manual** (comercial/gestão), **sem regredir** o macro/micro/harness/DocBrain existentes (viram opcionais). Micro autônomo por cliente = **v2** (spec própria).

## 1. Contexto

A superfície de publicação está em produção desde 2026-07-22 (contrato `databrain-to-sales-ai.md`, hoje **v1.24**): tabela canônica `noticias_publicas`, principal least-privilege `hermes-publisher`, MCP `sales-ai` **v3.1.0** com `publish_noticia`/`expire_noticia`. O lado **produtor** foi endereçado em duas frentes: databrain#6 ("Route B") entregou o **harness validador na DataBrain**; exocortex#137 entregou a skill **`excrtx-news-sales-ai`** (runbook manual Route B + `build_dossier.py` + testes). Nenhuma das duas entrega um produtor **autônomo/parametrizável**. Esta spec evolui `excrtx-news-sales-ai` para esse produtor.

O que **reusar** do já entregue: `build_dossier.py` (normalização/dedup/dossier — puro, testado, DataBrain/DocBrain-agnóstico nas entradas); o runbook de curadoria/fronteiras da skill; e o writer já endurecido (`skipped_retired`) como proteção server-side primária.

Decisões do owner (brainstorming 2026-07-24):
- **Escopo v1 = macro** (setor); micro vem depois.
- **Autonomia = cron** (publica sem revisão humana no modo automático).
- **Pesquisa = skills próprias do Exocórtex** (não reimplementar coleta).
- **Periodicidade e área macro monitorada = parametrizáveis**; idem para micro depois.
- **Publicar direto do comercial/gestão** = modo manual da skill, via agente (sem mudar o app).
- **A DataBrain NÃO precisa estar up para o agente publicar.**
- **A skill é uma "skill de skills"** — orquestra outras skills, reimplementa o mínimo.

## 2. Princípio central: skill de skills

O produtor **não reimplementa** coleta, síntese, controle de qualidade editorial nem transporte MCP. Ele contribui apenas: (a) **orquestração** dos passos, (b) **config** de áreas/periodicidade, (c) a **cola de publicação + guard de não-reativação** (read-before-write no Supabase). Tudo o mais é delegado a skills canônicas existentes:

| Responsabilidade | Skill delegada |
|---|---|
| Pesquisa setorial macro (multi-fonte PT-BR) | `excrtx-research-cpg-brasil` (compõe `crawler-brasil` + `last30days` + `integrate-agent-reach`) — **sem DocBrain** (não usar `--document`; ver §4) |
| Qualidade editorial (headline sem slop) | `excrtx-quality-antislop` / `excrtx-quality-gate` |
| Canal de escrita (publish/expire) | `excrtx-integrate-mcp` → MCP `sales-ai` `publish_noticia`/`expire_noticia` |
| Guard de não-reativação (fonte da verdade) | read-before-write no Supabase via `supabase-js` (policy `noticias_select_publisher`, ver §7) |
| Governança de ação externa | `excrtx-govern-draftfirst` (mesmo no modo autônomo, para logging/gate na criação do cron) |
| Estado de cadência (`last_run_at` por área) | `excrtx-memory-manager` (acervo `exocortex-ops`) |
| (v2 micro) pesquisa por empresa + resolução de cliente | `excrtx-crawler-brasil` + `excrtx-source-cnpj` (+ `source-reclameaqui`, `source-google-trends` como sinal) |

Regra de projeto: se um passo puder ser feito por uma skill existente, ele **é** feito por ela. Código novo só na orquestração e na cola de publish/guard.

## 3. Arquitetura e fluxo de dados

Caminho de publicação **independente da DataBrain**:

```
cron despachante → sessão Hermes carrega excrtx-news-sales-ai (modo auto) →
  para cada área monitorada vencida:
    1. PESQUISA    research-cpg-brasil --template <área> --output json  → itens (url/fonte reais; sem DocBrain)
    2. CURADORIA   DeepSeek + quality-antislop                          → inputs publish_noticia canônicos
    3. GUARD       read-before-write no Supabase (SELECT por url)       → descarta url já ativa OU retirada (não-reativação)
    4. PUBLICA     MCP sales-ai.publish_noticia (escopo=macro)          → noticias_publicas (idempotente via índice único Supabase)
    5. CADÊNCIA    grava last_run_at da área no acervo
    6. EXPIRA      itens vencidos → expire_noticia (ativo=false)
```

O harness da DataBrain (`databrain news guard/receipt/expire-plan`) permanece como **reconciliação offline opcional** — executada só quando a DataBrain estiver up (ex.: pipeline manual), nunca no caminho de publicação.

## 4. Configuração (parametrização)

Arquivo de config versionado com a skill, sobreponível pelo acervo `exocortex-ops`. Shape proposto (`config/noticias.toml`):

```toml
[publish]
default_escopo = "macro"
default_ttl_days = 30          # valido_ate = publicado_em + N
max_items_per_run = 4          # cap por área/run (anti-flood do feed)
relevance_threshold = 60       # 0-100; itens abaixo são descartados na curadoria
use_docbrain = false           # NÃO depender do DocBrain no pipeline de pesquisa

# --- áreas macro monitoradas (v1) ---
[[monitored_areas]]
slug = "varejo"                # template do research-cpg-brasil
cadence = "weekly"             # periodicidade parametrizável (daily|weekly|"0 7 * * 1"…)
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
- `use_docbrain = false`: o pipeline de pesquisa **não** injeta documentos via DocBrain (`--document`); depende só de crawler-brasil + last30days + agent-reach.
- Bloco `monitored_clients` fica comentado na v1, mas o shape e o guard `(url, cliente_id)` já suportam `cliente_id` (micro-ready).

## 5. Modo A — autônomo (cron)

Um **cron despachante único** registrado em `acervo/micro/exocortex-ops/knowledge/cron-registry.md`. A cada disparo, lê a config, calcula quais áreas estão vencidas pela `cadence` e roda o pipeline por área. O **último run por área** (`last_run_at`) é persistido no acervo (`exocortex-ops`, via `memory-manager`); uma área está vencida quando `now − last_run_at ≥ cadence`. A criação do cron passa pelo gate normal de `excrtx-govern-draftfirst` (ação externa recorrente); uma vez vivo, publica autonomamente. A cadência do cron do SO deve ser ≤ a menor `cadence` configurada (ex.: cron horário serve áreas `daily`/`weekly`); o despachante é o árbitro real de quando cada área roda.

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
6. Passa pelo **mesmo guard read-before-write** (§7) antes de publicar — não reativa url expirada mesmo no manual.

Sem pesquisa nem curadoria automática — é publicação humana-no-loop pelo canal governado. Não altera o app; o pedido chega pelo agente.

## 7. Guard de não-reativação — read-before-write no Supabase

⚠️ Regra do contrato: **re-publicar uma url expirada REATIVA a notícia** (`ativo=true` + novo TTL). Duas camadas cobrem isso, defesa em profundidade:

**Camada 1 — servidor (primária, já entregue nesta sessão).** O writer `publish_noticia` **v3.1.0** lê `ativo` na linha `(url, cliente_id)` e, se `ativo=false`, retorna `resultado='skipped_retired'` **sem tocar na linha** — nunca reativa. Isso fecha o hazard mesmo que o produtor erre. Foi refeito via TDD porque o hardening que o record #62 afirmava (v2.2.1) nunca tinha entrado (o merge do cockpit v3.0.0 passou por cima). Contrato v1.24; COLLAB record `2026-07-24_collab_noticias-writer-antireactivation.md`.

**Camada 2 — produtor (secundária, otimização).** Antes de publicar, o produtor faz um `SELECT` em `noticias_publicas` pela `url` (via `supabase-js` como `hermes-publisher`; a policy `noticias_select_publisher` deixa o principal ver linhas `ativo=false`). Serve para **evitar chamadas desnecessárias** (churn): pula url já ativa e url já retirada antes mesmo de chamar o writer. Se o `SELECT` falhar/for pulado, a Camada 1 ainda garante a invariância.

- Idempotência de duplicata é reforçada no servidor pelo índice único `(url, cliente_id) NULLS NOT DISTINCT`.
- O `SELECT` chaveia por `(url, cliente_id)` — `cliente_id IS NULL` no macro (micro-ready para v2).
- **Sem ledger de urls no acervo.** O único estado persistido no acervo (`exocortex-ops`, via `memory-manager`) é o **`last_run_at` por área** (cadência) — que não existe no Supabase.

> Transporte: leitura via `supabase-js` (read-only, creds do publisher); escrita sempre via MCP (`publish_noticia`/`expire_noticia`). O produtor trata `resultado ∈ {created, updated, skipped_retired}`.

## 8. Credenciais e segurança

- Escrita exclusiva pelo principal **`hermes-publisher`** (JWT com claim `app_metadata.noticias_publisher`), via MCP em modo `password` (`SALES_AI_MCP_AUTH_MODE=password` + `SUPABASE_USER_EMAIL`/`SUPABASE_USER_PASSWORD`).
- **PROIBIDO** `service_role` no caminho de publicação (o least-privilege do principal é o ponto central do design).
- Credenciais só em env do runtime Hermes (arquivo gitignored; senha nunca versionada nem ecoada). Documentar as variáveis esperadas em `.env.example` da skill **sem valores**.

## 9. Fronteiras (o que a skill NÃO faz)

- Não reimplementa coleta/síntese (delega ao `research-cpg-brasil`).
- Não escreve direto no Postgres nem usa `service_role` (escrita só via MCP; leitura read-only via supabase-js do principal).
- Não depende da DataBrain para publicar, nem do DocBrain para pesquisar.
- Não resolve `cliente_id` nem publica micro na v1 (só macro).
- Não cria afordância no app Sales-AI (modo manual é via agente).

## 10. Micro (v2) — desenhado, não construído

Quando priorizado, a v2 reusa o mesmo esqueleto trocando só o passo de PESQUISA e adicionando resolução de cliente:
- `monitored_clients[]` na config (cliente_id + CNPJ + aliases + cadence).
- Pesquisa por empresa: `excrtx-crawler-brasil` (por-empresa) + `excrtx-source-cnpj` (resolver/validar cadastro) + `source-reclameaqui`/`source-google-trends` como sinal.
- Publica com `escopo='micro'` + `cliente_id` (coerência escopo⇔cliente_id garantida por CHECK no banco).
- Mesmo guard read-before-write (já chaveado por `(url, cliente_id)`), mesmo canal MCP, mesmas travas de factualidade/relevância.

## 11. Change mode e artefatos

- **COLLAB**: change record em `.harness/changes/` (umbrella). O contrato `databrain-to-sales-ai.md` já foi para **v1.24** (workstream do writer, §7); a evolução da skill em si **consome** o contrato, sem nova superfície.
- **Evoluir a skill existente `skills/excrtx-news-sales-ai/` (sem regredir)** — não criar skill nova:
  - `SKILL.md`: adicionar os 2 modos (auto por cron / manual comercial-gestão) e o default DataBrain-free/sem-DocBrain, **preservando** as seções atuais (macro+micro, harness DataBrain sob demanda, DocBrain como contexto opcional) marcadas como opcionais. Atualizar `compiled_rules:` e rodar `python3 scripts/compile_soul.py`.
  - `config/noticias.toml` (novo): config default (áreas, periodicidade, `use_docbrain=false`, caps).
  - `scripts/` (novos, ao lado de `build_dossier.py` que é **reusado**): despachante de cadência, chamada MCP publish/expire, read-before-write no Supabase, estado de cadência.
  - `.env.example` (novo): variáveis, sem valores.
  - Registro do cron em `acervo/micro/exocortex-ops/knowledge/cron-registry.md`.
  - Manter `references/route-b-architecture.md` e os testes existentes verdes (não regredir).
- Qualidade: `skill_judge` da skill deve manter/atingir **PASS** (D1–D5) antes do merge.

## 12. Verificação (critérios de aceite)

1. **Dry-run** (`--no-publish`): pesquisa→curadoria→guard (read-before-write) produz candidatos, **todos com url/fonte reais** e `valido_ate` preenchido; nenhum item inventado.
2. **Publish macro live**: 1 item publicado via MCP aparece no feed "Notícias do Setor" do app; invisível a fluxo micro (não aplicável na v1).
3. **Idempotência**: re-run da mesma área não duplica (mesma `(url, cliente_id)` → update); url com `ativo=false` não é reativada (guard read-before-write detecta a linha expirada e faz skip).
4. **Expiração**: item vencido → `expire_noticia` (`ativo=false`) some do feed; o mesmo url deixa de ser candidato em runs futuros.
5. **Modo manual**: publish de comercial/gestão pelo agente entra com `origem` correta e passa pelo quality-gate.
6. **Parametrização**: mudar `cadence`/`slug`/`max_items` na config altera o comportamento do despachante sem tocar em código.
7. **Segurança**: nenhuma referência a `service_role` no caminho de publicação; nenhum segredo em código/commits.
8. **Skill de skills**: a skill delega pesquisa/qualidade/transporte às skills canônicas (verificável no SKILL.md e nos scripts — sem coleta/síntese reimplementadas).

## 13. Riscos e mitigações

| Risco | Mitigação |
|---|---|
| Publicar notícia irrelevante/ruído (Copa, política nos feeds gerais) | `research-cpg-brasil` já prioriza crawler setorial; curadoria com `relevance_threshold` + atribuição de fonte obrigatória |
| Reativar url expirada | Read-before-write no Supabase (§7): principal enxerga linhas `ativo=false` via `noticias_select_publisher` e faz skip |
| Alucinação factual | Trava de factualidade: só publica item com url real retornada pela pesquisa |
| Flood do feed | `max_items_per_run` por área |
| Deriva de credenciais entre hosts | Env-only no runtime Hermes; `.env.example` sem valores; principal least-privilege |
| `last30days` lento/flaky | `research-cpg-brasil` tem `--skip-l30d`; crawler BR é fonte primária |
| Indisponibilidade do Supabase | Guard e publish exigem Supabase (dependência autorizada); run falha fechada (não publica sem conferir a fonte da verdade) |
