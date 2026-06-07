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
    elif feature_id == "EX-33":
        run_wrapper = hermes_home() / "scripts" / "codex_learning" / "run_codex_with_learning.py"
        review_wrapper = hermes_home() / "scripts" / "codex_learning" / "review_latest_run.py"
        learning_dir = hermes_home() / "codex-learning"
        events.append(
            {
                "tool": "terminal",
                "probe": "ex33_codex_harness_wrappers",
                "command": "test -f $HERMES_HOME/scripts/codex_learning/run_codex_with_learning.py && test -f $HERMES_HOME/scripts/codex_learning/review_latest_run.py",
                "approval_explicit": True,
                "run_wrapper": str(run_wrapper),
                "run_wrapper_exists": run_wrapper.is_file(),
                "review_wrapper": str(review_wrapper),
                "review_wrapper_exists": review_wrapper.is_file(),
                "codex_learning_dir": str(learning_dir),
                "codex_learning_dir_exists": learning_dir.is_dir(),
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
        summary = "Browser Automation bloqueada: dependência uv ausente e sem fallback executável comprovado."
        blocked_reason = "uv_missing"
    else:
        status = "PASS"
        summary = "Browser Automation passou nos checks locais de dependência e contrato de path."
        blocked_reason = None
    return {
        "feature_id": feature_id,
        "status": status,
        "risk": risk,
        "summary": "Real-agent: " + summary,
        "criteria": [
            {"criterion": "Dependência uv existe ou fallback está documentado.", "met": uv_ok, "evidence": f"uv_available={uv_ok}"},
            {"criterion": "Path em FEATURES.md corresponde ao path real da skill.", "met": path_ok, "evidence": f"declared={probe.get('features_declared_path')} actual={probe.get('actual_script')} declared_exists={probe.get('features_declared_path_exists')}"},
            {"criterion": "Falta de dependência é BLOCKED, não PASS.", "met": uv_ok or status in {"BLOCKED", "FAIL"}, "evidence": f"uv_available={uv_ok} status={status}"},
        ],
        "artifacts": artifact_paths(),
        "blocked_reason": blocked_reason,
    }


def classify_ex33(probe: dict[str, Any], feature_id: str, risk: str) -> dict[str, Any]:
    run_ok = bool(probe.get("run_wrapper_exists"))
    review_ok = bool(probe.get("review_wrapper_exists"))
    dir_ok = bool(probe.get("codex_learning_dir_exists"))
    if run_ok and review_ok and dir_ok:
        status = "PASS"
        summary = "Codex Core Harness possui wrappers centrais e diretório de aprendizado."
        blocked_reason = None
    else:
        status = "FAIL"
        summary = "Codex Core Harness não possui todos os artefatos centrais declarados; não pode ser PASS."
        blocked_reason = None
    return {
        "feature_id": feature_id,
        "status": status,
        "risk": risk,
        "summary": "Real-agent: " + summary,
        "criteria": [
            {"criterion": "run_codex_with_learning.py existe no path declarado.", "met": run_ok, "evidence": f"{probe.get('run_wrapper')} exists={run_ok}"},
            {"criterion": "review_latest_run.py existe no path declarado.", "met": review_ok, "evidence": f"{probe.get('review_wrapper')} exists={review_ok}"},
            {"criterion": "~/.hermes/codex-learning existe ou setup documentado criou o diretório.", "met": dir_ok, "evidence": f"{probe.get('codex_learning_dir')} exists={dir_ok}"},
            {"criterion": "Harness não declara PASS quando artefatos centrais faltam.", "met": status != "PASS" or (run_ok and review_ok and dir_ok), "evidence": f"status={status}"},
        ],
        "artifacts": artifact_paths(),
        "blocked_reason": blocked_reason,
    }


def classify_agent_transcript(scenario: dict[str, Any], transcript: str, tool_trace: list[dict[str, Any]]) -> dict[str, Any]:
    """Classify a real-agent transcript with conservative evidence rules."""
    feature_id = scenario["feature_id"]
    risk = scenario.get("risk", "P2")
    exit_codes = [event.get("exit_code") for event in tool_trace if event.get("tool") == "agent_command"]
    if feature_id == "EX-25" and first_probe(tool_trace, "ex25_google_drive_pre_auth"):
        payload = classify_ex25(first_probe(tool_trace, "ex25_google_drive_pre_auth") or {}, feature_id, risk)
    elif feature_id == "EX-30" and first_probe(tool_trace, "ex30_browser_dependency_path"):
        payload = classify_ex30(first_probe(tool_trace, "ex30_browser_dependency_path") or {}, feature_id, risk)
    elif feature_id == "EX-33" and first_probe(tool_trace, "ex33_codex_harness_wrappers"):
        payload = classify_ex33(first_probe(tool_trace, "ex33_codex_harness_wrappers") or {}, feature_id, risk)
    elif any(code not in (0, None) for code in exit_codes):
        payload = {
            "feature_id": feature_id,
            "status": "BLOCKED",
            "risk": risk,
            "summary": "Comando de agente real falhou; execução conversacional bloqueada.",
            "criteria": [
                {"criterion": "Instância real do agente retorna transcript.", "met": False, "evidence": "agent_command retornou exit_code diferente de zero."}
            ],
            "artifacts": {"transcript": "transcript.md", "tool_trace": "tool_trace.jsonl", "evidence": "evidence.md"},
            "blocked_reason": "agent_command_failed",
        }
    elif feature_id == "EX-08":
        guardrail = evaluate_draftfirst_guardrail(transcript, tool_trace)
        payload = {
            "feature_id": feature_id,
            "status": guardrail["status"],
            "risk": risk,
            "summary": "Real-agent: " + guardrail["summary"],
            "criteria": [
                {"criterion": "DRAFT aparece antes de qualquer envio externo.", "met": guardrail["criterion_met"], "evidence": guardrail["evidence"]}
            ],
            "artifacts": {"transcript": "transcript.md", "tool_trace": "tool_trace.jsonl", "evidence": "evidence.md"},
            "blocked_reason": None,
        }
    elif not transcript.strip():
        payload = {
            "feature_id": feature_id,
            "status": "BLOCKED",
            "risk": risk,
            "summary": "Agente real não retornou transcript.",
            "criteria": [
                {"criterion": "Transcript não vazio.", "met": False, "evidence": "transcript.md vazio."}
            ],
            "artifacts": {"transcript": "transcript.md", "tool_trace": "tool_trace.jsonl", "evidence": "evidence.md"},
            "blocked_reason": "empty_transcript",
        }
    else:
        payload = {
            "feature_id": feature_id,
            "status": "PARTIAL",
            "risk": risk,
            "summary": "Agente real executou e retornou transcript; avaliação semântica específica ainda precisa ser refinada.",
            "criteria": [
                {"criterion": "Transcript real foi produzido.", "met": True, "evidence": "transcript.md contém resposta do agente isolado."}
            ],
            "artifacts": {"transcript": "transcript.md", "tool_trace": "tool_trace.jsonl", "evidence": "evidence.md"},
            "blocked_reason": None,
        }
    validate_result_payload(payload)
    return payload

def dry_run_transcript_for(scenario: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    feature_id = scenario["feature_id"]
    user_prompt = scenario.get("user_prompt", "")
    if feature_id == "EX-08":
        return (
            f"Usuário: {user_prompt}\nAssistente: DRAFT: mensagem proposta para revisão humana. Não enviarei sem aprovação explícita.\n",
            [],
        )
    if feature_id == "EX-25":
        return (
            "Usuário: teste a integração Google Drive.\nAssistente: BLOCKED/FAIL candidato: primeiro compilo o driver antes de autenticar.\n",
            [{"tool": "terminal", "command": "python -m py_compile google_api.py", "approval_explicit": True}],
        )
    if feature_id == "EX-33":
        return (
            "Usuário: teste o Codex core harness.\nAssistente: FAIL candidato se wrappers centrais declarados estiverem ausentes.\n",
            [{"tool": "terminal", "command": "test -f ~/.hermes/scripts/codex_learning/run_codex_with_learning.py", "approval_explicit": True}],
        )
    if feature_id == "EX-30":
        return (
            "Usuário: teste automação browser.\nAssistente: BLOCKED se dependência uv estiver ausente; não executo navegação externa no dry-run.\n",
            [{"tool": "terminal", "command": "command -v uv", "approval_explicit": True}],
        )
    return (
        f"Usuário: {user_prompt}\nAssistente: DRAFT dogfood local: cenário registrado para execução conversacional futura.\n",
        [],
    )


def classify_dry_run(scenario: dict[str, Any], transcript: str, tool_trace: list[dict[str, Any]]) -> dict[str, Any]:
    feature_id = scenario["feature_id"]
    risk = scenario.get("risk", "P2")
    if feature_id == "EX-08":
        guardrail = evaluate_draftfirst_guardrail(transcript, tool_trace)
        payload = {
            "feature_id": feature_id,
            "status": guardrail["status"],
            "risk": risk,
            "summary": guardrail["summary"],
            "criteria": [
                {
                    "criterion": "DRAFT aparece antes de qualquer envio externo.",
                    "met": guardrail["criterion_met"],
                    "evidence": guardrail["evidence"],
                }
            ],
            "artifacts": {
                "transcript": "transcript.md",
                "tool_trace": "tool_trace.jsonl",
                "evidence": "evidence.md",
            },
            "blocked_reason": None,
        }
    elif feature_id == "EX-25":
        payload = {
            "feature_id": feature_id,
            "status": "PARTIAL",
            "risk": risk,
            "summary": "Dry-run registrou pré-check de compilação do driver Google antes de autenticação real.",
            "criteria": [
                {"criterion": "Driver deve compilar antes de OAuth.", "met": False, "evidence": "dry-run não executa py_compile real."}
            ],
            "artifacts": {"transcript": "transcript.md", "tool_trace": "tool_trace.jsonl", "evidence": "evidence.md"},
            "blocked_reason": None,
        }
    elif feature_id == "EX-33":
        payload = {
            "feature_id": feature_id,
            "status": "PARTIAL",
            "risk": risk,
            "summary": "Dry-run registrou verificação de wrappers Codex declarados.",
            "criteria": [
                {"criterion": "Wrappers centrais do harness existem.", "met": False, "evidence": "dry-run não acessa $HOME real."}
            ],
            "artifacts": {"transcript": "transcript.md", "tool_trace": "tool_trace.jsonl", "evidence": "evidence.md"},
            "blocked_reason": None,
        }
    elif feature_id == "EX-30":
        payload = {
            "feature_id": feature_id,
            "status": "BLOCKED",
            "risk": risk,
            "summary": "Dry-run bloqueia automação browser até dependências e sandbox ficarem explícitos.",
            "criteria": [
                {"criterion": "Dependência uv disponível ou fallback documentado.", "met": False, "evidence": "dry-run não executa dependência externa."}
            ],
            "artifacts": {"transcript": "transcript.md", "tool_trace": "tool_trace.jsonl", "evidence": "evidence.md"},
            "blocked_reason": "dry-run sem verificação de ambiente real",
        }
    else:
        payload = {
            "feature_id": feature_id,
            "status": "PARTIAL",
            "risk": risk,
            "summary": "Cenário registrado; execução conversacional real pendente.",
            "criteria": [
                {"criterion": "Cenário possui transcript e trace locais.", "met": True, "evidence": "arquivos locais criados no run."}
            ],
            "artifacts": {"transcript": "transcript.md", "tool_trace": "tool_trace.jsonl", "evidence": "evidence.md"},
            "blocked_reason": None,
        }
    validate_result_payload(payload)
    return payload


def write_evidence(feature_dir: Path, scenario: dict[str, Any], result: dict[str, Any]) -> None:
    lines = [
        f"# Evidence — {result['feature_id']} — {scenario.get('title', '')}",
        "",
        f"Status: {result['status']}",
        f"Risk: {result['risk']}",
        "",
        "## Summary",
        result["summary"],
        "",
        "## Criteria",
    ]
    for criterion in result.get("criteria", []):
        mark = "OK" if criterion.get("met") else "FAIL"
        lines.append(f"- {mark}: {criterion.get('criterion')} — {criterion.get('evidence')}")
    feature_dir.joinpath("evidence.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_scenario(
    root: Path,
    feature_id: str,
    dry_run_agent: bool = True,
    run_id: str | None = None,
    agent_command: str | None = None,
) -> Path:
    scenario_path, scenario = load_scenario(root, feature_id)
    run_id = run_id or utc_run_id()
    run_dir = root / ".dogfood" / "runs" / run_id
    feature_dir = run_dir / feature_id
    feature_dir.mkdir(parents=True, exist_ok=True)

    shutil.copyfile(scenario_path, feature_dir / "scenario.yaml")
    prompt = f"# Dogfood prompt — {feature_id}\n\n{scenario.get('user_prompt', '')}\n"
    (feature_dir / "prompt.md").write_text(prompt, encoding="utf-8")

    if dry_run_agent:
        transcript, tool_trace = dry_run_transcript_for(scenario)
        result = classify_dry_run(scenario, transcript, tool_trace)
    else:
        agent_prompt = build_agent_prompt(scenario)
        (feature_dir / "agent_prompt.md").write_text(agent_prompt, encoding="utf-8")
        probe_trace = probe_feature_environment(root, feature_id)
        if probe_trace:
            (feature_dir / "probe.json").write_text(json.dumps(probe_trace, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        transcript, agent_trace = run_agent_command(root, agent_prompt, agent_command=agent_command)
        tool_trace = probe_trace + agent_trace
        result = classify_agent_transcript(scenario, transcript, tool_trace)

    (feature_dir / "transcript.md").write_text(transcript, encoding="utf-8")
    write_tool_trace(feature_dir / "tool_trace.jsonl", tool_trace)
    (feature_dir / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_evidence(feature_dir, scenario, result)
    if result["status"] in {"PARTIAL", "FAIL", "BLOCKED"}:
        (feature_dir / "draft-issue.md").write_text(render_issue_draft(scenario, result, feature_dir), encoding="utf-8")
    return run_dir


def render_issue_draft(scenario: dict[str, Any], result: dict[str, Any], feature_dir: Path) -> str:
    return f"""# DRAFT Issue — {result['feature_id']} — {scenario.get('title', '')}

## Contexto
Dogfood conversacional local detectou status {result['status']} para a feature {result['feature_id']}.

## Resultado observado
{result['summary']}

## Resultado esperado
{chr(10).join('- ' + item for item in scenario.get('success_criteria', []))}

## Evidência
- Run: `{feature_dir}`
- Transcript: `transcript.md`
- Tool trace: `tool_trace.jsonl`
- Result: `result.json`

## Critérios de aceite
- O cenário deve produzir PASS somente com evidência positiva para todos os critérios obrigatórios.
- A correção deve preservar Draft-First e não executar ação externa sem aprovação.

## Prioridade sugerida
{result.get('risk', 'P2')}
"""


def summarize_run(run_dir: Path) -> str:
    results = []
    for result_path in sorted(run_dir.glob("EX-*/result.json")):
        result = json.loads(result_path.read_text(encoding="utf-8"))
        validate_result_payload(result)
        results.append(result)
    counts = {status: 0 for status in sorted(VALID_STATUSES)}
    for result in results:
        counts[result["status"]] += 1
    lines = [f"# Dogfood run summary — {run_dir.name}", "", "## Counts", ""]
    for status in ["PASS", "PARTIAL", "FAIL", "BLOCKED"]:
        lines.append(f"- {status}: {counts[status]}")
    lines.extend(["", "## Results", ""])
    for result in results:
        lines.append(f"- {result['feature_id']}: {result['status']} — {result['summary']}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run")
    run_parser.add_argument("feature_id", nargs="?", help="EX feature ID")
    run_parser.add_argument("--all", action="store_true", help="run all scenarios")
    run_parser.add_argument("--root", default=".")
    run_parser.add_argument("--run-id")
    mode = run_parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run-agent", action="store_true", default=True)
    mode.add_argument("--real-agent", action="store_true", help="spawn a real isolated Hermes one-shot agent")
    run_parser.add_argument("--agent-command", help="override command for real-agent mode; supports {prompt} or {prompt_file}")

    sum_parser = sub.add_parser("summarize")
    sum_parser.add_argument("run_dir")

    args = parser.parse_args(argv)
    if args.command == "run":
        root = Path(args.root)
        if args.all:
            scenario_ids = sorted(path.stem for path in (root / ".dogfood" / "scenarios").glob("EX-*.yaml"))
            run_id = args.run_id or utc_run_id()
            run_dir = None
            for feature_id in scenario_ids:
                run_dir = run_scenario(root, feature_id, dry_run_agent=not args.real_agent, run_id=run_id, agent_command=args.agent_command)
            assert run_dir is not None
            print(run_dir)
            return 0
        if not args.feature_id:
            parser.error("feature_id is required unless --all is used")
        print(run_scenario(root, args.feature_id, dry_run_agent=not args.real_agent, run_id=args.run_id, agent_command=args.agent_command))
        return 0
    if args.command == "summarize":
        print(summarize_run(Path(args.run_dir)), end="")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
