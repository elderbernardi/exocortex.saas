---
name: excrtx-quality-taste
description: Visual Quality Gate — auto-selects the correct sub-skill for premium
  visual outputs
version: 1.1.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - quality
    - visual
    - design
    - anti-slop
    calibration:
    - feature_id: EX-19
      calibration_prompt: "Para qualquer geração visual ou de UI (HTML/CSS):\n- Roteie\
        \ automaticamente entre:\n  1. 'gpt-taste' (interfaces premium): Bento grid\
        \ sem gaps, animações sutis, hero headers curtos (2-3 linhas), sem seções\
        \ genéricas.\n  2. 'brutalist' (painéis e dados pesados): Alta densidade de\
        \ informações, fontes monoespaçadas, alto contraste, estilo técnico.\n  3.\
        \ 'brandkit' (identidades): Paletas de cores e tipografias exclusivas resolvendo\
        \ os tokens do Design System.\n- Faça pre-flight checks: rejeite headings\
        \ > 3 linhas, grids desiguais com lacunas e layouts repetitivos de alternância\
        \ simples."
      test_prompt: Desenhe uma interface web simples em HTML/CSS para monitorar os
        servidores de produção.
      acceptance_criteria: O agente deve rotear para o estilo 'brutalist' (painel
        denso de dados). O HTML gerado deve possuir fontes monoespaçadas, alto contraste,
        sem seções genéricas ou tags fictícias.
      remediation_tip: Falha no Visual Gate. Roteie para brutalist/gpt-taste, use
        bento grids/Swiss typography e remova marcações genéricas de template.
---
# Taste Skill — Visual Quality Gate

Sub-skills that break LLM statistical defaults in UI and visual output generation.

## Sub-Skills

### gpt-taste (premium UI / landing pages)
Activate when the output is a landing page, web product, or user interface.
Rules: varied layout via randomization, AIDA structure, hero max 2-3 lines, bento grid without gaps, GSAP motion, no meta-labels like SECTION 01.
Full details: gpt-taste.md

### brandkit (visual identity / branding)
Activate when the output involves visual identity, logos, brand boards, or color/typography systems.
Full details: brandkit.md

### brutalist (data-heavy / dashboards)
Activate when the output presents metrics, dashboards, data visualization, or data-heavy interfaces.
Style: Swiss typography, raw structure, high contrast, mechanical visual language.
Full details: brutalist.md

## Auto-Routing

The orchestrator selects the sub-skill by context:
- Data/metrics output → brutalist
- Identity/branding output → brandkit
- Landing/product/UI output → gpt-taste
- Book cover/editorial packaging → brandkit + editorial cover pre-flight

## Campaign Landing Depth Gate

For campaign, institutional, education, event, recruitment, or product landing pages with an existing knowledge base, visual tokens alone are insufficient. Before writing HTML/CSS:

1. Read governance, campaign strategy, canonical content, approved assets, and channel constraints.
2. Combine creative direction with editorial architecture when the page must explain a portfolio, offer, or decision.
3. Turn the campaign concept or local theme into information architecture or interaction — never leave it as decorative copy.
4. Inventory the substance available for each offer: audience, concise description, learning/content focus, fields of action, verified official links, and next step.
5. Integrate verified conversion and evidence channels where relevant (for example WhatsApp, Instagram, application portal, course sites); never add fake feeds or unverified contacts.
6. Reject the first composition if another organization could use it by swapping only the logo and colors. A generic hero plus equal cards does not satisfy a campaign with richer domain structure.

Use `references/campaign-landing-depth-gate.md` for the full context-to-interface workflow and critique checklist.

### Education portfolio landing pattern

When an education landing presents several courses, preserve two depths instead of forcing one component to do everything:

1. Keep a compact comparison surface for course, level, duration, schedule, and regulated status.
2. Organize detailed profiles by a domain-derived taxonomy such as area, level, or trajectory. Core decision content must remain visible in the active panel: affinity, what the course teaches, professional capabilities, and fields of work. Do not hide these four fields behind accordions merely to shorten the page.
3. Separate evidence by scope. Campus or school indicators such as ENEM must never look like individual course scores. Course-level indicators such as MEC concepts need their own block, with indicator, scale, edition, act, source, and validation state.
4. User-provided metrics may appear in an internal DRAFT only when the page names the unresolved source or act gate. Never let visual prominence erase provenance uncertainty.
5. On mobile, reserve the fixed action bar for the two highest-value service actions. Prefer application or process portal plus direct orientation such as WhatsApp; remove social discovery from the fixed bar when it competes visually, while preserving it in navigation or the channel section. Give the document bottom padding at least equal to the fixed bar height, require 44 px minimum targets, and validate in a real viewport because full-page screenshots can place fixed controls over arbitrary content and create a false defect.

See `references/education-course-landing-patterns.md` for the detailed content matrix, evidence taxonomy, fixed-action rules, and QA checks.

## Design System Integration

Before generating any visual output, check whether `excrtx-quality-designsys`
has resolved tokens for the active microverso:

