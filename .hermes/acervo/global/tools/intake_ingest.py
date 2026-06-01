#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import textwrap
import zipfile
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

try:
    from pypdf import PdfReader  # type: ignore
except Exception:
    PdfReader = None

try:
    from PIL import Image  # type: ignore
except Exception:
    Image = None

ALLOWED_TARGET_DIRS = {
    "context": ("contexto", "context"),
    "knowledge": ("conhecimento", "fact"),
    "contracts": ("instrucoes", "contract"),
    "prompts": ("processos", "prompt"),
    "skills": ("processos", "skill"),
    "workflows": ("processos", "workflow"),
    "tools": ("ferramentas", "tool"),
    "templates": ("processos", "template"),
    "decisions": ("conhecimento", "decision"),
    "reflections": ("reflexoes", "lesson"),
    "persona": ("persona", "profile"),
}

MICRO_KEYWORDS = [
    ("hermes-setup", ["hermes", "gateway", "mcp", "skill", "acervo", "setup", "dashboard", "profile", "bundle"]),
    ("ensino", ["ensino", "disciplina", "aula", "aluno", "avalia", "plano de ensino", "programação", "sistemas distribuídos", "serviços web"]),
    ("gabinete", ["gabinete", "ofício", "oficio", "memorando", "portaria", "campus", "reitoria", "direção", "diretor"]),
    ("dev", ["repo", "commit", "pull request", "frontend", "backend", "api", "bug", "feature", "deploy", "docker", "kubernetes"]),
    ("pesquisa-ia", ["paper", "artigo", "pesquisa", "arxiv", "llm", "modelo", "benchmark", "dataset"]),
]


def hermes_home() -> Path:
    return Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")).expanduser()


def acervo_root() -> Path:
    return hermes_home() / "acervo"


def inbox_root() -> Path:
    return acervo_root() / "_inbox"


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def today() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d")


def slugify(value: str, fallback: str = "intake") -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or fallback


def intake_id(title: str) -> str:
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"int_{stamp}_{slugify(title)[:48]}"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def append_log(intake_dir: Path, action: str, detail: dict[str, Any]) -> None:
    log_path = intake_dir / "log.json"
    log = read_json(log_path, [])
    log.append({"at": now_iso(), "action": action, "detail": detail})
    write_json(log_path, log)


def ensure_intake_dir(intake_dir: Path) -> None:
    (intake_dir / "original").mkdir(parents=True, exist_ok=True)
    (intake_dir / "derived").mkdir(parents=True, exist_ok=True)


def rel_to_acervo(path: Path) -> str:
    try:
        return path.relative_to(acervo_root()).as_posix()
    except Exception:
        return path.as_posix()


