#!/usr/bin/env python3
"""
compile_soul.py — Exocórtex Compiled SOUL Generator

Reads `compiled_rules:` from SKILL.md frontmatter across all excrtx-* skills
and injects them into SOUL_SEED.md between marker comments.

Usage:
    python3 scripts/compile_soul.py                        # compile in-place
    python3 scripts/compile_soul.py --dry-run               # preview output
    python3 scripts/compile_soul.py --skills-dir /path/to   # custom skills dir
    python3 scripts/compile_soul.py --soul /path/to/SOUL.md # custom SOUL target

The script is idempotent — running it multiple times produces the same result.
"""

import argparse
import re
import sys
from pathlib import Path

# ─── Markers ────────────────────────────────────────────────────────────────

START_MARKER = "<!-- COMPILED_RULES_START -->"
END_MARKER = "<!-- COMPILED_RULES_END -->"

# ─── Frontmatter parser ────────────────────────────────────────────────────

def extract_compiled_rules(skill_path: Path) -> tuple[str, str] | None:
    """Extract skill name and compiled_rules from SKILL.md frontmatter.

    Returns (name, rules) or None if no compiled_rules field.
    Handles files with line number prefixes (e.g. '1|---').
    """
    raw_text = skill_path.read_text(encoding="utf-8")

    # Strip line number prefixes (e.g. "1|---" → "---", "2|name: foo" → "name: foo")
    lines = raw_text.splitlines()
    stripped_lines = []
    for line in lines:
        if re.match(r"^\d+\|", line):
            stripped_lines.append(line.split("|", 1)[1])
        else:
            stripped_lines.append(line)
    text = "\n".join(stripped_lines) + "\n"

    # Find YAML frontmatter between --- markers
    match = re.match(r"^---\n(.*?\n)---", text, re.DOTALL)
    if not match:
        return None

    frontmatter = match.group(1)

    # Extract name
    name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
    name = name_match.group(1).strip() if name_match else skill_path.parent.name

    # Extract compiled_rules (YAML multiline scalar with | )
    rules_match = re.search(
        r"^compiled_rules:\s*\|\n((?:[ \t]+.+\n?)+)",
        frontmatter,
        re.MULTILINE,
    )
    if not rules_match:
        return None

    # Dedent the rules block (remove leading whitespace from YAML indentation)
    raw = rules_match.group(1)
    rule_lines = raw.splitlines()
    if rule_lines:
        # Find minimum indentation
        indents = [len(l) - len(l.lstrip()) for l in rule_lines if l.strip()]
        min_indent = min(indents) if indents else 0
        rule_lines = [l[min_indent:] for l in rule_lines]

    rules = "\n".join(rule_lines).strip()
    return (name, rules)


def format_section_title(skill_name: str) -> str:
    """Convert skill name to a readable section title.

    excrtx-behavior-vetor  → Vetor Classification
    excrtx-quality-antislop → Anti-Slop
    excrtx-govern-draftfirst → Draft-First
    """
    mapping = {
        "excrtx-behavior-vetor": "Vetor Classification",
        "excrtx-behavior-canvas": "Canvas",
        "excrtx-behavior-briefing": "Morning Briefing",
        "excrtx-behavior-accuracy": "Accuracy Verification",
        "excrtx-govern-draftfirst": "Draft-First",
        "excrtx-govern-tools": "Tool Governance",
        "excrtx-quality-gate": "Quality Gate",
        "excrtx-quality-antislop": "Anti-Slop",
    }
    return mapping.get(skill_name, skill_name.replace("excrtx-", "").replace("-", " ").title())


# ─── Validation ─────────────────────────────────────────────────────────────

