"""Guard read-before-write: classifica candidatos contra noticias_publicas.

Camada 2 (otimização) da não-reativação — a Camada 1 é o writer publish_noticia
v3.1.0 (resultado=skipped_retired). Aqui só evitamos chamadas redundantes ao MCP.
"""
from __future__ import annotations
import json
import urllib.parse
import urllib.request
from datetime import date


def row_key(url_normalized: str, cliente_id: str | None) -> tuple[str, str | None]:
    return (url_normalized, cliente_id)


def _coerce_today(value: date | str | None) -> date:
    if value is None:
        return date.today()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def published_age_days(candidate: dict, *, today: date | str | None = None) -> int | None:
    published = candidate.get("publicado_em")
    if not published:
        return None
    return (_coerce_today(today) - date.fromisoformat(str(published))).days


def is_stale(candidate: dict, max_age_days: int, *, today: date | str | None = None) -> bool:
    age_days = published_age_days(candidate, today=today)
    return age_days is None or age_days > max_age_days


def classify(existing: dict | None) -> str:
    if existing is None:
        return "new"
    return "skip_active" if existing.get("ativo") else "skip_retired"


def partition(
    candidates: list[dict],
    existing_by_key: dict,
    *,
    max_age_days: int | None = None,
    today: date | str | None = None,
) -> dict[str, list]:
    out: dict[str, list] = {"publish": [], "skip_active": [], "skip_retired": [], "skip_stale": []}
    for cand in candidates:
        if max_age_days is not None and is_stale(cand, max_age_days, today=today):
            out["skip_stale"].append(cand)
            continue
        key = row_key(cand["url_normalized"], cand.get("cliente_id"))
        decision = classify(existing_by_key.get(key))
        bucket = "publish" if decision == "new" else decision
        out[bucket].append(cand)
    return out


def fetch_existing(url_normalizeds: list[str], base_url: str, jwt: str,
                   anon_key: str) -> dict:
    """GET noticias_publicas por url (publisher JWT vê linhas ativo=false).

    Retorna { (url_normalized, cliente_id|None): {id, ativo} }.
    """
    if not url_normalizeds:
        return {}
    in_list = ",".join(f'"{u}"' for u in set(url_normalizeds))
    q = urllib.parse.urlencode({
        "url": f"in.({in_list})",
        "select": "id,url,cliente_id,ativo",
    })
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/rest/v1/noticias_publicas?{q}",
        headers={"apikey": anon_key, "Authorization": f"Bearer {jwt}"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
        rows = json.loads(resp.read().decode("utf-8"))
    return {row_key(r["url"], r.get("cliente_id")): {"id": r["id"], "ativo": r["ativo"]}
            for r in rows}
