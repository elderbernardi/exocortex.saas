"""Despachante de cadência: decide quais áreas macro rodam agora."""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

_UNIT = {"h": 3600, "d": 86400}
_NAMED = {"daily": 86400, "weekly": 604800}


def cadence_seconds(cadence: str) -> int:
    if cadence in _NAMED:
        return _NAMED[cadence]
    m = re.fullmatch(r"(\d+)([hd])", cadence.strip())
    if not m:
        raise ValueError(f"cadence inválida: {cadence!r}")
    return int(m.group(1)) * _UNIT[m.group(2)]


def due_areas(areas: list[dict], state: dict, now_epoch: int) -> list[str]:
    due = []
    for area in areas:
        last = state.get(area["slug"])
        if last is None or (now_epoch - int(last)) >= cadence_seconds(area["cadence"]):
            due.append(area["slug"])
    return due


def mark_run(state: dict, slug: str, now_epoch: int) -> dict:
    state = dict(state)
    state[slug] = int(now_epoch)
    return state


def _load_state(path: str) -> dict:
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="News cadence dispatcher")
    ap.add_argument("--config", required=True)
    ap.add_argument("--state", required=True)
    ap.add_argument("--now", type=int, required=True, help="epoch seconds")
    ap.add_argument("--mark", help="slug to mark as run (writes state)")
    args = ap.parse_args(argv)

    sys.path.insert(0, str(Path(__file__).parent))
    from news_config import load_config  # noqa: E402

    state = _load_state(args.state)
    if args.mark:
        state = mark_run(state, args.mark, args.now)
        Path(args.state).write_text(json.dumps(state, indent=1), encoding="utf-8")
        print(f"marked {args.mark}={args.now}")
        return 0
    cfg = load_config(args.config)
    for slug in due_areas(cfg["areas"], state, args.now):
        print(slug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
