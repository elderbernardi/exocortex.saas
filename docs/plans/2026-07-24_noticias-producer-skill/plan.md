# Evolução `excrtx-news-sales-ai` → produtor autônomo — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Evoluir a skill já mesclada `excrtx-news-sales-ai` para um produtor de notícias **macro autônomo e parametrizável** (cron), **sem regredir** o runbook Route B existente, reusando `build_dossier.py`.

**Architecture:** A skill continua sendo um runbook do agente + helpers Python determinísticos. Adiciona-se: (1) config TOML de áreas monitoradas + periodicidade; (2) um despachante de cadência que decide quais áreas rodar; (3) um guard read-before-write contra o Supabase (2ª camada; a 1ª é o writer `skipped_retired` v3.1.0). Pesquisa é delegada a `excrtx-research-cpg-brasil`; publicação ao MCP `sales-ai`. Nenhum caminho de publicação exige a DataBrain up.

**Tech Stack:** Python 3.11 (stdlib `tomllib`, `json`, `urllib`/`requests`), skills Markdown do Hermes, MCP `sales-ai` v3.1.0 (`publish_noticia`/`expire_noticia`), `excrtx-research-cpg-brasil`, `excrtx-quality-antislop`.

## Global Constraints

- **Python ≥ 3.11** (usa `tomllib`); helpers em `skills/excrtx-news-sales-ai/scripts/`, testes em `tests/` (padrão importlib+subprocess de `tests/test_news_sales_ai.py`).
- **Skill Hermes**: manter frontmatter válido e as seções `## When to Use`, `## Procedure`, `## Pitfalls`, `## Verification`; após editar `compiled_rules:` rodar `python3 scripts/compile_soul.py`; `skill_judge --skill excrtx-news-sales-ai --d1-only` deve dar PASS.
- **Sem regressão**: preservar as capacidades atuais (macro+micro, harness DataBrain sob demanda, DocBrain como contexto opcional) e manter `tests/test_news_sales_ai.py` verde. Novas capacidades entram como adição.
- **DataBrain-free / no-DocBrain no padrão**: `use_docbrain=false`; publicação nunca exige DataBrain up.
- **Segurança**: escrita só via MCP com o principal `hermes-publisher` (env only, password mode); **nunca** `service_role`; nenhum segredo em código/commits.
- **Não-reativação**: 1ª camada é o writer `publish_noticia` v3.1.0 (`resultado=skipped_retired`); a 2ª (este plano) é o guard read-before-write que evita chamadas redundantes.
- **Idempotência de commits**: TDD, commits frequentes, um por tarefa.

---

## File Structure

- `skills/excrtx-news-sales-ai/config/noticias.toml` — **novo**. Config de publicação + áreas monitoradas + periodicidade.
- `skills/excrtx-news-sales-ai/scripts/news_config.py` — **novo**. Carrega/valida a config.
- `skills/excrtx-news-sales-ai/scripts/news_dispatch.py` — **novo**. Despachante de cadência (áreas vencidas + estado `last_run_at`).
- `skills/excrtx-news-sales-ai/scripts/news_guard.py` — **novo**. Guard read-before-write (classificação pura + fetch PostgREST fino).
- `skills/excrtx-news-sales-ai/.env.example` — **novo**. Variáveis esperadas, sem valores.
- `skills/excrtx-news-sales-ai/scripts/build_dossier.py` — **reusado**, sem mudança.
- `skills/excrtx-news-sales-ai/SKILL.md` — **modificar**. Adicionar os 2 modos + config, preservando o existente.
- `acervo/micro/exocortex-ops/knowledge/cron-registry.md` — **modificar**. Entrada do cron despachante.
- `tests/test_news_producer.py` — **novo**. Pytest dos 3 helpers.

---

### Task 1: Config de áreas + loader (`news_config.py`)

**Files:**
- Create: `skills/excrtx-news-sales-ai/config/noticias.toml`
- Create: `skills/excrtx-news-sales-ai/scripts/news_config.py`
- Test: `tests/test_news_producer.py`

