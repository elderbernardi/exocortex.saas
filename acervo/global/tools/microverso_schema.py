#!/usr/bin/env python3
"""microverso_schema.py — excrtx/v1 Microverso manifest loader & validator.

Deterministic (no LLM) validation of a ``microverso.yaml`` against the
``excrtx/v1`` package schema documented in
``acervo/global/contracts/microverso-package-spec.md``.

Shared by the export tool (``microverso_package.py``) and the import tool
(``microverso_install.py``). Mirrors the conventions of
``scripts/validate_frontmatter.py``: PyYAML preferred, exit codes
0 = valid (warnings allowed) / 1 = error / 2 = file not found.

Usage:
    python3 microverso_schema.py --file path/to/microverso.yaml
    python3 microverso_schema.py --file path/to/microverso.yaml --report
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
    _HAS_PYYAML = True
except ImportError:  # pragma: no cover - exercised only without PyYAML
    _HAS_PYYAML = False

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+([-+][0-9A-Za-z.-]+)?$")

API_VERSION = "excrtx/v1"
KIND = "Microverso"

ERROR = "ERROR"
WARN = "WARN"


def load_manifest(path):
    """Load a microverso.yaml. Returns (data, error_message)."""
    p = Path(path)
    if not p.is_file():
        return None, f"manifest not found: {path}"
    text = p.read_text(encoding="utf-8-sig")
    if not _HAS_PYYAML:
        return None, (
            "PyYAML required to parse microverso.yaml (nested structure). "
            "Install with: uv pip install pyyaml (or pip install pyyaml)"
        )
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        return None, f"invalid YAML: {exc}"
    if not isinstance(data, dict):
        return None, "manifest root must be a mapping"
    return data, None


def _is_str_list(value):
    return isinstance(value, list) and all(isinstance(x, str) for x in value)


def _check_list(data, key, issues):
    """A requires.* / compat.* list field: absent is fine, present must be a list."""
    if key in data and not isinstance(data[key], list):
        issues.append((ERROR, "MV-R02", f"requires.{key} must be a list"))


def _skill_name(entry):
    """Normalize a requires.skills entry (str or {name: ...}) to a name string."""
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict):
        return entry.get("name")
    return None


def validate_manifest(data):
    """Validate a parsed manifest dict. Returns list of (severity, code, message)."""
    issues = []

    if data.get("apiVersion") != API_VERSION:
        issues.append((ERROR, "MV-001",
                       f"apiVersion must be '{API_VERSION}' (got {data.get('apiVersion')!r})"))
    if data.get("kind") != KIND:
        issues.append((ERROR, "MV-002",
                       f"kind must be '{KIND}' (got {data.get('kind')!r})"))

    # metadata
    meta = data.get("metadata")
    if not isinstance(meta, dict):
        issues.append((ERROR, "MV-010", "metadata block is required (mapping)"))
        meta = {}
    name = meta.get("name")
    if not name:
        issues.append((ERROR, "MV-011", "metadata.name is required"))
    elif not SLUG_RE.match(str(name)):
        issues.append((ERROR, "MV-012", f"metadata.name must be kebab-case slug (got {name!r})"))
    version = meta.get("version")
    if not version:
        issues.append((ERROR, "MV-013", "metadata.version is required"))
    elif not SEMVER_RE.match(str(version)):
        issues.append((ERROR, "MV-014", f"metadata.version must be semver X.Y.Z (got {version!r})"))
    if not meta.get("description"):
        issues.append((ERROR, "MV-015", "metadata.description is required"))
    if "tags" in meta and not _is_str_list(meta["tags"]):
        issues.append((WARN, "MV-016", "metadata.tags should be a list of strings"))

    # requires (optional block)
    req = data.get("requires")
    if req is not None:
        if not isinstance(req, dict):
            issues.append((ERROR, "MV-R01", "requires must be a mapping"))
        else:
            for key in ("python_packages", "node_packages", "mcps", "env", "system"):
                _check_list(req, key, issues)
            if "skills" in req:
                if not isinstance(req["skills"], list):
                    issues.append((ERROR, "MV-R02", "requires.skills must be a list"))
                else:
                    for entry in req["skills"]:
                        nm = _skill_name(entry)
                        if not nm:
                            issues.append((ERROR, "MV-R03",
                                           f"requires.skills entry missing name: {entry!r}"))
                        elif not str(nm).startswith("excrtx-"):
                            issues.append((WARN, "MV-R04",
                                           f"skill '{nm}' lacks excrtx- prefix"))

    # compat (optional)
    compat = data.get("compat")
    if compat is not None and not isinstance(compat, dict):
        issues.append((ERROR, "MV-C01", "compat must be a mapping"))
    elif isinstance(compat, dict) and "platforms" in compat and not _is_str_list(compat["platforms"]):
        issues.append((WARN, "MV-C02", "compat.platforms should be a list of strings"))

    # tree (optional)
    tree = data.get("tree")
    if tree is not None and not isinstance(tree, dict):
        issues.append((ERROR, "MV-T01", "tree must be a mapping of dir -> description"))

    # hooks (optional) — relative paths only
    hooks = data.get("hooks")
    if hooks:
        if not isinstance(hooks, dict):
            issues.append((ERROR, "MV-H01", "hooks must be a mapping"))
        else:
            for hk in ("post_install", "validate"):
                hv = hooks.get(hk)
                if hv is None:
                    continue
                if not isinstance(hv, str) or hv.startswith("/") or ".." in hv.split("/"):
                    issues.append((ERROR, "MV-H02",
                                   f"hooks.{hk} must be a relative path without '..' (got {hv!r})"))

    return issues


def has_errors(issues):
    return any(sev == ERROR for sev, _c, _m in issues)


def _main(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate a microverso.yaml against the excrtx/v1 schema.")
    parser.add_argument("--file", metavar="PATH", required=True,
                        help="Path to microverso.yaml")
    parser.add_argument("--report", action="store_true",
                        help="Print a one-line PASS/FAIL summary only")
    args = parser.parse_args(argv)

    data, err = load_manifest(args.file)
    if err:
        print(f"Error: {err}", file=sys.stderr)
        return 2 if "not found" in err else 1

    issues = validate_manifest(data)
    name = (data.get("metadata") or {}).get("name", "?")
    version = (data.get("metadata") or {}).get("version", "?")

    if args.report:
        verdict = "FAIL" if has_errors(issues) else "PASS"
        print(f"{verdict}  {name} v{version}  ({len(issues)} issue(s))")
    else:
        if not issues:
            print(f"PASS  {name} v{version} — manifest valid (excrtx/v1)")
        for sev, code, msg in issues:
            print(f"  [{sev}] {code}: {msg}")

    return 1 if has_errors(issues) else 0


if __name__ == "__main__":
    sys.exit(_main())
