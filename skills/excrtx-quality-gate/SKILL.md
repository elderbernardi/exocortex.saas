---
name: excrtx-quality-gate
description: Gate de qualidade aplicado pelo agente executor ao final de cada tarefa. Prosa passa por excrtx-quality-antislop, visual por excrtx-quality-taste. Correções são feitas pelo executor, nunca pelo orquestrador.
version: 1.1.0
category: exocortex
metadata:
  hermes:
    tags: [exocortex, behavior, quality, gate, excrtx-quality-antislop, excrtx-quality-taste]
    related_skills: [excrtx-quality-antislop, excrtx-quality-taste]
---

# Output Quality Gate — Responsabilidade do Executor

> O agente que produz o output é o agente que garante sua qualidade. O orquestrador **nunca** corrige — ele devolve.

## Princípio Central

```
Agente Executor  →  produz output  →  aplica quality gate  →  entrega
                                            ↓ (falha)
                                      corrige ele mesmo
                                            ↓ (falha 2x)
Orquestrador     →  detecta falha  →  devolve ao executor com feedback
                                      (NUNCA corrige por conta própria)
```

A qualidade do output é indissociável do contexto de produção. Um orquestrador que corrige perde o contexto do domínio, do modelo LLM usado, e da intenção original. Isso degrada a qualidade em vez de melhorá-la.

## Trigger

O agente executor aplica este gate como **último passo** antes de entregar qualquer output substantivo. O gate é parte do fluxo de produção, não uma camada externa.

## Escopo — Quando Aplicar e Quando Ignorar

### ✅ APLICAR (outputs para o executivo)

| Tipo | Gate | Exemplos |
|---|---|---|
| **PROSA** | `excrtx-quality-antislop` | Email, briefing, análise, reflexão, resumo, apresentação textual |
| **VISUAL** | `excrtx-quality-taste` | UI, dashboard, gráfico, layout, apresentação visual |
| **MISTO** | Ambos | Apresentação executiva com texto e métricas |

### ❌ IGNORAR (outputs técnicos)

| Tipo | Motivo | Exemplos |
|---|---|---|
| **CÓDIGO** | Estilo de código segue linters e convenções do projeto, não prosa humana | Scripts, configs, YAML, JSON, SQL, qualquer linguagem |
| **DOCUMENTAÇÃO TÉCNICA** | Clareza técnica > estilo narrativo. Jargão é necessário. | README, ADRs, SKILL.md, docstrings, comentários de código, specs, schemas |
| **DADOS BRUTOS** | Sem narrativa para filtrar | Tabelas numéricas, logs, dumps, CSVs |
| **RESPOSTAS CURTAS** | Overhead desproporcional | Confirmações ("Feito."), perguntas diretas, mensagens de sistema |
| **CITAÇÕES LITERAIS** | Fidelidade > estilo | Trechos de fontes externas reproduzidos ipsis litteris |

> **Regra de ouro:** Se o output é lido por máquinas ou por desenvolvedores em contexto técnico, o gate não se aplica.

## Procedure — Executor

### 1. Classificar o Output

Antes de entregar, o executor classifica:
- É prosa para o executivo? → Gate de Prosa
- É visual para o executivo? → Gate Visual
- É código, doc técnica, ou dados? → **Entregar sem gate**

### 2. Gate de Prosa (excrtx-quality-antislop)

Quick Checks — executar em cada parágrafo produzido:

| Check | Correção |
|---|---|
| Advérbio presente? | Cortar. "Significativamente aumentou" → "aumentou 40%" |
| Voz passiva? | Encontrar o ator. "Foi decidido que" → "O board decidiu" |
| Coisa inanimada com verbo humano? | "A decisão emerge" → "Elder decidiu" |
| Contraste "não X, é Y"? | Dizer Y diretamente |
| Frase soa como pull-quote? | Reescrever — se soa tweetável, está genérico |
| Declarativo vago? | Nomear. "Implicações significativas" → "Impacto: R$2M em margem" |
| Frase de enchimento? | Cortar. "É importante notar que" → (deletar) |

**Scoring (mínimo 35/50):**

| Dimensão | 10 pts | Pergunta |
|---|---|---|
| Diretividade | Declarações ou anúncios? | O texto diz algo ou se prepara para dizer? |
| Ritmo | Variado ou metrônomo? | Há mix de frases curtas e longas? |
| Confiança | Respeita o leitor? | Assume que o executivo é inteligente? |
| Autenticidade | Soa humano? | Alguém de verdade falaria assim? |
| Densidade | Algo cortável? | Cada frase carrega informação? |

### 3. Gate Visual (excrtx-quality-taste)

Pre-flight — verificar antes de entregar:

| Check | Correção |
|---|---|
| Hero ultrapassa 3 linhas? | Alargar container, reduzir fonte |
| Grid tem gaps vazios? | Aplicar grid-flow-dense |
| Labels genéricos (SECTION 01)? | Substituir por título descritivo |
| Layout idêntico ao anterior? | Forçar variação |
| Texto de botão invisível? | Corrigir contraste |

Sub-skill por contexto:
- Dados/métricas → `brutalist`
- Identidade/marca → `brandkit`
- Landing/produto/UI → `gpt-taste`

### 4. Correção pelo Executor

Se o gate falhar:

1. **O executor corrige ele mesmo** — ele tem o contexto do domínio, do prompt original, e do modelo LLM
2. **Re-aplica o gate** na versão corrigida
3. **Se falhar 2x** → sinalizar ao orquestrador com o output + diagnóstico de falha

### 5. Escalação ao Orquestrador

Quando o executor falha 2x no gate:

```
[QUALITY-GATE-FAIL] agent: {executor} | type: {prosa|visual} | score: {X}/50
Diagnóstico: {o que não passou}
Output anexado para revisão.
```

O orquestrador então:
1. **Devolve ao executor** com feedback específico ("reescreva o parágrafo 2, tom muito genérico")
2. **Ou roteia para outro agente/modelo** mais adequado ao tipo de output
3. **NUNCA** tenta corrigir o output por conta própria — isso degrada qualidade

## Regras

- O gate é **silencioso** — o executivo nunca sabe que existe
- O executor é o **único responsável** pela qualidade do seu output
- O orquestrador é **fiscal**, não **corretor** — devolve, não reescreve
- Quality score mínimo: 35/50 para prosa. Visual: zero falhas no pre-flight
- Código, documentação técnica e dados brutos **nunca** passam pelo gate
- Em caso de refatoração de skills, o gate continua vinculado ao executor — não migra para camada superior

## Verificação

- [ ] Briefing gerado pelo executor passa excrtx-quality-antislop (≥ 35/50)
- [ ] Draft de email gerado pelo executor passa excrtx-quality-antislop
- [ ] Dashboard gerado pelo executor passa excrtx-quality-taste pre-flight
- [ ] Código NÃO é filtrado pelo gate
- [ ] Documentação técnica (ADR, README, SKILL.md) NÃO é filtrada
- [ ] Falha 2x → orquestrador recebe sinalização, não corrige
- [ ] Orquestrador devolve ao executor com feedback, não reescreve
- [ ] O harness `validate_artifact_manifest.py` audita o pacote de artefatos rejeitando prosa com slop (score < 35) ou visual com meta-labels.
