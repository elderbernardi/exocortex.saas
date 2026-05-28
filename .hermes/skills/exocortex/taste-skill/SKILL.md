---
name: taste-skill
description: Quality Gate Visual - seleciona automaticamente o sub-skill correto para outputs visuais premium
version: 1.0.0
metadata:
  hermes:
    tags: [exocortex, quality, visual, design, anti-slop]
---

# Taste Skill - Visual Quality Gate

Conjunto de sub-skills que quebram defaults estatísticos de LLMs na geração de UI e outputs visuais.

## Sub-Skills

### gpt-taste (UI premium / landing pages)
Ativar quando o output é uma landing page, produto web ou interface de usuário.
Regras: layout variado via randomização, estrutura AIDA, hero max 2-3 linhas, bento grid sem gaps, GSAP motion, sem meta-labels como SECTION 01.
Detalhes completos em: gpt-taste.md

### brandkit (identidade visual / marca)
Ativar quando o output envolve identidade visual, logos, brand boards ou sistemas de cor/tipografia.
Detalhes completos em: brandkit.md

### brutalist (dados pesados / dashboards)
Ativar quando o output apresenta métricas, dashboards, visualização de dados ou interfaces data-heavy.
Estilo: tipografia Swiss, estrutura raw, alto contraste, linguagem visual mecânica.
Detalhes completos em: brutalist.md

## Routing Automático

O orquestrador seleciona o sub-skill por contexto:
- Output de dados/métricas → brutalist
- Output de identidade/marca → brandkit
- Output de landing/produto/UI → gpt-taste

## Integração com Design System

Antes de gerar qualquer output visual, verificar se `exocortex-design-system`
tem tokens resolvidos para o microverso ativo:

1. Chamar RESOLVE da skill `exocortex-design-system`
2. Se tokens existem → usar como base para cores, tipografia e spacing
3. Se não existem → aplicar defaults do sub-skill ativo (gpt-taste/brutalist)

Fluxo completo: `brandkit` (criação) → `exocortex-design-system` (tokens) → `taste-skill` (validação)

## Anti-Slop Checks

Antes de entregar qualquer output visual:
- Headings com mais de 3 linhas? Alargar container.
- Grid com espaços vazios? Aplicar grid-flow-dense.
- Meta-labels genéricos (SECTION 01)? Remover.
- Texto de botão invisível? Fixar contraste.
- Layout repetitivo (sempre left/right)? Variar.
