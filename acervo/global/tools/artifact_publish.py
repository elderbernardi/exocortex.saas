#!/usr/bin/env python3
"""Deterministic Drive publication for Exocórtex artifacts.

Commands:
  init     Initialize an artifact package with canonical Drive defaults.
  publish  Upload final files to Drive with deterministic folder resolution.
  move     Move an already-published Drive file/folder to another folder.

Core policy:
  1. Explicit destination from the executive wins.
  2. Existing manifest `drive_target.folder_path` is respected.
  3. Otherwise default to `exocortex/inbox`.
  4. Never infer Drive destination from the local filesystem path.
  5. Multiple interdependent files publish into a dedicated subfolder.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import mimetypes
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FOLDER_MIME = "application/vnd.google-apps.folder"
DEFAULT_DRIVE_PATH = "exocortex/inbox"


def hermes_home() -> Path:
    return Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))).expanduser()


def exocortex_home() -> Path:
    return Path(os.environ.get("EXOCORTEX_HOME", str(Path.home() / "exocortex"))).expanduser()


def acervo_root() -> Path:
    env = os.environ.get("ACERVO", "").strip()
    if env:
        return Path(env).expanduser()
    candidate = exocortex_home() / "acervo"
    if candidate.is_dir():
        return candidate
    return hermes_home() / "acervo"


def tools_root() -> Path:
    return acervo_root() / "global" / "tools"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(text: str) -> str:
    value = text.lower().strip().replace(" ", "-")
    value = "".join(ch for ch in value if ch.isalnum() or ch in {"-", "_"})
    value = value.strip("-_")
    return value or "artifact"


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class UploadItem:
    local_path: Path
    drive_name: str
    kind: str
    mime: str
    relative_path: str


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_manifest(artifact_dir: Path) -> dict[str, Any]:
    manifest_path = artifact_dir / "manifest.json"
    if not manifest_path.is_file():
        raise SystemExit(f"manifest.json não encontrado em {artifact_dir}")
    return read_json(manifest_path)


def save_manifest(artifact_dir: Path, manifest: dict[str, Any]) -> None:
    manifest["updated_at"] = now_iso()
    write_json(artifact_dir / "manifest.json", manifest)


def discover_google_api_driver() -> Path:
    candidates = [
        hermes_home() / "skills" / "productivity" / "google-workspace" / "scripts" / "google_api.py",
        hermes_home() / "hermes-agent" / "skills" / "productivity" / "google-workspace" / "scripts" / "google_api.py",
        Path.cwd() / "google_api.py",
        Path.cwd() / "scripts" / "google_api.py",
        Path(__file__).resolve().parents[4] / "skills" / "excrtx-integrate-gdrive" / "scripts" / "google_api.py",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise SystemExit("google_api.py não encontrado. Verifique a skill productivity/google-workspace no runtime Hermes.")


def load_google_api_module():
    driver = discover_google_api_driver()
    spec = importlib.util.spec_from_file_location("exocortex_google_api", driver)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Não foi possível carregar {driver}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_drive_service():
    module = load_google_api_module()
    return module.build_service("drive", "v3")


def normalize_drive_path(path: str | None) -> str:
    value = (path or "").strip().strip("/")
    return value or DEFAULT_DRIVE_PATH


def resolve_drive_target(manifest: dict[str, Any], explicit_drive_path: str | None = None) -> str:
    explicit = normalize_drive_path(explicit_drive_path) if explicit_drive_path else ""
    if explicit:
        return explicit
    existing = normalize_drive_path((manifest.get("drive_target") or {}).get("folder_path"))
    return existing or DEFAULT_DRIVE_PATH


def should_group_in_subfolder(items: list[UploadItem], force: bool = False) -> bool:
    return force or len(items) > 1


def resolve_publication_folder(base_path: str, manifest: dict[str, Any], items: list[UploadItem], force_group: bool = False) -> str:
    base = normalize_drive_path(base_path)
    if not should_group_in_subfolder(items, force=force_group):
        return base
    slug = manifest.get("canonical_slug") or slugify(manifest.get("title") or manifest.get("artifact_id") or "artifact")
    return f"{base}/{slug}"


def find_child_folder(service, name: str, parent_id: str | None) -> dict[str, Any] | None:
    escaped = name.replace("\\", "\\\\").replace("'", "\\'")
    parent_clause = f"'{parent_id}' in parents" if parent_id else "'root' in parents"
    query = (
        f"name = '{escaped}' and {parent_clause} and "
        f"mimeType = '{FOLDER_MIME}' and trashed = false"
    )
    result = service.files().list(
        q=query,
        pageSize=1,
        fields="files(id, name, webViewLink, parents)",
    ).execute()
    files = result.get("files", [])
    return files[0] if files else None


def ensure_folder(service, name: str, parent_id: str | None) -> dict[str, Any]:
    existing = find_child_folder(service, name=name, parent_id=parent_id)
    if existing:
        return existing
    body: dict[str, Any] = {"name": name, "mimeType": FOLDER_MIME}
    if parent_id:
        body["parents"] = [parent_id]
    return service.files().create(body=body, fields="id, name, webViewLink, parents").execute()


def ensure_folder_path(service, folder_path: str) -> dict[str, Any]:
    current_parent: str | None = None
    current_meta: dict[str, Any] | None = None
    for segment in [part for part in folder_path.split("/") if part]:
        current_meta = ensure_folder(service, segment, current_parent)
        current_parent = current_meta["id"]
    if current_meta is None:
        raise SystemExit("folder_path vazio após normalização")
    return current_meta


def get_drive_item(service, file_id: str) -> dict[str, Any]:
    return service.files().get(
        fileId=file_id,
        fields="id, name, mimeType, webViewLink, parents",
    ).execute()


def move_drive_item(service, file_id: str, new_parent_id: str) -> dict[str, Any]:
    meta = get_drive_item(service, file_id)
    parents = meta.get("parents", [])
    remove_parents = ",".join(parents) if parents else ""
    return service.files().update(
        fileId=file_id,
        addParents=new_parent_id,
        removeParents=remove_parents,
        fields="id, name, mimeType, webViewLink, parents",
    ).execute()


def upload_file(service, item: UploadItem, parent_id: str) -> dict[str, Any]:
    from googleapiclient.http import MediaFileUpload

    media = MediaFileUpload(str(item.local_path), mimetype=item.mime, resumable=True)
    body = {"name": item.drive_name, "parents": [parent_id]}
    return service.files().create(
        body=body,
        media_body=media,
        fields="id, name, mimeType, webViewLink, parents",
    ).execute()


def collect_upload_items(artifact_dir: Path, manifest: dict[str, Any], include_source_when_empty: bool = True) -> list[UploadItem]:
    items: list[UploadItem] = []
    exports = manifest.get("exports") or []
    for export in exports:
        rel = export.get("path", "")
        if not rel:
            continue
        local_path = artifact_dir / rel
        if not local_path.is_file():
            continue
        mime = export.get("mime") or mimetypes.guess_type(str(local_path))[0] or "application/octet-stream"
        items.append(
            UploadItem(
                local_path=local_path,
                drive_name=Path(rel).name,
                kind=export.get("kind") or local_path.suffix.lstrip(".") or "file",
                mime=mime,
                relative_path=rel,
            )
        )
    if items:
        return items

    if include_source_when_empty:
        source_rel = manifest.get("source_path", "source/source.md")
        source_path = artifact_dir / source_rel
        if source_path.is_file():
            items.append(
                UploadItem(
                    local_path=source_path,
                    drive_name=source_path.name,
                    kind="source",
                    mime=mimetypes.guess_type(str(source_path))[0] or "text/markdown",
                    relative_path=source_rel,
                )
            )
    return items


def update_manifest_for_publication(
    manifest: dict[str, Any],
    folder_path: str,
    folder_id: str,
    receipt_relpath: str,
    published_files: list[dict[str, Any]],
) -> None:
    manifest.setdefault("drive_target", {})
    manifest["drive_target"].update(
        {
            "provider": "google_drive",
            "folder_path": folder_path,
            "visibility": "private",
            "folder_id": folder_id,
        }
    )
    manifest.setdefault("publication", {}).setdefault("drive", {})
    manifest["publication"]["drive"].update(
        {
            "status": "published",
            "receipt_path": receipt_relpath,
            "folder_id": folder_id,
            "folder_path": folder_path,
            "published_at": now_iso(),
            "files": [{"id": f["drive_file_id"], "name": f["name"]} for f in published_files],
        }
    )
    manifest["status"] = "published"


def write_receipt(
    artifact_dir: Path,
    folder_meta: dict[str, Any],
    folder_path: str,
    files: list[dict[str, Any]],
    moved_from: dict[str, Any] | None = None,
) -> Path:
    receipt = {
        "provider": "google_drive",
        "published_at": now_iso(),
        "folder_path": folder_path,
        "folder_id": folder_meta["id"],
        "folder_link": folder_meta.get("webViewLink", ""),
        "visibility": "private",
        "files": files,
    }
    if moved_from:
        receipt["moved_from"] = moved_from
    receipt_path = artifact_dir / "receipts" / "receipt.google_drive.json"
    write_json(receipt_path, receipt)
    return receipt_path


def write_failure_receipt(artifact_dir: Path, error: str, folder_path: str) -> None:
    payload = {
        "provider": "google_drive",
        "failed_at": now_iso(),
        "folder_path": folder_path,
        "error": error[:2000],
    }
    write_json(artifact_dir / "receipts" / "receipt.google_drive.failed.json", payload)


def init_artifact(args) -> int:
    harness_dir = Path(__file__).resolve().parent / "harness"
    if not harness_dir.is_dir():
        harness_dir = tools_root() / "harness"
    sys.path.insert(0, str(harness_dir))
    from init_artifact_package import build_manifest, generate_artifact_id  # type: ignore

    artifact_id = generate_artifact_id(args.title)
    artifact_dir = acervo_root() / "_artifacts" / "items" / artifact_id
    artifact_dir.mkdir(parents=True, exist_ok=True)
    for subdir in ("source", "assets", "exports", "evaluations", "receipts"):
        (artifact_dir / subdir).mkdir(exist_ok=True)

    manifest = build_manifest(
        artifact_id=artifact_id,
        title=args.title,
        task_id=args.task_id,
        primary_microverso=args.microverso,
        related_microversos=args.related_microversos,
        artifact_type=args.artifact_type,
        source_type=args.source_type,
        scope=args.scope,
    )
    drive_target = resolve_drive_target(manifest, explicit_drive_path=args.drive_path)
    manifest.setdefault("drive_target", {})
    manifest["drive_target"].update(
        {
            "provider": "google_drive",
            "folder_path": drive_target,
            "visibility": "private",
        }
    )

    source_dst = artifact_dir / "source" / "source.md"
    if args.source_md:
        source_src = Path(args.source_md).expanduser()
        if not source_src.is_file():
            raise SystemExit(f"source_md não encontrado: {source_src}")
        shutil.copy2(source_src, source_dst)
    else:
        source_dst.write_text(f"# {args.title}\n\n", encoding="utf-8")

    save_manifest(artifact_dir, manifest)
    print(
        json.dumps(
            {
                "status": "initialized",
                "artifact_id": artifact_id,
                "artifact_dir": str(artifact_dir),
                "drive_target": drive_target,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def publish_artifact(args) -> int:
    artifact_dir = Path(args.artifact_dir).expanduser()
    manifest = load_manifest(artifact_dir)
    items = collect_upload_items(artifact_dir, manifest)
    if not items:
        raise SystemExit("Nenhum arquivo publicável encontrado em exports/ nem source/")

    base_target = resolve_drive_target(manifest, explicit_drive_path=args.drive_path)
    final_folder_path = resolve_publication_folder(
        base_target,
        manifest=manifest,
        items=items,
        force_group=args.force_subfolder,
    )

    try:
        service = build_drive_service()
        folder_meta = ensure_folder_path(service, final_folder_path)
        published_files: list[dict[str, Any]] = []
        for item in items:
            result = upload_file(service, item, parent_id=folder_meta["id"])
            published_files.append(
                {
                    "name": result.get("name", item.drive_name),
                    "relative_path": item.relative_path,
                    "kind": item.kind,
                    "mimeType": result.get("mimeType", item.mime),
                    "drive_file_id": result["id"],
                    "webViewLink": result.get("webViewLink", ""),
                    "sha256": compute_sha256(item.local_path),
                    "size": item.local_path.stat().st_size,
                }
            )
        receipt_path = write_receipt(artifact_dir, folder_meta, final_folder_path, published_files)
        receipt_relpath = str(receipt_path.relative_to(artifact_dir))
        update_manifest_for_publication(
            manifest,
            folder_path=final_folder_path,
            folder_id=folder_meta["id"],
            receipt_relpath=receipt_relpath,
            published_files=published_files,
        )
        save_manifest(artifact_dir, manifest)
        print(
            json.dumps(
                {
                    "status": "published",
                    "artifact_dir": str(artifact_dir),
                    "folder_path": final_folder_path,
                    "folder_id": folder_meta["id"],
                    "folder_link": folder_meta.get("webViewLink", ""),
                    "files": published_files,
                    "follow_up_question": "Você deseja mover para outro lugar?",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        write_failure_receipt(artifact_dir, str(exc), final_folder_path)
        raise


def move_artifact(args) -> int:
    artifact_dir = Path(args.artifact_dir).expanduser()
    manifest = load_manifest(artifact_dir)
    receipt_path = artifact_dir / "receipts" / "receipt.google_drive.json"
    if not receipt_path.is_file():
        raise SystemExit("receipt.google_drive.json não encontrado; publique antes de mover")
    receipt = read_json(receipt_path)

    service = build_drive_service()
    dest_folder_path = normalize_drive_path(args.drive_path)
    dest_folder_meta = ensure_folder_path(service, dest_folder_path)

    move_mode = args.mode
    if move_mode == "auto":
        move_mode = "folder" if receipt.get("folder_id") and len(receipt.get("files", [])) > 1 else "files"

    moved_files: list[dict[str, Any]] = []
    if move_mode == "folder":
        folder_id = receipt.get("folder_id")
        if not folder_id:
            raise SystemExit("Receipt sem folder_id para mover pasta")
        moved_folder = move_drive_item(service, folder_id, dest_folder_meta["id"])
        new_folder_path = f"{dest_folder_path}/{moved_folder['name']}"
        receipt_path_written = write_receipt(
            artifact_dir,
            folder_meta={
                "id": moved_folder["id"],
                "name": moved_folder.get("name", ""),
                "webViewLink": moved_folder.get("webViewLink", ""),
            },
            folder_path=new_folder_path,
            files=receipt.get("files", []),
            moved_from={
                "folder_path": receipt.get("folder_path", ""),
                "folder_id": receipt.get("folder_id", ""),
            },
        )
        update_manifest_for_publication(
            manifest,
            folder_path=new_folder_path,
            folder_id=moved_folder["id"],
            receipt_relpath=str(receipt_path_written.relative_to(artifact_dir)),
            published_files=receipt.get("files", []),
        )
        save_manifest(artifact_dir, manifest)
        print(json.dumps({
            "status": "moved",
            "mode": "folder",
            "folder_path": new_folder_path,
            "folder_id": moved_folder["id"],
            "question": "Você deseja mover para outro lugar?",
        }, ensure_ascii=False, indent=2))
        return 0

    for file_entry in receipt.get("files", []):
        moved = move_drive_item(service, file_entry["drive_file_id"], dest_folder_meta["id"])
        moved_files.append(
            {
                **file_entry,
                "webViewLink": moved.get("webViewLink", file_entry.get("webViewLink", "")),
            }
        )
    receipt_path_written = write_receipt(
        artifact_dir,
        folder_meta=dest_folder_meta,
        folder_path=dest_folder_path,
        files=moved_files,
        moved_from={
            "folder_path": receipt.get("folder_path", ""),
            "folder_id": receipt.get("folder_id", ""),
        },
    )
    update_manifest_for_publication(
        manifest,
        folder_path=dest_folder_path,
        folder_id=dest_folder_meta["id"],
        receipt_relpath=str(receipt_path_written.relative_to(artifact_dir)),
        published_files=moved_files,
    )
    save_manifest(artifact_dir, manifest)
    print(json.dumps({
        "status": "moved",
        "mode": "files",
        "folder_path": dest_folder_path,
        "folder_id": dest_folder_meta["id"],
        "files": moved_files,
        "question": "Você deseja mover para outro lugar?",
    }, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deterministic Drive publisher for Exocórtex artifacts")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init")
    p.add_argument("--title", required=True)
    p.add_argument("--task-id", default=None)
    p.add_argument("--microverso", default=None)
    p.add_argument("--related-microversos", nargs="*", default=[])
    p.add_argument("--artifact-type", default="document", choices=["document", "report", "deck", "html", "pdf", "image", "zip", "code", "mixed"])
    p.add_argument("--source-type", default="markdown", choices=["markdown", "html", "pptx", "xlsx", "external", "mixed"])
    p.add_argument("--scope", default="micro", choices=["micro", "shared", "global"])
    p.add_argument("--source-md", default=None)
    p.add_argument("--drive-path", default="")
    p.set_defaults(func=init_artifact)

    p = sub.add_parser("publish")
    p.add_argument("--artifact-dir", required=True)
    p.add_argument("--drive-path", default="")
    p.add_argument("--force-subfolder", action="store_true")
    p.set_defaults(func=publish_artifact)

    p = sub.add_parser("move")
    p.add_argument("--artifact-dir", required=True)
    p.add_argument("--drive-path", required=True)
    p.add_argument("--mode", default="auto", choices=["auto", "folder", "files"])
    p.set_defaults(func=move_artifact)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
