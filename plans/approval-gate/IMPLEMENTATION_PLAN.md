# Plano de implementação — approval-gate Draft-First

> Escopo: transformar a proposta conceitual do approval-gate em plano executável por camadas, sem iniciar implementação antes da decisão arquitetural do executivo.

## Objetivo

Definir como o Exocórtex deve aplicar Draft-First com enforcement real na fronteira entre produção interna e emissão externa, preservando cron, background jobs, staging privado e a arquitetura USER -> GUI -> SERVER -> HERMES.

## Artefatos de referência

- `plans/DECISIONS.md` — ADR-013 proposta
- `plans/STATUS.md` — Q002 e Pending TODOs
- `~/.hermes/acervo/micro/hermes-setup/decisions/approval-gate-draft-first.md` — mini-ADR canônico
- `~/.hermes/acervo/micro/hermes-setup/contracts/exocortex-hermes-identity.md` — identidade Exocórtex sobre Hermes
- `~/.hermes/acervo/micro/hermes-setup/workflows/replicable-exocortex-setup.md` — setup reproduzível com pendência aberta

## Resultado esperado

Ao final da implementação, qualquer efeito externo relevante só deve acontecer quando existirem ao mesmo tempo:

1. um draft materializado;
2. um fingerprint calculado sobre o payload exato;
3. uma aprovação humana vinculada a esse fingerprint;
4. uma revalidação positiva no instante da emissão.

## Princípio estrutural

O gate não deve nascer só na interface. A GUI pode apresentar e coletar a aprovação. O SERVER pode coordenar fluxo e storage. O HERMES precisa continuar sendo o executor real da ação, mas com interceptação suficiente para impedir emissão externa fora do contrato.

## Camadas do plano

### Camada 1 — Taxonomia de side effects

Objetivo: definir o que o sistema considera emissão externa bloqueada.

Entregas:
- matriz de efeitos por ferramenta e operação;
- classificação mínima: `internal`, `staging_private`, `external_blocked`;
- primeira lista de operações bloqueadas:
  - send_message
  - email
  - calendar create/update
  - docs/drive compartilhamento externo
  - commit/push/merge/deploy
  - qualquer mudança de permissão pública

Decisões necessárias:
- se upload privado no Drive do próprio usuário entra como `staging_private` por padrão;
- se commit local sem push continua livre;
- como tratar geração de links temporários.

Risco principal:
- taxonomia estreita demais deixa vazamentos; taxonomia larga demais paralisa fluxos legítimos.

### Camada 2 — Fingerprint e máquina de estados

Objetivo: criar o contrato transacional do draft.

Entregas:
- esquema canônico de fingerprint;
- normalização de payload por tipo de canal;
- máquina de estados mínima:
  - `draft_created`
  - `draft_ready`
  - `approved`
  - `expired`
  - `emitted`
  - `cancelled`
  - `failed`
- regra de expiração automática quando qualquer campo material mudar.

Campos mínimos do fingerprint:
- tipo de efeito externo;
- canal;
- destinatário;
- assunto/título quando houver;
- corpo normalizado;
- anexos;
- links emitidos;
- permissões ou visibilidade;
- versão do artefato referenciado.

Decisões necessárias:
- algoritmo e serialização do fingerprint;
- se aprovação tem TTL;
- se pequenas mudanças cosméticas invalidam ou não o draft.

Risco principal:
- fingerprint permissivo demais aprova payload alterado; fingerprint rígido demais causa atrito operacional desnecessário.

### Camada 3 — Storage e receipts

Objetivo: manter trilha auditável e reproduzível.

Entregas:
- ledger local de drafts, aprovações e emissões;
- receipt antes da emissão e receipt final depois da emissão;
- referência cruzada com artifact workspace e staging privado quando houver arquivo.

Opções de storage a comparar:
1. SQLite local no plano do server;
2. storage interno do workspace Exocórtex;
3. solução híbrida: índice em SQLite + blobs/artefatos em diretório.

Dados mínimos por registro:
- draft_id;
- fingerprint;
- status;
- timestamps;
- ator da aprovação;
- canal/target;
- referência para artefato local;
- receipt de emissão ou motivo de falha.

Risco principal:
- guardar pouco e perder auditabilidade; guardar demais e misturar memória cognitiva com trilha transacional.

### Camada 4 — Interceptação no harness

Objetivo: decidir onde o bloqueio acontece de fato.

Opções a comparar:

1. Plugin no Hermes
- vantagem: enforcement perto da execução;
- custo: acoplamento com internals do Hermes e manutenção com upstream.

