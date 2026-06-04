---
version: alpha
name: Exocórtex Executive Style
description: Tokens visuais do executivo. Aplicado a artefatos visuais sob demanda.
colors:
  primary: "#1a73e8"
  secondary: "#34a853"
  accent: "#fbbc04"
  neutral: "#f8f9fa"
  dark: "#202124"
  danger: "#ea4335"
typography:
  h1:
    fontFamily: Inter
    fontSize: 2.5rem
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  h2:
    fontFamily: Inter
    fontSize: 1.75rem
    fontWeight: 600
    lineHeight: 1.2
  body-md:
    fontFamily: Inter
    fontSize: 1rem
    lineHeight: 1.6
  mono:
    fontFamily: JetBrains Mono
    fontSize: 0.875rem
    lineHeight: 1.5
rounded:
  sm: 4px
  md: 8px
  lg: 16px
spacing:
  sm: 8px
  md: 16px
  lg: 24px
  xl: 48px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "#FFFFFF"
    rounded: "{rounded.sm}"
    padding: 12px
  button-primary-hover:
    backgroundColor: "{colors.dark}"
  card:
    backgroundColor: "#FFFFFF"
    textColor: "{colors.dark}"
    rounded: "{rounded.md}"
    padding: "{spacing.lg}"
  alert-danger:
    backgroundColor: "#fce8e6"
    textColor: "#a50e0e"
    rounded: "{rounded.sm}"
  alert-success:
    backgroundColor: "#e6f4ea"
    textColor: "#1e7e34"
    rounded: "{rounded.sm}"
  alert-warning:
    backgroundColor: "#fef7e0"
    textColor: "#594300"
    rounded: "{rounded.sm}"
  surface:
    backgroundColor: "{colors.neutral}"
    textColor: "{colors.dark}"
    rounded: "{rounded.md}"
  badge:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.dark}"
    rounded: "{rounded.lg}"
---

## Overview

Sistema visual para artefatos gerados pelo Exocórtex em nome do executivo.
Valores iniciais são placeholders genéricos — personalizar via `brandkit`
quando o executivo decidir definir identidade visual própria.

Estes tokens são carregados sob demanda pela skill `exocortex-design-system`
quando uma tarefa produz output visual (relatórios, dashboards, decks, etc.).

## Colors

- **Primary (#1a73e8):** Ações, links, headings de destaque.
- **Secondary (#34a853):** Sucesso, métricas positivas, confirmações.
- **Accent (#fbbc04):** Alertas, destaques, badges, atenção.
- **Neutral (#f8f9fa):** Fundos, superfícies, cards.
- **Dark (#202124):** Texto principal, contraste alto.
- **Danger (#ea4335):** Erros, alertas críticos, ações destrutivas.

## Typography

Inter como fonte principal para headings e corpo de texto.
JetBrains Mono para código, dados tabulares e labels técnicos.
Escala de heading: h1 (2.5rem/700) → h2 (1.75rem/600) → body (1rem/regular).

## Layout & Spacing

Escala de spacing em múltiplos de 8px: sm (8), md (16), lg (24), xl (48).
Border radius conservador: sm (4px) para botões, md (8px) para cards.

## Components

- `button-primary` — Ação principal com cor primária e hover para dark.
- `card` — Container de conteúdo com fundo branco e padding generoso.
- `alert-danger` / `alert-success` — Feedback visual para estados.

## Do's and Don'ts

- **Do:** Usar token references (`{colors.primary}`) em novos componentes.
- **Do:** Manter contraste WCAG AA (4.5:1) em texto sobre fundo.
- **Don't:** Adicionar cores ad-hoc fora da paleta sem justificativa.
- **Don't:** Usar mais de 2 font families no mesmo artefato.
