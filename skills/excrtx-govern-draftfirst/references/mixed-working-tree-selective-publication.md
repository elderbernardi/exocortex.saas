# Mixed working tree: publicação seletiva após aprovação

## Quando aplicar
- O executivo aprova commit/push/deploy/fechamento de issue
- O repositório tem mudanças locais de mais de um assunto ao mesmo tempo
- Parte das mudanças aprovadas compartilha arquivo com outras mudanças ainda não aprovadas

## Regra operacional
A aprovação vale para o **escopo do draft**, não para toda a working tree.

## Procedimento
1. Antes de publicar, listar claramente o escopo do draft: arquivos, issue, efeito externo e riscos.
2. Se houver mudanças não relacionadas, avisar isso no draft antes da aprovação.
3. Após aprovação, publicar só o conjunto aprovado:
   - stage seletivo por arquivo ou hunk;
   - commit separado por unidade lógica;
   - push apenas do que foi aprovado.
4. Só então fechar a issue correspondente.
5. Se o executivo também mandar publicar o restante, tratar como segunda unidade de publicação: revisar, validar, commitar e enviar separadamente.

## Pitfalls
- Não interpretar "aprovado" como autorização para empacotar toda a árvore de trabalho.
- Não misturar mudança de issue A com trabalho remanescente de issue B no mesmo commit só porque ambos estão prontos.
- Se um arquivo contém hunks de dois assuntos, usar stage seletivo; não forçar commit monolítico.

## Sinal de qualidade
- Cada commit consegue ser descrito em uma frase curta.
- Cada fechamento de issue aponta para o commit certo.
- O branch principal permanece verde após cada unidade publicada.
