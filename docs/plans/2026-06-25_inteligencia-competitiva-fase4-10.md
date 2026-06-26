# Plano: Inteligência Competitiva — Sistema de Obtenção de Dados (Fases 4–10)

> **Plano para META #97 e expansão** — 2026-06-25
> Consolida as Fases 1–3 já concluídas com a arquitetura expandida de coleta de dados
> competitivos para além da imprensa setorial.

## Status da META #97

| Fase | Issue | Escopo | Estado |
|---|---|---|---|
| 1 | #108 | Agent-Reach (4 canais zero-config) | ✅ Concluído |
| 2 | #98 | Crawler BR (15 fontes setoriais: RSS, HTML, API e browser) | ✅ Concluído |
| 3 | #99 | Skill-wrapper CPG (orquestração) | ✅ Concluído |
| F0 | #9 | **Firecrawl local/MCP** (capacidade opcional de scrape/search quando configurada) | ✅ Concluído 2026-06-25 |
| 4 | #111–#113 | **Fontes públicas estruturadas** (Reclame Aqui, Google Trends, CNPJ) | ✅ Implementadas localmente com testes; pendente publicação/fechamento remoto |
| 5 | #114–#115 | **DocBrain pipeline** (PDF, Office, scrape → Acervo) | 📋 Este plano |
| 6 | #116 | **Browser agent LLM** (e-commerce, sites sem API, gov arcaico) | 📋 Este plano |
| 7 | #117–#119 | **Sinais estruturados profundos** (INPI, ANVISA, Glassdoor, Diário Oficial) | 📋 Este plano |
| 8 | #120 | **Sinais indiretos e criativos** (vagas, feiras, podcasts, gôndola) | 📋 Este plano |
| 9 | #100 | Onboarding — captura de ramo, empresas, concorrentes | ⬜ Existente |
| 10 | #101 | Blueprint de generalização para outros domínios | ⬜ Existente |

### Estado local verificado em 2026-06-26

| Issue | Estado no GitHub | Estado no working tree |
|---|---|---|
| #111 | aberta | `tools/excrtx_source_reclameaqui/`, `tests/test_source_reclameaqui.py` e `skills/excrtx-source-reclameaqui/SKILL.md` criados; smoke real executado com `Girando Sol` |
| #112 | aberta | `tools/excrtx_source_google_trends/`, `tests/test_source_google_trends.py` e `skills/excrtx-source-google-trends/SKILL.md` criados; smoke real executado com `Girando Sol`; sujeito a rate limit |
| #113 | aberta | `tools/excrtx_source_cnpj/`, `tests/test_source_cnpj.py` e `skills/excrtx-source-cnpj/SKILL.md` existem; smoke real executado |

Este plano passa a refletir **estado real de execução local**, não apenas intenção de roadmap. Se o working tree avançar antes da publicação no GitHub, o plano deve ser atualizado no mesmo turno.

---

## Diagnóstico de Gap

### O que temos hoje (Fases 1–3)

```
Imprensa & Trade (71 itens/12 meses)
├── last30days (global)      → zero sinal social para marcas regionais
├── Agent-Reach (4 canais)   → YouTube + RSS + GitHub + Web READ
├── Crawler BR (15 fontes)   → Valor, Exame, G1, InfoMoney, SuperHiper, Nielsen, SuperVarejo, etc.
└── Firecrawl local/MCP      → busca/scrape quando endpoint estiver configurado
                                capacidade opcional; não assumir disponibilidade universal
```

**Limite estrutural:** só capturamos o que a imprensa publica e o que a empresa divulga. Não capturamos:
- Sinal de consumidor (queixas, avaliações, buscas)
- Dados corporativos estruturados (CNPJ, patentes, licenças)
- Sinais indiretos de movimentação (vagas, feiras, expansão física)

### O que precisamos

Para inteligência competitiva acionável, cada empresa monitorada precisa de um **perfil multidimensional**:

| Dimensão | Pergunta-chave |
|---|---|
| **Financeira** | Faturamento, capital social, quadro societário, ritmo de crescimento |
| **Operacional** | Expansão fabril, licenças, filiais, contratações |
| **Produto** | Lançamentos, patentes, registros regulatórios, portfólio |
| **Consumidor** | Avaliações, reclamações, volume de busca, preço praticado |
| **Reputação** | Processos judiciais, nota Reclame Aqui, imprensa negativa |
| **Distribuição** | Onde vende, preço por canal, presença em marketplaces |

