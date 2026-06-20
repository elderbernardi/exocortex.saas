#!/usr/bin/env python3
"""microverso_package.py — export a microverso as a portable .mvpkg (Docker-like).

Bundles a microverso's cognitive data, referenced skills, dependency pins and
integration configs into a self-contained, importable package. "Works on my
Exocortex → works on yours."

Produces (dir or tar.gz):
    {slug}-v{version}.mvpkg/
      microverso.yaml   MANIFEST.sum   INSTALL.md   env.example
      acervo/   skills/   deps/   integrations/

Pipeline: auto-fill manifest -> validate (excrtx/v1) -> OKF gate -> clean copy
-> bundle skills/deps/integrations -> MANIFEST.sum. See
acervo/global/contracts/microverso-package-spec.md.

Usage:
    python3 microverso_package.py --microverso estudio-criativo --out /tmp/out --tar
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import microverso_schema as schema  # noqa: E402
from microverso_common import (  # noqa: E402
    EXCLUDE_DIRS, EXCLUDE_FILES, resolve_acervo, resolve_hermes_skills,
    find_repo_root, okf_gate, frontmatter_value, strip_runtime_fields,
    write_manifest_sum,
)

try:
    import yaml
except ImportError:
    yaml = None

BUILDER_VERSION = "microverso_package/1.0"
SKILL_REF_RE = re.compile(r"excrtx-[a-z0-9]+(?:-[a-z0-9]+)+")
NATURE_DESC = {
    "context": "Contexto estrutural do microverso",
    "knowledge": "Base de conhecimento, fatos e referências",
    "contracts": "Contratos operacionais e de governança",
    "workflows": "Workflows e procedimentos",
    "decisions": "Decisões locais do microverso",
    "reflections": "Reflexões e lições aprendidas",
    "persona": "Personas operacionais",
    "prompts": "Prompts testados",
    "templates": "Templates reutilizáveis",
    "tools": "Documentação de ferramentas",
    "skills": "Skills locais do microverso",
    "_meta": "Índice e schema local do microverso",
}


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def detect_skill_refs(micro_dir):
    """Scan microverso text for referenced excrtx-* skill names."""
    refs = set()
    for path in micro_dir.rglob("*"):
        if not path.is_file() or path.suffix not in (".md", ".yaml", ".yml", ".py", ".sh"):
            continue
        try:
            refs.update(SKILL_REF_RE.findall(path.read_text(encoding="utf-8", errors="ignore")))
        except OSError:
            continue
    return sorted(refs)


def find_skill_dir(name):
    """Locate a skill's source dir across runtime and repo candidate roots."""
    candidates = [resolve_hermes_skills() / name]
    repo = find_repo_root()
    if repo:
        candidates.append(repo / "skills" / name)
    for root in candidates:
        if (root / "SKILL.md").is_file():
            return root
    return None


def detect_python_modules(micro_dir):
    """Best-effort: top-level non-stdlib modules imported by the microverso's scripts."""
    mods = set()
    imp_re = re.compile(r"^\s*(?:from|import)\s+([a-zA-Z_][\w]*)")
    for path in micro_dir.rglob("*.py"):
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            m = imp_re.match(line)
            if m:
                mods.add(m.group(1))
    stdlib = {"os", "sys", "re", "json", "pathlib", "subprocess", "argparse",
              "datetime", "hashlib", "shutil", "typing", "collections", "math",
              "io", "time", "tempfile", "functools", "itertools", "dataclasses"}
    return sorted(m for m in mods if m not in stdlib)


def build_tree(micro_dir):
    tree = {}
    for child in sorted(micro_dir.iterdir()):
        if child.is_dir() and child.name not in EXCLUDE_DIRS and not child.name.startswith("raw"):
            tree[f"{child.name}/"] = NATURE_DESC.get(child.name, f"Diretório {child.name}")
    return tree


