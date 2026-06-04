# DRAFT — Candidate Release de Consolidação do Exocórtex.IA
## Plano de Setup + Prompt Changelog + Decisões para Aprovação Executiva

> **Versão:** 0.1 (DRAFT)
> **Status:** Proposta para aprovação executiva
> **Branch:** consolidation/candidate-release
> **Fonte da Verdade:** Harness v0.4 (acervo/micro/harness-project/knowledge/exocortex-harness-v0.4/)
> **Inventário consolidado em:** consolidation/inventory/
> **Matriz de aspectos:** consolidation/MATRIX_ASPECTS.md

---

## Sumário Executivo

Este documento consolida o plano de setup do Exocórtex.IA sobre Hermes Agent em versão candidate-release. A consolidação partiu do **Harness v0.4** como fonte de verdade, foi comparada contra:
- O plano PDD v2 (plans/pdd_v2/)
- Os artefatos do projeto (setup.sh, SOUL.md, DECISIONS.md, etc.)
- Os microversos hermes-setup e harness-project no Acervo

**Resultado geral:** as fontes estão majoritariamente em **sinergia** (✅ compatível). Nenhum conflito crítico foi encontrado. As diferenças são principalmente de granularidade e escopo.

**Principais itens que requerem decisão executiva:**
1. Formato de deployment (PDD + hardcopy vs abordagem baseada em memórias)
2. Estruturação de Rotinas, Tarefas e Automações como artefatos canônicos
3. Formalização das personas Professor, Cientista e Zelador de Skills
4. Priority de implementação entre os 8 steps do setup-plan vs as 6 fases do PDD v2

---

## Parte 1 — Plano de Setup Consolidado (Candidate-Release)

### Estrutura Híbrida Proposta

Reconciliando as duas abordagens existentes:

| PDD v2 Phase | Setup-Plan Step | Propósito |
|-------------|----------------|-----------|
| **P0 Foundation** | Etapa 1 + Etapa 2 + Etapa 3 (parcial) | Pré-requisitos, diretórios operacionais, templates, agent_protocol |
| **P1 Identity** | Etapa 5 (skill identity) + SOUL.md | Identidade, quality skills, self-test, prompt-log |
| **P2 Memory** | Etapa 1 + Etapa 2 + Etapa 3 (acervo) | Acervo 4 camadas, acervo-manager, microverso template |
| **P3 Behavior** | Etapa 3 + Etapa 4 | Skills comportamentais, ferramentas, bundle, profiles |
| **P4 Validation** | Etapa 7 (critérios de aceite) | Smoke tests, quality gate, drift audit |
| **P5 Production** | Etapa 6 + Etapa 8 | Golden image, política de publicação, não-fazer |

**Fase Adicional (Proposta — Estudo de Deployment):**
| **P0.5** | Anterior a P1 | Estudar métodos de deployment e acoplamento com Hermes |
| **Study** | | Conforme sugestão do executivo |

### Requisitos Preservados (da fonte canônica)

1. ✅ **Identidade**: Exocórtex.IA roda sobre Hermes Agent. Hermes é infraestrutura; Exocórtex é contrato cognitivo.
2. ✅ **Acervo v2**: Fonte canônica semântica com 4 camadas (macro/global/micro/shared).
3. ✅ **Canvas**: Forma estruturada da intenção, com persistência em canvas.yaml.
4. ✅ **Tarefa**: Intenção do usuário persistida em acervo/_tasks/{task_id}/.
5. ✅ **Artefato**: Entrega reprodutível em acervo/_artifacts/items/{artifact_id}/.
6. ✅ **Quality Gate**: Piso mínimo de segurança, completude e verificabilidade.
7. ✅ **Draft-First**: Toda ação externa como DRAFT antes de execução.
8. ✅ **Vetores**: Evolução, Execução e Manutenção como três vetores de alto nível.
9. ⚠️ **Rotina**: Definida no canônico mas não implementada explicitamente. Decisão pendente.
10. ⚠️ **Automação**: Definida no canônico mas não implementada explicitamente. Decisão pendente.
11. ⚠️ **Personas**: Professor, Cientista e Zelador de Skills definidas no canônico mas não formalizadas no projeto. Decisão pendente.

