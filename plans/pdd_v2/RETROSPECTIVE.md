# PDD v1 → v2: Retrospectiva e Análise de Drift

> **Propósito:** Análise formal dos desvios entre o plano original (v1) e a execução real.
> Documenta o que funcionou, o que falhou, e o que emergiu organicamente.
> Este documento é a base factual para as decisões arquiteturais do PLAN_v2.

---

## 1. Desvios Estruturais (Drift Arquitetural)

### D1: Consolidação de Skills (7 → 1)
- **Plano v1:** 7 Nature skills individuais (contexto, conhecimento, instrucoes, persona, processos, ferramentas, reflexoes) + exocortex-search
- **Execução real:** Consolidação em `acervo-manager` (ADR-005)
- **Causa:** As 7 Natures eram **classificação de dados**, não comportamentos distintos. A mecânica (READ/WRITE/SEARCH/PROMOTE) era idêntica — só o frontmatter mudava.
- **Impacto:** Positivo. Reduziu 8 skills para 1. Eliminou duplicação de lógica. Simplificou o bundle.
- **Lição v2:** Projetar skills por **operação**, não por **taxonomia de dados**. Dados se classificam por frontmatter; skills se classificam por verbo.

### D2: Arquitetura de 4 Camadas (LLM Wiki)
- **Plano v1:** Acervo com 2 camadas implícitas (macro + microversos)
- **Execução real:** 4 camadas explícitas (macro / global / micro / shared) com lógica de wiki (index.md, _index.md, promoção arquivo→diretório)
- **Causa:** A P2 revelou que sem camada `global/` as regras universais se duplicavam em cada microverso, e sem `shared/` as referências cruzadas se perdiam.
- **Impacto:** Positivo. Isolamento de contexto funcional. Cross-refs sem duplicação.
- **Lição v2:** A camada `global/` e `shared/` devem existir **desde o P0**, não serem descobertas durante P2.

### D3: Quality Skills como Identidade (P1), não Comportamento (P4)
- **Plano v1:** stop-slop e taste-skill previstas para P4 (Behavior)
- **Execução real:** Instaladas em P1 como Prompts 004B/004C, com Values #6 e #7
- **Causa:** Qualidade de output é **constitutiva da identidade** do Exocórtex, não uma regra de negócio que se adiciona depois. O agente que não escreve bem "desde o primeiro dia" produz artefatos de P2/P3 com baixa qualidade.
- **Impacto:** Positivo. Toda prosa gerada durante P2-P5 já passou pelo gate de qualidade.
- **Lição v2:** Quality skills são P0 (pré-requisito), não P4.

### D4: Provisionamento Desacoplado
- **Plano v1:** Onboarding com auto-provisionamento implícito
- **Execução real:** Provisioner Agent como entidade externa (v1.1.0 do onboarding)
- **Causa:** O Hermes do executivo **não pode provisionar a si mesmo** — violaria o princípio de separação de concerns e criaria ciclo de dependência.
- **Impacto:** Positivo. Autonomia do Hermes-alvo preservada.
- **Lição v2:** O PDD configura o **produto** (golden image). O provisionamento é um processo externo que consome a golden image.

### D5: Configuration Discipline como Protocolo Transversal
- **Plano v1:** Nenhum protocolo formal de disciplina de configuração
- **Execução real:** `agent_protocol` com 5 regras de ouro (LOG_ALL, UPDATE_SETUP, VERIFY_BEFORE_DONE, BACKLOG_WITH_CRITERIA, STATE_IS_TRUTH)
- **Causa:** Agentes de P1/P2 tomavam ações sem registrar, gerando drift entre setup.sh e estado real.
- **Impacto:** Crítico positivo. Sem isso, a reprodutibilidade do PDD seria impossível.
- **Lição v2:** O agent_protocol deve ser o **primeiro artefato lido** pelo agente, antes de qualquer prompt.

### D6: Backlog com Critérios de Reavaliação
- **Plano v1:** MCPs (011-014) previstos como parte do fluxo sequencial
- **Execução real:** MCPs diferidos para BACKLOG_INTEGRATIONS.md com critérios de reavaliação + BKL-002 resolvido com alternativa (DDG + browser-use)
- **Causa:** Dependências externas (API keys, OAuth) não disponíveis. Nenhum teste de P4/P5 dependia deles.
- **Impacto:** Positivo. O plano avançou sem bloqueios.
- **Lição v2:** Integrações externas são **extensões pós-golden-image**, não parte do fluxo principal.

