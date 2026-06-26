---
name: excrtx-source-reclameaqui
description: Public reputation collector for Brazilian companies on Reclame Aqui, with Cloudflare-aware error handling and structured JSON envelope.
version: 1.0.0
category: excrtx
platforms: [linux]
metadata:
  hermes:
    tags: [exocortex, reclameaqui, reputation, consumer, brazil, competitive-intelligence]
    related_skills: [excrtx-source-cnpj, excrtx-research-cpg-brasil, excrtx-crawler-brasil]
compiled_rules: |
  # This skill does not inject runtime rules; it is a tool-only skill.
---
# excrtx-source-reclameaqui — Coletor de reputação pública no Reclame Aqui

## When to Use

Use quando o executivo precisa avaliar a reputação pública de uma empresa brasileira:
- nota geral no Reclame Aqui
- total de reclamações e taxa de resposta
- categorias de problema mais frequentes
- reclamações recentes listadas
- série temporal de volume de reclamações

**Don't use for:** dados qualitativos profundos (análise sentimento), histórico completo de todas as reclamações, comparação automática entre concorrentes (use o wrapper `excrtx-research-cpg-brasil` para orquestração multi-fonte), qualquer dado que requeira login.

## Procedure

### 1. Executar a CLI

```bash
cd /home/elder/projetos/projetob/exocortex.saas
python3 -m tools.excrtx_source_reclameaqui.cli "Girando Sol" --output json
```

Também aceita slug ou URL completa:

```bash
python3 -m tools.excrtx_source_reclameaqui.cli "girando-sol" --output json
python3 -m tools.excrtx_source_reclameaqui.cli "https://www.reclameaqui.com.br/empresa/girando-sol/" --output json
```

### 2. Ler o envelope de saída

```json
{
  "source": "reclameaqui",
  "query": "Girando Sol",
  "retrieved_at": "2026-06-25T21:00:00Z",
  "data": {
    "empresa": "Girando Sol",
    "slug": "girando-sol",
    "nota_geral": 7.3,
    "total_reclamacoes": 142,
    "respondidas": 138,
    "taxa_resolucao": 0.87,
    "tempo_medio_resposta": null,
    "categorias_problema": [
      {"categoria": "Propaganda enganosa", "count": 23},
      {"categoria": "Qualidade do produto", "count": 18}
    ],
    "reclamacoes": [
      {"titulo": "...", "data": "2026-05-12", "status": "respondida", "categoria": "..."}
    ],
    "serie_temporal": {}
  },
  "provenance": {
    "url": "https://www.reclameaqui.com.br/empresa/girando-sol/",
    "method": "html",
    "raw_cached": false
  },
  "errors": []
}
```

### 3. Resultado com bloqueio Cloudflare (cenário atual)

No runtime atual (sem proxy residencial, sem browser com challenge solver), o Reclame Aqui bloqueia com Cloudflare Turnstile/managed challenge. O envelope retornado será:

```json
{
  "source": "reclameaqui",
  "query": "Girando Sol",
  "retrieved_at": "2026-06-25T21:00:00Z",
  "data": {
    "empresa": null,
    "slug": null,
    "nota_geral": null,
    ...todos os campos null ou listas vazias
  },
  "provenance": {
    "url": "https://www.reclameaqui.com.br/empresa/girando-sol/",
    "method": "html",
    "raw_cached": false
  },
  "errors": [
    {
      "code": "cloudflare_challenge",
      "message": "Reclame Aqui requer verificação Cloudflare...",
      "source": "cloudflare"
    }
  ]
}
```

### 4. Saída textual

```bash
python3 -m tools.excrtx_source_reclameaqui.cli "Girando Sol" --output text
```

## Pitfalls

- **Cloudflare bloqueio** — Em 2026, o Reclame Aqui usa Cloudflare Turnstile/managed challenge em todas as rotas (páginas, API de busca, endpoints internos). HTTP puro e browser headless básico são bloqueados. O coletor detecta esse bloqueio e retorna erro estruturado `cloudflare_challenge`. **Caminhos futuros:** Firecrawl MCP (quando configurado com endpoint válido), browser agent com Playwright e resistor de challenge, ou contrato de API oficial se o Reclame Aqui vier a oferecer.
- **Dados embutidos em Next.js** — Quando o acesso funciona, o RA renderiza dados via `__NEXT_DATA__`. O coletor tenta extrair JSON desse script antes de recorrer a scraping de HTML. Ambos os caminhos estão implementados e testados.
- **Rate limit** — O coletor impõe intervalo mínimo de 2s entre requisições. Se o RA retornar 429, o erro é reportado no envelope.
- **Slug não é CNPJ** — A busca por nome gera um slug (ex: "Girando Sol" → "girando-sol"), mas o slug pode não corresponder à página real da empresa. Se o usuário tiver o CNPJ, prefira usar `excrtx-source-cnpj` para obter o nome fantasia e depois derive o slug.
- **Série temporal** — O campo `serie_temporal` é preenchido apenas quando o RA expõe esses dados no HTML ou no NEXT_DATA..Atualmente é frequentemente `{}`
- **robots.txt** — O RA permite crawl de `/empresa/` mas bloqueia `/busca/`, `/respondendo/` e `/confieaqui/`. O coletor só acessa rotas permitidas.

## Verification

- [x] `python3 -m pytest tests/test_source_reclameaqui.py -q -m 'not slow'`
- [x] `python3 -m tools.excrtx_source_reclameaqui.cli --help`
- [x] `python3 -m tools.excrtx_source_reclameaqui.cli "Girando Sol" --output json` ( Cloudflare bloqueio esperado no runtime atual)
- [x] Erro `cloudflare_challenge` retornado de forma estruturada no envelope
- [ ] Coleta real funcional quando_firecrawl_ou_browser_agent estiverem disponíveis