2. Camada server antes da tool call externa
- vantagem: separa política Exocórtex do runtime Hermes;
- custo: precisa mapear chamadas com precisão e não pode depender só da GUI.

3. Modelo híbrido
- server classifica e coordena;
- plugin Hermes revalida no último metro antes da emissão.

Recomendação atual:
- seguir com modelo híbrido como direção de desenho;
- evitar confiar só na GUI;
- evitar confiar só em prompt.

Critério de escolha:
- bloqueio deve continuar válido mesmo se mudar o canal de acesso do usuário;
- aprovação deve sobreviver à troca de interface, mas não à troca de payload.

### Camada 5 — GUI e experiência de aprovação

Objetivo: desenhar a experiência humana sem enfraquecer o controle.

Entregas:
- tela ou card de revisão do draft;
- exibição legível de alvo, canal, corpo, anexos e impacto;
- ação explícita de aprovar, cancelar ou pedir revisão;
- exposição de fila de drafts pendentes.

Princípios:
- a GUI mostra o draft humano, não detalhes técnicos desnecessários;
- o backend vincula a aprovação ao fingerprint invisível ao usuário;
- alteração posterior no draft invalida a aprovação anterior.

Risco principal:
- UX ruim leva o operador a buscar atalhos fora do fluxo governado.

### Camada 6 — Cron, background jobs e staging privado

Objetivo: preservar autonomia onde ela é legítima.

Entregas:
- regra de parada em `draft_ready` para jobs que terminariam em emissão externa;
- contrato para staging privado permitido;
- fila de pendências que o executivo pode revisar depois.

Regras propostas:
- cron pode pesquisar, consolidar, gerar arquivos e preparar drafts;
- cron não envia externamente sem aprovação vinculada;
- background job pode produzir artifacts, manifests e receipts locais;
- publicação ou compartilhamento externo sempre passa pelo gate.

Risco principal:
- bloquear tarefas cedo demais e matar o valor de automação interna.

### Camada 7 — Testes adversariais e validação

Objetivo: provar que o gate falha fechado.

Entregas:
- suíte de testes com casos positivos e negativos;
- cenários por canal e por tipo de side effect;
- teste de regressão para drift entre aprovação e payload emitido.

Casos mínimos:
- aprovar draft A e tentar emitir draft B;
- aprovar mensagem sem anexo e emitir com anexo;
- aprovar target X e emitir target Y;
- aprovar canal Telegram e emitir email;
- cron concluir em `draft_ready` sem travar o run;
- staging privado permitido sem liberar compartilhamento externo.

Critério de aceite:
- nenhuma emissão externa relevante passa sem approval binding válido.

## Sequência recomendada

### Fase A — modelagem
1. fechar taxonomia de side effects;
2. fechar fingerprint;
3. fechar máquina de estados;
4. escolher arquitetura de interceptação.

### Fase B — infraestrutura transacional
1. implementar ledger;
2. implementar receipts;
3. expor API interna de draft/aprovação/revalidação.

### Fase C — enforcement
1. conectar interceptação no server e/ou plugin Hermes;
2. bloquear ferramentas classificadas como `external_blocked`;
3. habilitar revalidação final antes da emissão.

### Fase D — superfícies humanas
1. fila de drafts pendentes;
2. revisão e aprovação;
3. histórico resumido por draft.

### Fase E — automação e regressão
1. adaptar cron/background;
2. rodar testes adversariais;
3. validar que staging privado continua funcional.

## Decisões do executivo ainda pendentes

1. Arquitetura preferida:
- plugin Hermes;
- server;
- híbrida.

2. Política de storage:
- SQLite;
- filesystem estruturado;
- híbrida.

3. Escopo da v1:
- só mensagens e email;
- mensagens + email + calendário + compartilhamento;
- cobertura completa de side effects já na primeira entrega.

4. Política de staging privado:
- quais destinos entram como privados por padrão;
- em quais casos link privado ainda conta como emissão externa.

## Recomendação operacional atual

Seguir com arquitetura híbrida e v1 limitada a mensagens, email, calendário e compartilhamento externo de arquivos. Esse recorte cobre o risco mais frequente, preserva clareza de implementação e evita acoplamento prematuro com todos os side effects possíveis do runtime.

## Condição para iniciar código

Não iniciar implementação antes de uma decisão explícita do executivo sobre:
- ponto principal de enforcement;
- política de storage;
- escopo da v1.

## Retomada

Este tema deve permanecer em backlog governado até decisão do executivo. A retomada deve começar por:
1. reler este plano;
2. reler ADR-013 proposta;
3. escolher arquitetura e escopo da v1;
4. abrir plano de execução técnica por tarefa.
