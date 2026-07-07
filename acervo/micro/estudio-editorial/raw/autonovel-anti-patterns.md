# AI WRITING ANTI-PATTERNS

Patterns discovered through iterative evaluation of AI-generated novel
chapters. These are the specific failure modes that survive prompt
engineering and surface-level slop detection. They are structural, not
lexical -- you won't catch them with word lists.

This document supplements ANTI-SLOP.md (which covers word-level slop).

---

## 1. THE OVER-EXPLAIN

**The #1 problem.** The narrator restates what a scene already showed.

A character's hands shake. The dialogue goes silent. The scene lands.
Then the narrator adds: "He was afraid." Or worse: a full paragraph
analyzing what the shaking hands meant.

**Detection:** After every emotional beat, check: does the next
paragraph explain what just happened? If yes, cut it.

**Rule:** If a scene shows it, the narrator doesn't say it. Trust
the image, the gesture, the silence.

---

## 2. TRIADIC LISTING

AI defaults to groups of three: "X. Y. Z." or "X and Y and Z."

Sensory descriptions: "Linseed oil. Cold bronze. The faint char..."
Options: "He could go left. He could go right. He could stay."
Adjectives: "warm and clean and simple"

**Detection:** Search for three consecutive fragments or three items
joined by "and." More than 2 per chapter is a pattern.

**Fix:** Combine two items. Cut one. Use a different number. Two is
often stronger than three.

---

## 3. NEGATIVE-ASSERTION REPETITION

"He did not look back."
"He did not think about the room."
"He did not say what he meant."

Each one is fine. Five in a chapter is a tic.

**Rule:** Max 1 per chapter. Replace with: active alternatives
("The door stayed closed"), or just cut (let the absence speak).

---

## 4. CATALOGING-BY-THINKING

"He thought about X. He thought about Y. He thought about Z."

AI compresses reflection into a list of topics the character
considers. Real interiority is messier -- one thought bleeds into
another, gets interrupted, loops back.

**Fix:** Replace with: the thought itself as a fragment ("The two
years. The wrong-pitched bells."), a physical action, or dialogue.

---

## 5. THE SIMILE CRUTCH

"the way X did Y" -- used 4-8 times per chapter.

AI reaches for simile when it doesn't trust the image. Most of these
can be cut entirely. The image is already there.

**Rule:** Max 2 "the way" similes per chapter. If you need the
comparison, vary the construction. "Like" is fine. Direct metaphor
("his words were bronze -- heavy, functional") is better.

---

## 6. SECTION BREAK AS RHYTHM CRUTCH

AI uses "---" breaks to avoid writing transitions. A chapter with
5 section breaks is 5 vignettes, not a chapter.

**Rule:** Max 2 per chapter, for genuine time/location jumps. Force
continuous prose for everything else.

---

## 7. PARAGRAPH LENGTH UNIFORMITY

AI paragraphs cluster at 4-6 sentences, especially in middle
sections. The variation that appears at chapter openings and closings
flattens in the middle.

**Fix:** Deliberately include 1-2 sentence paragraphs for impact
and 6+ sentence paragraphs for building. Never 3+ consecutive
paragraphs of similar length.

---

## 8. PREDICTABLE EMOTIONAL ARCS

Beats arrive on schedule. If the outline says "curiosity → discovery
→ dread," the chapter delivers exactly that in exactly that order
with no deviation. Real chapters have moments that arrive early,
late, or sideways.

**Fix:** Include one moment per chapter that surprises: a character
saying the wrong thing, an emotion arriving before its trigger, a
beat that interrupts another beat.

---

## 9. REPETITIVE CHAPTER ENDINGS

AI finds a closing pattern and reuses it. In this novel: 4 chapters
ended with "Cass outside, listening to his father work."

**Rule:** No two chapters end with the same structural move. Each
ending belongs to THAT chapter specifically.

---

## 10. BALANCED ANTITHESIS IN DIALOGUE

"I'm not saying X. I'm saying Y."
"Not X, but Y."
"There's a difference."
"Those are different things."

AI loves this rhetorical formula. It sounds clever the first time.
By the third character using it, they all sound like the same person.

**Detection:** Check that no two characters share this sentence
structure. If multiple characters use it, they're not distinct.

---

## 11. DIALOGUE AS WRITTEN PROSE

Characters speak in complete, polished sentences. No one stumbles,
interrupts, trails off, or says something slightly wrong.

A 14-year-old does not speak in epigrams. A 60-year-old merchant
does not deliver thesis statements.

**Fix:** Dialogue should sound like speech. Include: false starts,
interruptions, trailing off, saying the wrong word, not finishing
a thought. At least one imperfect line per scene.

---

## 12. SCENE-SUMMARY IMBALANCE

AI defaults to summary when a scene would be more engaging. "The
morning passed" skips what could be a 200-word interaction that
reveals character.

**Rule:** 70%+ of each chapter should be in-scene (moment by moment,
with dialogue and action). Summary is for time compression only.

---

## EVALUATION NOTES

These patterns are invisible to standard slop detection (word lists,
regex). They require either:

1. **Adversarial editing** -- ask a judge to cut 500 words and
   classify what it cuts. OVER-EXPLAIN type dominates every time.

2. **Comparative ranking** -- head-to-head matchups between chapters
   force discrimination the judge can't avoid. Produces a true rank
   order. Swiss-style Elo tournament works well with 4 rounds.

3. **Sentence-level grading** -- flag every sentence as STRONG /
   FINE / WEAK / CUT. The distribution matters more than the average.

Standard 1-10 scoring collapses to a 2-point band regardless of
rubric calibration. Avoid absolute scoring for revision work.