---

## 2. O que Funcionou (Preservar em v2)

| Aspecto | Por quê |
|---|---|
| **Fases sequenciais (P1→P6)** | Cada fase valida a anterior via self-test. Gate explícito impede avanço prematuro. |
| **Prompts como unidade atômica** | Cada prompt tem propósito, artefatos esperados, e validação. Reproduzível. |
| **Self-test progressivo** | Score cresce de 2/5 (P1) para 5/5 (P5). Feedback loop claro. |
| **SOUL.md como Constituição** | Identidade centralizada. Herda para todas as skills. |
| **Smoke tests obrigatórios** | VERIFY_BEFORE_DONE evitou que skills "fantasma" passassem despercebidas. |
| **Logs detalhados** | Cada sessão tem log completo. Permitiu esta retrospectiva. |

## 3. O que Falhou (Corrigir em v2)

| Falha | Sintoma | Causa Raiz |
|---|---|---|
| **Natures como skills separadas** | 8 skills com lógica idêntica | Confundiu taxonomia com comportamento |
| **Quality skills tardias** | Prosa de P2/P3 sem gate de qualidade | Tratadas como "comportamento" (P4) em vez de "identidade" (P1) |
| **Setup.sh desatualizado** | Drift entre estado real e script | Protocolo de disciplina inexistente nas primeiras fases |
| **MCPs no fluxo principal** | Bloqueio por API keys | Integrações externas misturadas com configuração core |
| **Acervo sem camadas** | Dados universais duplicados em microversos | Arquitetura de 2 camadas insuficiente |
| **Falta de auto-auditoria** | Drift detectado apenas no P5 | Nenhum checkpoint intermediário de integridade |

## 4. O que Emergiu (Incorporar em v2)

| Emergência | Como nasceu | Como incorporar |
|---|---|---|
| **acervo-manager unificado** | Refatoração orgânica de P2 | Projetar desde o início como skill única |
| **4 camadas (macro/global/micro/shared)** | Necessidade prática de P2 | Incluir no P0 como pré-requisito arquitetural |
| **agent_protocol** | Resposta a drift de P1-P3 | Codificar como artefato-semente obrigatório |
| **BACKLOG_INTEGRATIONS.md** | Resposta pragmática a bloqueios de P3 | Template no P0 para integrações futuras |
| **Promoção arquivo→diretório** | LLM Wiki pattern de P2 | Codificar no acervo-manager desde o início |
| **Output Quality Gate** | Separação executor/orquestrador em P4 | Manter como skill comportamental, mas quality skills em P0 |

---

## 5. Mapeamento Framework Exocórtex → Hermes

| Conceito Exocórtex | Implementação Hermes (v1) | Ajuste para v2 |
|---|---|---|
| **Macroverso** | `SOUL.md` + `acervo/macro/` | Correto. Preservar. |
| **Microverso** | `acervo/micro/{slug}/` + profiles | Correto. Preservar. |
| **Tarefa** | Input direto do executivo | Correto. Preservar. |
| **Canvas Cognitivo** | `exocortex-canvas` skill (extrator) | Funcional. Preservar. |
| **Vetor de Evolução** | `exocortex-vetor-ativo` + profile `evol` | Funcional. Preservar. |
| **Vetor de Execução** | `exocortex-vetor-ativo` + profile `exec` | Funcional. Preservar. |
| **7 Natures** | `acervo-manager` (unificado) | Correto. Nature = frontmatter, não skill. |
| **HITL (Human-in-the-Loop)** | `exocortex-draft-first` | Funcional. Preservar. |
| **Escalada Gentil** | Fases P1→P6 | Preservar, ajustar fronteiras (ver PLAN.md). |
| **Princípio da Autoria** | `stop-slop` + `taste-skill` | Mover para P0 como pré-requisito. |

---

> **Este documento é read-only.** As decisões derivadas dele estão em `PLAN.md`.
