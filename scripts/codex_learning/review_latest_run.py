#!/usr/bin/env python3
"""Review the latest Codex learning run and emit a markdown summary."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import os


def hermes_home() -> Path:
    raw = os.environ.get("HERMES_HOME", "").strip()
    return Path(raw).expanduser() if raw else Path.home() / ".hermes"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Review a Codex learning run summary.")
    parser.add_argument("--run-id", help="Run id específico; por default usa o mais recente.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    hh = hermes_home()
    runs_dir = hh / "codex-learning" / "runs"
    reviews_dir = hh / "codex-learning" / "reviews"
    reviews_dir.mkdir(parents=True, exist_ok=True)

    if args.run_id:
        summary_path = runs_dir / f"{args.run_id}.summary.json"
    else:
        candidates = sorted(runs_dir.glob("*.summary.json"))
        if not candidates:
            raise SystemExit("Nenhum run encontrado em ~/.hermes/codex-learning/runs/")
        summary_path = candidates[-1]

    if not summary_path.is_file():
        raise SystemExit(f"Run não encontrado: {summary_path}")

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    run_id = payload["run_id"]
    changed = payload.get("changed_files") or []
    changed_md = "\n".join(f"- {item}" for item in changed) if changed else "- Nenhum arquivo alterado"
    stdout = (payload.get("stdout") or "").strip() or "<vazio>"
    stderr = (payload.get("stderr") or "").strip() or "<vazio>"
    review_text = f"""# Codex Learning Review — {run_id}

- Timestamp UTC: {payload.get('timestamp_utc')}
- Workdir: `{payload.get('workdir')}`
- Sandbox: `{payload.get('sandbox')}`
- Exit code: `{payload.get('exit_code')}`

## Changed files
{changed_md}

## Prompt
```text
{payload.get('prompt', '')}
```

## Stdout
```text
{stdout}
```

## Stderr
```text
{stderr}
```

## Git evidence
```text
{payload.get('git_status_porcelain', '').strip() or '<sem mudanças>'}
```
"""
    review_path = reviews_dir / f"{run_id}.review.md"
    review_path.write_text(review_text, encoding="utf-8")
    print(json.dumps({"run_id": run_id, "review_path": str(review_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
