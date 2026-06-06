# DRAFT Issue — EX-06 precisa ancorar tarefa na tríade Macroverso → Microversos → Tarefa e resolver sharing constraints por allow/deny

Status: DRAFT local. Não publicar sem comando explícito.

## Feature

EX-06 — Canvas Cognitivo

## Prioridade

P1

## Contexto

A formulação anterior do sistema abria espaço para uma leitura errada:
- Macroverso = quem você é
- Microverso = onde você está agora
- Tarefa = o que precisa ser feito

Na prática, isso permitiu tratar Microverso como “sala”.

A filosofia correta é:
- Macroverso = quem fala
- Microversos = entidades semânticas e operacionais autocontidas, vivas, que ancoram e apoiam a tarefa
- Tarefa = sala operacional concreta onde a execução acontece

Além disso, tarefas cross-domain não podem compartilhar contexto livremente. As sharing constraints devem ser resolvidas a partir das regras de cada microverso, com a regra de precedência:
- `allow` SEMPRE sobrescreve `deny`

Exemplo canônico:
- `deny: [ALL]`
- `allow: [microverse_x]`

Significado:
- o microverso só pode ser compartilhado com `microverse_x`

## Problema

O Canvas Cognitivo v0.4 não impunha de forma suficiente:
- distinção explícita entre Microverso e Tarefa
- status explícito do Macroverso
- separação entre microverso principal e microversos de apoio
- resolução de sharing constraints a partir das regras allow/deny dos microversos

Isso permite respostas úteis, mas semanticamente fora do contrato do Exocórtex.

## Comportamento esperado

Para inputs complexos, o Canvas deve:
- declarar `macroverso.status`
- declarar `microversos.primary`
- declarar `microversos.related`
- declarar `task.anchor`
- deixar explícito que a tarefa é a sala operacional
- resolver `microversos.sharing_constraints` com base nas regras de sharing do microverso
- aplicar sempre `allow > deny`

## Comportamento observado

Antes do ajuste, a filosofia do WELCOME e o schema do Canvas não estavam totalmente alinhados. O sistema podia:
- ativar microversos sem explicitar a tarefa como sala
- cruzar domínios sem declarar sharing constraints
- omitir Macroverso como campo formal do Canvas

## Proposta

1. Atualizar a semântica do WELCOME e README
2. Patchar `excrtx-behavior-canvas` com campos estruturais da tríade
3. Incluir `microversos.sharing_constraints`
4. Tornar explícita a precedência `allow > deny`
5. Adicionar regressão determinística e smoke test para EX-06

## Critérios de aceite

- [ ] WELCOME afirma que Microverso não é sala
- [ ] WELCOME afirma que a tarefa é a sala operacional
- [ ] Canvas exige `macroverso.status`
- [ ] Canvas distingue microverso principal de secundários
- [ ] Canvas inclui `microversos.sharing_constraints`
- [ ] Canvas resolve sharing constraints a partir de regras allow/deny
- [ ] `allow` sobrescreve `deny` em exemplos, documentação e testes
- [ ] Harness EX-06 falha se a distinção Microverso/Tarefa desaparecer
- [ ] Harness EX-06 falha se sharing constraints não forem explicitadas em cenário cross-domain

## Casos de teste

1. Domínio único
- input: pedido ancorado em um único microverso
- esperado: 1 principal, nenhum secundário

2. Cross-domain simples
- input: tarefa entre gabinete e jurídico
- esperado: 1 principal, 1 secundário, tarefa explicitada como sala operacional

3. Cross-domain com sharing restrito
- input: jurídico com `deny: [ALL]` e `allow: [gabinete]`
- esperado: Canvas declara que jurídico só pode compartilhar contexto com gabinete

4. Macroverso placeholder
- esperado: `macroverso.status=placeholder`

## Artefatos locais

- `acervo/global/knowledge/WELCOME.md`
- `README.md`
- `skills/excrtx-behavior-canvas/SKILL.md`
- `skills/excrtx-onboard-welcome/SKILL.md`
- `skills/excrtx-onboard-welcome/references/bootstrap-macro-tutor.md`
- `scripts/test-registry.sh`
- `docs/harness/ex-06-context-anchor-semantic-update.md`