def validate_compiled_rules(skills_dir: Path) -> list[dict]:
    """Cross-check compiled_rules against body content for each skill.

    Returns a list of {name, issues} dicts for skills with desynchronized rules.
    A desynchronized rule is one where >50% of the non-trivial keywords in
    compiled_rules don't appear anywhere in the body.
    """
    TRIVIAL_WORDS = {
        "o", "a", "os", "as", "de", "do", "da", "dos", "das", "em", "no", "na",
        "nos", "nas", "por", "para", "com", "sem", "que", "se", "não", "e", "ou",
        "um", "uma", "uns", "umas", "ao", "à", "aos", "às", "the", "is", "are",
        "and", "or", "to", "in", "of", "for", "a", "an", "be", "if", "it", "on",
        "at", "as", "by", "do", "no", "so", "up", "we", "he", "me", "my",
    }
    results = []

    for skill_dir in sorted(skills_dir.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        result = extract_compiled_rules(skill_md)
        if not result:
            continue

        name, rules = result

        # Read body (everything after frontmatter)
        raw = skill_md.read_text(encoding="utf-8")
        clean = re.sub(r"^\d+\|", "", raw, flags=re.MULTILINE)
        fm_match = re.search(r"\n---\s*\n", clean[3:]) if clean.lstrip().startswith("---") else None
        body = clean[fm_match.end() + 3:] if fm_match else clean
        body_lower = body.lower()

        # Extract non-trivial keywords from compiled_rules
        rule_words = set(re.findall(r"[a-záàâãéêíóôõúçü]{4,}", rules.lower()))
        rule_words -= TRIVIAL_WORDS

        if not rule_words:
            continue

        # Check how many rule keywords appear in body
        missing = [w for w in rule_words if w not in body_lower]
        missing_ratio = len(missing) / len(rule_words) if rule_words else 0

        issues = []
        if missing_ratio > 0.5:
            issues.append(
                f"Desync: {len(missing)}/{len(rule_words)} rule keywords "
                f"({missing_ratio:.0%}) absent from body. "
                f"Missing: {', '.join(sorted(missing)[:10])}"
            )
        if issues:
            results.append({"name": name, "issues": issues})

    return results


# ─── Main ───────────────────────────────────────────────────────────────────

def compile_rules(skills_dir: Path) -> str:
    """Collect all compiled_rules and format them into a single block."""
    entries = []

    for skill_dir in sorted(skills_dir.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        result = extract_compiled_rules(skill_md)
        if result:
            name, rules = result
            title = format_section_title(name)
            entries.append(f"## {title}\n{rules}")

    if not entries:
        print("WARNING: No compiled_rules found in any SKILL.md", file=sys.stderr)
        return ""

    header = (
        "# Compiled Behavioral Rules (auto-generated by compile_soul.py — DO NOT EDIT)\n\n"
        "## Output Language\n"
        "Output language: Portuguese (PT-BR). Never respond in English unless quoting "
        "code, logs, commands, or external sources.\n"
    )

    return f"{START_MARKER}\n{header}\n" + "\n\n".join(entries) + f"\n{END_MARKER}"


def inject_into_soul(soul_path: Path, compiled_block: str, dry_run: bool = False) -> bool:
    """Replace content between markers in SOUL_SEED.md, or append if no markers."""
    text = soul_path.read_text(encoding="utf-8")

    if START_MARKER in text and END_MARKER in text:
        # Replace existing block
        pattern = re.compile(
            re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
            re.DOTALL,
        )
        new_text = pattern.sub(compiled_block, text)
    elif START_MARKER in text or END_MARKER in text:
        print("ERROR: Mismatched markers in SOUL_SEED.md", file=sys.stderr)
        return False
    else:
        # Append at end
        new_text = text.rstrip() + "\n\n" + compiled_block + "\n"

    if dry_run:
        print("=== DRY RUN — would write to", soul_path, "===")
        print(compiled_block)
        print("=== END DRY RUN ===")
        return True

    soul_path.write_text(new_text, encoding="utf-8")
    return True


def main():
    parser = argparse.ArgumentParser(description="Compile behavioral rules into SOUL_SEED.md")
    parser.add_argument("--skills-dir", type=Path, help="Skills directory")
    parser.add_argument("--soul", type=Path, help="Path to SOUL_SEED.md")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument(
        "--validate-compiled-rules", action="store_true",
        help="Cross-check compiled_rules against body content. Exit 1 if desync found.",
    )
    args = parser.parse_args()

    # Resolve paths relative to script location
    script_dir = Path(__file__).resolve().parent.parent
    skills_dir = args.skills_dir or script_dir / "skills"
    soul_path = args.soul or script_dir / "SOUL_SEED.md"

    if not skills_dir.is_dir():
        print(f"ERROR: Skills directory not found: {skills_dir}", file=sys.stderr)
        sys.exit(1)

    if not soul_path.is_file():
        print(f"ERROR: SOUL_SEED.md not found: {soul_path}", file=sys.stderr)
        sys.exit(1)

    # Validate compiled_rules sync if requested
    if args.validate_compiled_rules:
        desyncs = validate_compiled_rules(skills_dir)
        if desyncs:
            print(f"\n❌ COMPILED_RULES DESYNC ({len(desyncs)} skills):", file=sys.stderr)
            for d in desyncs:
                for issue in d["issues"]:
                    print(f"  - {d['name']}: {issue}", file=sys.stderr)
            sys.exit(1)
        else:
            print("✅ All compiled_rules are synchronized with their body content.")
            if args.dry_run:
                sys.exit(0)

    # Compile
    compiled = compile_rules(skills_dir)
    if not compiled:
        sys.exit(1)

    # Count rules
    rule_count = compiled.count("\n## ") - 1  # subtract the Output Language section header
    print(f"Compiled {rule_count} behavioral rules from {skills_dir}")

    # Inject
    if inject_into_soul(soul_path, compiled, dry_run=args.dry_run):
        if not args.dry_run:
            print(f"Written to {soul_path}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
