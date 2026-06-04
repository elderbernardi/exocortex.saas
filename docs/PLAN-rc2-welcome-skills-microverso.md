# PLAN — RC2: Welcome Flow, Skill Naming Convention, Microverso Package System

> **Criado:** 2026-06-04
> **Origem:** Notas do executivo no walkthrough + análise do blog Anthropic "Lessons from Building Claude Code"
> **Scope:** 3 workstreams paralelos, 2 ADRs novos, 1 migration script
> **Prerequisito:** RC1 (full-run validado com zero erros ✅)

---

## Contexto Geral

O RC1 validou a infraestrutura: 33 skills instaladas, acervo v0.4 funcional, Docker full-run limpo. Agora o RC2 endereça três gaps identificados pelo executivo:

1. **Welcome & Onboarding** — O Exocórtex instala, mas não se apresenta. Um novo usuário não sabe o que pode fazer, como usar, nem a filosofia por trás. O executivo pediu um "boas-vindas" que funcione em qualquer gateway (Telegram, Web UI, Hermes Desktop) e guie a configuração do Telegram como primeiro gate.

2. **Padronização de Skills** — As 33 skills têm nomes inconsistentes (`acervo-manager`, `stop-slop`, `taste-skill`, `codex-harness`). O executivo pediu o padrão `excrtx-{TYPE}-{NAME}` inspirado nas recomendações do blog "Lessons from Building Claude Code" da Anthropic.

3. **Microverso Package System** — O executivo notou que "microversos não são só os arquivos. São as skills, pacotes dependentes." O BKL-008 precisa de um design concreto para extensões de terceiros.

---

## User Review Required

> [!IMPORTANT]
> **Decisão de naming prefix:** O executivo pediu `excrtx-{TYPE}-{NAME}`. Antes de implementar, confirmar se o prefix `excrtx` é o desejado ou se `xc` (mais curto) seria preferível. `excrtx` tem 6 chars; `xc` tem 2. Em autocomplete, `excrtx-` já filtra tudo.

> [!IMPORTANT]
> **Taxonomia de tipos (TYPE):** A proposta abaixo usa 9 categorias derivadas do blog da Anthropic + domínio Exocórtex. O executivo deve validar antes do rename.

> [!WARNING]
> **Breaking change:** O rename de skills é uma migração destrutiva. Todos os arquivos que referenciam nomes antigos (bundle YAML, setup.sh, profile.yaml, SOUL.md, ADRs) precisam ser atualizados atomicamente. Proposta: script de migração + mapeamento old→new.

---

## Open Questions

1. **Prefix final**: `excrtx` ou `xc`? (Recomendação: `excrtx` por ser autoexplicativo e não colidir com nada)
2. **Microverso package format**: `.tar.gz` com manifest ou diretório git com `microverso.yaml`? (Recomendação: diretório git para versionamento)
3. **Welcome via Telegram**: O executivo tem bot Telegram já configurado ou precisa ser criado no onboarding?
4. **Google credential check no setup.sh**: Incluir neste RC2 ou manter como BKL-003?

---

## Workstream A — Welcome & Onboarding Multi-Gateway

### Filosofia

O Welcome não é um "tutorial". É a **primeira sessão do Exocórtex** — a primeira vez que o framework cognitivo opera. Deve encarnar os princípios do Cap. 1 e 3 do livro:

- *"Não é usar IA. É relacionar-se com IA."*
- *"A IA é um exoesqueleto para o pensamento."*
- *Memento te hominem* — lembre-se de que és humano.

O Welcome acontece em **duas fases**:

1. **Apresentação** (passiva) — O sistema se apresenta, explica a filosofia, mostra o que pode fazer
2. **Onboarding** (ativa) — A entrevista dos 5 blocos que gera o SOUL.md personalizado

### ADR-014: Welcome Flow Multi-Gateway

#### [NEW] `docs/ADR/ADR-014-welcome-flow.md`

**Decisão:** O Welcome é um artefato markdown (`WELCOME.md`) + uma skill comportamental (`excrtx-onboard-welcome`) que renderiza o conteúdo adaptado ao gateway.

**Motivação:** O conteúdo do Welcome é universal (a filosofia não muda), mas a *apresentação* muda por gateway:

| Gateway | Formato | Características |
|---------|---------|----------------|
| **Telegram** | Mensagens curtas, emojis, botões inline | Limite de 4096 chars/msg. Dividir em cards. Botões para "Continuar" / "Pular" |
| **Web UI** | Rich HTML, acordeões, progress bar | Pode mostrar Canvas Cognitivo visual, diagramas mermaid |
| **Hermes Desktop** | Markdown longo, terminal-friendly | Formato atual da skill, com sections colapsáveis |

