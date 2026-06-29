# [META][P0] Acervo MCP Control Plane — Consolidação do plano de controle semântico do Acervo

## Contexto

O Acervo já possui separação estrutural forte por `macro`, `global`, `micro` e `shared`, com frontmatter canônico, validação e logging. O que ainda não existe é uma **autoridade operacional única** para mutações semânticas agentic.

Hoje, a política de escrita está espalhada entre scripts, skills, documentação e convenções. Isso cria drift entre a semântica desejada e a implementação real.

A ADR `acervo/micro/exocortex-dev/decisions/adr-022-acervo-mcp-control-plane.md` fixou a tese arquitetural:

- filesystem = verdade física
- core semântico local = verdade operacional
- `acervoctl` = superfície local oficial
- `acervo-mcp` = superfície agentic oficial

O plano local que detalha a evolução está em:

- `.hermes/plans/2026-06-28_174717-acervo-mcp-control-plane.md`

## Objetivo

Transformar o Acervo em um sistema semântico operável por agentes sem perder auditabilidade humana e liberdade de arquivo para infraestrutura/manutenção.

Em termos práticos, esta iniciativa deve entregar:

1. um **core local** para mutação semântica
2. uma **CLI oficial** (`acervoctl`)
3. um **servidor MCP fino** sobre o mesmo core
4. migração gradual dos fluxos reais do repositório para esse caminho oficial

## Estratégia

A ordem é obrigatória. Não começar pelo servidor MCP.

1. **Autoridade** — congelar o contrato e as exceções
2. **Core** — extrair a regra operacional para uma library local
3. **CLI** — provar localmente o contrato de `prepare/commit`
4. **MCP** — expor o core sem duplicar regra
5. **Migração** — mover os primeiros clientes reais
6. **Governança** — alinhar skills, README e política de uso
7. **Hardening** — consolidar testes ponta a ponta e falhas esperadas

## Plano

### Fase 0 — autoridade e invariantes
- [x] registrar a autoridade semântica no repositório
- [x] atualizar o `mcp-registry` com `acervo` em `planned`
- [x] alinhar `README.md` e ADR-006 com a nova regra
- [x] deixar inequívoco quem pode escrever direto e quem deve usar o plano de controle

### Fase 1 — semantic core
- [x] criar `scripts/acervo_semantic_core.py`
- [x] centralizar resolução de `$ACERVO`, microverso ativo, scope guard, validate, index/log, receipt
- [x] cobrir o core com testes dedicados

### Fase 2 — CLI local
- [x] criar `scripts/acervoctl.py`
- [x] expor `list-microversos`, `search`, `prepare-write`, `commit-write`, `validate-frontmatter`, `export-microverso`
- [x] fixar saída JSON estável para `prepare` e `commit`

### Fase 3 — gates e validadores
- [ ] endurecer `validate_frontmatter.py` e `validate_log.py`
- [ ] transformar `log.md` e `index.md` em contrato executável, não só convenção

### Fase 4 — servidor MCP
- [x] criar `scripts/acervo_mcp_server.py`
- [x] expor apenas operações semânticas
- [x] garantir paridade funcional com `acervoctl`

### Fase 5 — registro e setup
- [x] registrar `acervo` via `hermes mcp add`
- [x] adicionar health check no setup/final verification
- [x] documentar modo degradado

### Fase 6 — migração dos primeiros clientes
- [x] migrar `scripts/docbrain_to_acervo.py`
- [x] atualizar `excrtx-memory-manager` e `excrtx-integrate-docbrain`

### Fase 7 — governança
- [x] consolidar a política de uso em skills, README e seed comportamental
- [x] declarar explicitamente as exceções de escrita direta

### Fase 8 — hardening
- [ ] teste ponta a ponta `prepare -> commit -> validate -> index/log`
- [ ] caso negativo de cross-microverso
- [ ] nota interna de rollout

## Dependências explícitas

- Esta issue **governa** a implementação do Acervo MCP Control Plane.
- O servidor MCP depende do core local e da CLI.
- A migração dos clientes reais depende da estabilização do core.
- O enforcement de comportamento depende de a política estar documentada primeiro.

## Relação com issues adjacentes

- **#114** cobre o runtime do DocBrain (`api health`, build, env e smoke do parser). É pré-condição operacional do pipeline documental, mas **não** é a issue de governança do Acervo MCP.
- **#115** cobre o adaptador DocBrain → Acervo. Nesta iniciativa, ele entra como primeiro cliente real migrado para o control plane oficial.
- **#121** continua sendo a META correta para autoridade, CLI, MCP, migração e governança do Acervo.

## Definition of Done

Fechar esta META somente quando os pontos abaixo forem verdadeiros ao mesmo tempo:

- [ ] existe um core local funcional sem depender de MCP
- [ ] existe uma CLI local verificável para `prepare` e `commit`
- [ ] existe um servidor MCP fino com paridade comportamental com a CLI
- [x] pelo menos um cliente real usa o novo caminho oficial
- [x] a política de uso está coerente entre ADR, README, skills e registro de MCPs
- [ ] há testes cobrindo sucesso e falha de `scope`, `frontmatter`, `index`, `log` e `cross-microverso`

## Notas para agentes menores

- Não tratar MCP como editor genérico de arquivos.
- Não duplicar regra entre core, CLI e servidor.
- Não inventar enforcement técnico total antes de ele existir.
- Preservar a liberdade de arquivo do humano, da infra e da manutenção corretiva.
- Se houver dúvida entre elegância protocolar e governança semântica, a governança vence.

## Arquivos de referência

- `acervo/micro/exocortex-dev/decisions/adr-022-acervo-mcp-control-plane.md`
- `.hermes/plans/2026-06-28_174717-acervo-mcp-control-plane.md`
- `acervo/micro/exocortex-ops/knowledge/mcp-registry.md`
- `acervo/micro/exocortex-dev/decisions/skill-vs-mcp-selection.md`
- `README.md`
