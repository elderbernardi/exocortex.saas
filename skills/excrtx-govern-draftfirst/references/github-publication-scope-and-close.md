# GitHub publication: escopo, publicação e fechamento

## Quando usar
Quando o executivo pedir commit, push, comentário em issue, fechamento de issue, abertura/edição de PR ou merge.

## Sequência recomendada
1. Inspecionar branch atual, remote e working tree.
2. Separar arquivos do escopo pedido dos arquivos paralelos fora de escopo.
3. Montar DRAFT com:
   - arquivos incluídos
   - arquivos excluídos
   - comandos sugeridos
   - testes executados e resultado
   - efeito externo exato (commit, push, comentário, fechamento)
4. Só executar após aprovação explícita pós-DRAFT.

## Pitfalls recorrentes
- `git status` pode conter ruído paralelo; não assumir que tudo pendente entra no commit.
- Rascunhos locais de comentário/issue podem ser úteis para publicação, mas não precisam entrar no commit.
- Fechar issue é efeito externo distinto de comentar issue; ambos precisam estar cobertos no DRAFT.
- Pedido imperativo do usuário para publicar não substitui aprovação pós-DRAFT.

## Regra de escopo
Se o pedido inicial é resolver uma issue específica, o default é publicar apenas os arquivos diretamente ligados àquela issue. Qualquer ampliação de escopo precisa ser explicitada no DRAFT.
