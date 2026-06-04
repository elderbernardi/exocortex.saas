---
name: excrtx-harness-codexint
description: "Integrar OpenAI Codex (CLI e provider) ao Hermes/Exocórtex com governança, roteamento e verificação."
version: 0.1.0
created_by: agent
context: exocortex
platforms: [linux]
---

CODex aqui significa duas coisas distintas:

1) Codex CLI (agente local via terminal; exige git repo; interativo/PTY)
2) Provider/model openai-codex dentro do Hermes (para subagentes via delegation)

Este skill define como usar as duas sem acoplamento frágil ao modelo principal do gateway.


QUANDO USAR

- O executivo quer “aproveitar assinatura do Codex” dentro do Hermes.
- Precisamos delegar tarefas gerais ao Codex (subagente Hermes) E usar Codex para codar (Codex CLI).
- O gateway do Hermes pode estar respondendo com outro LLM via API, mas a execução/roteamento precisa seguir funcionando.


PRINCÍPIO-CHAVE (anti-confusão)

- Codex CLI é um executável local. Independe do provider/model do Hermes.
- Delegation provider é configuração do Hermes. Independe do modelo principal do gateway.

Ou seja: dois trilhos, uma política de roteamento.


ARQUITETURA (DOIS TRILHOS)

TRILHO A — Codex CLI para trabalho que mexe em repositório
- Chamado via tool `terminal` com `pty=true`.
- Pré-condição: estar dentro de um git repo (Codex recusa fora).
- Modos:
  - One-shot: `codex exec '<prompt>'`
  - Mudança maior (preferir): `codex exec --full-auto '<prompt>'` (sandbox; auto-aprova mudanças no workspace)
  - Evitar `--yolo` como default (só com decisão explícita do executivo).

TRILHO B — Subagente Hermes usando provider openai-codex (tarefas gerais)
- Configurar `delegation.provider` + `delegation.model` para apontar para openai-codex.
- Executar via `delegate_task(...)` quando a tarefa for paralelizável e não exigir interatividade de CLI.


POLÍTICA DE ROTEAMENTO (REGRA OBJETIVA)

1) Se a tarefa envolve alteração de arquivos/código em repo, refactor, revisão de PR, ou execução de testes → TRILHO A (Codex CLI).
2) Se a tarefa é geral (pesquisa/síntese/plano/comparação/checklist) e o objetivo é velocidade/paralelismo → TRILHO B (delegate_task com provider Codex).
3) Se a tarefa é híbrida → Hermes/Exocórtex decompõe:
   - análise/decisão aqui
   - implementação no Codex CLI
   - validação aqui


PADRÕES DE PROMPT (CONTRATOS DE SAÍDA)

A) Template mínimo para Codex CLI (sempre pedir evidência verificável)

- Objetivo (1 linha)
- Contexto (paths, versões, constraints)
- Critérios de aceitação
- Restrições (não mexer em X; manter API)
- Validação: comandos a rodar (test/lint/build)
- Saída obrigatória:
  - lista de arquivos alterados
  - resumo por arquivo
  - comandos executados + status
  - riscos/limitações

B) Template mínimo para delegate_task

- Escopo do subagente (o que ele PODE e NÃO PODE fazer)
- Forma do output (estrutura explícita)
- Fontes: se puder usar web/file/terminal, dizer claramente
- Pedido de “assumptions list” (para separar fato de inferência)


VERIFICAÇÃO (PÓS-EXECUÇÃO)

Após Codex CLI:
- `git status` (limpo vs sujo)
- `git diff` (inspecionar)
- rodar testes/lint conforme stack
- se falhar: pedir correção incremental ao Codex com contexto (log + diff)

Após delegate_task:
- validar se o output é acionável
- quando houver comando sugerido: executar você mesmo (ou gerar DRAFT se ação externa)


GOVERNANÇA PARA GATEWAY (LLM PRINCIPAL POR API)

Meta: a operação não pode depender do modelo principal do gateway.

- TRILHO A (CLI) é sempre local e funciona mesmo que o gateway use outro LLM.
- TRILHO B depende apenas de `delegation.*` estar configurado; deve continuar estável quando `model.default/provider` do Hermes mudar.

Aceite (smoke tests):
- Rodar um `codex exec` em repo descartável e checar `git diff`.
- Rodar um `delegate_task` simples e confirmar execução.
- Trocar o modelo principal do Hermes (gateway/API) e repetir o `delegate_task`.


ECOSSISTEMA/COMUNIDADE (O QUE VALE AVALIAR)

- Plugin "Hermes Agent Gateway" (Bigsunnyboy/hermes-codex-gateway):
  - objetivo: governança chat→fila→worktree→runner→verify→artefatos
  - útil quando a execução deve ser comandada por chat com guardrails (approve/allow/verify)
- Plugin "Hermes Codex Learning" (New-dev0/hermes-codex-learning):
  - objetivo: instrumentar sessões do Codex e exportar artefatos locais para o Hermes aprender
- Harness "Maestro" (ReinaMacCredy/maestro):
  - objetivo: estado local durável (spec→task→verify→ship) para múltiplos agentes

Ver `references/hermes-community-codex.md` para notas curtas e critérios.


PITFALLS (NÃO ESQUECER)

- Codex CLI exige git repo; para scratch usar `mktemp -d && git init`.
- Sempre usar `pty=true` ao chamar Codex CLI pelo terminal.
- Não “chutar” string de `delegation.model`: descobrir via `hermes model` e então setar config.
- Não confundir: provider do modelo principal ≠ provider da delegação.


EVOLUÇÃO (QUANDO PRODUTIZAR)

Quando o fluxo estiver provado:
- encapsular em um skill-operacional (ou scripts) com:
  - criação automática de worktree
  - execução codex
  - captura de evidências (diff/test)
  - limpeza

