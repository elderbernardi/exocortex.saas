# F1a — Patch harness "canvas v0.5": plano de implementação (OWNER-GATED via PR)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> **Antes de qualquer tarefa, leia o contrato de execução em `00-INDEX.md`.** Este plano NÃO toca o hermes-webui — só o exocortex.saas. A F1b (fork) só começa DEPOIS que o PR deste plano for aprovado e mergeado pelo owner (guardrail do F1-CHARTER).

**Goal:** Unificar os 5 drifts do harness v0.4 e adicionar os campos do método ao canvas — entregue como **PR owner-gated** no exocortex.saas (`collab/canvas-v05` → `main`), retrocompatível.

**Architecture:** O v0.5 padroniza a chave canônica **`vetor`** (termo do framework, EX-05) em TODAS as camadas; adota o **superset de 8 valores** de `intent_type`; adiciona ao **núcleo** (schema) 3 campos do método (`shape`, `done_criteria`, `verification`) e ao **documento** (template) também `scope[]`, `assumptions[]`, `authorization[]` (preenchidos em sessão, não pelo LLM). Regra semântica nova e explícita: **canvas pode ser `ambiguo`; tarefa registrada NÃO pode** — `register_task_from_canvas.py` rejeita `ambiguo` com erro claro. Fallback de leitura `vector` mantido por 1 ciclo (retrocompat com os 10 canvases-spike vivos em `_tasks/`).

**Tech Stack:** Python stdlib + PyYAML; pytest do repo; `compile_soul.py`/`skill_judge.py` como gates.

## Global Constraints

- Repo alvo: `/home/elder/projetos/projetob/exocortex.saas`, branch nova **`collab/canvas-v05`** a partir de `main`.
- ⚠️ O working tree tem **sujeira local do owner** (`INSTALL.md`, `acervo/micro/estudio-criativo/microverso.yaml`, `install.sh`, …): NUNCA `git add -A/-u/.` — sempre paths explícitos; nunca tocar/reverter esses arquivos.
- Arquivos permitidos: `acervo/global/tools/harness/{canvas_schema.py,register_task_from_canvas.py}`, `acervo/global/templates/harness-v0.4/{canvas.yaml,task.yaml}`, `skills/excrtx-behavior-canvas/SKILL.md`, `SOUL_SEED.md` (SOMENTE via `compile_soul.py`, nunca à mão), `docs/plans/2026-07-23_canvas-tarefas/adr/ADR-CT-06-canvas-v05.md` (novo), `CHANGELOG.md`, `tests/test_canvas_v05.py` (novo). Nada além.
- Zero dependências novas. PT-BR em docs/comentários de domínio; código/commits em inglês.
- Prova bruta por tarefa (EX-49); bounds do INDEX (3 falhas → parar).
- **O PR final NÃO é mergeado pelo agente** — abrir e parar (gate do owner).

---

### Task 1: Branch + ADR-CT-06 (as decisões do v0.5, escritas antes do código)

**Files:**
- Create: `docs/plans/2026-07-23_canvas-tarefas/adr/ADR-CT-06-canvas-v05.md`

- [ ] **Step 1: Branch**

```bash
cd /home/elder/projetos/projetob/exocortex.saas
git checkout main && git pull origin main && git checkout -b collab/canvas-v05
git branch --show-current
```
Expected: `collab/canvas-v05`

- [ ] **Step 2: Escrever a ADR** com este conteúdo exato:

