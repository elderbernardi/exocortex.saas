---
version: alpha
name: Identidade Visual Global — IFSul
description: Tokens visuais globais (padrão institucional IFSul) para artefatos gerados pelo Exocórtex.
colors:
  primary: "#2f9e41"          # IFSul verde
  secondary: "#1d7a2d"        # IFSul verde escuro
  accent: "#cd191e"           # IFSul vermelho (destaque/ênfase)
  neutral: "#f8f9fa"          # superfícies neutras
  dark: "#202124"             # texto/contraste
  danger: "#cd191e"           # estados críticos (alinha com vermelho institucional)
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
    backgroundColor: "{colors.secondary}"
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
    textColor: "{colors.danger}"
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
    textColor: "#FFFFFF"
    rounded: "{rounded.lg}"
---

## Overview

Sistema visual global para artefatos gerados pelo Exocórtex.
Baseado na identidade institucional do IFSul (verde + vermelho), com tipografia neutra.
Overrides por microverso continuam permitidos (cascade global  micro).

Estes tokens são carregados sob demanda pela skill `exocortex-design-system`
quando uma tarefa produz output visual (relatórios, dashboards, decks, etc.).

## Colors

- **Primary ({colors.primary}):** Verde institucional IFSul. Chamadas visuais, títulos, ênfase.
- **Secondary ({colors.secondary}):** Verde escuro. CTA sólido (botões), estados de foco.
- **Accent ({colors.accent}):** Vermelho institucional. Destaques, marcações e ênfase.
- **Neutral ({colors.neutral}):** Fundos e superfícies.
- **Dark ({colors.dark}):** Texto principal e contraste.
- **Danger ({colors.danger}):** Estados críticos/erro (alinha com vermelho institucional).

## Typography

Inter como fonte principal para headings e corpo de texto.
JetBrains Mono para código, dados tabulares e labels técnicos.
Escala de heading: h1 (2.5rem/700) → h2 (1.75rem/600) → body (1rem/regular).

## Layout & Spacing

Escala de spacing em múltiplos de 8px: sm (8), md (16), lg (24), xl (48).
Border radius conservador: sm (4px) para botões, md (8px) para cards.

## Components

- `button-primary` — Ação principal em **verde escuro** (`{colors.secondary}`) para garantir contraste WCAG AA com texto branco.
- `card` — Container de conteúdo com fundo branco e padding generoso.
- `alert-danger` / `alert-success` — Feedback visual para estados.
- `badge` — Destaque pontual em **vermelho** (`{colors.accent}`) com texto branco.

## Do's and Don'ts

- **Do:** Usar token references (`{colors.primary}`) em novos componentes.
- **Do:** Manter contraste WCAG AA (4.5:1) em texto sobre fundo (lint obrigatório quando mexer em tokens).
- **Do:** Usar `colors.accent` (vermelho) para **destaque pontual/ênfase** quando necessário — não confundir com estado de erro.
- **Do:** Reservar `colors.danger` + `alert-danger` para **erro/estado crítico**.
- **Don't:** Adicionar cores ad-hoc fora da paleta sem justificativa.
- **Don't:** Tratar todo vermelho como erro — aqui ele também é semântica de marcação/ênfase.
- **Don't:** Usar mais de 2 font families no mesmo artefato.
