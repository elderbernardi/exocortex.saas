---
type: knowledge
title: Ecossistema Visual — Design System do Exocórtex
description: O Exocórtex adota o formato **Google DESIGN.md** (`google-labs-code/design.md`, Apache-2.0). Cada `DESIGN.md` é um ar...
tags: [design-system, tokens, brandkit, visual, DESIGN.md, cascade]
timestamp: 2026-06-10
class: volátil
created_at: 2026-06-10T00:00:00Z
last_accessed_at: 2026-06-10T00:00:00Z
updated: 2026-06-10
excrtx_type: reference
nature: knowledge
confidence: high
sources: [skills/excrtx-quality-designsys/SKILL.md, skills/excrtx-quality-taste/brandkit.md, acervo/global/_meta/DESIGN.md, acervo/micro/_template/_meta/SCHEMA.md]
created: 2026-06-10
---

# Ecossistema Visual do Exocórtex

## Formato: Google DESIGN.md

O Exocórtex adota o formato **Google DESIGN.md** (`google-labs-code/design.md`, Apache-2.0). Cada `DESIGN.md` é um arquivo Markdown com **YAML frontmatter obrigatório** (tokens machine-readable) + **markdown prosa** (rationale humano).

### Tipos de token

| Tipo            | Formato                    | Exemplo                                              |
| --------------- | -------------------------- | ---------------------------------------------------- |
| Color           | `#` + hex sRGB entre aspas | `"#1a73e8"`                                          |
| Dimension       | número + unidade           | `48px`, `"-0.02em"`                                  |
| Token reference | `{path.to.token}`          | `{colors.primary}`                                   |
| Typography      | objeto aninhado            | `fontFamily`, `fontSize`, `fontWeight`, `lineHeight` |

### Regras rígidas

1. Hex colors **SEMPRE entre aspas** — `#1a73e8` solto vira comentário YAML
2. Dimensões negativas entre aspas — `"-0.02em"`
3. Token references resolvem por dotted path absoluto — `{colors.primary}` funciona, `{primary}` não
4. Seção canônica é enforced pelo linter: Overview → Colors → Typography → Layout → Elevation → Shapes → Components → Do's/Don'ts
5. `version: alpha` é a versão atual da spec (Abril 2026)

## Cascade: global → microverso

```
acervo/global/_meta/DESIGN.md    → tokens base (obrigatório)
acervo/micro/{slug}/DESIGN.md    → override opcional (apenas deltas)
```

- Micro sem `DESIGN.md` → herda 100% do global
- Micro com `DESIGN.md` → DEVE ter `extends: global` no frontmatter
- Tokens declarados no micro **vencem** os do global
- Tokens não declarados → herdados do global
- Micro pode ADICIONAR tokens que não existem no global

## Tooling

```bash
# Lint: estrutura, referências, contraste WCAG
npx -y @google/design.md lint acervo/global/_meta/DESIGN.md

# Export: Tailwind ou DTCG
npx -y @google/design.md export --format tailwind DESIGN.md > theme.json
npx -y @google/design.md export --format dtcg DESIGN.md > tokens.json
```

## Skills envolvidas

### `excrtx-quality-designsys` — Persistência e resolução

- **4 operações:** RESOLVE (cascade), WRITE (criar/atualizar), LINT (WCAG), EXPORT (Tailwind/DTCG)
- Ativada quando tarefa precisa de tokens visuais
- **Não carregada no boot** — economia de contexto
- **Path mismatch conhecido:** skill referencia `acervo/global/DESIGN.md` mas o arquivo real está em `acervo/global/_meta/DESIGN.md`

### `brandkit` (sub-skill de `excrtx-quality-taste`) — Guia criativo

- **Não é skill executável** — é quality gate textual que orienta a definição de identidade visual
- Perguntas: posicionamento, personalidade, tensão visual, público
- Define: cores proprietárias, sistema tipográfico, linguagem visual
- **Não extrai cores de imagem** — é guia humano, não pipeline de processamento

### Fluxo completo

```
brandkit (guia criativo/extração)
  → excrtx-quality-designsys (persistir tokens em DESIGN.md)
  → excrtx-quality-taste (validar output visual contra tokens)
```

### `excrtx-produce-slides` — Consumidor de tokens

- Lê `global/DESIGN.md` + `micro/{slug}/DESIGN.md` para definir envelope visual
- Envelopes: strict (institucional), balanced (padrão), expressive (palestra), experimental

## Estado atual

- **Global:** 13 cores (primary, secondary, tertiary, accent, neutral, dark, danger, success, warning, on-primary, on-secondary, on-tertiary, on-accent), tipografia (Inter + JetBrains Mono), spacing (8px scale), 7 componentes
- **Microversos:** sales-ai tem DESIGN.md próprio (esquema cromático de marca #223874). Template \_template tem SCHEMA.md mas DESIGN.md não existe.
- **Consumo:** Sob demanda — ninguém carrega DESIGN.md no boot
