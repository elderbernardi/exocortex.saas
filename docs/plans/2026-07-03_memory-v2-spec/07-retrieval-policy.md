# 07 — Retrieval & Context Packing Policy

## 1. Doctrine

1. **Scope before search** (P6): no query runs unscoped.
2. **Route by query shape, not one mechanism** (MemoryAgentBench lesson): entity / temporal / literal / semantic / procedural queries hit different first surfaces.
3. **Agentic search is primary at Acervo scale**; the semantic index (Hindsight) supplements for vague/associative queries; embeddings never outrank an exact metadata or lexical hit on names/dates/IDs.
4. **Load-the-view beats retrieve-the-chunks** when the scoped set fits budget (a microverso's `context/` + index is often < 10k tokens).
5. **Pointers before payloads** (ADR-020); read 1–5 canonical files, never "top-20 chunks".
6. **Pack with epistemic labels and citations; position best-first, runner-up-last** (lost-in-the-middle).
7. **Degrade gracefully** (P12): Hindsight → catalog FTS5 → ripgrep. Log which rung answered.

## 2. Routing table (task type → strategy)

| Task | First surface | Then | Notes |
|---|---|---|---|
| Factual question | catalog filter (`type:knowledge`, scope, valid-now) + FTS5 | hindsight_recall if <2 hits | dispute banners attached |
| Email/draft in exec's style | persona + `USER.md` + 2–3 recent artifacts of same genre | entity page of recipient | style loads verbatim (P8) |
| Review proposal | scope contracts + pricing knowledge (valid-now) + client entity + open intentions to that client | related decisions | contracts outrank everything (authority ladder) |
| Client history | entity page → its episodes (time-desc) | session_search for literal quotes | |
| Cross-microverso synthesis | groups union scope; per-scope retrieval THEN merge labeled by scope | | never blend unlabeled (contamination) |
| Morning briefing | intentions (due), calendar, kanban, episodes (last 24h), context heads of active scopes | | assembled by routine, not ad-hoc search |
| "Where did we stop" / continuity | latest episodes in scope + open intentions | hindsight_recall | this is what episodes exist for |
| Conflict check on new info | detect_conflict (08) — catalog by entity+tags, then semantic | | write-path, not chat-path |
| Temporal ("what did we believe in March") | catalog with `as_of` filters incl. superseded | git history if needed | results labeled HISTORICAL |
| Execução (DO) | operational pack: contracts, workflow, templates, context head | | budget-tight |
| Evolução (THINK) | reflections, open conflicts, related decisions' *alternatives*, questions | | retrieve tension, not conclusions (P11) |
| Manutenção (CLEAN) | catalog health queries (stale, orphans, drafts, expired reviews) | | no semantic search needed |

## 3. Pseudocode (contract for `acervoctl` / memory-manager v3)

```python
def resolve_scope(query, session):                      # 06 §7
    for strategy in [explicit_slug, entity_home, session_anchor, classifier]:
        scope, conf = strategy(query, session)
        if conf >= THRESHOLD: return scope
    return ask_user_if_write_else(GLOBAL)

def retrieve_context(task, scope, budget):
    route = classify_query(task)          # entity|temporal|literal|semantic|procedural|factual
    view = load_scope_view(scope)         # context head + index (always; ~1-3k tokens)
    if route == LITERAL:   cands = session_search(task.quote)
    elif route == ENTITY:  cands = entity_pages(task.entities) + episodes_of(task.entities)
    elif route == TEMPORAL:cands = catalog(scope, as_of=task.time, include_superseded=True)
    else:
        cands  = catalog(scope, facets(task))            # metadata filter FIRST
        cands += fts5(task.keywords, scope)              # lexical (names/IDs)
        if len(active(cands)) < MIN or route == SEMANTIC:
            cands += hindsight_recall(task.query)        # pointers → paths
    cands = dedupe_by_path(cands)
    ranked = rank(cands, key=(scope_match, authority,    # contract>decision>knowledge>episode>reflection
                              validity_now, recency_if_volatile, lexical_or_sim_score))
    files = read_canonical(ranked[:5])                   # Plane 1 always wins over index text
    return pack_context(view + files, budget)

def pack_context(memories, budget):
    for m in memories:                                   # label EVERYTHING
        m.header = f"[{m.type}|{m.epistemic}|{m.confidence}|{m.status}|{m.scope}] {m.path}"
        if m.disputed_by: m.header += " ⚠ DISPUTED: " + summary(m.disputed_by)
        if m.status != "active": m.header += " ⏳ HISTORICAL"
    order = [best] + middle_by_relevance_desc + [second_best]   # U-curve packing
    while tokens(order) > budget:
        victim = lowest_rank(order)
        order.replace(victim, pointer_stub(victim))      # degrade to pointer, not silent drop
    return order

def detect_conflict(candidate, scope):                   # write-path (08 §4)
    overlap = catalog(scope, entities=candidate.entities, tags=candidate.tags,
                      type=candidate.type, status="active")
    for old in overlap:
        rel = judge(candidate, old)                      # same-assertion | supersession | dispute | coexist
        if rel == SUPERSESSION and old.class == "volátil": yield ("supersede", old)
        elif rel == DISPUTE:                              yield ("dispute", old)
        elif rel == SAME:                                 yield ("noop-or-enrich", old)

def write_memory(candidate, scope):        # full pipeline in 04 §3 / 08
def promote_memory(obj):                   # volátil→perene | micro→global | reflection→contract
    # requires: read target-layer rules; global/macro/contract promotions = Draft-First
def deprecate_memory(obj, reason):         # only for wrong/junk; supersession is NOT deprecation
def consolidate_episode(session):          # 04 §4 step 1; significance gate first
    if not significant(session): return None             # decisions? commitments? artifacts? flag?
    ep = draft_episode(session)                          # summary, entities, decisions, open loops
    for d in ep.decisions:   propose(decision_object(d))
    for c in ep.commitments: propose(intention_object(c))
    for e in ep.entities:    enqueue_entity_refresh(e)
    return commit_via_pipeline(ep)                       # journaled, indexed
```

## 4. Budgets

| Context | Retrieval budget (tokens) |
|---|---|
| Quick factual answer | ≤ 2 000 |
| Drafting/execution task | ≤ 6 000 |
| Review/strategy | ≤ 12 000 |
| Briefing | ≤ 4 000 (it's a digest, not an archive dump) |
| Explicit "pesquisa profunda no acervo" | negotiated, up to full scope view |

Budget exhaustion degrades items to pointer stubs (path + description) — the executive/agent can pull them next turn. Never silently drop; never exceed.

## 5. Citation & fallback

Every packed item carries its path; every answer that used retrieval cites paths short-form (`Acervo: micro/comercial/decisions/...`), consistent with the existing routing contract. If all rungs return nothing: say so explicitly ("não há registro no Acervo sobre X") — an exocortex that improvises around missing memory poisons trust (EX-49 applied to recall). Stale-protection: any retrieved file with `review_after < today` or `class: volátil` older than 90d gets a staleness flag in its header, and the answer must carry the caveat.