**Interfaces:**
- Produces: `load_config(path: str) -> dict` retornando `{"publish": {default_escopo, default_ttl_days, max_items_per_run, relevance_threshold, use_docbrain}, "areas": [{slug, cadence, max_items, relevance_threshold}, ...]}` com defaults já mesclados por área.

- [ ] **Step 1: Escrever a config default**

Create `skills/excrtx-news-sales-ai/config/noticias.toml`:

```toml
# Config do produtor de notícias (excrtx-news-sales-ai, modo auto macro).
[publish]
default_escopo = "macro"
default_ttl_days = 30
max_items_per_run = 4
relevance_threshold = 60
use_docbrain = false

[[monitored_areas]]
slug = "varejo"          # template do excrtx-research-cpg-brasil
cadence = "weekly"
max_items = 3
relevance_threshold = 65

[[monitored_areas]]
slug = "limpeza"
cadence = "weekly"
```

- [ ] **Step 2: Escrever o teste que falha**

Add to `tests/test_news_producer.py`:

```python
"""Testes do produtor de notícias (excrtx-news-sales-ai, modo auto)."""
from __future__ import annotations
import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "excrtx-news-sales-ai"
SCRIPTS = SKILL_DIR / "scripts"
CONFIG = SKILL_DIR / "config" / "noticias.toml"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_load_config_merges_area_defaults():
    cfg = _load("news_config").load_config(str(CONFIG))
    assert cfg["publish"]["default_ttl_days"] == 30
    assert cfg["publish"]["use_docbrain"] is False
    areas = {a["slug"]: a for a in cfg["areas"]}
    assert areas["varejo"]["cadence"] == "weekly"
    assert areas["varejo"]["max_items"] == 3            # override
    assert areas["varejo"]["relevance_threshold"] == 65 # override
    assert areas["limpeza"]["max_items"] == 4           # inherits publish default
    assert areas["limpeza"]["relevance_threshold"] == 60


def test_load_config_rejects_area_without_slug(tmp_path):
    bad = tmp_path / "bad.toml"
    bad.write_text('[[monitored_areas]]\ncadence = "weekly"\n', encoding="utf-8")
    import pytest
    with pytest.raises(ValueError, match="slug"):
        _load("news_config").load_config(str(bad))
```

- [ ] **Step 3: Rodar o teste e ver falhar**

Run: `python3 -m pytest tests/test_news_producer.py -q`
Expected: FAIL — `news_config.py` não existe (import error / ModuleNotFoundError).

- [ ] **Step 4: Implementar `news_config.py`**

Create `skills/excrtx-news-sales-ai/scripts/news_config.py`:

```python
"""Carrega e valida a config do produtor de notícias (TOML)."""
from __future__ import annotations
import tomllib
from typing import Any

_PUBLISH_DEFAULTS = {
    "default_escopo": "macro",
    "default_ttl_days": 30,
    "max_items_per_run": 4,
    "relevance_threshold": 60,
    "use_docbrain": False,
}


def load_config(path: str) -> dict[str, Any]:
    with open(path, "rb") as fh:
        raw = tomllib.load(fh)
    publish = {**_PUBLISH_DEFAULTS, **raw.get("publish", {})}
    areas: list[dict[str, Any]] = []
    for entry in raw.get("monitored_areas", []):
        slug = entry.get("slug")
        if not slug:
            raise ValueError("monitored_areas entry missing required 'slug'")
        areas.append({
            "slug": slug,
            "cadence": entry.get("cadence", "weekly"),
            "max_items": entry.get("max_items", publish["max_items_per_run"]),
            "relevance_threshold": entry.get(
                "relevance_threshold", publish["relevance_threshold"]),
        })
    return {"publish": publish, "areas": areas}
```

- [ ] **Step 5: Rodar o teste e ver passar**

Run: `python3 -m pytest tests/test_news_producer.py -q`
Expected: PASS (2 passed).

- [ ] **Step 6: Commit**

```bash
git add skills/excrtx-news-sales-ai/config/noticias.toml \
        skills/excrtx-news-sales-ai/scripts/news_config.py \
        tests/test_news_producer.py
git commit -m "feat(news): config de áreas monitoradas + loader (news_config)"
```

---

### Task 2: Despachante de cadência (`news_dispatch.py`)

