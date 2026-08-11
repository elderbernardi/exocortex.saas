#!/usr/bin/env python3
"""Export live Sales-AI roster inputs and optionally freeze per-seller manifests."""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

_INPUT_SCHEMA = "exocortex/micro-news-roster-input/v1"
_DEFAULT_PAGE_SIZE = 500
_DEFAULT_CHUNK_SIZE = 75


@dataclass(frozen=True)
class AuthMode:
    kind: str
    token: str | None = None
    email: str | None = None
    password: str | None = None


class SupabaseRestClient:
    def __init__(self, env: dict[str, str], page_size: int = _DEFAULT_PAGE_SIZE):
        self.env = env
        self.page_size = page_size
        self.base_url = env["SUPABASE_URL"].rstrip("/")
        self.auth_mode = resolve_auth_mode(env)
        self.api_key = self._resolve_api_key()
        self.bearer_token = self._resolve_bearer_token()

    def _resolve_api_key(self) -> str:
        if self.auth_mode.kind == "service":
            key = self.env.get("SUPABASE_SERVICE_ROLE_KEY")
            if not key:
                raise ValueError("SUPABASE_SERVICE_ROLE_KEY is required for service mode")
            return key
        anon_key = self.env.get("SUPABASE_ANON_KEY") or self.env.get("SUPABASE_PUBLISHABLE_KEY")
        if not anon_key:
            raise ValueError("SUPABASE_ANON_KEY (or SUPABASE_PUBLISHABLE_KEY) is required for user/password mode")
        return anon_key

    def _resolve_bearer_token(self) -> str:
        if self.auth_mode.kind == "service":
            return self.api_key
        if self.auth_mode.kind == "user":
            if not self.auth_mode.token:
                raise ValueError("SUPABASE_USER_JWT is required for user mode")
            return self.auth_mode.token
        return self._password_sign_in(self.auth_mode.email or "", self.auth_mode.password or "")

    def _password_sign_in(self, email: str, password: str) -> str:
        payload = json.dumps({"email": email, "password": password}).encode("utf-8")
        request = Request(
            f"{self.base_url}/auth/v1/token?grant_type=password",
            data=payload,
            method="POST",
            headers={
                "apikey": self.api_key,
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=60) as response:
                body = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Supabase password sign-in failed ({exc.code}): {detail}") from exc
        token = body.get("access_token")
        if not token:
            raise RuntimeError("Supabase password sign-in returned no access_token")
        return str(token)

    def fetch_rows(self, table: str, filters: dict[str, str] | None = None) -> list[dict[str, Any]]:
        filters = dict(filters or {})
        filters.setdefault("select", "*")
        rows: list[dict[str, Any]] = []
        offset = 0
        while True:
            params = dict(filters)
            params["limit"] = str(self.page_size)
            params["offset"] = str(offset)
            page = self._request_json(f"/rest/v1/{table}", params)
            if not isinstance(page, list):
                raise RuntimeError(f"Supabase table {table} returned non-list payload")
            chunk = [row for row in page if isinstance(row, dict)]
            rows.extend(chunk)
            if len(chunk) < self.page_size:
                break
            offset += self.page_size
        return rows

    def _request_json(self, path: str, params: dict[str, str]) -> Any:
        query = urlencode(params)
        request = Request(
            f"{self.base_url}{path}?{query}",
            headers={
                "apikey": self.api_key,
                "Authorization": f"Bearer {self.bearer_token}",
                "Accept": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Supabase request failed for {path} ({exc.code}): {detail}") from exc


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_env_file(path: str | None) -> dict[str, str]:
    if not path:
        return {}
    env: dict[str, str] = {}
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = _strip_env_value(value.strip())
    return env


def _strip_env_value(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def merged_env(env_file: str | None) -> dict[str, str]:
    file_env = load_env_file(env_file)
    merged = dict(file_env)
    for key, value in os.environ.items():
        if value:
            merged[key] = value
    return merged


def resolve_auth_mode(env: dict[str, str]) -> AuthMode:
    forced = env.get("SALES_AI_MCP_AUTH_MODE", "").strip().lower()
    if forced == "user":
        token = env.get("SUPABASE_USER_JWT")
        if not token:
            raise ValueError("SALES_AI_MCP_AUTH_MODE=user requires SUPABASE_USER_JWT")
        return AuthMode(kind="user", token=token)
    if forced == "password":
        email = env.get("SUPABASE_USER_EMAIL")
        password = env.get("SUPABASE_USER_PASSWORD")
        if not email or not password:
            raise ValueError("SALES_AI_MCP_AUTH_MODE=password requires SUPABASE_USER_EMAIL and SUPABASE_USER_PASSWORD")
        return AuthMode(kind="password", email=email, password=password)
    if forced == "service":
        return AuthMode(kind="service")
    if forced:
        raise ValueError(f"Invalid SALES_AI_MCP_AUTH_MODE {forced!r}")
    if env.get("SUPABASE_USER_JWT"):
        return AuthMode(kind="user", token=env["SUPABASE_USER_JWT"])
    if env.get("SUPABASE_USER_EMAIL") and env.get("SUPABASE_USER_PASSWORD"):
        return AuthMode(kind="password", email=env["SUPABASE_USER_EMAIL"], password=env["SUPABASE_USER_PASSWORD"])
    if env.get("SUPABASE_SERVICE_ROLE_KEY"):
        return AuthMode(kind="service")
    raise ValueError(
        "No Supabase auth configured. Set SUPABASE_SERVICE_ROLE_KEY, SUPABASE_USER_JWT, "
        "or SUPABASE_USER_EMAIL + SUPABASE_USER_PASSWORD."
    )


def chunked(values: Iterable[str], size: int) -> Iterable[list[str]]:
    bucket: list[str] = []
    for value in values:
        bucket.append(value)
        if len(bucket) >= size:
            yield bucket
            bucket = []
    if bucket:
        yield bucket


def seller_is_eligible(seller: dict[str, Any]) -> bool:
    return (
        seller.get("role") == "vendedor"
        and bool(seller.get("ativo"))
        and bool(seller.get("erp_ref_codes"))
        and seller.get("nome") != "<SEM VENDEDOR>"
    )


def build_payload(kind: str, rows: list[dict[str, Any]], auth_mode: str) -> dict[str, Any]:
    return {
        "schema": _INPUT_SCHEMA,
        "kind": kind,
        "generated_at": now_utc_iso(),
        "auth_mode": auth_mode,
        "total_count": len(rows),
        "data": rows,
    }


def _in_filter(values: list[str]) -> str:
    joined = ",".join(values)
    return f"in.({joined})"


def collect_live_inputs(
    client: Any,
    *,
    seller_ids: set[str] | None = None,
    chunk_size: int = _DEFAULT_CHUNK_SIZE,
) -> dict[str, dict[str, Any]]:
    sellers = client.fetch_rows(
        "vendedores",
        {"select": "*", "role": "eq.vendedor", "ativo": "eq.true"},
    )
    eligible_sellers = [seller for seller in sellers if seller_is_eligible(seller)]
    if seller_ids is not None:
        eligible_sellers = [seller for seller in eligible_sellers if seller.get("id") in seller_ids]
    selected_seller_ids = [str(seller["id"]) for seller in eligible_sellers if seller.get("id")]

    accesses: list[dict[str, Any]] = []
    for seller_chunk in chunked(selected_seller_ids, chunk_size):
        accesses.extend(
            client.fetch_rows(
                "cliente_acesso",
                {"select": "*", "vendedor_id": _in_filter(seller_chunk)},
            )
        )

    client_ids = sorted({str(row["cliente_id"]) for row in accesses if row.get("cliente_id")})
    clients: list[dict[str, Any]] = []
    for client_chunk in chunked(client_ids, chunk_size):
        clients.extend(
            client.fetch_rows(
                "clientes",
                {
                    "select": "*",
                    "id": _in_filter(client_chunk),
                    "status": "eq.ativo",
                    "tabela_atual": "not.is.null",
                    "rfm_label": "not.is.null",
                },
            )
        )

    eligible_client_ids = {str(client["id"]) for client in clients if client.get("id")}
    filtered_accesses = [row for row in accesses if str(row.get("cliente_id")) in eligible_client_ids]

    auth_kind = getattr(getattr(client, "auth_mode", None), "kind", "unknown")
    return {
        "vendedores": build_payload("vendedores", eligible_sellers, auth_kind),
        "clientes": build_payload("clientes", clients, auth_kind),
        "acessos": build_payload("cliente_acesso", filtered_accesses, auth_kind),
    }


def write_raw_exports(payloads: dict[str, dict[str, Any]], out_dir: str) -> dict[str, str]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    paths: dict[str, str] = {}
    mapping = {
        "vendedores": "vendedores.json",
        "clientes": "clientes.json",
        "acessos": "acessos.json",
    }
    for key, filename in mapping.items():
        path = root / filename
        path.write_text(json.dumps(payloads[key], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        paths[key] = str(path)
    return paths


def freeze_from_payloads(payloads: dict[str, dict[str, Any]], freeze_out_dir: str, seller_ids: set[str] | None = None) -> dict[str, Any]:
    script_dir = Path(__file__).resolve().parent
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
    from roster_freeze import freeze_rosters  # noqa: WPS433

    return freeze_rosters(
        payloads["vendedores"],
        payloads["clientes"],
        payloads["acessos"],
        freeze_out_dir,
        seller_ids=seller_ids,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", help="Optional .env file used when process env is not already populated")
    parser.add_argument("--raw-out-dir", required=True, help="Directory where vendedores.json, clientes.json and acessos.json will be written")
    parser.add_argument("--freeze-out-dir", help="Optional directory where per-seller manifests will be generated")
    parser.add_argument("--page-size", type=int, default=_DEFAULT_PAGE_SIZE, help="REST pagination size per request")
    parser.add_argument("--chunk-size", type=int, default=_DEFAULT_CHUNK_SIZE, help="Chunk size for vendedor_id/client_id in(...) filters")
    parser.add_argument("--seller-id", action="append", dest="seller_ids", help="Optional seller UUID filter (repeatable)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    env = merged_env(args.env_file)
    client = SupabaseRestClient(env, page_size=args.page_size)
    seller_ids = set(args.seller_ids or []) or None
    payloads = collect_live_inputs(client, seller_ids=seller_ids, chunk_size=args.chunk_size)
    raw_paths = write_raw_exports(payloads, args.raw_out_dir)

    freeze_summary: dict[str, Any] | None = None
    if args.freeze_out_dir:
        freeze_summary = freeze_from_payloads(payloads, args.freeze_out_dir, seller_ids=seller_ids)

    print(
        "auth_mode={auth} sellers={sellers} clients={clients} accesses={accesses} raw_out_dir={raw} freeze_out_dir={freeze}".format(
            auth=client.auth_mode.kind,
            sellers=payloads["vendedores"]["total_count"],
            clients=payloads["clientes"]["total_count"],
            accesses=payloads["acessos"]["total_count"],
            raw=args.raw_out_dir,
            freeze=args.freeze_out_dir or "-",
        )
    )
    print(json.dumps({"raw_paths": raw_paths, "freeze_summary": freeze_summary}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
