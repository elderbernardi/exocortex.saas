# Microverso: Exocortex Ops

Type: `domain`

Descrição: domínio canônico para setup, operação, manutenção, diagnóstico, integrações e evolução do próprio Exocórtex.IA sobre Hermes Agent.

## Escopo

O Exocortex Ops guarda conhecimento operacional sobre o próprio sistema: instalação, perfis, ferramentas, memória, microversos, integrações, providers, rotinas de manutenção, self-checks e decisões de governança.

Ele não guarda contexto pessoal do executivo nem conteúdo de projetos atendidos. Esses dados pertencem ao Macroverso ou aos microversos específicos. Aqui ficam método, estado técnico, contratos e decisões operacionais do Exocórtex.

## Tipo

`domain`: capacidade funcional permanente.

## Relação com outros microversos

- Atua como microverso-base de operações internas.
- Pode referenciar outros microversos apenas para manutenção estrutural, saúde, roteamento e governança.
- Não copia conhecimento de domínio atendido; usa `shared/cross-refs/` quando houver dependência transversal.
- É o lugar correto para decisões sobre setup replicável, runtime Hermes, providers de memória, skills, MCPs, DocBrain, NotebookLM, gateway, cron e harness.

## Contratos locais

1. Estado antes de ação: verificar runtime, paths e configuração antes de alterar.
2. Draft-First para setup executável, comunicação externa, documentos compartilhados, commits, deploys e mudanças irreversíveis.
3. Nenhuma mutação silenciosa em `setup.sh`, perfis, providers, cron, skills ou MCPs.
4. Registrar decisões operacionais relevantes em `decisions/`.
5. Registrar procedimentos reutilizáveis em `workflows/` ou `skills/`, não em memória solta.
6. Preservar isolamento entre profiles Hermes.
7. Corrigir drift entre skill, documentação e runtime quando detectado.

## Taxonomia inicial

- `setup`: instalação, bootstrap e reprodutibilidade.
- `runtime`: Hermes Agent, perfis, config, toolsets, providers e gateway.
- `memory`: acervo, Hindsight, built-in memory, session search e providers.
- `integration`: DocBrain, NotebookLM, Google Drive, MCPs, browser e serviços auxiliares.
- `maintenance`: health checks, self-tests, auditoria, limpeza e pendências.
- `governance`: Draft-First, approvals, escopo, segurança e isolamento.
- `drift`: divergência entre contrato, skill, docs e runtime real.

## Lint local

- Não registrar segredos, tokens ou chaves.
- Não transformar bug temporário em regra permanente sem confirmação.
- Não registrar dados pessoais do executivo; remeter ao Macroverso.
- Não registrar conteúdo de cliente/projeto; remeter ao microverso correspondente.
- Não alterar setup executável sem DRAFT e aprovação explícita.