**Files:**
- Create: `skills/excrtx-news-sales-ai/scripts/news_dispatch.py`
- Test: `tests/test_news_producer.py`

**Interfaces:**
- Consumes: `load_config` (Task 1).
- Produces:
  - `cadence_seconds(cadence: str) -> int` (`"daily"`→86400, `"weekly"`→604800, `"Nd"`/`"Nh"`).
  - `due_areas(areas: list[dict], state: dict, now_epoch: int) -> list[str]` — slugs vencidos (`now - last_run_at >= cadence`; sem registro = vencido).
  - `mark_run(state: dict, slug: str, now_epoch: int) -> dict`.

- [ ] **Step 1: Escrever o teste que falha**

Add to `tests/test_news_producer.py`:

```python
def test_cadence_seconds():
    d = _load("news_dispatch")
    assert d.cadence_seconds("daily") == 86400
    assert d.cadence_seconds("weekly") == 604800
    assert d.cadence_seconds("3d") == 3 * 86400
    assert d.cadence_seconds("12h") == 12 * 3600


def test_due_areas_first_run_and_window():
    d = _load("news_dispatch")
    areas = [{"slug": "varejo", "cadence": "weekly"},
             {"slug": "limpeza", "cadence": "daily"}]
    now = 1_000_000_000
    # nunca rodou → ambas vencidas
    assert set(d.due_areas(areas, {}, now)) == {"varejo", "limpeza"}
    # limpeza rodou há 2h (< 1d) → não vence; varejo há 8d → vence
    state = {"varejo": now - 8 * 86400, "limpeza": now - 2 * 3600}
    assert d.due_areas(areas, state, now) == ["varejo"]


def test_mark_run_updates_state():
    d = _load("news_dispatch")
    state = d.mark_run({}, "varejo", 123)
    assert state["varejo"] == 123
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python3 -m pytest tests/test_news_producer.py -k dispatch -q` (e `-k cadence -k due -k mark`)
Expected: FAIL — `news_dispatch` não existe.

- [ ] **Step 3: Implementar `news_dispatch.py`**

Create `skills/excrtx-news-sales-ai/scripts/news_dispatch.py`:

```python
"""Despachante de cadência: decide quais áreas macro rodam agora."""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

_UNIT = {"h": 3600, "d": 86400}
_NAMED = {"daily": 86400, "weekly": 604800}


def cadence_seconds(cadence: str) -> int:
    if cadence in _NAMED:
        return _NAMED[cadence]
    m = re.fullmatch(r"(\d+)([hd])", cadence.strip())
    if not m:
        raise ValueError(f"cadence inválida: {cadence!r}")
    return int(m.group(1)) * _UNIT[m.group(2)]


def due_areas(areas: list[dict], state: dict, now_epoch: int) -> list[str]:
    due = []
    for area in areas:
        last = state.get(area["slug"])
        if last is None or (now_epoch - int(last)) >= cadence_seconds(area["cadence"]):
            due.append(area["slug"])
    return due


def mark_run(state: dict, slug: str, now_epoch: int) -> dict:
    state = dict(state)
    state[slug] = int(now_epoch)
    return state


def _load_state(path: str) -> dict:
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="News cadence dispatcher")
    ap.add_argument("--config", required=True)
    ap.add_argument("--state", required=True)
    ap.add_argument("--now", type=int, required=True, help="epoch seconds")
    ap.add_argument("--mark", help="slug to mark as run (writes state)")
    args = ap.parse_args(argv)

    sys.path.insert(0, str(Path(__file__).parent))
    from news_config import load_config  # noqa: E402

    state = _load_state(args.state)
    if args.mark:
        state = mark_run(state, args.mark, args.now)
        Path(args.state).write_text(json.dumps(state, indent=1), encoding="utf-8")
        print(f"marked {args.mark}={args.now}")
        return 0
    cfg = load_config(args.config)
    for slug in due_areas(cfg["areas"], state, args.now):
        print(slug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python3 -m pytest tests/test_news_producer.py -q`
Expected: PASS (todos).

- [ ] **Step 5: Commit**