def read_text_file(path: Path) -> str:
    for encoding in ("utf-8", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except Exception:
            continue
    return path.read_text(errors="ignore")


def run_capture(cmd: list[str]) -> tuple[bool, str]:
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    except FileNotFoundError:
        return False, ""
    if proc.returncode != 0:
        return False, proc.stderr.strip() or proc.stdout.strip()
    return True, proc.stdout


def guess_content_type(path: Path | None, mime_type: str, explicit: str | None = None) -> str:
    if explicit:
        return explicit
    suffix = (path.suffix.lower() if path else "")
    if suffix == ".zip":
        return "zip"
    if suffix in {".md", ".txt", ".json", ".csv", ".xml", ".yaml", ".yml", ".html", ".htm"}:
        return "text"
    if suffix == ".pdf":
        return "document"
    if mime_type.startswith("image/"):
        return "image"
    if mime_type.startswith("audio/"):
        return "audio"
    if mime_type.startswith("video/"):
        return "video"
    if mime_type.startswith("text/"):
        return "text"
    if "officedocument" in mime_type or mime_type in {
        "application/msword",
        "application/vnd.oasis.opendocument.text",
        "application/vnd.ms-excel",
    }:
        return "document"
    return "document"


def create_from_args(args: argparse.Namespace) -> tuple[Path, dict[str, Any]]:
    inbox_root().mkdir(parents=True, exist_ok=True)
    title_base = args.title or (Path(args.input).stem if getattr(args, "input", None) else None) or (urlparse(args.link).netloc if getattr(args, "link", None) else None) or "intake"
    iid = args.intake_id or intake_id(title_base)
    intake_dir = inbox_root() / iid
    ensure_intake_dir(intake_dir)

    original_filename = None
    original_path = None
    mime_type = "text/plain"
    size = None
    original_hash = None

    if getattr(args, "input", None):
        src = Path(args.input).expanduser().resolve()
        if not src.exists():
            raise FileNotFoundError(src)
        original_filename = src.name
        original_path = intake_dir / "original" / src.name
        shutil.copy2(src, original_path)
        mime_type = mimetypes.guess_type(str(src))[0] or "application/octet-stream"
        size = original_path.stat().st_size
        original_hash = sha256(original_path)
    elif getattr(args, "link", None):
        original_filename = "link.txt"
        original_path = intake_dir / "original" / original_filename
        original_path.write_text(args.link.strip() + "\n", encoding="utf-8")
        mime_type = "text/uri-list"
        size = original_path.stat().st_size
        original_hash = sha256(original_path)
    elif getattr(args, "text", None):
        original_filename = "note.txt"
        original_path = intake_dir / "original" / original_filename
        original_path.write_text(args.text, encoding="utf-8")
        mime_type = "text/plain"
        size = original_path.stat().st_size
        original_hash = sha256(original_path)
    else:
        raise ValueError("one of --input, --link, or --text is required")

    ctype = guess_content_type(original_path, mime_type, getattr(args, "content_type", None))
    envelope = {
        "intake_id": iid,
        "channel": args.channel,
        "received_at": now_iso(),
        "content_type": ctype,
        "original_filename": original_filename,
        "mime_type": mime_type,
        "local_cached_path": rel_to_acervo(original_path),
        "user_caption": args.caption or "",
        "correlation_id": args.correlation_id,
        "session_ref": args.session_ref,
        "microverso_hint": args.microverso_hint,
    }
    manifest = {
        "intake_id": iid,
        "title": args.title or title_base,
        "status": "received",
        "envelope": envelope,
        "original": {
            "path": rel_to_acervo(original_path),
            "filename": original_filename,
            "mime_type": mime_type,
            "size": size,
            "sha256": original_hash,
        },
        "derived": {"files": []},
        "triage": None,
        "promotion": {"status": "not_promoted"},
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    write_json(intake_dir / "manifest.json", manifest)
    append_log(intake_dir, "received", {"title": manifest["title"], "content_type": ctype})
    return intake_dir, manifest


def preview_file(original_path: Path) -> dict[str, Any]:
    preview = {
        "path": original_path.name,
        "suffix": original_path.suffix.lower(),
        "size": original_path.stat().st_size,
    }
    if Image and original_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}:
        try:
            img = Image.open(original_path)
            preview["image"] = {"width": img.width, "height": img.height, "mode": img.mode}
        except Exception as exc:
            preview["image_error"] = str(exc)
    return preview


def write_markdown(path: Path, title: str, body: str) -> None:
    path.write_text(f"# {title}\n\n{body.strip()}\n", encoding="utf-8")


def extract_pdf(original_path: Path, derived_dir: Path) -> tuple[str, dict[str, Any]]:
    meta = {"extractor": None, "pages": None, "notes": []}
    text = ""
    if PdfReader is not None:
        try:
            reader = PdfReader(str(original_path))
            meta["pages"] = len(reader.pages)
            chunks = []
            for page in reader.pages:
                chunks.append(page.extract_text() or "")
            text = "\n\n".join(chunks).strip()
            meta["extractor"] = "pypdf"
        except Exception as exc:
            meta["notes"].append(f"pypdf_failed: {exc}")
    if len(text) < 120:
        ok, out = run_capture(["pdftotext", "-layout", "-nopgbrk", str(original_path), "-"])
        if ok and out.strip():
            text = out.strip()
            meta["extractor"] = "pdftotext"
        elif out:
            meta["notes"].append(f"pdftotext_failed: {out}")
    if text:
        write_markdown(derived_dir / "extracted.md", "Extracted Text", text)
    return text, meta


def extract_image(original_path: Path, derived_dir: Path) -> tuple[str, dict[str, Any]]:
    meta = preview_file(original_path)
    ok, out = run_capture(["tesseract", str(original_path), "stdout"])
    if ok and out.strip():
        text = out.strip()
        write_markdown(derived_dir / "ocr.md", "OCR", text)
        meta["ocr_extractor"] = "tesseract"
        return text, meta
    meta["ocr_error"] = out or "tesseract unavailable"
    return "", meta


def extract_zip(original_path: Path, derived_dir: Path) -> tuple[str, dict[str, Any]]:
    meta = {"entries": []}
    with zipfile.ZipFile(original_path) as zf:
        for info in zf.infolist():
            meta["entries"].append({
                "name": info.filename,
                "size": info.file_size,
                "compressed_size": info.compress_size,
                "is_dir": info.is_dir(),
            })
    inventory = "\n".join(f"- {e['name']} ({e['size']} bytes)" for e in meta["entries"][:500])
    write_markdown(derived_dir / "extracted.md", "ZIP Inventory", inventory or "Arquivo ZIP vazio.")
    return inventory, meta


def extract_textlike(original_path: Path, derived_dir: Path) -> tuple[str, dict[str, Any]]:
    text = read_text_file(original_path)
    write_markdown(derived_dir / "extracted.md", "Extracted Text", text)
    return text, {"extractor": "direct-read"}


def extract_av(original_path: Path, derived_dir: Path) -> tuple[str, dict[str, Any]]:
    ok, out = run_capture(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(original_path)])
    meta = json.loads(out) if ok and out.strip() else {"ffprobe_error": out or "ffprobe unavailable"}
    write_markdown(derived_dir / "transcript.md", "Transcript Placeholder", "Transcrição não gerada automaticamente neste MVP. Os metadados foram preservados em `preview.json`.")
    return "", meta


