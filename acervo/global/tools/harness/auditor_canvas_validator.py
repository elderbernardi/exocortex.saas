#!/usr/bin/env python3
"""
auditor_canvas_validator.py — Canvas Block Validator

Validates that:
1. Canvas block exists in transcript (for complex inputs)
2. Canvas block validates against the JSON schema
3. Canvas vetor aligns with response shape

Usage:
    python3 auditor_canvas_validator.py <transcript.jsonl>
    python3 auditor_canvas_validator.py <transcript.jsonl> --json
"""

import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

# Import schema from sibling module
try:
    from canvas_schema import CANVAS_SCHEMA
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from canvas_schema import CANVAS_SCHEMA


@dataclass
class CanvasValidation:
    passed: bool
    canvas_found: bool = False
    canvas_data: dict = field(default_factory=dict)
    schema_valid: bool = False
    alignment_valid: bool = False
    errors: list = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


# ─── Canvas block extraction ───────────────────────────────────────────────

CANVAS_BLOCK_RE = re.compile(
    r"```canvas\s*\n(.*?)\n```",
    re.DOTALL,
)


def extract_canvas_blocks(transcript_path: Path) -> list[dict]:
    """Extract all canvas blocks from a transcript JSONL."""
    blocks = []

    with open(transcript_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            content = entry.get("content", "")
            if not content or not isinstance(content, str):
                continue

            for match in CANVAS_BLOCK_RE.finditer(content):
                try:
                    block = json.loads(match.group(1))
                    blocks.append(block)
                except json.JSONDecodeError:
                    blocks.append({"_parse_error": match.group(1)[:200]})

    return blocks


# ─── Schema validation (lightweight, no jsonschema dependency) ─────────────

def validate_schema(canvas: dict) -> list[str]:
    """Validate canvas dict against CANVAS_SCHEMA without external deps."""
    errors = []
    props = CANVAS_SCHEMA.get("properties", {})
    required = CANVAS_SCHEMA.get("required", [])

    # Check required fields
    for field_name in required:
        if field_name not in canvas:
            errors.append(f"Missing required field: {field_name}")

    # Check field types and enums
    for field_name, value in canvas.items():
        if field_name.startswith("_"):
            continue
        spec = props.get(field_name)
        if spec is None:
            if CANVAS_SCHEMA.get("additionalProperties") is False:
                errors.append(f"Unknown field: {field_name}")
            continue

        # Check enum
        if "enum" in spec and value not in spec["enum"]:
            errors.append(f"{field_name}: '{value}' not in {spec['enum']}")

        # Check type
        expected_type = spec.get("type")
        if expected_type:
            if isinstance(expected_type, list):
                # Union type (e.g. ["string", "null"])
                valid = False
                for t in expected_type:
                    if t == "string" and isinstance(value, str):
                        valid = True
                    elif t == "null" and value is None:
                        valid = True
                    elif t == "array" and isinstance(value, list):
                        valid = True
                if not valid:
                    errors.append(f"{field_name}: wrong type {type(value).__name__}")
            elif expected_type == "string" and not isinstance(value, str):
                errors.append(f"{field_name}: expected string, got {type(value).__name__}")
            elif expected_type == "array" and not isinstance(value, list):
                errors.append(f"{field_name}: expected array, got {type(value).__name__}")

        # Check minLength
        if "minLength" in spec and isinstance(value, str) and len(value) < spec["minLength"]:
            errors.append(f"{field_name}: too short (min {spec['minLength']})")

    return errors


# ─── Alignment check ───────────────────────────────────────────────────────

def check_alignment(canvas: dict, transcript_path: Path) -> list[str]:
    """Check that canvas vetor aligns with response shape."""
    errors = []
    vetor = canvas.get("vetor", "")

    # Extract agent responses after the canvas block
    responses = []
    canvas_seen = False
    with open(transcript_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            content = entry.get("content", "")
            if not content:
                continue

            if "```canvas" in content:
                canvas_seen = True
                continue

            source = entry.get("source", entry.get("role", ""))
            if canvas_seen and source in ("MODEL", "assistant"):
                responses.append(content)

    if not responses:
        return []  # Can't validate alignment without responses

    combined = "\n".join(responses)
    question_count = combined.count("?")

    if vetor == "evolucao" and question_count < 2:
        errors.append(
            f"Vetor=evolucao but response has only {question_count} questions "
            "(expected ≥2 Socratic questions)"
        )

    if vetor == "execucao" and question_count > len(combined.split("\n")) // 2:
        errors.append(
            "Vetor=execucao but response is mostly questions "
            "(expected a deliverable)"
        )

    return errors


# ─── Main ───────────────────────────────────────────────────────────────────

def validate_canvas(transcript_path: Path) -> CanvasValidation:
    """Full canvas validation pipeline."""
    blocks = extract_canvas_blocks(transcript_path)

    if not blocks:
        # No canvas block — this might be OK for simple inputs
        return CanvasValidation(
            passed=True,  # Not a failure if no canvas — only complex inputs need it
            canvas_found=False,
            errors=["No canvas block found (OK for simple inputs)"],
        )

    # Validate the first (or most recent) canvas block
    canvas = blocks[-1]  # Use the last one

    if "_parse_error" in canvas:
        return CanvasValidation(
            passed=False,
            canvas_found=True,
            errors=[f"Canvas block JSON parse error: {canvas['_parse_error']}"],
        )

    # Schema validation
    schema_errors = validate_schema(canvas)
    schema_valid = len(schema_errors) == 0

    # Alignment validation
    alignment_errors = check_alignment(canvas, transcript_path)
    alignment_valid = len(alignment_errors) == 0

    all_errors = schema_errors + alignment_errors

    return CanvasValidation(
        passed=schema_valid,  # Alignment is WARN, not FAIL
        canvas_found=True,
        canvas_data=canvas,
        schema_valid=schema_valid,
        alignment_valid=alignment_valid,
        errors=all_errors,
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: auditor_canvas_validator.py <transcript.jsonl> [--json]", file=sys.stderr)
        sys.exit(1)

    transcript_path = Path(sys.argv[1])
    as_json = "--json" in sys.argv

    if not transcript_path.exists():
        print(f"ERROR: File not found: {transcript_path}", file=sys.stderr)
        sys.exit(1)

    result = validate_canvas(transcript_path)

    if as_json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(f"Canvas audit: {'PASS' if result.passed else 'FAIL'}")
        print(f"  Canvas found: {result.canvas_found}")
        if result.canvas_found:
            print(f"  Schema valid: {result.schema_valid}")
            print(f"  Alignment valid: {result.alignment_valid}")
        if result.errors:
            for err in result.errors:
                print(f"  ⚠ {err}")

    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
