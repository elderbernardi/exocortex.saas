#!/usr/bin/env python3
"""Runtime guardrails for Exocórtex production skills and Acervo write scope.

This module gives the repository an executable contract for two runtime checks:
1. Production skills can declare frontmatter gate rules and refuse execution when
   the required quality gate is not active.
2. Acervo writes can be denied when the destination escapes the active microverso.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
ACERVO_ROOT = REPO_ROOT / "acervo"
QUALITY_GATE_SKILL = "excrtx-quality-gate"


def _clean_frontmatter_text(raw: str) -> str:
    return re.sub(r"^\d+\|", "", raw, flags=re.MULTILINE)


def load_skill_frontmatter(skill_name: str, skills_dir: Path = SKILLS_DIR) -> dict[str, Any]:
    skill_path = skills_dir / skill_name / "SKILL.md"
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill não encontrada: {skill_path}")

    clean = _clean_frontmatter_text(skill_path.read_text(encoding="utf-8"))
    if not clean.lstrip().startswith("---"):
        return {}

    match = re.search(r"\n---\s*\n", clean[3:])
    if not match:
        return {}

    frontmatter = clean[3:match.start() + 3]
    return yaml.safe_load(frontmatter) or {}


def enforce_skill_gate(
    skill_name: str,
    loaded_skills: list[str] | None = None,
    estimated_context_tokens: int | None = None,
    skills_dir: Path = SKILLS_DIR,
) -> dict[str, Any]:
    """Validate runtime gate requirements declared in a skill frontmatter."""
    frontmatter = load_skill_frontmatter(skill_name, skills_dir=skills_dir)
    gate = frontmatter.get("gate") or {}
    loaded_skills = loaded_skills or []

    result: dict[str, Any] = {
        "allowed": True,
        "skill": skill_name,
        "gate": gate,
        "reason": "no_gate",
    }

    if not gate:
        return result

    if gate.get("require_quality_gate") and QUALITY_GATE_SKILL not in loaded_skills:
        return {
            "allowed": False,
            "skill": skill_name,
            "gate": gate,
            "reason": "quality_gate_required",
            "message": (
                f"{skill_name} exige {QUALITY_GATE_SKILL} ativo em runtime. "
                "Carregue a skill de quality gate antes de executar."
            ),
        }

    max_context_tokens = gate.get("max_context_tokens")
    if max_context_tokens is not None and estimated_context_tokens is not None:
        if estimated_context_tokens > max_context_tokens:
            return {
                "allowed": False,
                "skill": skill_name,
                "gate": gate,
                "reason": "context_budget_exceeded",
                "message": (
                    f"{skill_name} declarou teto de {max_context_tokens} tokens, "
                    f"mas recebeu estimativa de {estimated_context_tokens}."
                ),
            }

    result["reason"] = "passed"
    result["message"] = "Gate satisfeito."
    return result


def resolve_active_microverso(
    active_microverso: str | None = None,
    cwd: str | Path | None = None,
    acervo_root: str | Path = ACERVO_ROOT,
) -> str:
    """Resolve the active microverso from explicit arg, env, or current path."""
    if active_microverso:
        return active_microverso

    env_value = os.environ.get("EXOCTX_ACTIVE_MICROVERSO") or os.environ.get("ACTIVE_MICROVERSO")
    if env_value:
        return env_value

    acervo_root = Path(acervo_root).expanduser().resolve()
    current = Path(cwd or Path.cwd()).expanduser().resolve()

    try:
        rel = current.relative_to(acervo_root / "micro")
    except ValueError as exc:
        raise RuntimeError(
            "Microverso ativo não resolvido. Informe --active-microverso ou EXOCTX_ACTIVE_MICROVERSO."
        ) from exc

    parts = rel.parts
    if not parts:
        raise RuntimeError(
            "Diretório atual não aponta para um microverso específico. Informe --active-microverso explicitamente."
        )
    return parts[0]


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def guard_write_path(
    target_path: str | Path,
    active_microverso: str | None = None,
    acervo_root: str | Path = ACERVO_ROOT,
    cwd: str | Path | None = None,
) -> dict[str, Any]:
    """Allow writes only inside acervo/micro/{active_microverso}/."""
    acervo_root = Path(acervo_root).expanduser().resolve()
    target = Path(target_path).expanduser()
    if not target.is_absolute():
        target = (Path(cwd or Path.cwd()) / target).resolve()
    else:
        target = target.resolve()

    slug = resolve_active_microverso(active_microverso=active_microverso, cwd=cwd, acervo_root=acervo_root)
    allowed_root = (acervo_root / "micro" / slug).resolve()

    if _is_relative_to(target, allowed_root):
        return {
            "allowed": True,
            "reason": "within_active_microverso",
            "active_microverso": slug,
            "allowed_root": str(allowed_root),
            "target": str(target),
            "message": f"allow: {target} está dentro de {allowed_root}",
        }

    return {
        "allowed": False,
        "reason": "cross_microverso_write_blocked",
        "active_microverso": slug,
        "allowed_root": str(allowed_root),
        "target": str(target),
        "message": (
            f"deny: write fora do microverso ativo '{slug}'. "
            f"Destino: {target} | permitido: {allowed_root}"
        ),
    }


def _parse_loaded_skills(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Exocórtex runtime guard")
    sub = parser.add_subparsers(dest="command", required=True)

    skill_cmd = sub.add_parser("check-skill", help="Validate production skill runtime gate")
    skill_cmd.add_argument("--skill", required=True)
    skill_cmd.add_argument("--loaded-skills", default="")
    skill_cmd.add_argument("--estimated-context-tokens", type=int)

    write_cmd = sub.add_parser("guard-write", help="Block cross-microverso writes")
    write_cmd.add_argument("--path", required=True)
    write_cmd.add_argument("--active-microverso")
    write_cmd.add_argument("--acervo-root", default=str(ACERVO_ROOT))

    args = parser.parse_args()

    if args.command == "check-skill":
        result = enforce_skill_gate(
            skill_name=args.skill,
            loaded_skills=_parse_loaded_skills(args.loaded_skills),
            estimated_context_tokens=args.estimated_context_tokens,
        )
    else:
        result = guard_write_path(
            target_path=args.path,
            active_microverso=args.active_microverso,
            acervo_root=args.acervo_root,
        )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["allowed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
