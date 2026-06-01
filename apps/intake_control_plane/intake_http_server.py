#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(os.environ.get("EXOCORTEX_PROJECT_DIR", "/home/elder/projetos/pessoal/exocortex.saas")).expanduser()
DEFAULT_TOOL = ROOT / '.hermes' / 'acervo' / 'global' / 'tools' / 'intake_ingest.py'


@dataclass
class ServerConfig:
    host: str
    port: int
    hermes_home: Path
    intake_tool: Path
    upload_tmp: Path


class IntakeError(RuntimeError):
    def __init__(self, status: int, message: str, detail: Any | None = None):
        super().__init__(message)
        self.status = status
        self.message = message
        self.detail = detail


def run_tool(config: ServerConfig, args: list[str]) -> dict[str, Any]:
    cmd = [sys.executable, str(config.intake_tool), *args]
    env = os.environ.copy()
    env['HERMES_HOME'] = str(config.hermes_home)
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip()
        raise IntakeError(500, 'intake_tool_failed', {'command': cmd, 'detail': detail})
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise IntakeError(500, 'invalid_tool_output', {'stdout': proc.stdout, 'error': str(exc)})


def _maybe_add(args: list[str], flag: str, value: Any | None) -> None:
    if value is None:
        return
    sval = str(value)
    if sval == '':
        return
    args.extend([flag, sval])


def ingest_file(config: ServerConfig, *, file_path: Path, title: str | None, channel: str, caption: str | None,
                content_type: str | None, correlation_id: str | None, session_ref: str | None,
                microverso_hint: str | None) -> dict[str, Any]:
    args = ['ingest', '--input', str(file_path), '--channel', channel]
    _maybe_add(args, '--title', title)
    _maybe_add(args, '--caption', caption)
    _maybe_add(args, '--content-type', content_type)
    _maybe_add(args, '--correlation-id', correlation_id)
    _maybe_add(args, '--session-ref', session_ref)
    _maybe_add(args, '--microverso-hint', microverso_hint)
    return run_tool(config, args)


def ingest_text(config: ServerConfig, *, text: str, title: str | None, channel: str, caption: str | None,
                correlation_id: str | None, session_ref: str | None, microverso_hint: str | None) -> dict[str, Any]:
    args = ['ingest', '--text', text, '--channel', channel]
    _maybe_add(args, '--title', title)
    _maybe_add(args, '--caption', caption)
    _maybe_add(args, '--correlation-id', correlation_id)
    _maybe_add(args, '--session-ref', session_ref)
    _maybe_add(args, '--microverso-hint', microverso_hint)
    return run_tool(config, args)


def ingest_link(config: ServerConfig, *, link: str, title: str | None, channel: str, caption: str | None,
                correlation_id: str | None, session_ref: str | None, microverso_hint: str | None) -> dict[str, Any]:
    args = ['ingest', '--link', link, '--channel', channel]
    _maybe_add(args, '--title', title)
    _maybe_add(args, '--caption', caption)
    _maybe_add(args, '--correlation-id', correlation_id)
    _maybe_add(args, '--session-ref', session_ref)
    _maybe_add(args, '--microverso-hint', microverso_hint)
    return run_tool(config, args)


def analyze_intake(config: ServerConfig, intake_id: str) -> dict[str, Any]:
    return run_tool(config, ['analyze', '--intake-id', intake_id])


def show_intake(config: ServerConfig, intake_id: str) -> dict[str, Any]:
    return run_tool(config, ['show', '--intake-id', intake_id])


def promote_intake(config: ServerConfig, intake_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    args = ['promote', '--intake-id', intake_id, '--scope', payload.get('scope', 'micro')]
    _maybe_add(args, '--microverso', payload.get('microverso'))
    _maybe_add(args, '--functional-dir', payload.get('functional_dir'))
    _maybe_add(args, '--title', payload.get('title'))
    _maybe_add(args, '--slug', payload.get('slug'))
    return run_tool(config, args)


def parse_json(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get('Content-Length', '0'))
    raw = handler.rfile.read(length) if length else b'{}'
    try:
        return json.loads(raw.decode('utf-8') or '{}')
    except Exception as exc:
        raise IntakeError(400, 'invalid_json', str(exc))


def parse_multipart(handler: BaseHTTPRequestHandler, upload_tmp: Path) -> tuple[Path, dict[str, str], str]:
    content_type = handler.headers.get('Content-Type', '')
    if 'multipart/form-data' not in content_type or 'boundary=' not in content_type:
        raise IntakeError(415, 'expected_multipart_form_data')

    boundary = content_type.split('boundary=', 1)[1].strip().strip('"')
    boundary_bytes = ('--' + boundary).encode('utf-8')
    length = int(handler.headers.get('Content-Length', '0'))
    raw = handler.rfile.read(length)
    parts = raw.split(boundary_bytes)

    fields: dict[str, str] = {}
    file_bytes = None
    filename = 'upload.bin'

    for part in parts:
        part = part.strip()
        if not part or part == b'--' or part.startswith(b'--\r\n'):
            continue
        if part.startswith(b'\r\n'):
            part = part[2:]

        header_blob, sep, body = part.partition(b'\r\n\r\n')
        if not sep:
            continue

        headers = header_blob.decode('utf-8', errors='ignore').split('\r\n')
        disp = next((h for h in headers if h.lower().startswith('content-disposition:')), '')
        attrs = {}
        for chunk in disp.split(';')[1:]:
            if '=' in chunk:
                k, v = chunk.strip().split('=', 1)
                attrs[k.strip().lower()] = v.strip().strip('"')

        name = attrs.get('name', '')
        body = body[:-2] if body.endswith(b'\r\n') else body
        if attrs.get('filename') is not None and name == 'file':
            filename = Path(attrs.get('filename') or 'upload.bin').name
            file_bytes = body
        elif name:
            fields[name] = body.decode('utf-8', errors='ignore')

    if file_bytes is None:
        raise IntakeError(400, 'missing_file_field')

    upload_tmp.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix='intake_', suffix='_' + filename, dir=upload_tmp)
    os.close(fd)
    tmp_path = Path(tmp_name)
    tmp_path.write_bytes(file_bytes)
    metadata = {
        k: fields.get(k, '')
        for k in ('title', 'channel', 'caption', 'content_type', 'correlation_id', 'session_ref', 'microverso_hint')
        if k in fields
    }
    return tmp_path, metadata, filename