A imprensa cobre ~20% dessas dimensões. As fontes abaixo cobrem o resto.

---

## Arquitetura Expandida (7 camadas de coleta)

```
                          ┌──────────────────────────┐
                          │   Orquestrador de Sinais  │
                          │   (cron + on-demand)      │
                          └─────┬───────┬───────┬────┘
                                │       │       │
        ┌───────────────────────┤       │       ├───────────────────────┐
        │                       │       │       │                       │
   ┌────▼─────┐  ┌──────────┐   │  ┌────▼───┐  │  ┌──────────┐  ┌──────▼──────┐
   │Imprensa  │  │ Público  │   │  │Browser │  │  │ DocBrain │  │  Sinais     │
   │& Trade   │  │Estruturado│  │  │Agent   │  │  │Pipeline  │  │  Indiretos  │
   ├──────────┤  ├──────────┤   │  ├────────┤  │  ├──────────┤  ├─────────────┤
   │Crawler BR│  │CNPJ      │   │  │E-commer│  │  │PDF/Office│  │Vagas (INDEED│
   │(13 RSS)  │  │Google    │   │  │ce (ML, │  │  │Scrape    │  │LinkedIn)    │
   │Agent-    │  │Trends    │   │  │Amazon, │  │  │Web       │  │Expositores  │
   │Reach     │  │Reclame   │   │  │Magalu) │  │  │Tabelas   │  │de Feiras    │
   │last30days│  │Aqui      │   │  │Sites   │  │  │Entidades │  │Google Img   │
   │          │  │          │   │  │Gov sem │  │  │LLM       │  │Gôndola      │
   │          │  │          │   │  │API     │  │  │Vision    │  │Podcasts/    │
   │          │  │          │   │  │        │  │  │          │  │YouTube      │
   └────┬─────┘  └────┬─────┘   │  └────┬───┘  │  └────┬─────┘  └──────┬──────┘
        │             │         │       │       │       │             │
        └─────────────┴─────────┴───────┴───────┴───────┴─────────────┘
                                    │
                          ┌─────────▼──────────┐
                          │   LLM Structured    │
                          │   Extract & Classify│
                          └─────────┬──────────┘
                                    │
                          ┌─────────▼──────────┐
                          │  Acervo Cognitivo   │
                          │  micro/{empresa}/   │
                          └─────────┬──────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
              ┌─────▼─────┐  ┌──────▼──────┐  ┌─────▼─────┐
              │ Dossiê    │  │ Alerta      │  │ Timeline  │
              │ pontual   │  │ contínuo    │  │ histórico │
              └───────────┘  └─────────────┘  └───────────┘
```

---

## Fase 4 — Fontes Públicas Estruturadas (zero auth)

> **Status:** Implementada localmente — #111, #112 e #113 com tool, testes, skill e smoke real; falta governança remota (comentários/fechamento) e eventual push
> **Prioridade:** P0 — é o maior gap de sinal com menor complexidade
> **Dependências:** Nenhuma crítica para execução local. Google Trends usa endpoint público próprio e continua sujeito a rate limit.
> **Issues relacionadas:** #97 (META), #111, #112, #113

### Estado operacional da fase

| Issue | Objetivo | Situação |
|---|---|---|
| #113 | CNPJ / dados cadastrais | ferramenta, testes, skill, smoke real e integração opcional com `#99 excrtx-research-cpg-brasil` já feitos localmente; falta publicação remota |
| #112 | Google Trends | implementada localmente com endpoint público próprio, testes passando, smoke real executado e integração opcional com `#99`; limite conhecido: rate limit intermitente |
| #111 | Reclame Aqui | implementada localmente com parsing HTML/JSON-LD, testes passando, smoke real executado e integração opcional com `#99` |

### Contrato comum para a Fase 4

Antes de implementar qualquer coletor, use o mesmo contrato para os três. Isso evita três ferramentas parecidas com três schemas incompatíveis.

**Estrutura canônica:**

```text
tools/excrtx_source_{nome}/
├── __init__.py
├── cli.py
├── collector.py
└── schemas.py

skills/excrtx-source-{nome}/
└── SKILL.md

tests/test_source_{nome}.py
```

