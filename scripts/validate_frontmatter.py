#!/usr/bin/env python3
"""
validate_frontmatter.py — Acervo Cognitivo Frontmatter Validator

Validates YAML frontmatter in Acervo markdown files against the schema
defined in ADR-013 / schema-spec.md (Section 4: Validation Rules), or —
when the file declares ``schema: acervo/v0.2`` — against schema v0.2
(ADR-023, docs/plans/2026-07-03_memory-v2-spec/13-artifacts/SCHEMA-v0.2.md).

Version dispatch: ``schema: acervo/v0.2`` selects the v2 rule set; any other
file gets the unchanged v1 rules plus a V2-000 migration WARN (suppress with
--no-migration-warn).

This is a D1-equivalent deterministic check — no LLM needed. It is consumed
by the migration script (Task 08), lifecycle skills (Tasks 04–06), and CI
gates to prevent non-conformant files from entering the Acervo.

Usage:
    python3 scripts/validate_frontmatter.py --file path/to/file.md
    python3 scripts/validate_frontmatter.py --dir path/to/dir
    python3 scripts/validate_frontmatter.py --dir path/to/dir --report
    python3 scripts/validate_frontmatter.py --dir path/to/dir --no-migration-warn

Exit codes:
    0 — all files valid (warnings may be present)
    1 — one or more files have ERROR-severity violations
    2 — specified file or directory not found
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

# ─── YAML loader (PyYAML preferred, minimal fallback) ───────────────────────

try:
    import yaml
    _HAS_PYYAML = True
except ImportError:
    _HAS_PYYAML = False


# ─── Custom YAML loader (keeps dates/timestamps as strings) ─────────────────
#
# PyYAML by default parses ISO 8601 date/datetime strings into
# datetime.date / datetime.datetime objects. We need them as plain strings
# so the format regex checks (V-029, V-043, etc.) can validate the exact
# YYYY-MM-DD / YYYY-MM-DDTHH:MM:SSZ format.

if _HAS_PYYAML:
    class _FrontmatterLoader(yaml.SafeLoader):
        """SafeLoader variant that does not auto-parse dates/timestamps."""

    # Remove the timestamp implicit resolver so dates stay as plain strings.
    # Copy the resolvers dict to avoid mutating SafeLoader's class attribute.
    _clean = {}
    for _ch, _resolvers in list(yaml.SafeLoader.yaml_implicit_resolvers.items()):
        _clean[_ch] = [
            (tag, regexp) for tag, regexp in _resolvers
            if tag != 'tag:yaml.org,2002:timestamp'
        ]
    _FrontmatterLoader.yaml_implicit_resolvers = _clean


def _parse_yaml(text):
    """Parse YAML text. Returns (data, error_message).

    Uses PyYAML if available; falls back to a minimal parser for simple
    frontmatter (key: value, block lists, flow lists, quoted strings).
    """
    if _HAS_PYYAML:
        try:
            return yaml.load(text, Loader=_FrontmatterLoader), None
        except yaml.YAMLError as exc:
            return None, str(exc)
    return _minimal_yaml_parse(text)


def _minimal_yaml_parse(text):
    """Minimal YAML parser for simple frontmatter.

    Supports: comments, ``key: value`` scalars, flow lists ``[a, b]``,
    block lists (``- item``), and quoted strings. NOT a full YAML parser —
    intended only as a fallback when PyYAML is unavailable.
    """
    result = {}
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        # Block list item (continuation of previous key)
        if stripped.startswith("- ") and result:
            last_key = list(result.keys())[-1]
            if result[last_key] is None:
                result[last_key] = []
            if isinstance(result[last_key], list):
                result[last_key].append(_parse_scalar(stripped[2:].strip()))
            i += 1
            continue
        # Key: value
        if ":" in stripped:
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()
            if val == "":
                # Could be start of a block list — peek ahead
                result[key] = None
                i += 1
                while i < len(lines):
                    nxt = lines[i].strip()
                    if nxt.startswith("- "):
                        if result[key] is None:
                            result[key] = []
                        result[key].append(_parse_scalar(nxt[2:].strip()))
                        i += 1
                    elif not nxt or nxt.startswith("#"):
                        i += 1
                    else:
                        break
                continue
            result[key] = _parse_scalar(val)
            i += 1
            continue
        i += 1
    return result


def _parse_scalar(val):
    """Parse a scalar YAML value into a Python object."""
    if val == "":
        return None
    # Quoted string
    if (val.startswith('"') and val.endswith('"')) or (
        val.startswith("'") and val.endswith("'")
    ):
        return val[1:-1]
    # Flow list
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(item.strip()) for item in inner.split(",")]
    # Boolean
    if val in ("true", "True", "TRUE"):
        return True
    if val in ("false", "False", "FALSE"):
        return False
    if val in ("null", "None", "~"):
        return None
    # Integer
    try:
        return int(val)
    except ValueError:
        pass
    # Float
    try:
        return float(val)
    except ValueError:
        pass
    return val


# ─── Constants ──────────────────────────────────────────────────────────────

ALLOWED_TYPES = frozenset({
    "decision", "memory", "reflection", "context", "knowledge", "artifact",
})
ALLOWED_CLASSES = frozenset({"perene", "volátil"})
ALLOWED_CONFIDENCE = frozenset({"low", "medium", "high"})

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

# ─── Schema v0.2 constants (SCHEMA-v0.2.md / ADR-023) ───────────────────────

SCHEMA_V2 = "acervo/v0.2"

V2_ALLOWED_TYPES = frozenset({
    "context", "knowledge", "decision", "episode", "entity", "intention",
    "workflow", "contract", "reflection", "persona", "prompt", "template",
    "tool", "skill", "artifact", "conflict",
})
V2_ALLOWED_STATUS = frozenset({
    "draft", "active", "superseded", "deprecated", "quarantined", "archived",
})
V2_ALLOWED_EPISTEMIC = frozenset({
    "fact", "observation", "interpretation", "hypothesis",
    "decision", "preference", "rule", "intention",
})
V2_ALLOWED_CONFIDENCE = frozenset({"high", "likely", "possible", "low"})
V2_ALLOWED_SENSITIVITY = frozenset({"normal", "restricted"})

# Types for which Tier 1 (epistemic layer) is required (V2-040).
V2_TIER1_TYPES = frozenset({
    "knowledge", "context", "decision", "reflection", "entity", "conflict",
})

# Home-directory → type map (V2-020). `_meta` is exempt; `conflict` objects
# are exempt (they live in knowledge/); `cross-refs` holds knowledge objects.
V2_DIR_TO_TYPE = {
    "decisions": "decision",
    "knowledge": "knowledge",
    "context": "context",
    "episodes": "episode",
    "entities": "entity",
    "intentions": "intention",
    "workflows": "workflow",
    "contracts": "contract",
    "reflections": "reflection",
    "persona": "persona",
    "prompts": "prompt",
    "templates": "template",
    "tools": "tool",
    "skills": "skill",
    "cross-refs": "knowledge",
}
V2_LAYER_ROOTS = ("micro", "global", "shared")

# V2-060 trust gate: secret-shaped string patterns.
V2_SECRET_PATTERNS = (
    ("OpenAI-style API key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("GitHub token", re.compile(r"ghp_[A-Za-z0-9]{30,}")),
    ("AWS access key ID", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Slack token", re.compile(r"xox[bpars]-[A-Za-z0-9-]{10,}")),
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("Telegram bot token", re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b")),
)

# ─── Format helpers ─────────────────────────────────────────────────────────


def _is_valid_date(value):
    """True if value is a valid YYYY-MM-DD calendar date."""
    if not isinstance(value, str) or not DATE_RE.match(value):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def _is_valid_datetime(value):
    """True if value is a valid YYYY-MM-DDTHH:MM:SSZ UTC datetime."""
    if not isinstance(value, str) or not DATETIME_RE.match(value):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        return True
    except ValueError:
        return False


def _parse_dt(value):
    """Parse a UTC datetime string. Returns datetime or None."""
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, TypeError):
        return None


# ─── Frontmatter extraction ─────────────────────────────────────────────────


def extract_frontmatter(text):
    """Extract frontmatter and body from markdown text.

    Returns ``(data, body, structural_issues)`` where:
      - ``data`` is the parsed frontmatter dict (or ``None`` on failure)
      - ``body`` is the markdown content after the closing delimiter
      - ``structural_issues`` is a list of ``(rule_id, severity, message)``
        tuples for V-001 through V-004
    """
    issues = []
    # Strip a leading UTF-8 BOM so a BOM-prefixed (but otherwise valid) file is
    # not spuriously rejected by V-001. Editors that write UTF-8-with-BOM would
    # otherwise make every Acervo file fail the opening-delimiter check.
    if text.startswith("﻿"):
        text = text[1:]
    lines = text.split("\n")

    # V-001: File must start with ---\n
    if not lines or lines[0].rstrip("\r") != "---":
        issues.append((
            "V-001", "ERROR",
            "File must start with '---' (YAML frontmatter opening delimiter)",
        ))
        return None, text, issues

    # V-002: Find closing ---
    closing_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].rstrip("\r") == "---":
            closing_idx = idx
            break

    if closing_idx is None:
        issues.append((
            "V-002", "ERROR",
            "Missing closing '---' delimiter after frontmatter",
        ))
        return None, text, issues

    yaml_text = "\n".join(lines[1:closing_idx])
    body = "\n".join(lines[closing_idx + 1:])

    # V-003: Parse YAML
    data, err = _parse_yaml(yaml_text)
    if err is not None:
        issues.append(("V-003", "ERROR", f"Invalid YAML: {err}"))
        return None, body, issues

    if data is None:
        data = {}

    if not isinstance(data, dict):
        issues.append((
            "V-003", "ERROR",
            f"Frontmatter must be a YAML mapping, got {type(data).__name__}",
        ))
        return None, body, issues

    # V-004: Body should be non-empty (WARN)
    if not body.strip():
        issues.append((
            "V-004", "WARN",
            "File body is empty (non-empty markdown body recommended)",
        ))

    return data, body, issues


# ─── Validation rule groups ─────────────────────────────────────────────────
# Each function appends (rule_id, severity, message) tuples to ``issues``.


def _check_okf_presence(data, issues):
    """V-010 through V-014: mandatory OKF canonical fields present."""
    for field, rule_id in [
        ("type", "V-010"),
        ("title", "V-011"),
        ("description", "V-012"),
        ("tags", "V-013"),
        ("timestamp", "V-014"),
    ]:
        if field not in data:
            issues.append((rule_id, "ERROR", f"Missing required field '{field}'"))


def _check_okf_values(data, issues):
    """V-020 through V-030: OKF canonical field value constraints."""
    # type
    if "type" in data:
        if not isinstance(data["type"], str):
            issues.append(("V-020", "ERROR",
                           f"'type' must be a string, got {type(data['type']).__name__}"))
        elif data["type"] not in ALLOWED_TYPES:
            issues.append(("V-020", "ERROR",
                           f"'type' must be one of {sorted(ALLOWED_TYPES)}, "
                           f"got '{data['type']}'"))

    # title
    if "title" in data:
        title = data["title"]
        if not isinstance(title, str) or not title.strip():
            issues.append(("V-021", "ERROR", "'title' must be a non-empty string"))
        elif isinstance(title, str):
            if "\n" in title or "\r" in title:
                issues.append(("V-023", "ERROR", "'title' must not contain newlines"))
            if len(title) > 200:
                issues.append(("V-022", "WARN",
                               f"'title' exceeds 200 characters ({len(title)} chars)"))

    # description
    if "description" in data:
        desc = data["description"]
        if not isinstance(desc, str) or not desc.strip():
            issues.append(("V-024", "ERROR", "'description' must be a non-empty string"))
        elif isinstance(desc, str):
            if "\n" in desc or "\r" in desc:
                issues.append(("V-025", "WARN",
                               "'description' should not contain newlines"))
            if len(desc) > 120:
                issues.append(("V-026", "WARN",
                               f"'description' exceeds 120 characters ({len(desc)} chars)"))

    # tags
    if "tags" in data:
        tags = data["tags"]
        if not isinstance(tags, list):
            issues.append(("V-027", "ERROR",
                           f"'tags' must be a YAML list, got {type(tags).__name__}"))
        else:
            for idx, tag in enumerate(tags):
                if not isinstance(tag, str) or not tag.strip():
                    issues.append(("V-028", "ERROR",
                                   f"'tags[{idx}]' must be a non-empty string, "
                                   f"got {repr(tag)}"))

    # timestamp
    if "timestamp" in data:
        ts = data["timestamp"]
        if not isinstance(ts, str) or not DATE_RE.match(ts):
            issues.append(("V-029", "ERROR",
                           f"'timestamp' must match YYYY-MM-DD, got {repr(ts)}"))
        elif not _is_valid_date(ts):
            issues.append(("V-030", "ERROR",
                           f"'timestamp' is not a valid calendar date: {repr(ts)}"))


def _check_acervo_extension(data, issues):
    """V-040 through V-046: Acervo extension field rules."""
    # class
    if "class" not in data:
        issues.append(("V-040", "ERROR", "Missing required field 'class'"))
    else:
        cls = data["class"]
        if not isinstance(cls, str):
            issues.append(("V-041", "ERROR",
                           f"'class' must be a string, got {type(cls).__name__}"))
        elif cls not in ALLOWED_CLASSES:
            issues.append(("V-041", "ERROR",
                           f"'class' must be 'perene' or 'volátil', got '{cls}'"))

    # created_at
    if "created_at" not in data:
        issues.append(("V-042", "ERROR", "Missing required field 'created_at'"))
    else:
        ca = data["created_at"]
        if not isinstance(ca, str) or not DATETIME_RE.match(ca):
            issues.append(("V-043", "ERROR",
                           f"'created_at' must match YYYY-MM-DDTHH:MM:SSZ, got {repr(ca)}"))
        elif not _is_valid_datetime(ca):
            issues.append(("V-044", "ERROR",
                           f"'created_at' is not a valid datetime: {repr(ca)}"))

    _check_optional_timestamps(data, issues)


def _check_optional_timestamps(data, issues):
    """V-045 / V-046: optional lifecycle timestamps (shared by v1 and v2)."""
    # last_accessed_at (optional)
    if "last_accessed_at" in data:
        la = data["last_accessed_at"]
        if not isinstance(la, str) or not DATETIME_RE.match(la) or not _is_valid_datetime(la):
            issues.append(("V-045", "ERROR",
                           f"'last_accessed_at' must match YYYY-MM-DDTHH:MM:SSZ, "
                           f"got {repr(la)}"))

    # promoted_at (optional)
    if "promoted_at" in data:
        pa = data["promoted_at"]
        if not isinstance(pa, str) or not DATETIME_RE.match(pa) or not _is_valid_datetime(pa):
            issues.append(("V-046", "ERROR",
                           f"'promoted_at' must match YYYY-MM-DDTHH:MM:SSZ, "
                           f"got {repr(pa)}"))


def _check_deprecation(data, issues):
    """V-050 through V-056: deprecation field rules."""
    deprecated = data.get("deprecated")

    # V-050: deprecated must be boolean if present
    if "deprecated" in data and not isinstance(deprecated, bool):
        issues.append(("V-050", "ERROR",
                       f"'deprecated' must be a boolean (true/false), "
                       f"got {type(data['deprecated']).__name__}"))
        return  # Can't run conditional checks without a valid boolean

    if deprecated is True:
        # V-051: deprecated_at must be present
        if "deprecated_at" not in data:
            issues.append(("V-051", "ERROR",
                           "'deprecated_at' must be present when 'deprecated: true'"))
        else:
            da = data["deprecated_at"]
            if not isinstance(da, str) or not DATETIME_RE.match(da) or not _is_valid_datetime(da):
                issues.append(("V-053", "ERROR",
                               f"'deprecated_at' must match YYYY-MM-DDTHH:MM:SSZ, "
                               f"got {repr(da)}"))

        # V-052 / V-054: deprecated_reason must be present and non-empty
        if "deprecated_reason" not in data:
            issues.append(("V-052", "ERROR",
                           "'deprecated_reason' must be present when 'deprecated: true'"))
        else:
            dr = data["deprecated_reason"]
            if not isinstance(dr, str) or not dr.strip():
                issues.append(("V-054", "ERROR",
                               "'deprecated_reason' must be a non-empty string"))
    else:
        # deprecated is absent or False — deprecation fields must NOT be present
        if "deprecated_at" in data:
            issues.append(("V-055", "ERROR",
                           "'deprecated_at' must not be present when 'deprecated' is "
                           "absent or false"))
        if "deprecated_reason" in data:
            issues.append(("V-056", "ERROR",
                           "'deprecated_reason' must not be present when 'deprecated' is "
                           "absent or false"))


def _check_quarantine(data, issues):
    """V-060 through V-068: quarantine field rules."""
    has_q_at = "quarantined_at" in data

    # V-060: quarantined_at format
    if has_q_at:
        qa = data["quarantined_at"]
        if not isinstance(qa, str) or not DATETIME_RE.match(qa) or not _is_valid_datetime(qa):
            issues.append(("V-060", "ERROR",
                           f"'quarantined_at' must match YYYY-MM-DDTHH:MM:SSZ, "
                           f"got {repr(qa)}"))

    # V-063: quarantine_reason non-empty if present
    if "quarantine_reason" in data:
        qr = data["quarantine_reason"]
        if not isinstance(qr, str) or not qr.strip():
            issues.append(("V-063", "ERROR",
                           "'quarantine_reason' must be a non-empty string"))

    # V-064: quarantine_expires_at format if present
    if "quarantine_expires_at" in data:
        qe = data["quarantine_expires_at"]
        if not isinstance(qe, str) or not DATETIME_RE.match(qe) or not _is_valid_datetime(qe):
            issues.append(("V-064", "ERROR",
                           f"'quarantine_expires_at' must match YYYY-MM-DDTHH:MM:SSZ, "
                           f"got {repr(qe)}"))

    if has_q_at:
        # V-061 / V-062: reason and expires must be present
        if "quarantine_reason" not in data:
            issues.append(("V-061", "ERROR",
                           "'quarantine_reason' must be present when "
                           "'quarantined_at' is present"))
        if "quarantine_expires_at" not in data:
            issues.append(("V-062", "ERROR",
                           "'quarantine_expires_at' must be present when "
                           "'quarantined_at' is present"))

        # V-065: quarantine_expires_at >= quarantined_at
        if "quarantined_at" in data and "quarantine_expires_at" in data:
            q_start = _parse_dt(data["quarantined_at"])
            q_end = _parse_dt(data["quarantine_expires_at"])
            if q_start is not None and q_end is not None and q_end < q_start:
                issues.append(("V-065", "ERROR",
                               "'quarantine_expires_at' must be ≥ 'quarantined_at' "
                               f"(got expires={data['quarantine_expires_at']}, "
                               f"quarantined={data['quarantined_at']})"))
    else:
        # quarantined_at absent — quarantine fields must NOT be present
        if "quarantine_reason" in data:
            issues.append(("V-067", "ERROR",
                           "'quarantine_reason' must not be present when "
                           "'quarantined_at' is absent"))
        if "quarantine_expires_at" in data:
            issues.append(("V-068", "ERROR",
                           "'quarantine_expires_at' must not be present when "
                           "'quarantined_at' is absent"))


def _check_cross_field(data, issues):
    """V-070 through V-072: cross-field consistency rules."""
    # V-070: date portion of created_at must equal timestamp
    if "created_at" in data and "timestamp" in data:
        ca = data["created_at"]
        ts = data["timestamp"]
        if isinstance(ca, str) and DATETIME_RE.match(ca) and isinstance(ts, str):
            ca_date = ca[:10]  # YYYY-MM-DD portion
            if ca_date != ts:
                issues.append(("V-070", "ERROR",
                               f"Date portion of 'created_at' ({ca_date}) must equal "
                               f"'timestamp' ({ts})"))

    # V-071: not simultaneously deprecated and quarantined
    deprecated = data.get("deprecated")
    if deprecated is True and "quarantined_at" in data:
        issues.append(("V-071", "ERROR",
                       "File cannot be simultaneously deprecated and quarantined "
                       "('deprecated: true' and 'quarantined_at' both present)"))

    # V-072: promoted_at + class volátil → WARN (suggest updating class)
    if "promoted_at" in data and data.get("class") == "volátil":
        issues.append(("V-072", "WARN",
                       "'promoted_at' is present but 'class' is 'volátil'. "
                       "The file is treated as 'perene' at runtime; consider "
                       "updating 'class: perene' for consistency."))


def _check_legacy(data, issues):
    """V-073 through V-076: legacy retained field rules."""
    # V-073: excrtx_type must be a string if present
    if "excrtx_type" in data:
        et = data["excrtx_type"]
        if not isinstance(et, str):
            issues.append(("V-073", "ERROR",
                           f"'excrtx_type' must be a string, got {type(et).__name__}"))

    # V-074: nature must be a string if present
    if "nature" in data:
        nat = data["nature"]
        if not isinstance(nat, str):
            issues.append(("V-074", "ERROR",
                           f"'nature' must be a string, got {type(nat).__name__}"))

    # V-075: confidence should be low/medium/high (WARN)
    if "confidence" in data:
        conf = data["confidence"]
        if not isinstance(conf, str) or conf not in ALLOWED_CONFIDENCE:
            issues.append(("V-075", "WARN",
                           f"'confidence' should be one of {sorted(ALLOWED_CONFIDENCE)}, "
                           f"got {repr(conf)}"))

    # V-076: sources must be a list if present
    if "sources" in data:
        src = data["sources"]
        if not isinstance(src, list):
            issues.append(("V-076", "ERROR",
                           f"'sources' must be a YAML list, got {type(src).__name__}"))


# ─── Schema v0.2 rule groups (SCHEMA-v0.2.md / ADR-023) ─────────────────────
#
# Not implemented here (deliberately):
#   - V2-031 (`supersedes` targets exist and are `status: superseded`) needs
#     the whole-acervo view — it is a doctor/catalog concern (acervoctl doctor,
#     Phase 1 catalog builder), not a per-file check.
#   - V2-070 (kebab-filename ↔ title coherence) is advisory and heuristic;
#     deferred with V2-031 to the doctor layer.


def _check_v2_tier0(data, issues):
    """V2-010..V2-018: Tier 0 identity fields (all mandatory)."""
    for field in ("schema", "type", "title", "description", "tags",
                  "created_at", "class", "status"):
        if field not in data:
            issues.append(("V2-010", "ERROR",
                           f"Missing required field '{field}' (Tier 0)"))

    # type — closed 16-value vocabulary
    if "type" in data:
        t = data["type"]
        if not isinstance(t, str) or t not in V2_ALLOWED_TYPES:
            issues.append(("V2-011", "ERROR",
                           f"'type' must be one of {sorted(V2_ALLOWED_TYPES)}, "
                           f"got {repr(t)}"))

    # title
    if "title" in data:
        title = data["title"]
        if not isinstance(title, str) or not title.strip():
            issues.append(("V2-012", "ERROR", "'title' must be a non-empty string"))
        else:
            if "\n" in title or "\r" in title:
                issues.append(("V2-012", "ERROR", "'title' must not contain newlines"))
            if len(title) > 200:
                issues.append(("V2-012", "WARN",
                               f"'title' exceeds 200 characters ({len(title)} chars)"))

    # description
    if "description" in data:
        desc = data["description"]
        if not isinstance(desc, str) or not desc.strip():
            issues.append(("V2-013", "ERROR",
                           "'description' must be a non-empty string"))
        else:
            if "\n" in desc or "\r" in desc:
                issues.append(("V2-013", "WARN",
                               "'description' should be a single line"))
            if len(desc) > 160:
                issues.append(("V2-013", "WARN",
                               f"'description' exceeds 160 characters ({len(desc)} chars)"))

    # tags
    if "tags" in data:
        tags = data["tags"]
        if not isinstance(tags, list):
            issues.append(("V2-014", "ERROR",
                           f"'tags' must be a YAML list, got {type(tags).__name__}"))
        else:
            for idx, tag in enumerate(tags):
                if not isinstance(tag, str) or not tag.strip():
                    issues.append(("V2-014", "ERROR",
                                   f"'tags[{idx}]' must be a non-empty string, "
                                   f"got {repr(tag)}"))

    # created_at
    if "created_at" in data:
        ca = data["created_at"]
        if not isinstance(ca, str) or not DATETIME_RE.match(ca) or not _is_valid_datetime(ca):
            issues.append(("V2-015", "ERROR",
                           f"'created_at' must match YYYY-MM-DDTHH:MM:SSZ, got {repr(ca)}"))

    # class
    if "class" in data:
        cls = data["class"]
        if not isinstance(cls, str) or cls not in ALLOWED_CLASSES:
            issues.append(("V2-016", "ERROR",
                           f"'class' must be 'perene' or 'volátil', got {repr(cls)}"))

    # status — scalar lifecycle state (v0.2 delta ②)
    if "status" in data:
        status = data["status"]
        if not isinstance(status, str) or status not in V2_ALLOWED_STATUS:
            issues.append(("V2-017", "ERROR",
                           f"'status' must be one of {sorted(V2_ALLOWED_STATUS)}, "
                           f"got {repr(status)}"))

    # timestamp — optional in v0.2 (derived at OKF export). If present it must
    # be a valid date and match created_at (V-070 logic, checked in cross-field).
    if "timestamp" in data:
        ts = data["timestamp"]
        if not isinstance(ts, str) or not _is_valid_date(ts):
            issues.append(("V2-018", "ERROR",
                           f"'timestamp' must match YYYY-MM-DD when present, got {repr(ts)}"))


def _v2_layer_info(path):
    """Locate the acervo layer a file lives in.

    Returns ``("dir", name)`` where ``name`` is the type-directory component
    (micro/{slug}/{dir}/, global/{dir}/, shared/{dir}/), ``("root", layer)``
    for files sitting directly in a layer root (e.g. shared/groups.md), or
    ``(None, None)`` when no layer marker is found in the path.
    """
    parts = Path(path).parts
    for i in range(len(parts) - 1, -1, -1):
        if parts[i] in V2_LAYER_ROOTS:
            # micro/ has one extra level: micro/{slug}/{dir}/...
            dir_idx = i + (2 if parts[i] == "micro" else 1)
            if dir_idx >= len(parts) - 1:
                return "root", parts[i]
            return "dir", parts[dir_idx]
    return None, None


def _check_v2_dir_match(data, issues, path):
    """V2-020: `type` must match the home directory."""
    kind, name = _v2_layer_info(path)
    if kind is None:
        return  # path carries no layer marker — cannot derive the home dir
    if kind == "root":
        issues.append(("V2-020", "WARN",
                       f"file sits directly in the '{name}/' layer root — "
                       f"type↔directory check skipped"))
        return
    if name == "_meta":
        return  # index/log pages — exempt
    t = data.get("type")
    if t == "conflict":
        return  # conflict objects live in knowledge/ — exempt
    expected = V2_DIR_TO_TYPE.get(name)
    if expected is None:
        issues.append(("V2-020", "WARN",
                       f"directory '{name}/' has no v0.2 type mapping — "
                       f"type↔directory check skipped"))
        return
    if isinstance(t, str) and t in V2_ALLOWED_TYPES and t != expected:
        issues.append(("V2-020", "ERROR",
                       f"'type: {t}' does not match home directory '{name}/' "
                       f"(expected 'type: {expected}')"))


def _check_v2_status_consistency(data, issues):
    """V2-030 / V2-032 / V2-033 (+ V-071): status ⇔ lifecycle field coherence."""
    status = data.get("status")
    deprecated = data.get("deprecated")
    superseded_by = data.get("superseded_by")
    has_superseded_by = superseded_by not in (None, "")
    has_quarantine = "quarantined_at" in data

    # V2-030: superseded ⇔ superseded_by
    if status == "superseded" and not has_superseded_by:
        issues.append(("V2-030", "ERROR",
                       "'status: superseded' requires 'superseded_by' to be set"))
    if has_superseded_by and status != "superseded":
        issues.append(("V2-030", "ERROR",
                       f"'superseded_by' is set but 'status' is {repr(status)} "
                       f"(must be 'superseded')"))

    # V2-032: deprecated ⇔ deprecated:true trio (trio internals via V-050..V-056)
    if status == "deprecated" and deprecated is not True:
        issues.append(("V2-032", "ERROR",
                       "'status: deprecated' requires 'deprecated: true' "
                       "(with 'deprecated_at' and 'deprecated_reason')"))
    if deprecated is True and status != "deprecated":
        issues.append(("V2-032", "ERROR",
                       f"'deprecated: true' but 'status' is {repr(status)} "
                       f"(must be 'deprecated')"))

    # V2-033: quarantined ⇔ quarantine trio (trio internals via V-060..V-068)
    if status == "quarantined" and not has_quarantine:
        issues.append(("V2-033", "ERROR",
                       "'status: quarantined' requires the quarantine trio "
                       "('quarantined_at', 'quarantine_reason', "
                       "'quarantine_expires_at')"))
    if has_quarantine and status != "quarantined":
        issues.append(("V2-033", "ERROR",
                       f"'quarantined_at' is set but 'status' is {repr(status)} "
                       f"(must be 'quarantined')"))

    # V-071 stands in v0.2: deprecated XOR quarantined
    if deprecated is True and has_quarantine:
        issues.append(("V-071", "ERROR",
                       "File cannot be simultaneously deprecated and quarantined "
                       "('deprecated: true' and 'quarantined_at' both present)"))


def _check_v2_tier1(data, issues):
    """V2-040: Tier 1 epistemic layer for the six epistemic types."""
    t = data.get("type")
    if t in V2_TIER1_TYPES:
        if "epistemic" not in data:
            issues.append(("V2-040", "ERROR",
                           f"'epistemic' is required for type '{t}' (Tier 1)"))
        for field in ("confidence", "sources", "observed_at"):
            if field not in data:
                issues.append(("V2-040", "WARN",
                               f"'{field}' is recommended for type '{t}' (Tier 1)"))

    # Enum checks apply whenever the fields are present, regardless of type.
    if "epistemic" in data:
        ep = data["epistemic"]
        if not isinstance(ep, str) or ep not in V2_ALLOWED_EPISTEMIC:
            issues.append(("V2-040", "ERROR",
                           f"'epistemic' must be one of {sorted(V2_ALLOWED_EPISTEMIC)}, "
                           f"got {repr(ep)}"))
    if "confidence" in data:
        conf = data["confidence"]
        if not isinstance(conf, str) or conf not in V2_ALLOWED_CONFIDENCE:
            issues.append(("V2-040", "ERROR",
                           f"'confidence' must be one of {sorted(V2_ALLOWED_CONFIDENCE)}, "
                           f"got {repr(conf)}"))


def _check_v2_type_specific(data, issues):
    """V2-050 / V2-051: per-type field obligations."""
    t = data.get("type")

    # V2-050: entity objects must declare a non-empty aliases list
    if t == "entity":
        aliases = data.get("aliases")
        if not isinstance(aliases, list) or not aliases:
            issues.append(("V2-050", "ERROR",
                           "'aliases' (non-empty list) is mandatory for "
                           "type 'entity'"))

    # V2-051: intention objects should carry a due date or a trigger
    if t == "intention" and not data.get("due") and not data.get("trigger"):
        issues.append(("V2-051", "WARN",
                       "'intention' object has neither 'due' nor 'trigger' — "
                       "prospective memory needs one to fire"))


def _check_v2_temporal(data, issues):
    """V2-041 (+ V2-084 format): world-validity window."""
    parsed = {}
    for field in ("valid_from", "valid_until"):
        value = data.get(field)
        if value is None:
            continue
        if not _is_valid_date(value):
            issues.append(("V2-084", "WARN",
                           f"'{field}' should be a YYYY-MM-DD date, got {repr(value)}"))
        else:
            parsed[field] = datetime.strptime(value, "%Y-%m-%d")

    if "valid_from" in parsed and "valid_until" in parsed:
        if parsed["valid_until"] < parsed["valid_from"]:
            issues.append(("V2-041", "ERROR",
                           f"'valid_until' ({data['valid_until']}) is before "
                           f"'valid_from' ({data['valid_from']})"))


def _check_v2_tier2_formats(data, issues):
    """V2-080..V2-083: Tier 2 optional-field format checks (WARN on malformed)."""
    for field, rule_id in (("supersedes", "V2-080"), ("entities", "V2-081")):
        value = data.get(field)
        if value is None:
            continue
        if not isinstance(value, list) or any(
            not isinstance(item, str) or not item.strip() for item in value
        ):
            issues.append((rule_id, "WARN",
                           f"'{field}' should be a list of non-empty strings, "
                           f"got {repr(value)}"))

    sensitivity = data.get("sensitivity")
    if sensitivity is not None and sensitivity not in V2_ALLOWED_SENSITIVITY:
        issues.append(("V2-082", "WARN",
                       f"'sensitivity' should be one of "
                       f"{sorted(V2_ALLOWED_SENSITIVITY)}, got {repr(sensitivity)}"))

    review_after = data.get("review_after")
    if review_after is not None and not _is_valid_date(review_after):
        issues.append(("V2-083", "WARN",
                       f"'review_after' should be a YYYY-MM-DD date, "
                       f"got {repr(review_after)}"))


def _v2_secret_is_masked(container, match):
    """True if a secret-shaped match is a masked/redacted form."""
    if "***" in container or "REDACTED" in container:
        return True
    if container[match.end():match.end() + 3] == "...":
        return True
    return container.rstrip().endswith("...")


def _check_v2_secrets(data, body, issues):
    """V2-060 trust gate: secret-shaped strings in any field or the body."""
    containers = []  # (where, text) — masking is evaluated per container

    def _collect(value):
        if isinstance(value, str):
            containers.append(("frontmatter", value))
        elif isinstance(value, list):
            for item in value:
                _collect(item)
        elif isinstance(value, dict):
            for item in value.values():
                _collect(item)

    _collect(data)
    for line in (body or "").split("\n"):
        containers.append(("body", line))

    seen = set()
    for where, text in containers:
        for name, pattern in V2_SECRET_PATTERNS:
            if (name, where) in seen:
                continue
            for match in pattern.finditer(text):
                if _v2_secret_is_masked(text, match):
                    continue
                seen.add((name, where))
                issues.append(("V2-060", "ERROR",
                               f"secret-shaped string ({name}) detected in "
                               f"{where} — remove or mask it before committing"))
                break


def _check_v2_cross_misc(data, issues):
    """v0.2 carry-overs of V-070 / V-072."""
    # V-070: if the (now optional) timestamp is present, its date must equal
    # the date portion of created_at.
    if "timestamp" in data and "created_at" in data:
        ca = data["created_at"]
        ts = data["timestamp"]
        if isinstance(ca, str) and DATETIME_RE.match(ca) and isinstance(ts, str):
            if ca[:10] != ts:
                issues.append(("V-070", "ERROR",
                               f"Date portion of 'created_at' ({ca[:10]}) must "
                               f"equal 'timestamp' ({ts})"))

    # V-072: promoted_at + class volátil → WARN
    if "promoted_at" in data and data.get("class") == "volátil":
        issues.append(("V-072", "WARN",
                       "'promoted_at' is present but 'class' is 'volátil'. "
                       "The file is treated as 'perene' at runtime; consider "
                       "updating 'class: perene' for consistency."))


def _validate_v2(data, body, issues, path):
    """Run the full schema v0.2 rule set (structural V-001..V-004 already ran)."""
    _check_v2_tier0(data, issues)
    _check_v2_dir_match(data, issues, path)
    _check_optional_timestamps(data, issues)      # V-045 / V-046 (unchanged)
    _check_deprecation(data, issues)              # V-050..V-056 trio internals
    _check_quarantine(data, issues)               # V-060..V-068 trio internals
    _check_v2_status_consistency(data, issues)    # V2-030/032/033 + V-071
    _check_v2_tier1(data, issues)                 # V2-040
    _check_v2_type_specific(data, issues)         # V2-050 / V2-051
    _check_v2_temporal(data, issues)              # V2-041 (+ V2-084)
    _check_v2_tier2_formats(data, issues)         # V2-080..V2-083
    _check_v2_secrets(data, body, issues)         # V2-060
    _check_v2_cross_misc(data, issues)            # V-070 / V-072


# ─── Per-file validation orchestrator ───────────────────────────────────────


def validate_file(path, migration_warn=True):
    """Validate a single markdown file.

    Returns ``(path, issues, schema_version)`` where ``issues`` is a list of
    ``(rule_id, severity, message)`` tuples and ``schema_version`` is ``"v1"``
    or ``"v2"`` (files whose frontmatter cannot be parsed count as v1).
    """
    issues = []
    schema_version = "v1"
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        issues.append(("V-000", "ERROR", f"Cannot read file: {exc}"))
        return str(path), issues, schema_version

    data, body, structural = extract_frontmatter(text)
    issues.extend(structural)

    if data is not None:
        if data.get("schema") == SCHEMA_V2:
            schema_version = "v2"
            _validate_v2(data, body, issues, path)
        else:
            _check_okf_presence(data, issues)
            _check_okf_values(data, issues)
            _check_acervo_extension(data, issues)
            _check_deprecation(data, issues)
            _check_quarantine(data, issues)
            _check_cross_field(data, issues)
            _check_legacy(data, issues)
            if migration_warn:
                issues.append(("V2-000", "WARN",
                               "file not yet migrated to acervo/v0.2"))

    return str(path), issues, schema_version


# Non-semantic areas of the Acervo. These hold raw inputs, produced artifacts,
# operational queues, or superseded pages — none of which are semantic wiki
# pages, so they do not carry OKF frontmatter and must not be validated by
# default (otherwise --dir floods with false V-001/V-010 errors). Matched as
# path *components* relative to the scanned root.
DEFAULT_EXCLUDE_DIRS = frozenset({
    "_artifacts", "raw", "_archive", ".quarantine",
    "_inbox", "_tasks", "_routines", "_automations",
    # scaffolds / fixtures — not live semantic pages (carry placeholders)
    "_template",
    "_retired",
    "_ops_snapshots", "_fixture",
    # macro/ is the executive constitution, loaded VERBATIM into context at every
    # boot (cat SOUL.md/valores.md/estilo.md). Frontmatter there would leak as
    # literal identity context, so macro carries none — migrate_frontmatter.py
    # excludes it for the same reason. Keep the two tools in sync.
    "macro",
})
# Top-level non-semantic files (relative to the scanned root).
DEFAULT_EXCLUDE_NAMES = frozenset({"README.md"})


def _is_excluded(rel_parts):
    """True if a path (given as relative parts) is in a non-semantic area."""
    if any(part in DEFAULT_EXCLUDE_DIRS for part in rel_parts[:-1]):
        return True
    # Top-level README.md (and a README.md directly inside an excluded-style root)
    if rel_parts[-1] in DEFAULT_EXCLUDE_NAMES:
        return True
    return False


def validate_dir(dir_path, apply_excludes=True, migration_warn=True):
    """Validate all ``.md`` files in a directory recursively.

    By default, files under non-semantic areas (``DEFAULT_EXCLUDE_DIRS``) and
    top-level READMEs are skipped. Pass ``apply_excludes=False`` to validate
    every ``.md`` file (legacy behavior).

    Returns ``(results, skipped_count)`` where ``results`` is a list of
    ``(path, issues, schema_version)`` tuples sorted by path.
    """
    base = Path(dir_path)
    results = []
    skipped = 0
    for md_file in sorted(base.rglob("*.md")):
        if apply_excludes:
            rel_parts = md_file.relative_to(base).parts
            if _is_excluded(rel_parts):
                skipped += 1
                continue
        results.append(validate_file(md_file, migration_warn=migration_warn))
    return results, skipped


# ─── Output formatting ──────────────────────────────────────────────────────


def _has_errors(issues):
    return any(sev == "ERROR" for _rule, sev, _msg in issues)


def print_default(results):
    """Print per-file results (one block per file)."""
    for path, issues, _version in results:
        if _has_errors(issues):
            print(f"FAIL  {path}")
        else:
            print(f"PASS  {path}")
        for rule_id, severity, message in issues:
            tag = "ERROR" if severity == "ERROR" else "WARN "
            print(f"      [{rule_id}] {tag}: {message}")


def print_report(results):
    """Print a summary report."""
    total = len(results)
    valid = sum(1 for _p, iss, _v in results if not _has_errors(iss))
    invalid = total - valid
    v1_count = sum(1 for _p, _iss, v in results if v == "v1")
    v2_count = sum(1 for _p, _iss, v in results if v == "v2")

    print("Frontmatter Validation Report")
    print("=============================")
    print(f"Scanned: {total} files")
    print(f"  Schema v1 (pre-v0.2): {v1_count}")
    print(f"  Schema acervo/v0.2:   {v2_count}")
    print(f"Valid:   {valid}")
    print(f"Invalid: {invalid}")
    if invalid > 0:
        print("Errors:")
        for path, issues, _version in results:
            for rule_id, severity, message in issues:
                if severity == "ERROR":
                    print(f"  {path}: [{rule_id}] {message}")


# ─── CLI ────────────────────────────────────────────────────────────────────


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate Acervo Cognitivo YAML frontmatter (ADR-013 schema).",
    )
    parser.add_argument(
        "--file", metavar="PATH",
        help="Validate a single markdown file.",
    )
    parser.add_argument(
        "--dir", metavar="PATH",
        help="Validate all .md files in a directory (recursive).",
    )
    parser.add_argument(
        "--report", action="store_true",
        help="Output a summary report instead of per-file detail.",
    )
    parser.add_argument(
        "--no-exclude", action="store_true",
        help="Validate every .md file, including non-semantic areas "
             "(_artifacts/, raw/, _archive/, .quarantine/, _inbox/, READMEs).",
    )
    parser.add_argument(
        "--no-migration-warn", action="store_true",
        help="Suppress the V2-000 WARN on files not yet migrated to "
             "schema acervo/v0.2.",
    )
    args = parser.parse_args(argv)

    if not args.file and not args.dir:
        parser.error("at least one of --file or --dir is required")

    migration_warn = not args.no_migration_warn

    # Collect results
    results = []

    if args.file:
        file_path = Path(args.file)
        if not file_path.is_file():
            print(f"Error: file not found: {args.file}", file=sys.stderr)
            return 2
        results.append(validate_file(file_path, migration_warn=migration_warn))

    skipped = 0
    if args.dir:
        dir_path = Path(args.dir)
        if not dir_path.is_dir():
            print(f"Error: directory not found: {args.dir}", file=sys.stderr)
            return 2
        dir_results, skipped = validate_dir(
            dir_path, apply_excludes=not args.no_exclude,
            migration_warn=migration_warn,
        )
        results.extend(dir_results)

    # Output
    if args.report:
        print_report(results)
        if skipped:
            print(f"Skipped: {skipped} files in non-semantic areas "
                  f"(use --no-exclude to include them)")
    else:
        print_default(results)
        if skipped:
            print(f"# Skipped {skipped} non-semantic files "
                  f"(_artifacts/raw/_archive/.quarantine/_inbox/README; "
                  f"--no-exclude to include)")

    # Exit code
    return 1 if any(_has_errors(iss) for _p, iss, _v in results) else 0


if __name__ == "__main__":
    sys.exit(main())