def detect_compat():
    platforms = ["linux"] if sys.platform.startswith("linux") else [sys.platform]
    hermes_version = None
    if shutil.which("hermes"):
        try:
            out = subprocess.run(["hermes", "--version"], capture_output=True,
                                 text=True, timeout=10)
            hermes_version = out.stdout.strip().split("\n")[0] or None
        except (OSError, subprocess.SubprocessError):
            pass
    exocortex_version = os.environ.get("EXOCORTEX_VERSION")
    repo = find_repo_root()
    if not exocortex_version and repo and (repo / "VERSION").is_file():
        exocortex_version = (repo / "VERSION").read_text(encoding="utf-8").strip()
    return {
        "exocortex_version": exocortex_version or ">=0",
        "hermes_version": hermes_version or ">=0",
        "platforms": platforms,
    }


def build_manifest(slug, micro_dir, version, existing, skill_refs):
    """Assemble the enriched excrtx/v1 manifest, preserving curated fields."""
    existing = existing or {}
    meta = dict(existing.get("metadata") or {})
    meta["name"] = slug
    meta["version"] = version
    meta.setdefault("description", f"Microverso {slug}")
    meta.setdefault("author", "exocortex")
    meta.setdefault("tags", [])

    req = dict(existing.get("requires") or {})
    # reconcile skills: keep curated entries, add detected refs not yet listed
    curated = req.get("skills") or []
    curated_names = {schema._skill_name(s) for s in curated}
    skills = list(curated)
    for ref in skill_refs:
        if ref not in curated_names:
            skills.append(ref)
    req["skills"] = skills
    req.setdefault("python_packages", req.get("python_packages", []) or [])
    req.setdefault("node_packages", req.get("node_packages", []) or [])
    req.setdefault("mcps", req.get("mcps", []) or [])
    req.setdefault("env", req.get("env", []) or [])
    # system requirements
    system = set(req.get("system") or ["git", "python3", "rsync"])
    if req["python_packages"]:
        system.add("uv")
    if req["node_packages"]:
        system.add("node")
    req["system"] = sorted(system)

    return {
        "apiVersion": schema.API_VERSION,
        "kind": schema.KIND,
        "metadata": meta,
        "requires": req,
        "compat": detect_compat(),
        "tree": build_tree(micro_dir),
        "hooks": existing.get("hooks") or {},
        "provenance": {
            "built_at": now_iso(),
            "builder_version": BUILDER_VERSION,
            "content_digest": None,  # filled after payload copy
        },
    }


def clean_copy(micro_dir, dst_acervo, include_raw, include_deprecated):
    """Copy the microverso tree into the package, applying clean-portable rules."""
    stats = {"files": 0, "stripped": 0, "dropped_deprecated": 0, "skipped_dirs": 0}
    for path in sorted(micro_dir.rglob("*")):
        rel = path.relative_to(micro_dir)
        parts = set(rel.parts)
        if parts & EXCLUDE_DIRS:
            continue
        if not include_raw and (rel.parts and rel.parts[0].startswith("raw")):
            continue
        if path.is_dir():
            continue
        if path.name in EXCLUDE_FILES:
            continue
        if rel.as_posix() == "microverso.yaml":
            continue  # manifest lives at package root, regenerated
        target = dst_acervo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".md":
            text = path.read_text(encoding="utf-8")
            if not include_deprecated and frontmatter_value(text, "deprecated") == "true":
                stats["dropped_deprecated"] += 1
                continue
            new_text = strip_runtime_fields(text)
            if new_text != text:
                stats["stripped"] += 1
            target.write_text(new_text, encoding="utf-8")
        else:
            shutil.copy2(path, target)
        stats["files"] += 1
    return stats


def bundle_skills(skill_refs, mode, pkg_skills_dir):
    """Bundle referenced excrtx-* skill dirs. Returns (bundled, missing)."""
    bundled, missing = [], []
    if mode == "none":
        return bundled, skill_refs
    for name in skill_refs:
        src = find_skill_dir(name)
        if src is None:
            missing.append(name)
            continue
        dst = pkg_skills_dir / name
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", ".git"))
        bundled.append(name)
    return bundled, missing


