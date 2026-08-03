# F5 (Canvas de Tarefas) — Slice A: fatia F4-independente (design)

> Fase **C3 / F5 (Polish & GA)** do programa Canvas de Tarefas (meta issue elderbernardi/exocortex.saas#130,
> tracker F5 = #136). A F5 completa audita a **jornada inteira** (frase→sala→execução→**colheita→receita**) —
> logo depende da F4 mergeada+ao-vivo, o que é **owner-gated**. Esta **Slice A** recorta o que é
> **F4-independente** e entregável agora (F3+C0 já em `exocortex/stable`/`main`).
> Charter: `docs/plans/2026-07-23_canvas-tarefas/F5-CHARTER.md`. Plano task-by-task sai depois deste spec.

## 1. Contexto e problema

O mapa antigo da F5 (COMPLETION-prompt) listava como **prioridade #1** calibrar as skills de condução para
fechar o gate T16 — mas **isso já foi feito no C0** (gate T16 FECHADO ao vivo 2026-07-28: o agente lançado
escreve `conduct.jsonl` em vez de narrar). Logo o maior risco da F5 saiu da frente.

O que resta da F5 divide-se por dependência da F4:
- **F4-independente (esta Slice A):** (a) o **provisionamento não é totalmente idempotente** — o step-07 (SOUL
  runtime) **já foi consertado** pela installer-v2 (guard que preserva SOUL onboarded), mas o **step-04**
  (rsync principal do acervo, sem `--ignore-existing`) ainda pode sobrescrever a constituição do Macroverso do
  usuário, e o **step-05** (profiles `cp -r`) sobrescreve profiles; o **comando de GA da F5**
  (`EXOCORTEX_ENABLE_HERMES_WEBUI=1 bash setup.sh`) dispara esses → **resíduo do GA-blocker**; (b) os cenários
  dogfood `EX-60`/`EX-61` das skills
  de condução **ficaram pendentes** (deferidos no C0); (c) o grep anti-narração PT-BR do C0 é **prosa** em
  `docs/sala/F3-GATE-PROOF.md`, não um teste committado; (d) falta um **harness canônico** que torne o agente
  ciente do sistema Canvas e o **avalie** (o `calibrate-hermes.sh` nativo foi remodelado; owner quer um script
  canônico dedicado).
- **Bloqueado na F4 (Slice B, depois):** a11y/i18n das zonas de colheita/receita, auditoria interativa da
  jornada completa, re-pin `sources.lock`, `UPSTREAM-SYNC.md`, contrato `ativo`, **fechar #130**.

**Objetivo da Slice A:** fechar as pendências F4-independentes da F5 — provisionamento idempotente
(destrava o gate de GA), cenários dogfood das skills de condução, teste anti-narração committado, e um
**script canônico do Canvas** (primer + avaliação num comando).

## 2. Decisões do owner (vinculantes)

| # | Decisão | Consequência |
|---|---|---|
| OD-F5A-1 | **Slice A = fatia F4-independente agora** (D1 provisionamento idempotente · D2 dogfood EX-60/61 · D3 teste anti-narração · D4 script canônico). Slice B (a11y/i18n das zonas novas, auditoria, re-pin, fecha #130) espera a F4 landar. | Trabalho **exocortex-only**; nenhuma superfície de contrato tocada → **SOLO**. Branch off `origin/main`. |
| OD-F5A-2 | **Script canônico faz PRIMER + AVALIAÇÃO num comando.** (a) conscientizar: refresca/valida um primer do sistema Canvas + recompila/verifica o SOUL das skills EX-60/61; (b) avaliar: suite com veredito PASS/FAIL + evidência EX-49. | Dois tiers: **keyless** (default, CI-safe) + **`--live`** (owner-gated, LLM real isolado). |

**Defaults confirmados (owner "ok"):** nome do script = **`canvas-calibrate.{sh,py}`** (espelha
`calibrate-hermes.sh`); primer = **doc de repo `docs/canvas/AGENT-PRIMER.md`** (refrescado/validado pelo
script) + recompilação do SOUL como mecanismo de consciência em runtime.

## 3. Escopo

### Dentro da Slice A (tudo em `exocortex.saas`)
D1 provisionamento idempotente + issue · D2 `.dogfood/scenarios/EX-60.yaml`+`EX-61.yaml` · D3
`scripts/check_anti_narration.py` + teste · D4 `scripts/canvas-calibrate.{sh,py}` + `docs/canvas/AGENT-PRIMER.md`.

### Fora (Slice B — bloqueada na F4 mergeada+ao-vivo)
a11y/i18n das zonas colheita/receita · auditoria interativa da jornada completa · re-pin `sources.lock` ·
`UPSTREAM-SYNC.md` (inclui MOD-017) · contrato status `ativo` · **fechar #130**. A **seção colheita→receita
do primer** também é Slice B (cobre agora só o fluxo mergeado: frase→enquadrador→canvas→launch→conduct→sala).

### Não-objetivos
Nenhuma feature nova (polish only, guardrail F5); não tocar a F4 (`collab/canvas-f4` fica intocada); não
tocar o fork nem o contrato; não rodar o LLM real no tier keyless; **prod `:8787` + acervo real INTOCADOS**.

## 4. Detalhe por entregável

### D1 — Provisionamento idempotente (residual do GA-blocker)
> **Correção de premissa (confirmado no código atual, `origin/main@76142cd` "installer v2"):** o **step-07 JÁ É
> idempotente** — `setup/step-07-install-identity.sh:13` faz `if [ -f "$SOUL_TARGET" ] && grep -q "Você é o
> Exocórtex.IA" "$SOUL_TARGET"` → **preserva** (não `cp`; o `compile_soul.py` roda depois e atualiza só o bloco
> compilado). A nota C0 "step-07 apaga o onboarding em qualquer re-setup" está **stale** (a consolidação v2 já
> consertou). D1 recorta o **resíduo real**: step-04 e step-05.
- **Abrir issue** em `exocortex.saas` (a que o C0 marcou "to open"), **revisada**: registrar que step-07 já é
  idempotente (v2) e que o resíduo é step-04 (rsync do acervo sem `--ignore-existing`) + step-05 (profiles
  overwrite); referenciar C0-change-record + este spec.
- **step-04 (`setup/step-04-install-acervo.sh`):** o rsync principal do acervo (`copy_acervo_seed`, ~linha 15)
  usa `rsync -a "$ACERVO_SRC/" "$ACERVO/"` **sem `--ignore-existing`** → pode sobrescrever conteúdo do usuário,
  inclusive a **constituição do Macroverso `$ACERVO/macro/SOUL.md`** (preenchida pelo onboarding) e conhecimento
  seeded editado. Os seeds editorial/ops logo abaixo (~linhas 34/67) **já** usam `--ignore-existing` — o rsync
  principal é o outlier. **Fix:** adicionar `--ignore-existing` ao rsync principal (casa com o padrão existente;
  arquivos-seed novos ainda são adicionados, existentes ficam intocados).
- **step-05 (`setup/step-05-install-profiles.sh`):** `cp -r "$PROFILES_SRC"/* "$PROFILES_DST/"` (e bundles)
  sobrescreve sem guarda. **Fix:** no-clobber (`cp -rn`) para preservar profiles/bundles customizados no
  re-provisionamento (arquivos novos ainda copiados).
- **step-07:** sem mudança de código — **verificação owner-gated**: confirmar que o marcador `"Você é o
  Exocórtex.IA"` de fato aparece num `~/.hermes/SOUL.md` onboarded real (leitura owner-gated), de modo que o
  guard preserva. Se o marcador não bater num SOUL vivo → vira achado (fix separado); caso contrário, nada a
  fazer no step-07.
- **Verificação (keyless):** `$HERMES_HOME`/`$ACERVO` temp isolados populados (macro/SOUL.md com conteúdo de
  usuário + profile customizado + arquivos-seed com edições) → re-rodar step-04 + step-05 isolados → asserção:
  conteúdo do usuário **preservado** (diff vazio nos arquivos existentes; arquivos-seed novos adicionados). Sem
  tocar `$HERMES_HOME`/acervo reais.

### D2 — Cenários dogfood EX-60 / EX-61
- `.dogfood/scenarios/EX-60.yaml` (`excrtx-conduct-loop`) + `EX-61.yaml` (`excrtx-conduct-bounds`) no schema
  existente (`feature_id/title/category/source/risk/mode/user_prompt/allowed_tools/disallowed_tools/
  success_criteria/failure_signals/evidence_required`).
- **success_criteria** codificam o gate C0: o agente conduzido **faz append em `conduct.jsonl` por fase (shell)
  e NÃO narra o método** (sem "Classificação:"/"Definição de pronto:"…); respeita Draft-First (EX-08);
  bounds (3 verify falhos → devolve, 2 buscas vazias → para). **failure_signals:** narrar a fase; PASS sem
  linhas de conduct; fabricar em vez de perguntar.
- **Validação (keyless):** `bash scripts/test-registry.sh dogfood-catalog` (via `dogfood_validate_catalog.py`)
  aceita os 2 novos cenários; execução real (`dogfood_features.py run EX-60/61`) fica no tier `--live`.

### D3 — Teste anti-narração committado
- `scripts/check_anti_narration.py`: recebe um transcript de sessão (`.messages[]` JSON) → escaneia as
  respostas do agente pelos **7 rótulos de fase fable em PT-BR + EN** (Classificação/Definição de pronto/
  Evidência/Decisão/Ação/Verificação/Relatório e os tokens EN) via `grep -iqE` UTF-8-aware → **exit ≠ 0 se
  narrou**. (Promove a asserção que hoje é prosa no `F3-GATE-PROOF.md`.)
- **Teste** `tests/test_check_anti_narration.py` (pytest keyless) com fixtures: transcript **narrado** → falha;
  transcript **limpo** (só o trabalho, conduct fora de banda) → passa; cobre acentuação (locale UTF-8).

### D4 — Script canônico `canvas-calibrate` (primer + avaliação)
- `scripts/canvas-calibrate.sh` (wrapper) → `scripts/canvas-calibrate.py` (runner modular, padrão do
  `calibrate-hermes`).
- **Conscientizar (primer):**
  - **`docs/canvas/AGENT-PRIMER.md`** — primer canônico do sistema Canvas: o método (vetores, done_criteria/
    verification, shape), o loop de condução (append `conduct.jsonl` por fase, anti-narração, bounds), os
    eventos `sala_*`, e o **contrato de consciência** (o que o agente lançado deve fazer numa sala). *Seção
    colheita→receita = placeholder "F4/Slice B".* O script **valida** (existe, seções presentes) e pode
    **refrescar** partes derivadas (ex.: lista de eventos das skills).
  - **SOUL:** recompila via `compile_soul.py` e **verifica** que os blocos `## Conduct Loop`/`## Conduct Bounds`
    estão presentes + corpo-sincronizados (`--validate-compiled-rules` não lista conduct-loop/bounds) + guard
    C-S1 (cauda "NEVER narrate" sobrevive).
- **Avaliar (keyless, default):** (1) SOUL carrega os 2 blocos conduct (C-S1 OK); (2) `skill_judge.py --d1-only`
  = COMPLIANT p/ EX-60/EX-61; (3) `dogfood-catalog` valida EX-60/61; (4) `check_anti_narration.py` verde numa
  fixture; (5) primer presente/válido. Veredito **PASS/FAIL** + evidência bruta EX-49.
- **Avaliar `--live` (owner-gated):** smoke DeepSeek **isolado** (`$HERMES_HOME`/`ACERVO` temp, `model.provider/
  default/base_url/api_mode` sobrescritos, `context_file_max_chars` pinado; **prod :8787 + acervo real
  INTOCADOS**): (a) **enquadrador** classifica vetor correto nas **3 frases canônicas** (execução/produzir,
  evolução/explorar, manutenção/revisar) + **não fabrica gaps**; (b) **condução** — sessão lançada escreve
  `conduct.jsonl` (`n_events>0`) + **≥1 Draft-First AUTH** + `check_anti_narration` VAZIO na resposta real.
- Emite verdict + evidência; `--live` requer chave (de `databrain/.env`, mascarada nos logs).

## 5. Gate de saída (Slice A)
1. step-04 + step-05 re-rodados num `$ACERVO`/`$HERMES_HOME` isolado populado **preservam** o conteúdo do
   usuário (macro/SOUL.md + profiles customizados + arquivos-seed editados) — diff vazio nos existentes,
   novos adicionados (prova bruta EX-49, keyless). step-07 verificado owner-gated (marcador bate no SOUL vivo).
2. `dogfood-catalog` aceita EX-60/EX-61; `check_anti_narration.py` + seu teste verdes (keyless).
3. `canvas-calibrate` (keyless) = **PASS** com evidência; primer presente e válido; SOUL conduct-blocks OK.
4. (owner-gated) `canvas-calibrate --live` = PASS num smoke isolado (enquadrador 3/3 + condução escreve
   conduct + Draft-First AUTH) — a rodar pelo owner, prod intocada.

## 6. Guardrails e governança
- **SOLO exocortex:** só arquivos de `exocortex.saas` (`setup.sh`, `scripts/`, `.dogfood/scenarios/`,
  `docs/canvas/`, `tests/`). **Nenhuma skill nova** (EX-60/61 já existem do F3/C0; D2 só adiciona os cenários
  dogfood delas). **Nenhuma superfície de contrato** → sem mudança no umbrella/fork. Se algo exigir tocar o
  contrato → **parar e reportar** (vira COLLAB, provável Slice B).
- **Checkout compartilhado:** worktree isolada, branch `f5/canvas-slice-a` cortada de **`origin/main`**;
  verificar branch no comando do commit; **nunca `git add -A`**; push/merge **owner-gated** (worktree-detached
  nos tips de origin). Ver [[checkouts-compartilhados-sessoes-paralelas]].
- **Keyless-first:** todo o tier default roda sem chave (pytest, `skill_judge --d1-only`, `compile_soul`,
  `dogfood-catalog`). LLM real só em `--live` (owner). **SOUL propagação pro prod real = owner-gated**
  (`compile_soul.py --soul ~/.hermes/SOUL.md`), fora da Slice A.
- **Não perturbar F4:** `collab/canvas-f4` e as worktrees da F4 ficam intocadas; Slice A não depende nem toca
  o código da F4.

## 7. Riscos / gaps
1. **Guard do step-07 (já existente)** — usa `grep -q "Você é o Exocórtex.IA"`. Risco residual: se um SOUL
   onboarded real NÃO contiver essa string exata, o guard falha → cai no `cp` (com backup) e o onboarding
   pós-instalação precisaria ser refeito. Mitigação: **verificação owner-gated** do `~/.hermes/SOUL.md` real
   nesta slice; se não bater, abrir achado (fora do escopo de código da Slice A, que não altera step-07).
2. **`--live` é caro/frágil** (LLM + isolamento) — por isso é owner-gated e o gate de merge da Slice A é o tier
   **keyless**; `--live` é confirmação do owner.
3. **Primer x SOUL overlap** — o primer não substitui o SOUL (que é o mecanismo real de consciência em
   runtime); é doc canônico + seed. Evitar duplicar o texto das compiled_rules (referenciar).

## 8. Sequência do programa
C1(done)→C2/F4(code-complete, owner-gated merge+live)→**C3/F5**: **Slice A (esta, F4-independente, agora)** →
**Slice B (após F4 landar: a11y/i18n zonas novas + auditoria jornada completa + re-pin + UPSTREAM-SYNC +
contrato ativo + fecha #130)**. Índice: `docs/plans/2026-07-23_canvas-tarefas/00-INDEX.md`; charter
`F5-CHARTER.md`; tracker #136.