def extract_link(original_path: Path, derived_dir: Path) -> tuple[str, dict[str, Any]]:
    url = read_text_file(original_path).strip()
    parsed = urlparse(url)
    summary = f"URL recebida: {url}\n\nDomínio: {parsed.netloc or '(desconhecido)'}\nCaminho: {parsed.path or '/'}"
    write_markdown(derived_dir / "extracted.md", "Link Snapshot", summary)
    return summary, {"domain": parsed.netloc, "path": parsed.path}


def extract_for_manifest(manifest: dict[str, Any], intake_dir: Path) -> tuple[str, dict[str, Any], list[str]]:
    original_path = acervo_root() / manifest["original"]["path"]
    derived_dir = intake_dir / "derived"
    preview = preview_file(original_path)
    text = ""
    meta = {}
    ctype = manifest["envelope"]["content_type"]
    if ctype == "text":
        text, meta = extract_textlike(original_path, derived_dir)
    elif ctype == "document" and original_path.suffix.lower() == ".pdf":
        text, meta = extract_pdf(original_path, derived_dir)
    elif ctype == "image":
        text, meta = extract_image(original_path, derived_dir)
    elif ctype == "zip":
        text, meta = extract_zip(original_path, derived_dir)
    elif ctype in {"audio", "video"}:
        text, meta = extract_av(original_path, derived_dir)
    elif ctype == "link":
        text, meta = extract_link(original_path, derived_dir)
    else:
        text, meta = extract_textlike(original_path, derived_dir)
    preview["extraction"] = meta
    write_json(derived_dir / "preview.json", preview)
    files = []
    for p in sorted(derived_dir.iterdir()):
        if p.is_file():
            files.append(rel_to_acervo(p))
    return text, preview, files


def choose_microverso(text: str, filename: str, hint: str | None) -> tuple[str | None, list[str]]:
    reasons = []
    if hint:
        reasons.append(f"microverso_hint:{hint}")
        return hint, reasons
    hay = f"{filename} {text}".lower()
    for micro, keywords in MICRO_KEYWORDS:
        score = sum(1 for kw in keywords if kw in hay)
        if score > 0:
            reasons.append(f"{micro}:{score}")
            return micro, reasons
    return None, reasons


