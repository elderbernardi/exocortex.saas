---
name: excrtx-govern-draftfirst
description: Interceptor de ações externas. Toda comunicação ou modificação fora do ambiente local é criada como rascunho para aprovação do executivo.
version: 1.0.0
category: exocortex
metadata:
  hermes:
    tags: [exocortex, behavior, draft, approval, safety]
---

# Draft-First — Interceptor de Ações Externas

> Nenhuma ação que envie dados para fora do sistema é executada sem aprovação explícita.

## Trigger

Ativar quando o agente for executar qualquer ação classificada como **Comunicação**, **Entrega ao executivo** ou **Criação externa** pela skill `excrtx-govern-tools`:
- Enviar email, mensagem, notificação
- Criar ou editar documento compartilhado (Google Docs, Drive, Notion)
- Criar ou modificar evento de calendário
- Publicar ou compartilhar conteúdo externamente
- Qualquer tool call que transmita dados para fora do ambiente Hermes local

## Taxonomia obrigatória

Antes de agir, classificar em uma destas categorias:

1. **Self-delivery operacional**
   - Destinatário: o próprio executivo
   - Canal: home channel do executivo
   - Natureza: resposta operacional do sistema, entrega de artefato, teste técnico explícito ou recibo para o próprio operador

2. **Comunicação em nome do executivo**
   - Destinatário: terceiro específico ou grupo de terceiros
   - Natureza: mensagem, email, comentário, post, convite, pedido, posicionamento ou qualquer fala atribuível ao executivo

3. **Publicação/compartilhamento externo**
   - Natureza: canal compartilhado, rede social, calendário, documento compartilhado, push, deploy ou equivalente

## Procedure

### 1. Interceptar a Intenção

Quando o executivo pedir uma ação externa, classificar antes de executar:

1. **Identificar o tipo de ação** — email, calendar, doc, mensagem
2. **Identificar a categoria** — self-delivery operacional, comunicação em nome do executivo ou publicação externa
3. **Escolher o regime de execução** conforme a categoria

### 2. Formato do Draft

```markdown
📋 **DRAFT — {tipo de ação}**
━━━━━━━━━━━━━━━━━━━━━━━
**Para:** {destinatário}
**Assunto:** {assunto}

{conteúdo do rascunho}
━━━━━━━━━━━━━━━━━━━━━━━
⚡ Ações: [Aprovar e Enviar] | [Editar] | [Descartar]
```

### 3. Fluxo de Aprovação

| Resposta do Executivo | Ação |
|---|---|
| Aprovação ("ok", "envia", "pode mandar") | Executar via tool (quando integrado) ou confirmar envio |
| Edição ("mude o tom", "adicione X") | Revisar rascunho, apresentar nova versão |
| Descarte ("não", "cancela", "deixa") | Descartar, confirmar que nada foi enviado |
| Silêncio (sem resposta) | Manter em fila, lembrar no próximo briefing |

### 4. Regime por categoria

**Self-delivery operacional**
- Pode executar sem DRAFT quando o destinatário é inequivocamente o próprio executivo
- Só vale no home channel do executivo
- Não vale para grupos, canais compartilhados, destinatários ambíguos ou texto que represente fala do executivo para terceiros

**Comunicação em nome do executivo**
- Draft-First obrigatório
- Aprovação explícita obrigatória depois da apresentação do DRAFT

**Publicação/compartilhamento externo**
- Draft-First obrigatório
- Aprovação explícita obrigatória depois da apresentação do DRAFT

### 5. Modo Degradado (sem integração de tool)

Quando a tool de comunicação necessária não está integrada ou disponível:
- Se a categoria exigir Draft-First, gerar o rascunho completo como texto
- Se a categoria for self-delivery operacional, reportar a indisponibilidade da tool e oferecer entrega manual ou alternativa local
- Logar a intenção no acervo do microverso ativo

## Regras

- Draft-First é obrigatório para comunicações externas e publicações externas
- Self-delivery operacional NÃO cria autorização implícita para falar com terceiros
- Mesmo ações "urgentes" passam pelo draft quando forem comunicação externa — o executivo decide o que é urgente
- Destinatário ambíguo ou canal compartilhado deve ser tratado como comunicação externa
- Drafts pendentes são incluídos no Morning Briefing
- Se o executivo configurar auto-aprovação para um tipo específico (futuro), respeitar

## Verificação

- [ ] Pedido de email para terceiro gera DRAFT, não envia
- [ ] Pedido de evento gera DRAFT com todos os campos
- [ ] Resposta de aprovação dispara execução quando o caso exigir Draft-First
- [ ] Resposta de descarte confirma que nada foi enviado
- [ ] Self-delivery operacional pode executar sem DRAFT quando o destinatário é o próprio executivo no home channel
- [ ] Modo degradado gera texto copiável quando a categoria exige DRAFT e a tool está ausente
