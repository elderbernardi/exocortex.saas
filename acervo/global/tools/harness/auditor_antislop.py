#!/usr/bin/env python3
"""
auditor_antislop.py — Anti-Slop Content Auditor

Scores agent prose output on 5 dimensions (10 pts each, min 35/50).
Applies both PT-BR patterns (primary — output is PT-BR) and EN patterns
(fallback — catches language leaks).

Usage:
    python3 auditor_antislop.py <transcript.jsonl>
    python3 auditor_antislop.py <transcript.jsonl> --json
    echo "text to check" | python3 auditor_antislop.py --stdin
"""

import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class AntiSlopResult:
    score: int            # 0-50
    passed: bool          # score >= 35
    dimensions: dict      # {name: score}
    violations: list      # [{pattern, match, penalty}]
    word_count: int = 0

    def to_dict(self):
        return asdict(self)


# ─── Slop patterns ─────────────────────────────────────────────────────────

# Format: (compiled regex, category, penalty per match)

# PT-BR patterns (primary — output is PT-BR)
SLOP_PATTERNS_PT = [
    # Adverbs
    (re.compile(r"\b(significativamente|dramaticamente|fundamentalmente|notavelmente|"
                r"essencialmente|basicamente|simplesmente|literalmente|absolutamente|"
                r"extremamente|incrivelmente|tremendamente)\b", re.I),
     "adverb_pt", 1),
    # Throat-clearing
    (re.compile(r"\b(é importante notar|vale a pena mencionar|cabe destacar|"
                r"é interessante observar|convém lembrar|não podemos esquecer|"
                r"é crucial entender|primeiramente|antes de mais nada)\b", re.I),
     "throat_clearing_pt", 2),
    # False contrasts
    (re.compile(r"\bnão (?:é apenas|se trata apenas de|basta)\b.*\b(?:mas|e sim|porém|também)\b", re.I),
     "false_contrast_pt", 1),
    # Passive voice
    (re.compile(r"\b(foi|foram|sido|sendo|é|são)\s+\w+[aoe]d[oa]s?\b", re.I),
     "passive_pt", 1),
    # Filler
    (re.compile(r"\b(na verdade|com certeza|sem dúvida|obviamente|claramente|"
                r"naturalmente|evidentemente)\b", re.I),
     "filler_pt", 1),
]

# EN patterns (fallback — catches language leaks in PT-BR output)
SLOP_PATTERNS_EN = [
    (re.compile(r"\b(significantly|dramatically|fundamentally|notably|essentially|"
                r"basically|simply|literally|absolutely|extremely|incredibly)\b", re.I),
     "adverb_en", 1),
    (re.compile(r"\b(it is important to note|it's worth noting|"
                r"it should be noted|let's explore|great question|"
                r"that's a great|before we dive)\b", re.I),
     "throat_clearing_en", 3),  # Higher penalty — language leak
    (re.compile(r"\bnot (?:just|only|merely)\b.*\bbut (?:also|rather)\b", re.I),
     "false_contrast_en", 1),
    (re.compile(r"\b(was|were|been|being)\s+\w+ed\b", re.I),
     "passive_en", 1),
]

# Structural patterns (language-independent)
SLOP_STRUCTURAL = [
    # Em-dashes (should be avoided per anti-slop rules)
    (re.compile(r"—"), "em_dash", 0),  # tracked but no penalty — common in PT-BR
    # Punchy one-liners at end of paragraph
    (re.compile(r"\n\n.{5,40}\.\n\n", re.M), "punchy_ending", 1),
]


