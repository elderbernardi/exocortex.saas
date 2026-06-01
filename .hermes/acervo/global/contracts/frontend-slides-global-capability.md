---
title: Frontend Slides Global Capability
created: 2026-06-01
updated: 2026-06-01
nature: instrucoes
kind: contract
scope_mode: global
scope_slug: null
applies_to: [exocortex-frontend-slides, personal-artifact-workspace, exocortex-design-system, estudio-criativo]
authority: canonical
operational_mode: blocking
stability: active
sources:
  - https://github.com/zarazhangrui/frontend-slides
derived_from:
  - plans/frontend-slides-global/PLAN.md
confidence: high
promotion_policy: none
upstream:
  source_skill: zarazhangrui/frontend-slides
  assumed_version: 2.1.0
  coupling: adapter-only
tags: [frontend-slides, markdown, html, drive, artifacts, visual]
---

# Frontend Slides Global Capability

## Contrato

O Exocórtex trata Frontend Slides como capacidade global para exportar apresentações HTML premium a partir de fontes Markdown, Marp Markdown, PPTX ou briefs de deck.

A capacidade não pertence ao microverso ensino. Ela se adapta ao microverso ativo por Design System, contratos locais e intenção do usuário.

## Fonte canônica

Markdown permanece a fonte padrão.

```text
source/source.md
source/brief.md
source/slides.marp.md
assets/
```

HTML, PDF e ZIP são exports. Se HTML editado manualmente virar fonte de verdade, o manifesto precisa registrar a decisão e a divergência.

## Renderers

Marp continua a linha de produção para slides rotineiros, especialmente materiais didáticos, código, manutenção manual e PDF rápido.

Frontend Slides é renderer premium para apresentações que exigem direção visual, narrativa, motion, impacto ou entrega em browser.

## Design System

Antes de gerar previews ou deck final, o agente deve:

1. resolver microverso ativo;
2. ler `global/DESIGN.md`;
3. aplicar override `micro/{slug}/DESIGN.md`, quando existir;
4. ler contratos locais relevantes;
5. definir envelope visual: strict, balanced, expressive ou experimental.

A criatividade é permitida quando o usuário pedir ou o microverso permitir, mas nunca dispensa grounding no Design System.

## Export padrão

Google Drive privado é o destino padrão para entrega final de artefatos visuais ao usuário comum.

Vercel e outros deploys públicos são exceções. Criar conta externa é atrito alto e não deve ser caminho padrão.

Destino padrão quando nada for informado:

```text
exocortex/inbox
```

Destinos recomendados:

```text
exocortex/{microverso}/{ano}/apresentacoes
exocortex/ensino/{ano}/{disciplina}/slides-premium
exocortex/gabinete/{ano}/apresentacoes
exocortex/dev/{ano}/artefatos
exocortex/estudio-criativo/{ano}/decks
```

## Draft-First

Upload privado no Drive do próprio usuário conta como export pessoal quando solicitado.

Exigem aprovação explícita antes da execução:

- link público;
- compartilhamento com terceiros, turma, domínio ou organização;
- envio por email/mensagem;
- deploy Vercel ou equivalente;
- publicação em site, release, repositório público ou documento colaborativo.

## Estúdio Criativo

Estúdio Criativo e Frontend Slides são capacidades pares.

- Estúdio Criativo fornece direção de arte, moodboard, tese estética e exploração.
- Frontend Slides empacota em apresentação navegável e exports HTML/PDF/ZIP/Drive.

Quando uma apresentação exige linguagem visual forte, Frontend Slides deve consultar Estúdio Criativo. Quando Estúdio Criativo precisa entregar apresentação, deve usar Frontend Slides.

## Regras bloqueantes

1. Não substituir Marp como padrão de produção seriada.
2. Não gerar deck final visual sem resolver Design System.
3. Não publicar em Vercel por padrão.
4. Não deixar HTML substituir Markdown sem manifesto.
5. Não ignorar microverso ativo.
6. Não entregar deck visual sem ZIP quando houver assets ou fonte associada.
7. Não exibir metadados internos nos slides: “Option A”, “template”, “preview.md”, paths, labels de processo.
