---
title: "Codex × Hermes: integração caseira (dois trilhos)"
created: "2026-05-29"
updated: "2026-05-29"
tags: [codex, hermes, delegacao, harness, evidencias]
confidence: high
---

Contexto

Objetivo: integrar Codex ao Hermes de forma caseira, sem depender de plugins de terceiros, com separação clara entre:

Trilho A — Codex CLI (execução local / alteração de arquivos)

- Use quando a tarefa envolve: criar/editar arquivos, refactor, rodar comandos, mexer em repo, gerar patches, executar testes.
- Preferir wrapper/harness local (abaixo) para padronizar logging e evidências.
- Default seguro: rodar em scratch (repo temporário) quando a tarefa é “arbitrária” ou sem escopo claro.

Trilho B — Delegation provider openai-codex (tarefas gerais)

- Use quando a tarefa envolve: planejar, analisar, sintetizar, escrever checklist, gerar hipóteses.
- Implementa via delegate_task com delegation.provider=openai-codex e delegation.model fixo.
- Mantém independência do modelo principal do gateway (que pode ser outro provider).

Checklist de integração (Hermes)

1) Credenciais
- `hermes auth list` deve mostrar `openai-codex`.

2) Configuração delegação (Trilho B)
- `hermes config set delegation.provider openai-codex`
- `hermes config set delegation.model gpt-5.2` (ou outro listado no cache local)
- Verificar em `~/.hermes/config.yaml`.

Harness do Codex CLI (Trilho A)

Artefatos locais (padrão):
- runner: `~/.hermes/scripts/codex_learning/run_codex_with_learning.py`
- reviewer: `~/.hermes/scripts/codex_learning/review_latest_run.py`
- runs: `~/.hermes/codex-learning/runs/*.json`
- events: `~/.hermes/codex-learning/events/*.json`

Semântica importante

- Codex pode cair em sandbox read-only se não for explicitamente configurado para escrita.
- No wrapper: usar `--full-auto` para mapear para sandbox de escrita (`workspace-write`).
- Codex CLI costuma exigir estar dentro de um git repo; o wrapper garante `git init` + commit inicial.

Evidências (não confiar em “feito”)

Aprendizado-chave: `git diff --name-only` / `--stat` não inclui untracked (`??`). Para evidência correta, basear em:
- `git status --porcelain` (inclui `??`)
- `git ls-files --others --exclude-standard` (lista untracked)

Contrato de prompt (quando enviar tarefa para Codex CLI)

Sempre explicitar:
- Objetivo + critérios de aceite
- Restrições (não mexer em X, não mudar deps, etc.)
- Evidências esperadas: arquivos alterados/criados + comandos rodados + stdout relevante + exit code.

Heurística de roteamento

- “Precisa escrever/editar arquivo, rodar testes, mexer em repo” → Trilho A (Codex CLI)
- “Precisa analisar/planejar/sintetizar” → Trilho B (delegate_task)
- Híbrido → decompor: Trilho B (análise) → Trilho A (execução) → Hermes valida e resume evidências.
