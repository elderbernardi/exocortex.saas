# Macroverso, Microversos e Tarefa — alinhamento semântico

Aprendizado consolidado desta classe de tarefa:

## Correção de filosofia

Não modelar assim:
- Microverso = sala

Modelar assim:
- Macroverso = quem fala
- Microversos = entidades semânticas e operacionais autocontidas
- Tarefa = sala operacional concreta onde a execução acontece

## Regra operacional

Para qualquer canvas não-trivial:
1. declarar o estado do macroverso
2. identificar o microverso principal que ancora a tarefa
3. listar microversos secundários apenas quando houver apoio real
4. explicitar restrições de compartilhamento entre microversos em tarefas cross-domain
5. descrever a tarefa como espaço operacional, não como domínio

## Pitfall

Erro comum: usar "microverso" como sinônimo de contexto/sala/ambiente ativo.

Por que isso é ruim:
- colapsa domínio e execução numa só coisa
- apaga a diferença entre âncora principal e apoios secundários
- enfraquece o controle de compartilhamento entre microversos
- deixa o canvas filosoficamente fora do contrato do Exocórtex

## Heurística curta

Pergunta certa:
- que microverso ancora?
- quais microversos apoiam?
- que tarefa/sala estamos abrindo?
- que fronteiras de compartilhamento precisam ser respeitadas?

## Sinal de falha

Se a formulação do canvas puder ser lida como "estamos na sala X" quando X é um domínio, o canvas está errado. A sala é a tarefa; X é o microverso.