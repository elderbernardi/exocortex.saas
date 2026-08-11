#!/usr/bin/env python3
"""Freeze micro-news seller rosters from vendedores/clientes/cliente_acesso JSON exports."""
from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SCHEMA = "exocortex/micro-news-roster/v1"

_LEGAL_AND_CHANNEL_STOPWORDS = {
    "a",
    "ao",
    "cd",
    "cia",
    "companhia",
    "comercio",
    "comercial",
    "de",
    "do",
    "dos",
    "da",
    "das",
    "distribuicao",
    "distribuidora",
    "e",
    "eireli",
    "em",
    "grupo",
    "industria",
    "ltda",
    "me",
    "mercado",
    "rede",
    "sa",
    "s",
    "supermercado",
    "supermercados",
    "varejista",
}

_GENERIC_BRAND_BLACKLIST = {
    "dia",
    "economico",
    "economica",
    "embalagem",
    "embalagens",
    "geracao",
    "ideal",
    "ilha",
    "luiz",
    "mais",
    "max",
    "novo",
    "nova",
    "paulo",
    "porto",
    "produtos",
    "brasil",
    "uniao",
}


def load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def rows_from(payload: Any, label: str) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict) and isinstance(payload.get("data"), list):
        rows = payload["data"]
    else:
        raise ValueError(f"{label} must be a JSON array or an object with data[]")
    return [row for row in rows if isinstance(row, dict)]


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_alias(value: str | None) -> str | None:
    if not value:
        return None
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    ascii_value = "".join(char for char in decomposed if not unicodedata.combining(char))
    normalized = re.sub(r"[^a-z0-9]+", " ", ascii_value).strip()
    return normalized or None


def client_brand_aliases(client: dict[str, Any]) -> list[str]:
    token_lists: list[list[str]] = []
    for value in (client.get("nome_fantasia"), client.get("nome")):
        normalized = normalize_alias(str(value) if value is not None else None)
        if not normalized:
            return []
        tokens: list[str] = []
        for token in normalized.split():
            if token in _LEGAL_AND_CHANNEL_STOPWORDS or len(token) < 3:
                continue
            if token not in tokens:
                tokens.append(token)
        if not tokens:
            return []
        token_lists.append(tokens)

    if len(token_lists) != 2 or set(token_lists[0]) != set(token_lists[1]):
        return []
    candidate = " ".join(token_lists[0])
    if len(token_lists[0]) == 1 and candidate in _GENERIC_BRAND_BLACKLIST:
        return []
    return [candidate]


def client_aliases(client: dict[str, Any]) -> list[str]:
    aliases: list[str] = []
    for value in (client.get("nome"), client.get("nome_fantasia"), client.get("cnpj")):
        alias = normalize_alias(str(value) if value is not None else None)
        if alias and alias not in aliases:
            aliases.append(alias)
    city = client.get("cidade")
    uf = client.get("uf")
    if city and uf:
        alias = normalize_alias(f"{city} {uf}")
        if alias and alias not in aliases:
            aliases.append(alias)
    for alias in client_brand_aliases(client):
        if alias not in aliases:
            aliases.append(alias)
    return aliases


def seller_is_eligible(seller: dict[str, Any]) -> bool:
    return (
        seller.get("role") == "vendedor"
        and bool(seller.get("ativo"))
        and bool(seller.get("erp_ref_codes"))
        and seller.get("nome") != "<SEM VENDEDOR>"
    )


def client_is_eligible_matrix(client: dict[str, Any]) -> bool:
    return (
        client.get("status") == "ativo"
        and bool(client.get("tabela_atual"))
        and bool(client.get("rfm_label"))
    )


def roster_client(client: dict[str, Any], access_types: list[str]) -> dict[str, Any]:
    return {
        "cliente_id": client["id"],
        "nome": client.get("nome"),
        "nome_fantasia": client.get("nome_fantasia"),
        "cnpj": client.get("cnpj"),
        "cidade": client.get("cidade"),
        "uf": client.get("uf"),
        "erp_ref_code": client.get("erp_ref_code"),
        "tabela_atual": client.get("tabela_atual"),
        "rfm_label": client.get("rfm_label"),
        "matriz_id": client.get("matriz_id"),
        "access_types": access_types,
        "aliases": client_aliases(client),
        "brand_aliases": client_brand_aliases(client),
    }


