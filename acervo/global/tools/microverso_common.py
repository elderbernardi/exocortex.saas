#!/usr/bin/env python3
"""microverso_common.py — shared helpers for microverso export/import tools.

Acervo/runtime resolution, the OKF frontmatter gate (located dynamically so it
works both in the dev repo and in the runtime acervo), integrity hashing, and
frontmatter line helpers. Used by microverso_package.py and microverso_install.py.
"""

import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Dir/file names excluded from a clean-portable package (Docker-like).
EXCLUDE_DIRS = {".quarantine", "_archive", "__pycache__", ".git",
                "snapshots", "drafts", "node_modules", ".pytest_cache"}
EXCLUDE_FILES = {".DS_Store"}


def resolve_acervo(override=None):
    """Resolve acervo root: explicit override > $ACERVO > $EXOCORTEX_HOME/acervo > $HERMES_HOME/acervo."""
    if override:
        return Path(override).expanduser()
    if env := os.environ.get("ACERVO"):
        return Path(env)
    exo_home = os.environ.get("EXOCORTEX_HOME", os.path.expanduser("~/exocortex"))
    candidate = Path(exo_home) / "acervo"
    if candidate.is_dir():
        return candidate
    hermes_home = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
    return Path(hermes_home) / "acervo"


def resolve_hermes_skills():
    """Resolve the excrtx skills directory in the Hermes runtime."""
    hermes_home = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
    return Path(hermes_home) / "skills" / "excrtx"


def find_repo_root(start=None):
    """Walk upward looking for the exocortex.saas repo (has scripts/validate_frontmatter.py)."""
    if env := os.environ.get("EXOCORTEX_REPO"):
        p = Path(env)
        if (p / "scripts" / "validate_frontmatter.py").is_file():
            return p
    here = Path(start or __file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "scripts" / "validate_frontmatter.py").is_file():
            return parent
    return None


def find_validator():
    """Locate scripts/validate_frontmatter.py, or None if unavailable at runtime."""
    repo = find_repo_root()
    if repo:
        return repo / "scripts" / "validate_frontmatter.py"
    return None


def okf_gate(target_dir):
    """Run the OKF frontmatter validator over a directory.

    Returns (status, output) where status is 'pass', 'fail', or 'skipped'
    (validator not found — degraded gate, runtime context without the repo).
    """
    validator = find_validator()
    if validator is None:
        return "skipped", "validate_frontmatter.py not found — OKF gate skipped (non-repo runtime)"
    proc = subprocess.run(
        [sys.executable, str(validator), "--dir", str(target_dir), "--report"],
        capture_output=True, text=True,
    )
    status = "pass" if proc.returncode == 0 else "fail"
    return status, (proc.stdout + proc.stderr).strip()


def split_frontmatter(text):
    """Return (frontmatter_lines, rest_text) if text starts with a --- block, else (None, text)."""
    if not text.startswith("---"):
        return None, text
    lines = text.split("\n")
    # find closing --- (second delimiter)
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i], "\n".join(lines[i + 1:])
    return None, text


def frontmatter_value(text, key):
    """Read a top-level scalar value from a markdown file's frontmatter (or None)."""
    fm, _ = split_frontmatter(text)
    if fm is None:
        return None
    prefix = f"{key}:"
    for line in fm:
        if line.strip().startswith(prefix):
            return line.split(":", 1)[1].strip()
    return None


def strip_runtime_fields(text, fields=("last_accessed_at",)):
    """Remove per-instance runtime frontmatter lines (e.g. last_accessed_at)."""
    fm, _ = split_frontmatter(text)
    if fm is None:
        return text
    lines = text.split("\n")
    out = []
    in_fm = False
    seen_open = False
    for line in lines:
        if line.strip() == "---":
            if not seen_open:
                seen_open, in_fm = True, True
                out.append(line)
                continue
            if in_fm:
                in_fm = False
                out.append(line)
                continue
        if in_fm and any(line.strip().startswith(f"{f}:") for f in fields):
            continue
        out.append(line)
    return "\n".join(out)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_manifest_sum(pkg_dir, exclude_names=("MANIFEST.sum",)):
    """Write MANIFEST.sum: '<sha256>  <relpath>' for every file, sorted. Returns digest."""
    pkg_dir = Path(pkg_dir)
    entries = []
    for path in sorted(pkg_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(pkg_dir).as_posix()
        if rel in exclude_names:
            continue
        entries.append(f"{sha256_file(path)}  {rel}")
    content = "\n".join(entries) + "\n"
    (pkg_dir / "MANIFEST.sum").write_text(content, encoding="utf-8")
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def verify_manifest_sum(pkg_dir):
    """Verify MANIFEST.sum against package contents. Returns (ok, list_of_problems)."""
    pkg_dir = Path(pkg_dir)
    sum_file = pkg_dir / "MANIFEST.sum"
    if not sum_file.is_file():
        return False, ["MANIFEST.sum missing"]
    expected = {}
    for line in sum_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, _, rel = line.partition("  ")
        expected[rel] = digest
    problems = []
    actual = {}
    for path in pkg_dir.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(pkg_dir).as_posix()
        if rel == "MANIFEST.sum":
            continue
        actual[rel] = sha256_file(path)
    for rel, digest in expected.items():
        if rel not in actual:
            problems.append(f"missing file: {rel}")
        elif actual[rel] != digest:
            problems.append(f"checksum mismatch: {rel}")
    for rel in actual:
        if rel not in expected:
            problems.append(f"unexpected file: {rel}")
    return (not problems), problems


def safe_merge(src_dir, dst_dir):
    """Merge src into dst without overwriting existing files (rsync --ignore-existing, cp -rn fallback)."""
    src_dir, dst_dir = Path(src_dir), Path(dst_dir)
    dst_dir.mkdir(parents=True, exist_ok=True)
    if shutil.which("rsync"):
        subprocess.run(["rsync", "-a", "--ignore-existing",
                        f"{src_dir}/", f"{dst_dir}/"], check=True)
        return "rsync"
    # Python fallback (cp -rn semantics)
    for path in sorted(src_dir.rglob("*")):
        rel = path.relative_to(src_dir)
        target = dst_dir / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    return "cp-fallback"
