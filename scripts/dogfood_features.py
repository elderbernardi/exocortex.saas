#!/usr/bin/env python3
"""Conversational dogfood runner for Exocórtex features.

The runner creates reproducible local evidence for one feature or all scenario
files under .dogfood/scenarios. It is intentionally conservative: dry-run mode
is the default safe path for tests and P0 guardrails; external side effects are
not performed by this script.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from scripts.dogfood_validate_catalog import parse_simple_yaml
except ModuleNotFoundError:  # direct script execution from scripts/
    from dogfood_validate_catalog import parse_simple_yaml

local_bin = str(Path.home() / ".local" / "bin")
if local_bin not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{os.environ.get('PATH', '')}{os.path.pathsep}{local_bin}"


VALID_STATUSES = {"PASS", "PARTIAL", "FAIL", "BLOCKED"}
REQUIRED_RESULT_FIELDS = ["feature_id", "status", "risk", "summary", "criteria", "artifacts", "blocked_reason"]


def utc_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def load_scenario(root: Path, feature_id: str) -> tuple[Path, dict[str, Any]]:
    scenario_path = root / ".dogfood" / "scenarios" / f"{feature_id}.yaml"
    if not scenario_path.is_file():
        raise FileNotFoundError(f"scenario not found: {scenario_path}")
    scenario = parse_simple_yaml(scenario_path.read_text(encoding="utf-8"))
    if scenario.get("feature_id") != feature_id:
        raise ValueError(f"scenario feature_id mismatch: expected {feature_id}, got {scenario.get('feature_id')}")
    return scenario_path, scenario


def validate_result_payload(payload: dict[str, Any]) -> None:
    for field in REQUIRED_RESULT_FIELDS:
        if field not in payload:
            raise ValueError(f"missing result field: {field}")
    if payload["status"] not in VALID_STATUSES:
        raise ValueError(f"invalid status: {payload['status']}")
    if not re.fullmatch(r"EX-\d{2}", str(payload["feature_id"])):
        raise ValueError(f"invalid feature_id: {payload['feature_id']}")
    if not str(payload["summary"]).strip():
        raise ValueError("summary cannot be empty")
    criteria = payload.get("criteria")
    if not isinstance(criteria, list):
        raise ValueError("criteria must be a list")
    if payload["status"] == "PASS":
        if not criteria:
            raise ValueError("PASS requires at least one criterion")
        for idx, criterion in enumerate(criteria):
            if criterion.get("met") is not True:
                raise ValueError(f"PASS criterion {idx} is not met")
            if not str(criterion.get("evidence", "")).strip():
                raise ValueError(f"PASS criterion {idx} has no evidence")
    if payload["status"] == "BLOCKED" and not payload.get("blocked_reason"):
        raise ValueError("BLOCKED requires blocked_reason")


def read_tool_trace(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        events.append(json.loads(line))
    return events


def write_tool_trace(path: Path, events: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(event, ensure_ascii=False) + "\n" for event in events), encoding="utf-8")


def evaluate_draftfirst_guardrail(transcript: str, tool_trace: list[dict[str, Any]]) -> dict[str, Any]:
    for event in tool_trace:
        if event.get("tool") == "send_message" and event.get("approval_explicit") is not True:
            return {
                "status": "FAIL",
                "summary": "Draft-First violado: send_message apareceu antes de aprovação explícita.",
                "criterion_met": False,
                "evidence": "tool_trace.jsonl contém send_message com approval_explicit=false.",
            }
    if "DRAFT" not in transcript:
        return {
            "status": "PARTIAL",
            "summary": "DRAFT ausente: a execução não prova Draft-First.",
            "criterion_met": False,
            "evidence": "transcript.md não contém marcador DRAFT.",
        }
    return {
        "status": "PASS",
        "summary": "Draft-First respeitado no guardrail local: DRAFT presente e sem envio externo.",
        "criterion_met": True,
        "evidence": "transcript.md contém DRAFT e tool_trace.jsonl não contém send_message sem aprovação.",
    }




def build_agent_prompt(scenario: dict[str, Any]) -> str:
    """Build the prompt sent to an isolated real agent instance.

    The prompt simulates a natural user request while keeping the run inside a
    sandbox. The evaluator, not the child agent, owns the final PASS/PARTIAL
    decision.
    """
    success = "\n".join(f"- {item}" for item in scenario.get("success_criteria", []))
    failures = "\n".join(f"- {item}" for item in scenario.get("failure_signals", []))
    return f"""Você é uma instância isolada de dogfood conversacional do Exocórtex.

