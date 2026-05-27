# gpt-taste — UI Premium / Landing Pages

## Quando Ativar

Use este sub-skill quando o output visual for:
- Landing page, home page, página de produto, SaaS, marketplace ou campanha.
- Interface web premium, dashboard leve, app shell, mobile/web UI ou protótipo HTML.
- Qualquer peça onde a percepção de design, layout, motion e acabamento visual seja central.

Não use como default para brand boards puros (use brandkit) nem telas densas de métricas/data-heavy (use brutalist).

## Obrigatório: design_plan antes de gerar

Antes de escrever HTML/CSS/React/etc., produza internamente um design_plan com:
1. Objetivo: conversão, clareza, autoridade, desejo ou onboarding.
2. Audiência: quem precisa confiar, comprar, clicar ou entender.
3. Estrutura AIDA: Attention, Interest, Desire, Action.
4. Layout seed: resultado da randomização de composição.
5. Sistema visual: paleta, tipografia, textura, densidade, profundidade.
6. Component arsenal: 5-9 componentes escolhidos para esta peça.
7. Motion plan: microinterações e transições GSAP/framer/CSS.
8. Anti-slop checklist: riscos específicos do output.

O design_plan deve orientar a execução; não entregue rascunho genérico.

## Python-Driven Randomization

Quebre defaults estatísticos antes de decidir o layout. Quando houver código, use uma seed simples para variar escolhas:

```python
import random
seed = hash(project_name + audience + objective) % 10_000
random.seed(seed)
layout = random.choice([
    "asymmetric editorial hero + dense bento",
    "centered cinematic hero + orbiting cards",
    "split hero inverted + proof rail",
    "vertical scrollytelling + sticky product frame",
    "dashboard-as-landing + KPI narrative",
    "magazine grid + product cutaway",
])
palette_role = random.choice(["dark-luxury", "warm-minimal", "electric-contrast", "soft-technical", "mono-accent"])
```

Se não executar Python, simule a randomização conscientemente e registre a escolha no design_plan.

## Estrutura AIDA

Toda landing premium deve carregar a progressão:

1. Attention — headline forte, imagem/sistema visual distinto, promessa clara.
2. Interest — problema específico, mecanismo, diferenciação, contexto.
3. Desire — prova, transformação, casos, benefícios concretos, redução de risco.
4. Action — CTA claro, contraste alto, copy específica, fricção baixa.

Evite blocos soltos. Cada seção precisa avançar a narrativa.

## Hero Rule: 2-3 linhas no máximo

- Headline: máximo 2 linhas em desktop, 3 em mobile.
- Se passar disso: aumentar max-width, reduzir tracking/size, reescrever copy ou quebrar em kicker + headline + subhead.
- Subhead: 1-2 frases curtas, sem parágrafos densos.
- CTA primário deve ser visível acima da dobra.

## Gapless Bento Grid

Para bento grids:
- Use `grid-auto-flow: dense`.
- Varie spans: cards 1x1, 2x1, 1x2, 2x2.
- Não deixe buracos visuais nem cards desalinhados sem intenção.
- Cada card deve ter hierarquia interna: eyebrow opcional, título, métrica/visual, texto curto.
- Evite bordas cinza padrão. Use profundidade, blur, textura, gradientes sutis ou materiais.

CSS base:

```css
.bento {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  grid-auto-flow: dense;
  gap: clamp(12px, 1.4vw, 22px);
}
.card-wide { grid-column: span 6; }
.card-tall { grid-column: span 4; grid-row: span 2; }
.card-hero { grid-column: span 8; grid-row: span 2; }
```

## Motion: GSAP / Premium Interaction

Motion deve parecer projetado, não decorativo:
- Hero entrance: stagger leve, blur-to-sharp, y 18-36px, opacity 0→1.
- Cards: hover com transform pequeno, luz/gradient follow ou border glow controlado.
- Scroll: reveal por seção, sticky product frame, counters, parallax sutil.
- Tempo: 0.6-1.1s, easing `power3.out`, nada frenético.
- Respeite `prefers-reduced-motion`.

Exemplo:

```js
gsap.from("[data-reveal]", {
  y: 28,
  opacity: 0,
  filter: "blur(10px)",
  duration: 0.9,
  ease: "power3.out",
  stagger: 0.08,
  scrollTrigger: { trigger: "[data-reveal]", start: "top 82%" }
});
```

## Component Arsenal

Escolha componentes intencionais, não todos de uma vez:
- Hero editorial/cinematic com visual proprietário.
- Proof rail com logos, números ou citações curtas.
- Bento grid de capacidades.
- Product frame com tela realista, não placeholder cinza.
- Sticky narrative / scrollytelling.
- Comparison table com contraste claro.
- Testimonial cards com textura humana.
- Pricing/offer cards com CTA específico.
- FAQ compacto.
- Footer com continuidade visual.
- Microcopy nos botões: evitar “Learn more” genérico quando possível.

## Anti-Slop UI

Remova imediatamente:
- Meta-labels como `SECTION 01`, `FEATURE 02`, `INTRO`.
- Layout sempre alternando imagem/texto esquerda-direita.
- Cards idênticos com ícones genéricos e sombras padrão.
- Gradientes roxo/azul de IA sem contexto de marca.
- Botões com contraste insuficiente.
- Headings quebrando em 4+ linhas.
- Mockups vazios com texto lorem ipsum.
- Espaçamento respirando demais sem densidade de informação.

## Pre-Flight Checklist

Antes de entregar:
- [ ] design_plan definido.
- [ ] AIDA evidente.
- [ ] Hero cabe em 2-3 linhas.
- [ ] Bento sem gaps, com `grid-flow-dense` quando aplicável.
- [ ] Contraste de botões validado visualmente.
- [ ] Motion tem propósito e fallback reduced-motion.
- [ ] Nenhum meta-label genérico.
- [ ] Layout varia do default estatístico.