**Estrutura do WELCOME.md:**

```markdown
# Bem-vindo ao Exocórtex.IA

## O que é
(2 parágrafos: exoesqueleto para pensamento, não substitui — amplifica)

## A Filosofia
(Macroverso, Microverso, Tarefa — 3 camadas em 1 diagrama)

## O que você pode fazer
(Lista das capacidades principais, agrupadas por vetor)

### Vetor de Evolução (aprender, aprofundar)
- Pesquisa profunda com fontes
- Modo socrático (a IA guia, não entrega)
- Geração de personas para simulação

### Vetor de Execução (criar, decidir, revisar)
- Draft-First: rascunhos que você valida antes de enviar
- Canvas de projeto: planejamento estruturado
- Slides, documentos, apresentações
- Análise de repositórios técnicos

## Integrações disponíveis
- 📱 Telegram (recomendado para começar)
- 🌐 Web UI
- 💻 Hermes Desktop
- 📧 Google Workspace (Gmail, Calendar, Drive)
- 📓 NotebookLM

## Configurando o Telegram
(Passo a passo: obter token do BotFather, configurar no Hermes)

## Próximo passo: Onboarding
(Transição para a entrevista dos 5 blocos)
```

**Regras:**
- O WELCOME.md é estático (instalado pelo setup.sh no acervo/global/)
- A skill `excrtx-onboard-welcome` lê o WELCOME.md e adapta ao gateway
- O executivo pode pular direto para o onboarding
- Se o Telegram não estiver configurado, guiar a configuração como parte do welcome

---

### Arquivos Afetados

#### [NEW] `plans/pdd_v2/artifacts/acervo/global/knowledge/WELCOME.md`
Conteúdo estático do Welcome (filosofia + capabilities + setup guides).

#### [MODIFY] `plans/pdd_v2/artifacts/skills/exocortex-onboarding/SKILL.md`
Renomear para `excrtx-onboard-welcome` e adicionar:
- Seção de apresentação multi-gateway
- Detecção de gateway (Telegram/Web/Desktop)
- Guia de configuração do Telegram
- Transição para entrevista (skill `excrtx-onboard-interview`)

#### [NEW] `plans/pdd_v2/artifacts/skills/excrtx-onboard-interview/SKILL.md`
Skill que executa a entrevista dos 5 blocos (extraída da atual `exocortex-onboarding`). Separar welcome de interview permite que o executivo pule o welcome em re-onboarding.

---

## Workstream B — Skill Naming Convention (ADR-015)

### Lições do Blog Anthropic

Do artigo "Lessons from Building Claude Code: How we use skills" (2026-06-03):

1. **Skills são pastas, não arquivos** — `SKILL.md` + scripts + data + references
2. **Description é o trigger** — A description deve ser "pushy" e explicitar *quando* e *por quê* ativar
3. **Seção "Gotchas" é a mais valiosa** — Edge cases e failure points
4. **Enforcement via scripts, não via "MUST"** — Se precisa ser feito, forneça um script
5. **Verificação é tudo** — Skills que dão ao agente forma de verificar seu trabalho são as mais efetivas
6. **9 categorias recorrentes** — Library/API, Product Verification, Data Fetching, Debugging, Infrastructure, Domain Knowledge, Creative Design, Workflow Automation, Scaffolding

### ADR-015: Skill Naming Convention

#### [NEW] `docs/ADR/ADR-015-skill-naming-convention.md`

**Decisão:** Todas as skills do Exocórtex seguem o padrão: `excrtx-{TYPE}-{NAME}`

**Motivação:**
- Autocomplete: digitar `excrtx-` lista todas as skills do sistema
- Classificação implícita: o TYPE indica a natureza da skill
- Descoberta: novos agentes entendem o propósito pelo nome
- Extensibilidade: skills de terceiros usam outro prefix (e.g., `ext-{TYPE}-{NAME}`)

**Taxonomia de tipos (TYPE):**