```bash
git add skills/excrtx-news-sales-ai/scripts/news_dispatch.py tests/test_news_producer.py
git commit -m "feat(news): despachante de cadência por área (news_dispatch)"
```

---

### Task 3: Guard read-before-write (`news_guard.py`)

**Files:**
- Create: `skills/excrtx-news-sales-ai/scripts/news_guard.py`
- Test: `tests/test_news_producer.py`

**Interfaces:**
- Consumes: nada dos anteriores (usa `url_normalized` produzido por `build_dossier.py`).
- Produces:
  - `row_key(url_normalized: str, cliente_id: str | None) -> tuple[str, str | None]`.
  - `classify(existing: dict | None) -> str` → `"new" | "skip_active" | "skip_retired"` (retired se `existing["ativo"] is False`).
  - `partition(candidates: list[dict], existing_by_key: dict) -> dict` → `{"publish": [...], "skip_active": [...], "skip_retired": [...]}`. Candidato tem `url_normalized` e opcional `cliente_id`.

- [ ] **Step 1: Escrever o teste que falha**

Add to `tests/test_news_producer.py`:

```python
def test_classify_new_active_retired():
    g = _load("news_guard")
    assert g.classify(None) == "new"
    assert g.classify({"id": "1", "ativo": True}) == "skip_active"
    assert g.classify({"id": "1", "ativo": False}) == "skip_retired"


def test_partition_macro_keys_on_url_and_null_client():
    g = _load("news_guard")
    candidates = [
        {"url_normalized": "https://a.test/x"},                 # new
        {"url_normalized": "https://b.test/y"},                 # active → skip
        {"url_normalized": "https://c.test/z"},                 # retired → skip
    ]
    existing = {
        ("https://b.test/y", None): {"id": "2", "ativo": True},
        ("https://c.test/z", None): {"id": "3", "ativo": False},
    }
    out = g.partition(candidates, existing)
    assert [c["url_normalized"] for c in out["publish"]] == ["https://a.test/x"]
    assert [c["url_normalized"] for c in out["skip_active"]] == ["https://b.test/y"]
    assert [c["url_normalized"] for c in out["skip_retired"]] == ["https://c.test/z"]
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python3 -m pytest tests/test_news_producer.py -k guard -q` (e `-k classify -k partition`)
Expected: FAIL — `news_guard` não existe.

- [ ] **Step 3: Implementar `news_guard.py`**

Create `skills/excrtx-news-sales-ai/scripts/news_guard.py`:

```python
"""Guard read-before-write: classifica candidatos contra noticias_publicas.

Camada 2 (otimização) da não-reativação — a Camada 1 é o writer publish_noticia
v3.1.0 (resultado=skipped_retired). Aqui só evitamos chamadas redundantes ao MCP.
"""
from __future__ import annotations
import json
import os
import urllib.parse
import urllib.request
from typing import Any


def row_key(url_normalized: str, cliente_id: str | None) -> tuple[str, str | None]:
    return (url_normalized, cliente_id)


def classify(existing: dict | None) -> str:
    if existing is None:
        return "new"
    return "skip_active" if existing.get("ativo") else "skip_retired"


def partition(candidates: list[dict], existing_by_key: dict) -> dict[str, list]:
    out: dict[str, list] = {"publish": [], "skip_active": [], "skip_retired": []}
    for cand in candidates:
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
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python3 -m pytest tests/test_news_producer.py -q`
Expected: PASS (todos). `fetch_existing` fica sem teste de rede (I/O fino); a lógica pura (`classify`/`partition`) é o que carrega a invariância.

- [ ] **Step 5: Commit**

```bash
git add skills/excrtx-news-sales-ai/scripts/news_guard.py tests/test_news_producer.py
git commit -m "feat(news): guard read-before-write (classify/partition + fetch)"
```

---

### Task 4: Evoluir `SKILL.md` (2 modos, sem regredir) + recompilar SOUL_SEED

**Files:**
- Modify: `skills/excrtx-news-sales-ai/SKILL.md`
- Modify: `SOUL_SEED.md` (gerado — via `scripts/compile_soul.py`, não editar à mão)
- Test: `tests/test_news_sales_ai.py` (deve continuar verde) + `skill_judge --d1-only`