### Skills já formalizadas (validadas contra canônico)

- exocortex-self-test (core)
- exocortex-prompt-log (core)
- exocortex-vetor-ativo (behavior)
- exocortex-canvas (behavior)
- exocortex-draft-first (behavior)
- exocortex-briefing (behavior)
- exocortex-onboarding (behavior)
- exocortex-output-quality-gate (behavior)
- exocortex-tool-governance (behavior)
- acervo-manager (memory)
- exocortex-new-microverso (memory)
- exocortex-design-system (quality)
- stop-slop (quality)
- taste-skill (quality)
- browser-use (external)

### Skills candidatas (não implementadas, mencionadas em fontes)

- exocortex-harness-v0.4 (skill de ponta a ponta, mencionada no setup-plan)
- exocortex-frontend-slides (presente no PDD v2 artifacts)
- personal-artifact-workspace (mencionada no setup-plan)
- personal-intake-workspace (mencionado em decisões)

---

## Parte 2 — Changelog de Prompts e Configurações

### Prompts PDD v2 (001-027) — Status de Validação Contra Canônico

| ID | Nome | Status vs Canônico | Observação |
|----|------|--------------------|------------|
| 001 | Bootstrap self-test | ✅ Validado | Alinhado com quality gate |
| 002 | Core Identity | ✅ Validado | SOUL.md compatível com identidade canônica |
| 003 | Behavioral Boundaries | ✅ Validado | Draft-First e vetores alinhados |
| 004 | Prompt Log + Quality | ✅ Validado | Quality skills alinhadas |
| 005 | P1 Checkpoint + Drift | ✅ Validado | Drift audit como extensão válida |
| 006 | Acervo Architecture | ✅ Validado | 4 camadas + acervo-manager alinhados |
| 007 | Macroverso Bootstrap | ✅ Validado | Compatível |
| 008 | Global Layer + Index | ✅ Validado | Natures universais alinhadas |
| 009 | Microverso Template | ✅ Validado | Template + new-microverso skill |
| 010 | Shared Layer + Cross-refs | ✅ Validado | Compatível |
| 011 | Smoke Test CRUD | ⚠️ Requerer revisão | Validar contra estrutura do acervo v2 |
| 012 | P2 Checkpoint + Drift | ✅ Validado | Compatível |
| 013-019 | Behavior Skills | ✅ Validado | Draft-First, Vetor-Ativo, Canvas, Briefing, Onboarding, Quality Gate, Tool Governance |
| 020 | Bundle + Profiles | ✅ Validado | Profiles exec/evol + bundle exocortex-alpha |
| 021-026 | Validation Prompts | ✅ Validado (pending smoke test) | Smoke tests e drift audit |
| 027 | Production / Golden Image | ⚠️ Requerer revisão | Necessita integração com política de publicação do setup-plan |

**Alerta de Drift Potencial:** Os seguintes prompts não foram verificados diretamente contra o canônico porque o conteúdo detalhado deles está nos arquivos de fase (phases/P*.md) que não foram inventariados na totalidade. Recomenda-se revisão individual na implementação:
- 011 (CRUD smoke test)
- 027 (Golden image / Production)

### Configurações Chave (setup.sh)

O setup.sh atual (raiz do projeto) e o do PDD v2 (artifacts/setup.sh) precisam ser:
1. Comparados para detectar diferenças (não inventariado em detalhe)
2. Atualizados para refletir a estrutura operacional do canônico (_tasks/, _routines/, _automations/, _artifacts/items/)
3. Sincronizados com as skills declaradas no PDD v2

---

## Parte 3 — Registro de Decisões Pendentes

### D001 — Formato de Deployment (CRÍTICA)

**Contexto:** Atualmente usamos hardcopy de artefatos + PDD (prompt-driven development). O executivo sugere que PDD é uma garantia contra drift em atualizações sérias do Hermes e personalização baseada em memória, mas não é verdade canônica.

**Opções:**
- **A) PDD puro**: Manter a abordagem PDD v2 como está. Setup.sh + prompts = golden image.
- **B) PDD + skills de memória**: Evoluir PDD para usar as skills de memória do Hermes (Honcho, Mem0, etc.) como mecanismo de personalização, mantendo PDD como fallback para setup limpo.
- **C) Híbrido baseado em setup-plan**: Adotar o setup-plan como workflow principal, usando PDD como referência de fases mas integrando memória operacional e skill-based state management.

