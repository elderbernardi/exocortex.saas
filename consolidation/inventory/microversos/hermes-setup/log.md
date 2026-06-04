
# Log

## [2026-05-30] create | microverso hermes-setup ontology v2
- Criado microverso `hermes-setup` para registrar setup, replicabilidade e evolução do harness Hermes/Exocórtex.
- Definido `SCHEMA.md` local com Ontologia Multifocal v2: diretórios funcionais + Natures semânticas no frontmatter.
- Registrado contrato bloqueante `contracts/llm-wiki-adapter-contract.md`: LLM Wiki nativa é upstream mecânico; Acervo é fonte canônica; escrita somente via `acervo-llm-wiki-adapter` → `acervo-manager`.
- Registrada decisão `decisions/adr-007-ontology-v2-summary.md`: arquivos flat de Nature foram descontinuados; novas escritas usam diretórios funcionais.
- Registrado workflow `workflows/replicable-exocortex-setup.md`: setup reproduzível cria camadas, diretórios funcionais, bundle de skills, profiles e lint estrutural.
- Index atualizado com referências para contratos, decisões e workflows do microverso.
- Definições importantes vinculadas às ADRs do projeto Exocórtex SaaS: ADR-006 e ADR-007.

## [2026-05-30] update | Personal Artifact Workspace no microverso hermes-setup
- Registrada decisão `decisions/personal-artifact-workspace.md`: Drive é ferramenta de publicação, Acervo mantém fonte/assets/manifest/receipt e compartilhamento externo segue Draft-First.
- Registrado workflow `workflows/publish-final-artifacts.md`: pacote `_artifacts/`, exports finais, upload privado no Drive, receipt local e página semântica quando houver valor cognitivo.
- Atualizado `workflows/replicable-exocortex-setup.md` para incluir publicação de artefatos finais como etapa pós-setup.
- Index atualizado com decisão e workflow.

## [2026-05-30] update | Personal Intake Workspace no microverso hermes-setup
- Registrada decisão `decisions/personal-intake-workspace.md`: bruto entra por `_inbox/` e promoção semântica só ocorre após triagem.
- Registrado workflow `workflows/ingest-multichannel-inputs.md`: persistência, extração, roteamento e promoção semântica posterior.
- Atualizado `workflows/replicable-exocortex-setup.md` para incluir `_inbox/`, skill e ferramenta de intake como parte do setup reproduzível.
- Index atualizado com decisão e workflow.

## [2026-05-31] update | Hindsight como memória operacional auxiliar
- Adicionado contrato `contracts/hindsight-operational-memory-contract.md`: Hindsight atua como memória operacional semântica auxiliar; Acervo permanece fonte canônica.
- Adicionado workflow `workflows/hindsight-operational-memory.md`: instalação, uso, promoção para Acervo, ajuste de ruído, auditoria e desativação.
- Adicionados templates `templates/hindsight-config.local_embedded.json` e `templates/hindsight-config.cloud-pilot.json`.
- Atualizado `workflows/replicable-exocortex-setup.md` com etapa opcional-controlada para Hindsight.
- Atualizado `~/.hermes/setup.sh` previsto para configuração idempotente via `EXOCORTEX_ENABLE_HINDSIGHT=1`.
- Autoridade: Hindsight observa e recupera; Exocórtex interpreta; Acervo canoniza.

## [2026-05-31] update | DocBrain como parser engine local
- Adicionada ferramenta `tools/docbrain-cli-api.md`: contrato operacional para Hermes consumir DocBrain via CLI API local.
- Adicionado workflow `workflows/install-docbrain-parser-engine.md`: clone do repo, build, health check, política de key e lembrete quando key ausente.
- Adicionado registro de skill `skills/docbrain-cli-api.md`: skill local criada em `~/.hermes/skills/exocortex/docbrain-cli-api/SKILL.md`.
- Atualizado `workflows/replicable-exocortex-setup.md` com etapa de instalação do DocBrain para intake documental.
- Política de key: DocBrain reutiliza a key main do Hermes via `OPENROUTER_API_KEY`; `DOCBRAIN_LLM_API_KEY` é override explícito.
- Atualizado `~/.hermes/setup.sh` com etapa idempotente de DocBrain parser engine.

## [2026-05-31] decision | Hermes roda dentro de ~/exocortex em produção
- Registrada decisão `decisions/hermes-runtime-cwd-exocortex-home.md`.
- Atualizado `workflows/replicable-exocortex-setup.md` com separação runtime/workspace como etapa 0.
- Definido `HERMES_HOME=~/.hermes` como runtime/config.
- Definido `EXOCORTEX_HOME=~/exocortex` como workspace cognitivo.
- Definido `ACERVO=~/exocortex/acervo` como fonte canônica para novos Hermes.
- Definido que produção Hermes deve rodar com cwd em `~/exocortex`; `~/.hermes/acervo` fica apenas como symlink de compatibilidade.