**Interfaces:**
- Consumes: `news_dispatch.py`, `news_guard.py`, `news_config.py`, `build_dossier.py`, MCP `publish_noticia`/`expire_noticia`, `excrtx-research-cpg-brasil`, `excrtx-quality-antislop`.

- [ ] **Step 1: Adicionar a seção "## Modos de operação" após "## Overview"**

Inserir no `SKILL.md`, preservando todo o restante:

```markdown
## Modos de operação

Esta skill tem dois modos. O runbook Route B abaixo (harness DataBrain sob demanda,
DocBrain como contexto) permanece **válido e opcional** — nenhum foi removido.

### Modo A — autônomo (cron, macro)
Dirigido por `config/noticias.toml`. Um cron despachante decide quais áreas rodam:

1. `python3 scripts/news_dispatch.py --config config/noticias.toml --state <acervo>/news-cadence.json --now $(date +%s)` → lista de áreas vencidas.
2. Para cada área: `python3 ../excrtx-research-cpg-brasil/scripts/orchestrate.py --template <slug> --output json --skip-l30d` (sem `--document`; `use_docbrain=false`).
3. `python3 scripts/build_dossier.py --job-context <ctx.json> --crawler <research.json> --output-file <dossier.json>` (reusa o helper; **não** passar `--docbrain`).
4. Curadoria com o modelo a partir do `prompt_packet`: dedup, relevância ≥ `relevance_threshold`, `impacto`, headline via `excrtx-quality-antislop`, **só itens com url/fonte reais**; cap `max_items`.
5. Guard: `partition()` de `scripts/news_guard.py` (via `fetch_existing`) descarta url já ativa/retirada.
6. Publicar cada item do bucket `publish` via MCP `publish_noticia` (escopo=macro); tratar `resultado ∈ {created, updated, skipped_retired}`.
7. `news_dispatch.py --mark <slug> --now $(date +%s)` para carimbar o run.
8. Expirar vencidos via MCP `expire_noticia`.

### Modo B — manual (comercial/gestão, via agente)
Quando comercial ou gestão pede para publicar uma notícia específica:
1. Receber título, url (**obrigatória**), fonte, impacto (headline opcional).
2. Passar a headline por `excrtx-quality-antislop`.
3. Guard `partition()` de 1 item (não reativa retirada).
4. `publish_noticia` com `origem` = quem pediu (`comercial`/`gestao`). Sem pesquisa/curadoria.
```

- [ ] **Step 2: Marcar harness DataBrain e DocBrain como opcionais na fronteira**

No `SKILL.md`, na seção "## Fronteira obrigatória" (ou equivalente), acrescentar a nota, **sem apagar** o conteúdo existente:

```markdown
> **v1 autônomo (default):** o Modo A **não** usa o harness DataBrain nem DocBrain
> (publica sem DataBrain up; `use_docbrain=false`). As etapas de harness/DocBrain
> abaixo continuam disponíveis para o runbook manual/avançado, mas são **opcionais**.
```

- [ ] **Step 3: Atualizar `compiled_rules:` e recompilar**

No frontmatter do `SKILL.md`, ajustar `compiled_rules:` para citar o default DataBrain-free/no-DocBrain e o guard de não-reativação; depois:

Run: `python3 scripts/compile_soul.py`
Expected: exit 0; `SOUL_SEED.md` regenerado sem erro.

- [ ] **Step 4: Verificar D1 estrutural e não-regressão**

Run: `python3 scripts/skill_judge.py --skill excrtx-news-sales-ai --d1-only`
Expected: `PASS`.
Run: `python3 -m pytest tests/test_news_sales_ai.py -q`
Expected: PASS (o runbook existente e `build_dossier.py` intactos).

- [ ] **Step 5: Commit**

```bash
git add skills/excrtx-news-sales-ai/SKILL.md SOUL_SEED.md
git commit -m "feat(news): 2 modos (auto/manual) na skill, sem regredir Route B"
```

---

### Task 5: `.env.example` + entrada no cron-registry

**Files:**
- Create: `skills/excrtx-news-sales-ai/.env.example`
- Modify: `acervo/micro/exocortex-ops/knowledge/cron-registry.md`

