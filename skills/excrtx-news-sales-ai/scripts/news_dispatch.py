"""Despachante de cadência: decide áreas macro vencidas e marca só receipts completos."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

_UNIT = {"h": 3600, "d": 86400}
_NAMED = {"daily": 86400, "weekly": 604800}
_SCHEMA = "exocortex/news-cadence/v1"


def cadence_seconds(cadence: str) -> int:
    if cadence in _NAMED:
        return _NAMED[cadence]
    match = re.fullmatch(r"(\d+)([hd])", cadence.strip())
    if not match:
        raise ValueError(f"cadence inválida: {cadence!r}")
    return int(match.group(1)) * _UNIT[match.group(2)]


def _area_state(state: dict, slug: str) -> dict | None:
    areas = state.get("areas")
    if isinstance(areas, dict):
        value = areas.get(slug)
        return value if isinstance(value, dict) else None
    legacy = state.get(slug)
    return {"last_success_at": legacy, "last_run_id": None} if legacy is not None else None


def due_areas(areas: list[dict], state: dict, now_epoch: int) -> list[str]:
    due = []
    for area in areas:
        entry = _area_state(state, area["slug"])
        last = entry.get("last_success_at") if entry else None
        if last is None or (now_epoch - int(last)) >= cadence_seconds(area["cadence"]):
            due.append(area["slug"])
    return due


def mark_run(state: dict, slug: str, now_epoch: int, run_id: str, receipt_status: str) -> dict:
    if receipt_status != "success":
        raise ValueError("cadence may be marked only after receipt status success")
    current_areas = state.get("areas") if isinstance(state.get("areas"), dict) else None
    if current_areas is None:
        current_areas = {
            key: {"last_success_at": value, "last_run_id": None}
            for key, value in state.items()
            if key != "schema" and isinstance(value, (int, float))
        }
    areas = {key: dict(value) for key, value in current_areas.items() if isinstance(value, dict)}
    areas[slug] = {"last_success_at": int(now_epoch), "last_run_id": run_id}
    return {"schema": _SCHEMA, "areas": areas}


def _load_state(path: str) -> dict:
    file = Path(path)
    return json.loads(file.read_text(encoding="utf-8")) if file.exists() else {"schema": _SCHEMA, "areas": {}}


def _write_state(path: str, state: dict) -> None:
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    temporary = file.with_suffix(file.suffix + ".tmp")
    temporary.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, file)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="News cadence dispatcher")
    parser.add_argument("--config", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--now", type=int, required=True, help="epoch seconds")
    parser.add_argument("--mark", help="area slug to mark after a successful receipt")
    parser.add_argument("--run-id", help="DataBrain run UUID required with --mark")
    parser.add_argument("--receipt-status", choices=["success", "partial", "failed", "skipped"], help="final DataBrain receipt status")
    args = parser.parse_args(argv)

    sys.path.insert(0, str(Path(__file__).parent))
    from news_config import load_config  # noqa: E402

    state = _load_state(args.state)
    if args.mark:
        if not args.run_id or not args.receipt_status:
            parser.error("--mark requires --run-id and --receipt-status")
        marked = mark_run(state, args.mark, args.now, args.run_id, args.receipt_status)
        _write_state(args.state, marked)
        print(f"marked {args.mark}={args.now} run_id={args.run_id}")
        return 0

    config = load_config(args.config)
    for slug in due_areas(config["areas"], state, args.now):
        print(slug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
