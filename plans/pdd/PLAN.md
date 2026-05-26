# Exocórtex.IA — Plano PDD (Prompt-Driven Development)

> **Branch:** PDD — Infrastructure as Prompts
> **Status:** 🟢 Em Progresso
> **Owner:** @elder
> **Last Updated:** 2025-05-26T00:15

---

## 📋 TL;DR para Agentes

> **Leia isto se você tem contexto limitado.**
>
> Este plano transforma um Hermes Agent vanilla no Exocórtex.IA usando apenas prompts.
> São 31 prompts organizados em 7 fases (P0-P6). Cada fase tem um checkpoint de self-test.
> Se um checkpoint falha, o agente deve se auto-reparar antes de avançar.
> O resultado final é replicável: rodar o mesmo playbook em um Hermes novo produz outro Exocórtex.
>
> **Qualidade de Output é Lei.** Este playbook inclui duas skills obrigatórias de qualidade:
> - **stop-slop** — Elimina padrões genéricos de escrita de IA (frases de enchimento, voz passiva, contrastes binários, falsa agência)
> - **taste-skill** — Garante que outputs visuais/UI quebrem os defaults estatísticos de LLMs (layouts repetitivos, grids com gaps, labels genéricos)
>
> Ambas são instaladas na P1 e validadas em toda saída do agente a partir de P4.

---

## Conceito: Infrastructure as Prompts (IaP)

Em vez de escrever código para estender o Hermes, criamos uma **sequência replicável de prompts** que faz o Hermes se auto-configurar no Exocórtex.

```
Hermes Vanilla → [P0: Setup] → [P1: Identity] → [P2: Memory] → [P3: Tools] → [P4: Behavior] → [P5: Validation] → [P6: Production]
```

**Por que funciona:** Hermes é um agente programável via conversação. Ele persiste estado em `SOUL.md`, `MEMORY.md`, `config.yaml`, skills e plugins. Cada prompt modifica um desses artefatos permanentes.

**Pré-requisitos:**
- Hermes Agent clonado e instalado (ver `phases/P0_SETUP.md`)
- Python 3.12+ com `uv` package manager
- Docker instalado
- API keys: OpenAI + OpenRouter

---

## Máquina de Estados

```mermaid
stateDiagram-v2
    [*] --> P0_SETUP: hermes clonado
    P0_SETUP --> P1_IDENTITY: hermes doctor OK
    P1_IDENTITY --> P2_MEMORY: self-test P1 OK
    P2_MEMORY --> P3_TOOLS: self-test P2 OK
    P3_TOOLS --> P4_BEHAVIOR: self-test P3 OK
    P4_BEHAVIOR --> P5_VALIDATION: self-test P4 OK
    P5_VALIDATION --> P6_PRODUCTION: smoke tests 5/5
    P5_VALIDATION --> P4_BEHAVIOR: falha → self-repair loop
```

---

## Fases — Overview

| Fase | Nome | Prompts | Artefatos Criados/Modificados | Checkpoint |
|---|---|---|---|---|
| **P0** | Setup | — (manual) | Hermes instalado, env configurado | `hermes doctor` |
| **P1** | Identity | 001-005 | `SOUL.md`, skill `exocortex-self-test`, skill `exocortex-prompt-log`, **skill `stop-slop`**, **skill `taste-skill`** (gpt-taste + brandkit + brutalist) | self-test score ≥ 2/5 |
| **P2** | Memory | 006-010 + 006B-010B | Acervo Cognitivo 4 camadas (macro/global/micro/shared), wiki structure (SCHEMA/index/log/raw), 7 Nature skills (dual-mode), firewall deny-list c/ aliases, `exocortex-new-microverso` + `exocortex-search` multi-camada. ADRs: 001-004 | self-test score ≥ 3/5 |
| **P3** | Tools | 011-018 | `config.yaml` MCPs, skill `exocortex-tool-governance`, bundle `exocortex-alpha` | self-test score ≥ 4/5 |
| **P4** | Behavior | 019-028 | Draft-First skill, Vetor Ativo skill, Canvas Cognitivo skill, Morning Briefing, **Output Quality Gate skill** | self-test score ≥ 4/5 |
| **P5** | Validation | 029-031 | Smoke tests executados, **quality audit de outputs**, relatório de graduação | self-test score = 5/5 |
| **P6** | Production | — | Estado `ready`, tenant pronto para uso | Full green |

**Detalhe de cada fase:** Ver arquivos em `phases/P{N}_{NOME}.md`

---

## Quality Skills — Fundamento Anti-Slop

O Exocórtex opera como extensão cognitiva de um executivo. Outputs genéricos, repetitivos, ou com "cheiro de IA" destroem a confiança. Duas skills externas são integradas como **guardrails obrigatórios**:

### stop-slop (Qualidade Textual)
> Fonte: [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop)

