# PDD v2 — Plano de Configuração do Exocórtex.IA

> **Versão:** 2.0.0
> **Predecessor:** `plans/pdd/PLAN.md` (v1, concluído 2026-05-27)
> **Retrospectiva:** `RETROSPECTIVE.md` (análise de drift v1 → v2)
> **Playbook:** `PLAYBOOK.yaml` (protocolo de execução)
> **Metodologia:** Modelagem de configuração via prompts (evoluído de PDD)
> **Target:** Instância Docker limpa do Hermes Agent → Exocórtex.IA
> **Requisito:** `artifacts/` é autocontido — `setup.sh` provisiona sem dependências externas
> **Addendum pós-graduação:** `ARTIFACT_WORKSPACE.md` registra a capacidade de publicar artefatos finais no Drive do usuário via Acervo + receipt local.

---

## Princípios de Design (v2)

Derivados da retrospectiva do v1 (ver `RETROSPECTIVE.md`):

1. **Hermes é o centro.** O Exocórtex é uma configuração do Hermes, não um fork. Skills e artefatos respeitam a estrutura nativa.
2. **Skills por operação, não por taxonomia.** Dados se classificam por frontmatter; skills se classificam por verbo.
3. **Qualidade é identidade.** Quality skills (stop-slop, taste-skill) são pré-requisito, não comportamento tardio.
4. **Protocolo antes de prompt.** O `agent_protocol` é lido antes de qualquer ação de configuração.
5. **Estado é verdade.** O agente verifica o estado real do sistema, não confia na memória.
6. **Integrações são extensões.** MCPs e APIs externas ficam fora do fluxo principal — no BACKLOG.
7. **Auto-auditoria contínua.** Cada fase inclui um checkpoint de integridade (drift audit) antes de avançar.
8. **Provisionamento é externo.** O PDD produz a golden image. O Provisioner Agent a consome.

---

## Mapa de Fases

```
P0 (Foundation)  →  P1 (Identity)  →  P2 (Memory)  →  P3 (Behavior)  →  P4 (Validation)  →  P5 (Production)
     ↓                    ↓                ↓                 ↓                  ↓                    ↓
  Pré-req.          Alma + Quality    Acervo 4-layer     Skills de        Smoke Tests          Golden Image
  agent_protocol    SOUL.md           acervo-manager     negócio          5/5 self-test        Ready
  setup.sh seed     self-test         microversos        quality gate     drift audit final    
  quality skills    prompt-log        wiki architecture  vetor-ativo                           
```

### Mudanças em relação ao v1

| v1 | v2 | Motivo (ref. RETROSPECTIVE) |
|---|---|---|
| P0 = manual, sem artefatos | P0 = Foundation com agent_protocol + quality skills | D3, D5: protocolo e qualidade desde o dia 0 |
| P1 = Identity (005 prompts) | P1 = Identity + Quality (simplificado) | D3: stop-slop/taste já estão no P0, P1 foca em SOUL.md |
| P2 = Memory (010 prompts) | P2 = Memory (consolidado, 4 camadas desde o início) | D1, D2: acervo-manager + 4 camadas como design, não descoberta |
| P3 = Tools (MCPs) | P3 = Behavior (skills de negócio) | D6: MCPs vão para BACKLOG. P3 foca em comportamento |
| P4 = Behavior | P4 = Validation | v1 tinha P5 para validação; v2 antecipa |
| P5 = Validation | P5 = Production (golden image) | |
| P6 = Production | (eliminado, absorvido por P5) | P6 era um "estado", não uma fase com ações |
| Nenhum drift audit | Drift audit em TODAS as fases | D5: auto-auditoria contínua |

---

## P0: Foundation — Pré-requisitos e Protocolo

> **Status:** Pendente
> **Prompts:** Nenhum (setup manual)
> **Gate:** agent_protocol legível, setup.sh funcional, quality skills no path

### Objetivo

Preparar o terreno. O agente que executar P1 deve encontrar: protocolo de disciplina instalado, setup.sh semente funcional, e skills de qualidade disponíveis no diretório de artefatos.

### Artefatos-Semente (Golden Image Autocontida)

O diretório `artifacts/` espelha a estrutura do `~/.hermes/`, contendo a **golden image v2** completa e pronta para provisionamento via `setup.sh`.

