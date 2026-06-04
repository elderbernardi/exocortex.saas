# ADR-010 — Deployment em Camadas do Exocórtex

## Status

Aceita (candidate-release consolidation, 2026-06-03)

## Contexto

O Exocórtex.IA possui quatro métodos de deployment que emergiram organicamente:
- **PDD (Prompt-Driven Development):** setup.sh + 27 prompts sequenciais
- **Replicable Setup Workflow:** 12 etapas procedurais com Hindsight, DocBrain, estúdio criativo
- **Harness v0.4 Setup Plan:** 8 etapas focadas na ontologia operacional
- **Memória Operacional:** personalização via Hindsight/Hermes Memory

Nenhum método isolado cobre todos os requisitos: reprodutibilidade, personalização contínua, proteção contra drift do Hermes e cobertura completa da ontologia v0.4.

O executivo levantou explicitamente que PDD "é para prevenir drift em caso de updates mais sérios do Hermes e procurar personalização baseada em memórias, conforme o agente é modelado. Mas não é verdade canônica."

## Decisão

Adotar abordagem em **três camadas**, cada uma responsável por um aspecto distinto:

### Camada 1 — Infraestrutura (Métodos B + C)
- Cria `~/exocortex`, acervo, diretórios operacionais, templates, scripts
- Instala skills, profiles, bundles
- **Resultado:** Hermes pronto para receber personalização
- **Frequência:** Uma vez por instância (ou após upgrade do Hermes)
- **Fonte:** `replicable-exocortex-setup.md` + `exocortex-harness-v0.4-setup-plan.md`

### Camada 2 — Identidade (Método A, simplificado)
- Aplica SOUL.md, quality skills, valores, limites, personas
- Valida com self-test progressivo
- **Resultado:** Hermes transformado em Exocórtex.IA
- **Frequência:** Uma vez por instância (ou reset deliberado)
- **Fonte:** PDD v2 P1 (simplificado)

### Camada 3 — Evolução (Método D)
- Personaliza via memória operacional (Hindsight), interações, decisões
- Adapta sem re-deployment
- **Resultado:** Exocórtex cada vez mais afinado ao executivo
- **Frequência:** Contínua
- **Fonte:** Hindsight + Acervo como fonte canônica semântica

## Consequências

### PDD v2 muda de papel
- **Antes:** Blueprint de deployment (os 27 prompts são a verdade)
- **Depois:** Checklist de validação (os 27 prompts validam que as camadas estão corretas)

### setup.sh muda de escopo
- **Antes:** Provisiona tudo para `HERMES_HOME`
- **Depois:** Provisiona Camada 1 para `EXOCORTEX_HOME` e `HERMES_HOME` separados

### Personalização muda de mecanismo
- **Antes:** Re-executar prompts PDD
- **Depois:** Acervo v2 + Hindsight acumulam decisões, preferências e contexto

## Alternativas rejeitadas

- **PDD puro:** Não escala para personalização contínua
- **Skill monolítica `exocortex-harness-v0.4`:** Mais frágil, menos auditável
- **Manter deployment fragmentado:** Gera drift entre fontes

## Referências

- `plans/pdd_v2/PLAN.md`
- `micro/hermes-setup/workflows/replicable-exocortex-setup.md`
- `micro/harness-project/knowledge/exocortex-harness-v0.4/07-roadmap-e-pendencias.md`
- `micro/hermes-setup/decisions/hermes-runtime-cwd-exocortex-home.md`
