---
name: excrtx-memory-manager
description: Unified Acervo Cognitivo skill. Reads, writes, searches, and manages knowledge across the 4 layers (macro/global/micro/shared)
  with context isolation.
version: 2.0.0
category: excrtx
platforms:
- linux
author: Exocórtex
metadata:
  hermes:
    tags:
    - exocortex
    - acervo
    - knowledge
    - wiki
    - memory
    - nature
    - search
    - scope
    related_skills:
    - llm-wiki
    - excrtx-memory-newmicro
    replaces:
    - nature-context
    - nature-knowledge
    - nature-contracts
    - nature-prompts
    - nature-persona
    - nature-workflows
    - nature-skills
    - nature-tools
    - nature-templates
    - nature-decisions
    - nature-reflections
    - exocortex-search
    calibration:
    - feature_id: EX-11
      calibration_prompt: 'Você gerencia o Acervo Cognitivo de 4 camadas: macro (identidade), global (regras universais),
        micro (domínios isolados por slug) e shared (pontes). Regras: Filtro de Domínio para decidir onde gravar, frontmatter
        YAML obrigatório, atualizar index.md e log.md após cada escrita. Nunca duplicar entre microversos.'
      test_prompt: Preciso documentar que decidimos usar PostgreSQL como banco para o projeto 'portal-vendas'. Grave essa
        decisão no lugar correto do acervo.
      acceptance_criteria: '1. O agente aplica o Filtro de Domínio: grava em micro/portal-vendas/decisions/ (não em global)

        2. O arquivo criado tem frontmatter YAML (title, created, nature: decisions, type)

        3. Atualiza index.md e log.md do microverso portal-vendas

        4. Se o microverso ''portal-vendas'' não existe, pergunta antes de criar'
      remediation_tip: 'FALHA: Escrita no escopo errado ou sem frontmatter. O Filtro de Domínio exige que informação de um
        domínio específico vá para ''micro/{slug}/''. Decisões vão em ''decisions/'', com frontmatter YAML obrigatório. Se
        gravou em global/ ou sem frontmatter, mova para o microverso correto e adicione o cabeçalho YAML.'
---
# Acervo Manager

Unified skill for operating on the Exocórtex Acervo Cognitivo.
Replaces the 7 individual Nature skills and `exocortex-search` (ADR-005).

The 11 Natures (context, knowledge, contracts, prompts, persona, workflows, skills, tools, templates, decisions, reflections)
are **data classification**, not distinct behaviors. This skill implements the common mechanics:
read, write, search, and promote — each Nature's semantics are defined by the SCHEMA
and frontmatter of the files themselves.

## When to Use

Activate when:
- The executive asks about facts, data, rules, processes, or tools in a domain
- A task needs to read or write to the Acervo Cognitivo
- The agent needs to search information across multiple microversos
- A Nature needs to be promoted (file → directory)
- The agent needs to resolve access scope between microversos

**Don't use for:** Creating new microversos (use `excrtx-memory-newmicro`). Installing microverso structure (use `excrtx-memory-mvinstall`). Operational memory providers like Hindsight (use `excrtx-memory-opsmemory`). Wiki adapter setup (use `excrtx-memory-wikiadapt`).

## Acervo Location

Resolve the acervo root **once** as an absolute path and use `$ACERVO` for **every**
read and write. **Never** use a cwd-relative `acervo/...` path — that writes memory into
whatever directory the agent happens to run from (e.g. a code repository), not the canonical
acervo, breaking isolation.

```bash
# Resolution order (matches setup/common.sh): explicit $ACERVO, then the Exocórtex
# workspace (the live acervo), then the Hermes-home scaffold only as a last resort.
ACERVO="${ACERVO:-${EXOCORTEX_HOME:-$HOME/exocortex}/acervo}"
[ -d "$ACERVO" ] || ACERVO="${HERMES_HOME:-$HOME/.hermes}/acervo"
```

> Note: `$HERMES_HOME/acervo` is typically an empty scaffold; the real canonical memory
> lives at `$EXOCORTEX_HOME/acervo`. Always operate on the resolved absolute `$ACERVO`.