> **Princípio de autocontenção:** `HERMES_HOME=/target bash artifacts/setup.sh` numa instância Docker limpa do Hermes deve produzir um Exocórtex funcional. Nenhum artefato externo é necessário — tudo está neste diretório.
>
> **MEMORY.md** não é semente — é gerado durante a execução dos prompts P1. O `setup.sh` cria apenas a estrutura; a identidade emerge dos prompts.

```
artifacts/
├── setup.sh                    # Script de reprodução (provisiona Hermes)
├── SOUL_SEED.md                # Template de identidade (base para SOUL.md)
├── BACKLOG_TEMPLATE.md         # Template para integrações futuras
├── skills/                     # Espelho de ~/.hermes/skills/exocortex/
│   ├── exocortex-self-test/    # Core: auto-diagnóstico
│   ├── exocortex-prompt-log/   # Core: log de prompts
│   ├── stop-slop/              # Quality: anti-slop textual
│   ├── taste-skill/            # Quality: visual (gpt-taste, brandkit, brutalist)
│   ├── exocortex-design-system/# Quality: tokens visuais (DESIGN.md cascade)
│   ├── acervo-manager/         # Memory: gerenciador do acervo
│   ├── exocortex-new-microverso/# Memory: criação de microversos
│   ├── exocortex-draft-first/  # Behavior: protocolo draft-first
│   ├── exocortex-vetor-ativo/  # Behavior: classificador de vetores
│   ├── exocortex-canvas/       # Behavior: extrator cognitivo
│   ├── exocortex-briefing/     # Behavior: morning briefing
│   ├── exocortex-onboarding/   # Behavior: onboarding (sem auto-provisioning)
│   ├── exocortex-output-quality-gate/ # Behavior: quality gate de output
│   ├── exocortex-tool-governance/     # Behavior: governança de ferramentas
│   └── browser-use/            # External: automação de browser
├── acervo/                     # Espelho de ~/.hermes/acervo/
│   ├── macro/                  # soul.md, valores.md, estilo.md, assets/
│   ├── global/                 # index.md, DESIGN.md, 7 Natures
│   ├── micro/_template/        # Template de microverso
│   └── shared/                 # cross-refs/, groups.md, glossario.md
├── profiles/                   # exec/ e evol/
│   ├── exec/                   # Vetor de Execução
│   └── evol/                   # Vetor de Evolução
└── skill-bundles/
    └── exocortex-alpha.yaml    # Bundle com todas as skills
```

### Critérios de Saída

- [ ] Todos os artefatos-semente existem no diretório `artifacts/`
- [ ] `setup.sh` executa sem erros em ambiente limpo
- [ ] `PLAYBOOK.yaml` contém `agent_protocol` com 5 regras + drift_audit
- [ ] Diretório `logs/` criado e vazio

→ Detalhes: `phases/P0_FOUNDATION.md`

---

## P1: Identity — Alma do Exocórtex

> **Status:** Pendente
> **Prompts:** 001–005
> **Gate:** self-test ≥ 2/5
> **Depende de:** P0 completo

### Objetivo

Instalar a identidade do Exocórtex no Hermes: SOUL.md com personalidade executiva, skills de auto-teste e logging, e **quality skills já funcionais**.

### Diferenças do v1

1. **Quality skills (stop-slop + taste-skill) são instaladas nesta fase**, não na P4.
   - Prompt 004B: stop-slop (textual)
   - Prompt 004C: taste-skill (visual)
   - Values #6 e #7 adicionados ao SOUL.md
2. **Drift audit** ao final da fase: verificar que setup.sh reflete o estado real.
3. **Prompts reduzidos**: 005 → 005 (mesmo número, mas conteúdo mais preciso).

### Prompts

| ID | Propósito | Artefatos |
|---|---|---|
| 001 | Bootstrap self-test | `exocortex-self-test` skill + Configuration State em SOUL.md |
| 002 | Core Identity | SOUL.md com Identity, Values, Communication Style |
| 003 | Behavioral Boundaries | SOUL.md + Draft-First + Vetores + Limites |
| 004 | Prompt Log + Quality Skills | `exocortex-prompt-log` + `stop-slop` + `taste-skill` + `exocortex-design-system` + Values "Estética Funcional" / "Anti-Slop" |
| 005 | P1 Checkpoint + Drift Audit | self-test ≥ 2/5 + setup.sh audit |