**Opinião Exocórtex:** Recomendo **Opção C** (híbrido). O setup-plan é mais alinhado com o canônico e mais operável. PDD v2 serve como checklist de verificação. A camada de memória deve ser a base de personalização, não PDD.

**Decisão:** ⬜ Pendente

---

### D002 — Rotina e Automação como Entidades Formais

**Contexto:** O canônico define _routines/ e _automations/ no filesystem. O PDD v2 não implementa essas estruturas.

**Opções:**
- **A)** Criar _routines/ e _automations/ no setup, conforme canônico.
- **B)** Deixar rotinas e automações como conceitos implícitos, gerenciados via cronjobs and scripts avulsos.
- **C)** Adotar o sistema Kanban do Hermes como plataforma de automação, usando _automações como registros.

**Opinião Exocórtex:** Recomendo **Opção A** (criar logo). A estrutura _routines/ e _automations/ é leve, não conflita com Hermes, e garante rastreabilidade.

**Decisão:** ⬜ Pendente

---

### D003 — Personas Professor, Cientista e Zelador de Skills

**Contexto:** O canônico adiciona três personas. O projeto não as formalizou.

**Opções:**
- **A)** Criar skills específicas para cada persona (ex: exocortex-professor, exocortex-cientista, exocortex-zelador-de-skills).
- **B)** Mapear personas para habilidades existentes (ex: exocortex-output-quality-gate = Zelador de Skills).
- **C)** Adicionar ao SOUL.md como seção de personas, sem criar skills específicas.

**Opinião Exocórtex:** Recomendo **Opção B** (mapeamento). Personas são modos de ação, não scripts. Mapeá-las para skills existentes é mais limpo e evita poluição.

**Decisão:** ⬜ Pendente

---

### D004 — Prioridade: Setup-Plan vs PDD v2

**Contexto:** Setup-plan (8 etapas lineares) e PDD v2 (6 fases) divergem em sequenciamento.

**Opções:**
- **A)** Priorizar setup-plan sobre PDD v2 (setup-plan é canônico).
- **B)** Priorizar PDD v2 (mais detalhado, tem prompts).
- **C)** Usar a estrutura híbrida proposta na Parte 1.

**Opinião Exocórtex:** Recomendo **Opção C** (híbrida). Aproveita a granularidade do PDD v2 e a canonicidade do setup-plan.

**Decisão:** ⬜ Pendente

---

### D005 — Scripts de Ferramentas (Setup-Plan Etapa 4)

**Contexto:** O setup-plan lista 7 scripts (register_task_from_canvas.py, init_artifact_package.py, etc.). O PDD v2 não os implementa.

**Opções:**
- **A)** Implementar todos os 7 scripts como parte do candidate-release.
- **B)** Implementar apenas os críticos (register_task + init_artifact + validate_manifest) e deixar o restante para pós-release.
- **C)** Ignorar scripts e delegar essas funções para as skills do Hermes.

**Opinião Exocórtex:** Recomendo **Opção B** (apenas críticos). register_task, init_artifact e validate_manifest são essenciais para o fluxo Canvas → Tarefa → Artefato. O resto pode vir depois.

**Decisão:** ⬜ Pendente

---

### D006 — Memória Operacional vs PDD

**Contexto:** O executivo mencionou que PDD é "personalização baseada em memória conforme o agente é modelado".

**Opções:**
- **A)** Usar PDD como mecanismo primário de personalização (como é hoje).
- **B)** Explorar providers de memória do Hermes (built-in, Honcho, Mem0, etc.) para personalização dinâmica.
- **C)** Usar PDD para setup inicial + memória para evolução contínua.

**Opinião Exocórtex:** Recomendo **Opção C**. PDD é excelente para setup limpo/reproduzível. Memória é melhor para adaptação contínua. Essa combinação cobre ambos os cenários sem sobrescrever a verdade canônica.

**Decisão:** ⬜ Pendente

---

### D007 — Skills Faltantes (Backlog)

