---
name: excrtx-memory-manager
description: Unified Acervo Cognitivo skill. Reads, writes, searches, and manages
  knowledge across the 4 layers (macro/global/micro/shared) with context isolation.
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
      calibration_prompt: 'Você gerencia o Acervo Cognitivo de 4 camadas: macro (identidade),
        global (regras universais), micro (domínios isolados por slug) e shared (pontes).

        Regras de Escrita:

        - Execute o Filtro de Domínio: se a informação pertence a um domínio específico,
        escreva em ''micro/{slug}/{nature}.md''. Se for comum, ''global/{nature}.md''.
        Se for cross-domain, escreva em ''shared/cross-refs/'' e coloque um link de
        1 linha no microverso. Nunca duplique.

        - Toda página wiki criada ou modificada deve possuir o cabeçalho YAML (frontmatter)
        contendo: title, created, updated, nature e type.

        - Atualize sempre o ''index.md'' e o ''log.md'' correspondente ao escopo de
        gravação.'
      test_prompt: 'Verifique se o Acervo Manager opera no microverso ''estudio-criativo'':
        1. Leia o arquivo acervo/micro/estudio-criativo/context/mixed-task-model.md.
        2. Proponha a criação de um novo formato de publicação (ex: carrossel para
        redes sociais) para promover um curso do microverso ''ensino'', respeitando
        a regra de separação contra contaminação entre microversos.'
      acceptance_criteria: O agente deve propor a criação do formato no microverso
        estudio-criativo (como método criativo) e fazer referência ao curso do microverso
        ensino, sem misturar os contextos de forma contaminada, respeitando o mixed-task-model.
      remediation_tip: Violação do Mixed Task Model ou do Filtro de Domínio. As regras
        do formato/método devem residir no estudio-criativo e as do curso no ensino.
---
# Acervo Manager

Unified skill for operating on the Exocórtex Acervo Cognitivo.
Replaces the 7 individual Nature skills and `exocortex-search` (ADR-005).

The 11 Natures (context, knowledge, contracts, prompts, persona, workflows, skills, tools, templates, decisions, reflections)
are **data classification**, not distinct behaviors. This skill implements the common mechanics:
read, write, search, and promote — each Nature's semantics are defined by the SCHEMA
and frontmatter of the files themselves.

## When This Skill Activates

Activate when:
- The executive asks about facts, data, rules, processes, or tools in a domain
- A task needs to read or write to the Acervo Cognitivo
- The agent needs to search information across multiple microversos
- A Nature needs to be promoted (file → directory)
- The agent needs to resolve access scope between microversos

## Acervo Location

```
ACERVO="${HERMES_HOME:-$HOME/.hermes}/acervo"
```

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

### Verification

- [ ] Presented information exists in the Acervo (never fabricate)
- [ ] Source cited in response
- [ ] Data with old `updated` frontmatter flagged as potentially outdated

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

2. **Write format:**
   - If Nature is file → append to existing file
   - If Nature is directory → create new wiki page with frontmatter
   - Mandatory YAML frontmatter on every new page:
     ```yaml
     ---
     title: Descriptive Title
     created: YYYY-MM-DD
     updated: YYYY-MM-DD
     nature: {nature}
     type: {fact|rule|workflow|tool|profile|lesson|context}
     tags: [from SCHEMA taxonomy]
     sources: [raw/source if applicable]
     confidence: {high|medium|low}
     ---
     ```

3. **Log operation** in `log.md` of the corresponding scope:
   - Write to micro/ → `micro/{slug}/log.md`
   - Write to global/ → `global/log.md`
   - Write to shared/ → `shared/log.md`

4. **Update index.md** if new page created.

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

4. **Return results with metadata:**
   ```
   [Acervo: micro/cliente-acme/knowledge] Result here
   [Acervo: global/contracts] Universal rule here
   ```

5. **If nothing found:** Declare and offer external search.

### Verification

- [ ] Scope verified before search
- [ ] Results indicate layer of origin
- [ ] Priority respected (micro > global > shared)

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

## When to Use

Activate when working with this skill's domain. See procedure for details.

**Don't use for:** Unrelated domains or when a more specialized skill exists.

## Pitfalls

- **Over-application**: Only activate when the skill's trigger conditions are met.
- **Missing context**: Ensure required dependencies and related skills are loaded.
