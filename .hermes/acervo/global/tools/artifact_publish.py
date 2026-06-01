#!/usr/bin/env python3
"""Personal Artifact Publisher for Exocortex.

Publishes local artifact exports to the user's Google Drive through the
Hermes google-workspace OAuth wrapper. Keeps source, assets, manifest and
receipt local under ~/.hermes/acervo/_artifacts.
"""

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
from pathlib import Path
from typing import Any

FOLDER_MIME = "application/vnd.google-apps.folder"


def hermes_home() -> Path:
    return Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")).expanduser()


def acervo_root() -> Path:
    return hermes_home() / "acervo"


def artifacts_root() -> Path:
    return acervo_root() / "_artifacts"


def google_api() -> Path:
    return hermes_home() / "skills" / "productivity" / "google-workspace" / "scripts" / "google_api.py"


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value: str, fallback: str = "artifact") -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or fallback


def artifact_id(title: str) -> str:
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"art_{stamp}_{slugify(title)[:48]}"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def compact_error(text: str, limit: int = 1800) -> str:
    text = re.sub(r"https://[^\s]+", "[URL_REDACTED]", text)
    text = re.sub(r"\n\s+", "\n", text).strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "... [truncated]"


def run_json(cmd: list[str]) -> Any:
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(compact_error(f"command failed: {' '.join(cmd)}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"))
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(compact_error(f"command did not return JSON: {' '.join(cmd)}\n{proc.stdout}")) from exc


