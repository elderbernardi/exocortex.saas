# GitHub-first review of pendências entre sessões

Usar quando o projeto já externalizou o backlog para GitHub e o executivo pede uma leitura rápida do que segue aberto.

## Heurística

1. Fonte única vence memória de sessão.
   - Se os rascunhos locais já foram promovidos para issues, o backlog vivo está nas issues abertas.
2. Prioridade explícita vence interpretação subjetiva.
   - Labels `P0`, `P1`, `P2` devem estruturar a resposta.
3. Ausência de prioridade também comunica.
   - Issues sem label P não devem ser forçadas para uma fila arbitrária; listá-las separadamente.
4. Resumo executivo deve caber em um relance.
   - Encerrar com 2-3 linhas do tipo: `fila crítica`, `fila operacional`, `trilha de arquitetura/pesquisa`.

## Formato recomendado

- `P0`
- `P1`
- `P2`
- `Sem rótulo P explícito`
- `Leitura executiva`

## Erros a evitar

- tratar handoff antigo como pendência viva sem checar issue correspondente;
- misturar histórico local com backlog já promovido;
- esconder issues sem prioridade para simplificar a leitura;
- responder apenas com busca de sessões quando já existe backlog canônico no GitHub.
