# `log.md` Convention — Acervo Cognitivo

**Status:** Proposed
**Date:** 2026-06-19
**Depends on:** ADR-013 (Frontmatter Schema), ADR-014 (Deprecation Policy), ADR-015 (Quarantine Lifecycle)
**Audience:** Syndic, deprecation skill, promotion skill, any agent that creates/updates Acervo files

> This document is the **authoritative specification** for the `log.md` chronological history file used throughout the Acervo Cognitivo. The syndic (autonomous, under `manut`) and the semantic-revision / deprecation skills parse and append to logs following this convention. Deviations break automation — follow exactly.

---

## 1. Format Spec

A `log.md` file is an **append-only**, human- and machine-readable chronological history of lifecycle events for the files owned by its container (a microverso, `global/`, or `shared/`).

### 1.1 Document structure

```
# Log[ — <Human Name>]

## YYYY-MM-DD

- <ENTRY>
- <ENTRY>
...

## YYYY-MM-DD

- <ENTRY>
...
```

Rules:

- **Title (H1).** Exactly one H1 line at the top: `# Log`, optionally followed by ` — <Human Name>` (e.g. `# Log — Exocórtex Dev`). The suffix is cosmetic; parsers ignore it. No other H1 lines may appear.
- **Date headings (H2).** Each day with events gets exactly one `## YYYY-MM-DD` heading, where the date is an ISO 8601 calendar date (`YYYY-MM-DD`), no time, no timezone, no extra text on the heading line.
- **Entries (bullets).** Every entry is a single bullet line beginning with `- ` (dash, single space). One line per entry — no multi-line entries, no sub-bullets, no continuation lines. If a description is long, keep it on one line (wrap is a display concern, not a structural one).
- **No other content.** No prose, no paragraphs, no free-text notes between or under headings. The entire body of the file is H2 date headings + bullet entries. (Existing logs in the Acervo use an older free-text format; those are legacy and get replaced on next append — see §4, step 1.)

### 1.2 Ordering — newest at BOTTOM (chronological ascending)

Date headings are in **chronological ascending order**: the oldest day is at the top, the newest day is at the bottom. New entries are appended below all existing content.

```
## 2026-06-17   ← oldest, top
## 2026-06-18
## 2026-06-19   ← newest, bottom
```

Within a single date heading, entries are in **append order** — the order in which events occurred that day. Do not sort entries within a day by type or alphabetically; append-only means the sequence is the record.

### 1.3 Append-only invariant