def choose_target(text: str, content_type: str) -> tuple[str, str, str, list[str]]:
    hay = text.lower()
    reasons = []
    if any(k in hay for k in ["contrato", "edital", "ofício", "oficio", "portaria", "regulamento", "memorando"]):
        reasons.append("keyword:contract")
        return "contracts", "contract", "promote_candidate", reasons
    if any(k in hay for k in ["workflow", "runbook", "checklist", "passo a passo"]):
        reasons.append("keyword:workflow")
        return "workflows", "workflow", "promote_candidate", reasons
    if any(k in hay for k in ["decisão", "decisao", "adr"]):
        reasons.append("keyword:decision")
        return "decisions", "decision", "promote_candidate", reasons
    if content_type in {"zip", "audio", "video"}:
        reasons.append(f"content_type:{content_type}")
        return "knowledge", "fact", "review_first", reasons
    if content_type == "image":
        reasons.append("content_type:image")
        return "knowledge", "fact", "review_first", reasons
    reasons.append("default:knowledge")
    return "knowledge", "fact", "promote_candidate", reasons


def triage(manifest: dict[str, Any], extracted_text: str, preview: dict[str, Any]) -> dict[str, Any]:
    micro, micro_reasons = choose_microverso(
        extracted_text + "\n" + (manifest["envelope"].get("user_caption") or ""),
        manifest["original"]["filename"],
        manifest["envelope"].get("microverso_hint"),
    )
    target_dir, kind, action, target_reasons = choose_target(extracted_text + "\n" + (manifest["envelope"].get("user_caption") or ""), manifest["envelope"]["content_type"])
    nature, _default_kind = ALLOWED_TARGET_DIRS[target_dir]
    summary = extracted_text.strip().replace("\r", "")
    excerpt = summary[:500]
    next_actions = [
        "manter na inbox como referência operacional",
        f"promover para {target_dir}/" + (f" no microverso {micro}" if micro else " após escolher microverso"),
    ]
    if action == "review_first":
        next_actions.insert(0, "revisar manualmente a rota sugerida antes de promover")
    routing = {
        "suggested_scope_mode": "micro",
        "suggested_microverso": micro,
        "suggested_dir": target_dir,
        "suggested_kind": kind,
        "suggested_nature": nature,
        "action": action,
        "confidence": "medium" if excerpt else "low",
        "reasons": micro_reasons + target_reasons,
        "excerpt": excerpt,
        "next_actions": next_actions,
        "preview": preview,
    }
    return routing


def load_by_args(args: argparse.Namespace) -> tuple[Path, dict[str, Any]]:
    if getattr(args, "intake_dir", None):
        intake_dir = Path(args.intake_dir).expanduser().resolve()
    elif getattr(args, "intake_id", None):
        intake_dir = inbox_root() / args.intake_id
    else:
        raise ValueError("--intake-dir or --intake-id is required")
    if not intake_dir.exists():
        raise FileNotFoundError(intake_dir)
    manifest = read_json(intake_dir / "manifest.json", None)
    if not manifest:
        raise RuntimeError(f"manifest.json missing in {intake_dir}")
    return intake_dir, manifest


def analyze_existing(args: argparse.Namespace) -> None:
    intake_dir, manifest = load_by_args(args)
    extracted_text, preview, files = extract_for_manifest(manifest, intake_dir)
    routing = triage(manifest, extracted_text, preview)
    write_json(intake_dir / "routing.json", routing)
    manifest["derived"] = {"files": files}
    manifest["triage"] = routing
    manifest["status"] = "triaged"
    manifest["updated_at"] = now_iso()
    write_json(intake_dir / "manifest.json", manifest)
    append_log(intake_dir, "analyzed", {"derived_files": files, "action": routing["action"]})
    print(json.dumps({"status": "triaged", "intake_dir": str(intake_dir), "routing": routing, "manifest": manifest}, indent=2, ensure_ascii=False))


def ingest(args: argparse.Namespace) -> None:
    intake_dir, _manifest = create_from_args(args)
    ns = argparse.Namespace(intake_dir=str(intake_dir), intake_id=None)
    analyze_existing(ns)


