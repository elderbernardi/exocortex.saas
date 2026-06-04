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

Ativar quando o agente for executar qualquer ação classificada como **Comunicação** ou **Criação externa** pela skill `excrtx-govern-tools`:
- Enviar email, mensagem, notificação
- Criar ou editar documento compartilhado (Google Docs, Drive, Notion)
- Criar ou modificar evento de calendário
- Publicar ou compartilhar conteúdo externamente
- Qualquer tool call que transmita dados para fora do ambiente Hermes local

## Procedure

### 1. Interceptar a Intenção

Quando o executivo pedir uma ação externa, NÃO executar diretamente. Em vez disso:

1. **Identificar o tipo de ação** — email, calendar, doc, mensagem
2. **Gerar o conteúdo completo** como rascunho local
3. **Apresentar ao executivo** com marcação visual

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

### 4. Modo Degradado (sem integração de tool)

Quando o MCP de comunicação (ex: Google Workspace) não está integrado:
- Gerar o rascunho completo como texto
- O executivo copia e envia manualmente
- Logar a intenção no acervo do microverso ativo

## Regras

- **ZERO exceções** ao Draft-First para comunicações externas
- Mesmo ações "urgentes" passam pelo draft — o executivo decide o que é urgente
- Drafts pendentes são incluídos no Morning Briefing
- Se o executivo configurar auto-aprovação para um tipo específico (futuro), respeitar

## Verificação

- [ ] Pedido de email gera DRAFT, não envia
- [ ] Pedido de evento gera DRAFT com todos os campos
- [ ] Resposta de aprovação dispara execução
- [ ] Resposta de descarte confirma que nada foi enviado
- [ ] Modo degradado gera texto copiável quando MCP ausente
