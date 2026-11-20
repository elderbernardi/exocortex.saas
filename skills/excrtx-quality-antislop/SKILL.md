---
name: excrtx-quality-antislop
description: Use only on explicit request for an anti-slop review of this delivery.
  Preserve meaning, authorship and register. Ordinary drafting or revision is not a trigger.
version: 3.0.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - quality
    - anti-slop
    - writing
    - style-review
    related_skills:
    - excrtx-quality-gate
    - excrtx-quality-taste
    calibration:
    - feature_id: EX-18
      calibration_prompt: 'Só aplique o anti-slop a pedido expresso do executivo para esta entrega. Nesse caso, você é responsável pela revisão de estilo da prosa
        entregue ao executivo. Corte o que não acrescenta informação. Preserve grau
        de certeza, citação literal, formulação autoral e quem agiu; quando a fonte
        não nomeia o agente, mantenha a construção impessoal em vez de inventar um
        sujeito. Registro oral, humor e ficção didática são escolhas legítimas: sinalize
        o conflito de estilo antes de reescrever. Pontue o próprio texto de 1 a 10
        em Directness, Rhythm, Trust, Authenticity e Density; abaixo de 35/50, revise.
        O piso mede densidade, não fidelidade — ele não substitui a conferência de
        sentido.'
      test_prompt: Aplique excrtx-quality-antislop ao escrever uma mensagem de atualização sobre o status da correção
        do bug para o executivo.
      acceptance_criteria: O texto vai direto ao ponto, factual, sem saudação nem
        enchimento, e não acrescenta causa, responsável, prazo ou número que o pedido
        não forneceu.
      remediation_tip: Falha de Anti-Slop. O texto tem abertura vazia ou baixa densidade.
        Corte o que não informa e confira, frase por frase, se o sentido da fonte
        continua o mesmo.
compiled_rules: |
  Only on explicit user request for anti-slop on the current delivery, load excrtx-quality-antislop. Otherwise no review or score.
  When requested: preserve certainty, quote and actor; 35/50 is not a certificate of fidelity.
---
# Stop Slop

Cut what the reader gains nothing from. Keep what the source actually said.

## When to Use

Use only on an explicit user request for anti-slop on the current delivery, e.g. “aplique o anti-slop neste texto”. The technical name is optional. “Revise este texto”, a mention or quotation of the name, “não aplique anti-slop”, a previous request or another skill listing this one is not consent. Without opt-in, write or revise normally without this skill or its score. Requesting anti-slop does not start the unified gate.

When requested, apply to authorial prose too — books, essays, lectures, narrative cases,
didactic fiction — under the fidelity rules below.

**Don't use for:** Code, technical documentation (README, ADR, SKILL.md,
docstrings, specs, schemas), raw data, CSV, logs, system messages. A literal
quote from an external source passes through untouched.

## Procedure

### 1. Read the source before editing it

Name, for yourself, what the text asserts: who acted, what happened, how
certain the claim is, and what the text leaves open. That inventory is the
contract the revision has to honour.

### 2. Cut what carries no information

Remove empty openers, filler, and decorative emphasis. Length is the symptom;
absence of information is the defect. A sentence that informs survives the
revision regardless of how it sounds.

### 3. Preserve the source

| Preserve | Failure to avoid |
|---|---|
| Degree of **certainty** — "talvez", "pode precisar", "cerca de" | Turning a hypothesis into a confirmed fact |
| An **estimate** as an estimate | Presenting an estimate as a measurement |
| Absence of a decision | Reporting it as a refusal |
| A **literal quote**, verbatim | Editing inside quotation marks |
| Who acted, as the source names them | Inventing an actor |
| An **impersonal construction** when the source names no agent | "Foram localizados" → "Localizamos" |

Modality lives in words a mechanical eye reads as cuttable. "Cerca de",
"talvez" and "ainda" carry information. Cut them and the revision asserts
something the source did not.

When the source names no agent, keep the impersonal construction.
**Never invent an actor**, and never borrow one from context to satisfy a
preference for active voice.

Add no figure, cause, deadline or responsible party that the source lacks.

### 4. Respect authorship and register

