# ADR-CT-07 — Portar o método de condução como skills (`excrtx-conduct-*`), não embutir no brief

status: proposta (aprovação = merge do PR collab/canvas-f3 pelo owner)
data: 2026-07-25
contexto: meta issue #130 · F3-CHARTER (Sala viva conduzida) · F3-PLANO T13/T14/T15 · design workflow multiagente 2026-07-25 (6 leitores → 3 arquiteturas → síntese → crítica adversarial, veredito *needs-revision* / 7 must-fix, todos incorporados) · owner decisions OD-1..OD-4 (locked 2026-07-25)

## Decisão

**CRIAR duas skills de comportamento** que carregam o método fable-method de condução da sala viva:

- **`excrtx-conduct-loop` (EX-60)** — as 7 fases do loop (`classify → define_done → evidence → decide → act → verify → report`), a anti-narração (fase é sinal out-of-band em `conduct.jsonl`, nunca texto ao usuário) e o não-enfraquecimento da verificação.
- **`excrtx-conduct-bounds` (EX-61)** — os 3 bounds (3 falhas-conserto na mesma verificação · 2 buscas vazias · surpresa), a ordem de autoridade `executivo > spec > tests > código`, as 3 classes sancionadas de HITL e o protocolo de escrita do `conduct.jsonl`.

**Alternativa REJEITADA: embutir as regras no brief da tarefa lançada.** O brief é conteúdo de turno do usuário — some depois do turno 1. Ele não governa o *loop inteiro* de uma sessão viva multi-turno; só a persona (SOUL) persiste como identidade em todos os turnos.

## Evidência (trace SOUL — C-E)

A cadeia obrigatória que faz as regras alcançarem a sessão lançada:

```
skill compiled_rules → compile_soul.py → SOUL_SEED.md (entre marcadores COMPILED_RULES) → (setup.sh step-07 cp) → $HERMES_HOME/SOUL.md → run_agent.load_soul_md() → _build_system_prompt()
```

1. A persona da sessão lançada é `run_agent.load_soul_md()` lendo **`$HERMES_HOME/SOUL.md`** como slot de identidade #1 (`personality=None`; `config.yaml agent.personalities` é código morto para sessões lançadas).
2. `compile_soul.py` escreve o **`SOUL_SEED.md`** do repo (o `compiled_rules` de `excrtx-conduct-loop` compila para a seção `## Conduct Loop`; o de `excrtx-conduct-bounds` para `## Conduct Bounds`).
3. O runtime `$HERMES_HOME/SOUL.md` é uma **cópia verbatim** instalada por `setup.sh` **step-07** — que sobrescreve o compile in-place. Esse `cp` é o **2º hop obrigatório**: `compile_soul → SOUL_SEED.md` sozinho **não** alcança a sessão lançada. (destrutivo num install personalizado — ver `## Consequências`; a propagação viva usa o compile cirúrgico, não o cp).
4. Governança é **provável offline (sem chave LLM)** via `run_agent.load_soul_md()` + `agent._build_system_prompt()` (ambos montagem pura de arquivos). Os gates keyless desta fase são `skill_judge.py --skill excrtx-conduct-loop --d1-only` e `--skill excrtx-conduct-bounds --d1-only`, mais o grep de `## Conduct Loop`/`## Conduct Bounds` + a *cauda* (`NEVER narrate`) em `SOUL_SEED.md` (prova que o `compiled_rules` é um block scalar `|` e não foi truncado — C-S1).

## Caveats

- **Propagação é necessária mas não suficiente sem o step-07.** SOUL propagation é a condição, não a prova de escopo. O escopo "só sessões lançadas" (vetor→profile) fica para F5.
- **Forçar `profile=` no launch é no-op no smoke isolado** — o profile default já mapeia para `$HERMES_HOME`, que já carrega `$HERMES_HOME/SOUL.md`. Só seria load-bearing em prod multi-profile. Por isso **F3 não força profile**; o scoping para sessões-lançadas-apenas defere para F5.
- **Por que skill (persona) e não código, ao contrário do F2 Curador?** Os bounds-em-código do F2 governavam um *worker determinístico* — um contador basta. O loop vivo do F3 é o *próprio raciocínio do LLM* ao longo de muitos turnos; um contador não pode conduzi-lo, só uma regra de persona pode. A camada observadora do fork (`sala_reducer.py`) ainda espelha os contadores para *renderizar cards verificáveis*, mas ela **observa e traduz** — não conduz e não cunha primitiva bloqueante.

## Consequências

- Duas novas skills sob `skills/excrtx-conduct-*`, ambas registradas em `FEATURES.md` (EX-60, EX-61) e compiladas em `SOUL_SEED.md`.
- `SOUL_SEED.md` é **regenerado** por `compile_soul.py` — o bloco compilado nunca é editado à mão.
- A propagação das regras compiladas ao acervo vivo é **cirúrgica**:
`python3 scripts/compile_soul.py --soul "$HERMES_HOME/SOUL.md"` — `inject_into_soul` troca
**apenas** o bloco entre `<!-- COMPILED_RULES_START -->`/`END`, preservando a seção de
onboarding. **⚠ NÃO use `setup.sh` step-07 nem `cp SOUL_SEED.md $HERMES_HOME/SOUL.md`** num
install já personalizado: o `cp` sobrescreve o arquivo INTEIRO com o seed genérico, apagando
a identidade do onboarding (Identidade Raiz/Valores/Tom/Contexto de Negócio). O `cp`/step-07 só
é seguro num provisionamento novo ou num `$HERMES_HOME` isolado de smoke.
- `.dogfood/scenarios/EX-60.yaml` + `EX-61.yaml` (cenários de 10 campos) + `calibrate-hermes.sh` + `skill_judge` D2–D5 completo ficam para **F5**; F3 entrega as skills no D1 keyless + registro em `FEATURES.md`.
