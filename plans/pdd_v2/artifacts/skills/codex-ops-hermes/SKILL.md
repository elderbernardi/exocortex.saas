---
name: codex-ops-hermes
description: "Operar Codex no ecossistema Hermes/Exocórtex com dois trilhos (delegação vs CLI), com evidência local e padrões de segurança."
version: 1.0.0
author: Exocórtex
metadata:
  hermes:
    tags: [codex, hermes, delegation, cli, harness, evidence, safety]
    category: exocortex
---

# Codex Ops (Hermes)

Skill de classe para integrar e operar Codex dentro do Hermes/Exocórtex.
Objetivo: **usar os benefícios da assinatura do Codex** de forma consistente, verificável e segura.

## Quando usar

Use esta skill quando o executivo pedir qualquer coisa do tipo:
- “quero usar minha assinatura do Codex aqui”
- “delegue pro Codex”
- “integre Codex no Hermes”
- “faça o Codex codar/refatorar/executar comandos”
- “use Codex só para pensar/planejar”

## Princípio: Dois Trilhos (não misturar)

Você sempre declara explicitamente qual trilho está usando.

TRILHO A — Codex CLI (execução)
- Quando: editar/criar arquivos, rodar comandos, tocar em repositório, revisão com diffs.
- Meio preferido: **wrapper caseiro** que captura evidência local (JSON) em disco.

TRILHO B — Delegação via provider (raciocínio/planejamento)
- Quando: análise, síntese, plano, checklist, alternativas, hipóteses.
- Meio: `delegate_task` com provider `openai-codex` (independente do modelo principal do gateway).

## TRILHO B — Configurar e usar delegação via openai-codex

1) Verificar credenciais
- Rodar: `hermes auth list`
- Critério: deve existir `openai-codex`.

2) Setar provider/model de delegação
- `hermes config set delegation.provider openai-codex`
- `hermes config set delegation.model gpt-5.2` (ou outro estável disponível no provider)

3) Delegar com contrato mínimo
Toda delegação deve conter:
- objetivo + critérios de aceite
- restrições explícitas (ex.: “não mudar deps”, “não mexer em X”)
- se houver execução posterior: formato do output esperado (checklist, passos, comandos)

## TRILHO A — Codex CLI com evidência local (wrapper)

Preferência: usar o wrapper caseiro para rodar `codex exec` e registrar evidências.

Arquitetura (paths estáveis):
- runner: `~/.hermes/scripts/codex_learning/run_codex_with_learning.py`
- review: `~/.hermes/scripts/codex_learning/review_latest_run.py`
- evidências: `~/.hermes/codex-learning/`
  - `runs/` (JSON por execução)
  - `events/` (start/end)

Uso seguro (default):
- Por padrão, use `--scratch` para tarefas arbitrárias.
- Só use `--cd <repo>` quando o executivo apontar explicitamente o caminho e aceitar o risco.

Permissões de escrita (gotcha crítico):
- Sem `--full-auto`/`--yolo`, o Codex pode cair em sandbox read-only.
- Se a tarefa exige escrever arquivos: passar `--full-auto`.
  - O wrapper mapeia `--full-auto` para `codex exec --sandbox workspace-write`.

## Verificação (não confiar em “feito”)

Depois do TRILHO A, sempre checar evidência local.

Checklist mínimo:
- `git_status_porcelain` existe no JSON
- `git_changed_files` inclui **untracked** (arquivos novos) — não usar `git diff --name-only` como fonte única
- `git_untracked_files` capturado explicitamente
- `git_diff_stat` registrado

Em repositório real:
- rodar testes/build do projeto e registrar saída/exit code.

## Heurística de roteamento (regra simples)

- “precisa escrever/editar arquivo / mexer em repo” → TRILHO A
- “precisa pensar/planejar/resumir” → TRILHO B
- híbrido → decompor: TRILHO B (plano) → TRILHO A (execução) → verificação final

## Artefatos de apoio

- Referência de configuração e gotchas (sessão): `references/codex-hermes-two-tracks.md`
- Template de prompt de configuração (colar em outra instância): `templates/config-prompt-codex-hermes.md`

## Pitfalls (os que realmente mordem)

1) Untracked não aparece em diff
- `git diff --name-only` não lista arquivos `??`.
- Use `git status --porcelain` (ou evidência do wrapper) para enumerar mudanças.

2) Scratch pode ser read-only
- Se espera escrita, declarar e habilitar `--full-auto`.

3) Sem evidência, você não sabe se executou
- Exigir JSON do wrapper como prova, não narrativa.
