# Plano: Arquitetura de Pesquisa Setorial com Fontes Brasileiras

> **Plano para META #97** — 2026-06-24
> Atualizado para integrar #108 (Agent-Reach) como fase da arquitetura.

## Decisão

O executivo determinou que **#108 (Agent-Reach) deve ser integrada à META #97**, não tratada como issue paralela. A arquitetura passa a ter **4 camadas de coleta** em vez de 3, com o Agent-Reach fornecendo alcance web/social complementar ao last30days.

## Diagnóstico atual

- O briefing de tendências para "indústria de bens de consumo domésticos" via last30days global (2026-06-17) retornou 23 itens — 1 relevante.
- O engine varre Reddit, YouTube, HN e GitHub — fontes onde a indústria de CPG/FMCG não conversa.
- O debate setorial brasileiro acontece em portais especializados, associações de classe, bases governamentais e imprensa de negócios.
- A skill `excrtx-integrate-agent-reach` já existe como stub (v0.1.0), com schema normalizado definido.

## Arquitetura-alvo (4 camadas)

| Camada | Responsabilidade | Issue | Estado |
|---|---|---|---|
| **Coleta global** | last30days (existente) | EX-57 | Integrado |
| **Alcance web/social** | Agent-Reach — web, YouTube, RSS, GitHub, X/Twitter, Reddit | #108 | Skill stub existe |
| **Coleta setorial BR** | `excrtx-crawler-brasil` — portais, associações, bases governamentais | #98 | Não iniciado |
| **Síntese por domínio** | `excrtx-research-{domain}` — orquestra coleta + entrega briefing | #99 | Não iniciado |

Cada camada funciona independentemente. A skill-wrapper orquestra as três camadas de coleta e entrega briefing executivo em PT-BR.

## Fases

### Fase 1 — Agent-Reach (#108)
**Objetivo:** Integrar camada de alcance web/social ao pipeline de pesquisa.

- Auditar instalação segura no ambiente Hermes/Exocórtex
- Completar skill `excrtx-integrate-agent-reach` com wrapper de normalização funcional
- Smoke tests para canais zero-config: web, YouTube, RSS, GitHub
- Matriz de cobertura por canal (incluindo canais condicionais: X/Twitter, Reddit)
- Diagnóstico operacional (`agent-reach doctor`)
- Saída normalizada compatível com o contrato de síntese

### Fase 2 — Crawler BR (#98)
**Objetivo:** Coleta em fontes setoriais brasileiras com output padronizado.

- Crawler Python standalone (`excrtx-crawler-brasil`)
- Fontes: RSS de portais, APIs governamentais abertas, associações de classe (≥5 fontes)
- Formato de saída compatível com pipeline de síntese
- Sem dependência do engine upstream

### Fase 3 — Skill-wrapper CPG (#99)
**Objetivo:** Primeira skill de domínio. Orquestra last30days + Agent-Reach + crawler BR.

- Templates de query específicos para indústria de bens de consumo
- Síntese unificada com contrato last30days (badge, laws, KEY PATTERNS)
- Output em PT-BR
- Consome Agent-Reach e crawler BR como fontes plugáveis

### Fase 4 — Onboarding (#100)
**Objetivo:** Capturar ramo, empresas e concorrentes no onboarding.

- Estender `excrtx-onboard-welcome` para capturar: ramo de atuação, empresas do grupo, concorrentes
- Popular configuração da skill-wrapper automaticamente

### Fase 5 — Generalização (#101)
**Objetivo:** Blueprint para criar novos wrappers de domínio.

- Documentar padrão replicável (construção civil, agronegócio, etc.)
- Template de skill-wrapper

## Grafo de dependências

```
#108 (Agent-Reach) ──┐
                      ├──> #99 (wrapper CPG) ──┬──> #100 (onboarding)
#98 (crawler BR) ────┘                        └──> #101 (generalização)
```

- Fases 1 e 2 são independentes entre si — podem rodar em paralelo
- Fase 3 depende de ambas concluídas
- Fases 4 e 5 são independentes entre si e podem rodar em paralelo após a Fase 3

## Regras para agentes futuros

1. O crawler BR é independente do last30days — não fork, não monkey-patch
2. Agent-Reach é camada plugável/opcional — não substitui last30days nem crawler
3. O contrato de síntese (badge, What I learned, KEY PATTERNS, emoji-footer) é herdado do last30days upstream
4. Fontes precisam ser acessíveis sem autenticação na Fase 2 (RSS, APIs públicas)
5. O idioma do output final é PT-BR; coleta pode ser em português e inglês
6. O schema normalizado de cada item de coleta é: `title`, `url`, `date`, `source`, `channel`, `snippet`, `score`, `raw_provider`, `retrieved_at`

## Definição de Pronto da META

- [ ] Agent-Reach integrado com ≥4 canais zero-config testados (#108)
- [ ] Crawler rodando contra ≥5 fontes brasileiras setoriais com testes (#98)
- [ ] Skill-wrapper CPG gerando briefings sintetizados das 3 fontes (#99)
- [ ] Onboarding capturando ramo/empresas/concorrentes e populando config (#100)
- [ ] Blueprint de generalização documentado com template replicável (#101)
- [ ] ≥1 execução dogfood de ponta a ponta validada

## Checklist de publicação

- [x] Plano local escrito (`docs/plans/2026-06-24_pesquisa-setorial-arquitetura.md`)
- [ ] DRAFT do novo corpo da #97 apresentado ao executivo
- [ ] Aprovação do executivo para publicação
- [ ] Issue #97 atualizada com novo corpo
- [ ] Issue #108 atualizada com referência à fase na META
- [ ] Comentários de dependência publicados (#108 → blocks #99, #98 → blocks #99)
- [ ] Issues #99, #100, #101 ajustadas se necessário