| TYPE | Descrição | Exemplos (nome atual → novo) |
|------|-----------|------------------------------|
| `onboard` | Onboarding e welcome flows | `exocortex-onboarding` → `excrtx-onboard-welcome` |
| `memory` | Gestão de memória e acervo | `acervo-manager` → `excrtx-memory-manager` |
| `quality` | Qualidade de output e design system | `stop-slop` → `excrtx-quality-antislop` |
| `behavior` | Modos comportamentais e vetores | `exocortex-vetor-ativo` → `excrtx-behavior-vetor` |
| `produce` | Produção de artefatos (execução) | `exocortex-slides` → `excrtx-produce-slides` |
| `integrate` | Integrações externas (MCP, API) | `google-drive-direct-api` → `excrtx-integrate-gdrive` |
| `govern` | Governança, aprovação, compliance | `exocortex-tool-governance` → `excrtx-govern-tools` |
| `harness` | Infraestrutura operacional do Exocórtex | `codex-harness` → `excrtx-harness-core` |
| `assess` | Avaliação e diagnóstico | `technical-repo-fit-assessment` → `excrtx-assess-repofit` |

**Regras de NAME:**
- Máximo 12 caracteres
- Lowercase, sem underscores
- Descritivo da ação principal
- Sem redundância com TYPE (e.g., `excrtx-quality-quality-gate` ❌ → `excrtx-quality-gate` ✅)

### Tabela de Migração Completa

| # | Nome Atual | Nome Novo | TYPE |
|---|-----------|-----------|------|
| 1 | `acervo-llm-wiki-adapter` | `excrtx-memory-wikiadapt` | memory |
| 2 | `acervo-manager` | `excrtx-memory-manager` | memory |
| 3 | `browser-use` | `excrtx-integrate-browser` | integrate |
| 4 | `codex-harness` | `excrtx-harness-core` | harness |
| 5 | `codex-integration` | `excrtx-harness-codexint` | harness |
| 6 | `codex-ops-hermes` | `excrtx-harness-hermesops` | harness |
| 7 | `docbrain-cli-api` | `excrtx-integrate-docbrain` | integrate |
| 8 | `exocortex-base-microverso-setup` | `excrtx-memory-mvsetup` | memory |
| 9 | `exocortex-briefing` | `excrtx-behavior-briefing` | behavior |
| 10 | `exocortex-canvas` | `excrtx-behavior-canvas` | behavior |
| 11 | `exocortex-design-system` | `excrtx-quality-designsys` | quality |
| 12 | `exocortex-draft-first` | `excrtx-govern-draftfirst` | govern |
| 13 | `exocortex-kanban-backlog` | `excrtx-harness-kanban` | harness |
| 14 | `exocortex-new-microverso` | `excrtx-memory-newmicro` | memory |
| 15 | `exocortex-notebooklm-knowledge-router` | `excrtx-integrate-nlmroute` | integrate |
| 16 | `exocortex-notebooklm-operational-workflow` | `excrtx-integrate-nlmops` | integrate |
| 17 | `exocortex-onboarding` | `excrtx-onboard-welcome` | onboard |
| 18 | `exocortex-operational-memory` | `excrtx-memory-opsmemory` | memory |
| 19 | `exocortex-output-quality-gate` | `excrtx-quality-gate` | quality |
| 20 | `exocortex-prompt-log` | `excrtx-harness-promptlog` | harness |
| 21 | `exocortex-self-test` | `excrtx-assess-selftest` | assess |
| 22 | `exocortex-slides` | `excrtx-produce-slides` | produce |
| 23 | `exocortex-tool-governance` | `excrtx-govern-tools` | govern |
| 24 | `exocortex-vetor-ativo` | `excrtx-behavior-vetor` | behavior |
| 25 | `gerador-oficios` | `excrtx-produce-oficios` | produce |
| 26 | `google-drive-direct-api` | `excrtx-integrate-gdrive` | integrate |
| 27 | `hermes-mcp-oauth-integrations` | `excrtx-integrate-oauth` | integrate |
| 28 | `hermes-surface-architecture` | `excrtx-harness-surfaces` | harness |
| 29 | `personal-artifact-workspace` | `excrtx-produce-artifacts` | produce |
| 30 | `personal-intake-workspace` | `excrtx-memory-intake` | memory |
| 31 | `stop-slop` | `excrtx-quality-antislop` | quality |
| 32 | `taste-skill` | `excrtx-quality-taste` | quality |
| 33 | `technical-repo-fit-assessment` | `excrtx-assess-repofit` | assess |

#### [NEW] `plans/pdd_v2/artifacts/scripts/migrate_skill_names.sh`

Script de migração que:
1. Renomeia diretórios em `skills/`
2. Atualiza `name:` no frontmatter de cada SKILL.md
3. Atualiza `exocortex-alpha.yaml` (bundle)
4. Atualiza `EXPECTED_SKILLS` em `setup.sh`
5. Atualiza referências em `profile.yaml` (manut)
6. Atualiza referências cruzadas em SOUL_SEED.md
7. Gera relatório de diff

**Arquivos afetados pela migração:**

