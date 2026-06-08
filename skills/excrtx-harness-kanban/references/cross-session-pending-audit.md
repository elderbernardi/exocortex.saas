# Auditoria de pendências entre sessões

Usar quando o executivo perguntar variações de:
- "o que ficou pendente?"
- "o que temos de outras sessões?"
- "o que ainda está aberto?"
- "quais drafts/planos ainda valem?"

## Objetivo

Responder com backlog vivo, não com arqueologia cega. A auditoria deve separar:
1. pendência operacional viva;
2. artefato histórico já resolvido;
3. rascunho local pronto para triagem/publicação;
4. bloqueio externo real.

## Ordem de leitura recomendada

1. Recuperar sessões anteriores por termos de retomada:
   - `pendente`, `backlog`, `TODO`, `kanban`, `handoff`, `retomada`, `próxima sessão`
2. Verificar artefatos locais de retomada:
   - `.hermes/plans/*.md`
3. Verificar rascunhos locais de issue:
   - `acervo/_artifacts/items/draft-issue-*.md`
4. Verificar sumários consolidados que possam reclassificar o backlog:
   - ex.: `feature-dogfood-summary-*.md`
5. Checar estado operacional atual do repositório:
   - `git status --short`

## Heurística de classificação

### 1. Pendência viva

Manter como pendência quando houver trabalho ainda não executado, por exemplo:
- plano de implementação ainda não iniciado;
- defeito sem correção;
- bloqueio externo sem resolução;
- rascunho local aguardando triagem ou publicação.

### 2. Histórico resolvido

Rebaixar para histórico quando a sessão posterior já provar fechamento, por exemplo:
- PR merged em `main`;
- branch removida;
- handoff superado por execução posterior;
- artefato criado apenas para transição de contexto.

### 3. Rascunho triável

Listar separadamente quando houver drafts locais que já podem virar backlog formal.

### 4. Sem pendência operacional local

Declarar explicitamente quando o estado atual estiver limpo:
- sem mudanças locais;
- sem branch de trabalho restante;
- sem processo em aberto no repositório.

## Formato de resposta recomendado

- `Estado geral agora`
- `O que ainda parece pendente de verdade`
- `O que já não considero pendência real`
- `Resumo executivo`

## Pitfalls

### Pitfall 1 — tratar handoff como backlog eterno

Handoff é artefato de transição. Se a sessão seguinte já executou e fechou o trabalho, o handoff vira histórico.

### Pitfall 2 — confundir draft local com issue já publicada

Draft em `acervo/_artifacts/items/` é backlog potencial, não execução concluída.

### Pitfall 3 — ignorar o estado atual do git

Sessão antiga pode falar em pendência local, mas o repositório atual pode já estar limpo. Sempre revalidar o presente.

### Pitfall 4 — devolver lista plana sem priorização

Separar pelo menos:
- plano-mãe;
- falhas críticas;
- drafts para triagem;
- itens já resolvidos.