**CLI canônica:**

```bash
python3 -m tools.excrtx_source_{nome}.cli "input" --output json
```

**Envelope JSON canônico:**

```json
{
  "source": "reclameaqui|google_trends|cnpj",
  "query": "input original",
  "retrieved_at": "2026-06-25T12:00:00Z",
  "data": {},
  "provenance": {
    "url": "https://...",
    "method": "api|html|browser|firecrawl",
    "raw_cached": false
  },
  "errors": []
}
```

Use `retrieved_at` como timestamp padrão para alinhar com `excrtx_crawler_brasil` e `excrtx-integrate-agent-reach`. Se uma issue antiga citar `coletado_em`, trate como alias legado e normalize para `retrieved_at`.

**Compatibilidade obrigatória com o repo:**
- CLI: `python3 -m tools.excrtx_source_{nome}.cli ...`
- módulo Python sob `tools/`, não pacote solto na raiz
- skill em `skills/excrtx-source-{nome}/SKILL.md`
- saída sempre embrulhada no envelope comum, mesmo quando a fonte devolver um JSON já estruturado

**Regras técnicas comuns:**

- Unit tests offline primeiro: fixture HTML/JSON ou mock de API. Smoke real deve ser opcional/lento.
- Falhas de rede, rate limit e página sem dados retornam `errors[]`; não despejar stack trace como output do CLI.
- Sem login, sem API key e sem bypass de barreiras de acesso.
- GitHub writes são externos: ao concluir, preparar DRAFT de comentário com evidências; publicar só com aprovação.
- Não executar `pip install`, `npm install` ou equivalente sem aprovação. Se faltar dependência, registrar no plano e no draft da issue.
- Se criar ou alterar skill, validar com `python3 scripts/skill_judge.py --skill excrtx-source-{nome} --d1-only`.

### Ordem operacional recomendada

1. **#113 CNPJ** — menor risco técnico; cria o padrão de envelope, CLI e tests com API pública.
2. **#112 Google Trends** — adiciona tratamento de rate limit e mocks de biblioteca não-oficial.
3. **#111 Reclame Aqui** — maior impacto de consumidor, mas scraping mais frágil; executar depois do contrato estar validado.

Se o objetivo do turno for reputação pública imediata, #111 pode rodar em paralelo com #113. Para um único agente, começar por #113 reduz retrabalho.

### 4a. `excrtx-source-reclameaqui` — Coletor Reclame Aqui

**Entrada:** CNPJ, nome da empresa, ou URL da página no Reclame Aqui
**Saída:** JSON com reputação da empresa nos últimos 12–24 meses

```
Input: "Girando Sol" ou "/empresa/girando-sol/"
Output: {
  "empresa": "Girando Sol",
  "nota_geral": 7.3,
  "total_reclamacoes": 142,
  "respondidas": 138,
  "taxa_resolucao": 0.87,
  "tempo_medio_resposta": "2 dias",
  "categorias_problema": [
    {"categoria": "Propaganda enganosa", "count": 23},
    {"categoria": "Qualidade do produto", "count": 18}
  ],
  "reclamacoes": [
    {"titulo": "...", "data": "2026-05-12", "status": "respondida", "categoria": "..."}
  ],
  "serie_temporal": {
    "2025-01": 8, "2025-02": 12, ...
  },
  "retrieved_at": "2026-06-25T12:00:00Z"
}
```

**Implementação:**
- Começar por HTTP + HTML/JSON embutido da página; usar Playwright/Firecrawl só se a página depender de renderização JS.
- URL pattern: `https://www.reclameaqui.com.br/empresa/{slug}/`.
- Resolver slug por URL explícita primeiro; busca por nome/CNPJ entra como helper separado para não bloquear o coletor principal.
- Respeitar rate limit e retornar `errors[]` quando a página bloquear ou não expuser dados.
- Testes: fixtures de 3 perfis (empresa grande, empresa média, empresa sem reclamações) + caso de página inexistente.
- CLI: `python3 -m tools.excrtx_source_reclameaqui.cli "Girando Sol" --output json`.

**Arquivo de saída:** `tools/excrtx_source_reclameaqui/`
**Skill wrapper:** `skills/excrtx-source-reclameaqui/SKILL.md`

