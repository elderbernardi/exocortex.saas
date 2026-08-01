#!/usr/bin/env python3
"""Verify Exocórtex runtime capabilities without installing dependencies."""

from __future__ import annotations

import argparse
import json
import os
import platform as platform_module
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = REPO_ROOT / "setup" / "capabilities.json"
SUPPORTED_LAYERS = {"runtime", "system", "service", "user-tool"}
SUPPORTED_PROFILES = {"core", "full"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verifica capacidades exigidas pelo instalador Exocórtex")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--profile", choices=("core", "full"), default="full")
    parser.add_argument("--allow-degraded-services", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def _read_os_release(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return values
    for line in lines:
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key] = value.strip().strip('"').strip("'")
    return values


def detect_platform(manifest: dict[str, Any]) -> dict[str, str]:
    if platform_module.system().lower() == "darwin":
        platform_id = "darwin"
        like: list[str] = []
    else:
        path = Path(os.environ.get("EXOCORTEX_OS_RELEASE", "/etc/os-release"))
        release = _read_os_release(path)
        platform_id = release.get("ID", "unknown").lower()
        like = release.get("ID_LIKE", "").lower().split()

    platforms = manifest.get("platforms", {})
    selected = platform_id if platform_id in platforms else next((item for item in like if item in platforms), "unknown")
    platform_config = platforms.get(selected, {})
    return {
        "id": platform_id,
        "family": selected,
        "package_manager": platform_config.get("package_manager", "unknown"),
        "install_template": platform_config.get("install_template", "Instale {package} manualmente"),
    }


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema") != "exocortex-capabilities/v1":
        errors.append("schema deve ser exocortex-capabilities/v1")
    if not isinstance(manifest.get("platforms"), dict):
        errors.append("platforms deve ser um objeto")
    capabilities = manifest.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        errors.append("capabilities deve ser uma lista não vazia")
        return errors
    ids: set[str] = set()
    for index, capability in enumerate(capabilities):
        prefix = f"capabilities[{index}]"
        capability_id = capability.get("id")
        if not isinstance(capability_id, str) or not capability_id:
            errors.append(f"{prefix}.id é obrigatório")
        elif capability_id in ids:
            errors.append(f"id duplicado: {capability_id}")
        else:
            ids.add(capability_id)
        profiles = capability.get("profiles")
        if not isinstance(profiles, list) or not profiles or not set(profiles) <= SUPPORTED_PROFILES:
            errors.append(f"{prefix}.profiles é inválido")
        if capability.get("layer") not in SUPPORTED_LAYERS:
            errors.append(f"{prefix}.layer é inválido")
        commands = capability.get("commands")
        if not isinstance(commands, list) or not commands or not all(isinstance(item, str) and item for item in commands):
            errors.append(f"{prefix}.commands é inválido")
    return errors


def remediation_for(capability: dict[str, Any], platform: dict[str, str]) -> str:
    if capability.get("remediation"):
        return str(capability["remediation"])
    manager = platform["package_manager"]
    package = capability.get("packages", {}).get(manager)
    if package:
        return platform["install_template"].format(package=package)
    return "Instale a capacidade manualmente e execute novamente o preflight."


def _version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split("."))