1. Call RESOLVE from `excrtx-quality-designsys`
2. If tokens exist → use as base for colors, typography, and spacing
3. If tokens don't exist → apply defaults from the active sub-skill (gpt-taste/brutalist)

Flow: `brandkit` (creation) → `excrtx-quality-designsys` (tokens) → `excrtx-quality-taste` (validation)

## Exocórtex Governance

- **Execution vector:** create or fix a visual deliverable, then run the appropriate gate on the rendered output.
- **Maintenance vector:** audit an existing visual system, report failures and correct local artifacts when the requested scope permits.
- **Evolution vector:** when the executive is comparing meanings or positioning rather than requesting production, expand alternatives before recommending a direction.
- **Draft-First boundary:** rendering, linting, local file edits and self-delivery to the executive are internal. Publishing, sharing, deploying or sending the visual output to third parties requires an explicit approved DRAFT.
- **Evidence:** record the actual viewport, page, spread, renderer output or screenshot used for the verdict. Never approve from source code alone when a render is possible.

## Anti-Slop Checks

Before delivering any visual output:
- Headings longer than 3 lines? Widen container.
- Grid with empty spaces? Apply grid-flow-dense.
- Generic meta-labels (SECTION 01)? Remove.
- Invisible button text? Fix contrast.
- Repetitive layout (always left/right)? Vary.

## Editorial Book-Cover Gate

For trade books, manuals presented as books, or any full-wrap cover, generic visual QA is insufficient. Require front, provisional spine and fourth cover/back; test title readability at 160 px; separate the public title from framework/runtime names; and reject generic AI art, technical labels on the printable cover, fabricated publishing data, or brand marks copied literally from terminal/CLI surfaces.

Render both a front-only contact sheet and a full-spread contact sheet. Capture renderer stderr and require zero warnings. Measure contrast on final text/background pairs, document spine assumptions, and separate technical PASS from market positioning. Use `references/editorial-book-cover-preflight.md` for the complete gate.

## Landing pages institucionais e campanhas públicas

Quando a landing usa marca oficial, edital, datas ou dados regulatórios, o gate visual também precisa preservar governança e resiliência:

1. **Arte oficial sem reconstrução:** prefira exibir a peça fornecida inteira. Se a proporção desktop não funcionar no mobile, use outra peça oficial aprovada para o formato; não recorte lockup, assinatura ou pessoas para forçar responsividade.
2. **DRAFT visível e não indexável:** enquanto faltarem fatos ou aprovação, mantenha aviso de revisão e `noindex, nofollow`. Remova ambos somente no gate de publicação.
3. **Dados bloqueados continuam ausentes:** não transforme placeholders regulatórios em copy pública. Mostre a fonte oficial e explique o que ainda depende dela.
4. **Motion deve falhar aberto:** conteúdo com reveal por `IntersectionObserver` precisa permanecer acessível se a observação falhar. Use fallback curto que revele tudo e respeite `prefers-reduced-motion`.
5. **Auditoria em viewports reais:** capture ao menos desktop e mobile com dimensões explícitas. Verifique primeira dobra, menu móvel, título, peça oficial, CTAs, overflow e alvos de toque.
6. **Capture por viewport e página inteira:** screenshots full-page podem distorcer elementos `sticky` e registrar itens ainda não revelados. Use-as para cobertura, mas julgue composição com capturas do viewport após rolagem real.
7. **Interações fazem parte do visual:** teste filtros, menu, acordeões, foco e console antes de aprovar. Uma tela bonita com estados quebrados reprova.

Checklist executável e critérios de evidência: `references/public-campaign-landing-review.md`.

## When to Use

Activate when:

- creating or auditing any visual artifact, interface, landing, dashboard, identity, campaign piece or editorial cover;
- selecting the appropriate visual sub-skill;
- deciding whether a rendered output is deliverable.

**Don't use for:** prose-only, data-only or code-only tasks without a visual surface.

## Procedure

1. Resolve the active design system.
2. Route to brandkit, gpt-taste, brutalist or the editorial-cover gate.
3. Load the specialized reference required by the surface.
4. Render the real output and inspect the relevant viewport, page or spread.
5. Fix every failed check and repeat the gate before delivery.

## Pitfalls

- **Over-application**: Only activate when the skill's trigger conditions are met.
- **Missing context**: Ensure required dependencies and related skills are loaded.
- **Print-ready overclaim**: A visually approved mockup is not print-ready without final pagination, paper, binding, printer template, ISBN/barcode and author approval.

## Verification

- [ ] Active design tokens were resolved, or their absence was recorded before applying defaults
- [ ] Output type routed to brandkit, gpt-taste, brutalist or editorial-cover gate
- [ ] Specialized reference for the chosen surface was loaded and applied
- [ ] Anti-slop checks passed: hierarchy, contrast, density and repetition inspected
- [ ] Real render inspected at the relevant viewport, page or spread
- [ ] Full-wrap covers passed front, spine and fourth-cover checks when applicable
- [ ] Renderer warnings, contrast, thumbnail view and complete-spread view were verified for editorial covers
- [ ] External publication or third-party delivery remained blocked until explicit Draft-First approval