### 4b. `excrtx-source-google-trends` — Coletor Google Trends

**Entrada:** Termo(s) de busca, período, região
**Saída:** JSON com séries temporais, distribuição geográfica, queries relacionadas

```
Input: ["Girando Sol", "Ypê", "Omo"], periodo="2021-01-01 2026-06-25", regiao="BR"
Output: {
  "termos": ["Girando Sol", "Ypê", "Omo"],
  "serie_temporal": {
    "Girando Sol": [{"date": "2021-01", "value": 12}, ...],
    "Ypê": [...], "Omo": [...]
  },
  "interesse_por_regiao": {
    "Girando Sol": {"RS": 100, "SC": 72, "PR": 45, ...}
  },
  "queries_relacionadas": {
    "Girando Sol": {
      "rising": ["girando sol reclamação", "girando sol coco baunilha"],
      "top": ["girando sol produtos", "girando sol onde comprar"]
    }
  },
  "retrieved_at": "2026-06-25T12:00:00Z"
}
```

**Implementação:**
- Biblioteca `pytrends` (zero auth). Declarar dependência no projeto; não instalar ad hoc durante execução sem aprovação.
- Envelopar em CLI padronizada
- **Padrões de consulta criativos:**
  - Autocomplete como sinal: `suggestions("Girando Sol")` → revela intenção real do consumidor
  - Correlação campanha↔busca: sobrepor picos com datas de feiras e lançamentos
  - Detector de concorrente: `related_queries` + filtro geográfico → quem está crescendo onde
- Testes: mock de resposta da API do Google Trends
- CLI: `python3 -m tools.excrtx_source_google_trends.cli "Girando Sol" --periodo "5y" --output json`

**Limitação operacional:** `pytrends` é API não-oficial. Sujeita a rate limit. Sem credenciais, sem SLA.
**Arquivo de saída:** `tools/excrtx_source_google_trends/`
**Skill wrapper:** `skills/excrtx-source-google-trends/SKILL.md`

### 4c. `excrtx-source-cnpj` — Coletor CNPJ / Receita Federal

> **Estado atual:** Implementação local já criada e validada com testes + smoke real. Esta seção passa a servir como contrato e checklist de fechamento, não como ideia futura.

**Entrada:** CNPJ (14 dígitos)
**Saída:** JSON com dados cadastrais públicos

```
Input: "12.345.678/0001-90"
Output: {
  "source": "cnpj",
  "query": "12345678000190",
  "retrieved_at": "2026-06-25T12:00:00Z",
  "data": {
    "cnpj": "12345678000190",
    "razao_social": "Girando Sol Limpeza e Higiene Ltda.",
    "nome_fantasia": "Girando Sol",
    "data_abertura": "1991-04-15",
    "capital_social": 5000000.00,
    "cnaes": [
      {"codigo": "2061-4/00", "descricao": "Fabricação de sabões e detergentes sintéticos"}
    ],
    "socios": [
      {"nome": "...", "qualificacao": "Sócio-Administrador"}
    ],
    "filiais": []
  },
  "provenance": {
    "url": "https://brasilapi.com.br/api/cnpj/v1/12345678000190",
    "method": "api",
    "raw_cached": false
  },
  "errors": []
}
```

**Implementação:**
- API primária: BrasilAPI (`https://brasilapi.com.br/api/cnpj/v1/{cnpj}`)
- Fallback: ReceitaWS (`https://www.receitaws.com.br/v1/cnpj/{cnpj}`), respeitando rate limit e falha estruturada
- Complementar com consulta de situação cadastral (ativa, suspensa, baixada)
- Testes: fixtures JSON estáveis; smoke real com CNPJs públicos só como teste opcional
- CLI canônica: `python3 -m tools.excrtx_source_cnpj.cli "12345678000190" --output json`

**Status local já verificado:**
- `tools/excrtx_source_cnpj/` criado
- `tests/test_source_cnpj.py` criado e passando
- `skills/excrtx-source-cnpj/SKILL.md` criada e validada em D1
- smoke real executado com `33000167000101`

**Ainda pendente para encerrar a issue:**
- publicar comentário remoto da issue só após aprovação explícita
- decidir se o fechamento remoto já inclui referência ao wrapper `#99` ou se isso fica detalhado no comentário da própria `#99`

