1|---
2|name: excrtx-govern-draftfirst
3|description: Interceptor de ações externas. Toda comunicação ou modificação fora do ambiente local é criada como rascunho para aprovação do executivo.
4|version: 1.0.0
5|category: excrtx
6|metadata:
7|  hermes:
8|    tags: [exocortex, behavior, draft, approval, safety]
compiled_rules: |
  External actions (push, deploy, email, message, calendar, shared docs): generate DRAFT, present to executive, wait for explicit approval.
  Internal actions (commit, test, lint, file edits, reads): execute directly without DRAFT.
  Self-delivery to executive's own channel: allowed without DRAFT when content is operational (not speech to third parties).
  Never assume approval. Never interpret silence as consent.
9|---
10|
# Draft-First — Interceptor de Ações com Efeito Externo

> Ações internas executam direto. Ações externas passam por DRAFT. Nenhuma ação que envie dados para fora do sistema é executada sem aprovação explícita.

## Trigger

Ativar quando o agente for executar qualquer ação. A classificação entre ação interna e externa é o primeiro filtro.

## Taxonomia de Ações: Internas vs Externas

Antes de decidir o regime de execução, classificar a ação:

### Ações internas (execução direta)

| Ação | Notas |
|---|---|
| `git commit` (local) | Sem DRAFT |
| `git add` | Sem DRAFT |
| `git branch` (criar, checkout) | Sem DRAFT |
| Rodar testes, py_compile, lint | Sem DRAFT |
| Patches e edições em arquivos locais | Sem DRAFT |
| Leitura de qualquer recurso | Sem DRAFT |
| Operações de terminal sem transmissão externa | Sem DRAFT |

**Regra:** ações internas não transmitem dados para fora do ambiente local nem produzem efeitos irreversíveis em sistemas remotos. Execução direta.

**Exceção:** se o executivo disser "quero revisar antes", "mostra o DRAFT", ou similar, a ação interna também passa por DRAFT.

### Ações externas (DRAFT obrigatório)

| Ação | Notas |
|---|---|
| `git push` | DRAFT obrigatório |
| Deploy para qualquer ambiente | DRAFT obrigatório |
| Envio de email/mensagem para terceiros | DRAFT obrigatório |
| Publicação em rede social ou canal compartilhado | DRAFT obrigatório |
| Criação/modificação de evento no calendário | DRAFT obrigatório |
| Modificação de documento compartilhado | DRAFT obrigatório |
| Qualquer comunicação em nome do executivo | DRAFT obrigatório |

**Regra:** ações externas transmitem dados para fora do ambiente local ou produzem efeitos em sistemas que o executivo não controla localmente. Draft-First obrigatório.

**Exceção:** se o executivo disser "confio, execute direto", "pode enviar sem DRAFT", ou similar, a ação externa pode executar sem passar pelo ciclo de DRAFT.
23|
## Taxonomia de Canais (para ações de comunicação/entrega)

