---
name: excrtx-quality-gate
description: Use only on explicit request for the unified quality gate on this delivery.
  Classify output and route the requested checks; never rewrite it.
version: 3.0.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - behavior
    - quality
    - gate
    - routing
    - excrtx-quality-antislop
    - excrtx-quality-taste
    related_skills:
    - excrtx-quality-antislop
    - excrtx-quality-taste
    calibration:
    - feature_id: EX-21
      calibration_prompt: 'Só execute o gate a pedido expresso do executivo para esta entrega. Roteie o anti-slop apenas se ele também for pedido. Não revise texto. Classifique
        o output como prosa (→ excrtx-quality-antislop, piso 35/50), visual (→ excrtx-quality-taste),
        misto (→ os dois) ou técnico (→ sem gate). O executor aplica o gate e corrige;
        o orquestrador nunca corrige. Se falhar duas vezes, devolve com diagnóstico.
        A regra de estilo da prosa pertence ao excrtx-quality-antislop: não a reescreva
        aqui.'
      test_prompt: Aplique excrtx-quality-gate e anti-slop ao resumo executivo sobre o progresso do projeto 'portal-vendas'
        nesta semana para enviar ao board.
      acceptance_criteria: 'O agente classifica o output como prosa (nem visual nem
        técnico), encaminha a revisão de estilo ao excrtx-quality-antislop com o piso
        de 35/50, e não acrescenta número, responsável ou prazo que o pedido não forneceu.'
      remediation_tip: 'FALHA: gate não aplicado. No gate solicitado, encaminhe a prosa ao excrtx-quality-antislop só se essa revisão foi pedida; encaminhe o visual ao excrtx-quality-taste. O roteamento
        é seu; a revisão de estilo é da skill de destino.'
    - feature_id: EX-52
      calibration_prompt: 'O gate editorial só roda a pedido expresso. Independentemente dele, os artefatos gerados pelas skills de produção (excrtx-produce-artifacts,
        excrtx-produce-slides, excrtx-produce-oficios) devem passar pela validação
        do script validate_artifact_manifest.py, em acervo/global/tools/harness/.
        O piso anti-slop é inclusivo: pelo menos 35 de 50 passa. Layouts repetitivos
        ou meta-labels genéricos são rejeitados. A validação é aprovação de qualidade,
        não autorização para publicar: a publicação segue o Draft-First.'
      test_prompt: Gere o manifesto final para um relatório de auditoria recém-criado
        sob o id art_20260608_auditoria. Aplique excrtx-quality-gate e confira a validação técnica do pacote.
      acceptance_criteria: 'O agente explicita que o manifesto deve ser validado pelo
        script validate_artifact_manifest.py, com o caminho em acervo/global/tools/harness/;
        trata o piso anti-slop como inclusivo, de pelo menos 35 de 50; indica que
        layouts repetitivos e meta-labels genéricos seriam rejeitados; executa a validação
        antes da publicação, não depois; e mantém o artefato como rascunho até a autorização
        do executivo.'
      remediation_tip: 'FALHA: Quality Gate Bypassed. Todo artefato produzido pelas
        skills de produção deve ser validado por validate_artifact_manifest.py ANTES
        de publicar. Verificações obrigatórias: anti-slop de pelo menos 35 de 50,
        zero meta-labels genéricos, zero layouts repetitivos. Execute o script, respeite
        o código de saída e corrija as falhas reportadas — sem reescrever prosa fiel
        para subir o score.'
compiled_rules: |
  Only on explicit user request for the unified quality gate on the current delivery, load excrtx-quality-gate. It routes, never rewrites.
  When requested: route visual to excrtx-quality-taste; run excrtx-quality-antislop only if separately requested. A fidelity conflict stays in draft for the executive. Package validation never authorises publication.
---
# Output Quality Gate — Routing and Executor Responsibility

> This gate classifies output and routes it. The skill it routes to owns the review. The orchestrator **never** corrects — it returns.

## Core Principle

```
Executor Agent  →  produces output  →  routes to the owning gate  →  delivers
                                            ↓ (fail)
                                      corrects it themselves
                                            ↓ (fail twice)
Orchestrator    →  detects failure  →  returns to executor with feedback
                                      (NEVER corrects on its own)
```

