#!/usr/bin/env python3
"""Adaptador mínimo DocBrain → Acervo.

Recebe um arquivo local, resolve um workspace DocBrain válido via `api health`,
executa `api parse create`, renderiza markdown estruturado com provenance e grava
em `acervo/micro/{slug}/knowledge/`.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DOCBRAIN_SIBLING = REPO_ROOT.parent / "docbrain"
DEFAULT_MANAGED_DOCBRAIN = Path(os.environ.get("EXOCORTEX_HOME", str(Path.home() / "exocortex"))) / "tools" / "docbrain"
VALIDATOR = REPO_ROOT / "scripts" / "validate_frontmatter.py"


def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_only).strip("-").lower()
    return slug or "documento"


def quote_table_cell(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\n", " ").replace("|", "\\|").strip()
    return text or "—"


def render_markdown_table(table: dict[str, Any]) -> str:
    columns = [str(col) for col in table.get("columns") or []]
    rows = table.get("rows") or []
    if not columns and rows:
        first = rows[0]
        if isinstance(first, dict):
            columns = [str(k) for k in first.keys()]
    if not columns:
        return "_Tabela sem colunas reconhecidas._"

    header = "| " + " | ".join(quote_table_cell(col) for col in columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    body = []
    for row in rows:
        if isinstance(row, dict):
            values = [quote_table_cell(row.get(col)) for col in columns]
        else:
            values = [quote_table_cell(row)] + ["—"] * (len(columns) - 1)
        body.append("| " + " | ".join(values) + " |")
    if not body:
        body.append("| " + " | ".join("—" for _ in columns) + " |")
    return "\n".join([header, sep, *body])


def relative_to_acervo(path: Path, acervo_root: Path) -> str:
    return path.resolve().relative_to(acervo_root.resolve()).as_posix()


def run_json_command(args: list[str], cwd: Path) -> dict[str, Any]:
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Comando falhou ({result.returncode}): {' '.join(args)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Saída não é JSON válido para {' '.join(args)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        ) from exc


def resolve_docbrain_dir(explicit: str | None) -> tuple[Path, dict[str, Any]]:
    seen: set[str] = set()
    candidates: list[Path] = []

    def add(path: Path | None) -> None:
        if not path:
            return
        key = str(path.expanduser())
        if key in seen:
            return
        seen.add(key)
        candidates.append(path.expanduser())

    if explicit:
        add(Path(explicit))
    if env_dir := os.environ.get("EXOCORTEX_DOCBRAIN_DIR"):
        add(Path(env_dir))
    add(DEFAULT_DOCBRAIN_SIBLING)
    add(DEFAULT_MANAGED_DOCBRAIN)

    failures: list[str] = []
    for candidate in candidates:
        if not candidate.exists():
            failures.append(f"missing:{candidate}")
            continue
        try:
            payload = run_json_command(
                ["npm", "run", "--silent", "cli", "--", "api", "health", "--output", "json"],
                cwd=candidate,
            )
        except Exception as exc:  # pragma: no cover - surfaced in error aggregation
            failures.append(f"invalid:{candidate}: {exc}")
            continue
        if payload.get("ok") is True and payload.get("api_version") == "docbrain.cli.v1":
            return candidate.resolve(), payload
        failures.append(f"invalid:{candidate}: {payload}")

    joined = "\n- ".join(failures) if failures else "(sem candidatos)"
    raise RuntimeError(f"Nenhum workspace DocBrain válido encontrado.\n- {joined}")


def call_docbrain_parse(docbrain_dir: Path, input_path: Path) -> dict[str, Any]:
    return run_json_command(
        [
            "npm",
            "run",
            "--silent",
            "cli",
            "--",
            "api",
            "parse",
            "create",
            "--input",
            str(input_path.resolve()),
            "--include",
            "tables,sections",
            "--output",
            "json",
        ],
        cwd=docbrain_dir,
    )


def build_frontmatter(payload: dict[str, Any], input_path: Path, title: str, description: str, tags: list[str], ts: datetime) -> dict[str, Any]:
    data = payload["data"]
    document = data.get("document", {})
    job = payload.get("job", {})
    return {
        "type": "knowledge",
        "title": title,
        "description": description,
        "tags": tags,
        "timestamp": ts.strftime("%Y-%m-%d"),
        "class": "volátil",
        "created_at": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "created": ts.strftime("%Y-%m-%d"),
        "updated": ts.strftime("%Y-%m-%d"),
        "nature": "knowledge",
        "excrtx_type": "fact",
        "confidence": "medium",
        "sources": [str(input_path.resolve())],
        "docbrain_document_id": data.get("document_id"),
        "docbrain_job_id": job.get("job_id"),
        "docbrain_request_id": payload.get("request_id"),
        "docbrain_extractor": document.get("extractor"),
    }


def render_markdown(payload: dict[str, Any], input_path: Path, ts: datetime) -> tuple[str, str]:
    data = payload["data"]
    document = data.get("document", {})
    sections = data.get("sections") or []
    tables = data.get("tables") or []

    base_title = Path(document.get("filename") or input_path.name).stem.replace("_", " ").strip()
    title = base_title or input_path.stem
    description = f"Ingestão DocBrain de {input_path.name} para promoção ao Acervo."
    tags = ["docbrain", "acervo", "ingest", slugify(input_path.stem)]
    frontmatter = build_frontmatter(payload, input_path, title, description, tags, ts)

    body: list[str] = [
        f"# {title}",
        "",
        "> Documento estruturado pelo adaptador DocBrain → Acervo.",
        "",
        "## Provenance",
        "",
        f"- Arquivo de origem: `{input_path.resolve()}`",
        f"- document_id: `{data.get('document_id')}`",
        f"- job_id: `{payload.get('job', {}).get('job_id')}`",
        f"- extractor: `{document.get('extractor')}`",
        f"- gerado_em: `{ts.strftime('%Y-%m-%dT%H:%M:%SZ')}`",
        "",
        "## Resumo do parse",
        "",
        f"- Seções extraídas: **{len(sections)}**",
        f"- Tabelas extraídas: **{len(tables)}**",
        f"- Extensão: `{document.get('extension')}`",
        f"- Tamanho: `{document.get('size_bytes')}` bytes",
        "",
    ]

    if sections:
        body.extend(["## Seções", ""])
        for idx, section in enumerate(sections, start=1):
            title_text = section.get("title") or section.get("id") or f"Seção {idx}"
            body.extend([f"### {title_text}", "", (section.get("text") or "").strip() or "_Sem texto extraído._", ""])

    if tables:
        body.extend(["## Tabelas", ""])
        for idx, table in enumerate(tables, start=1):
            title_text = table.get("source") or table.get("id") or f"Tabela {idx}"
            body.extend([
                f"### {title_text}",
                "",
                f"- row_count: `{table.get('row_count')}`",
                "",
                render_markdown_table(table),
                "",
            ])

    markdown = "---\n" + yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip() + "\n---\n\n" + "\n".join(body).rstrip() + "\n"
    return markdown, title


def ensure_microverso_structure(acervo_root: Path, microverso: str) -> tuple[Path, Path, Path]:
    micro_root = acervo_root / "micro" / microverso
    knowledge_dir = micro_root / "knowledge"
    meta_dir = micro_root / "_meta"
    index_path = meta_dir / "index.md"
    log_path = meta_dir / "log.md"

    if not micro_root.exists():
        raise RuntimeError(f"Microverso inexistente: {micro_root}")
    knowledge_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)
    if not index_path.exists():
        raise RuntimeError(f"Índice ausente: {index_path}")
    if not log_path.exists():
        raise RuntimeError(f"Log ausente: {log_path}")
    return knowledge_dir, index_path, log_path


def guard_write(target_path: Path, acervo_root: Path, microverso: str) -> None:
    guard_script = REPO_ROOT / "scripts" / "exocortex_runtime_guard.py"
    result = subprocess.run(
        [
            sys.executable,
            str(guard_script),
            "guard-write",
            "--path",
            str(target_path),
            "--active-microverso",
            microverso,
            "--acervo-root",
            str(acervo_root),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stdout or result.stderr or "guard-write falhou")
    payload = json.loads(result.stdout)
    if payload.get("allowed") is not True:
        raise RuntimeError(payload.get("message") or str(payload))


def update_index(index_path: Path, relative_output: str) -> None:
    content = index_path.read_text(encoding="utf-8")
    bullet = f"- `{relative_output}`"
    if bullet in content:
        return

    if "### Knowledge" in content:
        pattern = r"(### Knowledge\n)"
        content, count = re.subn(pattern, r"\1" + bullet + "\n", content, count=1)
        if count:
            index_path.write_text(content, encoding="utf-8")
            return

    separator = "\n" if content.endswith("\n") else "\n\n"
    content += f"{separator}### Knowledge\n{bullet}\n"
    index_path.write_text(content, encoding="utf-8")


def append_log(log_path: Path, relative_output: str, input_path: Path, ts: datetime) -> None:
    date = ts.strftime("%Y-%m-%d")
    entry = f"- CREATED: {relative_output} (volátil) — ingestão DocBrain de {input_path.name}"
    content = log_path.read_text(encoding="utf-8")
    if entry in content:
        return

    heading = f"## {date}"
    if heading in content:
        content = content.rstrip() + "\n" + entry + "\n"
    else:
        suffix = "\n" if content.endswith("\n") else "\n\n"
        content = content + suffix + heading + "\n" + entry + "\n"
    log_path.write_text(content, encoding="utf-8")


def validate_frontmatter(path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--file", str(path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Frontmatter inválido para {path}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")


def command(args: argparse.Namespace) -> dict[str, Any]:
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise RuntimeError(f"Arquivo de entrada não encontrado: {input_path}")

    acervo_root = Path(args.acervo_root).expanduser().resolve()
    ts = now_utc()
    docbrain_dir, health = resolve_docbrain_dir(args.docbrain_dir)
    payload = call_docbrain_parse(docbrain_dir, input_path)
    if payload.get("ok") is not True or payload.get("api_version") != "docbrain.cli.v1":
        raise RuntimeError(f"Parse DocBrain inválido: {payload}")

    markdown, title = render_markdown(payload, input_path, ts)
    knowledge_dir, index_path, log_path = ensure_microverso_structure(acervo_root, args.microverso)
    filename = slugify(args.output_name or input_path.stem) + ".md"
    output_path = knowledge_dir / filename
    guard_write(output_path, acervo_root=acervo_root, microverso=args.microverso)
    output_path.write_text(markdown, encoding="utf-8")
    validate_frontmatter(output_path)

    relative_output = relative_to_acervo(output_path, acervo_root)
    update_index(index_path, relative_output)
    append_log(log_path, relative_output, input_path, ts)

    data = payload["data"]
    return {
        "ok": True,
        "docbrain_dir": str(docbrain_dir),
        "health": health,
        "output_file": str(output_path),
        "relative_output": relative_output,
        "title": title,
        "document_id": data.get("document_id"),
        "job_id": payload.get("job", {}).get("job_id"),
        "sections": len(data.get("sections") or []),
        "tables": len(data.get("tables") or []),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Adaptador mínimo DocBrain → Acervo")
    parser.add_argument("--input", required=True, help="Arquivo local a processar")
    parser.add_argument("--microverso", required=True, help="Slug do microverso de destino")
    parser.add_argument("--acervo-root", required=True, help="Raiz do Acervo")
    parser.add_argument("--docbrain-dir", help="Workspace DocBrain explícito")
    parser.add_argument("--output-name", help="Slug base do arquivo de saída (sem .md)")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = command(args)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