## Architecture: 4 Layers

```
acervo/
├── macro/          # Layer 1: Identity (FLAT — always loaded)
├── global/         # Layer 2: Universal Operations (WIKI — index at boot)
├── micro/{slug}/   # Layer 3: Isolated Domains (WIKI — by scope)
└── shared/         # Layer 4: Cross-domain Bridge
```

Full details in `acervo/README.md`.

## Resuming (CRITICAL — do this every session)

At every session boot:

① **Read `macro/*`** — soul.md, valores.md, estilo.md (entire files, ~100 lines total)
② **Read `global/index.md`** — catalog of universal rules/processes/tools
③ **DO NOT load** micro/ or shared/ until a task defines the scope

```bash
cat "$ACERVO/macro/soul.md"
cat "$ACERVO/macro/valores.md"
cat "$ACERVO/macro/estilo.md"
cat "$ACERVO/global/index.md"
```

### Design System (On Demand)

- `global/DESIGN.md` is **NOT** loaded at boot (context economy)
- Loaded when: task demands visual output, `excrtx-quality-designsys` requests it, or `excrtx-quality-taste` needs validation
- Per-microverso override: `micro/{slug}/DESIGN.md` (optional, deltas only)
- Cascade: global = base, micro override wins. Skill `excrtx-quality-designsys` resolves merge.

---

## Operation: READ

Read content of any Nature in any layer.

### Procedure

1. **Resolve layer:**
   - Identity? → `macro/{file}.md` (direct read)
   - Universal? → `global/{nature}.md` or `global/{nature}/`
   - Specific domain? → `micro/{slug}/{nature}.md` or `micro/{slug}/{nature}/`