| Arquivo | Tipo de mudança |
|---------|----------------|
| `skills/*/SKILL.md` | Rename dir + update `name:` frontmatter |
| `skill-bundles/exocortex-alpha.yaml` | Update 33 entradas |
| `setup.sh` | Update `EXPECTED_SKILLS` array |
| `profiles/manut/profile.yaml` | Update `skills:` list |
| `SOUL_SEED.md` | Update referências a skills |
| `BACKLOG_TEMPLATE.md` | Update nomes nas descrições |
| `scripts/docker-fullrun-entrypoint.sh` | Nenhum (não referencia nomes) |
| `docs/ADR/ADR-011-*` a `ADR-013-*` | Update referências (non-blocking) |

---

## Workstream C — Microverso Package System (ADR-016)

### ADR-016: Microverso Package Format

#### [NEW] `docs/ADR/ADR-016-microverso-package-format.md`

**Decisão:** Um "microverso package" é um diretório versionável com um `microverso.yaml` manifest que declara seus requisitos.

**Motivação:** O executivo pediu: *"Microversos não são só os arquivos. São as skills, pacotes dependentes."* O sistema precisa:
1. Instalar um microverso com um comando
2. Verificar que as skills necessárias existem (ou instalar)
3. Validar dependências de pacotes Python/Node
4. Permitir extensões de terceiros

**Formato do `microverso.yaml`:**

```yaml
# microverso.yaml — manifesto de um microverso empacotado
apiVersion: excrtx/v1
kind: Microverso
metadata:
  name: estudio-criativo
  version: 1.0.0
  description: "Microverso para produção criativa — slides, apresentações, design thinking"
  author: exocortex-team
  tags: [criativo, design, slides, produção]

# Dependências
requires:
  skills:
    - excrtx-produce-slides      # Skill que precisa existir
    - excrtx-quality-designsys   # Skill de design system
    - excrtx-behavior-canvas     # Canvas cognitivo
  python_packages:               # Pacotes pip/uv (opcionais)
    - python-pptx>=0.6.21
  node_packages: []              # Pacotes npm (opcionais)
  mcps: []                       # MCPs necessários (opcionais)

# Estrutura (relativa ao diretório do pacote)
tree:
  contracts/: "Contratos e manifestos"
  workflows/: "Workflows de produção"
  templates/: "Templates reutilizáveis"
  personas/: "Personas do microverso"
  prompts/: "Prompts testados"
  knowledge/: "Base de conhecimento"
  decisions/: "ADRs locais"
  reflections/: "Meta-reflexões"
  tools/: "Scripts utilitários"
  skills/: "Skills locais do microverso (se houver)"

# Hooks (opcionais)
hooks:
  post_install: "scripts/post_install.sh"   # Executado após instalação
  validate: "scripts/validate.sh"           # Verifica integridade
```

**Fluxo de instalação:**

```
excrtx-memory-mvinstall (skill)
  ├── 1. Lê microverso.yaml
  ├── 2. Verifica requires.skills (existem no bundle?)
  │     └── Se falta → WARN + offer to install
  ├── 3. Verifica requires.python_packages
  │     └── Se falta → uv pip install
  ├── 4. Copia árvore para $EXOCORTEX_HOME/acervo/micro/{name}/
  ├── 5. Executa hooks.post_install (se existir)
  ├── 6. Registra no manifest global (acervo/global/_meta/microversos.yaml)
  └── 7. Executa hooks.validate (se existir)
```

#### [NEW] `plans/pdd_v2/artifacts/skills/excrtx-memory-mvinstall/SKILL.md`
Skill que implementa o fluxo acima.

#### [MODIFY] `plans/pdd_v2/artifacts/acervo/micro/estudio-criativo/`
Adicionar `microverso.yaml` ao Estúdio Criativo como primeiro exemplo do formato.

---

## Verificação

### Automated Tests

```bash
# 1. Validar migração de nomes
bash plans/pdd_v2/artifacts/scripts/migrate_skill_names.sh --dry-run

# 2. Rebuild + full-run Docker
docker build --no-cache -t exocortex-fullrun -f Dockerfile.fullrun .
docker run --rm -e OPENROUTER_API_KEY="..." -e EXOCORTEX_ENABLE_HINDSIGHT=0 exocortex-fullrun

# 3. Verificar WELCOME.md instalado
docker run --rm exocortex-fullrun cat /home/testuser/exocortex/acervo/global/knowledge/WELCOME.md

# 4. Verificar microverso.yaml no Estúdio Criativo
docker run --rm exocortex-fullrun cat /home/testuser/exocortex/acervo/micro/estudio-criativo/microverso.yaml

# 5. Verificar que 0 referências aos nomes antigos restam
docker run --rm exocortex-fullrun grep -r "acervo-manager\|stop-slop\|taste-skill\|codex-harness" /home/testuser/.hermes/
```