def drive_search_raw(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    return run_json([
        sys.executable,
        str(google_api()),
        "drive",
        "search",
        query,
        "--raw-query",
        "--max",
        str(max_results),
    ])


def drive_create_folder(name: str, parent: str | None) -> dict[str, Any]:
    cmd = [sys.executable, str(google_api()), "drive", "create-folder", name]
    if parent:
        cmd.extend(["--parent", parent])
    return run_json(cmd)


def drive_upload(path: Path, parent: str, name: str | None = None) -> dict[str, Any]:
    cmd = [sys.executable, str(google_api()), "drive", "upload", str(path), "--parent", parent]
    if name:
        cmd.extend(["--name", name])
    return run_json(cmd)


def escape_drive_query_value(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def find_child_folder(name: str, parent: str | None) -> dict[str, Any] | None:
    q = f"name = '{escape_drive_query_value(name)}' and mimeType = '{FOLDER_MIME}' and trashed = false"
    if parent:
        q += f" and '{parent}' in parents"
    matches = drive_search_raw(q, max_results=20)
    for item in matches:
        if item.get("name") == name and item.get("mimeType") == FOLDER_MIME:
            return item
    return None


def ensure_drive_path(path: str) -> dict[str, Any]:
    parts = [p.strip() for p in path.split("/") if p.strip()]
    if not parts:
        raise ValueError("drive path must not be empty")
    parent = None
    current = None
    for part in parts:
        current = find_child_folder(part, parent)
        if current is None:
            current = drive_create_folder(part, parent)
        parent = current["id"]
    assert current is not None
    return current


def load_manifest(artifact_dir: Path) -> dict[str, Any]:
    manifest_path = artifact_dir / "manifest.json"
    if manifest_path.exists():
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    return {}


def write_manifest(artifact_dir: Path, manifest: dict[str, Any]) -> None:
    manifest["updated_at"] = now_iso()
    (artifact_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def export_entry(artifact_dir: Path, export_path: Path) -> dict[str, Any]:
    rel = export_path.relative_to(artifact_dir).as_posix()
    mime = mimetypes.guess_type(str(export_path))[0] or "application/octet-stream"
    return {
        "path": rel,
        "kind": export_path.suffix.lower().lstrip(".") or "file",
        "mime": mime,
        "sha256": sha256(export_path),
        "size": export_path.stat().st_size,
    }


def init_package(args: argparse.Namespace) -> None:
    root = artifacts_root()
    root.mkdir(parents=True, exist_ok=True)
    aid = args.artifact_id or artifact_id(args.title)
    artifact_dir = root / aid
    for sub in ["source", "assets/images", "assets/data", "assets/logos", "assets/fonts", "assets/raw", "assets/generated", "exports"]:
        (artifact_dir / sub).mkdir(parents=True, exist_ok=True)

    source_path = None
    source_type = args.source_type
    if args.source_md:
        src = Path(args.source_md).expanduser().resolve()
        if not src.exists():
            raise FileNotFoundError(src)
        dest = artifact_dir / "source" / "source.md"
        shutil.copy2(src, dest)
        source_path = "source/source.md"
        source_type = source_type or "markdown"

    created = now_iso()
    manifest = {
        "artifact_id": aid,
        "title": args.title,
        "microverso": args.microverso,
        "status": "draft",
        "source_type": source_type or "mixed",
        "source_path": source_path,
        "assets_dir": "assets",
        "exports": [],
        "drive_target": {
            "provider": "google_drive",
            "folder_path": args.drive_path,
            "visibility": "private",
        },
        "created_at": created,
        "updated_at": created,
    }
    write_manifest(artifact_dir, manifest)
    print(json.dumps({"status": "created", "artifact_dir": str(artifact_dir), "manifest": manifest}, indent=2, ensure_ascii=False))


def publish(args: argparse.Namespace) -> None:
    artifact_dir = Path(args.artifact_dir).expanduser().resolve()
    if not artifact_dir.exists():
        raise FileNotFoundError(artifact_dir)
    exports_dir = artifact_dir / "exports"
    if not exports_dir.exists():
        raise FileNotFoundError(exports_dir)

    manifest = load_manifest(artifact_dir)
    drive_path = args.drive_path or manifest.get("drive_target", {}).get("folder_path") or "exocortex/inbox"
    folder = ensure_drive_path(drive_path)

    export_files = [p for p in exports_dir.iterdir() if p.is_file()]
    if args.file:
        wanted = {Path(f).name for f in args.file}
        export_files = [p for p in export_files if p.name in wanted]
    if not export_files:
        raise RuntimeError(f"no export files found in {exports_dir}")

    uploaded = []
    export_entries = []
    for path in sorted(export_files):
        entry = export_entry(artifact_dir, path)
        upload = drive_upload(path, folder["id"])
        uploaded.append({
            "export_path": entry["path"],
            "drive_file_id": upload.get("id"),
            "name": upload.get("name"),
            "web_view_link": upload.get("webViewLink"),
            "mime": upload.get("mimeType") or entry["mime"],
            "visibility": "private",
            "sha256": entry["sha256"],
            "size": entry["size"],
        })
        export_entries.append(entry)

    published_at = now_iso()
    receipt = {
        "provider": "google_drive",
        "published_at": published_at,
        "folder_path": drive_path,
        "folder_id": folder["id"],
        "folder_link": folder.get("webViewLink"),
        "files": uploaded,
    }
    (artifact_dir / "receipt.google_drive.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    manifest.setdefault("artifact_id", artifact_dir.name)
    manifest.setdefault("title", artifact_dir.name)
    manifest["status"] = "published"
    manifest["exports"] = export_entries
    manifest["drive_target"] = {"provider": "google_drive", "folder_path": drive_path, "visibility": "private"}
    write_manifest(artifact_dir, manifest)

    print(json.dumps({"status": "published", "artifact_dir": str(artifact_dir), "receipt": receipt}, indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish Exocortex artifact exports to Google Drive.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create an artifact package")
    p_init.add_argument("--title", required=True)
    p_init.add_argument("--microverso", default="global")
    p_init.add_argument("--source-md")
    p_init.add_argument("--source-type")
    p_init.add_argument("--drive-path", default="exocortex/inbox")
    p_init.add_argument("--artifact-id")
    p_init.set_defaults(func=init_package)

    p_pub = sub.add_parser("publish", help="Upload exports to Google Drive and write receipt")
    p_pub.add_argument("--artifact-dir", required=True)
    p_pub.add_argument("--drive-path")
    p_pub.add_argument("--file", action="append", help="Export filename to publish. Repeatable. Defaults to all files in exports/.")
    p_pub.set_defaults(func=publish)

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as exc:
        error_payload = {"status": "failed", "error": compact_error(str(exc)), "failed_at": now_iso()}
        if getattr(args, "command", None) == "publish" and getattr(args, "artifact_dir", None):
            artifact_dir = Path(args.artifact_dir).expanduser().resolve()
            if artifact_dir.exists():
                try:
                    (artifact_dir / "receipt.google_drive.failed.json").write_text(
                        json.dumps(error_payload, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8",
                    )
                    manifest = load_manifest(artifact_dir)
                    if manifest:
                        manifest["status"] = "failed"
                        manifest["last_error"] = error_payload["error"]
                        write_manifest(artifact_dir, manifest)
                except Exception:
                    pass
        print(json.dumps(error_payload, indent=2, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
