# 14 — Final Recommendation

## Preserve (it was right)

- **Markdown-first canonical truth + derived indexes** — now independently validated by both first-party labs and benchmark evidence (02 §A/E). The Acervo's core bet was correct.
- **The routing doctrine** (ADR-019/020/021): pointers not copies, tools-first recall, hard fast-layer budgets. *"Hindsight aponta. Acervo decide. MEMORY.md só inicializa"* stays the constitution of the memory system.
- **4 layers** (macro/global/micro/shared), microverso isolation with scope guard, Draft-First, lifecycle-without-deletion (deprecate→quarantine→purge), the control plane (acervoctl/MCP), the syndic, append-only journals.

## Abandon

- **The triple classification** (`type`/`excrtx_type`/`nature`) → one `type` axis, directory-enforced.
- **Deprecation as the only conflict verb** → supersede/dispute/coexist; deprecation reserved for junk.
- **Hand-maintained indexes and the two conflicting `groups.md`** → generated MOCs + single `groups.yaml`.
- **docBrain as a second canonical brain** → demoted to ingestion engine; Acervo is the only truth.
- **Approval-less trust in ingested web/email content** → trust gate (this is now a documented attack class, not a hypothetical).

## Redesign

- **Schema v0.2**: `status` scalar, bitemporal-lite (`observed_at`, `valid_from/until`), epistemic tier (`epistemic`, `confidence`, `sources`, `extraction`), structured supersedence. (05, 13-artifacts.)
- **Three missing memory types get homes**: episodes (what happened), entities (who), intentions (what's promised). These are the executive's three most frequent questions and today none has a canonical answer.
- **Contradiction as first-class** conflict objects with retrieval banners.
- **Consolidation loop** (daily distillation + weekly audit) — the system currently only forgets; it must also digest.
- **Retrieval as routed policy with budgets and labeled packing** (07), with a measured fallback ladder.

## Implement first (order is load-bearing)

Phase 0 (repairs) → Phase 1 (schema+catalog) → Phase 2 (write pipeline) → Phase 3 (retrieval). Everything after that improves a working system; everything before Phase 3 is foundation. See 12-roadmap.md cut criteria: if only one thing survives, make it **Phase 6's eval harness** — an unmeasured memory system is a story.

## Test before coding

- **H2** (agentic+lexical vs Hindsight vs hybrid) — 3-way golden-set run; it decides how much retrieval machinery to build at all.
- **H9** (episode significance gate) — 2 weeks of manual episode flagging before automating.
- Migration dry-run on fixture before touching the live acervo.

## Requires human judgment (never automate)

- Dispute resolution (which claim wins), reflection→rule promotion, anything macro/contract, microverso merges/retirements, purge confirmations past the window, and the weekly 5 minutes that keep the human the owner of his own mind. The system's ambition is to make that ownership *cheap*, not to take it.

## The one-paragraph version for the executive

> Seu exocórtex já guarda bem; agora ele vai *lembrar* bem. Tudo continua em arquivos que você pode abrir e ler. O que muda: cada fato passa a dizer de onde veio, desde quando vale e com que confiança; reuniões e conversas importantes viram episódios consultáveis; pessoas e empresas ganham fichas com histórico; promessas ganham prazo e cobrança; contradições não somem — elas chegam a você como uma pergunta de uma linha; e uma bateria de testes prova, todo mês, que a memória não está inventando. Você gasta cinco minutos por semana decidindo o que só você pode decidir. O resto é serviço.
