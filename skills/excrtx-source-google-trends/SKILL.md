---
name: excrtx-source-google-trends
description: Public Google Trends query for interest-over-time, regional interest, and related queries via the Explore API with normalized JSON envelope.
version: 1.0.0
category: excrtx
platforms: [linux]
metadata:
  hermes:
    tags: [exocortex, google-trends, trends, search, popularity, competitive-intelligence, api]
    related_skills: [excrtx-source-cnpj, excrtx-crawler-brasil]
compiled_rules: |
  # This skill does not inject runtime rules; it is a tool-only skill.
---
# excrtx-source-google-trends — Coletor de tendências de busca do Google

## When to Use

Use when the executive needs to understand consumer search behavior, brand awareness signals, or competitive positioning via search volume:
- interest over time for one or more terms
- geographic distribution of search interest
- related queries (rising/top) for keyword expansion
- autocomplete suggestions for consumer intent inference

**Don't use for:** precise market-size estimation (relative values only), historical data older than ~5 years via public endpoint, or data when Google blocks/ rate-limits the request.

## Procedure

### 1. Executar a CLI

```bash
cd /home/elder/projetos/projetob/exocortex.saas
python3 -m tools.excrtx_source_google_trends.cli "Girando Sol" --periodo "5y" --output json
```

### 2. Multi-term comparison

```bash
python3 -m tools.excrtx_source_google_trends.cli "Girando Sol, Ypê, Omo" --periodo "5y" --geo BR --output json
```

### 3. Short period with autocomplete

```bash
python3 -m tools.excrtx_source_google_trends.cli "Girando Sol" --periodo "3m" --autocomplete --output json
```

### 4. Custom date range

```bash
python3 -m tools.excrtx_source_google_trends.cli "Girando Sol" --periodo "2025-01-01 2026-06-25" --output json
```

### 5. Ler o envelope de saída

```json
{
  "source": "google_trends",
  "query": "Girando Sol",
  "retrieved_at": "2026-06-25T20:24:45Z",
  "data": {
    "termos": ["Girando Sol"],
    "serie_temporal": {
      "Girando Sol": [{"date": "2021-06", "value": 12}, ...]
    },
    "interesse_por_regiao": {
      "Girando Sol": {"RS": 100, "SC": 72, "PR": 45}
    },
    "queries_relacionadas": {
      "Girando Sol": {
        "rising": ["girando sol coco baunilha"],
        "top": ["girando sol produtos", "girando sol onde comprar"]
      }
    }
  },
  "provenance": {
    "url": "https://trends.google.com/trends/explore?q=...&geo=BR&date=today%205-y",
    "method": "api",
    "raw_cached": false,
    "geo": "BR",
    "period": "today 5-Y"
  },
  "errors": []
}
```

## Pitfalls

- **Sem autenticação** — o endpoint público `trends.googleapis.com/data/api/v1/explore` não requer credencial mas pode retornar 429 (rate limit) ou 403 (block). Não há SLA.
- **Valores relativos** — o Google retorna valores normalizados (0–100), não volume absoluto de buscas. Não somar entre períodos diferentes.
- **Granularidade** — períodos longos retornam dados mensais; períodos curtos podem retornar diários. O parser converte `YYYY-MM-DD` para `YYYY-MM`.
- **Bloqueio** — se a requisição falhar consistentemente, rate limit ou geo-block é a causa mais provável. Documentar o erro no campo `errors[]`.
- **Biblioteca pytrends** — não utilizada. Esta implementação chama os endpoints públicos diretamente via `httpx`, sem dependências extras.

## Verification

- [x] `python3 -m pytest tests/test_source_google_trends.py -q -m 'not slow'`
- [x] `python3 -m tools.excrtx_source_google_trends.cli --help`
- [x] Smoke real: `python3 -m tools.excrtx_source_google_trends.cli "Girando Sol" --periodo "5y" --output json`
- [ ] Integração com `excrtx-research-cpg-brasil` quando conectado ao wrapper multi-fonte (Fase 4)