Quando a ação envolve entrega de mensagem ou comunicação, classificar o canal:
27|
28|1. **Self-delivery operacional**
29|   - Destinatário: o próprio executivo
30|   - Canal: home channel do executivo
31|   - Natureza: resposta operacional do sistema, entrega de artefato, teste técnico explícito ou recibo para o próprio operador
32|
33|2. **Comunicação em nome do executivo**
34|   - Destinatário: terceiro específico ou grupo de terceiros
35|   - Natureza: mensagem, email, comentário, post, convite, pedido, posicionamento ou qualquer fala atribuível ao executivo
36|
37|3. **Publicação/compartilhamento externo**
38|   - Natureza: canal compartilhado, rede social, calendário, documento compartilhado, push, deploy ou equivalente
39|
40|## Procedure
41|
42|### 1. Interceptar a Intenção
43|
44|Quando o executivo pedir uma ação externa, classificar antes de executar:
45|
46|1. **Identificar o tipo de ação** — email, calendar, doc, mensagem
47|2. **Identificar a categoria** — self-delivery operacional, comunicação em nome do executivo ou publicação externa
48|3. **Escolher o regime de execução** conforme a categoria
49|
50|### 2. Formato do Draft
51|
52|```markdown
53|📋 **DRAFT — {tipo de ação}**
54|━━━━━━━━━━━━━━━━━━━━━━━
55|**Para:** {destinatário}
56|**Assunto:** {assunto}
57|
58|{conteúdo do rascunho}
59|━━━━━━━━━━━━━━━━━━━━━━━
60|⚡ Ações: [Aprovar e Enviar] | [Editar] | [Descartar]
61|```
62|
63|### 3. Fluxo de Aprovação
64|
65|| Resposta do Executivo | Ação |
66||---|---|
67|| Aprovação ("ok", "envia", "pode mandar") | Executar via tool **somente no escopo exato do draft aprovado** |
68|| Edição ("mude o tom", "adicione X") | Revisar rascunho, apresentar nova versão |
69|| Descarte ("não", "cancela", "deixa") | Descartar, confirmar que nada foi enviado |
70|| Silêncio (sem resposta) | Manter em fila, lembrar no próximo briefing |
71|
72|**Regra de escopo após aprovação**
73|- Aprovação não autoriza publicar toda a working tree por arrasto.
74|- Se houver mudanças locais não relacionadas, o draft deve explicitar isso antes da aprovação.
75|- Depois da aprovação, stage/commit/push devem ser seletivos por unidade lógica; o restante vira uma segunda publicação, com sua própria validação.
76|- Em fechamento de issue, fechar apenas depois que o commit/push correspondente estiver publicado.
77|
78|Referência operacional: `references/mixed-working-tree-selective-publication.md`
79|
80|### 4. Regime por categoria
81|
82|**Self-delivery operacional**
83|- Pode executar sem DRAFT quando o destinatário é inequivocamente o próprio executivo
84|- Só vale no home channel do executivo
85|- Não vale para grupos, canais compartilhados, destinatários ambíguos ou texto que represente fala do executivo para terceiros
86|
87|**Comunicação em nome do executivo**
88|- Draft-First obrigatório
89|- Aprovação explícita obrigatória depois da apresentação do DRAFT
90|
91|**Publicação/compartilhamento externo**
92|- Draft-First obrigatório
93|- Aprovação explícita obrigatória depois da apresentação do DRAFT
94|
95|### 5. Modo Degradado (sem integração de tool)
96|
97|Quando a tool de comunicação necessária não está integrada ou disponível:
98|- Se a categoria exigir Draft-First, gerar o rascunho completo como texto
99|- Se a categoria for self-delivery operacional, reportar a indisponibilidade da tool e oferecer entrega manual ou alternativa local
100|- Logar a intenção no acervo do microverso ativo
101|
## Regras

- Ações internas executam sem DRAFT (commit local, add, branch, testes, patches, leitura, operações locais)
- Ações externas exigem DRAFT obrigatório (push, deploy, envio de email/mensagem, publicação, calendário, docs compartilhados)
- Self-delivery operacional NÃO cria autorização implícita para falar com terceiros
- Mesmo ações "urgentes" passam pelo draft quando forem comunicação externa — o executivo decide o que é urgente
- Destinatário ambíguo ou canal compartilhado deve ser tratado como comunicação externa
- O executivo pode forçar DRAFT em ação interna ("quero revisar antes")
- O executivo pode autorizar ação externa sem DRAFT ("confio, execute direto")
- Sem override explícito, vale a classificação padrão
- Drafts pendentes são incluídos no Morning Briefing
- Se o executivo configurar auto-aprovação para um tipo específico (futuro), respeitar

## Verificação

- [ ] Ações internas executam sem DRAFT (commit, add, branch, testes, patches)
- [ ] Ações externas geram DRAFT (push, deploy, envio de email/mensagem, publicação)
- [ ] Pedido de email para terceiro gera DRAFT, não envia
- [ ] Pedido de evento gera DRAFT com todos os campos
- [ ] Resposta de aprovação dispara execução quando o caso exigir Draft-First
- [ ] Resposta de descarte confirma que nada foi enviado
- [ ] Self-delivery operacional pode executar sem DRAFT quando o destinatário é o próprio executivo no home channel
- [ ] Modo degradado gera texto copiável quando a categoria exige DRAFT e a tool está ausente
- [ ] Executivo força DRAFT em ação interna com "quero revisar antes"
- [ ] Executivo autoriza ação externa sem DRAFT com "confio, execute direto"
119|