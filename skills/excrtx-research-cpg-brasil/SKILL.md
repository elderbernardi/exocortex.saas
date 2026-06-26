---
name: excrtx-research-cpg-brasil
description: Skill-wrapper de pesquisa setorial para indústria de bens de consumo no Brasil. Orquestra last30days (global), Agent-Reach (web/social), crawler-brasil (setorial) e documentos locais via DocBrain, entregando briefing executivo unificado em PT-BR seguindo o contrato de síntese adaptado do last30days.
version: 1.0.0
category: excrtx
platforms: [linux]
metadata:
  hermes:
    tags: [exocortex, research, cpg, brasil, fmcg, setorial]
    related_skills: [excrtx-integrate-last30days, excrtx-integrate-agent-reach, excrtx-crawler-brasil]
compiled_rules: |
  # This skill does not inject runtime rules; it is a tool-only skill.
---
# excrtx-research-cpg-brasil — Skill-wrapper CPG

> **Fase 3 da META #97** — Arquitetura de pesquisa setorial.
> Plano: `docs/plans/2026-06-24_pesquisa-setorial-arquitetura.md`

## When to Use

- O executivo pede um briefing setorial da indústria de bens de consumo no Brasil.
- Você precisa de uma visão consolidada de múltiplas fontes (global + setorial + web/social).
- O briefing será usado para decisão estratégica, preparação de reunião ou monitoramento de mercado.

**Don't use for:** Pesquisas pontuais de uma empresa específica (use o crawler direto). Tópicos fora do escopo CPG/FMCG. Briefings que não precisam de múltiplas fontes.

## Arquitetura

```
┌────────────────────────────────────────────────┐
│           orchestrate.py (Dispatcher)          │
│  --template panorama|varejo|inovacao|limpeza   │
└──┬─────────────────┬─────────────────┬─────────┘
   │                 │                 │
┌──▼──────────┐ ┌───▼──────────┐ ┌───▼──────────────┐
│ last30days  │ │ Agent-Reach  │ │ Crawler BR       │
│ (global)    │ │ (web/social) │ │ (setorial 13     │
│ Reddit, YT, │ │ web, YT,     │ │ fontes BR: Valor,│
│ HN, GitHub  │ │ RSS, GitHub  │ │ Exame, SuperHiper│
└─────────────┘ └──────────────┘ └──────────────────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                             │
                    ┌────────▼────────┐
                    │   Síntese PT-BR │
                    │  Badge + Insights│
                    │  + PADRÕES-CHAVE│
                    │  + emoji-footer │
                    └─────────────────┘
```

## Procedure

### 1. Executar pesquisa

```bash
# Template de panorama setorial (todas as fontes, ~2-3 min)
python3 skills/excrtx-research-cpg-brasil/scripts/orchestrate.py --template panorama

# Varejo e consumo (foco em supermercados e canais)
python3 skills/excrtx-research-cpg-brasil/scripts/orchestrate.py --template varejo

# Inovação e embalagens
python3 skills/excrtx-research-cpg-brasil/scripts/orchestrate.py --template inovacao

# Limpeza e household
python3 skills/excrtx-research-cpg-brasil/scripts/orchestrate.py --template limpeza

# Supply chain
python3 skills/excrtx-research-cpg-brasil/scripts/orchestrate.py --template supply

# Skip last30days para teste rápido (~30s)
python3 skills/excrtx-research-cpg-brasil/scripts/orchestrate.py --template varejo --skip-l30d

# Incluir documento local promovido via DocBrain no briefing e no JSON estruturado
python3 skills/excrtx-research-cpg-brasil/scripts/orchestrate.py \
  --template panorama \
  --skip-l30d \
  --output json \
  --document /abs/path/dossie.pdf \
  --document-microverso exocortex-dev \
  --document-acervo-root /abs/path/acervo
```

### 2. Interpretar o briefing

O output segue este contrato:

```
📊 CPG Brasil · [Template] · YYYY-MM-DD
   Fontes: last30days (N) + Agent-Reach (N) + Crawler BR (N) = Total

**O que aprendemos:**

[insight 1 com inline link]
[insight 2 com inline link]
...

**PADRÕES-CHAVE da pesquisa:**

1. Cobertura setorial BR: N itens de M fontes brasileiras
2. Alcance web/social: N itens via Agent-Reach
3. ...

---
✅ 🇧🇷 crawler-brasil · 🌐 agent-reach · 📰 last30days
   N itens · YYYY-MM-DD
```

### 3. Templates disponíveis

| Template | Foco | Fontes BR primárias |
|---|---|---|
| `panorama` | Movimentos macro do setor CPG | Todas as 13 fontes cpg |
| `varejo` | Supermercados, canais, consumo | superhiper, supervarejo, scanntech |
| `inovacao` | Embalagens, sustentabilidade, novos materiais | embalagem-marca, food-connection |
| `limpeza` | Produtos de limpeza, household | household-innovation, superhiper |
| `supply` | Logística, supply chain, gargalos | valor-economico, exame, infomoney |

Templates detalhados: `references/query-templates.md`

## Contrato de Síntese

A skill-wrapper adapta o contrato last30days (LAWs 1-8) para o contexto multi-fonte PT-BR:

1. **BADGE obrigatório:** Primeira linha com data, template e contagem de fontes
2. **"O que aprendemos":** Parágrafos com bold-lead-in e inline links. Sem `##` headers
3. **"PADRÕES-CHAVE":** Lista numerada com padrões e tendências identificados
4. **Emoji-footer:** Bloco final com fontes ativas e contagem total
5. **PT-BR sem slop:** Anti-slop ≥ 35/50. Sem jargão corporativo vazio
6. **Atribuição por fonte:** Cada insight indica origem (`[supervarejo]`, `[l30d]`, `[web·AR]`, `[docbrain]`)
7. **Documentos estruturados opcionais:** `--document` injeta artefatos promovidos via DocBrain em `structured_sources.docbrain` e os reflete nos padrões-chave

## Pitfalls

- **last30days timeout:** O engine leva 60-180s. Use `--skip-l30d` para testes rápidos
- **Resultados vazios no social:** Empresas B2B/regionais têm baixa superfície social. O crawler BR é a fonte primária para essas
- **Ruído do Google News:** Notícias de Copa do Mundo e política se misturam com economia nos feeds generalistas. A síntese prioriza itens do crawler BR setorial
- **Cache do crawler:** 15 min TTL. Para forçar refresh: `rm -rf /tmp/excrtx-crawler-cache`
- **Agent-Reach sem web search:** Sem Exa MCP, a busca web retorna apenas YouTube. Instale `mcporter` para busca semântica

## Verification

- [x] `--template varejo --skip-l30d` retorna briefing com ≥20 itens de 2+ fontes
- [x] Output segue contrato: badge + O que aprendemos + PADRÕES-CHAVE + emoji-footer
- [x] Todos os insights têm inline link e atribuição de fonte
- [x] Output em PT-BR sem slop
- [ ] Testes de integração: `python3 -m pytest tests/test_research_cpg_brasil.py -v`
- [ ] Dogfood: briefing real do setor CPG com dados de Jun/2026
- [ ] Skill passa D1 structural check

## Referências

- `scripts/orchestrate.py` — Dispatcher principal
- `references/query-templates.md` — Templates de query por ângulo
- Plano da META: `docs/plans/2026-06-24_pesquisa-setorial-arquitetura.md`
- Contrato de síntese: LAWs 1-8 do last30days (adaptado para PT-BR)