def _check_versions(capability: dict[str, Any]) -> tuple[bool, list[str]]:
    evidence: list[str] = []
    for check in capability.get("versions", []):
        command = check["command"]
        minimum = check["minimum"]
        try:
            completed = subprocess.run(
                [command, *check.get("args", ["--version"])],
                text=True,
                capture_output=True,
                timeout=15,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            evidence.append(f"{command}: versão indisponível")
            return False, evidence
        match = re.search(r"\d+(?:\.\d+){1,3}", (completed.stdout or completed.stderr))
        if completed.returncode != 0 or not match:
            evidence.append(f"{command}: versão não detectada")
            return False, evidence
        current = match.group(0)
        width = max(len(_version_tuple(current)), len(_version_tuple(minimum)))
        current_parts = _version_tuple(current) + (0,) * (width - len(_version_tuple(current)))
        minimum_parts = _version_tuple(minimum) + (0,) * (width - len(_version_tuple(minimum)))
        if current_parts < minimum_parts:
            evidence.append(f"{command}: {current} < {minimum}")
            return False, evidence
        evidence.append(f"{command}: {current} >= {minimum}")
    return True, evidence


def _package_owner(path: str, manager: str) -> str:
    probes = {
        "pacman": (["pacman", "-Qo", path], r" owned by (.+)$"),
        "apt": (["dpkg-query", "-S", path], r"^([^:]+):"),
        "dnf": (["rpm", "-qf", path], r"^(.+)$"),
    }
    if manager == "brew" and "/Cellar/" in path:
        parts = Path(path).parts
        try:
            return f"os-package:{parts[parts.index('Cellar') + 1]}"
        except (ValueError, IndexError):
            return "external-or-user"
    probe = probes.get(manager)
    if not probe or shutil.which(probe[0][0]) is None:
        return "external-or-user"
    try:
        completed = subprocess.run(probe[0], text=True, capture_output=True, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return "external-or-user"
    if completed.returncode != 0:
        return "external-or-user"
    match = re.search(probe[1], completed.stdout.strip())
    return f"os-package:{match.group(1)}" if match else "external-or-user"


def evaluate(manifest: dict[str, Any], profile: str, allow_degraded_services: bool = False) -> dict[str, Any]:
    platform = detect_platform(manifest)
    results: list[dict[str, Any]] = []
    for capability in manifest.get("capabilities", []):
        if profile not in capability.get("profiles", []):
            continue
        commands = capability.get("commands", [])
        paths = {command: shutil.which(command) for command in commands}
        provenance: dict[str, str] = {}
        for command, path in paths.items():
            if path is None:
                provenance[command] = "missing"
            elif capability.get("layer") == "system":
                provenance[command] = _package_owner(path, platform["package_manager"])
            else:
                provenance[command] = capability.get("layer", "runtime")
        missing = [command for command, path in paths.items() if path is None]
        passed = not missing
        evidence = ", ".join(f"{command}={path or 'ausente'}" for command, path in paths.items())

        if passed:
            versions_ok, version_evidence = _check_versions(capability)
            passed = versions_ok
            if version_evidence:
                evidence += "; " + "; ".join(version_evidence)

        probe = capability.get("probe")
        if passed and probe:
            try:
                completed = subprocess.run(probe, text=True, capture_output=True, timeout=30, check=False)
                passed = completed.returncode == 0
                evidence += f"; probe exit={completed.returncode}"
            except (OSError, subprocess.TimeoutExpired):
                passed = False
                evidence += "; probe indisponível"

        degraded = bool(capability.get("degradable")) and allow_degraded_services
        status = "pass" if passed else ("warn" if degraded else "fail")
        results.append(
            {
                "id": capability["id"],
                "description": capability.get("description", ""),
                "layer": capability.get("layer", "system"),
                "status": status,
                "evidence": evidence,
                "provenance": provenance,
                "remediation": "" if passed else remediation_for(capability, platform),
            }
        )

    return {
        "schema": "exocortex-capability-report/v1",
        "profile": profile,
        "platform": platform,
        "summary": {
            "passed": sum(item["status"] == "pass" for item in results),
            "warnings": sum(item["status"] == "warn" for item in results),
            "failed": sum(item["status"] == "fail" for item in results),
        },
        "capabilities": results,
    }


def main() -> int:
    args = parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Manifesto de capacidades inválido: {exc}", file=sys.stderr)
        return 2

    manifest_errors = validate_manifest(manifest)
    if manifest_errors:
        print("Manifesto de capacidades inválido: " + "; ".join(manifest_errors), file=sys.stderr)
        return 2

    report = evaluate(manifest, args.profile, args.allow_degraded_services)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        platform = report["platform"]
        print(f"Capacidades — profile={args.profile} SO={platform['id']} gerenciador={platform['package_manager']}")
        for item in report["capabilities"]:
            symbol = "✓" if item["status"] == "pass" else "⚠" if item["status"] == "warn" else "✗"
            print(f"  {symbol} {item['id']}: {item['status']} — {item['evidence']}")
            if item["remediation"]:
                print(f"    correção: {item['remediation']}")
    return 1 if report["summary"]["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
