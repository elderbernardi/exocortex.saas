# EX-06 / WELCOME / Canvas — alinhamento semântico de Macroverso, Microversos e Tarefa

Status: draft
Tipo: evolução de filosofia + ajuste de harness
Escopo: WELCOME, README, onboarding e excrtx-behavior-canvas

## Contexto

A formulação histórica do WELCOME dizia:
- Macroverso = quem você é
- Microverso = onde você está agora
- Tarefa = o que precisa ser feito

Isso abriu margem para uma leitura errada: tratar Microverso como “sala”.

A filosofia corrigida é:
- Macroverso = quem fala
- Microversos = entidades semânticas e operacionais vivas, autocontidas, que ancoram e apoiam a tarefa
- Tarefa = sala operacional concreta onde a execução acontece

Consequência prática:
- uma tarefa pode ter 1 microverso principal
- pode ter N microversos secundários de apoio
- cruzamento entre microversos é permitido
- compartilhamento nunca é livre por default; deve respeitar as regras de sharing de cada microverso
- regra de precedência: `allow` sempre sobrescreve `deny`
- exemplo: `deny: [ALL]` + `allow: [microverse_x]` significa que o microverso fica shared somente com `microverse_x`
- `shared/` contém síntese cross-domain, não fusão cega de conteúdo

## Problema

O Canvas Cognitivo v0.4 modelava microversos, mas não impunha de forma explícita:
- distinção entre Microverso e Tarefa
- status do Macroverso
- microverso principal vs microversos de apoio
- restrições de compartilhamento em tarefas cross-domain, resolvidas a partir das regras allow/deny dos microversos

Isso permite respostas “úteis” mas fora do contrato filosófico do Exocórtex.

## Objetivo

Tornar a tríade Macroverso → Microversos → Tarefa executável no harness e ensinável no onboarding, sem drift semântico.

## Mudanças propostas

### 1. Filosofia / documentação
- Atualizar `acervo/global/knowledge/WELCOME.md`
- Atualizar `README.md`
- Atualizar fluxo de onboarding e bootstrap tutor

### 2. Harness / Canvas
Adicionar ao Canvas campos explícitos para:
- `macroverso.status`
- `macroverso.sources`
- `macroverso.constraints`
- `microversos.status`
- `microversos.primary`
- `microversos.related`
- `microversos.rationale`
- `microversos.sharing_constraints`
- `task.anchor`

### 3. Regras de comportamento
- Microverso nunca pode ser descrito como sala
- Tarefa é a sala operacional
- Em tarefas cross-domain, declarar sempre:
  - microverso principal
  - microversos de apoio
  - restrições de compartilhamento derivadas das regras do microverso
- Aplicar a precedência `allow > deny` em toda resolução de sharing constraint
- Se o Macroverso estiver placeholder ou missing, isso precisa aparecer explicitamente no canvas

## Critérios de aceite

- [ ] WELCOME explica que Microversos não são salas
- [ ] WELCOME explica que a tarefa é a sala operacional
- [ ] README reflete a nova semântica
- [ ] onboarding ensina a distinção corretamente
- [ ] Canvas declara microverso principal e secundários
- [ ] Canvas considera sharing constraints em tarefas cross-domain
- [ ] Canvas resolve sharing constraints usando regras allow/deny do microverso
- [ ] `allow` sobrescreve `deny` em todos os exemplos e testes
- [ ] Canvas declara `macroverso.status`
- [ ] EX-06 em `FEATURES.md` descreve a tríade atualizada

## Testes sugeridos

1. Pedido em domínio único
- Esperado: 1 microverso principal, nenhum secundário

2. Pedido cross-domain
- Esperado: 1 principal, 1+ secundários, sharing constraints explícitas

2b. Pedido com sharing restrito
- Configuração: `deny: [ALL]` + `allow: [microverse_x]`
- Esperado: o canvas declara que o microverso só pode compartilhar contexto com `microverse_x`

3. Macroverso placeholder
- Esperado: `macroverso.status=placeholder`

4. Pedido ambíguo
- Esperado: canvas exposto com lacuna clara entre tarefa e microverso

## Estado atual

Mudanças documentais e patch inicial do Canvas já aplicados localmente no repositório fonte de verdade.

## Próximo passo recomendado

Adicionar teste de regressão do EX-06 para impedir que futuras respostas voltem a tratar Microverso como sala.
