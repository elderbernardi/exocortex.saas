# Style-Set Visual — Artefatos v2

Feature: Design System visual com cascade global→micro usando Google DESIGN.md.

## Estrutura

```
style-set/
├── acervo/
│   ├── global/
│   │   ├── DESIGN.md       ← [NEW] tokens visuais (cores, typo, spacing, componentes)
│   │   └── index.md        ← [MOD] +entrada para DESIGN.md
│   └── micro/_template/
│       ├── SCHEMA.md       ← [MOD] +convenção de Style Override
│       └── index.md        ← [MOD] +seção Estilo Visual no catálogo
└── skills/
    ├── exocortex-design-system/
    │   └── SKILL.md        ← [NEW] fork de design-md — RESOLVE/WRITE/LINT/EXPORT
    ├── taste-skill/
    │   └── SKILL.md        ← [MOD] +integração com design system
    ├── acervo-manager/
    │   └── SKILL.md        ← [MOD] +DESIGN.md sob demanda (não carrega no boot)
    └── exocortex-new-microverso/
        └── SKILL.md        ← [MOD] +pergunta de estilo visual no onboarding
```

## Provisionamento

Estes artefatos substituem os equivalentes em `.hermes/` durante deploy.
O `test-entrypoint.sh` do Docker copia de `.hermes/` — para testar esta feature,
provisione o runtime com estes arquivos antes de subir o container.

## Validação

- Lint: `npx -y @google/design.md lint acervo/global/DESIGN.md`
- Resultado: 0 errors, 1 warning (cor `danger` sem ref em componente — aceitável)
- WCAG: alerts com contraste AA (4.5:1+)

## Decisões (ADR-006)

| Decisão | Justificativa |
|---|---|
| Google DESIGN.md (não CSS) | Machine-readable, tooling nativo (lint/diff/export) |
| Tokens em `global/` (não `macro/`) | Sob demanda — evita custo de contexto |
| Assets em `macro/assets/` | Binários, coerência com identidade |
| `extends: global` no micro | Explícito: micro é delta, não standalone |
| brandkit → design-system → taste | Criação → persistência → validação |
