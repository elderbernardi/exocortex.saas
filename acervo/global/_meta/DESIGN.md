---
type: context
title: DESIGN
description: Sistema visual para artefatos gerados pelo Exocórtex em nome do executivo.
tags: []
timestamp: 2026-05-27
class: perene
created_at: 2026-05-27T20:48:57Z
last_accessed_at: 2026-05-27T20:48:57Z
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
