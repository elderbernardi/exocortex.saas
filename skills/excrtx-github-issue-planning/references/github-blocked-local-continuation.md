# GitHub bloqueado: continuar execução local sem perder o plano

Use quando o executivo aprova criação/edição de issues, mas o runtime/harness bloqueia `gh issue create`, `gh issue comment`, `gh issue close` ou equivalente.

## Regra operacional

O bloqueio do harness vence a aprovação textual da conversa. Não repita, não fragmente o comando, não troque para API/curl e não tente contornar.

## Sequência segura

1. Reporte exatamente o que publicou e o que não publicou.
2. Preserve o plano em arquivo local durável, preferencialmente `docs/plans/` quando servir de âncora futura.
3. Se issues antigas ficaram perigosas ou confusas e o executivo pedir fechamento explícito, essa nova autorização cobre apenas o fechamento solicitado.
4. Se criação de novas issues continuar bloqueada, converta o plano em execução local:
   - escreva um prompt autocontido para nova sessão/agente;
   - proíba GitHub writes no prompt;
   - liste arquivos obrigatórios a ler;
   - limite o escopo a uma fatia implementável;
   - exija verificação real e `git status`.
5. Após a sessão/agente terminar, verifique os artefatos localmente antes de reportar sucesso.

## Prompt mínimo para nova sessão local

Inclua:

- contexto arquitetural e decisões recentes;
- caminho do repositório;
- plano local canônico;
- restrições: sem GitHub, sem sudo, sem commit/push;
- escopo pequeno e verificável;
- comandos de validação obrigatórios;
- formato do relatório final.

## Pitfall

Não tratar "criar issues novas" e "começar desenvolvimento local das issues planejadas" como a mesma ação. A primeira é externa; a segunda pode ser interna se operar só no filesystem local.
