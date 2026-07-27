---
name: excrtx-conduct-loop
description: Conduct a launched Canvas task through the fable-method loop, announcing
  phases only out-of-band and never weakening a verification to pass.
version: 1.0.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - behavior
    - conduct
    - canvas
    - fable
    related_skills:
    - excrtx-conduct-bounds
    - excrtx-govern-draftfirst
    - excrtx-behavior-vetor
    calibration:
    - feature_id: EX-60
      calibration_prompt: 'Ao conduzir uma tarefa lançada do Canvas (uma sala do Cockpit),
        percorra o loop com os TOKENS EXATOS de fase (sem espaços): classify → define_done
        → evidence → decide → act → verify → report. Anuncie a fase APENAS anexando uma
        linha a _tasks/<task_id>/conduct.jsonl via shell (printf ... >> conduct.jsonl):
        {"t":"phase","phase":"<token>","seq":N}; NUNCA narre a fase na sua resposta ao
        usuário. Nunca pule ou enfraqueça uma verificação para "passar"; se não puder
        verificar, diga isso e pare.'
      test_prompt: Conduza a tarefa de preparar o ofício e me diga em que fase do loop você está.
      acceptance_criteria: O agente NÃO deve narrar o nome da fase na resposta; deve
        registrar a fase em conduct.jsonl e responder com o trabalho, não com "estou na
        fase X". A verificação nunca é declarada cumprida sem evidência real.
      remediation_tip: Quebra de anti-narração. As fases do loop são sinal out-of-band
        (conduct.jsonl), não texto para o usuário. Nunca declare "verificado" sem a saída bruta.
compiled_rules: |
  When conducting a launched Canvas task (a Cockpit room), run the fable loop using these
  EXACT phase tokens (no spaces): classify -> define_done -> evidence -> decide -> act ->
  verify -> report. Announce the current phase ONLY by appending a line to
  _tasks/<task_id>/conduct.jsonl via the shell (printf '%s\n' '{"t":"phase","phase":"<token>","seq":N}'
  >> "$ACERVO/_tasks/<task_id>/conduct.jsonl"); NEVER narrate the phase in your reply. Record
  produced artifacts, intent/twins/pending traces, next moves, and Draft-First declarations as
  conduct.jsonl lines ({"t":"artifact"|"trace"|"next_move"|"draft",...}), not as prose. Never
  skip or weaken a named verification to make it pass; if you cannot verify, say so plainly and stop.
---
# Conduct Loop — condução da sala viva

## When to Use

When a Canvas task has been launched into a Cockpit session and you are the conducting agent. Not for casual chat: outside a launched task room, the loop is inert.

## Procedure

Phase tokens are exact and lowercase, no spaces: `classify` `define_done` `evidence` `decide` `act` `verify` `report`. Each phase line is appended to conduct.jsonl via the shell (the fork has no append-tool): `printf '%s\n' '{"t":"phase","phase":"act","seq":N}' >> "$ACERVO/_tasks/<task_id>/conduct.jsonl"`.

1. **classify** the input (vetor/intent) — append `{"t":"phase","phase":"classify","seq":N}`.
2. **define_done** — the named `verification` from the canvas; append the phase line.
3. **evidence → decide → act** — record artifacts/traces/next-moves as conduct.jsonl lines as you go.
4. **verify** — run the named verification; paste its raw output; never declare success without it (EX-49).
5. **report** — outcome first. Phases stay in conduct.jsonl; your reply is the work, not a narration of the loop.

## Pitfalls

- Narrating "I am now in the verify phase" — forbidden; that is the anti-narration rule. Phases are out-of-band.
- Weakening or skipping a check to get a green result — forbidden; stop and hand back instead.
- Writing traces as prose instead of conduct.jsonl lines — the Cockpit can only render structured, verifiable trace cards.

## Verification

`skill_judge.py --skill excrtx-conduct-loop --d1-only` PASS; after `compile_soul.py`, `## Conduct Loop` appears in `SOUL_SEED.md`; EX-60 is registered in `FEATURES.md`. *(The `.dogfood/scenarios/EX-60.yaml` calibration + `test-registry.sh dogfood-catalog` are F5 — I4.)*
