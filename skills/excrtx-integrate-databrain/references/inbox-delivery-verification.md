> **Escopo operacional vigente:** consultar `databrain_execution_status` e o runbook DataBrain `ops/EXECUTION_CONTROL.md` antes de usar estados/versões históricos deste documento. Gates são locais via `pb heavy`; o perfil factual atual é `semantic-v1`. Instruções de segurança, publicação ampla e autorização deste documento continuam aplicáveis.

# Verificação de entrega da inbox Sales-AI

## Quando usar

Use quando o Publisher reportar `inbox_mensagens insert complete`, mas alguém não encontrar a mensagem no aplicativo.

## Regra de evidência

Não conclua entrega com base apenas no log do Publisher nem em uma listagem base-wide. A prova precisa ser feita no destino do usuário afetado:

1. Resolver o `vendedor_id` da conta autenticada.
2. Consultar `inbox_mensagens` filtrando esse `vendedor_id`, com mensagens expiradas incluídas para auditoria temporal.
3. Conferir título, `created_at`, `valido_ate`, origem e estado de leitura.
4. Comparar a lista específica do usuário com o lote e timestamp registrados no Publisher.
5. Só então separar: mensagem persistida e exibível; persistida para outros destinatários; ou não criada.

## Padrão crítico: acesso compartilhado não é elegibilidade de inbox

No Publisher atual, `test-access-overrides` adiciona pares em `cliente_acesso` para uma conta de teste/sombra. Isso preserva acesso a clientes e permite fan-out de briefings e insights.

As mensagens automáticas de campanhas, porém, usam a lista `vendedorIdMap`, que é construída apenas com registros que possuem `erp_ref_code`. Uma conta de teste/sombra sem esse código pode ter carteira, briefings e insights, mas ficar fora de mensagens de inbox geradas pelo Publisher.

Esse cenário é uma diferença de elegibilidade entre dois fluxos, não um problema de cache do PWA.

## Diagnóstico de causa

Verifique estas fronteiras, nesta ordem:

| Camada | Pergunta | Evidência esperada |
|---|---|---|
| Publisher | O lote foi inserido? | `inbox_mensagens insert complete`, `errors: 0` |
| Destinatário | A conta afetada recebeu uma linha? | consulta por `vendedor_id` |
| Elegibilidade | A conta entrou no conjunto de destinatários? | `erp_ref_code`, `vendedorIdMap`, filtros da campanha e `vendedorClienteMap` |
| Frontend | A UI faz fetch da conta autenticada? | `ApiInboxRepository` filtra por `auth.getSession().user.id` e ordena `created_at DESC` |

Se a linha não existe para aquela conta, não atribua a falha ao PWA. Se a linha existe e a UI não a mostra, então investigar sessão, ambiente Supabase, filtros de validade e versão implantada.

## Remediação correta

Antes de alterar o código, definir a regra de produto:

- contas de teste/sombra devem receber os mesmos comunicados automáticos das carteiras que espelham; ou
- devem receber apenas um broadcast operacional específico; ou
- devem ficar deliberadamente fora de notificações comerciais.

A implementação deve tornar o conjunto de destinatários explícito e coberto por teste: acesso compartilhado sem `erp_ref_code` + carteira elegível deve resultar na política escolhida. Como isso altera a superfície DataBrain → Sales-AI, tratar como mudança COLLAB e aplicar DRAFT antes de deploy.

## Padrão de implementação seguro

Não derive os destinatários adicionais de todos os valores de `vendedorClienteMap`: esse mapa pode conter acessos gerenciais, administrativos ou legados, que não devem receber campanhas por efeito colateral.

No Publisher, a solução mínima e auditável é:

1. Fazer `appendTestAccessOverrides` retornar apenas os IDs de contas teste/sombra que tiveram ao menos um cliente resolvido pela configuração.
2. Unir esses IDs ao conjunto ERP (`vendedorIdMap.values()`) no ponto que constrói `allVendedorIds` para `generateAllTradeOutputs`.
3. Deduplicar com ordem estável: destinatários ERP primeiro, contas de teste depois.
4. Manter o filtro posterior de carteira/campanha: uma conta adicional só recebe inbox se tiver clientes na interseção da campanha.

Teste de regressão mínimo: um destinatário ERP e uma conta teste repetida mais uma conta teste adicional devem resultar em uma lista única e ordenada. Execute o teste específico, lint e build. Ao rodar a suíte completa, compare qualquer falha com uma worktree limpa da base antes de atribuí-la à alteração — fixtures ausentes podem gerar ruído não relacionado.

Depois do deploy, a correção só se materializa na próxima execução do Publisher. Não reexecute `publish` apenas para provar a notificação: ele tem escopo amplo e exige DRAFT próprio. Para uma mensagem retroativa, use uma capability de broadcast dedicada ou apresente o DRAFT de publicação ampla com impacto explícito.