def build_rosters(
    sellers: list[dict[str, Any]],
    clients: list[dict[str, Any]],
    accesses: list[dict[str, Any]],
    *,
    seller_ids: set[str] | None = None,
) -> dict[str, Any]:
    eligible_sellers = {
        seller["id"]: seller
        for seller in sellers
        if seller.get("id") and seller_is_eligible(seller)
    }
    if seller_ids is not None:
        eligible_sellers = {seller_id: seller for seller_id, seller in eligible_sellers.items() if seller_id in seller_ids}

    eligible_clients = {
        client["id"]: client
        for client in clients
        if client.get("id") and client_is_eligible_matrix(client)
    }

    grouped: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for access in accesses:
        seller_id = access.get("vendedor_id")
        client_id = access.get("cliente_id")
        if seller_id not in eligible_sellers or client_id not in eligible_clients:
            continue
        grouped[str(seller_id)][str(client_id)].add(str(access.get("tipo") or "titular"))

    frozen_at = now_utc_iso()
    seller_entries: list[dict[str, Any]] = []
    seller_manifest_payloads: dict[str, dict[str, Any]] = {}
    total_clients = 0

    for seller_id in sorted(grouped):
        seller = eligible_sellers[seller_id]
        client_ids = sorted(grouped[seller_id])
        clients_payload = [
            roster_client(eligible_clients[client_id], sorted(grouped[seller_id][client_id]))
            for client_id in client_ids
        ]
        total_clients += len(clients_payload)
        manifest = {
            "schema": _SCHEMA,
            "generated_at": frozen_at,
            "seller": {
                "seller_id": seller_id,
                "seller_name": seller.get("nome"),
                "seller_email": seller.get("email"),
                "erp_ref_code": seller.get("erp_ref_code"),
                "erp_ref_codes": seller.get("erp_ref_codes") or [],
            },
            "client_count": len(clients_payload),
            "clients": clients_payload,
        }
        seller_entries.append(
            {
                "seller_id": seller_id,
                "seller_name": seller.get("nome"),
                "seller_email": seller.get("email"),
                "client_count": len(clients_payload),
                "json_path": f"sellers/{seller_id}.json",
                "csv_path": f"sellers/{seller_id}.csv",
            }
        )
        seller_manifest_payloads[seller_id] = manifest

    index = {
        "schema": _SCHEMA,
        "generated_at": frozen_at,
        "seller_count": len(seller_entries),
        "client_count_total": total_clients,
        "sellers": seller_entries,
    }
    return {"index": index, "seller_manifests": seller_manifest_payloads}


def write_csv(path: Path, clients: list[dict[str, Any]]) -> None:
    fieldnames = [
        "cliente_id",
        "nome",
        "nome_fantasia",
        "cnpj",
        "cidade",
        "uf",
        "erp_ref_code",
        "tabela_atual",
        "rfm_label",
        "matriz_id",
        "access_types",
        "aliases",
        "brand_aliases",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for client in clients:
            row = dict(client)
            row["access_types"] = ";".join(client.get("access_types") or [])
            row["aliases"] = ";".join(client.get("aliases") or [])
            row["brand_aliases"] = ";".join(client.get("brand_aliases") or [])
            writer.writerow(row)


def freeze_rosters(
    sellers_payload: Any,
    clients_payload: Any,
    accesses_payload: Any,
    out_dir: str,
    *,
    seller_ids: set[str] | None = None,
) -> dict[str, Any]:
    sellers = rows_from(sellers_payload, "vendedores")
    clients = rows_from(clients_payload, "clientes")
    accesses = rows_from(accesses_payload, "cliente_acesso")
    frozen = build_rosters(sellers, clients, accesses, seller_ids=seller_ids)

    root = Path(out_dir)
    sellers_dir = root / "sellers"
    sellers_dir.mkdir(parents=True, exist_ok=True)
    (root / "index.json").write_text(json.dumps(frozen["index"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for seller_id, manifest in frozen["seller_manifests"].items():
        json_path = sellers_dir / f"{seller_id}.json"
        csv_path = sellers_dir / f"{seller_id}.csv"
        json_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_csv(csv_path, manifest["clients"])
    return frozen["index"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vendedores", required=True, help="JSON export with vendedores rows")
    parser.add_argument("--clientes", required=True, help="JSON export with clientes rows")
    parser.add_argument("--acessos", required=True, help="JSON export with cliente_acesso rows")
    parser.add_argument("--out-dir", required=True, help="Output directory for frozen manifests")
    parser.add_argument("--seller-id", action="append", dest="seller_ids", help="Optional seller UUID filter (repeatable)")
    args = parser.parse_args(argv)

    index = freeze_rosters(
        load_json(args.vendedores),
        load_json(args.clientes),
        load_json(args.acessos),
        args.out_dir,
        seller_ids=set(args.seller_ids or []) or None,
    )
    print(
        f"seller_count={index['seller_count']} client_count_total={index['client_count_total']} out_dir={args.out_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
