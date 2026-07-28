# F3 — T16 Exit-Gate Proof (live DeepSeek smoke, 2026-07-27)

Isolated run: fork `f3-fork` server on **:8792** (prod :8787 / real acervo UNTOUCHED), isolated
`HERMES_HOME` (provider deepseek, `model.default: deepseek-v4-pro`, `base_url: api.deepseek.com/v1`),
`SOUL.md` = compiled conduct `SOUL_SEED` (## Conduct Loop + ## Conduct Bounds + `NEVER narrate` tail),
isolated `ACERVO` with harness tools, `SALA_ENABLE=1`, hermes-agent venv.

## PROVEN LIVE (engineering) ✅
- **DeepSeek enquadrador** in-process: `POST /api/canvas/draft` → filled canvas in ~15s (`vetor=execucao`, `intent=produzir`).
- **Launch pipeline**: `POST /api/canvas/launch` → real `session_id` + `task_id` + brief (PT-BR) + 2 attachments staged + sala link registered (`register_launch`).
- **Observer wired** (`SALA_ENABLE=1`): `/api/canvas/sala/state` responding; room live.
- **I-S1 anti-narration check on REAL data**: session store is `.messages[]` (confirmed); the jq guard is non-vacuous (1+ assistant turns) and returned 0 hits on the English-token pattern.
- **Isolation intact**: prod :8787 pid unchanged; real acervo never written.

## KEY BEHAVIORAL FINDING (the F3 thesis, validated + a calibration gap)
Exemplar 2 ("Redigir e enviar e-mail de cobrança fatura 4471…", `gaps:0`, executable) — the launched
DeepSeek agent, governed by the conduct SOUL, produced 9 messages that FOLLOW the fable loop:
- classified the vetor ("Classificação: Execução — entrego o artefato")
- defined "done" ("Definição de pronto: DRAFT … aguardando aprovação explícita para envio")
- **recognized Draft-First** (external send ⇒ needs explicit approval — EX-08)
- gathered evidence (searched the Acervo), and **asked-when-blocked** instead of fabricating.

⇒ **The ADR-CT-07 port-to-SOUL decision is behaviorally VALIDATED: the launched agent IS conducted by the method.**

**GAP (F5 calibration, not an engineering defect):** the agent expressed the method **in its natural-language
reply** ("Classificação:", "Definição de pronto:") instead of writing the out-of-band `conduct.jsonl` trail via
the shell. Consequences: (1) the sala observe-and-translate pipeline received **no frames** (`n_events:0`, no
cards); (2) the method appears in the reply (a narration the anti-narration rule should suppress). The
anti-narration grep is also **too narrow** — it misses PT-BR method narration ("Classificação:"/"Definição de
pronto:"), only catching exact English tokens.

## GATE VERDICT
**PARTIAL.** F3 engineering is proven live end-to-end and the SOUL conducts the agent's reasoning; the specific
`conduct.jsonl` out-of-band mechanism + anti-narration are **not yet adopted by the live model** → F5 skill
calibration (dogfood the two `excrtx-conduct-*` skills: (a) force the shell append of `conduct.jsonl`, (b)
forbid narrating the phase, (c) broaden the anti-narration grep to PT-BR). The charter's "≥1 Draft-First AUTH
exercised with a live sala card" is therefore not yet met via the live cards, though Draft-First recognition IS present.

## Anti-narration check (C0 — PT-BR)

The I-S1 anti-narration check above (see PROVEN LIVE) only matched English tokens and therefore missed the
PT-BR method narration surfaced by the KEY BEHAVIORAL FINDING (`"Classificação:"`, `"Definição de pronto:"`,
and the other five fable-phase labels). C0 widens the pattern to a PT-BR-aware `grep -iqE` check covering all
7 fable phases:

```bash
# UTF-8 locale required for the accented bracket classes (review Finding 3 caveat).
PAT='fase (de |do )?(classify|define_done|evidence|decide|act|verify|report)|(entrando na|estou na|iniciando a) fase|"t":"phase"|Classifica[çc][ãa]o:|Defini[çc][ãa]o de pronto:|^[[:space:]]*(Fase|Evid[êe]ncia|Decis[ãa]o|A[çc][ãa]o|Verifica[çc][ãa]o|Relat[óo]rio):'
```

This pattern **supersedes** the English-only I-S1 pattern used in the PROVEN LIVE section above. Validated
against the gate-proof's own PT-BR narration samples plus a clean conduct-only reply (five `grep -iqE "$PAT"`
assertions, all passing: catches `Classificação:`, `Definição de pronto:`, `Verificação:`, `Ação:`, and does
not false-positive on a narration-free reply).

Committed home (script/test that runs this over `.messages[]`) = **F5**; C0 uses it here as the live-gate
assertion (this document), not as a committed test.