**Arquivo de saída:** `tools/excrtx_source_cnpj/`
**Skill wrapper:** `skills/excrtx-source-cnpj/SKILL.md`

---

## Fase 5 — DocBrain Pipeline (PDF, Office, Web → Acervo)

> **Status:** DocBrain instalado. Falta adaptador Exocórtex→DocBrain e integração com o orquestrador.
> **Prioridade:** P0 — habilitante para consumir relatórios, catálogos e dados públicos em PDF
> **Dependências:** DocBrain funcional no runtime (verificar com health check)
> **Issues relacionadas:** #114, #115, #11 (drift de paths DocBrain)

### 5a. DocBrain Health Check & Reparo

**Objetivo:** Garantir que o DocBrain está operacional no runtime atual do Exocórtex.

```bash
cd /home/elder/projetos/projetob/docbrain
npm run --silent cli -- api health --output json
# Esperado: {"ok": true, "api_version": "docbrain.cli.v1", ...}
```

Se falhar:
- Verificar `node --version` (≥22)
- Não executar `npm install` sem aprovação. Se dependências estiverem ausentes, registrar diagnóstico e pedir autorização antes de instalar; depois rodar build.
- Verificar `.env` com `DOCBRAIN_LLM_API_KEY` ou `DEEPSEEK_API_KEY`
- Verificar Python 3.12+ e dependências Python; se faltar pacote, pedir autorização antes de instalar.

### 5b. `excrtx-adapter-docbrain-acervo` — Adaptador DocBrain → Acervo

**Objetivo:** Pipeline que recebe um arquivo, chama DocBrain para parse, e promove o resultado para o Acervo Cognitivo.

```
Fluxo:
  1. Arquivo chega (PDF de relatório, catálogo de feira, página web)
  2. DocBrain `api parse create --input {path} --include tables,sections --output json`
  3. Adaptador recebe JSON do DocBrain:
     - document_id, filename, extension, extractor
     - sections[] (títulos, texto estruturado)
     - tables[] (colunas, linhas tipadas)
  4. Adaptador classifica conteúdo por entidade (empresa, produto, categoria)
  5. Escreve no Acervo: micro/{empresa}/knowledge/{documento}.md
     - Frontmatter YAML com provenance (document_id, sha256, fonte)
     - Corpo: markdown com tabelas, seções, metadados
  6. Registra no log.md do microverso
```

**Formatos suportados pelo DocBrain (parse-service.ts):**

| Extensão | Extrator | Tabelas? | LLM opcional? |
|---|---|---|---|
| `.pdf` | LiteParse (+ Docling escalation) | Sim (nativas + LLM) | Sim (`--llm`) |
| `.xlsx/.csv` | Python extract_tables.py | Sim (tipadas) | Não |
| `.docx/.pptx` | MarkItDown | Sim (markdown tables) | Não |
| `.txt/.md` | TextAdapter | Sim (markdown tables) | Não |

**Casos de uso imediatos para inteligência competitiva:**

1. **Relatórios de sustentabilidade** (PDF 80p) → extrair metas, certificações, fornecedores
2. **Catálogos de feiras** (PDF/Excel) → extrair expositores, categorias, localização
3. **Demonstrações financeiras** (PDF S.A.) → extrair receita, margem, endividamento
4. **Diário Oficial** (PDF) → extrair licenças ambientais, alvarás
5. **Páginas web de associações** (scrape → DocBrain) → extrair dados de membros

**Arquivo de saída:** `skills/excrtx-adapter-docbrain-acervo/`
**Contrato:** [exocortex-to-docbrain](../../.harness/contracts/exocortex-to-docbrain.md)

---

## Fase 6 — Browser Agent com LLM (e-commerce, sites sem API)

> **Status:** Não iniciado
> **Prioridade:** P1 — maior complexidade, mas fecha o gap de preço praticado e avaliações de consumidor
> **Dependências:** Playwright instalado no ambiente Hermes; LLM capaz de raciocinar sobre DOM/snapshots
> **Issues relacionadas:** #116, #9 (Firecrawl local)

### 6a. `excrtx-source-ecommerce` — Coletor de Marketplaces

**Objetivo:** Navegar marketplaces brasileiros como um humano, extrair dados de produto que não existem via API.