```markdown
# ADR-CT-06 — Canvas v0.5: unificação de drifts + campos do método

status: proposta (aprovação = merge do PR collab/canvas-v05 pelo owner)
data: 2026-07-24
contexto: meta issue #130 · F0-RESULTADO §6 (drifts 1-4) · F1-CHARTER §Insumos (5º drift) · recon F1 2026-07-24

## Decisões

1. **Chave canônica: `vetor`** (termo do framework, EX-05) em todas as camadas — schema (já usa), template canvas.yaml (era `vector`), task.yaml (era `vector`), `register_task_from_canvas.py` (era `vector`). Leitura com **fallback `vector`** mantida por 1 ciclo no register (10 canvases-spike vivos em `_tasks/` usam `vector`; nunca são re-validados, mas podem ser registrados).
2. **Enum de `vetor`**: canvas = 4 valores (`execucao|evolucao|manutencao|ambiguo`) em schema E comentários de template. **task.yaml = 3 valores** — não é drift, é regra semântica explícita: *canvas pode ser ambiguo; tarefa registrada não pode*; o register rejeita `ambiguo` com erro acionável.
3. **Enum de `intent_type`: superset de 8** (`explorar|decidir|produzir|revisar|manter|publicar|ingestao|outro`) em schema, template, SKILL (body e compiled_rules) e espelhos do fork (F1b). Retrocompatível (só amplia).
4. **Núcleo v0.5 (+3 campos opcionais, emitidos pelo enquadrador)**: `shape` (`pergunta|tarefa|plano-primeiro`), `done_criteria` (string), `verification` (string — a verificação nomeada do fable-method). `focus.minLength: 3` mantido.
5. **Documento v0.5 (+6 campos)**: os 3 do núcleo + `scope: []`, `assumptions: []`, `authorization: []` (preenchidos durante a sessão — AUTH com palavras exatas do executivo; NÃO são emitidos pelo LLM).
6. `additionalProperties: false` mantido no schema do núcleo (novos campos declarados).
7. Correções de arrasto no register: `--from-stdin` passa a parsear campos (bug latente: hoje ignora e cai nos defaults da CLI); `task_id` ganha sufixo `_HHMMSS` (colisão mesmo-dia-mesmo-título hoje sobrescreve silenciosamente via `exist_ok=True`); template inline de fallback alinhado ao arquivo (`status: candidate`, era `registered`).

## Consequências

- F1b atualiza os espelhos do fork (`canvas_validate._ENUMS/_ALLOWED`, `canvas_store._CORE_TO_DOC` vira identidade em `vetor`, `_DEFAULTS`, JS lê `canvas.vetor`) SOMENTE após o merge deste PR.
- Propagação ao acervo vivo: re-rodar `bash setup.sh` (step-04 sobrescreve tools/templates incondicionalmente) OU cópia manual dirigida — passo T0 da F1b.
- `compile_soul.py --validate-compiled-rules --require-d1-pass` e `skill_judge --d1-only` são gates deste PR.
```

- [ ] **Step 3: Commit**

```bash
git add docs/plans/2026-07-23_canvas-tarefas/adr/ADR-CT-06-canvas-v05.md
git commit -m "docs(canvas-v05): ADR-CT-06 — unification decisions before code"
```

---

### Task 2: `canvas_schema.py` v0.5 + testes

**Files:**
- Modify: `acervo/global/tools/harness/canvas_schema.py`
- Create: `tests/test_canvas_v05.py`

**Interfaces:**
- Produces: `CANVAS_SCHEMA` v0.5 — required inalterado (`focus`,`vetor`,`intent_type`); `intent_type` enum com 8 valores; novas properties opcionais `shape` (enum `pergunta|plano-primeiro|tarefa`), `done_criteria` (string), `verification` (string); `title` atualizado para "Exocórtex Canvas v0.5". `get_schema()` inalterado.

- [ ] **Step 1: Testes (falhando)** — `tests/test_canvas_v05.py`:

```python
import importlib.util
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parents[1] / \
    "acervo/global/tools/harness/canvas_schema.py"


def _load():
    spec = importlib.util.spec_from_file_location("cs", SCHEMA_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.CANVAS_SCHEMA


def test_v05_intent_type_superset_de_8():
    s = _load()
    assert set(s["properties"]["intent_type"]["enum"]) == {
        "explorar", "decidir", "produzir", "revisar", "manter",
        "publicar", "ingestao", "outro"}


def test_v05_campos_do_metodo_presentes_e_opcionais():
    s = _load()
    for campo in ("shape", "done_criteria", "verification"):
        assert campo in s["properties"], campo
        assert campo not in s["required"], campo
    assert set(s["properties"]["shape"]["enum"]) == {
        "pergunta", "plano-primeiro", "tarefa"}


def test_v05_nucleo_preservado():
    s = _load()
    assert s["required"] == ["focus", "vetor", "intent_type"]
    assert set(s["properties"]["vetor"]["enum"]) == {
        "execucao", "evolucao", "manutencao", "ambiguo"}
    assert s["properties"]["focus"]["minLength"] == 3
    assert s["additionalProperties"] is False
```

- [ ] **Step 2: Rodar e ver falhar**

```bash
python3 -m pytest tests/test_canvas_v05.py -q 2>&1 | tail -3
```
Expected: 2 FAILED (superset e campos do método), 1 passed (núcleo).

- [ ] **Step 3: Editar `canvas_schema.py`** — no dict `CANVAS_SCHEMA`: `"title": "Exocórtex Canvas v0.5"`; em `intent_type.enum` acrescentar `"publicar", "ingestao", "outro"`; acrescentar às `properties` (antes de `additionalProperties`):

