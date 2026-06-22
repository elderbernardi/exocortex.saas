#!/usr/bin/env python3
"""Migração one-shot: chaves LLM legadas → 3 papéis (default / vision / aux).

Converte um `.env.local` no esquema antigo (OPENROUTER_API_KEY, DEEPSEEK_API_KEY,
DOCBRAIN_LLM_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY, ...) para o esquema de papéis
`EXOCORTEX_<ROLE>_{PROVIDER,MODEL,API_KEY,BASE_URL}`.

Idempotente: se o papel `default` já existe no arquivo, não faz nada (use --force
para reescrever). Chaves de serviços não-LLM (Telegram, Firecrawl, Context7, Brave,
ScrapeCreators, Google OAuth, XAI/X-Twitter, Hindsight cloud) são preservadas
intactas; as chaves LLM legadas migradas são comentadas com um marcador.

Uso:
    python3 scripts/migrate-env-roles.py                # migra o .env.local detectado
    python3 scripts/migrate-env-roles.py --env-file P   # arquivo explícito
    python3 scripts/migrate-env-roles.py --dry-run      # mostra o que faria
    python3 scripts/migrate-env-roles.py --force        # reescreve mesmo se já migrado
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROVIDERS_FILE = REPO_ROOT / "setup" / "providers.json"
MIGRATION_MARKER = "# [migrado→EXOCORTEX_*]"

# Chaves LLM legadas que viram papéis (e serão comentadas no arquivo).
# Mapa: legacy env var → (papel, provider). API_KEY-only quando provider é None
# (o resolvedor herda provider/model do default).
LEGACY_LLM = {
    "OPENROUTER_API_KEY": ("default", "openrouter"),
    "DEEPSEEK_API_KEY": ("default", "deepseek"),
    "OPENCODE_API_KEY": ("default", "opencode"),
    "OPENCODE_GO_API_KEY": ("default", "opencode-go"),
    "DOCBRAIN_LLM_API_KEY": ("aux", None),
    "OPENAI_API_KEY": ("vision", "openai"),
    "GEMINI_API_KEY": ("vision", "gemini"),
    "GOOGLE_API_KEY": ("vision", "gemini"),
    "GOOGLE_GENAI_API_KEY": ("vision", "gemini"),
}

# Precedência de qual chave legada vira a credencial do papel default.
DEFAULT_PRECEDENCE = ["OPENROUTER_API_KEY", "DEEPSEEK_API_KEY", "OPENCODE_API_KEY"]
VISION_PRECEDENCE = ["OPENAI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GENAI_API_KEY"]


def load_providers() -> dict:
    try:
        return json.loads(PROVIDERS_FILE.read_text(encoding="utf-8")).get("providers", {})
    except (OSError, json.JSONDecodeError):
        return {}


def detect_env_file(override: str | None) -> Path:
    if override:
        return Path(override).expanduser()
    installer = os.environ.get("EXOCORTEX_INSTALLER_DIR")
    candidates = []
    if installer:
        candidates.append(Path(installer) / ".env.local")
    candidates += [
        REPO_ROOT / ".env.local",
        Path.home() / ".exocortex-installer" / ".env.local",
    ]
    for c in candidates:
        if c.is_file():
            return c
    # default destino se nenhum existir
    return REPO_ROOT / ".env.local"


def parse_env(lines: list[str]) -> dict:
    out: dict[str, str] = {}
    for line in lines:
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        k = k.strip()
        v = v.strip().strip("'").strip('"')
        if k:
            out[k] = v
    return out


def read_config_model() -> tuple[str, str]:
    """Lê (provider, model) de $HERMES_HOME/config.yaml se existir."""
    hermes_home = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")).expanduser()
    cfg = hermes_home / "config.yaml"
    if not cfg.is_file():
        return "", ""
    try:
        import yaml

        data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
        model = data.get("model", {}) or {}
        return str(model.get("provider", "") or ""), str(model.get("default", "") or "")
    except Exception:
        return "", ""


def build_roles(values: dict) -> dict:
    """Constrói as vars EXOCORTEX_<ROLE>_* a partir das chaves legadas presentes."""
    providers = load_providers()
    cfg_provider, cfg_model = read_config_model()
    roles: dict[str, dict] = {}

    def _get(name: str) -> str:
        return (values.get(name) or os.environ.get(name) or "").strip()

    # ── default ──────────────────────────────────────────────────────────────
    for legacy in DEFAULT_PRECEDENCE:
        key = _get(legacy)
        if not key:
            continue
        provider = LEGACY_LLM[legacy][1]
        model = providers.get(provider, {}).get("default_model", "")
        # config.yaml refina quando o provider bate (ou quando não há catálogo).
        if cfg_model and (cfg_provider.lower() == provider or not cfg_provider):
            model = cfg_model
        roles["default"] = {
            "PROVIDER": provider,
            "MODEL": model,
            "API_KEY": key,
            "BASE_URL": "",
        }
        break

    # ── vision ───────────────────────────────────────────────────────────────
    for legacy in VISION_PRECEDENCE:
        key = _get(legacy)
        if not key:
            continue
        provider = LEGACY_LLM[legacy][1]
        roles["vision"] = {
            "PROVIDER": provider,
            "MODEL": providers.get(provider, {}).get("default_model", ""),
            "API_KEY": key,
            "BASE_URL": "",
        }
        break

    # ── aux ──────────────────────────────────────────────────────────────────
    aux_key = _get("DOCBRAIN_LLM_API_KEY")
    if aux_key:
        # Provider/model vazios → herdam o default no resolvedor.
        roles["aux"] = {"PROVIDER": "", "MODEL": "", "API_KEY": aux_key, "BASE_URL": ""}

    return roles


def render_role_block(roles: dict) -> list[str]:
    out = [
        "",
        "# ─── Provedores LLM (3 papéis) — gerado por migrate-env-roles.py ───",
        "# default: sempre usado. vision/aux: herdam 'default' campo a campo se vazios.",
    ]
    for role in ("default", "vision", "aux"):
        if role not in roles:
            continue
        for field in ("PROVIDER", "MODEL", "API_KEY", "BASE_URL"):
            val = roles[role][field]
            out.append(f'EXOCORTEX_{role.upper()}_{field}="{val}"')
    return out


def already_migrated(values: dict) -> bool:
    return any(
        k.startswith("EXOCORTEX_DEFAULT_") and values.get(k)
        for k in values
    )


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--env-file")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)

    env_file = detect_env_file(args.env_file)
    if not env_file.is_file():
        print(f"⚠ .env.local não encontrado em {env_file} — nada a migrar.")
        return 0

    original = env_file.read_text(encoding="utf-8")
    lines = original.splitlines()
    values = parse_env(lines)

    if already_migrated(values) and not args.force:
        print(f"✓ {env_file} já contém papéis EXOCORTEX_DEFAULT_* — nada a fazer (use --force para reescrever).")
        return 0

    roles = build_roles(values)
    if not roles:
        print("⚠ Nenhuma chave LLM legada encontrada para migrar.")
        print("  Configure os papéis manualmente ou rode: bash setup.sh")
        return 0

    # Comenta as chaves LLM legadas in-place; preserva todo o resto.
    new_lines: list[str] = []
    migrated_legacy: list[str] = []
    for line in lines:
        s = line.strip()
        if s and not s.startswith("#") and "=" in s:
            key = s.split("=", 1)[0].strip()
            if key in LEGACY_LLM:
                new_lines.append(f"{MIGRATION_MARKER} {line}")
                migrated_legacy.append(key)
                continue
        new_lines.append(line)

    new_lines.extend(render_role_block(roles))
    new_content = "\n".join(new_lines).rstrip("\n") + "\n"

    if args.dry_run:
        print(f"── DRY-RUN: {env_file} ──")
        print(f"Papéis a escrever: {', '.join(roles)}")
        print(f"Legados a comentar: {', '.join(migrated_legacy) or '(nenhum)'}")
        print("─── conteúdo resultante ───")
        # Mascara chaves no preview
        for ln in new_content.splitlines():
            if "_API_KEY=" in ln and not ln.lstrip().startswith("#"):
                k = ln.split("=", 1)[0]
                print(f'{k}="***"')
            else:
                print(ln)
        return 0

    # Backup + escrita
    backup = env_file.with_suffix(env_file.suffix + ".pre-roles.bak")
    backup.write_text(original, encoding="utf-8")
    env_file.write_text(new_content, encoding="utf-8")
    try:
        env_file.chmod(0o600)
    except OSError:
        pass

    print(f"✓ Migração concluída: {env_file}")
    print(f"  Papéis criados: {', '.join(roles)}")
    print(f"  Legados comentados: {', '.join(migrated_legacy) or '(nenhum)'}")
    print(f"  Backup: {backup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