def extract_prose(transcript_path: Path) -> str:
    """Extract agent prose from transcript JSONL (skip tool calls, code blocks)."""
    prose_parts = []

    with open(transcript_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Look for agent text output
            content = entry.get("content", "")
            if not content or not isinstance(content, str):
                continue

            # Skip if it's a tool call or system message
            source = entry.get("source", entry.get("role", ""))
            if source in ("tool", "system", "SYSTEM", "USER_EXPLICIT"):
                continue

            # Strip code blocks
            content = re.sub(r"```[\s\S]*?```", "", content)
            # Strip inline code
            content = re.sub(r"`[^`]+`", "", content)
            # Strip URLs
            content = re.sub(r"https?://\S+", "", content)

            if content.strip():
                prose_parts.append(content.strip())

    return "\n\n".join(prose_parts)


def score_text(text: str) -> AntiSlopResult:
    """Score text on 5 dimensions, 10 pts each. Min pass: 35/50.
    Applies both PT and EN patterns — PT with full weight, EN as leak detection.
    """
    if not text.strip():
        return AntiSlopResult(score=50, passed=True, dimensions={}, violations=[], word_count=0)

    word_count = len(text.split())
    violations = []

    # Collect all violations
    all_patterns = SLOP_PATTERNS_PT + SLOP_PATTERNS_EN + SLOP_STRUCTURAL
    for pattern, category, penalty in all_patterns:
        matches = pattern.findall(text)
        for match in matches:
            match_str = match if isinstance(match, str) else match[0] if match else ""
            violations.append({
                "pattern": category,
                "match": match_str[:50],
                "penalty": penalty,
            })

    # Score each dimension (start at 10, subtract penalties)
    dims = {
        "directness": 10,   # throat-clearing, filler
        "rhythm": 10,       # structural issues, em-dashes
        "trust": 10,        # false contrasts, hand-holding
        "authenticity": 10, # adverbs, passive, language leaks
        "density": 10,      # filler, punchy endings
    }

    # Map violations to dimensions
    for v in violations:
        cat = v["pattern"]
        penalty = v["penalty"]
        if "throat_clearing" in cat or "filler" in cat:
            dims["directness"] = max(0, dims["directness"] - penalty)
            dims["density"] = max(0, dims["density"] - penalty)
        elif "adverb" in cat:
            dims["authenticity"] = max(0, dims["authenticity"] - penalty)
            dims["density"] = max(0, dims["density"] - penalty)
        elif "passive" in cat:
            dims["authenticity"] = max(0, dims["authenticity"] - penalty)
        elif "false_contrast" in cat:
            dims["trust"] = max(0, dims["trust"] - penalty)
        elif "em_dash" in cat:
            dims["rhythm"] = max(0, dims["rhythm"] - penalty)
        elif "punchy" in cat:
            dims["rhythm"] = max(0, dims["rhythm"] - penalty)

    total = sum(dims.values())

    return AntiSlopResult(
        score=total,
        passed=total >= 35,
        dimensions=dims,
        violations=violations,
        word_count=word_count,
    )


def main():
    as_json = "--json" in sys.argv
    use_stdin = "--stdin" in sys.argv

    if use_stdin:
        text = sys.stdin.read()
    elif len(sys.argv) >= 2 and sys.argv[1] not in ("--json", "--stdin"):
        transcript_path = Path(sys.argv[1])
        if not transcript_path.exists():
            print(f"ERROR: File not found: {transcript_path}", file=sys.stderr)
            sys.exit(1)
        text = extract_prose(transcript_path)
    else:
        print("Usage: auditor_antislop.py <transcript.jsonl> [--json]", file=sys.stderr)
        print("       echo 'text' | auditor_antislop.py --stdin", file=sys.stderr)
        sys.exit(1)

    result = score_text(text)

    if as_json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(f"Anti-slop audit: {'PASS' if result.passed else 'FAIL'} ({result.score}/50)")
        print(f"  Words analyzed: {result.word_count}")
        for dim, score in result.dimensions.items():
            status = "✓" if score >= 7 else "⚠" if score >= 5 else "✗"
            print(f"  {status} {dim}: {score}/10")
        if result.violations:
            print(f"  Violations ({len(result.violations)}):")
            for v in result.violations[:10]:  # show first 10
                print(f"    - [{v['pattern']}] \"{v['match']}\" (penalty: {v['penalty']})")
            if len(result.violations) > 10:
                print(f"    ... and {len(result.violations) - 10} more")

    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
