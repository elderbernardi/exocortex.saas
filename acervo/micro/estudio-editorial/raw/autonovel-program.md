# autonovel

Autonomous fantasy novel writing pipeline. The agent writes and refines
a novel across 5 co-evolving layers, guided by automated evaluation.

## Required Reading

Before ANY writing or evaluation, the agent must internalize:
  - `voice.md` -- Part 1 (guardrails) is permanent. Part 2 is per-novel.
  - `CRAFT.md` -- Operationalizable frameworks for plot, character,
    worldbuilding, foreshadowing, prose quality. This is the education.
  - `ANTI-SLOP.md` -- Full reference on AI writing tells.

## The Layer Stack

```
  Layer 5:  voice.md          -- HOW we write (style, tone, vocabulary)
  Layer 4:  world.md          -- WHAT exists (lore, magic, geography, history)
  Layer 3:  characters.md     -- WHO acts (registry, arcs, relationships)
  Layer 2:  outline.md        -- WHAT HAPPENS (beats, foreshadowing map)
  Layer 1:  chapters/ch_NN.md -- THE ACTUAL PROSE (one file per chapter)
  Cross-cutting: canon.md     -- WHAT IS TRUE (hard facts, consistency DB)
```

## Setup

1. **Tag the run**: Create branch `autonovel/<tag>` from master.
2. **Read all layer files** for full context.
3. **Verify state.json** shows phase=foundation.
4. **Confirm and go**.

## Phase 1: Foundation (no prose yet)

LOOP until foundation_score > 7.5 AND lore_score > 7.0:
  1. Run `python evaluate.py --phase=foundation`
  2. Identify the weakest layer/dimension from the eval output
  3. Expand or revise that layer's document
  4. When adding facts to world.md or characters.md, ALSO log them
     in canon.md as canonical entries
  5. git commit with description of what changed
  6. Re-evaluate
  7. If score improved -> keep. If worse -> git reset --hard HEAD~1, discard.
  8. Log to results.tsv

Lore priorities (the foundation evaluator weights these at 40%):
  - Magic system: hard rules, costs, limitations, societal implications
  - History: timeline that creates PRESENT-DAY TENSIONS, not decoration
  - Geography/culture: distinct locations, specific customs and taboos
  - Interconnection: magic affects politics, history explains factions,
    geography shapes culture. Pulling one thread should move everything.
  - Iceberg depth: more implied than stated. Hints at deeper systems.

Cross-layer consistency checks on every iteration:
  - Outline references only lore that exists in world.md
  - Character arcs align with outline beats
  - Character abilities match magic system rules
  - Foreshadowing ledger balances (every plant has a payoff)
  - Voice exemplars exist and are non-generic
  - Canon.md is populated with all hard facts from world.md and
    characters.md

Exit: When foundation_score > 7.5 AND lore_score > 7.0, update
state.json phase to "drafting".

## Phase 2: First Draft (sequential chapter writing)

FOR each chapter in outline order:
  LOOP until chapter_score > 6.0 or attempts > 5:
    1. Load context: voice.md + world.md + characters.md
       + this chapter's outline entry
       + previous chapter's last ~1000 words
       + next chapter's outline (for continuity)
    2. Write chapters/ch_NN.md
    3. Run `python evaluate.py --chapter=NN`
    4. Keep/discard based on score
    5. If writing reveals a lore gap or inconsistency, log a debt
       in state.json
    6. After evaluation, check new_canon_entries in the eval output.
       Add any new facts established in the chapter to canon.md.
    7. Log to results.tsv
    8. git commit

Canon grows during drafting. Every chapter establishes facts (a
character reveals something, a place is described, an event occurs).
These get logged in canon.md so future chapters stay consistent.

After all chapters drafted, update state.json phase to "revision".

## Phase 3: Revision (infinite refinement)

LOOP FOREVER:
  1. Run `python evaluate.py --full`
  2. Identify weakest point:
     - Lowest-scoring chapter
     - Unresolved foreshadowing thread
     - Consistency violation
     - Voice deviation
     - Pacing problem
     - Pending debt from state.json
  3. Decide action:
     a. Revise a weak chapter
     b. Fix a consistency violation (may touch lore + chapters)
     c. Strengthen a foreshadowing thread (plant + payoff chapters)
     d. Refine voice in the most-deviant chapter
     e. Adjust pacing (split/merge chapters)
     f. Update planning docs to reflect reality
  4. Make the change(s)
  5. git commit
  6. Re-evaluate affected scope
  7. Keep/discard
  8. Log to results.tsv