- [ ] **Step 1: Escrever `.env.example` (sem valores)**

Create `skills/excrtx-news-sales-ai/.env.example`:

```bash
# Publicação de notícias — principal least-privilege hermes-publisher (password mode).
# NUNCA versionar valores; NUNCA usar SUPABASE_SERVICE_ROLE_KEY aqui.
SUPABASE_URL=
SUPABASE_ANON_KEY=
SALES_AI_MCP_AUTH_MODE=password
SUPABASE_USER_EMAIL=
SUPABASE_USER_PASSWORD=
# Estado de cadência (JSON) no acervo:
NEWS_CADENCE_STATE=acervo/micro/exocortex-ops/knowledge/news-cadence.json
```

- [ ] **Step 2: Adicionar a entrada do cron**

Append em `acervo/micro/exocortex-ops/knowledge/cron-registry.md` (seguir o formato de tabela existente das outras entradas), documentando: nome `news-producer-dispatch`, comando (sessão Hermes que carrega `excrtx-news-sales-ai` modo auto), cadência do SO ≤ menor `cadence` da config (ex.: diária), gate de aprovação de ação externa na criação, e que o despachante é o árbitro real de quando cada área roda.

- [ ] **Step 3: Verificar frontmatter do acervo**

Run: `python3 scripts/validate_frontmatter.py acervo/micro/exocortex-ops/knowledge/cron-registry.md`
Expected: exit 0.

- [ ] **Step 4: Commit**

```bash
git add skills/excrtx-news-sales-ai/.env.example \
        acervo/micro/exocortex-ops/knowledge/cron-registry.md
git commit -m "docs(news): .env.example + registro do cron despachante"
```

---

### Task 6: Verificação dry-run ponta-a-ponta

**Files:**
- Test: `tests/test_news_producer.py`

- [ ] **Step 1: Teste de integração do despachante + guard sobre fixtures**

Add to `tests/test_news_producer.py`:

```python
def test_dispatch_cli_lists_due_areas(tmp_path):
    import subprocess, sys
    state = tmp_path / "state.json"
    state.write_text("{}", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "news_dispatch.py"),
         "--config", str(CONFIG), "--state", str(state), "--now", "1000000000"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0
    assert set(proc.stdout.split()) == {"varejo", "limpeza"}  # nunca rodaram
```

- [ ] **Step 2: Rodar toda a suíte nova + a existente**

Run: `python3 -m pytest tests/test_news_producer.py tests/test_news_sales_ai.py -q`
Expected: PASS em ambos os arquivos.

- [ ] **Step 3: Commit**

```bash
git add tests/test_news_producer.py
git commit -m "test(news): integração dry-run do despachante"
```

---

## Verificação final (critérios de aceite da spec)

1. **Dry-run**: `news_dispatch` lista áreas vencidas; a curadoria (SKILL Modo A) só emite candidatos com url/fonte reais — **nenhum item inventado**.
2. **Parametrização**: mudar `cadence`/`slug`/`max_items` em `noticias.toml` muda o comportamento sem tocar código (coberto por Task 1/2/6).
3. **Não-reativação**: `classify`/`partition` fazem skip de url retirada (Task 3) **e** o writer garante server-side (`skipped_retired`, já em prod v3.1.0).
4. **Sem regressão**: `tests/test_news_sales_ai.py` verde; harness DataBrain/DocBrain preservados como opcionais (Task 4).
5. **Skill de skills**: pesquisa via `excrtx-research-cpg-brasil`, qualidade via `excrtx-quality-antislop`, transporte via MCP; código novo só em config + cadência + guard.
6. **Segurança**: `.env.example` sem valores; nenhuma referência a `service_role`; escrita só via MCP.
7. **Qualidade**: `skill_judge --d1-only` PASS.

## Live smoke (owner-gated, pós-implementação)

Com creds reais do `hermes-publisher` no env do runtime Hermes: rodar 1 área em modo auto → confirmar 1 notícia macro no feed "Notícias do Setor" do app; re-run idempotente; expirar; e um publish do Modo B. (Fora do escopo dos testes unitários; requer prod.)
