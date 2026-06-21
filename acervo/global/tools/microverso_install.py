#!/usr/bin/env python3
"""microverso_install.py — import a microverso from a portable .mvpkg.

Executable counterpart of the excrtx-memory-mvinstall skill. Installs a
Docker-like microverso package (dir, .tar.gz, or git URL) into the acervo:
integrity check -> manifest (excrtx/v1) -> OKF gate -> compat preflight ->
dependency resolution (skills with collision handling) -> safe merge -> hooks
-> global manifest registration.

Usage:
    python3 microverso_install.py <pkg-dir | .tar.gz | git-url> [--acervo PATH]
                                   [--install-deps] [--update-skills] [--dry-run]
"""

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import microverso_schema as schema  # noqa: E402
from microverso_common import (  # noqa: E402
    resolve_acervo, resolve_hermes_skills, okf_gate, frontmatter_value,
    verify_manifest_sum, safe_merge,
)

try:
    import yaml
except ImportError:
    yaml = None

SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)")


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_git_url(s):
    return s.startswith(("http://", "https://", "git@")) or s.endswith(".git")


def stage_package(source, tmp):
    """Resolve <source> to an on-disk package root (dir containing microverso.yaml)."""
    tmp = Path(tmp)
    if is_git_url(source):
        clone = tmp / "clone"
        subprocess.run(["git", "clone", "--depth", "1", source, str(clone)], check=True)
        root = clone
    elif source.endswith((".tar.gz", ".tgz")):
        with tarfile.open(source, "r:gz") as tf:
            try:
                tf.extractall(tmp / "extract", filter="data")
            except TypeError:  # Python < 3.12 has no filter kwarg
                tf.extractall(tmp / "extract")
        root = tmp / "extract"
    else:
        root = Path(source)
    if (root / "microverso.yaml").is_file():
        return root
    for child in sorted(Path(root).rglob("microverso.yaml")):
        return child.parent
    raise SystemExit(f"ERROR: no microverso.yaml found in {source}")


def semver_tuple(v):
    m = SEMVER.match(str(v or ""))
    return tuple(int(g) for g in m.groups()) if m else None