def make_handler(config: ServerConfig):
    class Handler(BaseHTTPRequestHandler):
        server_version = 'ExocortexIntakeHTTP/0.1'

        def log_message(self, fmt: str, *args: Any) -> None:
            return

        def _send(self, status: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, ensure_ascii=False, indent=2).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self) -> None:
            self._send(200, {'ok': True})

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            path = parsed.path.rstrip('/') or '/'
            if path == '/health':
                self._send(200, {
                    'ok': True,
                    'service': 'intake_control_plane',
                    'hermes_home': str(config.hermes_home),
                    'intake_tool': str(config.intake_tool),
                })
                return
            if path.startswith('/v1/intake/'):
                intake_id = path.split('/')[-1]
                try:
                    result = show_intake(config, intake_id)
                except IntakeError as exc:
                    self._send(exc.status, {'ok': False, 'error': exc.message, 'detail': exc.detail})
                    return
                self._send(200, {'ok': True, 'result': result})
                return
            self._send(404, {'ok': False, 'error': 'not_found'})

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            path = parsed.path.rstrip('/')
            try:
                if path == '/v1/intake/text':
                    payload = parse_json(self)
                    if not payload.get('text'):
                        raise IntakeError(400, 'missing_text')
                    result = ingest_text(
                        config,
                        text=payload['text'],
                        title=payload.get('title'),
                        channel=payload.get('channel', 'api_server'),
                        caption=payload.get('caption'),
                        correlation_id=payload.get('correlation_id'),
                        session_ref=payload.get('session_ref'),
                        microverso_hint=payload.get('microverso_hint'),
                    )
                    self._send(201, {'ok': True, 'result': result})
                    return
                if path == '/v1/intake/link':
                    payload = parse_json(self)
                    if not payload.get('link'):
                        raise IntakeError(400, 'missing_link')
                    result = ingest_link(
                        config,
                        link=payload['link'],
                        title=payload.get('title'),
                        channel=payload.get('channel', 'api_server'),
                        caption=payload.get('caption'),
                        correlation_id=payload.get('correlation_id'),
                        session_ref=payload.get('session_ref'),
                        microverso_hint=payload.get('microverso_hint'),
                    )
                    self._send(201, {'ok': True, 'result': result})
                    return
                if path == '/v1/intake/upload':
                    tmp_path, meta, filename = parse_multipart(self, config.upload_tmp)
                    try:
                        result = ingest_file(
                            config,
                            file_path=tmp_path,
                            title=meta.get('title') or Path(filename).stem,
                            channel=meta.get('channel', 'api_server'),
                            caption=meta.get('caption'),
                            content_type=meta.get('content_type'),
                            correlation_id=meta.get('correlation_id'),
                            session_ref=meta.get('session_ref'),
                            microverso_hint=meta.get('microverso_hint'),
                        )
                    finally:
                        tmp_path.unlink(missing_ok=True)
                    self._send(201, {'ok': True, 'result': result})
                    return
                if path.endswith('/analyze') and path.startswith('/v1/intake/'):
                    intake_id = path.split('/')[-2]
                    result = analyze_intake(config, intake_id)
                    self._send(200, {'ok': True, 'result': result})
                    return
                if path.endswith('/promote') and path.startswith('/v1/intake/'):
                    intake_id = path.split('/')[-2]
                    payload = parse_json(self)
                    result = promote_intake(config, intake_id, payload)
                    self._send(200, {'ok': True, 'result': result})
                    return
                raise IntakeError(404, 'not_found')
            except IntakeError as exc:
                self._send(exc.status, {'ok': False, 'error': exc.message, 'detail': exc.detail})

    return Handler


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description='Exocortex intake control plane (minimal HTTP server)')
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--port', type=int, default=8765)
    p.add_argument('--hermes-home', default=os.environ.get('HERMES_HOME', str(Path.home() / '.hermes')))
    p.add_argument('--intake-tool', default=str(DEFAULT_TOOL))
    p.add_argument('--upload-tmp', default='')
    return p


def main() -> None:
    args = build_arg_parser().parse_args()
    config = ServerConfig(
        host=args.host,
        port=args.port,
        hermes_home=Path(args.hermes_home).expanduser().resolve(),
        intake_tool=Path(args.intake_tool).expanduser().resolve(),
        upload_tmp=Path(args.upload_tmp).expanduser().resolve() if args.upload_tmp else Path(tempfile.gettempdir()) / 'exocortex-intake',
    )
    if not config.intake_tool.exists():
        raise SystemExit(f'intake tool not found: {config.intake_tool}')
    httpd = ThreadingHTTPServer((config.host, config.port), make_handler(config))
    print(json.dumps({
        'service': 'intake_control_plane',
        'listen': f'http://{config.host}:{config.port}',
        'hermes_home': str(config.hermes_home),
        'intake_tool': str(config.intake_tool),
    }, ensure_ascii=False))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
