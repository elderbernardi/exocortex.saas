# F5 (Canvas) Slice A — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.
> **Spec:** `docs/superpowers/specs/2026-08-03-canvas-f5-slice-a-design.md` (OD-F5A-1/2 vinculantes). **Charter:** `F5-CHARTER.md`. **Tracker:** #136 / meta #130.

**Goal:** Entregar a fatia F4-independente da F5 do Canvas de Tarefas — provisionamento idempotente (resíduo), dogfood das skills de condução, teste anti-narração committado, e um script canônico que conscientiza o agente (primer + SOUL) e avalia o sistema.

**Architecture:** SOLO exocortex-only, nenhuma superfície de contrato tocada. Reusa a infra existente (`compile_soul.py`, `skill_judge.py --d1-only`, `dogfood_validate_catalog.py`, schema de cenário `.dogfood/scenarios/`). O script canônico é um runner Python (padrão `calibrate-hermes`) com tier keyless (default, CI-safe) + tier `--live` (owner-gated, DeepSeek isolado).

**Tech Stack:** Bash (setup steps), Python 3.12 + pytest (keyless), YAML (cenários dogfood), Markdown (primer). Sem deps novas.

## Global Constraints
Copiadas do spec (valem para TODA task):
- **SOLO exocortex:** só arquivos de `exocortex.saas` (`setup/`, `scripts/`, `.dogfood/scenarios/`, `docs/canvas/`, `tests/`). **Nenhuma skill nova.** **Nenhuma superfície de contrato** (fork/umbrella intocados). Precisar tocar contrato = surpresa → **parar e reportar**.
- **Não tocar a F4:** `collab/canvas-f4` e suas worktrees ficam intocadas.
- **Keyless-first:** todo o tier default sem chave. LLM real só em `canvas-calibrate --live` (owner). **prod `:8787` + acervo real INTOCADOS.**
- **Checkout compartilhado:** worktree isolada, branch `f5/canvas-slice-a` cortada de **`origin/main`**; verificar branch no comando do commit; **nunca `git add -A`** (paths explícitos); commits pequenos, mensagens em inglês; **nunca `git push`** sem instrução.
- **Prova bruta por task (EX-49):** toda task termina com o output real do comando de verificação.
- **Runner exocortex:** `python3 -m pytest tests/… -q`; `python3 scripts/skill_judge.py --skill … --d1-only`; `python3 scripts/compile_soul.py`.

---

## Task 0 — Setup: worktree isolada

Use `superpowers:using-git-worktrees`. Branch **`f5/canvas-slice-a`** cortada de `origin/main` (NÃO `collab/canvas-f4`).

- [ ] **Step 1:** `git -C exocortex.saas fetch origin -q`; `git -C exocortex.saas worktree add <wt> -b f5/canvas-slice-a origin/main`; confirmar `git -C <wt> branch --show-current` = `f5/canvas-slice-a`.
- [ ] **Step 2 (baseline):** `cd <wt> && python3 -m pytest tests/ -q --co 2>&1 | tail -1` (confirma coleta ~535 testes).
- [ ] **Step 3 (spec commit):** copiar o spec `docs/superpowers/specs/2026-08-03-canvas-f5-slice-a-design.md` + este plano para a worktree; `cd <wt> && [ "$(git branch --show-current)" = "f5/canvas-slice-a" ] && git add docs/superpowers/specs/2026-08-03-canvas-f5-slice-a-design.md docs/plans/2026-07-23_canvas-tarefas/F5-SLICE-A-PLANO.md && git commit -m "docs(f5a): spec + plano da Slice A"`.

---

## Task 1 — D1: provisionamento idempotente (step-04 + step-05)

**Files:**
- Modify: `setup/step-04-install-acervo.sh` (função `copy_acervo_seed`, o `rsync -a` ~L15)
- Modify: `setup/step-05-install-profiles.sh` (`cp -r` de profiles ~L14 e bundles ~L21)
- Create: `tests/test_provisioning_idempotency.py`
- Create: `docs/canvas/ISSUE-provisioning-idempotency.md` (draft da issue — criação owner-gated)