**Contexto:** O BACKLOG do projeto (BACKLOG_TEMPLATE.md, PLAYBOOK.yaml) lista possíveis skills futuras.

**Opções:**
- **A)** Revisar e priorizar o backlog como parte do candidate-release.
- **B)** Mover backlog para depois do release.
- **C)** Descartar backlog e revisar do zero após release.

**Opinião Exocórtex:** Recomendo **Opção B** (adiar). Foco no candidate-release. Backlog é importante mas não é crítico agora.

**Decisão:** ⬜ Pendente

---

## Parte 4 — Critérios de Aceite da Candidate-Release

Para que esta release seja considerada "consolidada e pronta para execução", os seguintes critérios devem ser atendidos:

1. [ ] **Decisões D001-D007 resolvidas** pelo executivo
2. [ ] **Setup.sh atualizado** para refletir a estrutura _tasks/, _routines/, _automations/, _artifacts/items/ do canônico
3. [ ] **Skills validadas**: todas as skills formalizadas estão funcionais e consistentes
4. [ ] **Matrix de aspectos finalizada** e aprovada pelo executivo
5. [ ] **Prompts revisados**: especialmente 011 (CRUD) e 027 (Production)
6. [ ] **Drift audit** entre setup.sh, skills instaladas e PDD v2 plan
7. [ ] **Self-test ≥ 5/5** no perfil de target
8. [ ] **Política de publicação definida** (alinhada com setup-plan Etapa 6)
9. [ ] **Plano de deployment e acoplamento estudado** conforme sugestão do executivo (P0.5)

---

## Parte 5 — Nota sobre Formato de Deployment e Próximos Passos

Conforme sugestão do executivo, **antes de iniciar o desenvolvimento**, devemos estudar quais métodos de deployment e acoplamento funcionam melhor com o Hermes.

**Questões a Investigar na P0.5 Study:**
1. **PDD puro vs skill-based**: O PDD funciona como blueprint, mas skills de memória (Honcho, Mem0, built-in) podem oferecer personalização mais rica. Qual a maturidade dessas opções?
2. **Acoplamento com Hermes**: O Exocórtex é uma configuração (não fork). Como garantir que upgrades do Hermes não quebrem o setup? Testes de integração?
3. **Docker vs nativo**: Docker oferece isolamento mas adiciona complexidade. Nativo é mais simples mas menos portável. Qual o cenário target?
4. **MCPs e provedores externos**: Qual a fronteira entre setup do Exocórtex e configuração de provedores externos?

**Recomendação:** Conduzir um estudo de 1-2 dias para responder essas questões, documentar como ADR no Acervo, e consolidar as respostas no plano candidate-release.

---

## Arquivos Produzidos nesta Consolidação

| Arquivo | Conteúdo |
|---------|----------|
| consolidation/inventory/canonical/ | Cópia dos módulos do Harness v0.4 |
| consolidation/inventory/project/ | Cópia do PDD v2 PLAN.md, SOUL.md, etc. |
| consolidation/inventory/microversos/ | Cópia dos microversos hermes-setup e harness-project |
| consolidation/MATRIX_ASPECTS.md | Matriz de 19 aspectos, classificados por fonte |
| plans/candidate-release/DRAFT_CANDIDATE_RELEASE.md | Este documento |

---

## Estado da Branch

- **Branch:** `consolidation/candidate-release`
- **Local:** /home/elder/projetos/pessoal/exocortex.saas/
- **Base:** main (atualizado na criação)
- **Conteúdo:** inventário + matriz + draft (sem alterações em arquivos canônicos existentes)

---

## Próximo Passo

✅ **Aguardar aprovação executiva das decisões D001-D007**

Após aprovação:
1. Consolidar respostas neste documento
2. Atualizar setup.sh e skills conforme decisões
3. Aplicar alterações nos arquivos canônicos (quando autorizado)
4. Executar P0.5 (estudo de deployment) como fase inicial
5. Executar fases P0 a P5 conforme prioridade decidida em D004
6. Verificar critérios de aceite

---

*Documento gerado pelo Exocórtex.IA sobre Hermes Agent em branch isolation consolidation/candidate-release. Nenhum arquivo canônico do Acervo ou do projeto foi alterado durante esta fase de consolidação.*