def ensure_scope(scope_mode: str, microverso: str | None) -> Path:
    base = acervo_root() / ("global" if scope_mode == "global" else f"micro/{microverso}")
    if not base.exists():
        raise FileNotFoundError(f"target scope not found: {base}")
    return base


def update_index(index_path: Path, functional_dir: str, filename: str) -> None:
    line = f"- [{filename}]({functional_dir}/{filename})"
    if not index_path.exists():
        index_path.write_text(f"# Index\n\n## {functional_dir}\n{line}\n", encoding="utf-8")
        return
    text = index_path.read_text(encoding="utf-8")
    if line in text:
        return
    heading = f"## {functional_dir}"
    if heading in text:
        parts = text.split(heading, 1)
        head, tail = parts[0], parts[1]
        tail = tail.lstrip("\n")
        if tail.startswith("<!-- vazio -->"):
            tail = tail.replace("<!-- vazio -->", line, 1)
            text = head + heading + "\n" + tail
        else:
            lines = tail.splitlines()
            insert_at = 0
            while insert_at < len(lines) and (lines[insert_at].startswith("-") or lines[insert_at].startswith("<!--") or lines[insert_at].strip() == ""):
                insert_at += 1
            lines.insert(insert_at, line)
            text = head + heading + "\n" + "\n".join(lines)
    else:
        text = text.rstrip() + f"\n\n## {functional_dir}\n{line}\n"
    index_path.write_text(text.rstrip() + "\n", encoding="utf-8")


def append_scope_log(log_path: Path, message: str) -> None:
    if not log_path.exists():
        log_path.write_text("# Log\n\n", encoding="utf-8")
    text = log_path.read_text(encoding="utf-8").rstrip()
    text += f"\n\n## [{today()}] promote | intake semantic promotion\n- {message}\n"
    log_path.write_text(text, encoding="utf-8")


def frontmatter_for(title: str, scope_mode: str, scope_slug: str | None, target_dir: str, content_type: str, sources: list[str]) -> str:
    nature, kind_default = ALLOWED_TARGET_DIRS[target_dir]
    return textwrap.dedent(f"""\
    ---
    title: {title}
    created: {today()}
    updated: {today()}
    nature: {nature}
    kind: {kind_default}
    scope_mode: {scope_mode}
    scope_slug: {scope_slug if scope_slug else 'null'}
    applies_to: []
    authority: derived
    operational_mode: advisory
    stability: experimental
    sources:
      - {sources[0]}
      - {sources[1]}
    derived_from:
      - intake:{sources[2]}
    confidence: medium
    promotion_policy: none
    upstream:
      source_skill: exocortex/personal-intake-workspace
      assumed_version: 1.0.0
      coupling: adapter-only
    tags: [intake, promoted, {content_type}]
    ---
    """)


