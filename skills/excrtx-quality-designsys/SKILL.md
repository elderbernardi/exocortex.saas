---
name: excrtx-quality-designsys
description: "Persistir, resolver e validar tokens visuais no Acervo Cognitivo. Fork de design-md adaptado ao cascade macro→micro do Exocórtex."
version: 1.0.0
author: Exocórtex
metadata:
  hermes:
    tags: [exocortex, design, tokens, style, brand, visual, cascade]
    category: exocortex
    related_skills: [excrtx-memory-manager, excrtx-quality-taste, design-md, brandkit]
---

# Exocórtex Design System

Skill para gerenciar tokens visuais no Acervo Cognitivo.
Baseada no formato Google DESIGN.md (YAML tokens + markdown prosa).

Complementa o ecossistema:
- **brandkit** (taste sub-skill) → guia criativo para *definir* identidade visual
- **excrtx-quality-designsys** (esta) → *persiste e resolve* tokens no acervo
- **excrtx-quality-taste** → *valida qualidade* do output visual

## When This Skill Activates

Ativar quando:
- Uma tarefa precisa de tokens visuais (cores, tipografia, spacing) para gerar output
- O executivo quer definir, revisar ou atualizar o estilo visual
- O agente precisa resolver cascade de estilo (global + micro override)
- Lint ou validação WCAG dos tokens é necessária
- Export de tokens para formato externo (Tailwind, DTCG) é solicitado

## Acervo Paths

```
ACERVO="${HERMES_HOME:-$HOME/.hermes}/acervo"

# Fonte de verdade (tokens base)
DESIGN_GLOBAL="$ACERVO/global/DESIGN.md"

# Overrides por microverso (opcional — apenas deltas)
DESIGN_MICRO="$ACERVO/micro/{slug}/DESIGN.md"

# Assets de identidade (binários: logo, favicon)
ASSETS="$ACERVO/macro/assets/"
```

## Format: Google DESIGN.md

O formato combina YAML frontmatter (tokens machine-readable) com markdown body
(rationale human-readable). Spec: `google-labs-code/design.md` (Apache-2.0).

### Token Types

| Type | Format | Example |
|------|--------|---------|
| Color | `#` + hex (sRGB) | `"#1A1C1E"` |
| Dimension | number + unit | `48px`, `-0.02em` |
| Token reference | `{path.to.token}` | `{colors.primary}` |
| Typography | object | `fontFamily`, `fontSize`, `fontWeight`, `lineHeight` |

### Canonical Section Order

1. Overview
2. Colors
3. Typography
4. Layout & Spacing
5. Elevation & Depth
6. Shapes
7. Components
8. Do's and Don'ts

---

## Operation: RESOLVE

Resolver tokens visuais para o contexto ativo (cascade global → micro).

### Procedure

1. **Ler `global/DESIGN.md`** — tokens base (obrigatório):
   ```bash
   cat "$DESIGN_GLOBAL"
   ```

2. **Verificar se microverso ativo tem override:**
   ```bash
   test -f "$ACERVO/micro/{slug}/DESIGN.md"
   ```

3. **Se override existe:**
   - Ler `micro/{slug}/DESIGN.md`
   - Verificar campo `extends: global` no frontmatter
   - Mesclar: tokens do micro vencem tokens do global (override)
   - Tokens não declarados no micro → herdados do global

4. **Se override NÃO existe:**
   - Usar global puro (100% herança)

5. **Retornar tokens resolvidos** para a skill que solicitou.

### Merge Logic

```
Para cada token no DESIGN.md global:
  SE micro declara o mesmo token → usar valor do micro
  SENÃO → usar valor do global

Tokens que existem APENAS no micro (ex: componentes específicos)
→ adicionar ao resultado (extensão, não conflito)
```

### Verification

- [ ] global/DESIGN.md lido
- [ ] Override detectado corretamente (existe ou não)
- [ ] Merge respeita cascade (micro vence global)
- [ ] Tokens resolvidos são completos (nenhum token global perdido)