def write_aux_files(pkg_dir, manifest, bundled_skills):
    req = manifest["requires"]
    # deps/requirements.txt
    deps_dir = pkg_dir / "deps"
    deps_dir.mkdir(exist_ok=True)
    py = req.get("python_packages") or []
    (deps_dir / "requirements.txt").write_text(
        ("\n".join(py) + "\n") if py else "# no python packages required\n",
        encoding="utf-8")
    node = req.get("node_packages") or []
    if node:
        (deps_dir / "node-packages.txt").write_text("\n".join(node) + "\n", encoding="utf-8")
    # integrations/mcps.yaml
    integ = pkg_dir / "integrations"
    integ.mkdir(exist_ok=True)
    mcps = req.get("mcps") or []
    if yaml:
        (integ / "mcps.yaml").write_text(
            yaml.safe_dump({"mcps": mcps}, sort_keys=False, allow_unicode=True),
            encoding="utf-8")
    else:
        (integ / "mcps.yaml").write_text("mcps: []\n", encoding="utf-8")
    # env.example
    env = req.get("env") or []
    lines = ["# Required environment variables / secrets for this microverso.",
             "# Fill values on the target instance — NEVER commit real secrets.", ""]
    lines += [f"{name}=" for name in env]
    (pkg_dir / "env.example").write_text("\n".join(lines) + "\n", encoding="utf-8")
    # INSTALL.md
    meta = manifest["metadata"]
    md = [f"# {meta['name']} v{meta['version']}", "", meta.get("description", ""), "",
          "## O que será instalado", "",
          f"- Skills embutidas: {', '.join(bundled_skills) or 'nenhuma'}",
          f"- Pacotes Python: {', '.join(py) or 'nenhum'}",
          f"- MCPs/integrações: {', '.join(mcps) or 'nenhum'}",
          f"- Env vars exigidas: {', '.join(env) or 'nenhuma'}",
          f"- Software de sistema: {', '.join(req.get('system') or [])}", "",
          "## Instalar", "",
          "```bash", f"python3 microverso_install.py {meta['name']}-v{meta['version']}.mvpkg.tar.gz",
          "```", ""]
    (pkg_dir / "INSTALL.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def write_manifest_yaml(path, manifest):
    if yaml is None:
        raise SystemExit("PyYAML required to write microverso.yaml")
    path.write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True, default_flow_style=False),
        encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Export a microverso as a portable .mvpkg")
    parser.add_argument("--microverso", required=True, help="microverso slug")
    parser.add_argument("--acervo", help="acervo root override")
    parser.add_argument("--out", default=".", help="output directory (default: cwd)")
    parser.add_argument("--tar", action="store_true", help="emit a .mvpkg.tar.gz instead of a dir")
    parser.add_argument("--version", help="override package version (semver)")
    parser.add_argument("--include-raw", action="store_true", help="include raw/ immutable sources")
    parser.add_argument("--include-deprecated", action="store_true",
                        help="include files with deprecated: true")
    parser.add_argument("--bundle-skills", choices=["auto", "all", "none"], default="auto",
                        help="bundle referenced excrtx-* skills (default: auto)")
    args = parser.parse_args(argv)

    acervo = resolve_acervo(args.acervo)
    micro_dir = acervo / "micro" / args.microverso
    if not micro_dir.is_dir():
        print(f"ERROR: microverso not found: {micro_dir}", file=sys.stderr)
        return 1

    # 1. Load existing manifest (curated base), determine version
    existing = None
    existing_path = micro_dir / "microverso.yaml"
    if existing_path.is_file():
        existing, err = schema.load_manifest(existing_path)
        if err:
            print(f"WARN: existing microverso.yaml unreadable ({err}); regenerating", file=sys.stderr)
            existing = None
    version = args.version or (existing or {}).get("metadata", {}).get("version") or "0.1.0"

    # 2. Detect refs and build manifest
    skill_refs = detect_skill_refs(micro_dir)
    detected_mods = detect_python_modules(micro_dir)
    manifest = build_manifest(args.microverso, micro_dir, version, existing, skill_refs)

    # 3. Validate manifest
    issues = schema.validate_manifest(manifest)
    for sev, code, msg in issues:
        print(f"  [{sev}] {code}: {msg}")
    if schema.has_errors(issues):
        print("ERROR: generated manifest failed excrtx/v1 validation", file=sys.stderr)
        return 1

    # 4. OKF gate on source content
    status, output = okf_gate(micro_dir)
    print(f"OKF gate: {status}")
    if output:
        print(f"  {output}")
    if status == "fail":
        print("ERROR: source microverso has OKF frontmatter errors — fix before export.",
              file=sys.stderr)
        return 1

    # 5. Assemble package
    pkg_name = f"{args.microverso}-v{version}.mvpkg"
    out_dir = Path(args.out).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    pkg_dir = out_dir / pkg_name
    if pkg_dir.exists():
        shutil.rmtree(pkg_dir)
    pkg_dir.mkdir(parents=True)

    copy_stats = clean_copy(micro_dir, pkg_dir / "acervo", args.include_raw, args.include_deprecated)

    return _finish(args, manifest, micro_dir, pkg_dir, skill_refs, detected_mods,
                   copy_stats, version, out_dir, pkg_name)