### Critérios de Saída

- [ ] SOUL.md com 5 seções + 7 Values
- [ ] 5 skills instaladas: self-test, prompt-log, stop-slop, taste-skill, exocortex-design-system
- [ ] MEMORY.md com log dos prompts 001-005 (gerado durante execução, não é semente)
- [ ] self-test ≥ 2/5
- [ ] **Drift audit:** setup.sh espelha o estado real (skills instaladas = skills no script)
- [ ] Configuration State = P2_MEMORY

→ Detalhes: `phases/P1_IDENTITY.md`

---

## P2: Memory — Acervo Cognitivo

> **Status:** Pendente
> **Prompts:** 006–012
> **Gate:** self-test ≥ 3/5
> **Depende de:** P1 completo

### Objetivo

Implementar o sistema de memória com arquitetura de 4 camadas **desde o início** (não como descoberta orgânica), usando `acervo-manager` como skill unificada.

### Diferenças do v1

1. **4 camadas (macro/global/micro/shared) desde o P0**, não descobertas durante execução.
2. **acervo-manager como skill única** (não 7 Nature skills + search).
3. **exocortex-new-microverso** com template completo (index.md, SCHEMA.md, 7 Natures).
4. **Wiki architecture** (index.md, promoção, archiving) nativa desde o início.

### Prompts

| ID | Propósito | Artefatos |
|---|---|---|
| 006 | Acervo Architecture + acervo-manager | Skill `acervo-manager` + estrutura 4 camadas |
| 007 | Macroverso Bootstrap | `acervo/macro/soul.md`, `valores.md`, `estilo.md` |
| 008 | Global Layer + Index | `acervo/global/index.md` + Natures universais |
| 009 | Microverso Template + new-microverso skill | `_template/` + `exocortex-new-microverso` |
| 010 | Shared Layer + Cross-refs | `acervo/shared/` + `groups.md` + `cross-refs/` |
| 011 | Smoke Test: Microverso CRUD | Criar → ler → buscar → deletar microverso de teste |
| 012 | P2 Checkpoint + Drift Audit | self-test ≥ 3/5 + setup.sh audit |

### Critérios de Saída

- [ ] `acervo-manager` funcional (READ/WRITE/SEARCH/PROMOTE/SCOPE)
- [ ] 4 camadas criadas e populadas (macro, global com index, micro com template, shared com groups)
- [ ] `exocortex-new-microverso` cria microverso completo a partir de template
- [ ] Smoke test CRUD passa
- [ ] self-test ≥ 3/5
- [ ] **Drift audit:** setup.sh + acervo structure espelham estado real

→ Detalhes: `phases/P2_MEMORY.md`

---

## P3: Behavior — Skills de Negócio

> **Status:** Pendente
> **Prompts:** 013–021
> **Gate:** self-test ≥ 4/5
> **Depende de:** P2 completo

### Objetivo

Implementar as regras de negócio do Exocórtex como skills comportamentais. **Sem MCPs.** Integrações externas ficam no BACKLOG.

### Diferenças do v1

1. **MCPs eliminados desta fase** → BACKLOG_INTEGRATIONS.md (D6).
2. **Tool governance simplificada** (sem MCPs para governar, foca em skills internas).
3. **Output Quality Gate** como skill comportamental que **usa** stop-slop/taste-skill (já instalados em P1).
4. **Bundle e Profiles** criados ao final da fase.

### Prompts

| ID | Propósito | Artefatos |
|---|---|---|
| 013 | Draft-First Protocol | `exocortex-draft-first` skill |
| 014 | Vetor Ativo (Classifier) | `exocortex-vetor-ativo` skill |
| 015 | Canvas Cognitivo (Extrator) | `exocortex-canvas` skill |
| 016 | Morning Briefing | `exocortex-briefing` skill |
| 017 | Onboarding Skill | `exocortex-onboarding` skill (v1.1 — sem auto-provisioning) |
| 018 | Output Quality Gate | `exocortex-output-quality-gate` skill |
| 019 | Tool Governance | `exocortex-tool-governance` skill (scope interno) |
| 020 | Bundle + Profiles | `exocortex-alpha` bundle + profiles `exec`/`evol` |
| 021 | P3 Checkpoint + Drift Audit | self-test ≥ 4/5 + setup.sh audit + bundle validation |

