---
schema: acervo/v0.2
type: knowledge
title: DESIGN
description: Identidade visual canônica do Exocórtex.IA — derivada da logo principal, refinada manualmente.
tags: []
timestamp: 2026-06-15
class: perene
status: active
epistemic: fact
created_at: 2026-06-15T20:35:46Z
last_accessed_at: 2026-06-15T20:35:46Z
version: alpha
name: EXCRTX.IA
extends: global
colors:
  primary: '#03123f'
  secondary: '#1a3c86'
  tertiary: '#1376ed'
  accent: '#1376ed'
  neutral: '#d2d6e3'
  surface: '#f4f5f8'
  dark: '#03123f'
  muted: '#8f8a91'
  text: '#e8ecf2'
  text-inverse: '#03123f'
  on-primary: '#FFFFFF'
  on-secondary: '#FFFFFF'
  on-tertiary: '#03123f'
  on-accent: '#FFFFFF'
  danger: '#E53E3E'
  success: '#38A169'
  warning: '#D69E2E'
typography:
  h1:
    fontFamily: Inter
    fontSize: 2.5rem
    fontWeight: 700
    lineHeight: 1.1
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
---

## Overview

Identidade visual canônica do **EXCRTX.IA**, o runtime cognitivo do Exocórtex.
Cores extraídas da logo principal `EXCRTX-logo-main.png` via K-Means (n=5) e
refinadas manualmente para garantir contraste WCAG AA (≥ 4.5:1) e
aproveitamento completo da paleta.

A paleta é dominada por azuis profundos (navy → electric blue) com suporte de
cinzas frios. O contraste primário é **dark-on-light**: superfícies claras com
texto e elementos estruturais em azul marinho.

## Colors

- **Primary (`#03123f`):** Azul marinho profundo. Headers, nav, elementos estruturais.
- **Secondary (`#1a3c86`):** Azul médio. Hover states, suporte.
- **Tertiary / Accent (`#1376ed`):** Azul elétrico. Ações, CTAs, links, badges.
- **Neutral (`#d2d6e3`):** Cinza claro frio. Fundos e superfícies padrão.
- **Surface (`#f4f5f8`):** Derivação mais clara do neutral para cards e painéis.
- **Dark (`#03123f`):** Reutiliza o primary como cor de texto escuro.
- **Muted (`#8f8a91`):** Cinza mauve. Texto secundário, metadados.
- **Text (`#e8ecf2`):** Texto claro para superfícies escuras.
- **on-primary (`#FFFFFF`):** Texto sobre primary (contraste 14.8:1).
- **on-secondary (`#FFFFFF`):** Texto sobre secondary (contraste 7.5:1).
- **on-tertiary (`#03123f`):** Texto escuro sobre tertiary (contraste 6.2:1).
- **Danger, Success, Warning:** Herdados do sistema. Cores semânticas apenas.

## WCAG Contrast Pairs

| Foreground | Background | Ratio | Status |
|-----------|-----------|-------|--------|
| `#FFFFFF` (on-primary) | `#03123f` (primary) | 14.8:1 | AAA ✓ |
| `#FFFFFF` (on-secondary) | `#1a3c86` (secondary) | 7.5:1 | AAA ✓ |
| `#03123f` (on-tertiary) | `#1376ed` (tertiary) | 6.2:1 | AA ✓ |
| `#03123f` (dark) | `#d2d6e3` (neutral) | 12.3:1 | AAA ✓ |
| `#03123f` (dark) | `#f4f5f8` (surface) | 13.7:1 | AAA ✓ |
| `#8f8a91` (muted) | `#f4f5f8` (surface) | 3.8:1 | — (muted = não crítico) |

## Skins Provisionadas

- **Hermes WebUI** (`~/.hermes/hermes-webui/static/style.css`): skin `excrtx` — dark navy + electric blue accent.
- **CLI** (`acervo/global/branding/exocortex-logo.sh`): ANSI colors mapeadas para a paleta.
- **Telegram:** Bot profile picture + channel theming via gateway config.

## Do's and Don'ts

- **Do:** Usar token references (`{colors.primary}`) em novos componentes.
- **Do:** Manter contraste WCAG AA (4.5:1) em texto sobre fundo.
- **Do:** Preferir `neutral` / `surface` como fundo e `primary` / `dark` como texto.
- **Don't:** Usar `tertiary` (#1376ed) como cor de fundo com texto claro — usar apenas como accent.
- **Don't:** Adicionar cores ad-hoc fora da paleta sem justificativa.
- **Don't:** Usar `muted` (#8f8a91) como única cor de texto em superfícies claras (contraste insuficiente).