def promote(args: argparse.Namespace) -> None:
    intake_dir, manifest = load_by_args(args)
    routing = read_json(intake_dir / 'routing.json', None)
    if not routing:
        raise RuntimeError('routing.json missing; run analyze first')
    scope_mode = args.scope
    microverso = args.microverso or routing.get('suggested_microverso')
    if scope_mode == 'micro' and not microverso:
        raise RuntimeError('microverso is required when scope is micro and routing has no suggestion')
    base = ensure_scope(scope_mode, microverso)
    target_dir = args.functional_dir or routing.get('suggested_dir') or 'knowledge'
    if target_dir not in ALLOWED_TARGET_DIRS:
        raise RuntimeError(f'invalid functional dir: {target_dir}')
    title = args.title or manifest.get('title') or manifest['intake_id']
    slug = args.slug or slugify(title)
    page_path = base / target_dir / f'{slug}.md'
    extracted = ''
    for candidate in ['derived/extracted.md', 'derived/ocr.md', 'derived/transcript.md']:
        p = intake_dir / candidate
        if p.exists():
            extracted = p.read_text(encoding='utf-8')
            break
    excerpt = routing.get('excerpt') or 'Sem extração textual relevante.'
    frontmatter = frontmatter_for(
        title,
        scope_mode,
        microverso,
        target_dir,
        manifest['envelope']['content_type'],
        [
            f"_inbox/{manifest['intake_id']}/manifest.json",
            f"_inbox/{manifest['intake_id']}/routing.json",
            manifest['intake_id'],
        ],
    )
    body = textwrap.dedent(f"""
    # {title}

    ## Origem do intake

    - intake_id: `{manifest['intake_id']}`
    - canal: `{manifest['envelope']['channel']}`
    - recebido_em: `{manifest['envelope']['received_at']}`
    - arquivo_original: `{manifest['original']['filename']}`
    - mime: `{manifest['original']['mime_type']}`
    - sha256: `{manifest['original']['sha256']}`

    ## Hipótese de triagem

    - microverso sugerido: `{routing.get('suggested_microverso')}`
    - diretório sugerido: `{routing.get('suggested_dir')}`
    - ação sugerida: `{routing.get('action')}`
    - razões: {', '.join(routing.get('reasons', [])) or '(nenhuma)'}

    ## Resumo

    {excerpt}

    ## Referências operacionais

    - original: `~/.hermes/acervo/{manifest['original']['path']}`
    - derived: `~/.hermes/acervo/_inbox/{manifest['intake_id']}/derived/`

    ## Conteúdo extraído

    {extracted if extracted else 'Sem conteúdo textual extraído.'}
    """).strip() + "\n"
    page_path.parent.mkdir(parents=True, exist_ok=True)
    page_path.write_text(frontmatter + "\n" + body, encoding='utf-8')
    update_index(base / 'index.md', target_dir, page_path.name)
    append_scope_log(base / 'log.md', f"Promovido intake `{manifest['intake_id']}` para `{scope_mode}`/{microverso or 'global'}/{target_dir}/{page_path.name}`.")
    manifest['promotion'] = {
        'status': 'promoted',
        'scope_mode': scope_mode,
        'scope_slug': microverso,
        'functional_dir': target_dir,
        'page_path': rel_to_acervo(page_path),
        'promoted_at': now_iso(),
    }
    manifest['status'] = 'promoted'
    manifest['updated_at'] = now_iso()
    write_json(intake_dir / 'manifest.json', manifest)
    append_log(intake_dir, 'promoted', manifest['promotion'])
    print(json.dumps({'status': 'promoted', 'page_path': str(page_path), 'manifest': manifest}, indent=2, ensure_ascii=False))


def show(args: argparse.Namespace) -> None:
    intake_dir, manifest = load_by_args(args)
    routing = read_json(intake_dir / 'routing.json', {})
    output = {'intake_dir': str(intake_dir), 'manifest': manifest, 'routing': routing}
    print(json.dumps(output, indent=2, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Personal Intake Workspace tool')
    sub = parser.add_subparsers(dest='command', required=True)

    ingest_p = sub.add_parser('ingest', help='Create intake package and analyze it')
    ingest_p.add_argument('--input')
    ingest_p.add_argument('--link')
    ingest_p.add_argument('--text')
    ingest_p.add_argument('--title')
    ingest_p.add_argument('--intake-id')
    ingest_p.add_argument('--channel', default='cli')
    ingest_p.add_argument('--caption', default='')
    ingest_p.add_argument('--content-type')
    ingest_p.add_argument('--correlation-id', default='')
    ingest_p.add_argument('--session-ref', default='')
    ingest_p.add_argument('--microverso-hint', default='')
    ingest_p.set_defaults(func=ingest)

    analyze_p = sub.add_parser('analyze', help='Re-run extraction and routing')
    analyze_p.add_argument('--intake-dir')
    analyze_p.add_argument('--intake-id')
    analyze_p.set_defaults(func=analyze_existing)

    show_p = sub.add_parser('show', help='Show manifest and routing')
    show_p.add_argument('--intake-dir')
    show_p.add_argument('--intake-id')
    show_p.set_defaults(func=show)

    promote_p = sub.add_parser('promote', help='Promote intake to semantic page')
    promote_p.add_argument('--intake-dir')
    promote_p.add_argument('--intake-id')
    promote_p.add_argument('--scope', choices=['micro', 'global'], default='micro')
    promote_p.add_argument('--microverso')
    promote_p.add_argument('--functional-dir')
    promote_p.add_argument('--title')
    promote_p.add_argument('--slug')
    promote_p.set_defaults(func=promote)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