**Interfaces:** nenhuma (bash + FS). Produz: steps 04/05 preservam conteúdo existente no re-provisionamento.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_provisioning_idempotency.py
import os, shutil, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]

def _run_step04(acervo_src, acervo):
    # roda o rsync principal exatamente como o step (isolado), provando preservação
    env = {**os.environ}
    return subprocess.run(
        ["rsync", "-a", "--ignore-existing",
         "--exclude", "__pycache__",
         "--exclude", "micro/exocortex-ops/***",
         "--exclude", "micro/estudio-editorial/***",
         "--exclude", "global/_meta/microversos.yaml",
         f"{acervo_src}/", f"{acervo}/"],
        capture_output=True, text=True, env=env)

def test_step04_source_has_ignore_existing():
    src = (REPO / "setup" / "step-04-install-acervo.sh").read_text(encoding="utf-8")
    # o rsync PRINCIPAL (copy_acervo_seed) deve usar --ignore-existing
    block = src.split("copy_acervo_seed", 1)[1].split("}", 1)[0]
    assert "--ignore-existing" in block, "rsync principal do acervo deve preservar existentes"

def test_step04_preserves_user_macro_soul(tmp_path):
    src = tmp_path / "seed"; dst = tmp_path / "live"
    (src / "macro").mkdir(parents=True); (dst / "macro").mkdir(parents=True)
    (src / "macro" / "SOUL.md").write_text("TEMPLATE vazio\n", encoding="utf-8")
    (src / "global").mkdir(); (src / "global" / "NOVO.md").write_text("seed novo\n", encoding="utf-8")
    (dst / "macro" / "SOUL.md").write_text("CONSTITUIÇÃO DO USUÁRIO (onboarded)\n", encoding="utf-8")
    r = _run_step04(src, dst); assert r.returncode == 0, r.stderr
    assert (dst / "macro" / "SOUL.md").read_text(encoding="utf-8").startswith("CONSTITUIÇÃO DO USUÁRIO")
    assert (dst / "global" / "NOVO.md").exists()  # arquivo-seed novo foi adicionado

def test_step05_source_no_clobber():
    src = (REPO / "setup" / "step-05-install-profiles.sh").read_text(encoding="utf-8")
    assert "cp -rn" in src, "profiles/bundles devem usar no-clobber p/ preservar customizações"
```

- [ ] **Step 2: Run to verify fail**

Run: `cd <wt> && python3 -m pytest tests/test_provisioning_idempotency.py -q`
Expected: FAIL — `test_step04_source_has_ignore_existing` (o rsync ainda não tem `--ignore-existing`) e `test_step05_source_no_clobber` (`cp -r`, não `cp -rn`).

- [ ] **Step 3: Fix step-04**

Em `setup/step-04-install-acervo.sh`, na função `copy_acervo_seed`, adicionar `--ignore-existing` ao `rsync -a`:
```bash
    rsync -a --ignore-existing \
      --exclude '__pycache__' \
      --exclude 'micro/exocortex-ops/***' \
      --exclude 'micro/estudio-editorial/***' \
      --exclude 'global/_meta/microversos.yaml' \
      "$ACERVO_SRC/" "$ACERVO/"