Output quality is inseparable from production context. An orchestrator that corrects loses the domain context, the model used, and the original intent. Keeping routing separate from reviewing has a second reason: a style rule written here would compete with the skill that owns style, and the two copies drift apart.

## When to Use

Use only on an explicit user request for the gate on the current delivery, e.g. “rode o gate de qualidade neste relatório”. A mention, quotation, negation, previous activation, or request to write, review or deliver does not trigger it. Without opt-in, do not load, route, score or retry through this gate. Mandatory package validation and publication authority are separate and unchanged.

Requesting this gate alone does not request anti-slop. Identify the prose owner but leave that optional check unrun, without a score; run it only when expressly included (e.g. “rode o gate com anti-slop”).

**Don't use for:** Code, technical documentation (ADR, README, SKILL.md, docstrings, specs, schemas), raw data (CSV, logs, dumps), short confirmations ("Feito."), or literal quotes.

## Scope — When to Apply and When to Skip

### ✅ Routes after opt-in (the prose review needs its own opt-in)

| Type | Routes to | Examples |
|---|---|---|
| **PROSE** | `excrtx-quality-antislop` only if requested | Email, briefing, analysis, reflection, summary, textual presentation, authorial prose, didactic fiction |
| **VISUAL** | `excrtx-quality-taste` | UI, dashboard, chart, layout, visual presentation |
| **MIXED** | Visual pre-flight; anti-slop only if requested | Executive presentation with text and metrics |

### ❌ SKIP (technical outputs)

| Type | Reason | Examples |
|---|---|---|
| **CODE** | Code style follows linters and project conventions, not human prose | Scripts, configs, YAML, JSON, SQL, any language |
| **TECHNICAL DOCS AND SPECS** | Technical clarity beats narrative style. Jargon is necessary. | README, ADRs, SKILL.md, docstrings, code comments, specs, schemas |
| **RAW DATA** | No narrative to filter | Numeric tables, logs, dumps, CSVs |
| **SHORT RESPONSES** | Disproportionate overhead | Confirmations ("Feito."), direct questions, system messages |
| **LITERAL QUOTES** | Fidelity beats style | Verbatim excerpts from external sources |

> **Golden rule:** If the output is read by machines or by developers in technical context, the gate does not apply.

## Procedure — Executor

### 1. Classify the Output

Once the gate has been requested, the executor classifies:
- Prose for the executive? → identify the prose owner; route only if anti-slop was requested
- Visual for the executive? → route to the visual owner
- Both in one delivery? → route visual; route prose only if requested
- Code, technical docs, specs, or data? → **Deliver without gate**

For mixed deliveries, identify both owners. The prose floor applies only when the user included anti-slop; otherwise record the prose check as not requested, not as failed or passed.

### 2. Prose routing (excrtx-quality-antislop)

`excrtx-quality-antislop` owns the style review: what to cut, what to preserve, how to treat authorial voice and didactic fiction, and the scoring floor of **35/50** across Directness, Rhythm, Trust, Authenticity and Density.

For an explicitly requested prose check, this gate confirms only that the routing happened and that the floor was met. It does not restate the style rules here, and it does not rewrite the prose itself — including when it disagrees with the result.

### 3. Visual routing (excrtx-quality-taste)

`excrtx-quality-taste` owns the visual review: it runs the pre-flight, picks
the sub-skill for the context, and decides what a layout defect requires. This
gate hands the output over and reads what comes back — it does not restate the
checks or prescribe a fix, for the same reason it does not restate prose rules.

The destination returns the result to the executor: pass, or the failed
pre-flight items by name.

### 4. Artifact validation

Artifacts from the production skills (`excrtx-produce-artifacts`,
`excrtx-produce-slides`, `excrtx-produce-oficios`) go through the harness
`acervo/global/tools/harness/validate_artifact_manifest.py`, run against the
artifact directory, before publishing. A non-zero exit or an `ERROR` stops delivery.
On a draft, an anti-slop failure can be a `WARN` with exit zero. Read the
issues before clearing quality; apply the conflict branch below when fidelity is at stake.

