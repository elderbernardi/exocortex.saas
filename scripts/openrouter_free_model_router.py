#!/usr/bin/env python3
"""Rank free OpenRouter models with a deterministic fallback chain.

Primary signal:
- fox-in-the-box-ai/hermes-best-models benchmark

Secondary coverage signal for models not present in fox:
- OpenRouter catalog metadata (description, context, recency, top-provider limits)

This router is intentionally *not* a default mode. It becomes actionable only
when the caller opts into emergency mode via ``--imbroke``. In that mode the
script may also apply the selected model to Hermes config with ``--apply``.

Circuit breaker (imbroke mode):
- Sentinel file tracks activation state, previous config, and failed models.
- When a model fails, the next eligible model is auto-selected and a recovery
  cron is scheduled to re-evaluate after a cooldown period.
- A watchdog cron periodically checks if the provider changed externally;
  if so, imbroke mode auto-deactivates (guard tripwire).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
# Ensure ~/.local/bin is in PATH so the 'hermes' command can be found
local_bin = str(Path.home() / ".local" / "bin")
if local_bin not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{os.environ.get('PATH', '')}{os.path.pathsep}{local_bin}"

DEFAULT_OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
DEFAULT_FOX_METRICS_INDEX_URL = (
    "https://api.github.com/repos/fox-in-the-box-ai/hermes-best-models/contents/eval_results?ref=main"
)
USER_AGENT = "Exocortex-Issue29/1.1"
SECONDARY_SOURCE_NAME = "openrouter_catalog_metadata"
SECONDARY_KEYWORDS: tuple[tuple[str, float], ...] = (
    ("agentic", 14.0),
    ("tool use", 14.0),
    ("function calling", 12.0),
    ("reasoning", 10.0),
    ("coding", 9.0),
    ("code", 6.0),
    ("long-context", 4.0),
    ("long context", 4.0),
    ("multimodal", 2.0),
)

RATING_SCALE = 10.0  # Escala 1-10
MIN_RATING = 1.0
MAX_RATING = 10.0

# Circuit breaker defaults
DEFAULT_COOLDOWN_SECONDS = 1800  # 30 minutes
WATCHDOG_INTERVAL_MINUTES = 5
IMBROKE_PROVIDER = "openrouter"


def convert_to_10_scale(intelligence_index: float | None, secondary_index: float | None) -> float:
    """Converte intelligence/secondary index (0-100) para escala 1-10."""
    raw_index = None
    if intelligence_index is not None:
        raw_index = intelligence_index
    elif secondary_index is not None:
        raw_index = secondary_index
    
    if raw_index is None:
        return MIN_RATING
    
    # Mapeia 0-100 para 1-10
    rating = round(raw_index / 10.0, 1)
    return max(MIN_RATING, min(MAX_RATING, rating))


def get_warning(rating: float) -> tuple[str, str, str]:
    """Retorna (emoji, status, mensagem) baseado na classificação."""
    if rating >= 8.0:
        return ("🟢", "[OK]", "Aproveite, bom modelo gratuito ativo!")
    elif rating >= 5.0:
        return ("🟡", "[ALERTA]", "Cuidado: este modelo pode ignorar algumas regras e alucinar eventualmente. Revise outputs críticos.")
    else:
        return ("🔴", "[PERIGO]", "Modelo de baixa capacidade. Recomenda-se revisar tudo e avaliar resultados com cautela.\n🔴 [PERIGO] Cuidado com operações que resultem em alteração no sistema.")


def format_transparency_response(model: RankedModel) -> str:
    """Formata resposta de transparência (100% determinística)."""
    rating = convert_to_10_scale(model.intelligence_index, model.secondary_index)
    source = "fox" if model.benchmarked else model.secondary_source or SECONDARY_SOURCE_NAME
    emoji, status, message = get_warning(rating)
    
    lines = [
        f"Modelo selecionado: {model.id}",
        "✅ Gratuito (custo zero)",
        f"✅ Classificação: {rating}/10 (baseado em benchmarks globais)",
        f"📊 Fonte: {source}",
        "",
        f"{emoji} {status} {message}",
    ]
    return "\n".join(lines)


@dataclass
class RankedModel:
    id: str
    canonical_slug: str
    name: str
    context_length: int | None
    pricing: dict[str, Any]
    benchmarked: bool
    intelligence_index: float | None
    pass_rate: float | None
    composite_score: float | None
    avg_latency: float | None
    fox_model_id: str | None
    benchmark_timestamp: str | None
    secondary_source: str | None
    secondary_index: float | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "canonical_slug": self.canonical_slug,
            "name": self.name,
            "context_length": self.context_length,
            "pricing": self.pricing,
            "benchmarked": self.benchmarked,
            "intelligence_index": self.intelligence_index,
            "pass_rate": self.pass_rate,
            "composite_score": self.composite_score,
            "avg_latency": self.avg_latency,
            "fox_model_id": self.fox_model_id,
            "benchmark_timestamp": self.benchmark_timestamp,
            "secondary_source": self.secondary_source,
            "secondary_index": self.secondary_index,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seleciona e ranqueia modelos gratuitos do OpenRouter com fallback determinístico."
    )
    parser.add_argument("--openrouter-models-source", default=DEFAULT_OPENROUTER_MODELS_URL)
    parser.add_argument("--fox-metrics-source", help="JSON local/URL com métricas do fox-in-the-box.")
    parser.add_argument(
        "--fox-metrics-index-url",
        default=DEFAULT_FOX_METRICS_INDEX_URL,
        help="Endpoint GitHub contents usado para descobrir automaticamente o metrics_*.json mais recente.",
    )
    parser.add_argument("--format", choices=["json", "text"], default="text")
    parser.add_argument("--imbroke", action="store_true", help="Ativa o modo de emergência OpenRouter free.")
    parser.add_argument("--apply", action="store_true", help="Aplica provider/model no Hermes local.")
    parser.add_argument("--report-path", help="Caminho opcional para gravar o relatório JSON completo.")
    # Circuit breaker flags
    parser.add_argument("--activate", action="store_true", help="Entra no modo imbroke: salva config atual, aplica melhor free, inicia watchdog.")
    parser.add_argument("--deactivate", action="store_true", help="Sai do modo imbroke: restaura config anterior, remove sentinel e crons.")
    parser.add_argument("--status", action="store_true", help="Mostra estado do modo imbroke.")
    parser.add_argument("--mark-failed", metavar="MODEL_ID", help="Registra modelo como falho e ativa failover.")
    parser.add_argument("--fail-reason", default="unknown", help="Motivo da falha (rate_limit, timeout, api_error).")
    parser.add_argument("--cooldown", type=int, default=DEFAULT_COOLDOWN_SECONDS, help=f"Cooldown em segundos antes de reavaliar (default: {DEFAULT_COOLDOWN_SECONDS}).")
    parser.add_argument("--recover", action="store_true", help="Reavalia modelos após cooldown (chamado pelo cron de recovery).")
    parser.add_argument("--guard", action="store_true", help="Verifica se provider mudou externamente (chamado pelo watchdog cron).")
    args = parser.parse_args()
    if args.apply and not args.imbroke:
        parser.error("--apply exige --imbroke. O roteador não é modo default.")
    if args.activate and not args.imbroke:
        parser.error("--activate exige --imbroke. O roteador não é modo default.")
    return args


def _request_json(url: str) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.load(response)


def load_json_source(source: str) -> Any:
    if source.startswith(("http://", "https://")):
        return _request_json(source)
    path = Path(source).expanduser()
    return json.loads(path.read_text(encoding="utf-8"))


def decimal_zero(value: Any) -> bool:
    try:
        return Decimal(str(value or "0")) == 0
    except (InvalidOperation, ValueError):
        return False


def is_expired(model: dict[str, Any]) -> bool:
    expiration = model.get("expiration_date")
    if not expiration:
        return False
    try:
        expiration_dt = datetime.fromisoformat(expiration.replace("Z", "+00:00"))
    except ValueError:
        return False
    if expiration_dt.tzinfo is None:
        expiration_dt = expiration_dt.replace(tzinfo=timezone.utc)
    return expiration_dt <= datetime.now(timezone.utc)


def is_free_model(model: dict[str, Any]) -> bool:
    pricing = model.get("pricing") or {}
    return decimal_zero(pricing.get("prompt")) and decimal_zero(pricing.get("completion"))


def discover_latest_fox_metrics(index_url: str) -> tuple[str, dict[str, Any]]:
    listing = _request_json(index_url)
    candidates = [item for item in listing if item.get("name", "").startswith("metrics_") and item.get("download_url")]
    if not candidates:
        raise RuntimeError("Nenhum arquivo metrics_*.json encontrado no repositório fox-in-the-box.")
    latest = max(candidates, key=lambda item: item["name"])
    return latest["name"], _request_json(latest["download_url"])


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def benchmark_aliases(model: dict[str, Any]) -> list[str]:
    aliases: list[str] = []
    for raw in (model.get("id"), model.get("canonical_slug")):
        if not raw:
            continue
        if raw not in aliases:
            aliases.append(raw)
        base = raw.removesuffix(":free")
        if base not in aliases:
            aliases.append(base)
    return aliases


def compute_intelligence_index(metric: dict[str, Any]) -> float:
    categories = metric.get("by_category") or {}
    overall = safe_float(metric.get("pass_rate"))
    multi_step_tool = safe_float((categories.get("multi_step_tool") or {}).get("pass_rate"))
    delegation = safe_float((categories.get("delegation_reasoning") or {}).get("pass_rate"))
    reasoning = safe_float((categories.get("reasoning") or {}).get("pass_rate"))
    failure_mode = safe_float((categories.get("failure_mode") or {}).get("pass_rate"))
    return round(
        overall * 0.50
        + multi_step_tool * 0.20
        + delegation * 0.15
        + reasoning * 0.10
        + failure_mode * 0.05,
        3,
    )


def compute_secondary_index(model: dict[str, Any]) -> float:
    description = str(model.get("description") or "").lower()
    keyword_score = 0.0
    for keyword, weight in SECONDARY_KEYWORDS:
        if keyword in description:
            keyword_score += weight

    context_score = min((safe_int(model.get("context_length")) / 262144.0) * 10.0, 10.0)
    created_score = min(max((safe_int(model.get("created")) - 1_700_000_000) / 10_000_000.0, 0.0), 10.0)
    max_completion = safe_float((model.get("top_provider") or {}).get("max_completion_tokens"))
    completion_score = min(max_completion / 32768.0, 8.0)
    multimodal_penalty = -2.0 if len((model.get("architecture") or {}).get("input_modalities") or []) > 1 else 0.0

    return round(keyword_score + context_score + created_score + completion_score + multimodal_penalty, 3)


def rank_models(openrouter_payload: dict[str, Any], fox_metrics: dict[str, Any], benchmark_name: str) -> list[RankedModel]:
    ranked: list[RankedModel] = []
    for model in openrouter_payload.get("data", []):
        if is_expired(model) or not is_free_model(model):
            continue

        match = None
        for alias in benchmark_aliases(model):
            if alias in fox_metrics:
                match = fox_metrics[alias]
                break

        secondary_index = None if match else compute_secondary_index(model)
        ranked.append(
            RankedModel(
                id=model.get("id", ""),
                canonical_slug=model.get("canonical_slug") or model.get("id", ""),
                name=model.get("name") or model.get("id", ""),
                context_length=model.get("context_length"),
                pricing=model.get("pricing") or {},
                benchmarked=match is not None,
                intelligence_index=compute_intelligence_index(match) if match else None,
                pass_rate=safe_float(match.get("pass_rate")) if match else None,
                composite_score=safe_float(match.get("composite_score")) if match else None,
                avg_latency=safe_float(match.get("avg_latency")) if match else None,
                fox_model_id=match.get("model_id") if match else None,
                benchmark_timestamp=benchmark_name,
                secondary_source=None if match else SECONDARY_SOURCE_NAME,
                secondary_index=secondary_index,
            )
        )

    ranked.sort(
        key=lambda item: (
            0 if item.benchmarked else 1,
            -(item.intelligence_index if item.intelligence_index is not None else -1.0),
            -(item.composite_score if item.composite_score is not None else -1.0),
            -(item.secondary_index if item.secondary_index is not None else -1.0),
            -(item.context_length or 0),
            item.id,
        )
    )
    return ranked


def _hermes_home() -> Path:
    """Resolve HERMES_HOME directory."""
    if os.environ.get("HERMES_HOME"):
        return Path(os.environ["HERMES_HOME"]).expanduser()
    env_home = Path(Path.cwd())
    if env_home.name == ".hermes":
        return env_home
    return Path(Path.home(), ".hermes")


def default_report_path() -> Path:
    return _hermes_home() / "model-routing" / "openrouter-free-models.json"


def default_state_path() -> Path:
    """Path to imbroke sentinel file."""
    return _hermes_home() / "model-routing" / "imbroke-state.json"


def apply_selected_model(model_id: str) -> None:
    commands = [
        ["hermes", "config", "set", "model.provider", IMBROKE_PROVIDER],
        ["hermes", "config", "set", "model.default", model_id],
    ]
    for cmd in commands:
        completed = subprocess.run(
            cmd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"Falha ao aplicar configuração Hermes: {' '.join(cmd)}\nSTDOUT: {completed.stdout}\nSTDERR: {completed.stderr}"
            )


def _hermes_config_get(key: str) -> str | None:
    """Read a Hermes config value.

    Tries ``hermes config get <key>`` first. If that subcommand is unavailable
    (the real Hermes CLI uses ``config show`` but has no ``get``), falls back to
    reading ``config.yaml`` directly.
    """
    # Try CLI first
    try:
        result = subprocess.run(
            ["hermes", "config", "get", key],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip() or None
    except FileNotFoundError:
        pass

    # Fallback: read config.yaml directly
    config_path = _hermes_home() / "config.yaml"
    if not config_path.is_file():
        return None
    try:
        import yaml  # noqa: delayed import — only needed for fallback
        config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except Exception:
        # If yaml is not available, parse the key manually for simple dotted keys
        try:
            return _parse_yaml_key_simple(config_path, key)
        except Exception:
            return None
    # Resolve dotted key: "model.provider" → config["model"]["provider"]
    parts = key.split(".")
    node: Any = config
    for part in parts:
        if isinstance(node, dict):
            node = node.get(part)
        else:
            return None
    return str(node) if node is not None else None


def _parse_yaml_key_simple(config_path: Path, key: str) -> str | None:
    """Minimal YAML parser for simple dotted keys like 'model.provider'.

    Works without PyYAML by doing basic text parsing of well-formatted YAML.
    Only handles top-level dict with one level of nesting.
    """
    parts = key.split(".")
    if len(parts) != 2:
        return None
    section, field = parts
    lines = config_path.read_text(encoding="utf-8").splitlines()
    in_section = False
    for line in lines:
        stripped = line.rstrip()
        # Check for top-level key (no leading whitespace)
        if not stripped.startswith(" ") and not stripped.startswith("\t"):
            if stripped.startswith(f"{section}:"):
                in_section = True
                continue
            elif in_section and ":" in stripped:
                in_section = False
        elif in_section:
            # Indented line within section
            trimmed = stripped.lstrip()
            if trimmed.startswith(f"{field}:"):
                value = trimmed[len(f"{field}:"):].strip()
                # Remove quotes if present
                if (value.startswith("'") and value.endswith("'")) or \
                   (value.startswith('"') and value.endswith('"')):
                    value = value[1:-1]
                return value if value else None
    return None


def _get_current_fallback_providers() -> list[dict[str, str]]:
    """Read the current fallback_providers list from config.yaml."""
    config_path = _hermes_home() / "config.yaml"
    if not config_path.is_file():
        return []
    try:
        import yaml
        config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        fb = config.get("fallback_providers", [])
        if isinstance(fb, list):
            return [e for e in fb if isinstance(e, dict) and "provider" in e and "model" in e]
        return []
    except ImportError:
        return []
    except Exception:
        return []


def _hermes_config_set(key: str, value: str) -> bool:
    """Set a Hermes config value. Returns True on success."""
    try:
        result = subprocess.run(
            ["hermes", "config", "set", key, value],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def _set_fallback_providers(fallback_list: list[dict[str, str]]) -> bool:
    """Write fallback_providers and fallback_model as proper YAML lists in config.yaml.

    ``hermes config set`` serializes lists as strings, which breaks the
    agent's fallback chain parsing. We edit config.yaml directly instead.
    """
    config_path = _hermes_home() / "config.yaml"
    if not config_path.is_file():
        return False
    try:
        import yaml
        config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        config["fallback_providers"] = fallback_list
        config["fallback_model"] = fallback_list
        config_path.write_text(
            yaml.dump(config, default_flow_style=False, allow_unicode=True),
            encoding="utf-8",
        )
        return True
    except ImportError:
        # Fallback without PyYAML: write minimal YAML snippets
        return _set_fallback_providers_manual(config_path, fallback_list)
    except Exception:
        return False


def _set_fallback_providers_manual(config_path: Path, fallback_list: list[dict[str, str]]) -> bool:
    """Write fallback_providers and fallback_model without PyYAML — text-based replacement."""
    try:
        text = config_path.read_text(encoding="utf-8")
        lines = text.splitlines(keepends=True)
        new_lines: list[str] = []
        skip_block = False
        inserted_providers = False
        inserted_model = False
        for line in lines:
            stripped = line.lstrip()
            if skip_block:
                # Skip continuation lines (indented or list items)
                if line.startswith(" ") or line.startswith("\t") or stripped.startswith("-"):
                    continue
                skip_block = False

            if stripped.startswith("fallback_providers:"):
                skip_block = True
                # Write new value
                if not fallback_list:
                    new_lines.append("fallback_providers: []\n")
                else:
                    new_lines.append("fallback_providers:\n")
                    for fb in fallback_list:
                        new_lines.append(f"- provider: {fb['provider']}\n")
                        new_lines.append(f"  model: {fb['model']}\n")
                inserted_providers = True
                continue
            elif stripped.startswith("fallback_model:"):
                skip_block = True
                # Write new value
                if not fallback_list:
                    new_lines.append("fallback_model: []\n")
                else:
                    new_lines.append("fallback_model:\n")
                    for fb in fallback_list:
                        new_lines.append(f"- provider: {fb['provider']}\n")
                        new_lines.append(f"  model: {fb['model']}\n")
                inserted_model = True
                continue

            new_lines.append(line)

        if not inserted_providers:
            # Key didn't exist — append
            if not fallback_list:
                new_lines.append("fallback_providers: []\n")
            else:
                new_lines.append("fallback_providers:\n")
                for fb in fallback_list:
                    new_lines.append(f"- provider: {fb['provider']}\n")
                    new_lines.append(f"  model: {fb['model']}\n")
        if not inserted_model:
            # Key didn't exist — append
            if not fallback_list:
                new_lines.append("fallback_model: []\n")
            else:
                new_lines.append("fallback_model:\n")
                for fb in fallback_list:
                    new_lines.append(f"- provider: {fb['provider']}\n")
                    new_lines.append(f"  model: {fb['model']}\n")

        config_path.write_text("".join(new_lines), encoding="utf-8")
        return True
    except Exception:
        return False


def _build_imbroke_hint(model_id: str, rating: float) -> str:
    """Build the prompt hint notifying the agent it is in imbroke mode."""
    return f"[IMBROKE MODE] Sistema operando em contingência de modelos gratuitos. Modelo atual ativo: {model_id} (Classificação: {rating}/10)."


def _set_environment_hint(hint: str | None) -> bool:
    """Set the agent.environment_hint config value.

    Tries to write directly using PyYAML if available. Falls back to running
    ``hermes config set agent.environment_hint "<hint>"``.
    """
    config_path = _hermes_home() / "config.yaml"
    if not config_path.is_file():
        return False
    try:
        import yaml
        config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        if "agent" not in config:
            config["agent"] = {}
        if isinstance(config["agent"], dict):
            if hint is None:
                if "environment_hint" in config["agent"]:
                    del config["agent"]["environment_hint"]
            else:
                config["agent"]["environment_hint"] = hint
        config_path.write_text(
            yaml.dump(config, default_flow_style=False, allow_unicode=True),
            encoding="utf-8",
        )
        return True
    except ImportError:
        # Fallback to hermes config set agent.environment_hint
        if hint is None:
            return _hermes_config_set("agent.environment_hint", "")
        return _hermes_config_set("agent.environment_hint", hint)
    except Exception:
        return False


def _hermes_cron_create(
    schedule: str, script_path: str, name: str, *, repeat: int | None = None,
) -> str | None:
    """Create a Hermes cron job. Returns job ID or None.

    Uses ``--no-agent --script`` so the job runs as a plain script without
    involving the LLM, which is essential for deterministic circuit breaker
    operations.
    """
    cmd = [
        "hermes", "cron", "create", schedule,
        "--script", script_path,
        "--no-agent",
        "--name", name,
    ]
    if repeat is not None:
        cmd.extend(["--repeat", str(repeat)])
    try:
        result = subprocess.run(
            cmd,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        if result.returncode == 0:
            # Parse "Created job: <id>" or similar output
            for line in result.stdout.strip().splitlines():
                stripped = line.strip()
                if ":" in stripped:
                    # e.g. "Created job: c7716265f273"
                    return stripped.split(":", 1)[1].strip()
                elif stripped:
                    return stripped
        return None
    except FileNotFoundError:
        return None


def _hermes_cron_remove(cron_id: str) -> bool:
    """Remove a Hermes cron job."""
    try:
        result = subprocess.run(
            ["hermes", "cron", "remove", cron_id],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


# ──────────────────────────────────────────────────────────────────────────────
# Sentinel state management
# ──────────────────────────────────────────────────────────────────────────────

def load_imbroke_state(state_path: Path) -> dict[str, Any] | None:
    """Load sentinel state. Returns None if sentinel does not exist."""
    if not state_path.is_file():
        return None
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def save_imbroke_state(state_path: Path, state: dict[str, Any]) -> None:
    """Persist sentinel state to disk."""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def is_imbroke_active(state_path: Path) -> bool:
    """Check if imbroke mode is active."""
    state = load_imbroke_state(state_path)
    return state is not None and state.get("active", False)


# ──────────────────────────────────────────────────────────────────────────────
# Circuit breaker
# ──────────────────────────────────────────────────────────────────────────────

def is_model_available(model_id: str, failed_models: dict[str, Any]) -> bool:
    """True if model is not failed or its cooldown has expired."""
    if model_id not in failed_models:
        return True
    cooldown_until = failed_models[model_id].get("cooldown_until")
    if not cooldown_until:
        return False
    try:
        deadline = datetime.fromisoformat(cooldown_until.replace("Z", "+00:00"))
        return datetime.now(timezone.utc) >= deadline
    except (ValueError, TypeError):
        return False


def select_with_failover(ranked: list[RankedModel], failed_models: dict[str, Any]) -> RankedModel:
    """Select the best available model, skipping those in failed state."""
    for model in ranked:
        if is_model_available(model.id, failed_models):
            return model
    # All models failed — pick the one whose cooldown expires soonest
    if ranked:
        def _cooldown_sort(m: RankedModel) -> str:
            entry = failed_models.get(m.id, {})
            return entry.get("cooldown_until", "9999")
        return min(ranked, key=_cooldown_sort)
    raise RuntimeError("Nenhum modelo disponível no ranking.")


def _cleanup_expired_failures(state: dict[str, Any]) -> list[str]:
    """Remove expired failures from state. Returns list of cleared model IDs."""
    failed = state.get("failed_models", {})
    now = datetime.now(timezone.utc)
    cleared: list[str] = []
    for model_id in list(failed.keys()):
        cooldown_until = failed[model_id].get("cooldown_until")
        if cooldown_until:
            try:
                deadline = datetime.fromisoformat(cooldown_until.replace("Z", "+00:00"))
                if now >= deadline:
                    del failed[model_id]
                    cleared.append(model_id)
            except (ValueError, TypeError):
                del failed[model_id]
                cleared.append(model_id)
    return cleared


# ──────────────────────────────────────────────────────────────────────────────
# Guard tripwire
# ──────────────────────────────────────────────────────────────────────────────

def guard_check(state_path: Path) -> bool:
    """Check if provider is still openrouter. Auto-deactivate if not.

    Returns True if imbroke is still active, False if it was deactivated.
    """
    state = load_imbroke_state(state_path)
    if state is None or not state.get("active"):
        return False

    current_provider = _hermes_config_get("model.provider")
    if current_provider is None:
        # Cannot determine provider — keep imbroke active (fail-safe)
        return True

    if current_provider.strip().lower() == IMBROKE_PROVIDER:
        return True

    # Provider changed externally — auto-deactivate
    _cancel_all_crons(state)
    previous_hint = state.get("previous_environment_hint")
    _set_environment_hint(previous_hint)
    if state_path.is_file():
        state_path.unlink()

    print(format_guard_notification(current_provider.strip()))
    return False


def _cancel_all_crons(state: dict[str, Any]) -> None:
    """Cancel recovery and watchdog crons if they exist."""
    for key in ("recovery_cron_id", "watchdog_cron_id"):
        cron_id = state.get(key)
        if cron_id:
            _hermes_cron_remove(cron_id)


# ──────────────────────────────────────────────────────────────────────────────
# Deterministic notification formatting
# ──────────────────────────────────────────────────────────────────────────────

def format_failover_notification(
    failed_model: str, reason: str, new_model: RankedModel, cooldown: int,
) -> str:
    """Format failover notification (100% deterministic)."""
    rating = convert_to_10_scale(new_model.intelligence_index, new_model.secondary_index)
    source = "fox" if new_model.benchmarked else new_model.secondary_source or SECONDARY_SOURCE_NAME
    emoji, status, message = get_warning(rating)
    cooldown_min = cooldown // 60
    lines = [
        f"⚠️ [FAILOVER] Modelo {failed_model} marcado como falho ({reason})",
        f"🔄 Alternando para: {new_model.id}",
        f"✅ Classificação: {rating}/10 (baseado em benchmarks globais)",
        f"📊 Fonte: {source}",
        f"⏱️ Recovery agendado: reavaliação em {cooldown_min} min",
        "",
        f"{emoji} {status} {message}",
    ]
    return "\n".join(lines)


def format_recovery_notification(
    model: RankedModel, restored: bool, still_failed: list[str],
    next_recovery_min: int | None,
) -> str:
    """Format recovery notification (100% deterministic)."""
    rating = convert_to_10_scale(model.intelligence_index, model.secondary_index)
    source = "fox" if model.benchmarked else model.secondary_source or SECONDARY_SOURCE_NAME
    emoji, status, message = get_warning(rating)
    lines = ["🔄 [RECOVERY] Reavaliação de modelos concluída"]
    if restored:
        lines.append(f"✅ Modelo restaurado: {model.id} ({rating}/10)")
    else:
        lines.append(f"✅ Mantendo: {model.id} ({rating}/10)")
    lines.append(f"📊 Fonte: {source}")
    if still_failed:
        lines.append(f"⚠️ Modelos ainda indisponíveis: {', '.join(still_failed)}")
    if next_recovery_min is not None:
        lines.append(f"⏱️ Próxima reavaliação em {next_recovery_min} min")
    lines.extend(["", f"{emoji} {status} {message}"])
    return "\n".join(lines)


def format_guard_notification(new_provider: str) -> str:
    """Format guard auto-deactivation notification (100% deterministic)."""
    current_model = _hermes_config_get("model.default") or "desconhecido"
    lines = [
        "🔌 [AUTO-OFF] Modo imbroke desativado automaticamente",
        f"📡 Provider alterado para: {new_provider}",
        f"🔄 Modelo ativo: {current_model}",
        "🧹 Crons de recovery/watchdog removidos",
        "✅ Configuração anterior não restaurada (nova seleção manual detectada)",
    ]
    return "\n".join(lines)


def format_activate_notification(model: RankedModel, previous_provider: str, previous_model: str) -> str:
    """Format activation notification (100% deterministic)."""
    rating = convert_to_10_scale(model.intelligence_index, model.secondary_index)
    source = "fox" if model.benchmarked else model.secondary_source or SECONDARY_SOURCE_NAME
    emoji, status, message = get_warning(rating)
    lines = [
        "🟢 [IMBROKE] Modo imbroke ativado",
        f"💾 Config anterior salva: {previous_provider}/{previous_model}",
        f"🔄 Modelo selecionado: {model.id}",
        f"✅ Classificação: {rating}/10 (baseado em benchmarks globais)",
        f"📊 Fonte: {source}",
        "👁️ Watchdog ativo (verifica provider a cada 5 min)",
        "",
        f"{emoji} {status} {message}",
    ]
    return "\n".join(lines)


def format_deactivate_notification(previous_provider: str, previous_model: str) -> str:
    """Format deactivation notification (100% deterministic)."""
    return "\n".join([
        "🔴 [IMBROKE OFF] Modo imbroke desativado",
        f"🔄 Config restaurada: {previous_provider}/{previous_model}",
        "🧹 Crons de recovery/watchdog removidos",
        "✅ Provider/modelo anterior restaurados",
    ])


def format_status(state: dict[str, Any] | None) -> str:
    """Format status output (100% deterministic)."""
    if state is None or not state.get("active"):
        return "ℹ️ Modo imbroke: INATIVO"
    failed = state.get("failed_models", {})
    lines = [
        "ℹ️ Modo imbroke: ATIVO",
        f"📅 Ativado em: {state.get('activated_at', '?')}",
        f"💾 Config anterior: {state.get('previous_provider', '?')}/{state.get('previous_model', '?')}",
        f"🔄 Modelo atual: {state.get('current_model', '?')}",
        f"📊 Rating atual: {state.get('current_rating', '?')}/10",
    ]
    if failed:
        lines.append(f"❌ Modelos falhos ({len(failed)}):")
        for model_id, info in failed.items():
            lines.append(f"   - {model_id}: {info.get('reason', '?')} (até {info.get('cooldown_until', '?')})")
    else:
        lines.append("✅ Nenhum modelo em estado de falha")
    lines.append(f"🔁 Recovery cron: {state.get('recovery_cron_id') or 'nenhum'}")
    lines.append(f"👁️ Watchdog cron: {state.get('watchdog_cron_id') or 'nenhum'}")
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# High-level operations
# ──────────────────────────────────────────────────────────────────────────────

def _script_path() -> str:
    """Absolute path of this script (for cron prompts)."""
    return str(Path(__file__).resolve())


def _ensure_cron_scripts() -> tuple[str, str]:
    """Create wrapper scripts under ~/.hermes/scripts/ for cron jobs.

    Returns (guard_script_name, recovery_script_name) — just filenames,
    since ``hermes cron create --script`` expects paths relative to
    ``~/.hermes/scripts/``.
    """
    scripts_dir = _hermes_home() / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    router = _script_path()

    guard_name = "imbroke-guard.sh"
    guard_script = scripts_dir / guard_name
    guard_script.write_text(
        f"#!/usr/bin/env bash\npython3 {router} --guard\n",
        encoding="utf-8",
    )
    guard_script.chmod(guard_script.stat().st_mode | 0o755)

    recovery_name = "imbroke-recovery.sh"
    recovery_script = scripts_dir / recovery_name
    recovery_script.write_text(
        f"#!/usr/bin/env bash\npython3 {router} --recover\n",
        encoding="utf-8",
    )
    recovery_script.chmod(recovery_script.stat().st_mode | 0o755)

    return guard_name, recovery_name


def do_activate(args: argparse.Namespace) -> int:
    """Activate imbroke mode."""
    state_path = default_state_path()
    if is_imbroke_active(state_path):
        state = load_imbroke_state(state_path)
        print(format_status(state))
        print("\n⚠️ Modo imbroke já está ativo. Use --deactivate primeiro para resetar.")
        return 0

    # Capture current config
    previous_provider = _hermes_config_get("model.provider") or "unknown"
    previous_model = _hermes_config_get("model.default") or "unknown"
    previous_hint = _hermes_config_get("agent.environment_hint")

    # Capture current fallback_providers for later restoration
    previous_fallback = _get_current_fallback_providers()

    # Build ranking and select best
    payload = build_payload(args)
    ranked = payload["_ranked_models"]
    selected = ranked[0]

    # Apply primary model
    apply_selected_model(selected.id)

    # Configure Hermes native fallback chain with remaining ranked models
    # so Hermes auto-switches on model failure (rate_limit, 503, etc.)
    fallback_chain = [
        {"provider": "openrouter", "model": m.id}
        for m in ranked[1:]  # all ranked models except the selected primary
    ]
    _set_fallback_providers(fallback_chain)

    # Set imbroke environment hint
    rating = convert_to_10_scale(selected.intelligence_index, selected.secondary_index)
    _set_environment_hint(_build_imbroke_hint(selected.id, rating))

    # Create wrapper scripts and schedule watchdog cron
    guard_script, _recovery_script = _ensure_cron_scripts()
    watchdog_id = _hermes_cron_create(
        f"every {WATCHDOG_INTERVAL_MINUTES}m",
        guard_script,
        "imbroke-watchdog",
    )

    # Save sentinel
    state: dict[str, Any] = {
        "active": True,
        "activated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "previous_provider": previous_provider,
        "previous_model": previous_model,
        "previous_fallback_providers": previous_fallback,
        "previous_environment_hint": previous_hint,
        "current_model": selected.id,
        "current_rating": rating,
        "fallback_chain": [m.id for m in ranked[1:]],
        "failed_models": {},
        "recovery_cron_id": None,
        "watchdog_cron_id": watchdog_id,
    }
    save_imbroke_state(state_path, state)

    # Write report
    report_path = Path(args.report_path).expanduser() if args.report_path else default_report_path()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_payload = {k: v for k, v in payload.items() if k != "_ranked_models"}
    report_path.write_text(json.dumps(report_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    n_fb = len(fallback_chain)
    print(format_activate_notification(selected, previous_provider, previous_model))
    if n_fb:
        print(f"🔄 Fallback chain configurada ({n_fb} modelos alternativos)")
    return 0


def do_deactivate(_args: argparse.Namespace) -> int:
    """Deactivate imbroke mode and restore previous config."""
    state_path = default_state_path()
    state = load_imbroke_state(state_path)
    if state is None or not state.get("active"):
        print("ℹ️ Modo imbroke já está inativo.")
        return 0

    previous_provider = state.get("previous_provider", "unknown")
    previous_model = state.get("previous_model", "unknown")
    previous_hint = state.get("previous_environment_hint")

    # Restore previous config
    _hermes_config_set("model.provider", previous_provider)
    _hermes_config_set("model.default", previous_model)
    _set_environment_hint(previous_hint)

    # Restore previous fallback_providers
    previous_fallback = state.get("previous_fallback_providers", [])
    _set_fallback_providers(previous_fallback if isinstance(previous_fallback, list) else [])

    # Cancel crons
    _cancel_all_crons(state)

    # Remove sentinel
    if state_path.is_file():
        state_path.unlink()

    print(format_deactivate_notification(previous_provider, previous_model))
    return 0


def do_status(_args: argparse.Namespace) -> int:
    """Show imbroke status."""
    state_path = default_state_path()
    state = load_imbroke_state(state_path)
    print(format_status(state))
    return 0


def do_mark_failed(args: argparse.Namespace) -> int:
    """Mark a model as failed and failover to the next one."""
    state_path = default_state_path()

    # Guard check first
    if not guard_check(state_path):
        return 1

    state = load_imbroke_state(state_path)
    if state is None or not state.get("active"):
        print("❌ Modo imbroke não está ativo. Use --imbroke --activate primeiro.", file=sys.stderr)
        return 1

    model_id = args.mark_failed
    reason = args.fail_reason
    cooldown = args.cooldown
    now = datetime.now(timezone.utc)
    cooldown_until = (now + timedelta(seconds=cooldown)).isoformat().replace("+00:00", "Z")

    # Register failure
    failed_models = state.setdefault("failed_models", {})
    entry = failed_models.get(model_id, {})
    failed_models[model_id] = {
        "failed_at": now.isoformat().replace("+00:00", "Z"),
        "reason": reason,
        "cooldown_until": cooldown_until,
        "attempts": entry.get("attempts", 0) + 1,
    }

    # Build ranking and select next available
    payload = build_payload(args)
    ranked = payload["_ranked_models"]
    selected = select_with_failover(ranked, failed_models)

    # Apply new model
    apply_selected_model(selected.id)

    # Schedule recovery cron (cancel previous if exists)
    old_recovery = state.get("recovery_cron_id")
    if old_recovery:
        _hermes_cron_remove(old_recovery)
    cooldown_min = max(1, cooldown // 60)
    _guard_script, recovery_script = _ensure_cron_scripts()
    recovery_id = _hermes_cron_create(
        f"{cooldown_min}m",
        recovery_script,
        "imbroke-recovery",
        repeat=1,
    )

    # Update state
    rating = convert_to_10_scale(selected.intelligence_index, selected.secondary_index)
    _set_environment_hint(_build_imbroke_hint(selected.id, rating))
    state["current_model"] = selected.id
    state["current_rating"] = rating
    state["recovery_cron_id"] = recovery_id
    save_imbroke_state(state_path, state)

    # Write report
    report_path = default_report_path()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_payload = {k: v for k, v in payload.items() if k != "_ranked_models"}
    report_path.write_text(json.dumps(report_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(format_failover_notification(model_id, reason, selected, cooldown))
    return 0


def do_recover(args: argparse.Namespace) -> int:
    """Recovery: re-evaluate models after cooldown."""
    state_path = default_state_path()

    # Guard check first
    if not guard_check(state_path):
        return 0  # Guard deactivated imbroke — not an error

    state = load_imbroke_state(state_path)
    if state is None or not state.get("active"):
        return 0

    previous_model = state.get("current_model")

    # Clean expired failures
    cleared = _cleanup_expired_failures(state)
    failed_models = state.get("failed_models", {})
    still_failed = list(failed_models.keys())

    # Re-rank and select best available
    payload = build_payload(args)
    ranked = payload["_ranked_models"]
    selected = select_with_failover(ranked, failed_models)

    model_changed = selected.id != previous_model
    if model_changed:
        apply_selected_model(selected.id)

    # Schedule next recovery if there are still failed models
    old_recovery = state.get("recovery_cron_id")
    if old_recovery:
        _hermes_cron_remove(old_recovery)

    next_recovery_min: int | None = None
    recovery_id: str | None = None
    if still_failed:
        cooldown_min = max(1, args.cooldown // 60)
        next_recovery_min = cooldown_min
        _guard_script, recovery_script = _ensure_cron_scripts()
        recovery_id = _hermes_cron_create(
            f"{cooldown_min}m",
            recovery_script,
            "imbroke-recovery",
            repeat=1,
        )

    # Update state
    rating = convert_to_10_scale(selected.intelligence_index, selected.secondary_index)
    _set_environment_hint(_build_imbroke_hint(selected.id, rating))
    state["current_model"] = selected.id
    state["current_rating"] = rating
    state["recovery_cron_id"] = recovery_id
    save_imbroke_state(state_path, state)

    restored = model_changed and selected.id != previous_model
    print(format_recovery_notification(selected, restored, still_failed, next_recovery_min))
    return 0


def do_guard(_args: argparse.Namespace) -> int:
    """Guard check — called by watchdog cron."""
    state_path = default_state_path()
    state = load_imbroke_state(state_path)

    if state is None or not state.get("active"):
        # Imbroke not active — self-remove watchdog if possible
        watchdog_id = (state or {}).get("watchdog_cron_id")
        if watchdog_id:
            _hermes_cron_remove(watchdog_id)
        return 0

    if not guard_check(state_path):
        # Guard deactivated imbroke — notification already printed
        return 0

    return 0


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    openrouter_payload = load_json_source(args.openrouter_models_source)
    if args.fox_metrics_source:
        benchmark_name = Path(args.fox_metrics_source).name
        fox_metrics = load_json_source(args.fox_metrics_source)
    else:
        benchmark_name, fox_metrics = discover_latest_fox_metrics(args.fox_metrics_index_url)

    ranked = rank_models(openrouter_payload, fox_metrics, benchmark_name)
    if not ranked:
        raise RuntimeError("Nenhum modelo gratuito elegível foi encontrado no catálogo do OpenRouter.")

    # Check circuit breaker for model selection
    state_path = default_state_path()
    state = load_imbroke_state(state_path)
    failed_models = (state or {}).get("failed_models", {})
    selected = select_with_failover(ranked, failed_models) if failed_models else ranked[0]

    payload: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "mode": "imbroke" if args.imbroke else "report-only",
        "openrouter_models_source": args.openrouter_models_source,
        "fox_metrics_source": args.fox_metrics_source or benchmark_name,
        "secondary_source": SECONDARY_SOURCE_NAME,
        "selection_basis": {
            "free_rule": "pricing.prompt == 0 and pricing.completion == 0",
            "ranking_rule": (
                "benchmarked first; fox intelligence_index desc; then composite_score desc; "
                "unbenchmarked models sorted by OpenRouter secondary_index desc, then context_length desc"
            ),
            "intelligence_index_formula": "0.50*pass_rate + 0.20*multi_step_tool + 0.15*delegation_reasoning + 0.10*reasoning + 0.05*failure_mode",
            "secondary_index_formula": "keyword(description)+context_length+recency+top_provider.max_completion_tokens-multimodal_penalty",
            "activation": "non-default; apply path requires --imbroke",
        },
        "selected_model": selected.to_dict(),
        "fallback_chain": [item.id for item in ranked],
        "ranked_free_models": [item.to_dict() for item in ranked],
        "benchmarked_count": sum(1 for item in ranked if item.benchmarked),
        "unbenchmarked_count": sum(1 for item in ranked if not item.benchmarked),
        # Internal: not serialized in report but used by do_activate/do_mark_failed
        "_ranked_models": ranked,
    }
    return payload


def format_text(payload: dict[str, Any]) -> str:
    lines = ["OpenRouter free model router", ""]
    selected = payload["selected_model"]
    lines.append(f"Modo: {payload['mode']}")
    lines.append(f"Selecionado: {selected['id']}")
    lines.append(f"Intelligence index: {selected['intelligence_index']}")
    lines.append(f"Secondary index: {selected['secondary_index']}")
    lines.append(f"Benchmark primário: {payload['fox_metrics_source']}")
    lines.append(f"Cobertura secundária: {payload['secondary_source']}")
    lines.append("")
    
    # Adiciona classificação 1-10 e warning
    rating = convert_to_10_scale(selected['intelligence_index'], selected['secondary_index'])
    source = "fox" if selected['benchmarked'] else selected.get('secondary_source', SECONDARY_SOURCE_NAME)
    emoji, status, message = get_warning(rating)
    
    lines.append(f"Classificação: {rating}/10")
    lines.append(f"Fonte: {source}")
    lines.append(f"{emoji} {status} {message}")
    lines.append("")
    
    lines.append("Fallback chain:")
    for idx, item in enumerate(payload["ranked_free_models"], start=1):
        source = "fox" if item["benchmarked"] else item.get("secondary_source", SECONDARY_SOURCE_NAME)
        item_rating = convert_to_10_scale(item['intelligence_index'], item['secondary_index'])
        lines.append(
            f"{idx}. {item['id']} | rating={item_rating}/10 | intelligence={item['intelligence_index']} | secondary={item['secondary_index']} | pass_rate={item['pass_rate']} | context={item['context_length']} | {source}"
        )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()

    # Circuit breaker commands (no ranking needed)
    if args.status:
        return do_status(args)
    if args.deactivate:
        return do_deactivate(args)
    if args.guard:
        return do_guard(args)

    # Commands that need ranking
    if args.activate:
        return do_activate(args)
    if args.mark_failed:
        return do_mark_failed(args)
    if args.recover:
        return do_recover(args)

    # Legacy flow (ranking + optional apply)
    payload = build_payload(args)

    if args.apply:
        apply_selected_model(payload["selected_model"]["id"])

    report_path = Path(args.report_path).expanduser() if args.report_path else (default_report_path() if args.apply else None)
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_payload = {k: v for k, v in payload.items() if k != "_ranked_models"}
        report_path.write_text(json.dumps(report_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.format == "json":
        output = {k: v for k, v in payload.items() if k != "_ranked_models"}
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(format_text(payload))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
