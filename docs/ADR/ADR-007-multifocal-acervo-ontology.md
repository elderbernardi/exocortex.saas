# ADR-007: Ontologia Multifocal v2 do Acervo

> **Status:** Aceita  
> **Data:** 2026-05-30  
> **Decisor:** @elder  
> **Contexto:** Tornar o Acervo mais orgânico ao harness Hermes e mais compreensível para leigos

## Contexto

A primeira geração do Acervo usava 7 Natures como arquivos ou diretórios: `contexto`, `conhecimento`, `instrucoes`, `persona`, `processos`, `ferramentas`, `reflexoes`. Isso ajudou a explicar o sistema para humanos, mas criou acoplamento fraco com o funcionamento do Hermes. Exemplo: `processos` pode significar prompt, skill, workflow, checklist ou playbook.

## Decisão

Adotar Ontologia Multifocal v2:

- Diretórios funcionais representam como o agente opera.
- Natures representam semântica para o humano.
- Frontmatter v2 conecta as duas lentes.

## Estrutura funcional padrão

```text
context/
knowledge/
contracts/
prompts/
skills/
workflows/
tools/
templates/
decisions/
reflections/
persona/
_meta/
raw/
_archive/
```

## Natures preservadas

As 7 Natures continuam como vocabulário semântico:

- contexto
- conhecimento
- instrucoes
- processos
- ferramentas
- persona
- reflexoes

Elas não são mais a estrutura primária de arquivos.

## Frontmatter obrigatório

Todo arquivo novo deve declarar `nature`, `kind`, `scope_mode`, `authority`, `operational_mode`, `stability`, `sources`, `confidence`, `promotion_policy` e `upstream`.

## Legado

Arquivos flat de Nature estão descontinuados. Conteúdo existente deve ser migrado para diretórios funcionais e os originais arquivados em `_archive/legacy-flat-natures/`.

## Consequências

- `acervo-manager` deve operar por diretório funcional e validar frontmatter.
- `exocortex-new-microverso` deve criar estrutura v2.
- `setup.sh` deve verificar estrutura v2.
- Microversos legados devem ser migrados.