def _finish(args, manifest, micro_dir, pkg_dir, skill_refs, detected_mods,
            copy_stats, version, out_dir, pkg_name):
    # bundle skills
    pkg_skills = pkg_dir / "skills"
    pkg_skills.mkdir(exist_ok=True)
    bundled, missing = bundle_skills(skill_refs, args.bundle_skills, pkg_skills)
    if not any(pkg_skills.iterdir()):
        pkg_skills.rmdir()

    # aux files (deps, integrations, env.example, INSTALL.md)
    write_aux_files(pkg_dir, manifest, bundled)

    # content digest over payload (acervo + skills), then write manifest, then MANIFEST.sum
    manifest["provenance"]["content_digest"] = _payload_digest(pkg_dir)
    write_manifest_yaml(pkg_dir / "microverso.yaml", manifest)
    pkg_digest = write_manifest_sum(pkg_dir)

    # optional tar
    final_path = pkg_dir
    if args.tar:
        tar_path = out_dir / f"{pkg_name}.tar.gz"
        if tar_path.exists():
            tar_path.unlink()
        base = str(out_dir / pkg_name)
        shutil.make_archive(base, "gztar", root_dir=out_dir, base_dir=pkg_name)
        final_path = tar_path

    # report (EX-49)
    print("\n=== export report ===")
    print(f"package: {final_path}")
    print(f"version: {version}")
    print(f"files copied: {copy_stats['files']} "
          f"(last_accessed_at stripped from {copy_stats['stripped']}, "
          f"deprecated dropped: {copy_stats['dropped_deprecated']})")
    print(f"skills bundled: {', '.join(bundled) or 'none'}")
    if missing:
        print(f"WARN skills referenced but not found (declared only): {', '.join(missing)}")
    if detected_mods:
        print(f"NOTE python modules detected in scripts (review pins): {', '.join(detected_mods)}")
    print(f"content_digest: {manifest['provenance']['content_digest'][:16]}…")
    print(f"package_digest: {pkg_digest[:16]}…")
    return 0


def _payload_digest(pkg_dir):
    import hashlib
    h = hashlib.sha256()
    for sub in ("acervo", "skills"):
        d = pkg_dir / sub
        if not d.is_dir():
            continue
        for path in sorted(d.rglob("*")):
            if path.is_file():
                h.update(path.relative_to(pkg_dir).as_posix().encode())
                h.update(path.read_bytes())
    return h.hexdigest()


if __name__ == "__main__":
    sys.exit(main())
