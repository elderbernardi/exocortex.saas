---
version: alpha
name: Exocórtex Executive Style
description: Tokens visuais do executivo. Aplicado a artefatos visuais sob demanda.
colors:
  primary: "#1a73e8"
  secondary: "#34a853"
  tertiary: "#5f6368"
  accent: "#fbbc04"
  neutral: "#f8f9fa"
  dark: "#202124"
  danger: "#ea4335"
  success: "#34a853"
  warning: "#fbbc04"
  on-primary: "#FFFFFF"
  on-secondary: "#FFFFFF"
  on-tertiary: "#FFFFFF"
  on-accent: "#202124"
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

## Schemas

### sales-ai

Esquema cromático derivado de marca institucional (#223874). Azul confiança + Laranja ação.
Ativado por microversos que usam `extends: global` e sobrescrevem tokens de cor.

| Token | Hex | Função |
|---|---|---|
| primary | `#223874` | Marca, headers, nav |
| secondary | `#5a6e9a` | Suporte, hover, backgrounds |
| tertiary | `#1f6e5a` | Destaque sutil, tags |
| accent | `#e88d25` | Ação, CTAs, badges |
| neutral | `#f4f4f6` | Fundos e superfícies |
| dark | `#101218` | Texto principal |
| on-primary | `#FFFFFF` | Texto sobre primary (11.1:1) |
| on-secondary | `#ffffff` | Texto sobre secondary (5.1:1) |
| on-tertiary | `#FFFFFF` | Texto sobre tertiary (6.1:1) |
| on-accent | `#101218` | Texto sobre accent (7.4:1) |

**Showcase:** `sales-AI/_design/showcase.html`

Microverso correspondente: `acervo/micro/sales-ai/DESIGN.md`

---

## Overview

Sistema visual para artefatos gerados pelo Exocórtex em nome do executivo.
Valores iniciais são placeholders genéricos — personalizar via `brandkit`
quando o executivo decidir definir identidade visual própria.

Estes tokens são carregados sob demanda pela skill `exocortex-design-system`
quando uma tarefa produz output visual (relatórios, dashboards, decks, etc.).

## Colors

- **Primary (#1a73e8):** Ações, links, headings de destaque.
- **Secondary (#34a853):** Suporte, métricas positivas, confirmações.
- **Tertiary (#5f6368):** Destaque sutil — tags secundárias, labels informativos.
- **Accent (#fbbc04):** Alertas, destaques, badges, atenção.
- **Neutral (#f8f9fa):** Fundos, superfícies, cards.
- **Dark (#202124):** Texto principal, contraste alto.
- **Danger (#ea4335):** Erros, alertas críticos, ações destrutivas.
- **Success (#34a853):** Confirmações, métricas positivas (igual secondary por default).
- **Warning (#fbbc04):** Alertas de atenção (igual accent por default).
- **on-primary (#FFFFFF):** Texto sobre primary (contraste garantido).
- **on-secondary (#FFFFFF):** Texto sobre secondary.
- **on-tertiary (#FFFFFF):** Texto sobre tertiary.
- **on-accent (#202124):** Texto sobre accent.

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