```python
        "shape": {
            "type": "string",
            "enum": ["pergunta", "plano-primeiro", "tarefa"],
            "description": "Shape of the ask (fable-method): question, plan-first or task",
        },
        "done_criteria": {
            "type": "string",
            "description": "What 'done' looks like for this task, in one sentence",
        },
        "verification": {
            "type": "string",
            "description": "Named verification proving done_criteria (observable check)",
        },
```

- [ ] **Step 4: Rodar e ver passar**

```bash
python3 -m pytest tests/test_canvas_v05.py -q 2>&1 | tail -2
```
Expected: `3 passed`

- [ ] **Step 5: Regressão do auditor (consumidor direto do schema)**

```bash
python3 - <<'EOF'
import sys
sys.path.insert(0, "acervo/global/tools/harness")
from auditor_canvas_validator import validate_canvas
ok_core = {"focus": "Renegociar Alfa", "vetor": "execucao", "intent_type": "publicar",
           "shape": "tarefa", "done_criteria": "oficio aprovado",
           "verification": "manifest + receipt"}
print("v05 core:", validate_canvas(ok_core))
print("v04 core:", validate_canvas({"focus": "Renegociar Alfa", "vetor": "execucao",
                                    "intent_type": "produzir"}))
EOF
```
Expected: ambas as linhas indicam válido (sem "Unknown field"). Se a assinatura de `validate_canvas` diferir, use a função pública que `auditor_pipeline.py:70` chama e cole a saída bruta.

- [ ] **Step 6: Commit**

```bash
git add acervo/global/tools/harness/canvas_schema.py tests/test_canvas_v05.py
git commit -m "feat(canvas-v05): schema — intent_type superset(8) + shape/done_criteria/verification"
```

---

### Task 3: Templates `canvas.yaml` + `task.yaml` v0.5

**Files:**
- Modify: `acervo/global/templates/harness-v0.4/canvas.yaml`
- Modify: `acervo/global/templates/harness-v0.4/task.yaml`

- [ ] **Step 1: `canvas.yaml`** — trocar a linha `vector: evolucao  # evolucao|execucao|manutencao` por:

```yaml
vetor: evolucao  # evolucao|execucao|manutencao|ambiguo (canvas PODE ser ambiguo; tarefa registrada NÃO — ver ADR-CT-06)
```

Atualizar o comentário de `intent_type` para os 8 valores. Acrescentar após o bloco `user_intention:` os campos do método:

```yaml
shape: tarefa  # pergunta|plano-primeiro|tarefa (fable-method)
done_criteria: ""       # o que é "pronto", em 1 frase
verification: ""        # verificação nomeada e observável do done_criteria
scope: []               # superfícies que a tarefa vai tocar (expandir = surprise)
assumptions: []         # premissas load-bearing (checáveis)
authorization: []       # AUTH: palavras exatas do executivo p/ cada ação externa (preenchido em sessão)
```

- [ ] **Step 2: `task.yaml`** — trocar `vector:` por `vetor:` com comentário:

```yaml
vetor: "{vector}"  # evolucao|execucao|manutencao — tarefa registrada exige vetor RESOLVIDO (ambiguo é estado de canvas, não de task; ADR-CT-06)
```

(manter o placeholder `{vector}` — é o nome do parâmetro de `str.format` no register; renomeá-lo é Task 4).

- [ ] **Step 3: Verificar que os templates continuam YAML válido**

```bash
python3 -c "import yaml,sys; [yaml.safe_load(open(p)) for p in ['acervo/global/templates/harness-v0.4/canvas.yaml','acervo/global/templates/harness-v0.4/task.yaml']]; print('YAML OK')"
```
Expected: `YAML OK` (nota: task.yaml contém placeholders `{...}` de format — se o safe_load falhar por isso, valide só o canvas.yaml e confirme o task.yaml com o teste do register na Task 4; diga qual caminho usou).

- [ ] **Step 4: Commit**

```bash
git add acervo/global/templates/harness-v0.4/canvas.yaml acervo/global/templates/harness-v0.4/task.yaml
git commit -m "feat(canvas-v05): templates — vetor key, ambiguo comment, method fields"
```

---

### Task 4: `register_task_from_canvas.py` v0.5 + testes

**Files:**
- Modify: `acervo/global/tools/harness/register_task_from_canvas.py`
- Modify: `tests/test_canvas_v05.py` (acrescentar classe de testes)