For **authorial** prose, the author's wording, cadence, metaphors, jokes and
localisms are the content, not noise around it. Prefer punctuation,
paragraphing and structural reduction over paraphrase. Operating order: retain
lexicon → retain cadence → reduce friction → only then rewrite isolated
phrases.

**Didactic fiction** — an invented classroom scene in a teaching book — is
admissible and **not a testimony**. Preserve the **oral register** ("profe",
"dá pra"), the pauses, and the characters' participation. Ask whether a reader
could mistake the scene for a recorded account; ask inside the text only when
the context creates that ambiguity. Executive-prose criteria do not apply to a
scene, and a scene is not evidence that anything worked in a real classroom.

### 5. Signal the conflict instead of deciding it

When a style preference collides with fidelity, authorship or register,
**signal the conflict** and leave the choice with the author. A revision that
reads better and sounds less like the author is a bad revision.

### 6. Score, then check meaning

Rate 1-10 on each dimension:

| Dimension | Question |
|-----------|----------|
| Directness | Statements or announcements? |
| Rhythm | Varied or metronomic? |
| Trust | Respects reader intelligence? |
| Authenticity | Sounds human? |
| Density | Anything cuttable without losing information? |

Below **35/50**: revise. The floor is inclusive — **35/50 exactly passes**, so
a text at the edge needs no edit on account of the score. The floor measures
density; it certifies neither voice nor fidelity. Run step 3 again on the
revised text before delivering.

**Didactic fiction and authorial prose:** a scene is not scored as executive
prose. Score it for its own purpose — does it teach, does it sound like the
author — and read Density as a question about the scene, not about a briefing:
Density never counts an intentional pause as cuttable, and neither do the
pauses, the oral register or a character's repetition count against Rhythm. The
floor does not license skipping the review: the fidelity checks still apply to a
scene, because the quote, the register and the characters' participation are the
content.

## Pitfalls

- **Mechanical prohibition**: A blanket ban on a word class deletes meaning.
  "Aproximadamente 40%" without "aproximadamente" claims a measurement nobody
  took. Judge each word by what it carries.
- **Voice preference over fidelity**: Forcing a subject onto every sentence
  invents actors. The source's silence about who acted is information.
- **False positives on technical prose**: Technical documents, code comments
  and system messages answer to other criteria. Leave them alone.
- **Flattening authorship**: A technically clean edit can still erase the
  author. For authored long-form the target is faithful amplification, not
  neutral polish.
- **Fiction judged as a report**: Scoring an invented scene by executive-prose
  criteria strips the oral register that makes it teach.
- **Cultural blindness**: PT-BR rhythm differs from English. Three-item lists
  and travessões are ordinary in Portuguese formal writing.
- **Score as certificate**: 35/50 is a floor on density. A text can clear it
  and still misstate the source.
- **Mechanical score as editing licence**: A counter — the artifact harness's
  adverb, passive and em-dash tally, or any similar lint — is a **mechanical
  signal** of density. A low score **does not authorise changing faithful
  text**. When the counter penalises exactly what fidelity requires, report the
  conflict with the excerpt quoted and leave the decision upstream.

## Verification

One list, run before delivering. Each line names the defect and the repair.

- [ ] Certainty, modality and hedges survive the revision — claims more than the source? **restore the hedge**
- [ ] Estimates are not presented as measurements
- [ ] Literal quotes are identical to the source — anything different inside quotation marks? put it back
- [ ] No actor, figure, cause or deadline absent from the source appears — appeared from nowhere? **remove it**
- [ ] Impersonal constructions kept where the source names no agent — an actor appeared? **restore the impersonal** form
- [ ] Authorial wording, cadence and oral register preserved
- [ ] Didactic fiction reviewed as fiction, not as a report
- [ ] Style conflicts signalled to the author, not resolved unilaterally
- [ ] No opener prepares to say something instead of saying it, and no sentence carries no information — cut both
- [ ] Vary a sentence only when the rhythm is accidentally repetitive; preserve deliberate repetition, pauses and authorial cadence. If intent is unclear, ask the author instead of rewriting.
- [ ] Replace a generic phrase only with a specific one supported by the source.
- [ ] Score ≥ 35/50 across 5 dimensions (35 passes), with step 3 re-run afterwards
- [ ] Technical docs and code NOT filtered by anti-slop
- [ ] PT-BR prose evaluated with PT-BR rhythm expectations
