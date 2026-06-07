#!/usr/bin/env python3
"""Rank free OpenRouter models with a deterministic fallback chain.

Primary signal:
- fox-in-the-box-ai/hermes-best-models benchmark

Secondary coverage signal for models not present in fox:
- OpenRouter catalog metadata (description, context, recency, top-provider limits)

This router is intentionally *not* a default mode. It becomes actionable only
when the caller opts into emergency mode via ``--imbroke``. In that mode the
script may also apply the selected model to Hermes config with ``--apply``.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

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
    args = parser.parse_args()
    if args.apply and not args.imbroke:
        parser.error("--apply exige --imbroke. O roteador não é modo default.")
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


def default_report_path() -> Path:
    hermes_home = Path(Path.home(), ".hermes")
    env_home = Path(Path.cwd())
    if os.environ.get("HERMES_HOME"):
        hermes_home = Path(os.environ["HERMES_HOME"]).expanduser()
    elif env_home.name == ".hermes":
        hermes_home = env_home
    return hermes_home / "model-routing" / "openrouter-free-models.json"


def apply_selected_model(model_id: str) -> None:
    commands = [
        ["hermes", "config", "set", "model.provider", "openrouter"],
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

    selected = ranked[0]
    return {
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
    }


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
    payload = build_payload(args)

    if args.apply:
        apply_selected_model(payload["selected_model"]["id"])

    report_path = Path(args.report_path).expanduser() if args.report_path else (default_report_path() if args.apply else None)
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(format_text(payload))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
