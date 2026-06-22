#!/usr/bin/env python3
"""Resolvedor central de papéis LLM do Exocórtex.

Fonte única de verdade para *qual provider/modelo/chave/endpoint* cada parte do
sistema deve usar. Toda configuração de LLM é reduzida a 3 papéis lógicos:

    default  — sempre usado quando nenhum outro papel foi informado.
    vision   — modelo com visão; herda `default` campo a campo se vazio.
    aux       — modelo para softwares externos (DocBrain, backend do Hindsight);
               herda `default` campo a campo se vazio.

Cada papel é um quádruplo lido do ambiente:

    EXOCORTEX_<ROLE>_PROVIDER
    EXOCORTEX_<ROLE>_MODEL
    EXOCORTEX_<ROLE>_API_KEY
    EXOCORTEX_<ROLE>_BASE_URL   (opcional; default vem do catálogo de providers)

`base_url` vazio é resolvido pelo catálogo `setup/providers.json`.

Uso:
    from llm_roles import resolve_role
    role = resolve_role("default")
    role.api_key, role.model, role.chat_url, role.style ...

Sem leitura de nomes de chave legados (corte limpo): a migração one-shot
(`scripts/migrate-env-roles.py`) já populou as vars de papel no `.env.local`.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

# scripts/lib/llm_roles.py -> repo root é parent.parent.parent
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROVIDERS_FILE = Path(
    os.environ.get("EXOCORTEX_PROVIDERS_FILE", REPO_ROOT / "setup" / "providers.json")
)

ROLES = ("default", "vision", "aux")
_FIELDS = ("provider", "model", "api_key", "base_url")
_ROLE_ALIASES = {"auxiliar": "aux", "auxiliary": "aux"}


class LLMRoleError(RuntimeError):
    """Configuração de papel LLM inválida ou incompleta."""


@dataclass
class Role:
    """Configuração resolvida de um papel LLM."""

    role: str
    provider: str
    model: str
    api_key: str
    base_url: str
    chat_url: str
    style: str  # "openai" (todos os providers do catálogo expõem API OpenAI-compatible)
    vision: bool

    def is_usable(self) -> bool:
        return bool(self.api_key and self.model and self.chat_url)


# ─── Catálogo de providers ──────────────────────────────────────────────────

_providers_cache: dict | None = None


def load_providers() -> dict:
    """Carrega o catálogo de providers (cacheado)."""
    global _providers_cache
    if _providers_cache is None:
        try:
            data = json.loads(PROVIDERS_FILE.read_text(encoding="utf-8"))
            _providers_cache = data.get("providers", {})
        except (OSError, json.JSONDecodeError):
            _providers_cache = {}
    return _providers_cache


# ─── Lookup de ambiente (.env.local / .secrets como fallback) ────────────────

_env_file_cache: dict | None = None


def _candidate_env_files() -> list[Path]:
    paths: list[Path] = []
    installer = os.environ.get("EXOCORTEX_INSTALLER_DIR")
    if installer:
        paths.append(Path(installer) / ".env.local")
    paths.extend(
        [
            REPO_ROOT / ".env.local",
            Path.home() / ".exocortex-installer" / ".env.local",
            REPO_ROOT / ".secrets",
            Path.home() / ".secrets",
        ]
    )
    return paths


def _load_env_files() -> dict:
    """Lê pares KEY=value dos arquivos de fallback (primeiro a definir vence)."""
    global _env_file_cache
    if _env_file_cache is not None:
        return _env_file_cache
    merged: dict[str, str] = {}
    for path in _candidate_env_files():
        if not path.is_file():
            continue
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'").strip('"')
                if k and k not in merged:
                    merged[k] = v
        except OSError:
            continue
    _env_file_cache = merged
    return merged


def _lookup(name: str) -> str:
    """Resolve uma var: ambiente do processo, depois arquivos de fallback."""
    val = os.environ.get(name)
    if val:
        return val.strip()
    return _load_env_files().get(name, "").strip()


def _normalize_role(role: str) -> str:
    role = (role or "").strip().lower()
    role = _ROLE_ALIASES.get(role, role)
    if role not in ROLES:
        raise LLMRoleError(
            f"papel desconhecido: {role!r} (use um de {', '.join(ROLES)})"
        )
    return role


# ─── Resolução ───────────────────────────────────────────────────────────────


def _raw_fields(role: str) -> dict:
    prefix = f"EXOCORTEX_{role.upper()}_"
    return {f: _lookup(prefix + f.upper()) for f in _FIELDS}


def _build_chat_url(provider: str, base_url: str) -> tuple[str, str, bool]:
    """Retorna (base_url, chat_url, vision) usando o catálogo quando preciso."""
    catalog = load_providers().get(provider, {})
    if not base_url:
        base_url = catalog.get("base_url", "")
    chat_path = catalog.get("chat_path", "/chat/completions")
    vision = bool(catalog.get("vision", False))
    if not base_url:
        return base_url, "", vision
    # Se o usuário já colou um endpoint completo, respeita.
    if base_url.endswith("/chat/completions") or "/responses" in base_url:
        chat_url = base_url
    else:
        chat_url = base_url.rstrip("/") + chat_path
    return base_url, chat_url, vision


def resolve_role(role: str) -> Role:
    """Resolve um papel para configuração concreta, aplicando herança de default.

    `vision` e `aux` herdam de `default` qualquer campo vazio. `default` não
    herda de ninguém — se incompleto, retorna o que houver (chamadores checam
    `is_usable()` ou usam `require_role`).
    """
    role = _normalize_role(role)
    fields = _raw_fields(role)

    if role != "default":
        base = _raw_fields("default")
        for f in _FIELDS:
            if not fields[f]:
                fields[f] = base[f]

    provider = fields["provider"].strip().lower()
    base_url, chat_url, vision = _build_chat_url(provider, fields["base_url"])

    return Role(
        role=role,
        provider=provider,
        model=fields["model"],
        api_key=fields["api_key"],
        base_url=base_url,
        chat_url=chat_url,
        style=load_providers().get(provider, {}).get("style", "openai"),
        vision=vision,
    )


def require_role(role: str) -> Role:
    """Como resolve_role, mas levanta LLMRoleError se o papel não for utilizável."""
    resolved = resolve_role(role)
    if not resolved.is_usable():
        raise LLMRoleError(
            f"papel '{resolved.role}' incompleto: "
            f"provider={resolved.provider or '∅'} model={resolved.model or '∅'} "
            f"api_key={'definida' if resolved.api_key else '∅'} "
            f"base_url={resolved.base_url or '∅'}. "
            f"Configure EXOCORTEX_{resolved.role.upper()}_* no .env.local "
            f"(ou rode: bash setup.sh)."
        )
    return resolved


def reset_cache() -> None:
    """Limpa caches (útil em testes que alteram env/arquivos)."""
    global _providers_cache, _env_file_cache
    _providers_cache = None
    _env_file_cache = None


# ─── CLI de inspeção/diagnóstico ─────────────────────────────────────────────

def _export_shell(role: str) -> str:
    """Emite atribuições shell (com a chave REAL) para `eval` em llm-roles.sh.

    Uso interno: a saída é capturada em variáveis locais, nunca logada.
    """
    import shlex

    r = resolve_role(role)
    pairs = {
        "ROLE_PROVIDER": r.provider,
        "ROLE_MODEL": r.model,
        "ROLE_API_KEY": r.api_key,
        "ROLE_BASE_URL": r.base_url,
        "ROLE_CHAT_URL": r.chat_url,
        "ROLE_STYLE": r.style,
        "ROLE_VISION": "1" if r.vision else "0",
        "ROLE_USABLE": "1" if r.is_usable() else "0",
    }
    return "\n".join(f"{k}={shlex.quote(v)}" for k, v in pairs.items())


def _main(argv: list[str]) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Inspeciona papéis LLM resolvidos.")
    parser.add_argument("role", nargs="?", choices=[*ROLES, "all"], default="all")
    parser.add_argument("--json", action="store_true", help="saída JSON")
    parser.add_argument(
        "--export-shell",
        action="store_true",
        help="(interno) emite atribuições shell com a chave real",
    )
    args = parser.parse_args(argv)

    if args.export_shell:
        target = "default" if args.role == "all" else args.role
        print(_export_shell(target))
        return 0

    targets = ROLES if args.role == "all" else (args.role,)
    out = {}
    for r in targets:
        role = resolve_role(r)
        out[r] = {
            "provider": role.provider,
            "model": role.model,
            "api_key": "***" if role.api_key else "",
            "base_url": role.base_url,
            "chat_url": role.chat_url,
            "vision": role.vision,
            "usable": role.is_usable(),
        }

    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        for r, d in out.items():
            mark = "✓" if d["usable"] else "○"
            print(f"{mark} {r:8} provider={d['provider'] or '∅':12} "
                  f"model={d['model'] or '∅':28} "
                  f"key={'set' if d['api_key'] else '∅':3} "
                  f"url={d['chat_url'] or '∅'}")
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(_main(sys.argv[1:]))