### Critérios de Saída

- [ ] 7 skills comportamentais instaladas e listadas
- [ ] Bundle `exocortex-alpha` carrega todas as skills
- [ ] Profiles `exec` e `evol` funcionais
- [ ] Testes comportamentais básicos: draft-first, vetor-ativo, canvas, briefing
- [ ] self-test ≥ 4/5
- [ ] **Drift audit:** bundle lista = skills instaladas = setup.sh

→ Detalhes: `phases/P3_BEHAVIOR.md`

---

## P4: Validation — Testes e Qualidade

> **Status:** Pendente
> **Prompts:** 022–026
> **Gate:** self-test = 5/5, smoke tests 7/7
> **Depende de:** P3 completo

### Objetivo

Bateria completa de testes que validam o sistema inteiro como unidade funcional. Nenhuma nova skill é criada — apenas testes.

### Diferenças do v1

1. **Fase dedicada a testes** (v1 misturava testes com criação de skills).
2. **Quality gate testado formalmente** (stop-slop scoring + taste-skill pre-flight).
3. **Drift audit final** antes da graduação.

### Prompts

| ID | Propósito | Resultado Esperado |
|---|---|---|
| 022 | Smoke Test: Microverso CRUD | Microverso criado → dados escritos → buscados → deletado |
| 023 | Smoke Test: Draft-First | "Envie email" → gera DRAFT, não envia |
| 024 | Smoke Test: Vetor de Evolução | "O que eu deveria considerar?" → perguntas socráticas |
| 025 | Smoke Test: Briefing Cross-Microverso | Briefing consolida dados de múltiplos microversos |
| 026 | Smoke Test: Quality Gates | Prosa ≥ 35/50 (stop-slop) + Visual sem falhas (taste-skill) |

### Critérios de Saída

- [ ] 5 smoke tests passam
- [ ] self-test = 5/5
- [ ] Output Quality Gate funcional (prosa + visual)
- [ ] **Drift audit final:** estado real do sistema = setup.sh = PLAN.md
- [ ] Zero skills fantasma (listadas mas não funcionais)
- [ ] Configuration State = P5_PRODUCTION

→ Detalhes: `phases/P4_VALIDATION.md`

---

## P5: Production — Golden Image

> **Status:** Pendente
> **Prompts:** 027 (único)
> **Gate:** Todos os critérios anteriores + golden image exportável
> **Depende de:** P4 completo

### Objetivo

Estado final. O Hermes agora **é** o Exocórtex.IA e está pronto para uso real ou para servir como golden image consumida pelo Provisioner Agent.

### Diferenças do v1

1. **P5 = P6 do v1** (absorveu o estado final — P6 era redundante).
2. **Golden image inclui setup.sh definitivo** que reproduz tudo.
3. **BACKLOG_INTEGRATIONS.md** atualizado com estado final.
4. **Personal Artifact Workspace** documentado como addendum pós-graduação: publicação de documentos, PDFs, planilhas, HTML, imagens e ZIPs no Drive privado do usuário, com fonte/assets/manifest/receipt no Acervo.

### Prompt

| ID | Propósito | Resultado |
|---|---|---|
| 027 | Graduação + Export | Configuration State = PRODUCTION + setup.sh final + BACKLOG atualizado |

### Estado Final Esperado

#### Skills (14 core + 1 externa no bundle quando disponível)

| Skill | Categoria | Fase de Instalação |
|---|---|---|
| `exocortex-self-test` | Core | P1 |
| `exocortex-prompt-log` | Core | P1 |
| `stop-slop` | Quality | P1 |
| `taste-skill` | Quality | P1 |
| `exocortex-design-system` | Quality | P1 |
| `acervo-manager` | Memory | P2 |
| `exocortex-new-microverso` | Memory | P2 |
| `exocortex-draft-first` | Behavior | P3 |
| `exocortex-vetor-ativo` | Behavior | P3 |
| `exocortex-canvas` | Behavior | P3 |
| `exocortex-briefing` | Behavior | P3 |
| `exocortex-onboarding` | Behavior | P3 |
| `exocortex-output-quality-gate` | Behavior | P3 |
| `exocortex-tool-governance` | Behavior | P3 |