**Entrada:** Nome da marca/produto
**Saída:** JSON com listagens, preços, avaliações

```
Input: "Girando Sol lava roupas"
Output: {
  "marketplaces": {
    "mercadolivre": {
      "listings": [
        {
          "titulo": "Lava Roupas em Pó Girando Sol Coco & Baunilha 1kg",
          "preco": 12.90,
          "vendedor": "Supermercado X",
          "avaliacoes": 47,
          "nota": 4.5,
          "url": "https://..."
        }
      ],
      "total_listings": 23,
      "preco_medio": 13.45,
      "preco_range": [8.90, 22.50]
    },
    "amazon": { ... },
    "magazineluiza": { ... }
  },
  "retrieved_at": "2026-06-25T12:00:00Z"
}
```

**Abordagem técnica:**

```
Playwright (navegador headless)
  → Navega até a página de busca do marketplace
  → Preenche campo de busca com termo
  → Aguarda renderização dos resultados
  → LLM analisa o DOM snapshot e decide:
      "Tem uma lista de produtos em elementos article[class*=product]"
      "O preço está em span.price ou div.price-tag"
      "A avaliação está em span.review-count ou div.stars"
  → Extrai os dados estruturados (não via XPath fixo — via LLM entendendo o layout)
  → Navega para próxima página se houver paginação
```

**Por que LLM + browser, não scraper tradicional:**
- Marketplaces mudam layout constantemente
- Bloqueiam scrapers padrão (User-Agent, fingerprinting)
- Playwright emula navegador real, LLM entende semântica, não selectores fixos
- Um único agente adaptável substitui 3 scrapers dedicados

**Marketplaces a cobrir (Fase 6a):**
1. Mercado Livre (maior volume de sellers)
2. Amazon Brasil
3. Magazine Luiza

**Arquivo de saída:** `tools/excrtx_source_ecommerce/`
**Skill wrapper:** `skills/excrtx-source-ecommerce/SKILL.md`

### 6b. `excrtx-source-gov` — Coletor de Sites Governamentais Arcaicos

**Objetivo:** Extrair dados de Diários Oficiais, licenciamento ambiental, juntas comerciais onde não há API e o formato é PDF, imagem ou HTML da década de 2000.

**Mesma abordagem técnica do e-commerce** (Playwright + LLM), mas com foco em:
- Download de PDF de edital → encaminha para DocBrain (Fase 5)
- OCR de imagem de publicação → LLM multimodal extrai entidade, atividade, local
- Navegação em sites sem busca textual → LLM entende a estrutura do site

---

## Fase 7 — Sinais Estruturados Profundos

> **Status:** Não iniciado
> **Prioridade:** P1 — sinal de alto valor mas complexidade média
> **Dependências:** Nenhuma crítica. Cada fonte é independente.
> **Issues relacionadas:** #117, #118, #119

### 7a. `excrtx-source-inpi` — Coletor INPI (Marcas e Patentes)

**Entrada:** Nome da empresa ou CNPJ do titular
**Saída:** JSON com pedidos de registro de marca e patentes

```
Input: "Girando Sol"
Output: {
  "marcas": [
    {
      "processo": "900123456",
      "marca": "Girando Sol Coco & Baunilha",
      "status": "Registrada",
      "data_deposito": "2024-08-15",
      "data_concessao": "2025-11-20",
      "classes_nice": ["03 - Produtos de limpeza"]
    }
  ],
  "patentes": [
    {
      "numero": "BR 102025012345-6",
      "titulo": "Composição detergente com microcápsulas de fragrância",
      "data_deposito": "2025-03-10",
      "status": "Em exame"
    }
  ],
  "retrieved_at": "2026-06-25T12:00:00Z"
}
```

**Implementação:**
- Consulta pública INPI: `https://busca.inpi.gov.br/` → formulário web
- Estratégia: Playwright + LLM (navega o formulário, submete busca, extrai resultado)
- Sem API oficial. Consulta pública via navegador.

**Valor para inteligência competitiva:**
- Patente de "composição detergente com microcápsulas de fragrância" → revela P&D 18 meses antes do produto
- Registro de marca em novas classes → revela plano de expansão de categorias

### 7b. `excrtx-source-anvisa` — Coletor ANVISA (Saneantes)

