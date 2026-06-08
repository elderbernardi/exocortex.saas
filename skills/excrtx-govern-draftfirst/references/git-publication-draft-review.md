# Publicação de branch e PR — review draft-first

Use este fluxo quando o executivo pedir push, PR, comentário em PR/issue ou qualquer publicação de estado do repositório.

## Objetivo

Evitar que publicação externa misture:
- escopo real do commit/branch
- ruído local no working tree
- duplicação de branch remota ou PR já existente

## Checklist mínimo antes do DRAFT

1. Confirmar branch atual e HEAD.
2. Confirmar o commit exato que será publicado.
3. Comparar a branch contra a base (`origin/main` ou base equivalente).
4. Separar:
   - arquivos no diff rastreado da branch
   - arquivos paralelos locais fora de escopo (modified/untracked fora do commit)
5. Verificar se a branch remota já existe.
6. Verificar se já existe PR para a mesma head branch.
7. Rodar os checks relevantes e registrar resultado real.
8. Só então montar o DRAFT.

## Forma do DRAFT

### DRAFT de push
- impacto externo
- comando exato de push
- confirmação do commit/branch publicados
- confirmação explícita do que fica de fora

### DRAFT de PR
- base branch
- head branch
- título sugerido
- corpo sugerido
- test plan com checks realmente executados
- riscos e pendências explícitas

## Pitfalls observados

- "working tree sujo" não significa automaticamente que o push publicará tudo; diferenciar estado local de escopo commitado evita falso alarme.
- Push e PR são dois efeitos externos distintos; exigir aprovação separada reduz erro operacional.
- Se o smoke/harness ficar bloqueado pelo ambiente, registrar como pendência real; não preencher o PR como se tivesse sido executado.

## Resultado esperado

O executivo recebe um pacote de publicação verificável: o que entra, o que fica fora, o que já foi validado e o comando pronto para aprovação.