### Propagation Rules

When a layer changes, check downstream:
  - voice.md changes    -> re-evaluate ALL chapters for voice adherence
  - world.md changes    -> check all chapters for lore consistency
  - characters.md changes -> check affected chapters for dialogue/behavior
  - outline.md changes  -> re-evaluate affected chapters for beat coverage
  - chapter changes     -> check foreshadowing ledger, check adjacent chapters

When writing reveals upstream issues, log a debt in state.json:
```json
{"trigger": "ch_07: magic system needs teleportation rules",
 "affected": ["world.md", "ch_03.md"],
 "status": "pending"}
```

## Context Window Strategy

ALWAYS loaded (~8k tokens):
  - voice.md (full)
  - characters.md (full)
  - world.md (key rules summary)
  - outline.md (full)
  - foreshadowing ledger (full)

PER TASK (~20-30k tokens):
  - Target chapter(s)
  - Adjacent chapters (prev + next)
  - Chapters connected by foreshadowing threads

## Evaluation Dimensions

Foundation: world_depth, character_depth, outline_completeness,
  foreshadowing_balance, internal_consistency

Chapter: voice_adherence, beat_coverage, character_voice,
  plants_seeded, prose_quality, continuity

Full novel: all above + arc_completion, pacing_curve,
  theme_coherence, foreshadowing_resolution, overall_engagement

## The Stability Trap (CRITICAL)

AI's worst tendency is FAVOURING STABILITY OVER CHANGE. This kills
fiction. Actively fight it at every phase:

- Characters must end TRULY different from how they began.
- Let bad things stay bad. Not everything gets fixed.
- Allow irreversible decisions and irreversible loss.
- Withhold information from the reader. Maintain mystery.
- Create genuine moral ambiguity. The "right" choice should be unclear.
- Vary emotional intensity: quiet/explosive/dread/relief/wonder/horror.
- If a choice has no real cost, it's not a real choice.
- Conflicts should NOT resolve too quickly or too cleanly.
- Resist the urge to round off sharp edges into something safer.

## Foundation Phase: Voice Discovery

During foundation, the agent must DISCOVER the voice for this novel:
1. Read the world concept and initial ideas
2. Write 5 trial passages in different registers (mythic, spare,
   warm, cold, whimsical, etc.)
3. Evaluate which register best serves THIS story's world and tone
4. Select the best, refine it, write exemplar and anti-exemplar passages
5. Fill in voice.md Part 2 with the discovered voice

The voice should feel like it BELONGS in the world (Le Guin's insight:
in fantasy, the language creates the world, not just describes it).

## Foundation Phase: Character Framework

Every POV character must have documented before drafting begins:
- Wound/Want/Need/Lie chain (see CRAFT.md)
- Three-slider profile (proactivity, likability, competence)
- Arc type (positive, negative, or flat)
- Speech pattern distinct from every other character
- At least one secret the reader doesn't learn immediately

## Foundation Phase: Plot Framework

The outline must demonstrate:
- Save the Cat beats at roughly correct percentage marks
- Try-fail cycle types planned for each chapter (yes-but / no-and)
- Foreshadowing ledger with every plant and its planned payoff
- MICE threads identified and planned to close in reverse order
- Escalating stakes through Act 2

## Rules

- **NEVER STOP** during a phase. Keep looping until interrupted.
- **Simpler is better**: Don't add complexity for marginal gains.
- **Forward progress over perfection**: In Phase 2, a 6.0 chapter
  is good enough. Phase 3 is for polish.
- **Log everything**: Every experiment goes in results.tsv.
- **Different judge**: Evaluation model should differ from writing model
  when possible to avoid self-congratulation bias.
- **Fight stability**: Actively push toward transformation, cost, and
  genuine consequence. See "The Stability Trap" above.
- **Specificity over abstraction**: "a jay" not "a bird." "lupine" not
  "flowers." "the smell of hot iron" not "a metallic scent."
- **Earn every metaphor**: Metaphors come from character experience.
  A blacksmith thinks in terms of heat and metal. A sailor in tides.