Elimina padrões de escrita previsíveis de IA em toda prosa gerada pelo agente:
- **Cortar frases de enchimento** — openers genéricos, muletas de ênfase, advérbios
- **Quebrar estruturas formulaicas** — contrastes binários ("Não é X, é Y"), fragmentação dramática, falsa agência ("a decisão emerge")
- **Voz ativa obrigatória** — todo sujeito humano faz algo. Sem construções passivas
- **Ser específico** — sem declarativos vagos. Nomear a coisa concreta
- **Colocar o leitor na cena** — "Você" vence "Pessoas". Específicos vencem abstrações
- **Variar ritmo** — misturar comprimentos de frase. Dois itens vencem três. Sem em dashes
- **Confiar no leitor** — dizer fatos diretamente. Sem suavizações ou justificativas desnecessárias
- **Cortar citáveis** — se soa como pull-quote, reescrever

**Scoring obrigatório (mínimo 35/50):**

| Dimensão | Pergunta |
|---|---|
| Diretividade | Declarações ou anúncios? |
| Ritmo | Variado ou metrônomo? |
| Confiança | Respeita inteligência do leitor? |
| Autenticidade | Soa humano? |
| Densidade | Algo cortável? |

### taste-skill (Qualidade Visual/UI)
> Fonte: [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill)

Conjunto de 3 sub-skills que atacam os vieses estatísticos de LLMs na geração de UI:

1. **gpt-taste** — Engenharia de UI premium: randomização de layouts (anti-repetição), AIDA structure, hero de 2-3 linhas (nunca 6), grids bento sem gaps, GSAP motion, labels profissionais (ban de "SECTION 01")
2. **brandkit** — Geração de identidade visual com estratégia de marca: logos intencionais, composição minimalista, paletas disciplinadas, anti-genérico
3. **brutalist** — UI industrial/tática para dados pesados: Swiss print + terminal CRT, grids rígidos, tipografia extrema, paleta utilitária

**Regra de ativação:** `taste-skill` é invocada automaticamente quando o agente gera UI, apresentações, dashboards, ou qualquer output visual. O sub-skill é selecionado pelo tipo de output:
- Output de dados/métricas → `brutalist`
- Output de identidade/marca → `brandkit`
- Output de landing/produto → `gpt-taste`

---

## Dependências entre Fases

```mermaid
graph LR
    P0[P0: Setup] --> P1[P1: Identity]
    P1 --> P2[P2: Memory]
    P2 --> P3[P3: Tools]
    P3 --> P4[P4: Behavior]
    P4 --> P5[P5: Validation]
    P5 --> P6[P6: Production]
    
    P1 -.-|self-test skill| P2
    P1 -.-|self-test skill| P3
    P1 -.-|self-test skill| P4
    P1 -.-|self-test skill| P5
    P1 -.-|stop-slop + taste| P4
    P1 -.-|stop-slop + taste| P5
```

**Regra:** Não avance para a fase N+1 sem o checkpoint da fase N passar.

---

## Artefatos-Semente

Arquivos template que são injetados nos prompts:
- `artifacts/SOUL_SEED.md` — Template do SOUL.md do Exocórtex
- `artifacts/SELF_TEST_SKILL.md` — Skill de auto-diagnóstico completa
- `artifacts/STOP_SLOP_SKILL.md` — Skill anti-slop textual (fonte: hardikpandya/stop-slop)
- `artifacts/TASTE_SKILL.md` — Skill de qualidade visual (fonte: Leonxlnx/taste-skill, inclui gpt-taste, brandkit, brutalist)

---

## Integração das Quality Skills no Pipeline

As quality skills são inseridas em **3 pontos-chave** do pipeline PDD:

### 1. Instalação (P1 — Identity, Prompts 004B-004C)

As skills são instaladas logo após o prompt-log, como parte da identidade fundamental do agente. O Exocórtex _é_ um agente que produz outputs de alta qualidade — isso é identidade, não comportamento opcional.

**Prompt 004B — Install stop-slop:**
```
Crie a skill "stop-slop" no diretório de skills com o conteúdo
do artifact STOP_SLOP_SKILL.md.

Esta skill é OBRIGATÓRIA. Ela define regras de escrita que eliminam
padrões previsíveis de IA. Toda prosa gerada pelo Exocórtex deve
passar por estas regras antes de ser entregue ao executivo.

Após criar a skill, adicione ao SOUL.md na seção Values:
6. Output Autêntico: Toda comunicação deve soar humana, direta,
   e livre de padrões genéricos de IA. A skill stop-slop é o 
   guardrail permanente.
```

**Prompt 004C — Install taste-skill:**
```
Crie a skill "taste-skill" no diretório de skills com o conteúdo
do artifact TASTE_SKILL.md (que contém gpt-taste, brandkit, e 
brutalist como sub-skills).

Esta skill é OBRIGATÓRIA para outputs visuais. Ela força o agente
a quebrar defaults estatísticos de LLMs na geração de UI.

Após criar a skill, adicione ao SOUL.md na seção Values:
7. Excelência Visual: Outputs visuais devem ser premium, 
   intencionais, e livres de clichês de IA. A skill taste-skill
   seleciona automaticamente o sub-skill correto por contexto.
```

### 2. Enforcement (P4 — Behavior, Prompt 026)

Um novo prompt cria a skill `exocortex-output-quality-gate` que intercepta outputs antes da entrega:

