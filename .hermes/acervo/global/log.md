
# Global Log

> Registro cronológico de operações na camada global. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: create, update, ingest, archive, lint
> Rotacionar quando exceder 500 entradas: renomear para log-YYYY.md

## [2026-05-26] create | Global layer initialized
- Structure created with SCHEMA.md, index.md, log.md
- Natures: instrucoes.md, processos.md, ferramentas.md, conhecimento.md, reflexoes.md
- Directories: raw/ (articles, documents, assets), _archive/

## [2026-05-28] update | Macro layer populated (3 artefatos)
- macro/soul.md: natureza contexto — identidade do Exocórtex, papel, boundary
- macro/valores.md: natureza reflexão — 7 Values expandidos, trade-offs, red lines
- macro/estilo.md: natureza instrução — regras de tom, anti-padrões, modos por veto
- Fonte: SOUL.md do agente (P1 Identity). Seed templates substituídos por conteúdo real.

## [2026-05-28] create | Global layer artefatos transversais (3 artefatos)
- global/index.md: natureza contexto — catálogo universal com links para ferramentas-base e processos-transversais
- global/ferramentas-base.md: natureza ferramenta — Hermes core tools (19 tools) + 15 skills exocortex + tabela de uso por tipo de tarefa
- global/processos-transversais.md: natureza processo — 8 workflows universais: Boot Sequence, Vetor Classification, Draft-First, Quality Gates, Acervo Operations, Cross-Ref Protocol, Memory Hygiene, Escalação de Ambiguidade
- Seed templates (ferramentas.md, processos.md) mantidos como placeholders. Novos artefatos são os populados.

## [2026-05-28] onboarding | Onboarding do executivo Elder concluído
Microversos criados: gabinete (domain), ensino (domain), dev (project), pesquisa-ia (domain).
SOUL.md personalizado com perfil do executivo.
estilo.md atualizado com tom analítico-didático e modo par.
ferramentas-base.md atualizado com integrações do executivo.
groups.md atualizado com custom groups: IFSUL, CRIACAO, GESTAO.

## [2026-05-29] update | Superfícies operacionais e hardening do dashboard
- Criado `global/superficies-operacionais.md` com arquitetura recomendada: Telegram como interface principal, Hermes Dashboard com TUI como cockpit operacional.
- Requisito de segurança registrado: dashboard deve permanecer em `127.0.0.1:9119`; acesso remoto contínuo via Tailscale ou, pontualmente, túnel SSH.
- `global/index.md` atualizado para incluir o novo artefato e refletir a decisão operacional.

## [2026-05-30] migrate | legacy flat natures → functional ontology v2
- conhecimento.md → knowledge/legacy-conhecimento.md; original em _archive/legacy-flat-natures/conhecimento.md

## [2026-05-30] migrate | global ontology v2
- Diretórios funcionais criados
- SCHEMA.md atualizado
- index.md regenerado

## [2026-05-30] create | Personal Artifact Workspace MVP
- Criado contrato global `contracts/personal-artifact-workspace.md`.
- Criada documentação operacional `tools/personal-artifact-publisher.md`.
- Criada ferramenta executável `tools/artifact_publish.py` para pacote local + upload privado ao Google Drive via OAuth Hermes.
- Criada área operacional `acervo/_artifacts/` com README.
- Teste mínimo criou pacote `art_20260530_141313_teste-personal-artifact-workspace`; publicação falhou com 403 porque Google Drive API está desabilitada no projeto OAuth atual. Falha registrada em `receipt.google_drive.failed.json` e no manifesto.
- Decisão: Drive é ferramenta de publicação, não sincronização; Composio fica como fallback futuro, não dependência do MVP.

## [2026-05-30] update | Skill personal-artifact-workspace complementada
- Skill local `exocortex/personal-artifact-workspace` revisada após criação por self-improvement.
- Versão ajustada para 1.0.1 com licença MIT.
- Acrescentados triggers, skills relacionadas a carregar, procedimento expandido, manifest/receipt mínimo, política de destino, pitfalls e checklist de verificação.
- Criados arquivos auxiliares `templates/manifest-template.md` e `references/replication-checklist.md` dentro da skill.
- Validação local: frontmatter e tamanho do SKILL.md OK.

## [2026-05-30] create | Personal Intake Workspace
- Criado contrato global `contracts/personal-intake-workspace.md`.
- Criada documentação operacional `tools/personal-intake-workspace.md`.
- Criada ferramenta executável `tools/intake_ingest.py` para pacote local `_inbox/`, extração, triagem e promoção semântica posterior.
- Criada área operacional `acervo/_inbox/` com README.
- Atualizada skill local `exocortex/personal-intake-workspace` com checklist de repetibilidade.

## [2026-06-01] create | Frontend Slides Global Capability
- Criado contrato global `contracts/frontend-slides-global-capability.md`.
- Definido Markdown como fonte canônica e HTML/PDF/ZIP como exports.
- Definido Google Drive privado como destino padrão; Vercel apenas exceção com Draft-First.
- Registrada relação operacional com Estúdio Criativo.