Existing lines must never be reordered, edited, or deleted. The only permitted mutation is **appending** new lines (a new bullet under today's heading, or a new `## YYYY-MM-DD` heading followed by its bullets). See §4 for the protocol.

---

## 2. Entry Types

Seven entry types exist. Each begins with the type keyword in `UPPERCASE`, followed by `: `, then a type-specific payload. The separator between the path and the free-text tail is ` — ` (space, em-dash, space). All paths are **relative to the owning root** (the microverso directory, `global/`, or `shared/`), using forward slashes — never absolute paths, never `./` prefixes.

| # | Entry Type | Exact Format | Who Writes |
|---|------------|--------------|------------|
| 1 | `CREATED` | `CREATED: <relative-path> (<class>) — <one-line description>` | Any agent that writes a new file into the container |
| 2 | `UPDATED` | `UPDATED: <relative-path> — <what changed>` | Any agent that modifies an existing file's content or frontmatter |
| 3 | `DEPRECATED` | `DEPRECATED: <relative-path> — <reason>` | Semantic-revision skill (ADR-016) — the only writer of this type |
| 4 | `PROMOTED` | `PROMOTED: <relative-path> → perene` | Executive, or a promotion skill acting on executive intent |
| 5 | `QUARANTINED` | `QUARANTINED: <relative-path> — <reason>` | Syndic (ADR-015, ADR-018) — the only writer of this type |
| 6 | `PURGED` | `PURGED: <relative-path> — quarantine expired (30 days)` | Syndic — the only writer of this type |
| 7 | `RESTORED` | `RESTORED: <relative-path> — restored from quarantine by executive` | Executive, or a restore skill acting on executive intent |

### 2.1 Field semantics

- **`<relative-path>`** — Path from the owning root to the file the event concerns. Example: `knowledge/modelo-default-v2.md`, `decisions/adr-013-frontmatter-schema.md`. Always forward-slash, never absolute, never `./`.
- **`<class>`** (CREATED only) — The Acervo `class` frontmatter value of the newly created file: `perene` or `volátil` (ADR-014). Parenthesized, lowercase, matching the YAML value exactly.
- **`<one-line description>`** (CREATED) — A short human-readable summary of what the file is. Keep to a single line; no trailing punctuation required.
- **`<what changed>`** (UPDATED) — A concise statement of the substantive change (not a full diff). Example: `added OKF alignment info to section 2`.
- **`<reason>`** (DEPRECATED, QUARANTINED) — The deprecation or quarantine reason. For DEPRECATED, typically references the superseding file (e.g. `superseded by knowledge/modelo-default-v2.md`). For QUARANTINED, the trigger (e.g. `not accessed in 92 days`).
- **`→ perene`** (PROMOTED) — Literal string. Promotion always targets `perene`; there is no demotion entry. The arrow is the Unicode character `→` (U+2192).
- **`quarantine expired (30 days)`** (PURGED) — Literal string. Purge only happens when the 30-day quarantine window (ADR-015) elapses without restoration. The syndic does not purge for any other reason.
- **`restored from quarantine by executive`** (RESTORED) — Literal string. Restoration is an executive act that cancels a pending purge (ADR-015).

### 2.2 What is NOT logged

- Reads (file accessed by an agent) — not logged here; that's tracked in `last_accessed_at` frontmatter.
- Frontmatter-only `last_accessed_at` updates — not logged (too noisy; the field is the record).
- `macro/` identity changes — not logged anywhere; tracked in git (see §3).
- Edits to the log itself — impossible; append-only.

---

## 3. Location Rules

Each container that owns files has **at most one** `log.md`. The location is determined by the container's directory structure.

### 3.1 Per-microverso log

For a microverso at `micro/{slug}/`:

- **If `micro/{slug}/_meta/` exists** → the log lives at `micro/{slug}/_meta/log.md`.
- **Otherwise** → the log lives at `micro/{slug}/log.md` (top-level of the microverso).

Agents must **check for `_meta/` first and never assume**. Both patterns exist in production today (most microversos use `_meta/log.md`; `estudio-criativo` and `hermes-setup` use top-level `log.md`). When `_meta/` is absent, do not create it just to host the log — use the top-level path; `_meta/` is created by other concerns (onboarding, metadata).

### 3.2 Global and shared logs

- `global/log.md` — wait, correction: `global/_meta/log.md` if `global/_meta/` exists (it does today), otherwise `global/log.md`. Apply the same `_meta/`-first rule as microversos.
- `shared/log.md` — same rule: `shared/_meta/log.md` if `shared/_meta/` exists (it does today), otherwise `shared/log.md`.

In short: **the `_meta/`-first rule applies uniformly to `micro/`, `global/`, and `shared/`.** Today all three have `_meta/` and therefore all logs live at `{container}/_meta/log.md`.

### 3.3 Macro does NOT have a log

`macro/` (the Macroverso — `SOUL.md`, valores, estilo) **does not have a `log.md`**. Identity-layer changes are tracked exclusively in **git history**, not in an Acervo log. Do not create `macro/log.md` or `macro/_meta/log.md` under any circumstance. If an agent believes a macro change needs recording, the answer is a git commit message, not a log entry.

### 3.4 Other top-level directories

`_artifacts/`, `_inbox/`, `_routines/`, `_tasks/`, `_automations/` do **not** have their own logs. Files written into these are either transient (inbox, tasks) or tracked by their own subsystem (routines, automations). Only `micro/`, `global/`, and `shared/` host `log.md` files.

### 3.5 Ownership rule for entries

An entry is written to the log of the container that **owns** the file being acted upon. A file at `micro/excrtx/knowledge/foo.md` is logged in `micro/excrtx/_meta/log.md` (or `micro/excrtx/log.md`), never in `global/log.md`. Cross-container operations (e.g. a file moved from `global/` to `micro/excrtx/`) produce one entry in each log: a `DEPRECATED`/`PURGED`-style note in the source log is **not** standard — instead, log `CREATED` in the destination container. (Moves are rare; if needed, use `UPDATED` with a clear `moved from global/...` note in the destination log.)

---

## 4. Append Protocol

Every agent that creates, updates, promotes, deprecates, quarantines, purges, or restores an Acervo file MUST append a corresponding entry to the correct `log.md` (per §3) in the same operation. The protocol is strict:

1. **Locate the log.** Determine the owning container (§3.5) and resolve the log path using the `_meta/`-first rule (§3.1, §3.2). If the log file does not exist, it will be created in step 4.
2. **Read the current log (or treat as empty).** Read the file if it exists; capture its full contents. If it does not exist, start from an empty buffer. **If the existing content uses the legacy free-text format** (e.g. `## DATE | type | desc` with paragraphs), preserve it verbatim below any new content you add — do not rewrite history. New `## YYYY-MM-DD` headings you add must follow this spec; legacy headings are left untouched (they will age out naturally as they are historical).
3. **Find or create today's date heading.** Search the buffer for a line matching `## ` + today's `YYYY-MM-DD` exactly.
   - **If found** — today's heading already exists. Append new bullet(s) immediately after the last existing bullet under that heading (i.e. before the next `## ` heading or EOF).
   - **If not found** — create the heading. Because ordering is chronological ascending (§1.2), insert the new `## YYYY-MM-DD` heading **after the last existing date heading that is earlier than today**, and before any later date heading. In the common case (today is the newest day), this means appending at the **bottom** of the file. Add a blank line before the new heading if the preceding line is not blank.
4. **Append the entry as a bullet.** Add a single line `- <ENTRY>` using the exact format for the entry type (§2). Append below the last bullet under today's heading. If multiple events occurred in one operation, append one bullet per event, in the order they occurred.
5. **Write the file back and never edit existing entries.** Write the full buffer back to the resolved log path (creating the file if it did not exist, with `# Log\n\n` as the header). **Never reorder, edit, or delete existing lines.** The only mutation is the append performed in steps 3–4. If you discover a past entry was wrong, add a new corrective entry today — do not edit the old one.

### 4.1 Atomicity expectation

The agent should write the Acervo file and append its log entry as a single logical operation. If the log append fails, the file write should be considered incomplete and retried or rolled back. A file without a log entry is not a violation of the file's integrity, but it is a gap in the history that the syndic will detect on its next scan.

### 4.2 Concurrency

The Acervo is single-writer per container in practice (one agent active per microverso at a time, and the syndic runs under `manut` on a schedule). If a race is possible, agents must re-read the log immediately before writing (step 2) and write back the full buffer (step 5) — do not compute a diff against a stale read.

---

## 5. Worked Example

The following is a complete, spec-conformant `log.md` for a microverso. It shows two days, with the newer day at the bottom containing multiple entry types in append order (the order events occurred that day).

````markdown
# Log — Exocórtex Dev

## 2026-06-18

- CREATED: decisions/adr-013-frontmatter-schema.md (perene) — Adopts OKF v0.1 superset frontmatter schema
- UPDATED: context/current-state.md — added OKF alignment info to section 2

## 2026-06-19

- CREATED: knowledge/modelo-default-v2.md (volátil) — MiniMax-M3 is the new default LLM model
- DEPRECATED: knowledge/modelo-default-v1.md — superseded by knowledge/modelo-default-v2.md
- PROMOTED: artifacts/exocortex-architecture.md → perene
- QUARANTINED: knowledge/old-pricing.md — not accessed in 92 days
- PURGED: knowledge/config-port-v1.md — quarantine expired (30 days)
- RESTORED: knowledge/needed-config.md — restored from quarantine by executive
````

### 5.1 Parser sanity check

A compliant parser reading the above file should extract, in order:

1. `2026-06-18` → 2 entries (`CREATED`, `UPDATED`)
2. `2026-06-19` → 6 entries (`CREATED`, `DEPRECATED`, `PROMOTED`, `QUARANTINED`, `PURGED`, `RESTORED`)

Total: 8 entries across 2 days, oldest first, newest at the bottom. No entry spans more than one line. Every bullet matches one of the seven type formats in §2.

### 5.2 Minimal valid log

A freshly created log with a single entry is also conformant:

````markdown
# Log

## 2026-06-19

- CREATED: knowledge/first-note.md (volátil) — initial note in this microverso
````

---

## 6. Verification Checklist

- [x] Format spec: append-only, H2 date headings, single-line bullets, no free text.
- [x] Ordering: chronological ascending (newest at bottom).
- [x] All 7 entry types documented with exact format and designated writer.
- [x] Location rules: `_meta/`-first for `micro/`, `global/`, `shared/`; `macro/` has no log.
- [x] Append protocol: 5 steps, including find-or-create-today-heading and never-edit rule.
- [x] Complete worked example with a multi-entry day.
- [x] Minimal valid example.