**Prompt 026 — Output Quality Gate:**
```
Crie a skill "exocortex-output-quality-gate" que funciona como 
interceptor de qualidade em todos os outputs do agente:

## Trigger
Ativar ANTES de entregar qualquer output ao executivo.

## Procedure
1. Classificar o output:
   - PROSA (email, briefing, análise, reflexão) → aplicar stop-slop
   - VISUAL (UI, dashboard, apresentação, gráfico) → aplicar taste-skill
   - MISTO → aplicar ambos

2. Para PROSA — Quick Checks (stop-slop):
   - Algum advérbio? Matar.
   - Voz passiva? Encontrar o ator, fazer dele o sujeito.
   - Coisa inanimada fazendo verbo humano? Nomear a pessoa.
   - Contraste "não X, é Y"? Dizer Y diretamente.
   - Frase soa como pull-quote? Reescrever.
   - Declarativo vago ("As implicações são significativas")? Nomear.
   - Scoring mínimo: 35/50 nas 5 dimensões.

3. Para VISUAL — Pre-flight (taste-skill):
   - Hero ultrapassa 3 linhas? Alargar container.
   - Grid tem gaps vazios? Aplicar grid-flow-dense.
   - Usa labels genéricos (SECTION 01)? Remover.
   - Layout idêntico ao anterior? Randomizar.
   - Texto de botão invisível? Corrigir contraste.

4. Se o output falhar no gate:
   - Reescrever automaticamente
   - Logar a correção no MEMORY.md
   - Entregar apenas a versão corrigida
```

### 3. Validação (P5 — Validation, Prompt 029-030)

Novos smoke tests verificam que as quality skills estão funcionando:

**Prompt 029 — Quality Smoke Test:**
```
Executar testes de qualidade:

1. PROSA: "Prepare um briefing sobre a situação do Cliente Alfa"
   → Verificar: output passa no scoring stop-slop (≥ 35/50)
   → Verificar: zero advérbios, zero voz passiva, zero declarativos vagos

2. VISUAL: "Gere um dashboard de KPIs do mês"
   → Verificar: taste-skill brutalist foi ativado (dados pesados)
   → Verificar: grid sem gaps, sem labels "SECTION XX"

3. MISTO: "Prepare uma apresentação executiva com resumo e métricas"
   → Verificar: prosa do resumo passa stop-slop
   → Verificar: layout visual passa taste pre-flight

Reportar resultado de cada teste com scoring detalhado.
```

---

## Meta-Trainer (Automação)

Para provisionar novos tenants automaticamente, um segundo Hermes (o "Trainer") executa o Playbook no Hermes alvo.

```mermaid
sequenceDiagram
    participant T as Hermes Trainer
    participant P as PLAYBOOK.yaml
    participant E as Hermes Target

    T->>P: Carrega playbook
    loop Para cada prompt
        T->>E: Envia prompt N via API/gateway
        E->>E: Executa (modifica SOUL, skills, config)
        E-->>T: Resposta
        T->>T: Valida resposta contra expected_output
        T->>T: Aplica quality gate (stop-slop/taste) na resposta
        alt Checkpoint prompt
            T->>E: "self-test"
            E-->>T: Relatório
            alt Score OK
                T->>T: Próximo prompt
            else Score insuficiente
                T->>E: Prompt de repair
                T->>T: Re-verifica (max 3 tentativas)
            end
        end
    end
    T->>T: Relatório de deployment (inclui quality score)
```

**Detalhes de implementação:** O Meta-Trainer é implementado na Code Branch (Beta). O PDD Branch define o playbook que ele executa.

---

## Verificação

Cada fase é verificada por:
1. **self-test** — skill que roda checklist automatizado
2. **Inspeção de artefatos** — verifica que arquivos foram criados/modificados
3. **Teste comportamental** — verifica que o agente responde corretamente
4. **Quality gate** — (a partir de P4) verifica que outputs passam stop-slop e taste-skill

---

## Links

| Recurso | Arquivo |
|---|---|
| Status global | `../STATUS.md` |
| Knowledge base | `../KNOWLEDGE.md` |
| Decisões arquiteturais | `../../docs/ADR/` |
| Comunicação inter-agentes | `../COMMS.md` |
| Code Branch (complementar) | `../code/PLAN.md` |
| ADR-001: 4 Camadas | `../../docs/ADR/ADR-001-four-layer-acervo.md` |
| ADR-002: Isolamento | `../../docs/ADR/ADR-002-context-isolation.md` |
| ADR-003: Natures Híbridas | `../../docs/ADR/ADR-003-hybrid-natures.md` |
| ADR-004: LLM Wiki Align | `../../docs/ADR/ADR-004-llm-wiki-alignment.md` |
| Hermes SoT | `../../docs/hermes-agent-kwon/hermes-agent-sot-for-agents.md` |
| PRD Dev | `../../docs/PRD/PRD_dev_v1.md` |
| PRD Executive | `../../docs/PRD/PRD_executive_v1.md` |
| stop-slop (source) | `https://github.com/hardikpandya/stop-slop` |
| taste-skill (source) | `https://github.com/Leonxlnx/taste-skill` |