**Interfaces:**
- Produces: register lê **`vetor` com fallback `vector`** (canvas doc); rejeita `vetor=ambiguo` (exit 1, mensagem `ERROR: vetor 'ambiguo' — resolva o vetor antes de registrar a tarefa`); `--from-stdin` parseia os campos do texto (mesmo `load` do arquivo); `task_id = task_{YYYYMMDD}_{slug}_{HHMMSS}`; fallback inline do template com `status: candidate`.

- [ ] **Step 1: Testes (falhando)** — acrescentar a `tests/test_canvas_v05.py`:

```python
import os
import subprocess
import sys

REGISTER = str(Path(__file__).resolve().parents[1] /
               "acervo/global/tools/harness/register_task_from_canvas.py")


def _run_register(tmp_path, canvas_yaml: str, extra=()):
    acervo = tmp_path / "acervo"
    (acervo / "_tasks").mkdir(parents=True)
    (acervo / "global/templates/harness-v0.4").mkdir(parents=True)
    src = Path(__file__).resolve().parents[1] / \
        "acervo/global/templates/harness-v0.4/task.yaml"
    (acervo / "global/templates/harness-v0.4/task.yaml").write_text(
        src.read_text(encoding="utf-8"), encoding="utf-8")
    cpath = tmp_path / "c.yaml"
    cpath.write_text(canvas_yaml, encoding="utf-8")
    env = dict(os.environ, ACERVO=str(acervo))
    proc = subprocess.run(
        [sys.executable, REGISTER, "--canvas", str(cpath), "--title", "Tarefa X",
         *extra], env=env, capture_output=True, text=True)
    return proc, acervo


def test_register_le_vetor_v05(tmp_path):
    proc, acervo = _run_register(tmp_path, "vetor: manutencao\nfocus: f\n")
    assert proc.returncode == 0, proc.stderr + proc.stdout
    task_yaml = next((acervo / "_tasks").glob("task_*/task.yaml")).read_text()
    assert "manutencao" in task_yaml


def test_register_fallback_vector_v04(tmp_path):
    proc, acervo = _run_register(tmp_path, "vector: evolucao\nfocus: f\n")
    assert proc.returncode == 0
    task_yaml = next((acervo / "_tasks").glob("task_*/task.yaml")).read_text()
    assert "evolucao" in task_yaml


def test_register_rejeita_ambiguo(tmp_path):
    proc, _ = _run_register(tmp_path, "vetor: ambiguo\nfocus: f\n")
    assert proc.returncode == 1
    assert "ambiguo" in (proc.stderr + proc.stdout)


def test_task_id_tem_sufixo_de_unicidade(tmp_path):
    proc, acervo = _run_register(tmp_path, "vetor: execucao\n")
    task_dir = next((acervo / "_tasks").glob("task_*")).name
    import re
    assert re.fullmatch(r"task_\d{8}_[a-z0-9-]+_\d{6}", task_dir), task_dir
```

- [ ] **Step 2: Rodar e ver falhar**

```bash
python3 -m pytest tests/test_canvas_v05.py -q 2>&1 | tail -3
```

- [ ] **Step 3: Editar o register** — mudanças cirúrgicas:
  1. Leitura (linhas ~186-187): `vector = canvas_data.get("vetor", canvas_data.get("vector", args.vector))` (mesma dupla no `compute_content_hash`, linha ~85).
  2. Gate ambiguo, logo após resolver `vector`: `if vector == "ambiguo": print("ERROR: vetor 'ambiguo' — resolva o vetor antes de registrar a tarefa"); sys.exit(1)`.
  3. `--from-stdin` (linhas ~168-176): após ler `canvas_text`, também `canvas_data = parse` do texto (reusar o mesmo parser YAML/fallback de `load_yaml_file` extraído para função que aceite string).
  4. `generate_task_id` (linhas ~69-76): sufixo `_%H%M%S` UTC.
  5. Template inline de fallback (linhas ~103/136): `status: candidate` e `lifecycle_state: candidate`.

- [ ] **Step 4: Rodar e ver passar (arquivo todo)**

```bash
python3 -m pytest tests/test_canvas_v05.py -q 2>&1 | tail -2
```
Expected: `7 passed` (3 da Task 2 + 4 novos)

- [ ] **Step 5: Commit**

```bash
git add acervo/global/tools/harness/register_task_from_canvas.py tests/test_canvas_v05.py
git commit -m "feat(canvas-v05): register — vetor key w/ v04 fallback, reject ambiguo, stdin parse fix, unique task_id, inline template status=candidate"
```

---

### Task 5: EX-06 SKILL.md v0.5 + compile_soul + D1