2. **Verify scope** (if reading from micro/):
   - Does the task have `scope.deny`? → Execute [SCOPE](#operation-scope)
   - Microverso blocked? → STOP. Declare: "Access to domain {slug} not permitted in this scope."

3. **Detect format (dual logic):**

   ```
   IF path is .md file:
     → direct file_read (entire content)
   ELIF path is directory:
     → read {nature}/_index.md (catalog)
     → identify relevant page by query
     → read specific page
   ```

4. **Cite source:** All presented information must indicate origin:
   `[Acervo: {layer}/{slug or nature}]`

5. **If not found:** Declare honestly:
   "I don't have this information in the Acervo. Shall I search externally?"

6. **Update `last_accessed_at`:** After a successful read of any Acervo file with frontmatter, update the `last_accessed_at` field in the file's YAML frontmatter to the current UTC datetime (`YYYY-MM-DDTHH:MM:SSZ`). This is a frontmatter-only update — do NOT log it in `log.md` (per log-convention §2.2, `last_accessed_at` updates are not logged). Skip this step for files without frontmatter (e.g. `macro/` identity files, `raw/` sources) or for `_index.md` catalog reads.

### Verification

- [ ] Presented information exists in the Acervo (never fabricate)
- [ ] Source cited in response
- [ ] Data with old `last_accessed_at` (or old `updated`) flagged as potentially outdated
- [ ] `last_accessed_at` updated on every read of a frontmatter-bearing file

---

## Operation: WRITE

Write content to the Acervo with Domain Filter.

### Procedure

1. **Domain Filter (MANDATORY before any write):**

   ```
   BEFORE writing, classify the content:

   1. Check task scope → Microverso blocked? → DO NOT write
   2. Content is SPECIFIC to this domain?
      → YES → write to micro/{slug}/{nature}
   3. Is it cross-domain (involves 2+ microversos)?
      → YES → shared/cross-refs/ + pointer (1 line) in each micro
   4. Belongs to another microverso?
      → YES → write there (if scope permits)
   5. Is it universal (valid for ALL contexts)?
      → YES → write to global/{nature}
   6. None of the above?
      → DISCARD
   ```

2. **Scope guard pré-WRITE (runtime obrigatório):**

   ```bash
   python scripts/exocortex_runtime_guard.py guard-write \
     --path "$TARGET_PATH" \
     --active-microverso "{slug}"
   ```

   - `allow` → prosseguir com a gravação
   - `deny` → bloquear com erro explícito de cross-microverso
   - Sem microverso ativo resolvido → falha dura; não escrever por adivinhação

3. **Write format:**
   - If Nature is file → append to existing file
   - If Nature is directory → create new wiki page with frontmatter
   - Mandatory YAML frontmatter on every new page (OKF v0.1 superset — see `docs/plans/2026-06-19_acervo-lifecycle-okf/SCHEMA.md`):
     ```yaml
     ---
     # OKF Canonical (mandatory)
     type: knowledge              # concept type: decision|memory|reflection|context|knowledge|artifact
     title: Descriptive Title
     description: One-line summary (≤ 120 chars)
     tags: [from SCHEMA taxonomy]
     timestamp: YYYY-MM-DD        # creation date (must equal date portion of created_at)

     # Acervo Extension (lifecycle — mandatory)
     class: volátil               # perene (permanent) or volátil (transient)
     created_at: YYYY-MM-DDTHH:MM:SSZ  # UTC creation timestamp

     # Acervo Extension (optional)
     # last_accessed_at: YYYY-MM-DDTHH:MM:SSZ  # set by agent on read; absent on new files
     # promoted_at: YYYY-MM-DDTHH:MM:SSZ       # present only if promoted volátil → perene

     # Legacy Retained (optional — carried forward from pre-migration schema)
     nature: {nature}             # directory routing key (context|knowledge|contracts|workflows|tools|skills|persona|...)
     excrtx_type: {fact|rule|workflow|tool|profile|lesson|context}  # old Acervo type; renamed from `type` to avoid OKF collision
     confidence: {high|medium|low}
     sources: [raw/source if applicable]
     ---
     ```

     **Field semantics:**
     - `type` — OKF concept type (mandatory). NOT the old Acervo type. Derived from directory path.
     - `excrtx_type` — legacy Acervo type (optional). The old `type` field, renamed during migration. Preserves whatever vocabulary the original file had.
     - `nature` — directory routing key (optional but recommended). Used by this skill to route reads/writes. Coexists with `type`.
     - `class` — lifecycle class. `perene` = never auto-deprecated; `volátil` = deprecation candidate. Derived from directory path if absent.

4. **Semantic revision hook (MANDATORY before commit — ADR-016):**
   Before writing the new file to disk, call `excrtx-memory-deprecate` to check for semantic overlap with existing files in the same container:
   - The skill searches for files with 2+ shared tags, title similarity, or entity matching.
   - **Direct contradiction found** → the old file is deprecated (`deprecated: true`, `deprecated_at`, `deprecated_reason`). The new file body gets a `Superseded:` link to the old.
   - **Partial overlap (new replaces old's claim)** → old is deprecated.
   - **Complementary overlap (different aspect)** → both coexist; no deprecation.
   - **Ambiguous** → no deprecation; new file gets a `Potential overlap with:` note; flagged for executive review.
   - **Never deprecate:** `class: perene` files, `promoted_at` files, `raw/` sources, files already `deprecated: true`, files in other microversos.
   - Conservative detection: only deprecate on clear, direct contradictions. When in doubt, flag — do not deprecate.

5. **Log operation** in `log.md` of the corresponding scope:
   - Write to micro/ → `micro/{slug}/_meta/log.md` (or `micro/{slug}/log.md` if no `_meta/`)
   - Write to global/ → `global/_meta/log.md` (or `global/log.md`)
   - Write to shared/ → `shared/_meta/log.md` (or `shared/log.md`)
   - Entry format (per `log-convention.md`): `- CREATED: {relative-path} ({class}) — {one-line description}`

6. **Update index.md** if new page created.

### Rules

- **NEVER** copy content between microversos — use cross-ref in `shared/`
- **NEVER** modify `raw/` in any layer — sources are immutable
- **NEVER** write domain A information in domain B
- Cross-ref pointer = 1 line: `> Cross: see shared/cross-refs/{slug}.md`

### Verification

- [ ] Domain Filter executed (content is in the right place)
- [ ] YAML frontmatter present on every new page
- [ ] log.md updated
- [ ] index.md updated (if new page)
- [ ] No cross-domain duplication

---

## Operation: PROMOTE

Convert Nature from file to directory when it exceeds ~150 lines.

### Procedure

1. **Detect candidate:** After any WRITE, check file lines:
   ```bash
   wc -l "$ACERVO/micro/{slug}/{nature}.md"
   ```

2. **If > ~150 lines:**

   a. Create directory: `micro/{slug}/{nature}/`

   b. Extract sections from file into separate pages:
      - Each `## Heading` becomes a page: `{heading-slug}.md`
      - Each page gets YAML frontmatter

   c. Create `_index.md` with page catalog

   d. Remove original file `{nature}.md`

   e. Update `micro/{slug}/index.md` (point to directory)

   f. Log in `micro/{slug}/log.md`:
      ```
      ## [YYYY-MM-DD] promote | {nature} file → directory ({N} pages)
      ```

3. **Wiki page split:** If an individual page > ~200 lines, split into 2+.

### Verification

- [ ] Directory created with `_index.md`
- [ ] All sections extracted as separate pages
- [ ] Original file removed
- [ ] Microverso index.md updated
- [ ] log.md records the promotion

---

## Operation: SEARCH

Search information across the 4 layers with priority.

### Procedure

1. **Resolve scope:** Which microversos are accessible? (see [SCOPE](#operation-scope))

2. **Search in priority order:**

   ```
   Priority 1: micro/{active-slug}/   ← most specific
   Priority 2: global/               ← universal rules/processes
   Priority 3: shared/cross-refs/    ← cross-references
   Priority 4: other micro/ (if in scope)
   ```

3. **Search mechanics (per layer):**
   - Read `index.md` → identify candidate pages by title/tags
   - If Nature is file → grep in content
   - If Nature is directory → grep in `_index.md` → read matching page
   - Use frontmatter `tags` for narrowing

4. **Lifecycle filtering (MANDATORY):**
   - **Skip `deprecated: true` files** — these are superseded and not part of active truth. Only include them if the executive explicitly asks for deprecated/historical content (e.g. "show me the old model config", "what did we believe before").
   - **Skip `.quarantine/` entirely** — quarantined files are not part of active memory under any circumstance. If the executive needs a quarantined file, they must explicitly reference the quarantine path or request a restore (see `excrtx-memory-quarantine`).
   - When returning results, note the `class` of each result (`perene` vs `volátil`) so the executive knows the lifecycle status.

5. **Return results with metadata:**
   ```
   [Acervo: micro/cliente-acme/knowledge] Result here
   [Acervo: global/contracts] Universal rule here
   ```

6. **If nothing found:** Declare and offer external search.

### Verification

- [ ] Scope verified before search
- [ ] Results indicate layer of origin
- [ ] Priority respected (micro > global > shared)
- [ ] Deprecated files excluded (unless explicitly requested)
- [ ] `.quarantine/` excluded entirely

---

## Operation: SCOPE

Resolve access firewall for a task.

### Procedure

1. **Read `shared/groups.md`** to get aliases:
   - `ALL` → list all directories in `micro/` (except `_template`)
   - `CLIENTS` → filter by SCHEMA.md `type: client`
   - `PROJECTS` → filter by SCHEMA.md `type: project`
   - Custom groups → resolve members

2. **Apply deny-list:**
   ```
   For each microverso:
     1. Is it in deny? → marked as BLOCKED
     2. Is it in allow? → UNBLOCKED (override)
     3. Result: allow ALWAYS overrides deny
   ```

3. **If no scope defined:** Everything accessible (open default).

4. **Return list of accessible microversos.**

### Examples

```yaml
# Only client ACME
scope: { deny: [ALL], allow: [cliente-acme] }
→ Accessible: [cliente-acme]

# Block clients, allow projects
scope: { deny: [CLIENTS] }
→ Accessible: [all projects + domains + roles]

# Everything open (default)
scope: {}
→ Accessible: [all]
```

---

## Natures Reference

The 7 Natures are data classification. Semantics of each:

| Nature | Content | When to Read | When to Write |
|---|---|---|---|
| `context` | Current situation, priorities, stakeholders | Task start in domain | Scenario change |
| `knowledge` | Facts, metrics, references | Factual question | New confirmed data |
| `contracts` | Conditional rules (WHEN/THEN) | Before actions in domain | New executive rule |
| `prompts` | Reusable prompts | Repetitive task | New validated prompt |
| `persona` | Voice, tone, style | When communicating in domain | New audience profile |
| `workflows` | Workflows, SOPs | Recurring task | New approved workflow |
| `skills` | Encapsulated capabilities | Specialized task | New skill created |
| `tools` | MCPs, APIs, integrations | Task requiring tool | New integration |
| `templates` | Templates (emails, docs) | Standardized output | New approved template |
| `decisions` | Architectural decisions (ADR) | Structural change | Decision made |
| `reflections` | Lessons learned | Similar task start | After incident/learning |

---

## Archiving

Superseded content is not deleted. Procedure:

1. Move wiki page to `_archive/{nature}/` (or `_archive/` at scope root)
2. Remove from `index.md`
3. Replace wikilinks `[[page]]` with plain text + "(archived)"
4. Log in `log.md`: `## [YYYY-MM-DD] archive | {page} (reason: {reason})`
5. **raw/ remains intact** — sources are immutable

---

## ADRs

- ADR-001: 4-Layer Architecture
- ADR-002: Context Isolation (domain filter + firewall)
- ADR-003: Hybrid Natures (file → directory)
- ADR-004: LLM Wiki Integration
- ADR-005: Skill Consolidation (7 → 1)
- ADR-013: Frontmatter Schema with OKF v0.1 Alignment
- ADR-014: Deprecation Policy for Transient Knowledge
- ADR-015: Quarantine Lifecycle — Safe Cleanup with Purge Window
- ADR-016: Semantic Revision on Insert
- ADR-017: OKF v0.1 Compatibility
- ADR-018: Autonomous Syndic


## Pitfalls

- **Domain contamination:** Writing domain A info in domain B violates the Domain Filter. Always classify content scope before writing. Use `shared/cross-refs/` for cross-domain content.
- **Scope conflicts:** When multiple microversos have similar content, verify `shared/groups.md` scope resolution. `allow` always overrides `deny`.
- **`type` vs `excrtx_type` confusion:** The OKF `type` field (concept type: `decision`, `memory`, `knowledge`, ...) is NOT the old Acervo `type` (now `excrtx_type`: `fact`, `rule`, `workflow`, ...). They are orthogonal — `type` is for OKF interoperability, `excrtx_type` preserves the legacy vocabulary. Never use `excrtx_type` values in the `type` field or vice versa. See `docs/plans/2026-06-19_acervo-lifecycle-okf/SCHEMA.md` §2.
- **Stale frontmatter:** Files with old `last_accessed_at` (or legacy `updated`) dates may be outdated. Flag data with `last_accessed_at` > 90 days as potentially stale — these are quarantine candidates for the syndic.
- **Deprecated files in search results:** Always filter out `deprecated: true` files in SEARCH unless the executive explicitly asks for historical content. Returning deprecated data as current truth is a critical error.
- **Quarantine directory leakage:** `.quarantine/` must never appear in search results or context loading. It is not active memory.
- **Missing semantic revision on WRITE:** Every WRITE to `knowledge/`, `context/`, `contracts/`, or `tools/` must call `excrtx-memory-deprecate` before commit. Skipping this step leaves contradictory knowledge active — the agent may retrieve stale truth.
- **Promotion threshold:** Don't promote a Nature file to directory prematurely. Only at ~150 lines. Check with `wc -l`.
- **raw/ immutability:** Never modify files in `raw/` directories — sources are immutable by contract. Only Acervo pages may be edited.
- **Missing index.md update:** Every new wiki page requires updating both `index.md` and `log.md`. Forgetting either breaks discoverability or audit trail.
- **Large wiki search:** In microversos with 50+ pages, searching by `_index.md` then targeted page read is mandatory — never `cat` entire directories.