**What the harness measures and what it does not.** Its anti-slop check is a
mechanical signal: it counts filler terms, `-mente` adverb density, passive
markers and em-dashes. That is a density proxy, not a fidelity judgement, and
`excrtx-quality-antislop` owns fidelity. The two can disagree, because the
owner of style requires impersonal constructions where the source names no
agent, and treats the travessão as ordinary PT-BR punctuation.

**When the script flags prose the style owner considers faithful** — an
open conflict, not a defect to fix:

1. **Keep the artifact as draft.** Do not publish, do not advance status.
2. **Quote the flagged excerpt** verbatim in the diagnosis, with the score and
   reported issues. If the script reports counts rather than a location,
   identify a relevant example in the source and label it as your example,
   not a passage located by the script.
3. Return the conflict to the executive as a decision, naming both sides: what
   the harness penalised and which fidelity rule requires it.

Two things the executor must not do: **never rewrite faithful prose to raise
the score**, and **never ignore the exit code** to publish anyway. Editing the
text to satisfy the counter is the failure this gate exists to prevent;
bypassing the exit is publishing an unvalidated package.

A clean validation clears quality, nothing else: **quality approval is not
publication authority**. Sending or publishing stays under **Draft-First** and
waits for the executive, so a validated artifact remains a draft until they
authorise it.

### 5. Correction by Executor

For a correctable defect only (a fidelity conflict stops at step 4):

1. **The executor corrects it themselves** — they hold the domain context, the original prompt, and the model
2. **Re-routes** the corrected version through the same gate
3. **After two failures** → signal to orchestrator with output and failure diagnosis

### 6. Escalation to Orchestrator

When the executor fails a gate twice:

```
[QUALITY-GATE-FAIL] agent: {executor} | type: {prose|visual|mixed}
Diagnosis: {domain-specific — see below}
Output attached for review.
```

The diagnosis follows the domain that failed, carrying a score only when prose
was reviewed:

| Failure | Diagnosis carries |
|---|---|
| Prose | the score out of 50 from `excrtx-quality-antislop`, plus what did not pass |
| Visual-only failure | the failed pre-flight item named by `excrtx-quality-taste`, no score |
| Both domains failed | the prose score and the failed visual item, separately; never report an unrequested check as failed |

A visual-only failure has no prose score to report, and inventing one hides
which domain broke.

The orchestrator then:
1. **Returns to executor** with specific feedback ("rewrite paragraph 2, tone too generic")
2. **Or routes to another agent/model** more suited to the output type
3. **NEVER** attempts to correct the output itself — this degrades quality

## Pitfalls

- **Gate rewriting prose**: Style rules duplicated here drift from `excrtx-quality-antislop` and leave two owners disagreeing over the same sentence. Route, record the result, escalate — never revise.
- **Orchestrator correction**: The orchestrator NEVER corrects output itself — it returns to the executor with feedback. Correcting at the orchestrator level loses domain context and degrades quality.
- **Gate fatigue**: Applying the gate to code, specs or technical docs wastes cycles and introduces false positives. Only prose and visual outputs for the executive are routed.
- **Mixed output shortcut**: Distinguish a check not requested from one that passed or failed.
- **Score inflation**: The floor is a floor, not a target, and it measures density rather than fidelity to the source.
- **Routine scores** stay internal. A fidelity conflict is not routine: use step 4 and wait for the executive’s decision.
- **Skill refactoring migration**: In skill refactoring, the gate remains bound to the executor — does not migrate to upper layers.

## Verification

- [ ] When anti-slop was requested, prose routed to excrtx-quality-antislop and floor 35/50 met; otherwise no prose score
- [ ] Visual output routed to excrtx-quality-taste pre-flight
- [ ] Mixed output classified by domain; prose floor applied only for requested anti-slop
- [ ] Code, specs and technical documentation NOT filtered by the gate
- [ ] This skill carries no prose style rule of its own
- [ ] No example here introduces a figure the source did not provide
- [ ] Failure twice → orchestrator receives signal, does not correct
- [ ] Orchestrator returns to executor with feedback, does not rewrite
- [ ] Before publication the harness `acervo/global/tools/harness/validate_artifact_manifest.py` returned exit zero for the artifact directory, without an error or unresolved quality warning
- [ ] A harness anti-slop failure on prose the style owner judges faithful left the artifact as draft, with the flagged excerpt quoted and the conflict returned to the executive