def dir_digest(path):
    h = hashlib.sha256()
    for p in sorted(Path(path).rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            h.update(p.relative_to(path).as_posix().encode())
            h.update(p.read_bytes())
    return h.hexdigest()


def skill_version(skill_dir):
    skill_md = Path(skill_dir) / "SKILL.md"
    if not skill_md.is_file():
        return None
    return frontmatter_value(skill_md.read_text(encoding="utf-8"), "version")


def resolve_skill(name, src, dst_root, update_skills, dry_run):
    """Collision resolution for a bundled skill. Returns (action, final_name, note)."""
    dst = dst_root / name
    if not dst.exists():
        if not dry_run:
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", ".git"))
        return "install", name, "new"
    if dir_digest(src) == dir_digest(dst):
        return "skip", name, "identical"
    sv, dv = semver_tuple(skill_version(src)), semver_tuple(skill_version(dst))
    if sv and dv and sv > dv:
        if update_skills:
            if not dry_run:
                shutil.rmtree(dst)
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", ".git"))
            return "update", name, f"{dv}->{sv}"
        return "update-pending", name, f"{dv}->{sv} (use --update-skills to apply)"
    # divergent / not-newer → rename incoming, keep existing intact (caller builds new name)
    return "rename", name, "divergent content"


def install(args):
    acervo = resolve_acervo(args.acervo)
    if not acervo.is_dir() and not args.dry_run:
        acervo.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        pkg = stage_package(args.package, tmp)

        # 1. Integrity
        ok, problems = verify_manifest_sum(pkg)
        print(f"integrity: {'OK' if ok else 'FAILED'}")
        if not ok:
            for p in problems[:10]:
                print(f"  {p}")
            print("ERROR: package integrity check failed (MANIFEST.sum mismatch)", file=sys.stderr)
            return 1

        # 2. Manifest
        manifest, err = schema.load_manifest(pkg / "microverso.yaml")
        if err:
            print(f"ERROR: {err}", file=sys.stderr)
            return 1
        issues = schema.validate_manifest(manifest)
        for sev, code, msg in issues:
            print(f"  [{sev}] {code}: {msg}")
        if schema.has_errors(issues):
            print("ERROR: manifest is not valid excrtx/v1", file=sys.stderr)
            return 1
        name = manifest["metadata"]["name"]
        version = manifest["metadata"]["version"]
        print(f"manifest: {name} v{version} (excrtx/v1)")

        # 3. OKF gate on packaged content
        status, output = okf_gate(pkg / "acervo")
        print(f"OKF gate: {status}")
        if status == "fail":
            print(output)
            print("ERROR: package content has OKF errors — refusing to install.", file=sys.stderr)
            return 1

        # 4. Compat preflight
        requires_met = preflight(manifest)

        # 5. Dependency report + env
        deps_report(pkg, manifest, args.install_deps, args.dry_run)
        mcp_report(manifest)
        env_report(manifest)

        if args.dry_run:
            print("\n[dry-run] would merge acervo, resolve skills, run hooks, register manifest.")
            plan_skills(pkg, args)
            return 0

        # 6. Safe merge of cognitive tree
        dst_micro = acervo / "micro" / name
        method = safe_merge(pkg / "acervo", dst_micro)
        print(f"merged acervo -> {dst_micro} ({method})")
        # persist authoritative manifest into the installed microverso
        shutil.copy2(pkg / "microverso.yaml", dst_micro / "microverso.yaml")

        # 7. Skills (collision resolution) + reference rewrite
        skill_actions = install_skills(pkg, name, dst_micro, args)

        # 8. Hooks
        run_hooks(manifest, dst_micro)

        # 9. Register in global manifest
        register(acervo, name, version, requires_met, manifest)

        # 10. Post-install verify (EX-49)
        v_status, _ = okf_gate(dst_micro)
        print(f"\npost-install OKF verify: {v_status}")

    # report
    print("\n=== install report ===")
    print(f"installed: {name} v{version} -> {dst_micro}")
    print(f"requires_met: {requires_met}")
    for action, final, note in skill_actions:
        print(f"  skill {final}: {action} ({note})")
    return 0


def preflight(manifest):
    compat = manifest.get("compat") or {}
    requires_met = True
    platforms = compat.get("platforms") or []
    cur = "linux" if sys.platform.startswith("linux") else sys.platform
    if platforms and cur not in platforms:
        print(f"WARN compat: package platforms {platforms}, current {cur}")
        requires_met = False
    system = (manifest.get("requires") or {}).get("system") or []
    missing = [b for b in system if not shutil.which(b)]
    if missing:
        print(f"WARN system binaries missing: {', '.join(missing)} "
              f"(install them; rsync has a Python fallback)")
        requires_met = False
    else:
        print(f"system requirements: {', '.join(system) or 'none'} — all present")
    return requires_met


def deps_report(pkg, manifest, install_deps, dry_run):
    req = manifest.get("requires") or {}
    py = req.get("python_packages") or []
    if not py:
        return
    print(f"python packages required: {', '.join(py)}")
    if install_deps and not dry_run:
        reqs = pkg / "deps" / "requirements.txt"
        if shutil.which("uv"):
            subprocess.run(["uv", "pip", "install", "-r", str(reqs)])
        elif shutil.which("pip"):
            subprocess.run(["pip", "install", "-r", str(reqs)])
        else:
            print("WARN: neither uv nor pip available; skipping dependency install")
    else:
        print("  (report-only; pass --install-deps to install)")


def mcp_report(manifest):
    mcps = (manifest.get("requires") or {}).get("mcps") or []
    if mcps:
        print(f"MCPs to register (Draft-First — register manually): {', '.join(map(str, mcps))}")


def env_report(manifest):
    env = (manifest.get("requires") or {}).get("env") or []
    missing = [e for e in env if not os.environ.get(e)]
    if env:
        print(f"env vars required: {', '.join(env)}")
        if missing:
            print(f"  WARN missing in this environment: {', '.join(missing)}")


def _bundled_skill_dirs(pkg):
    sk = pkg / "skills"
    if not sk.is_dir():
        return []
    return [d for d in sorted(sk.iterdir()) if d.is_dir()]


def plan_skills(pkg, args):
    dst_root = resolve_hermes_skills()
    for src in _bundled_skill_dirs(pkg):
        action, _final, note = resolve_skill(src.name, src, dst_root, args.update_skills, True)
        print(f"  [dry-run] skill {src.name}: {action} ({note})")


def install_skills(pkg, micro_name, dst_micro, args):
    dst_root = resolve_hermes_skills()
    dst_root.mkdir(parents=True, exist_ok=True)
    actions = []
    for src in _bundled_skill_dirs(pkg):
        action, final, note = resolve_skill(src.name, src, dst_root, args.update_skills, False)
        if action == "rename":
            new_name = f"{src.name}-{micro_name}"
            shutil.copytree(src, dst_root / new_name,
                            ignore=shutil.ignore_patterns("__pycache__", ".git"))
            rewrite_refs(dst_micro, src.name, new_name)
            final, note = new_name, f"renamed from {src.name} (existing kept)"
        actions.append((action, final, note))
    return actions


def rewrite_refs(root, old, new):
    for p in Path(root).rglob("*"):
        if p.is_file() and p.suffix in (".md", ".yaml", ".yml"):
            text = p.read_text(encoding="utf-8")
            if old in text:
                p.write_text(text.replace(old, new), encoding="utf-8")


def run_hooks(manifest, micro_dir):
    hooks = manifest.get("hooks") or {}
    for hook in ("post_install", "validate"):
        rel = hooks.get(hook)
        if not rel:
            continue
        if rel.startswith("/") or ".." in rel.split("/"):
            print(f"WARN unsafe hook path skipped: {hook}={rel}")
            continue
        script = micro_dir / rel
        if not script.is_file():
            print(f"WARN hook {hook} not found: {script}")
            continue
        os.chmod(script, 0o755)
        try:
            proc = subprocess.run(["bash", str(script)], cwd=str(micro_dir),
                                  capture_output=True, text=True, timeout=60)
            print(f"hook {hook}: exit {proc.returncode}")
            if proc.stdout.strip():
                print(proc.stdout.strip())
        except subprocess.TimeoutExpired:
            print(f"WARN hook {hook} timed out (60s)")


def register(acervo, name, version, requires_met, manifest):
    meta_dir = acervo / "global" / "_meta"
    meta_dir.mkdir(parents=True, exist_ok=True)
    reg_path = meta_dir / "microversos.yaml"
    data = {"installed": []}
    if reg_path.is_file() and yaml:
        loaded = yaml.safe_load(reg_path.read_text(encoding="utf-8")) or {}
        if isinstance(loaded.get("installed"), list):
            data = loaded
    entry = {
        "name": name,
        "version": version,
        "installed_at": now_iso(),
        "path": f"micro/{name}",
        "status": "active",
        "requires_met": requires_met,
        "content_digest": (manifest.get("provenance") or {}).get("content_digest"),
    }
    data["installed"].append(entry)
    if yaml:
        reg_path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
                            encoding="utf-8")
        print(f"registered in {reg_path}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Import a microverso from a .mvpkg")
    parser.add_argument("package", help="package dir, .tar.gz, or git URL")
    parser.add_argument("--acervo", help="acervo root override")
    parser.add_argument("--install-deps", action="store_true",
                        help="install python/node packages (default: report-only)")
    parser.add_argument("--update-skills", action="store_true",
                        help="apply skill upgrades when a newer version is bundled")
    parser.add_argument("--dry-run", action="store_true",
                        help="validate and plan without modifying the acervo")
    args = parser.parse_args(argv)
    return install(args)


if __name__ == "__main__":
    sys.exit(main())
