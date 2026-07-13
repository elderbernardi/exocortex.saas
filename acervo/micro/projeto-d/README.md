# Projeto D — Microverso de Desenvolvimento

Este microverso concentra o desenvolvimento do **Projeto D** dentro do Acervo Cognitivo do Exocórtex.

## Escopo

- organizar contexto, decisões, workflows, ferramentas e artefatos do Projeto D
- preservar isolamento semântico em relação aos demais microversos
- servir como domínio canônico para evolução e execução do projeto
- apontar para o repositório de desenvolvimento ativo em `/home/elder/projetos/lotostate`

## Estrutura

```text
projeto-d/
├── microverso.yaml
├── README.md
├── _meta/
├── context/
├── knowledge/
├── contracts/
├── prompts/
├── persona/
├── workflows/
├── skills/
├── tools/
├── templates/
├── decisions/
├── reflections/
├── raw/
└── _archive/
```

## Convenção operacional

- `context/` guarda o estado corrente do projeto
- `knowledge/` guarda fatos, referências e documentação de trabalho
- `decisions/` guarda ADRs e decisões aprovadas
- `workflows/` guarda procedimentos recorrentes
- `raw/` é imutável

## Contrato canônico

A estrutura deste microverso segue `global/contracts/microverso-directory-structure.md`.