**Entrada:** Nome da empresa, CNPJ, ou número de registro
**Saída:** JSON com produtos registrados na categoria saneantes

```
Input: "Girando Sol"
Output: {
  "registros": [
    {
      "numero": "25351.123456/2025",
      "produto": "Limpador Perfumado Flor de Coco & Baunilha",
      "categoria": "Saneante Domissanitário",
      "data_registro": "2025-10-20",
      "validade": "2030-10-20",
      "principio_ativo": "Tensoativo aniônico"
    }
  ],
  "retrieved_at": "2026-06-25T12:00:00Z"
}
```

**Implementação:**
- Consulta pública ANVISA: `https://consultas.anvisa.gov.br/#/saneantes/`
- Similar ao INPI — Playwright + LLM para navegação do formulário web
- A ANVISA regula **todos** os produtos de limpeza — é o ground truth do portfólio real

### 7c. `excrtx-source-glassdoor` — Coletor Glassdoor / Indeed

**Entrada:** Nome da empresa
**Saída:** JSON com avaliações de funcionários e vagas abertas

```
Input: "Girando Sol"
Output: {
  "avaliacoes": {
    "nota_geral": 3.8,
    "total_avaliacoes": 23,
    "recomendam_ceo": 0.72,
    "pros": ["Bom ambiente", "Crescimento rápido"],
    "contras": ["Salário abaixo do mercado", "Hora extra frequente"]
  },
  "vagas_abertas": [
    {"titulo": "Vendedor Externo", "local": "Porto Alegre - RS", "data": "2026-06-20"},
    {"titulo": "Químico de P&D", "local": "Arroio do Meio - RS", "data": "2026-06-18"}
  ],
  "retrieved_at": "2026-06-25T12:00:00Z"
}
```

**Valor para inteligência competitiva:**
- "Vendedor Externo Porto Alegre" + "Vendedor Externo Curitiba" + "Vendedor Externo São Paulo" = expansão geográfica
- "Químico de P&D" = desenvolvimento de novo produto
- "Gerente de E-commerce" = vai digitalizar
- Headcount crescendo 30% em 6 meses = confirma expansão fabril

---

## Fase 8 — Sinais Indiretos e Criativos

> **Status:** Não iniciado
> **Prioridade:** P2 — menor densidade de sinal, mas cobre dimensões que nenhuma outra fonte atinge
> **Dependências:** Fase 5 (DocBrain) para documentos e Fase 6 (browser agent) para navegação web
> **Issues relacionadas:** #120

### 8a. Expositores de Feiras

**Fontes:** Catálogos de Expoagas, ExpoApras, APAS Show, ABRAS, SuperMinas

**Estratégia:**
1. Identificar feiras do setor no ano corrente
2. Obter catálogo de expositores (PDF, Excel, página web)
3. DocBrain (Fase 5) ou browser agent (Fase 6) para extrair lista completa
4. Cruzar com Acervo: "essa empresa está no nosso radar?"
5. Sinal: empresa que aparece pela primeira vez como expositora está investindo em presença de mercado

### 8b. Google Imagens de Gôndola

**Estratégia:**
1. Busca: `"Girando Sol" gôndola supermercado`
2. Coletar imagens de prateleiras (Google Images, redes sociais)
3. LLM multimodal analisa cada imagem:
   - Quantas faces de produto? (share of shelf)
   - Preço visível na prateleira?
   - Que marcas estão ao lado? (vizinhança competitiva real)
   - Em qual rede de supermercado? (distribuição)

### 8c. Podcasts e YouTube Regionais

**Estratégia:**
1. Busca YouTube: "Entrevista Girando Sol", "Caso de sucesso Arroio do Meio"
2. Transcrição automática (yt-dlp + whisper ou API de transcrição)
3. LLM extrai: menções a planos de expansão, novos produtos, parcerias
4. Canais de rádio e TV regional mencionam a empresa em contexto informal — sinal que a imprensa escrita não captura

### 8d. Grupos Públicos de Telegram/WhatsApp

**Estratégia (apenas grupos públicos):**
1. Monitorar grupos de representantes comerciais, distribuidores, varejistas
2. LLM classifica menções: lançamento, ruptura de estoque, promoção, reclamação
3. Sinal orgânico de canal — o que os vendedores comentam entre si

---

