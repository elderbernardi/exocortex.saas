---
name: excrtx-crawler-brasil
description: Brazilian sectoral crawler for CPG/FMCG research. Crawls 10+ RSS sources (Valor Econômico, Exame, G1, InfoMoney, Brazil Journal, CNN Brasil, Agência Brasil, Google News, Food Connection, Embalagem & Marca) with async fetch, rate limiting, and local cache. Outputs normalized JSON compatible with the Exocórtex research pipeline.
version: 1.0.0
category: excrtx
platforms: [linux]
metadata:
  hermes:
    tags: [exocortex, crawler, brasil, cpg, pesquisa, setorial]
    related_skills: [excrtx-integrate-agent-reach, excrtx-integrate-last30days, excrtx-research-cpg-brasil]
compiled_rules: |
  # This skill does not inject runtime rules; it is a tool-only skill.
---
# excrtx-crawler-brasil — Coleta em fontes setoriais brasileiras

> **Fase 2 da META #97** — Arquitetura de pesquisa setorial.
> Plano: `docs/plans/2026-06-24_pesquisa-setorial-arquitetura.md`

## When to Use

- Você precisa coletar notícias e dados de fontes brasileiras setoriais (economia, negócios, CPG/FMCG).
- O executivo pediu "colete dados do setor de bens de consumo no Brasil".
- Você quer alimentar o pipeline de pesquisa com fontes brasileiras complementares ao `last30days` e `Agent-Reach`.

**Don't use for:** Fontes com paywall (Valor PRO, Exame premium), APIs que exigem autenticação, ou coleta de fontes globais (use `last30days`).

## Arquitetura

```
┌─────────────────────────────────────┐
│         cli.py (CLI)                │
│  --domain cpg --limit 15            │
└──────────┬──────────────────────────┘
           │
┌──────────▼──────────────────────────┐
│      crawler.py (Orquestrador)       │
│  Async fetch, rate limit, cache      │
└──────┬───────┬───────┬───────────────┘
       │       │       │
  ┌────▼──┐ ┌─▼───┐ ┌─▼──────────┐
  │Valor  │ │Exame│ │Food Connect.│  ... (10 fontes)
  │(RSS)  │ │(RSS)│ │(RSS)        │
  └───────┘ └─────┘ └─────────────┘
```

## Procedure

### 1. Listar fontes disponíveis

```bash
python3 -m tools.excrtx-crawler-brasil.cli --list-sources
```

### 2. Coletar dados do domínio CPG

```bash
# JSON (default)
python3 -m tools.excrtx-crawler-brasil.cli --domain cpg --limit 10

# Texto legível
python3 -m tools.excrtx-crawler-brasil.cli --domain cpg --limit 10 --output text

# Fontes específicas
python3 -m tools.excrtx-crawler-brasil.cli \
  --sources "exame,valor-economico,food-connection" \
  --limit 15
```

### 3. Schema de saída

Todo item segue este schema:

```json
{
  "title": "Título da notícia",
  "url": "https://...",
  "date": "2026-06-25",
  "source": "valor-economico",
  "snippet": "Trecho do conteúdo (até 500 chars)",
  "domain": "cpg, economia, negocios",
  "retrieved_at": "2026-06-25T00:00:00Z"
}
```

## Fontes disponíveis (10)

| Slug | Nome | Tipo | Domínios |
|---|---|---|---|
| `valor-economico` | Valor Econômico | RSS | cpg, economia, negocios, financas |
| `exame` | Exame | RSS | cpg, economia, negocios |
| `g1-economia` | G1 Economia | RSS | cpg, economia, governo |
| `infomoney` | InfoMoney | RSS | cpg, financas, economia, investimentos |
| `brazil-journal` | Brazil Journal | RSS | cpg, negocios, economia |
| `cnn-brasil` | CNN Brasil | RSS | cpg, geral, economia |
| `agencia-brasil` | Agência Brasil | RSS | governo, geral |
| `google-news-economia` | Google News BR | RSS | cpg, economia, geral |
| `food-connection` | Food Connection | RSS | alimentos, cpg |
| `embalagem-marca` | Embalagem & Marca | RSS | embalagens, cpg |

## Pitfalls

- **RSS com ruído** → feeds generalistas (G1, CNN, InfoMoney) incluem esportes e política junto com economia. A skill-wrapper (#99) fará a filtragem por relevância.
- **Cache local** → `--limit` só afeta a primeira coleta; o cache (15 min TTL) retorna os mesmos dados. Para forçar refresh, limpe `/tmp/excrtx-crawler-cache/`.
- **Rate limiting** → 2s entre requests por domínio. Crawl de 10 fontes leva ~20s.
- **Fontes offline** → se uma fonte falhar (timeout, 5xx), o crawler simplesmente pula e continua com as demais.
- **IBGE e Gov.br** → testados mas bloqueados (502/403). Serão adicionados quando disponíveis.

## Verification

- [x] `--list-sources` mostra 10 fontes
- [x] `--domain cpg --limit 5` coleta de ≥5 fontes
- [x] Todos os itens têm schema completo (title, url, date, source, snippet, domain, retrieved_at)
- [x] Cache evita re-requests dentro de 15 min
- [x] Rate limiting respeita 2s entre requests por domínio
- [x] Smoke test real: 45 itens de 9 fontes (food-connection falhou no primeiro crawl, recuperou no segundo)
- [ ] Skill-wrapper CPG (#99) consome o output (Fase 3)

## Referências

- `tools/excrtx-crawler-brasil/sources.py` — Registry de fontes
- `tools/excrtx-crawler-brasil/crawler.py` — Orquestrador assíncrono
- `tools/excrtx-crawler-brasil/cli.py` — CLI
- Plano da META: `docs/plans/2026-06-24_pesquisa-setorial-arquitetura.md`