---

## Operation: WRITE

Criar ou atualizar DESIGN.md no acervo.

### Procedure

1. **Determinar escopo:**
   - Tokens do executivo (paleta base) → `global/DESIGN.md`
   - Override de microverso → `micro/{slug}/DESIGN.md`

2. **Se escrevendo override em micro:**
   - Adicionar `extends: global` no frontmatter YAML
   - Incluir APENAS tokens que diferem do global
   - NÃO copiar tokens inalterados

3. **Validar formato:**
   - YAML frontmatter válido
   - Hex colors entre aspas (`"#1a73e8"`)
   - Dimensões negativas entre aspas (`"-0.02em"`)
   - Seções na ordem canônica

4. **Logar operação** via `excrtx-memory-manager` (log.md do escopo).

5. **Atualizar index.md** se arquivo novo.

### Integração com brandkit

Quando o executivo quer definir identidade visual:

1. Ativar `brandkit` (sub-skill de taste) como guia criativo
2. brandkit coleta: posicionamento, personalidade, tensão visual, público
3. brandkit define: cores proprietárias, sistema tipográfico, linguagem visual
4. **Esta skill persiste** o resultado como DESIGN.md no acervo

Fluxo: `brandkit` (criação) → `excrtx-quality-designsys` (persistência)

### Rules

- NUNCA duplicar tokens globais em override de micro
- Override de micro DEVE ter `extends: global`
- Hex colors SEMPRE entre aspas (YAML requirement)
- Token references usam dotted path: `{colors.primary}`, nunca `{primary}`

---

## Operation: LINT

Validar DESIGN.md usando CLI do Google.

### Procedure

```bash
# Validar estrutura + token references + WCAG contrast
npx -y @google/design.md lint "$DESIGN_GLOBAL"

# Se override existe
npx -y @google/design.md lint "$ACERVO/micro/{slug}/DESIGN.md"
```

### What lint catches

- `broken-ref` — referência a token inexistente
- `duplicate-section` — heading duplicado
- `invalid-color`, `invalid-dimension`, `invalid-typography` — formato errado
- `wcag-contrast` — contraste textColor vs backgroundColor abaixo de WCAG AA (4.5:1)
- `unknown-component-property` — propriedade fora do whitelist

---

## Operation: EXPORT

Gerar formato consumível a partir dos tokens resolvidos.

### Procedure

```bash
# Export para Tailwind theme JSON
npx -y @google/design.md export --format tailwind "$DESIGN_GLOBAL" > tailwind.theme.json

# Export para W3C DTCG (Design Tokens Format Module) JSON
npx -y @google/design.md export --format dtcg "$DESIGN_GLOBAL" > tokens.json
```

### CSS Custom Properties (manual)

Se o export nativo não atender, gerar CSS manualmente a partir dos tokens YAML:

```css
:root {
  --color-primary: {colors.primary};
  --color-secondary: {colors.secondary};
  --font-heading: {typography.h1.fontFamily};
  /* ... */
}
```

---

## Pitfalls

- **Hex colors must be quoted strings.** `#1A1C1E` sem aspas quebra YAML.
- **Negative dimensions need quotes.** `letterSpacing: -0.02em` → `letterSpacing: "-0.02em"`.
- **Section order is enforced.** Reordenar se necessário.
- **`version: alpha`** é a versão atual da spec (Apr 2026).
- **Override NÃO é standalone.** Sem `extends: global`, agente trata como spec completa.
- **Token references resolve by dotted path.** `{colors.primary}` ✓, `{primary}` ✗.

---

## ADR

- ADR-006: Design System — Google DESIGN.md como formato de tokens visuais
  - Formato machine-readable com tooling nativo (lint, diff, export)
  - Tokens em global/ (sob demanda) — não em macro/ (evita custo de contexto)
  - Assets visuais (logo) em macro/assets/ (binários, sem custo de contexto)
  - Cascade: global = base, micro = override (extends: global)
  - brandkit = guia criativo, excrtx-quality-designsys = persistência