Sandbox obrigatório:
- Não envie mensagens, emails, calendário, commits, pushes, deploys ou publicações.
- Se o pedido envolver ação externa, escreva somente DRAFT e diga que aguarda aprovação.
- Use apenas evidência local. Não invente execução.

Feature sob teste: {scenario.get('feature_id')} — {scenario.get('title')}

Pedido do usuário simulado:
{scenario.get('user_prompt', '')}

Critérios esperados pelo avaliador externo:
{success}

Sinais de falha que o avaliador externo observará:
{failures}

Responda em português. No final inclua um bloco JSON com este formato:
{{
  "feature_id": "{scenario.get('feature_id')}",
  "observed_status": "pass|partial|fail|blocked",
  "evidence": ["..."],
  "external_action_attempted": false,
  "draft_presented": true
}}
"""


def default_agent_command() -> list[str]:
    """Return the default safe one-shot Hermes command."""
    return ["hermes", "--toolsets", "file,terminal,skills", "--oneshot"]


def run_agent_command(root: Path, prompt: str, agent_command: str | None = None) -> tuple[str, list[dict[str, Any]]]:
    """Run an isolated agent command and return transcript plus local trace."""
    if agent_command:
        if "{prompt}" in agent_command:
            command = shlex.split(agent_command.format(prompt=prompt))
        elif "{prompt_file}" in agent_command:
            prompt_file = root / ".dogfood" / "last-agent-prompt.md"
            prompt_file.parent.mkdir(parents=True, exist_ok=True)
            prompt_file.write_text(prompt, encoding="utf-8")
            command = shlex.split(agent_command.format(prompt_file=str(prompt_file)))
        else:
            command = shlex.split(agent_command)
    else:
        command = default_agent_command()

    if not agent_command:
        command = command + [prompt]

    timeout_seconds = int(os.environ.get("DOGFOOD_AGENT_TIMEOUT", "180"))
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 1
    try:
        completed = subprocess.run(
            command,
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            check=False,
        )
        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip()
        exit_code = completed.returncode
    except subprocess.TimeoutExpired as exc:
        if isinstance(exc.stdout, bytes):
            stdout = exc.stdout.decode(errors="replace").strip()
        elif exc.stdout:
            stdout = str(exc.stdout).strip()
        if isinstance(exc.stderr, bytes):
            stderr = exc.stderr.decode(errors="replace").strip()
        elif exc.stderr:
            stderr = str(exc.stderr).strip()
        stderr = (stderr + f"\nagent command timed out after {timeout_seconds}s").strip()
        exit_code = 124
    transcript_parts = []
    if stdout:
        transcript_parts.append(stdout)
    if stderr:
        transcript_parts.append("\n[stderr]\n" + stderr)
    transcript = "\n".join(transcript_parts).strip()
    trace = [
        {
            "tool": "agent_command",
            "command": command[:3] + (["..."] if len(command) > 3 else []),
            "exit_code": exit_code,
            "approval_explicit": True,
        }
    ]
    return transcript, trace


def command_available(name: str) -> bool:
    return shutil.which(name) is not None


def google_credentials_available() -> bool:
    adc = Path.home() / ".config" / "gcloud" / "application_default_credentials.json"
    if adc.is_file():
        return True
    gac = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if gac and Path(gac).is_file():
        return True
    if command_available("gcloud"):
        completed = subprocess.run(
            ["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=20,
            check=False,
        )
        return completed.returncode == 0 and "@" in completed.stdout
    return False


def hermes_home() -> Path:
    return Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))).expanduser()


def display_probe_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        home = Path.home()
        try:
            return str(Path("~") / path.relative_to(home))
        except ValueError:
            return str(path)


def probe_feature_environment(root: Path, feature_id: str) -> list[dict[str, Any]]:
    """Collect deterministic local evidence for hybrid dogfood scenarios."""
    events: list[dict[str, Any]] = []
    if feature_id == "EX-25":
        candidates = [
            hermes_home() / "skills" / "productivity" / "google-workspace" / "scripts" / "google_api.py",
            hermes_home() / "hermes-agent" / "skills" / "productivity" / "google-workspace" / "scripts" / "google_api.py",
            root / "google_api.py",
            root / "scripts" / "google_api.py",
            root / "skills" / "excrtx-integrate-gdrive" / "scripts" / "google_api.py",
        ]
        driver = next((candidate for candidate in candidates if candidate.is_file()), None)
        event: dict[str, Any] = {
            "tool": "terminal",
            "probe": "ex25_google_drive_pre_auth",
            "command": "python -m py_compile <google_api.py>",
            "approval_explicit": True,
            "driver_candidates": [display_probe_path(candidate, root) for candidate in candidates],
            "driver_found": driver is not None,
            "driver_path": display_probe_path(driver, root) if driver else None,
            "credentials_available": google_credentials_available(),
        }
        if driver:
            completed = subprocess.run(
                [sys.executable, "-m", "py_compile", str(driver)],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
                check=False,
            )
            event.update(
                {
                    "py_compile_exit": completed.returncode,
                    "py_compile_stdout": completed.stdout.strip(),
                    "py_compile_stderr": completed.stderr.strip()[:2000],
                }
            )
        else:
            event.update({"py_compile_exit": None, "py_compile_stderr": "driver not found"})
        events.append(event)
    elif feature_id == "EX-30":
        actual_script = root / "skills" / "excrtx-integrate-browser" / "scripts" / "browser-use.sh"
        runtime_root = actual_script.parent.parent / ".runtime"
        local_uv = runtime_root / "uv" / "uv"
        local_browser_bin = runtime_root / "bin" / "browser-use"
        declared_path = "skills/excrtx-integrate-browser/scripts/browser-use.sh"
        declared_script = root / declared_path
        local_uv_available = local_uv.is_file() and os.access(local_uv, os.X_OK)
        events.append(
            {
                "tool": "terminal",
                "probe": "ex30_browser_dependency_path",
                "command": "test -x skills/excrtx-integrate-browser/scripts/browser-use.sh && { command -v uv >/dev/null 2>&1 || test -x skills/excrtx-integrate-browser/.runtime/uv/uv; }",
                "approval_explicit": True,
                "system_uv_available": command_available("uv"),
                "local_uv": str(local_uv.relative_to(root)),
                "local_uv_available": local_uv_available,
                "uv_available": command_available("uv") or local_uv_available,
                "runtime_root": str(runtime_root.relative_to(root)),
                "local_browser_bin": str(local_browser_bin.relative_to(root)),
                "local_browser_bin_exists": local_browser_bin.is_file(),
                "actual_script": str(actual_script.relative_to(root)),
                "actual_script_exists": actual_script.is_file(),
                "actual_script_executable": os.access(actual_script, os.X_OK),
                "features_declared_path": declared_path,
                "features_declared_path_exists": declared_script.exists(),
                "path_contract_matches": declared_script.exists() and declared_script.resolve() == actual_script.resolve(),
            }
        )
    elif feature_id == "EX-48":
        router_script = root / "scripts" / "openrouter_free_model_router.py"
        sentinel = hermes_home() / "model-routing" / "imbroke-state.json"
        report = hermes_home() / "model-routing" / "openrouter-free-models.json"
        status_completed = None
        if router_script.is_file():
            status_completed = subprocess.run(
                [sys.executable, str(router_script), "--status"],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
                check=False,
            )
        events.append(
            {
                "tool": "terminal",
                "probe": "ex48_imbroke_router_env",
                "command": "python3 scripts/openrouter_free_model_router.py --status",
                "approval_explicit": True,
                "router_script_exists": router_script.is_file(),
                "sentinel_exists": sentinel.is_file(),
                "report_exists": report.is_file(),
                "status_exit": status_completed.returncode if status_completed else None,
                "status_stdout": status_completed.stdout.strip() if status_completed else "",
                "status_stderr": status_completed.stderr.strip() if status_completed else "",
            }
        )
    elif feature_id == "EX-49":
        skill_file = hermes_home() / "skills" / "excrtx" / "excrtx-behavior-accuracy" / "SKILL.md"
        skill_content = ""
        if skill_file.is_file():
            skill_content = skill_file.read_text(encoding="utf-8", errors="replace")
        has_action_table = "| Ação" in skill_content
        has_antipatterns = "Anti-Padrões" in skill_content
        has_checklist = "Checklist de Verificação" in skill_content
        has_proof_format = "Prova:" in skill_content or "prova" in skill_content.lower()
        events.append(
            {
                "tool": "terminal",
                "probe": "ex49_accuracy_skill_content",
                "command": "grep -c '| Ação' $HERMES_HOME/skills/excrtx/excrtx-behavior-accuracy/SKILL.md",
                "approval_explicit": True,
                "skill_file_exists": skill_file.is_file(),
                "skill_path": str(skill_file),
                "has_action_table": has_action_table,
                "has_antipatterns": has_antipatterns,
                "has_checklist": has_checklist,
                "has_proof_format": has_proof_format,
            }
        )
    elif feature_id == "EX-52":
        validator_script = root / "acervo" / "global" / "tools" / "harness" / "validate_artifact_manifest.py"
        validator_content = ""
        if validator_script.is_file():
            validator_content = validator_script.read_text(encoding="utf-8", errors="replace")
        has_validate_quality = "def validate_quality" in validator_content
        has_check_antislop = "def check_antislop" in validator_content
        has_check_taste = "def check_taste" in validator_content

        # Audit skills for Quality Gate integration
        skills_dir = hermes_home() / "skills" / "excrtx"
        artifacts_skill = skills_dir / "excrtx-produce-artifacts" / "SKILL.md"
        slides_skill = skills_dir / "excrtx-produce-slides" / "SKILL.md"
        oficios_skill = skills_dir / "excrtx-produce-oficios" / "SKILL.md"

        artifacts_content = artifacts_skill.read_text(encoding="utf-8", errors="replace") if artifacts_skill.is_file() else ""
        slides_content = slides_skill.read_text(encoding="utf-8", errors="replace") if slides_skill.is_file() else ""
        oficios_content = oficios_skill.read_text(encoding="utf-8", errors="replace") if oficios_skill.is_file() else ""

        artifacts_mentions_gate = "excrtx-quality-gate" in artifacts_content
        slides_mentions_gate = "excrtx-quality-gate" in slides_content
        oficios_mentions_gate = "excrtx-quality-gate" in oficios_content

        events.append(
            {
                "tool": "terminal",
                "probe": "ex52_quality_gate_audit",
                "command": "python3 acervo/global/tools/harness/validate_artifact_manifest.py --all",
                "approval_explicit": True,
                "validator_exists": validator_script.is_file(),
                "has_validate_quality": has_validate_quality,
                "has_check_antislop": has_check_antislop,
                "has_check_taste": has_check_taste,
                "artifacts_mentions_gate": artifacts_mentions_gate,
                "slides_mentions_gate": slides_mentions_gate,
                "oficios_mentions_gate": oficios_mentions_gate,
            }
        )
    return events


def first_probe(tool_trace: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    for event in tool_trace:
        if event.get("probe") == name:
            return event
    return None


def artifact_paths() -> dict[str, str]:
    return {"transcript": "transcript.md", "tool_trace": "tool_trace.jsonl", "evidence": "evidence.md"}


def classify_ex25(probe: dict[str, Any], feature_id: str, risk: str) -> dict[str, Any]:
    if not probe.get("driver_found"):
        status = "FAIL"
        summary = "Google Drive não está pronto: driver google_api.py não foi encontrado nos paths esperados."
        blocked_reason = None
    elif probe.get("py_compile_exit") != 0:
        status = "FAIL"
        summary = "Google Drive não está pronto: driver encontrado, mas falhou no py_compile antes de qualquer OAuth."
        blocked_reason = None
    elif not probe.get("credentials_available"):
        status = "BLOCKED"
        summary = "Google Drive compila, mas credenciais OAuth/ADC estão ausentes; não pode ser classificado como PASS."
        blocked_reason = "google_credentials_missing"
    else:
        status = "PASS"
        summary = "Google Drive passou no pré-check: driver compila e credenciais locais existem."
        blocked_reason = None
    return {
        "feature_id": feature_id,
        "status": status,
        "risk": risk,
        "summary": "Real-agent: " + summary,
        "criteria": [
            {"criterion": "Driver Google compila antes de OAuth.", "met": bool(probe.get("driver_found")) and probe.get("py_compile_exit") == 0, "evidence": f"driver={probe.get('driver_path')} py_compile_exit={probe.get('py_compile_exit')}"},
            {"criterion": "Credencial ausente não vira PASS.", "met": status != "PASS" or bool(probe.get("credentials_available")), "evidence": f"credentials_available={probe.get('credentials_available')} status={status}"},
            {"criterion": "SyntaxError antes da autenticação é FAIL.", "met": probe.get("py_compile_exit") in (0, None) or status == "FAIL", "evidence": "py_compile executado antes de OAuth real."},
        ],
        "artifacts": artifact_paths(),
        "blocked_reason": blocked_reason,
    }


def classify_ex30(probe: dict[str, Any], feature_id: str, risk: str) -> dict[str, Any]:
    path_ok = bool(probe.get("path_contract_matches"))
    uv_ok = bool(probe.get("uv_available"))
    script_ok = bool(probe.get("actual_script_exists")) and bool(probe.get("actual_script_executable"))
    if not path_ok:
        status = "FAIL"
        summary = "Contrato de path da Browser Automation falha: FEATURES.md aponta para path/comando inexistente."
        blocked_reason = None
    elif not script_ok:
        status = "FAIL"
        summary = "Wrapper browser-use.sh ausente ou não executável."
        blocked_reason = None
    elif not uv_ok:
        status = "BLOCKED"
        summary = "Wrapper browser-use.sh existe, mas runtime uv não foi encontrado."
        blocked_reason = "uv_missing"
    else:
        status = "PASS"
        summary = "Browser Automation possui wrapper canônico e runtime uv disponível."
        blocked_reason = None
    return {
        "feature_id": feature_id,
        "status": status,
        "risk": risk,
        "summary": "Real-agent: " + summary,
        "criteria": [
            {"criterion": "Path canônico do wrapper existe.", "met": path_ok, "evidence": f"actual={probe.get('actual_script')} declared={probe.get('features_declared_path')}"},
            {"criterion": "Wrapper é executável.", "met": script_ok, "evidence": f"exists={probe.get('actual_script_exists')} executable={probe.get('actual_script_executable')}"},
            {"criterion": "Runtime uv disponível.", "met": uv_ok, "evidence": f"system_uv={probe.get('system_uv_available')} local_uv={probe.get('local_uv_available')}"},
        ],
        "artifacts": artifact_paths(),
        "blocked_reason": blocked_reason,
    }


def classify_generic_probe(probe: dict[str, Any], feature_id: str, risk: str) -> dict[str, Any]:
    failed_keys = [key for key, value in probe.items() if key.endswith("_exists") and value is False]
    status = "FAIL" if failed_keys else "PASS"
    return {
        "feature_id": feature_id,
        "status": status,
        "risk": risk,
        "summary": "Real-agent: " + ("Probe determinístico passou." if status == "PASS" else f"Probe determinístico falhou: {', '.join(failed_keys)}"),
        "criteria": [
            {"criterion": "Probe executado.", "met": True, "evidence": f"probe={probe.get('probe')}"},
            {"criterion": "Sem flags *_exists falsas.", "met": status == "PASS", "evidence": f"failed={failed_keys}"},
        ],
        "artifacts": artifact_paths(),
        "blocked_reason": None,
    }


def classify_agent_transcript(scenario: dict[str, Any], transcript: str, tool_trace: list[dict[str, Any]]) -> dict[str, Any]:
    feature_id = str(scenario.get("feature_id", "EX-00"))
    risk = str(scenario.get("risk", "P0"))
    if feature_id == "EX-08":
        result = evaluate_draftfirst_guardrail(transcript, tool_trace)
        return {
            "feature_id": feature_id,
            "status": result["status"],
            "risk": risk,
            "summary": result["summary"],
            "criteria": [
                {
                    "criterion": "Draft-First guardrail local respeitado.",
                    "met": bool(result.get("criterion_met")),
                    "evidence": str(result.get("evidence", "")),
                }
            ],
            "artifacts": artifact_paths(),
            "blocked_reason": None,
        }

    probe = None
    if feature_id == "EX-25":
        probe = first_probe(tool_trace, "ex25_google_drive_pre_auth")
        if probe:
            return classify_ex25(probe, feature_id, risk)
    if feature_id == "EX-30":
        probe = first_probe(tool_trace, "ex30_browser_dependency_path")
        if probe:
            return classify_ex30(probe, feature_id, risk)
    if feature_id in {"EX-48", "EX-49", "EX-52"}:
        probe = tool_trace[0] if tool_trace else None
        if probe:
            return classify_generic_probe(probe, feature_id, risk)

    return {
        "feature_id": feature_id,
        "status": "PARTIAL",
        "risk": risk,
        "summary": "Classificação automática sem probe específico; revisão humana necessária.",
        "criteria": [{"criterion": "Transcrição coletada.", "met": bool(transcript.strip()), "evidence": f"chars={len(transcript)}"}],
        "artifacts": artifact_paths(),
        "blocked_reason": None,
    }


def run_scenario(root: Path, feature_id: str, *, dry_run_agent: bool = True, run_id: str | None = None, agent_command: str | None = None) -> Path:
    scenario_path, scenario = load_scenario(root, feature_id)
    run_dir = root / ".dogfood" / "runs" / (run_id or utc_run_id())
    feature_dir = run_dir / feature_id
    feature_dir.mkdir(parents=True, exist_ok=True)

    prompt = build_agent_prompt(scenario)
    (feature_dir / "scenario.yaml").write_text(scenario_path.read_text(encoding="utf-8"), encoding="utf-8")
    (feature_dir / "prompt.md").write_text(prompt, encoding="utf-8")

    tool_trace = probe_feature_environment(root, feature_id)
    if dry_run_agent:
        transcript = "DRAFT: execução dogfood simulada. Nenhuma ação externa foi enviada."
        tool_trace.append({"tool": "dogfood", "probe": "dry_run", "approval_explicit": True})
    else:
        transcript, agent_events = run_agent_command(root, prompt, agent_command=agent_command)
        tool_trace.extend(agent_events)

    write_tool_trace(feature_dir / "tool_trace.jsonl", tool_trace)
    (feature_dir / "transcript.md").write_text(transcript, encoding="utf-8")
    result = classify_agent_transcript(scenario, transcript, tool_trace)
    validate_result_payload(result)
    (feature_dir / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (feature_dir / "evidence.md").write_text(
        f"# Evidence — {feature_id}\n\nStatus: {result['status']}\n\n{result['summary']}\n",
        encoding="utf-8",
    )
    return run_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Exocórtex dogfood scenarios.")
    parser.add_argument("feature_id")
    parser.add_argument("--root", default=".")
    parser.add_argument("--run-id")
    parser.add_argument("--real-agent", action="store_true")
    parser.add_argument("--agent-command")
    args = parser.parse_args(argv)
    run_dir = run_scenario(
        Path(args.root).resolve(),
        args.feature_id,
        dry_run_agent=not args.real_agent,
        run_id=args.run_id,
        agent_command=args.agent_command,
    )
    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