**Files:**
- Modify: `skills/excrtx-behavior-canvas/SKILL.md`
- Modify: `SOUL_SEED.md` (SOMENTE via compile_soul.py)

- [ ] **Step 1: Editar SKILL.md** — (a) `version: 2.0.0` → `2.1.0`; (b) em `compiled_rules:` atualizar a lista de campos: required inalterado; Optional passa a `macroverso_status, microverso_primary, gaps[], urgency, shape, done_criteria, verification`; acrescentar a linha: `When proposing a canvas for launch, always propose done_criteria plus a NAMED verification; if none can be named, emit a gap question instead.`; (c) no body: tabela §1 ganha as 3 linhas novas (shape / done_criteria / verification com pergunta e exemplo cada); §2 nota que scope/assumptions/authorization são preenchidos em sessão (documento, não núcleo); enum de intent_type no body alinhado aos 8 valores; formato de exposição §4 ganha linha `│ Pronto quando: {done_criteria} · verificação: {verification}`.

- [ ] **Step 2: Gates de compilação (saída bruta obrigatória)**

```bash
python3 scripts/skill_judge.py --skill excrtx-behavior-canvas --d1-only 2>&1 | tail -5
python3 scripts/compile_soul.py --validate-compiled-rules --require-d1-pass 2>&1 | tail -5
```
Expected: D1 `COMPLIANT`; compile OK (bloco `## Canvas` do SOUL_SEED regenerado). Se o desync-guard reclamar (>50% keywords ausentes do body), os termos novos precisam constar no body — volte ao Step 1.

- [ ] **Step 3: Conferir o SOUL_SEED regenerado e commitar**

```bash
git diff --stat SOUL_SEED.md skills/excrtx-behavior-canvas/SKILL.md
git add skills/excrtx-behavior-canvas/SKILL.md SOUL_SEED.md
git commit -m "feat(canvas-v05): EX-06 v2.1 — method fields in compiled rules + body; soul recompiled"
```
Expected no diff stat: só o bloco Canvas mudou no SOUL_SEED (se outros blocos mudarem, PARE e reporte — compile_soul não deveria tocá-los).

---

### Task 6: CHANGELOG + PR owner-gated (PARAR no gate)

**Files:**
- Modify: `CHANGELOG.md` (entrada no topo, seção Unreleased ou data corrente, 5-8 linhas resumindo ADR-CT-06)

- [ ] **Step 1: CHANGELOG + push**

```bash
git add CHANGELOG.md && git commit -m "docs(canvas-v05): changelog entry"
git push -u origin collab/canvas-v05 2>&1 | tail -2
```

- [ ] **Step 2: Abrir o PR (NÃO mergear)**

```bash
gh pr create -R elderbernardi/exocortex.saas --base main --head collab/canvas-v05 \
  --title "Canvas v0.5 — unificação de drifts + campos do método (ADR-CT-06)" \
  --body "Implementa ADR-CT-06 (docs/plans/2026-07-23_canvas-tarefas/adr/ADR-CT-06-canvas-v05.md). Épico #130 · F1 #132. Resolve os 5 drifts do F0-RESULTADO §6 + F1-CHARTER §Insumos. Retrocompatível (fallback vector; enums só ampliam). Gates: pytest tests/test_canvas_v05.py (7 passed), skill_judge D1 COMPLIANT, compile_soul --validate-compiled-rules OK. **Owner-gated: F1b só começa após o merge (guardrail F1-CHARTER).**

🤖 Generated with [Claude Code](https://claude.com/claude-code)"
```

- [ ] **Step 3: Prova + parada**

```bash
gh pr view -R elderbernardi/exocortex.saas --json number,url,state | head -3
```
Colar saída bruta no report; comentar o link do PR na issue #132; **PARAR — o merge é decisão do owner.**

---

## Self-review do plano (executado na escrita)

- Cobertura: 5 drifts ↔ T2 (enums/campos), T3 (templates/ambiguo), T4 (register/vetor+fallback) · campos do método ↔ T2/T3/T5 · gates compile/D1 ↔ T5 · owner gate ↔ T6.
- Correções de arrasto do recon (stdin bug, task_id collision, inline status) ↔ T4 com testes.
- Consistência: chave `vetor`; enum shape `pergunta|plano-primeiro|tarefa`; nomes de teste únicos; `{vector}` placeholder do format preservado no template (renomeio do parâmetro é interno ao register e não exigido).
- O fork NÃO é tocado (F1b); espelhos listados na ADR-CT-06 §Consequências.
