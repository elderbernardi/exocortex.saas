Notas de comunidade (Codex  Hermes)  varredura inicial

Objetivo
- Mapear projetos/plugins/skills existentes que resolvem: governana de execuo local via chat, integrao Codex CLI, e pipeline de aprendizado.

1) Bigsunnyboy/hermes-codex-gateway (aka hermes-agent-gateway)
- Evidncias (README/plugin.yaml/OPERATIONS.md):
  - Instalao: `hermes plugins install Bigsunnyboy/hermes-agent-gateway` + enable + restart gateway.
  - Hook: `pre_gateway_dispatch` (intercepta comando de canal antes do dispatch normal).
  - Runner atual habilitado: Codex CLI.
  - Fluxo declarado: channel `/agent ...`  plugin  queue  cron wake gate  git worktree  runner  verify  delivery.
  - Governana:
    - `mode=read` vs `mode=write`
    - write requer aprovao
    - `allow=` enforce de paths alterados
    - `verify=` comandos antes de reportar sucesso
    - captura de artefatos
  - Tooling exportado (plugin.yaml):
    - create_agent_task, approve_agent_task, get_agent_task_status, ensure_agent_worker_cron, etc.
- Observao de compatibilidade:
  - UX de aprovao e cards  citada para Feishu/Lark; em outros adapters pode cair para fallback textual.
- Quando vale:
  - Operar execuo local governada por chat (com trilha de auditoria) e reduzir risco operacional.

2) New-dev0/hermes-codex-learning
- Propsito: instrumentar sesses Codex com hooks e exportar logs/summaries para o Hermes consumir.
- Artefatos declarados (locais):
  - `~/.hermes/codex-learning/events/<session_id>.jsonl`
  - `~/.hermes/codex-learning/runs/<session_id>.summary.json`
  - `~/.hermes/codex-learning/reviews/<session_id>.review.md`
  - gera/atualiza skill inbox: `~/.hermes/skills/codex-learning-inbox/SKILL.md`
- Dois modos:
  - hooks (dependem de trust e de suporte da build do Codex)
  - wrapper (mais confivel para automao/CI)
- Quando vale:
  - melhorar operao do Codex ao longo do tempo com aprendizado local (sem telemetria externa).

3) ReinaMacCredy/maestro
- Propsito: harness local-first para spec  task  verify  ship com evidncia e handoffs em disco.
- Integra com vrios agentes (Codex/Claude/Hermes) como um conductor.
- Quando vale:
  - quando o problema for disciplina de execuo multi-agente (estado durvel, evidencia, handoff) e no apenas integrao pontual.

Critrios para escolher (prtico)
- Quer governana por chat (approve/allow/verify/worktree/artifacts)?  hermes-agent-gateway.
- Quer extrair aprendizado de sesses reais do Codex para skills/memria?  hermes-codex-learning.
- Quer padronizar ciclo spec/task/verify/ship multi-agente com estado compartilhado?  maestro.

Prximo passo recomendado (seguro)
- Provar primeiro a camada dois trilhos (Codex CLI + delegation provider) sem plugins.
- Se precisar governana em chat: testar hermes-agent-gateway em modo local e validar compatibilidade do adapter.