## Fase 9 — #100: Onboarding de Domínio

> **Issue existente:** #100 (P2a)
> **Status:** Planejada, não iniciada

**Objetivo:** Estender `excrtx-onboard-welcome` para capturar durante o onboarding:
- Ramo de atuação do executivo (ex: "bens de consumo — limpeza doméstica")
- Empresas do grupo (ex: nomes e CNPJs)
- Concorrentes diretos (ex: "Ypê, Urca, Mon Bijou")
- Empresas-alvo para monitoramento (ex: "Girando Sol")

**Saída:** Configuração que popula automaticamente as skills de coleta com os alvos corretos.

---

## Fase 10 — #101: Blueprint de Generalização

> **Issue existente:** #101 (P2b)
> **Status:** Planejada, não iniciada

**Objetivo:** Documentar o padrão replicável para criar domínios além de CPG:
- Construção civil
- Agronegócio
- Tecnologia/SaaS
- Saúde (hospitais, operadoras)

**Entregável:** Template de diretório + documento de passo a passo:

```
skills/excrtx-research-{domain}/
├── SKILL.md
├── scripts/orchestrate.py     # importa e adapta o orquestrador CPG
├── references/
│   ├── query-templates.md     # templates de busca específicos do domínio
│   └── sources.json           # fontes setoriais específicas (ex: Sinduscon, CBIC para construção)
└── tests/
    └── test_orchestrate.py
```

---

## Definition of Done para cada coletor novo

- [ ] CLI executa localmente e emite JSON parseável.
- [ ] Saída segue o envelope comum da Fase 4.
- [ ] Unit tests offline cobrem sucesso, ausência de dados e falha/rate limit.
- [ ] Smoke test real documenta comando e output ou registra bloqueio verificável.
- [ ] Skill wrapper inclui frontmatter Hermes, procedimento, pitfalls e verificação.
- [ ] DRAFT de comentário da issue inclui comandos executados, resultado e próximos riscos.

---

## Checklist de Publicação

- [x] Diagnóstico de gap documentado
- [x] Arquitetura de 7 camadas definida
- [x] Detalhamento técnico de cada fase (suficiente para sub-agentes executarem)
- [x] Referências cruzadas com issues existentes (#97, #98, #99, #100, #101, #108, #9, #11, #22)
- [ ] DRAFT do novo corpo da #97 apresentado ao executivo (incorpora Fases 4–8)
- [x] Issues filhas criadas: #111 `excrtx-source-reclameaqui`, #112 `excrtx-source-google-trends`, #113 `excrtx-source-cnpj`
- [x] Issues DocBrain criadas: #114 health check e #115 adaptador DocBrain→Acervo
- [x] Issues Fases 6–8 criadas: #116, #117, #118, #119, #120
- [ ] Issues #100, #101 revisadas para refletir novo escopo
- [ ] DocBrain health check executado (Fase 5a)

---

## Diagrama de Dependências

```
Fase 1 │ #108 Agent-Reach                ✅
Fase 2 │ #98 Crawler BR                  ✅
Fase 3 │ #99 Wrapper CPG                 ✅
       │
Fase 4 │ 4a Reclame Aqui                 ✅
       │ 4b Google Trends                ✅
       │ 4c CNPJ                         ✅
       │
Fase 5 │ 5a DocBrain health check        ⬜ (depende de #11 path drift)
       │ 5b Adapter DocBrain→Acervo      ⬜ (depende de 5a)
       │
Fase 6 │ 6a E-commerce browser agent      ⬜ (Playwright + LLM)
       │ 6b Sites gov arcaicos           ⬜ (depende de 6a)
       │
Fase 7 │ 7a INPI                         ⬜ (independente)
       │ 7b ANVISA                       ⬜ (independente)
       │ 7c Glassdoor                    ⬜ (independente)
       │
Fase 8 │ 8a-d Sinais indiretos           ⬜ (depende de Fases 5+6)
       │
Fase 9 │ #100 Onboarding                 ⬜ (independente)
Fase 10│ #101 Generalização              ⬜ (independente)
```

As Fases 4, 7 (sub-fontes), 9 e 10 são independentes entre si — podem rodar em paralelo.
Fases 5 e 6 habilitam a Fase 8. Fase 6 depende de Playwright + LLM multimodal.