**Ferramentas externas** (opcionais, dependem de tooling no host):
- `browser-use` — incluso no bundle, requer `browser-use.sh` funcional
- `duckduckgo-search` — MCP externo, não tem seed em artifacts/

#### Profiles
- `exec` — Vetor de Execução
- `evol` — Vetor de Evolução

#### Acervo
```
acervo/
├── macro/          # soul.md, valores.md, estilo.md
│   └── assets/     # Logo, favicon, identidade visual
├── global/         # index.md, DESIGN.md + contratos/tools globais
├── micro/          # {slug}/ por domínio
│   └── _template/  # Template de microverso (com DESIGN.md override)
├── shared/         # cross-refs/, groups.md
└── _artifacts/     # Pacotes operacionais de artefatos finais (source/assets/exports/manifest/receipt)
```

`_artifacts/` não substitui a ontologia do Acervo. Ele guarda pacotes de trabalho e publicação. Quando o artefato gerar conhecimento, decisão ou contrato, o microverso registra uma página semântica apontando para o `artifact_id`.

#### Personal Artifact Workspace

Capacidade pós-graduação documentada em `ARTIFACT_WORKSPACE.md`:

- fontes em `source/`, preferencialmente Markdown;
- assets relativos em `assets/`;
- exports finais em `exports/`;
- `manifest.json` como rastreabilidade local;
- `receipt.{provider}.json` como prova de publicação;
- Google Drive privado via OAuth local como provider inicial;
- Draft-First para links públicos, compartilhamento externo e envio.

→ Detalhes: `phases/P5_PRODUCTION.md` e `ARTIFACT_WORKSPACE.md`

---

## Mecanismo de Drift Audit (Novo em v2)

Cada fase termina com um **drift audit** — verificação automatizada de que o estado real do sistema corresponde ao que o plano e o setup.sh declaram.

### Procedure

```bash
# 1. Skills declaradas no PLAN vs. instaladas no Hermes
EXPECTED=$(grep -c "skill" plan_phase_file)
ACTUAL=$(hermes skills list | wc -l)
# Se EXPECTED != ACTUAL → DRIFT detectado

# 2. setup.sh reproduz o estado?
# Executar setup.sh em /tmp/hermes-test e comparar com HERMES_HOME

# 3. MEMORY.md tem entries para todos os prompts da fase?
PROMPTS_EXECUTED=$(grep -c "PDD-" MEMORY.md)
PROMPTS_EXPECTED=$(fase_prompt_count)
```

### Output do Audit

```markdown
## Drift Audit — Phase P{N}
| Check | Expected | Actual | Status |
|---|---|---|---|
| Skills count | {N} | {N} | ✅/❌ |
| setup.sh sync | match | match/drift | ✅/❌ |
| MEMORY.md entries | {N} | {N} | ✅/❌ |
| Bundle contains all | {list} | {list} | ✅/❌ |
```

### Regra de Bloqueio

Se o drift audit falhar, a fase **não avança**. O agente deve:
1. Identificar a causa do drift
2. Corrigir (atualizar setup.sh, instalar skill faltante, etc.)
3. Re-executar o audit
4. Só então avançar

---

## Contagem Total de Prompts

| Fase | Prompts | Range |
|---|---|---|
| P0 | 0 (manual) | — |
| P1 | 5 | 001–005 |
| P2 | 7 | 006–012 |
| P3 | 9 | 013–021 |
| P4 | 5 | 022–026 |
| P5 | 1 | 027 |
| **Total** | **27** | |

v1 tinha 31 prompts. v2 reduz para 27 eliminando MCPs do fluxo principal e consolidando Natures.

---

## Referências

- `RETROSPECTIVE.md` — Análise de drift v1 → v2
- `PLAYBOOK.yaml` — Protocolo de execução + agent_protocol
- `ARTIFACT_WORKSPACE.md` — Addendum pós-graduação para publicação de artefatos finais no Drive do usuário
- `plans/pdd/` — Plano v1 completo (read-only, referência histórica)
- `docs/exocortex.ia/03_framework.md` — Framework conceitual
- `.hermes/` — Artefatos de runtime do v1 (golden image atual)