## [2026-06-01] decision | Estúdio Criativo como microverso base
- Criado microverso `estudio-criativo` como domínio transversal de criação do Exocórtex.
- Registrada decisão `decisions/estudio-criativo-base-microverso.md`.
- Atualizado `workflows/replicable-exocortex-setup.md` para provisionar o Estúdio como microverso base, adaptável ao usuário e compatível com criação com IA e sem IA.
- Aplicado patch aprovado em `~/.hermes/setup.sh` para provisionamento idempotente do microverso `estudio-criativo`.
- Validado com `bash -n` e teste isolado em `HERMES_HOME` temporário, incluindo reexecução idempotente.

## [2026-06-01] update | Setup alinhado para estudo com NotebookLM
- Verificada disponibilidade do NLM (`nlm`) e autenticação ativa.
- Verificado MCP server `notebooklm` habilitado no Hermes.
- Ajustada numeração das etapas do `~/.hermes/setup.sh` para fluxo consistente `[1/8]..[8/8]`.
- Mantida etapa de integração NotebookLM no setup com fallback de instalação e lembrete de login.

## [2026-06-01] update | Hindsight local single-node como padrão de setup
- Atualizado `~/.hermes/setup.sh` e `exocortex.saas/setup.sh` para provisionar Hindsight local em Docker único (`~/.hermes/hindsight-local`) com volume persistente (`data/`) antes da configuração final de memória.
- Adicionada regra de exclusão segura da memória local Hindsight apenas com confirmação explícita por parâmetros (`EXOCORTEX_HINDSIGHT_RESET_DATA=1` + `EXOCORTEX_HINDSIGHT_CONFIRM_DELETE=DELETE_HINDSIGHT_MEMORY`).
- Atualizados workflows `hindsight-operational-memory.md` e `replicable-exocortex-setup.md` para refletir sync automático de `llm_model`/`llm_base_url` a partir do setup Hermes.
- Memória simples local agora é desativada quando Hindsight fica ativo (`memory.memory_enabled=false`, `memory.user_profile_enabled=false`).
- Política de escopo formalizada: um Hindsight por Hermes e bank único compartilhado entre perfis `exec`/`evol` (`bank_id_template=exocortex`).
- Novo workflow canônico: `workflows/hindsight-local-docker-single-node.md`.
- Templates `hindsight-config.local_embedded.json` e `hindsight-config.cloud-pilot.json` alinhados para bank único (`exocortex`).
- [2026-06-01T21:06:19-03:00] Contrato local de identidade Exocórtex sobre Hermes aplicado em `contracts/exocortex-hermes-identity.md`.

## [2026-06-01] pending | Approval-gate / Draft-First como tema de setup e harness
- Registrada pendência no projeto de setup (`plans/STATUS.md`) para modelar um gateway de aprovação com enforcement real, vinculado a draft/fingerprint.
- Atualizado `workflows/replicable-exocortex-setup.md` com etapa pendente sobre approval-gate, staging privado, cron/background e implantação do Exocórtex sobre Hermes.
- Escopo da pendência: evitar drift de Draft-First sem quebrar autonomia de produção interna.

## [2026-06-01] proposed | Mini-ADR para approval-gate Draft-First
- Criado `decisions/approval-gate-draft-first.md` com proposta de approval-gate transacional na fronteira entre produção interna e emissão externa.
- A proposta vincula aprovação humana a fingerprint do draft e explicita impacto sobre cron, background jobs, staging privado e implantação do Exocórtex sobre Hermes.
- Próximo passo, se aprovado, é transformar a proposta em ADR aceita com ponto de interceptação, ledger e máquina de estados definidos.

## [2026-06-01] planned | Plano por camadas + retomada em kanban
- Criado `/home/elder/projetos/pessoal/exocortex.saas/plans/approval-gate/IMPLEMENTATION_PLAN.md` com plano por camadas para GUI, server, harness, storage, cron/background e testes adversariais.
- Atualizado `plans/STATUS.md` para usar esse plano como base formal de retomada e decisão arquitetural.
- Criado card de kanban `t_86183f68` em estado `blocked`, reservado para retomada após decisão explícita do executivo sobre arquitetura, storage, escopo da v1 e staging privado.

## [2026-06-02] workflow | Plano de setup do Harness Exocórtex v0.4
- Criado `workflows/exocortex-harness-v0.4-setup-plan.md` para materializar a arquitetura do microverso `harness-project`.
- O plano cobre diretórios `_tasks`, `_activities`, `_automations`, `_inbox`, `_artifacts/items`, templates, skills comportamentais, ferramentas mínimas, atividades programáveis, política de publicação e critérios de aceite.
- Index atualizado.

## [2026-06-03] workflow | Setup Harness v0.4 atualizado pelos TODOs

- Atualizado `workflows/exocortex-harness-v0.4-setup-plan.md` para refletir a troca Atividade→Rotina e o uso de `_routines/`.
- Incluídos scripts candidatos: `generate_artifact_views.py`, `compute_task_state_hash.py`, `scan_maintenance_recommendations.py` e `sindico_maintenance_report.py`.
- Incluídos critérios de aceite sobre Kanban HITL, views determinísticas, hash de tarefa e email sob Draft-First.
