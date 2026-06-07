---
name: excrtx-harness-core
description: "Harness caseiro para operar Codex CLI (exec) com rastreabilidade e verificação leve, sem plugins de terceiros."
version: 0.2.0
created_by: agent
platforms: [linux]
metadata:
  intent: class-level
---

# Codex Harness (caseiro)

Skill de operao para usar **Codex CLI** como executor de trabalho (especialmente cdigo) de forma reprodutedvel, com rastreabilidade local, **sem depender de plugins comunite1rios**.

Ne3o e9 uma skill de *learning*; e9 um harness de execue7e3o + evideancia.

## Quando usar

- O usue1rio quer *Codex para codar* (alterar arquivos, refatorar, criar scripts).
- O usue1rio quer delegar execue7f5es para o Codex sem acoplar ao modelo do gateway Hermes.
- Vocea precisa de um rastro local do que foi pedido/feito (prompt + saedda + evideancia git).

## Artefatos (local)

Padrão recomendado: usar o wrapper em `~/.hermes/scripts/codex_learning/` que grava em:

- `~/.hermes/codex-learning/runs/*.json`
- `~/.hermes/codex-learning/events/*.json`
- `~/.hermes/codex-learning/reviews/*.md`

Provisionamento esperado:
- `setup.sh` deve copiar `scripts/codex_learning/run_codex_with_learning.py` para `~/.hermes/scripts/codex_learning/`
- `setup.sh` deve copiar `scripts/codex_learning/review_latest_run.py` para `~/.hermes/scripts/codex_learning/`
- `setup.sh` deve criar `~/.hermes/codex-learning/{runs,events,reviews}`

## Modos

### 1) Scratch (padre3o seguro)

Use quando a tarefa ne3o depende de um repo real.

- cria diretf3rio tempore1rio
- inicializa git
- roda Codex
- captura evideancia

Exemplo:

```bash
python3 ~/.hermes/scripts/codex_learning/run_codex_with_learning.py \
  --scratch \
  --full-auto \
  --prompt 'Crie hello.py que imprime "hello" e rode python3 hello.py.'
```

### 2) Repo ne3o-credtico (aberto)

Use apenas quando explicitamente direcionado e o repo e9 ne3o-credtico.

```bash
python3 ~/.hermes/scripts/codex_learning/run_codex_with_learning.py \
  --cd /caminho/do/repo \
  --full-auto \
  --prompt '...'
```

## Flags e seme2ntica

- `--full-auto`: deve permitir escrita. Internamente, **mapear para** `--sandbox workspace-write` (o Codex vem depreciando `--full-auto`).
- `--yolo`: evita como padre3o; sf3 quando o usue1rio pedir explicitamente.

## Evideancia: o que capturar (ne3o-negocie1vel)

1) Prompt e comando executado.
2) stdout/stderr (com truncamento).
3) Git evidence:
   - `git status --porcelain`
   - `git_diff_stat`
   - lista de arquivos alterados **incluindo untracked** (importante).

## Pitfalls (aprendidos em produe7e3o)

- `git diff --name-only` e `git diff --stat` **ne3o mostram arquivos untracked** (`??`). Para medir "changed files" corretamente, derive do `git status --porcelain` e/ou `git ls-files --others --exclude-standard`.
- Codex pode cair em sandbox read-only se ne3o houver flag de escrita. Para tarefas que esperam criae7e3o/edie7e3o de arquivo, use `--full-auto` (ou equivalente `--sandbox workspace-write`).
- `--full-auto` pode aparecer como deprecated em builds recentes; preferir `--sandbox workspace-write`.

## Refereancias

- `references/codex-cli-gotchas.md` (gotchas + sinais em stderr + como interpretar)