### Manual Verification
- Executivo revisa WELCOME.md e valida o tom/conteúdo
- Executivo valida a taxonomia TYPE antes do rename
- Executivo confirma o formato de microverso.yaml

---

## Task Breakdown

### Fase 1 — ADRs & Design (HITL) ⏱️ ~2h

| Task | Entrega | HITL |
|------|---------|------|
| T1.1 | Escrever ADR-014 (Welcome Flow) | ✅ Review |
| T1.2 | Escrever ADR-015 (Naming Convention) | ✅ Review |
| T1.3 | Escrever ADR-016 (Microverso Package) | ✅ Review |
| T1.4 | Executivo valida taxonomia TYPE | ✅ Blocking |
| T1.5 | Executivo confirma prefix `excrtx` | ✅ Blocking |

### Fase 2 — Welcome Content ⏱️ ~1h

| Task | Entrega | HITL |
|------|---------|------|
| T2.1 | Criar `acervo/global/knowledge/WELCOME.md` | ✅ Review conteúdo |
| T2.2 | Criar skill `excrtx-onboard-welcome` | — |
| T2.3 | Extrair skill `excrtx-onboard-interview` (da atual onboarding) | — |
| T2.4 | Atualizar setup.sh para copiar WELCOME.md | — |

### Fase 3 — Skill Rename Migration ⏱️ ~2h

| Task | Entrega | HITL |
|------|---------|------|
| T3.1 | Criar `migrate_skill_names.sh` | — |
| T3.2 | Dry-run da migração | — |
| T3.3 | Executar migração real nos artifacts | — |
| T3.4 | Atualizar setup.sh (EXPECTED_SKILLS, funções) | — |
| T3.5 | Atualizar bundle, profiles, SOUL_SEED | — |
| T3.6 | Atualizar ADRs existentes (best-effort) | — |
| T3.7 | Full-run Docker validação | — |

### Fase 4 — Microverso Package ⏱️ ~1.5h

| Task | Entrega | HITL |
|------|---------|------|
| T4.1 | Criar `microverso.yaml` para Estúdio Criativo | ✅ Review format |
| T4.2 | Criar skill `excrtx-memory-mvinstall` | — |
| T4.3 | Atualizar setup.sh para verificar microverso.yaml | — |
| T4.4 | Documentar formato para extensores | — |

### Fase 5 — Validação Final ⏱️ ~30min

| Task | Entrega | HITL |
|------|---------|------|
| T5.1 | Docker full-run com tudo integrado | — |
| T5.2 | Walkthrough atualizado | ✅ Review |
| T5.3 | Commit + tag `rc2` | — |

---

## Resumo de Arquivos

| Ação | Arquivo |
|------|---------|
| **NEW** | `docs/ADR/ADR-014-welcome-flow.md` |
| **NEW** | `docs/ADR/ADR-015-skill-naming-convention.md` |
| **NEW** | `docs/ADR/ADR-016-microverso-package-format.md` |
| **NEW** | `plans/pdd_v2/artifacts/acervo/global/knowledge/WELCOME.md` |
| **NEW** | `plans/pdd_v2/artifacts/skills/excrtx-onboard-interview/SKILL.md` |
| **NEW** | `plans/pdd_v2/artifacts/skills/excrtx-memory-mvinstall/SKILL.md` |
| **NEW** | `plans/pdd_v2/artifacts/scripts/migrate_skill_names.sh` |
| **RENAME** | 33 diretórios em `plans/pdd_v2/artifacts/skills/` |
| **MODIFY** | `plans/pdd_v2/artifacts/setup.sh` |
| **MODIFY** | `plans/pdd_v2/artifacts/skill-bundles/exocortex-alpha.yaml` |
| **MODIFY** | `plans/pdd_v2/artifacts/profiles/manut/profile.yaml` |
| **MODIFY** | `plans/pdd_v2/artifacts/SOUL_SEED.md` |
| **MODIFY** | `plans/pdd_v2/artifacts/BACKLOG_TEMPLATE.md` |
| **MODIFY** | `plans/pdd_v2/artifacts/acervo/micro/estudio-criativo/` (add microverso.yaml) |
| **MODIFY** | `Dockerfile.fullrun` (se necessário por rename) |
| **MODIFY** | `scripts/docker-fullrun-entrypoint.sh` (se necessário) |
