# Template de Microverso — Exocórtex

Este diretório é o molde para novos microversos no Acervo Cognitivo.
**Não edite arquivos aqui para uso direto** — crie uma cópia com
`excrtx-memory-newmicro`.

## Estrutura (14 diretórios)

```
{slug}/
├── microverso.yaml       # Manifesto excrtx/v1
├── .gitignore
├── README.md
├── _meta/                # SCHEMA.md + index.md + log.md
├── context/              # Nature 1  — Situação atual
├── knowledge/            # Nature 2  — Fatos e dados
├── contracts/            # Nature 3  — Regras e contratos
├── prompts/              # Nature 4  — Prompts reutilizáveis
├── persona/              # Nature 5  — Voz e estilo
├── workflows/            # Nature 6  — SOPs e processos
├── skills/               # Nature 7  — Capacidades
├── tools/                # Nature 8  — Ferramentas
├── templates/            # Nature 9  — Modelos
├── decisions/            # Nature 10 — Decisões (ADR)
├── reflections/          # Nature 11 — Lições
├── raw/                  # Fontes brutas (imutáveis)
└── _archive/             # Conteúdo supersedido
```

## Como usar

```bash
# Criar um novo microverso a partir deste template
cp -r _template/ micro/{slug}/

# Substituir placeholders
# {{DOMAIN_NAME}}       → nome legível (ex: "Produto Alpha")
# {{DOMAIN_DESCRIPTION}} → descrição de uma linha
# {{CREATED_DATE}}       → data ISO (ex: 2026-06-21)
# {{MICROVERSO_SLUG}}    → slug kebab-case (ex: produto-alpha)
# {{micro_type}}         → client | project | domain | role
```

## Contrato canônico

A estrutura é definida em `global/contracts/microverso-directory-structure.md`.
Toda skill de criação/instalação/exportação de microverso deve respeitar este contrato.

## Placeholders

Arquivos com `{{...}}` são preenchidos pelo `excrtx-memory-newmicro` durante a
criação. Após a criação, nenhum placeholder deve permanecer.
