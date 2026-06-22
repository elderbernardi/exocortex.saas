# Competitive Digital Maturity Assessment

Use when supplementing thin B2B/regional research with competitor analysis — assess
how digitally mature competitors are relative to the target company.

## When to Apply

Trigger when the executive asks:
- "What are competitors doing with AI/digital/tech?"
- "Where is [company] being outpaced?"
- "How do competitors compare digitally?"
- Sales visit prep for B2B companies in low-tech sectors

## Methodology

### Step 1 — Identify competitors

From Google News RSS + last30days engine output, extract company names that appear
alongside the target in trade publications, industry association sites, and news.

Prioritize: same region, same product category, similar scale.

### Step 2 — Probe digital presence

For each competitor + the target, run lightweight curl probes:

```bash
# Check if domain resolves and returns content
curl -s -o /dev/null -w '%{http_code}' -L -A 'Mozilla/5.0' "https://$domain"

# Extract signals of digital maturity
curl -s -L -A 'Mozilla/5.0' "https://$domain" | python3 -c "
import sys, re
c = sys.stdin.read().lower()
signals = {
    'ecommerce': 'Loja virtual / portal B2B',
    'login': 'Área do cliente / portal',
    'whatsapp': 'WhatsApp Business integrado',
    'chatbot': 'Chatbot / atendimento automatizado',
    'catalogo': 'Catálogo digital',
    'app': 'Aplicativo mobile',
    'blog': 'Marketing de conteúdo',
    'sac': 'SAC estruturado',
    'portal': 'Portal do cliente/fornecedor',
    'marketplace': 'Presença em marketplace',
    'cotacao': 'Sistema de cotação online',
}
for signal, label in signals.items():
    if signal in c:
        print(f'  [+] {label}')
"
```

### Step 3 — Map the landscape

Build a comparison table:

| Company | Site status | Digital signals found | IA mention? | Maturity level |
|---|---|---|---|---|
| Target | domain resolves? | signals list | yes/no | ████░░░░░░ |
| Competitor A | ... | ... | ... | ... |

### Step 4 — Read the absence

**Zero signals is a finding, not a failure.** When no competitor in the sector
shows IA adoption or advanced digital presence:

- Label the sector as "digital desert" — no one is doing it
- Frame the gap as **opportunity** for the target, not just weakness
- The sales angle becomes: "You can be the first mover"

### Step 5 — Cross-reference with trade events

Check if the target or competitors are exhibiting at industry events happening
*during or near* the research date. Trade show presence (or absence) is a strong
signal of market posture.

For Brazilian cleaning products sector: ACATS ExpoSuper (annual, June, Balneário
Camboriú/SC).

## Signal Interpretation Guide

| Signal | What it means | Typical sector |
|---|---|---|
| SPA (JS-only site, 0 chars without JS) | Modern frontend, some digital investment | Mid-market+ |
| WordPress + WhatsApp | Basic digital presence, manual sales | Small/mid B2B |
| No site / domain doesn't resolve | Offline-first, relationship-based sales | Family businesses |
| Ecommerce/portal B2B | Digital sales channel mature | Distributors |
| Chatbot/AI mention in news | Leading edge — rare in regional B2B | Enterprise only |
| CRM/ERP mentioned in news | Back-office digitalization in progress | Growing manufacturers |
| Trade show presence (ExpoSuper, etc.) | Active commercial posture, industry engagement | All sizes |

## Pitfalls

- **SPA ≠ advanced digital.** A React site may just be a modern landing page with
  no backend integration. Treat JS-only sites as "presence exists" not "digitally mature."
- **WhatsApp ≠ digital sales.** Most Brazilian B2B companies use WhatsApp manually.
  Only count it as a digital signal if there's evidence of automation (chatbot, catalog
  integration, order-taking).
- **Domínio não resolve pode ser temporário.** Try `www.` prefix, `.ind.br`, `.com`
  variants before concluding the company has no site.
- **Ausência de sinal em IA não significa que não usam.** Many companies use AI
  operationally without press releases. The absence in news/search means they're
  not *marketing* it — which is still useful for sales positioning.

## Session Example: Guimarães Produtos de Limpeza vs Concorrentes (2026-06-17)

| Company | Digital Signals | Maturity |
|---|---|---|
| Copapel (R$164,7M) | SPA moderna, JS-dependente | ███░░░░░░░ |
| Girando Sol (R$1 bi) | WordPress + WhatsApp + SAC | ██░░░░░░░░ |
| Guimarães (target) | Sem site funcional, YouTube só | █░░░░░░░░░ |
| Super Globo (R$16M inv.) | Domínio não resolve | ░░░░░░░░░░ |

Resultado: **Deserto digital.** Nenhum concorrente usa IA para gestão ou
atendimento. Oportunidade de venda: "Sejam os primeiros."