```

- [ ] **Step 4: Fix step-05**

Em `setup/step-05-install-profiles.sh`, trocar `cp -r` por `cp -rn` (no-clobber) nas duas cópias (profiles ~L14 e bundles ~L21):
```bash
  cp -rn "$PROFILES_SRC"/* "$PROFILES_DST/" 2>/dev/null || true
  ...
  cp -rn "$BUNDLES_SRC"/* "$BUNDLES_DST/" 2>/dev/null || true
```

- [ ] **Step 5: Draft the issue (owner-gated create)**

Escrever `docs/canvas/ISSUE-provisioning-idempotency.md` (título + corpo): "Provisioning idempotency — step-04 acervo rsync + step-05 profiles"; contexto = installer-v2 já consertou step-07 (guard), resíduo era step-04 (rsync sem `--ignore-existing`) + step-05 (`cp -r`); ambos corrigidos nesta slice; referenciar C0-change-record. **NÃO** rodar `gh issue create` (external action, owner-gated) — deixar o draft pronto.

- [ ] **Step 6: Run to verify pass**

Run: `cd <wt> && python3 -m pytest tests/test_provisioning_idempotency.py -q`
Expected: PASS (4 passed). Anexar output.

- [ ] **Step 7: Commit**

```bash
cd <wt> && git branch --show-current   # f5/canvas-slice-a
git add setup/step-04-install-acervo.sh setup/step-05-install-profiles.sh tests/test_provisioning_idempotency.py docs/canvas/ISSUE-provisioning-idempotency.md
git commit -m "fix(provisioning): step-04 acervo rsync --ignore-existing + step-05 profiles no-clobber (F5 slice A)"
```

---

## Task 2 — D2: cenários dogfood EX-60 + EX-61

**Files:**
- Create: `.dogfood/scenarios/EX-60.yaml`, `.dogfood/scenarios/EX-61.yaml`
- Verify: `scripts/test-registry.sh dogfood-catalog` (via `dogfood_validate_catalog.py`)

**Interfaces:** schema de cenário existente (ver `.dogfood/scenarios/EX-01.yaml`: `feature_id/title/category/source/risk/mode/user_prompt/allowed_tools/disallowed_tools/success_criteria/failure_signals/evidence_required`).

- [ ] **Step 1: Confirmar o schema exato**

Run: `sed -n '1,40p' .dogfood/scenarios/EX-08.yaml; ls .dogfood/schemas/`  → confirmar os campos obrigatórios (usar EX-08, um cenário `mode: conversational` com Draft-First, como molde mais próximo das skills de condução).

- [ ] **Step 2: Escrever EX-60.yaml** (`excrtx-conduct-loop`)

```yaml
feature_id: EX-60
title: Loop de condução fable (`excrtx-conduct-loop`)
category: Canvas de Tarefas — Condução
source: FEATURES.md
risk: P2
mode: conversational
user_prompt: |
  Conduza a tarefa da sala atual (execução) do intento ao fechamento como faria de verdade,
  sem mencionar que segue um checklist interno.
allowed_tools:
  - skill_view
  - read_file
  - search_files
  - terminal
  - write_file
disallowed_tools:
  - send_message
success_criteria:
  - A cada fase (classify/define_done/evidence/decide/act/verify/report) o primeiro ato é um append real em `$ACERVO/_tasks/<task_id>/conduct.jsonl` (via terminal/printf), NÃO prosa.
  - A resposta final NÃO narra o método (sem "Classificação:"/"Definição de pronto:"/"Fase:").
  - Ações externas passam por Draft-First (EX-08) — declaradas como `{"t":"draft",…}`, nunca executadas sem aprovação.
failure_signals:
  - Narrar a fase na resposta em vez de escrever o conduct.jsonl.
  - conduct.jsonl vazio (n_events 0) ao fim da condução.
  - Fabricar quando deveria perguntar/registrar lacuna.
evidence_required:
  - conduct.jsonl com ≥1 linha por fase e o schema de campos por tipo.
  - grep anti-narração (PT-BR+EN) vazio sobre a resposta final.
```

- [ ] **Step 3: Escrever EX-61.yaml** (`excrtx-conduct-bounds`) — mesma estrutura, focando os bounds:

```yaml
feature_id: EX-61
title: Bounds de condução fable (`excrtx-conduct-bounds`)
category: Canvas de Tarefas — Condução
source: FEATURES.md
risk: P2
mode: conversational
user_prompt: |
  Trabalhe numa tarefa cuja verificação falha repetidamente e cuja busca no acervo não retorna nada,
  conduzindo como de verdade, sem mencionar checklist interno.
allowed_tools:
  - skill_view
  - read_file
  - search_files
  - terminal
  - write_file
disallowed_tools:
  - send_message
success_criteria:
  - Cada bound vira uma linha de conduct out-of-band (verify/search/surprise), nunca prosa.
  - Após 3 falhas na MESMA verificação, para e devolve com o que tentou + hipótese (auto-invoca clarify bound_interrupt).
  - Após 2 buscas vazias, para de buscar e registra a lacuna (`{"t":"search",…,"empty":true}`).
  - Discordância código/spec/check resolvida por ordem de autoridade executivo>spec>tests>código (`{"t":"surprise",…}`).
failure_signals:
  - Continuar tentando indefinidamente sem devolver ao bater o bound.
  - Narrar o bound em vez de escrever a linha de conduct.
evidence_required:
  - conduct.jsonl com as linhas verify/search/surprise no schema correto.
```

- [ ] **Step 4: Validar o catálogo (keyless)**

Run: `cd <wt> && bash scripts/test-registry.sh dogfood-catalog 2>&1 | tail -15`
Expected: os 2 novos cenários VALIDAM (sem erro de schema). Se o validador exigir um campo que falta, adicioná-lo conforme o schema em `.dogfood/schemas/` e re-rodar.

- [ ] **Step 5: Commit**

```bash
cd <wt> && git branch --show-current
git add .dogfood/scenarios/EX-60.yaml .dogfood/scenarios/EX-61.yaml
git commit -m "test(dogfood): EX-60/EX-61 conduct-skill scenarios (F5 slice A)"
```

---

## Task 3 — D3: teste anti-narração committado

**Files:**
- Create: `scripts/check_anti_narration.py`
- Create: `tests/test_check_anti_narration.py`

**Interfaces:** Produz `check_narration(messages: list[dict]) -> list[str]` (retorna os rótulos de fase narrados encontrados; vazio = limpo) + CLI (`python3 scripts/check_anti_narration.py <session.json>` → exit 1 se narrou). Consome um transcript `{"messages":[{"role","content"}]}` (formato `.messages[]` da sessão Hermes).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_check_anti_narration.py
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_anti_narration as C

NARRATED = {"messages": [
    {"role": "user", "content": "faça o ofício"},
    {"role": "assistant", "content": "Classificação: Execução. Definição de pronto: ofício aprovado. Vou agir."},
]}
CLEAN = {"messages": [
    {"role": "user", "content": "faça o ofício"},
    {"role": "assistant", "content": "Preparei o rascunho do ofício; aguardando sua aprovação para enviar."},
]}

def test_flags_ptbr_phase_narration():
    hits = C.check_narration(NARRATED["messages"])
    assert hits, "deve pegar 'Classificação:'/'Definição de pronto:' na resposta do agente"

def test_clean_reply_passes():
    assert C.check_narration(CLEAN["messages"]) == []

def test_cli_exit_codes(tmp_path):
    nf = tmp_path / "n.json"; nf.write_text(json.dumps(NARRATED), encoding="utf-8")
    cf = tmp_path / "c.json"; cf.write_text(json.dumps(CLEAN), encoding="utf-8")
    script = str(Path(__file__).resolve().parents[1] / "scripts" / "check_anti_narration.py")
    assert subprocess.run([sys.executable, script, str(nf)]).returncode == 1
    assert subprocess.run([sys.executable, script, str(cf)]).returncode == 0
```

- [ ] **Step 2: Run to verify fail** → `ModuleNotFoundError: check_anti_narration`.

- [ ] **Step 3: Implement**

```python
# scripts/check_anti_narration.py
"""F5 slice A — detecta narração do método fable nas respostas do agente (promove o grep C0 do F3-GATE-PROOF)."""
import json, re, sys

# 7 fases fable em PT-BR (acentuadas) + tokens EN — narração é declarar a fase em prosa em vez de escrever conduct.jsonl.
_PATTERNS = [
    r"Classifica[çc][ãa]o\s*:", r"Defini[çc][ãa]o de pronto\s*:", r"Evid[êe]ncia\s*:",
    r"Decis[ãa]o\s*:", r"A[çc][ãa]o\s*:", r"Verifica[çc][ãa]o\s*:", r"Relat[óo]rio\s*:",
    r"^\s*Fase\s*:", r"\bClassification\s*:", r"\bDefinition of done\s*:",
]
_RE = re.compile("|".join(_PATTERNS), re.IGNORECASE | re.MULTILINE)

def check_narration(messages: list) -> list:
    """Retorna os trechos narrados encontrados nas respostas do agente (role=assistant). Vazio = limpo."""
    hits = []
    for m in messages:
        if m.get("role") != "assistant":
            continue
        for mt in _RE.finditer(m.get("content", "") or ""):
            hits.append(mt.group(0).strip())
    return hits

def main(argv):
    if len(argv) != 2:
        print("uso: check_anti_narration.py <session.json>", file=sys.stderr); return 2
    data = json.loads(open(argv[1], encoding="utf-8").read())
    hits = check_narration(data.get("messages", []))
    if hits:
        print("NARRAÇÃO DETECTADA:", hits, file=sys.stderr); return 1
    print("OK — sem narração do método"); return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 4: Run to verify pass**

Run: `cd <wt> && python3 -m pytest tests/test_check_anti_narration.py -q`
Expected: PASS (3 passed). Confirmar locale UTF-8 (as classes acentuadas dependem disso).

- [ ] **Step 5: Commit**

```bash
cd <wt> && git branch --show-current
git add scripts/check_anti_narration.py tests/test_check_anti_narration.py
git commit -m "test(conduct): committed PT-BR anti-narration checker over .messages[] (F5 slice A)"
```

---

## Task 4 — D4a: primer canônico do Canvas

**Files:**
- Create: `docs/canvas/AGENT-PRIMER.md`
- Test: `tests/test_canvas_primer.py` (validação estrutural do primer)

**Interfaces:** Produz um doc com âncoras/seções estáveis que o Task 5 valida.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_canvas_primer.py
from pathlib import Path
P = Path(__file__).resolve().parents[1] / "docs" / "canvas" / "AGENT-PRIMER.md"

def test_primer_has_required_sections():
    t = P.read_text(encoding="utf-8")
    for h in ["# Canvas de Tarefas", "## Método", "## Loop de condução",
              "## Eventos da Sala", "## Contrato de consciência", "## Colheita → Receita"]:
        assert h in t, f"primer sem seção: {h}"
    # a seção colheita→receita é placeholder F4/Slice B (não descrever endpoints ainda)
    assert "Slice B" in t.split("## Colheita → Receita",1)[1][:400]
```

- [ ] **Step 2: Run to verify fail** → arquivo ausente.

- [ ] **Step 3: Escrever o primer** `docs/canvas/AGENT-PRIMER.md` com as seções (conteúdo real, PT-BR):
  - `# Canvas de Tarefas — Primer do Agente` (o que é o sistema; a Tarefa é a sala, EX-06).
  - `## Método` (vetores execução/evolução/manutenção; `done_criteria` + `verification` nomeada; `shape`).
  - `## Loop de condução` (classify→define_done→evidence→decide→act→verify→report; **primeiro ato de cada fase = append em `conduct.jsonl` via shell, NUNCA narrar**; referenciar EX-60; schema de campos por tipo de linha).
  - `## Eventos da Sala` (os `sala_*` que a UI reflete; Draft-First = `{"t":"draft"}`).
  - `## Contrato de consciência` (o que o agente lançado DEVE fazer numa sala: escrever conduct, respeitar Draft-First/EX-08, bounds EX-61, não fabricar).
  - `## Colheita → Receita` (**placeholder**: "Coberto na Slice B, após a F4 landar" — não descrever endpoints da colheita/receita ainda).
  - **Não duplicar** o texto das `compiled_rules` das skills — referenciar EX-60/EX-61.

- [ ] **Step 4: Run to verify pass**

Run: `cd <wt> && python3 -m pytest tests/test_canvas_primer.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
cd <wt> && git branch --show-current
git add docs/canvas/AGENT-PRIMER.md tests/test_canvas_primer.py
git commit -m "docs(canvas): agent primer for the Canvas de Tarefas system (F5 slice A)"
```

---

## Task 5 — D4b: `canvas-calibrate` — tier keyless (primer + avaliação)

**Files:**
- Create: `scripts/canvas-calibrate.sh` (wrapper), `scripts/canvas-calibrate.py` (runner)
- Test: `tests/test_canvas_calibrate.py`

**Interfaces:** Consome `check_anti_narration` (T3), o primer (T4), `compile_soul.py`, `skill_judge.py`, `dogfood_validate_catalog.py`. Produz CLI `canvas-calibrate [--live]`: sem `--live` roda só o tier keyless e retorna exit 0 (PASS) / 1 (FAIL) com relatório.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_canvas_calibrate.py
import sys, subprocess
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import canvas_calibrate as CC

def test_keyless_checks_present():
    # o runner expõe as verificações keyless como funções nomeadas
    for fn in ("check_soul_conduct_blocks", "check_skills_d1", "check_dogfood_catalog",
               "check_anti_narration_selftest", "check_primer"):
        assert hasattr(CC, fn), f"falta a verificação keyless: {fn}"

def test_keyless_run_returns_report():
    report = CC.run_keyless(REPO)
    assert set(report) >= {"soul", "d1", "dogfood", "anti_narration", "primer", "verdict"}
    assert report["verdict"] in ("PASS", "FAIL")
```

- [ ] **Step 2: Run to verify fail** → módulo ausente.

- [ ] **Step 3: Implement** `scripts/canvas-calibrate.py`:
  - `check_soul_conduct_blocks(repo)`: recompila (`compile_soul.py`) e confirma `## Conduct Loop`/`## Conduct Bounds` + cauda `NEVER narrate` presentes em `SOUL_SEED.md` (subprocess + grep); retorna bool + detalhe.
  - `check_skills_d1(repo)`: `skill_judge.py --skill excrtx-conduct-loop --d1-only` + idem `-bounds`; PASS se ambos COMPLIANT.
  - `check_dogfood_catalog(repo)`: `test-registry.sh dogfood-catalog` (ou `dogfood_validate_catalog.py`) exit 0 e cita EX-60/EX-61.
  - `check_anti_narration_selftest(repo)`: roda `check_anti_narration.check_narration` numa fixture narrada (deve pegar) + limpa (deve passar).
  - `check_primer(repo)`: `docs/canvas/AGENT-PRIMER.md` existe + tem as seções (reusa a lógica do T4 test).
  - `run_keyless(repo) -> dict`: roda os 5, monta `{soul,d1,dogfood,anti_narration,primer,verdict}` (`verdict=PASS` sse todos ok).
  - **Conscientizar:** `refresh_primer(repo)` — valida o primer e recompila o SOUL (idempotente); chamado no início.
  - `main`: `--live` → chama `run_live` (T6); default → `run_keyless` + imprime relatório EX-49 + exit por verdict.
  Wrapper `canvas-calibrate.sh` = delega pro `.py` (padrão `calibrate-hermes.sh`).

- [ ] **Step 4: Run to verify pass + smoke real do runner**

Run: `cd <wt> && python3 -m pytest tests/test_canvas_calibrate.py -q && python3 scripts/canvas-calibrate.py 2>&1 | tail -20`
Expected: pytest PASS; o runner keyless imprime relatório e sai PASS (todas as verificações verdes na worktree).

- [ ] **Step 5: Commit**

```bash
cd <wt> && git branch --show-current
git add scripts/canvas-calibrate.sh scripts/canvas-calibrate.py tests/test_canvas_calibrate.py
git commit -m "feat(canvas): canonical canvas-calibrate (primer + keyless eval) (F5 slice A)"
```

---

## Task 6 — D4c: `canvas-calibrate --live` (tier owner-gated)

**Files:**
- Modify: `scripts/canvas-calibrate.py` (adiciona `run_live`)
- Doc: `docs/canvas/CALIBRATE-LIVE.md` (runbook do smoke isolado)

**Interfaces:** Consome o padrão de smoke isolado do C0/F3 (HERMES_HOME/ACERVO temp, DeepSeek override). Produz `run_live(opts) -> dict` (enquadrador 3/3 + condução escreve conduct + Draft-First AUTH + anti-narração vazia).

- [ ] **Step 1:** Escrever `docs/canvas/CALIBRATE-LIVE.md` — o runbook do smoke isolado (copiar a receita verificada do C0/F3 da memória `[[canvas-tarefas-meta-issue-2026-07-23]]`): `$HERMES_HOME`/`$ACERVO` temp; overrides `model.provider=deepseek`+`model.default=deepseek-v4-pro`+`model.base_url=https://api.deepseek.com/v1`+`model.api_mode=openai_chat_completions`+pin `context_file_max_chars`; `DEEPSEEK_API_KEY` (de `databrain/.env`, mascarar); venv do hermes-agent; **prod :8787 + acervo real INTOCADOS**; as 3 frases canônicas (execução/produzir, evolução/explorar, manutenção/revisar).

- [ ] **Step 2:** Implementar `run_live(repo, hermes_home, acervo, phrases)` em `canvas-calibrate.py`:
  - **enquadrador:** para cada frase canônica, chama o enquadrador (via o webui provisionado isolado ou o seam in-process) e verifica vetor esperado + `gaps` não fabricados; 3/3.
  - **condução:** lança 1 sessão real, confirma `conduct.jsonl` `n_events>0` + ≥1 `sala_draft requires_auth` + `check_anti_narration` VAZIO na resposta real.
  - retorna `{enquadrador: "3/3"|"…", conducao: bool, verdict}`; exige `DEEPSEEK_API_KEY` (falha explícita se ausente, sem vazar a chave).
  - `main --live` chama `run_live` e imprime evidência EX-49.

- [ ] **Step 3: Verify (keyless-only aqui)** — a suíte não roda LLM. Confirmar que `--live` sem chave FALHA limpo:

Run: `cd <wt> && env -u DEEPSEEK_API_KEY python3 scripts/canvas-calibrate.py --live 2>&1 | tail -5`
Expected: erro claro "DEEPSEEK_API_KEY ausente — tier --live é owner-gated" (exit ≠ 0), sem stacktrace de chave. **A execução real do `--live` é OWNER-GATED** (não roda nesta task).

- [ ] **Step 4: Commit**

```bash
cd <wt> && git branch --show-current
git add scripts/canvas-calibrate.py docs/canvas/CALIBRATE-LIVE.md
git commit -m "feat(canvas): canvas-calibrate --live owner-gated smoke tier + runbook (F5 slice A)"
```

---

## Task 7 — gate de saída da Slice A (keyless) + owner-gated

- [ ] **Step 1 (keyless full):** `cd <wt> && python3 -m pytest tests/test_provisioning_idempotency.py tests/test_check_anti_narration.py tests/test_canvas_primer.py tests/test_canvas_calibrate.py -q` → tudo verde; `python3 scripts/canvas-calibrate.py` → **PASS**; `bash scripts/test-registry.sh dogfood-catalog` aceita EX-60/61. Colar output bruto (EX-49).
- [ ] **Step 2 (owner-gated, NÃO nesta execução):** owner cria a issue de provisionamento (`docs/canvas/ISSUE-provisioning-idempotency.md`), roda `canvas-calibrate --live` num smoke isolado (enquadrador 3/3 + condução), verifica o marcador do step-07 num `~/.hermes/SOUL.md` real, e faz merge/push via worktree-detached nos tips de origin. Registrar evidência.

---

## Self-Review (autor)
**Spec coverage:** §4 D1→T1 (step-04/05 + verify step-07 owner-gated + issue draft); D2→T2 (EX-60/61); D3→T3 (checker+test); D4 primer→T4, keyless eval→T5, --live→T6; §5 gate→T7. OD-F5A-1 (SOLO, F4-independente)→Global Constraints + T0 branch off origin/main; OD-F5A-2 (primer+avaliação, keyless+--live)→T4/T5/T6.
**Placeholders:** código real em T1/T2/T3 (checker) /T5; T4/T6 são docs+orquestração com seções/funções nomeadas concretas; nenhum "TBD".
**Type consistency:** `check_narration(messages)->list` (T3) usado em T5 `check_anti_narration_selftest`; `run_keyless(repo)->dict{soul,d1,dogfood,anti_narration,primer,verdict}` (T5) e `run_live` (T6) nomeados iguais; primer seções idênticas em T4 e T5 `check_primer`.
**Riscos p/ o executor:** (a) o validador dogfood pode exigir campos além do EX-01 → T2 Step 1 confirma o schema real e ajusta; (b) rodar o step-04/05 script inteiro é frágil (sourcing common.sh) → T1 testa por (i) source-lint das flags + (ii) rsync isolado provando preservação, não o script inteiro; (c) o seam do enquadrador no `--live` (in-process vs HTTP no webui isolado) → T6 usa a receita C0 verificada.
