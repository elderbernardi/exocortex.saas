#!/usr/bin/env python3
"""
Orquestrador de pesquisa CPG Brasil.

Executa 3 fontes em paralelo:
  1. last30days (global — Reddit, YouTube, X, HN, etc.)
  2. Agent-Reach (web/social — web, YouTube, RSS, GitHub)
  3. Crawler BR (setorial — 13 fontes brasileiras)

Produz briefing executivo unificado em PT-BR seguindo o contrato de síntese
do last30days adaptado: badge, O que aprendemos, PADRÕES-CHAVE, footer.

Usage:
    python3 orchestrate.py --template panorama
    python3 orchestrate.py --template varejo --output md
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── Paths ───────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parents[3]  # exocortex.saas/
SKILL_DIR = Path(__file__).resolve().parent.parent

L30D_ENGINE = os.path.expanduser(
    "~/.hermes/skills/research/last30days/scripts/last30days.py"
)
L30D_PYTHON = "/usr/sbin/python3.14"

AGENT_REACH_ADAPTER = os.path.expanduser(
    "~/.hermes/skills/excrtx/excrtx-integrate-agent-reach/scripts/agent_reach_adapter.py"
)
AGENT_REACH_VENV = os.path.expanduser(
    "~/.hermes/skills/excrtx/excrtx-integrate-agent-reach/.venv"
)

CRAWLER_CLI = str(REPO_ROOT / "tools" / "excrtx_crawler_brasil" / "cli.py")
GOOGLE_TRENDS_CLI = "tools.excrtx_source_google_trends.cli"
RECLAMEAQUI_CLI = "tools.excrtx_source_reclameaqui.cli"
CNPJ_CLI = "tools.excrtx_source_cnpj.cli"


# ── Templates ───────────────────────────────────────────────────────────────

TEMPLATES = {
    "panorama": {
        "l30d_query": '"consumer goods" OR "CPG" OR "FMCG" Brazil industry trends',
        "l30d_subreddits": "supplychain,manufacturing,business",
        "l30d_search": "reddit,youtube",
        "ar_query": '"indústria de bens de consumo" Brasil tendências 2026',
        "ar_channels": "web,youtube",
        "cr_domain": "cpg",
        "label": "Panorama Setorial CPG",
    },
    "varejo": {
        "l30d_query": "Brazil retail supermarket consumer spending trends",
        "l30d_subreddits": "business,economy",
        "l30d_search": "reddit,youtube",
        "ar_query": "consumo Brasil varejo supermercado tendências 2026",
        "ar_channels": "web,youtube,rss",
        "ar_rss": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB?hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "cr_domain": "varejo",
        "cr_sources": "superhiper,supervarejo,scanntech",
        "label": "Varejo e Consumo",
    },
    "inovacao": {
        "l30d_query": "sustainable packaging innovation food beverage industry",
        "l30d_subreddits": "packaging,sustainability,manufacturing",
        "l30d_search": "reddit,youtube",
        "ar_query": "embalagens sustentáveis inovação indústria alimentos Brasil",
        "ar_channels": "web,youtube",
        "cr_domain": "embalagens",
        "cr_sources": "embalagem-marca,food-connection",
        "label": "Inovação e Embalagens",
    },
    "limpeza": {
        "l30d_query": "household cleaning products market trends Brazil",
        "l30d_subreddits": "cleaning,business",
        "l30d_search": "reddit,youtube",
        "ar_query": "produtos limpeza doméstica Brasil mercado tendências 2026",
        "ar_channels": "web,youtube",
        "cr_domain": "cpg",
        "cr_sources": "household-innovation,embalagem-marca,superhiper",
        "label": "Limpeza e Household",
    },
    "supply": {
        "l30d_query": "supply chain logistics Brazil manufacturing challenges",
        "l30d_subreddits": "supplychain,logistics,manufacturing",
        "l30d_search": "reddit,youtube",
        "ar_query": "logística supply chain Brasil indústria desafios 2026",
        "ar_channels": "web,youtube",
        "cr_domain": "cpg",
        "cr_sources": "valor-economico,exame,infomoney",
        "label": "Supply Chain e Logística",
    },
}


# ── Dispatcher ──────────────────────────────────────────────────────────────

def run_last30days(template: dict, days: int = 30) -> Optional[dict]:
    """Executa o engine last30days e retorna JSON parseado."""
    query = template["l30d_query"]
    subreddits = template.get("l30d_subreddits", "")
    search = template.get("l30d_search", "reddit,youtube")

    cmd = [
        L30D_PYTHON, L30D_ENGINE,
        query,
        f"--days={days}",
        f"--search={search}",
        f"--subreddits={subreddits}",
        "--emit=json",
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=180,
            env={**os.environ, "OPENROUTER_API_KEY": ""},  # usa config local
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception:
        pass
    return None


def run_agent_reach(template: dict) -> list[dict]:
    """Executa o adaptador Agent-Reach e retorna itens."""
    query = template["ar_query"]
    channels = template.get("ar_channels", "web,youtube")
    rss_url = template.get("ar_rss", "")

    args = [
        sys.executable, AGENT_REACH_ADAPTER,
        "search", query,
        "--channels", channels,
        "--limit", "10",
    ]
    if rss_url:
        args.extend(["--rss-url", rss_url])

    try:
        env = os.environ.copy()
        env["PATH"] = f"{AGENT_REACH_VENV}/bin:{env.get('PATH', '')}"
        result = subprocess.run(args, capture_output=True, text=True, timeout=90, env=env)
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception:
        pass
    return []


def run_crawler(template: dict) -> list[dict]:
    """Executa o crawler brasileiro e retorna itens."""
    domain = template.get("cr_domain", "cpg")
    sources = template.get("cr_sources", "")

    args = [
        sys.executable, "-m", "tools.excrtx_crawler_brasil.cli",
        "--domain", domain,
        "--limit", "10",
    ]
    if sources:
        args.extend(["--sources", sources])

    try:
        result = subprocess.run(
            args, capture_output=True, text=True, timeout=120,
            cwd=str(REPO_ROOT),
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception:
        pass
    return []


def _run_json_cli(args: list[str], timeout: int = 90) -> dict | None:
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(REPO_ROOT),
        )
    except Exception:
        return None
    stdout = (result.stdout or "").strip()
    if not stdout:
        return None
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return None


def run_google_trends(brand: str | None, period: str = "5y", geo: str = "BR") -> dict | None:
    if not brand:
        return None
    return _run_json_cli(
        [sys.executable, "-m", GOOGLE_TRENDS_CLI, brand, "--output", "json", "--period", period, "--geo", geo],
        timeout=120,
    )


def run_reclameaqui(company: str | None) -> dict | None:
    if not company:
        return None
    return _run_json_cli(
        [sys.executable, "-m", RECLAMEAQUI_CLI, company, "--output", "json"],
        timeout=90,
    )


def run_cnpj_source(cnpj: str | None) -> dict | None:
    if not cnpj:
        return None
    return _run_json_cli(
        [sys.executable, "-m", CNPJ_CLI, cnpj, "--output", "json"],
        timeout=90,
    )


# ── Síntese ─────────────────────────────────────────────────────────────────

def synthesize(template_name: str, template: dict, l30d: Optional[dict],
               ar_items: list[dict], cr_items: list[dict],
               trends_payload: Optional[dict] = None,
               reclame_payload: Optional[dict] = None,
               cnpj_payload: Optional[dict] = None) -> str:
    """Produz briefing executivo unificado em PT-BR."""

    label = template.get("label", template_name)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    l30d_version = "3.3.2"

    lines = []

    # ── BADGE ──
    l30d_count = sum(l30d.get("items_by_source", {}).values()) if l30d else 0
    ar_count = len(ar_items)
    cr_count = len(cr_items)
    total = l30d_count + ar_count + cr_count

    lines.append(f"📊 CPG Brasil · {label} · {today}")
    lines.append(f"   Fontes: last30days ({l30d_count} itens) + Agent-Reach ({ar_count}) + Crawler BR ({cr_count}) = {total} total")
    lines.append("")

    # ── O QUE APRENDEMOS ──
    lines.append("**O que aprendemos:**")
    lines.append("")

    # Coleta itens por fonte
    l30d_clusters = []
    if l30d:
        for c in l30d.get("clusters", []):
            evidence = c.get("evidence", [])
            if evidence:
                l30d_clusters.append({
                    "title": c.get("title", ""),
                    "evidence": evidence,
                    "why": c.get("why", ""),
                })

    # Gera parágrafos de síntese
    insights = []

    # 1. Crawler BR insights (prioridade: setorial brasileiro)
    for item in cr_items[:5]:
        title = item.get("title", "")
        source = item.get("source", "")
        date = item.get("date", "")
        url = item.get("url", "")
        snippet = item.get("snippet", "")[:200]
        if title:
            insights.append(f"**[{source}]** {title} — {snippet} ({date}) [↗]({url})")

    # 2. Agent-Reach insights
    ar_added = 0
    for item in ar_items:
        if ar_added >= 3:
            break
        title = item.get("title", "")
        source = item.get("source", "")
        date = item.get("date", "")
        url = item.get("url", "")
        if title and len(title) > 15 and "youtube" not in source:
            insights.append(f"**[{source}·AR]** {title} ({date}) [↗]({url})")
            ar_added += 1

    # 3. last30days insights (filtra ruído)
    l30d_added = 0
    for cluster in l30d_clusters:
        if l30d_added >= 3:
            break
        title = cluster["title"]
        why = cluster.get("why", "")
        # Pula clusters irrelevantes
        skip_words = ["roborock", "k-pop", "sixers", "draft", "blue lock", "gothic", "polymarket"]
        if any(w in title.lower() for w in skip_words):
            continue
        evidence = cluster["evidence"]
        if evidence:
            e = evidence[0]
            insights.append(f"**[l30d]** {title} — ({e.get('source', '')}, {e.get('published_at', '')}) [↗]({e.get('url', '')})")
            l30d_added += 1

    # 4. Fontes públicas estruturadas (opcionais por marca/empresa)
    if trends_payload and not trends_payload.get("errors"):
        trend_data = trends_payload.get("data", {})
        brand = (trend_data.get("termos") or [trends_payload.get("query") or "marca"])[0]
        serie = trend_data.get("serie_temporal", {}).get(brand, [])
        geo_data = trend_data.get("interesse_por_regiao", {}).get(brand, {})
        if serie:
            peak = max(serie, key=lambda item: item.get("value") or 0)
            region_txt = ""
            if geo_data:
                top_region = max(geo_data.items(), key=lambda item: item[1] or 0)
                region_txt = f" Região líder: {top_region[0]} ({top_region[1]})."
            insights.append(
                f"**[google-trends]** {brand} atingiu pico relativo de busca em {peak.get('date')} (índice {peak.get('value')}).{region_txt} "
                f"[↗]({trends_payload.get('provenance', {}).get('url', '')})"
            )

    if reclame_payload and not reclame_payload.get("errors"):
        ra_data = reclame_payload.get("data", {})
        if ra_data.get("nota_geral") is not None or ra_data.get("total_reclamacoes") is not None:
            insights.append(
                f"**[reclameaqui]** {ra_data.get('empresa') or reclame_payload.get('query')} tem nota {ra_data.get('nota_geral')} "
                f"com {ra_data.get('total_reclamacoes')} reclamações e taxa de resolução {ra_data.get('taxa_resolucao')}. "
                f"[↗]({reclame_payload.get('provenance', {}).get('url', '')})"
            )

    if cnpj_payload and not cnpj_payload.get("errors"):
        cnpj_data = cnpj_payload.get("data", {})
        if cnpj_data.get("razao_social"):
            insights.append(
                f"**[cnpj]** {cnpj_data.get('razao_social')} está com situação cadastral {cnpj_data.get('situacao_cadastral')} "
                f"e abertura em {cnpj_data.get('data_abertura') or 'data não informada'}. "
                f"[↗]({cnpj_payload.get('provenance', {}).get('url', '')})"
            )

    # Emite insights
    for i, insight in enumerate(insights[:8]):
        lines.append(f"{insight}")
        lines.append("")

    if not insights:
        lines.append("Nenhum sinal relevante encontrado nas três fontes no período.")
        lines.append("")

    # ── PADRÕES-CHAVE ──
    lines.append("**PADRÕES-CHAVE da pesquisa:**")
    lines.append("")

    pattern_idx = 1

    # Conta fontes por domínio
    cr_sources = {}
    for item in cr_items:
        s = item.get("source", "?")
        cr_sources[s] = cr_sources.get(s, 0) + 1

    if cr_sources:
        top_sources = sorted(cr_sources.items(), key=lambda x: -x[1])[:3]
        lines.append(f"{pattern_idx}. **Cobertura setorial BR:** {len(cr_items)} itens de {len(cr_sources)} fontes brasileiras. Maior volume: {', '.join(f'{s} ({n})' for s, n in top_sources)}.")
        pattern_idx += 1

    if ar_items:
        ar_sources = {}
        for item in ar_items:
            s = item.get("source", "?")
            ar_sources[s] = ar_sources.get(s, 0) + 1
        lines.append(f"{pattern_idx}. **Alcance web/social:** {len(ar_items)} itens via Agent-Reach de {len(ar_sources)} fontes.")
        pattern_idx += 1

    if l30d and l30d.get("clusters"):
        relevant = [c for c in l30d["clusters"] if sum(1 for w in ["roborock","k-pop","sixers","draft","blue lock","gothic","polymarket"] if w in c.get("title","").lower()) == 0]
        if relevant:
            lines.append(f"{pattern_idx}. **Cobertura global:** {len(relevant)} clusters relevantes via last30days. Fontes: {', '.join(l30d.get('items_by_source',{}).keys())}.")
            pattern_idx += 1

    structured_hits = []
    if trends_payload and not trends_payload.get("errors"):
        trend_brand = ((trends_payload.get("data") or {}).get("termos") or [trends_payload.get("query") or "marca"])[0]
        trend_regions = ((trends_payload.get("data") or {}).get("interesse_por_regiao") or {}).get(trend_brand, {})
        structured_hits.append(f"Google Trends ({len(trend_regions)} regiões)")
    if reclame_payload and not reclame_payload.get("errors"):
        ra_data = reclame_payload.get("data") or {}
        structured_hits.append(f"Reclame Aqui (nota {ra_data.get('nota_geral')}, {ra_data.get('total_reclamacoes')} reclamações)")
    if cnpj_payload and not cnpj_payload.get("errors"):
        cnpj_data = cnpj_payload.get("data") or {}
        structured_hits.append(f"CNPJ ({cnpj_data.get('situacao_cadastral') or 'situação n/d'})")
    if structured_hits:
        lines.append(f"{pattern_idx}. **Fontes públicas estruturadas:** {' · '.join(structured_hits)}.")
        pattern_idx += 1

    # Emoji-footer
    lines.append("")
    lines.append("---")
    emoji_sources = []
    if cr_items:
        emoji_sources.append("🇧🇷 crawler-brasil")
    if ar_items:
        emoji_sources.append("🌐 agent-reach")
    if l30d and l30d.get("clusters"):
        emoji_sources.append("📰 last30days")
    if trends_payload and not trends_payload.get("errors"):
        emoji_sources.append("📈 google-trends")
    if reclame_payload and not reclame_payload.get("errors"):
        emoji_sources.append("🧾 reclame-aqui")
    if cnpj_payload and not cnpj_payload.get("errors"):
        emoji_sources.append("🏢 cnpj")
    lines.append(f"✅ {' · '.join(emoji_sources)}")
    lines.append(f"   {total} itens + sinais estruturados · {today}")

    return "\n".join(lines)


# ── CLI ─────────────────────────────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(
        prog="orchestrate",
        description="Orquestrador de pesquisa CPG Brasil — 3 fontes em paralelo",
    )
    parser.add_argument("--template", "-t", default="panorama",
                       choices=list(TEMPLATES.keys()),
                       help="Template de pesquisa")
    parser.add_argument("--days", type=int, default=30,
                       help="Período em dias (default: 30)")
    parser.add_argument("--output", "-o", choices=["md", "json"], default="md",
                       help="Formato de saída")
    parser.add_argument("--skip-l30d", action="store_true",
                       help="Pula last30days (mais rápido, útil para testes)")
    parser.add_argument("--company", help="Empresa-alvo para enriquecer com Reclame Aqui", default="")
    parser.add_argument("--brand", help="Marca/termo para enriquecer com Google Trends", default="")
    parser.add_argument("--cnpj", help="CNPJ para enriquecer com dados cadastrais", default="")
    parser.add_argument("--trends-period", default="5y", help="Período do Google Trends (default: 5y)")
    parser.add_argument("--trends-geo", default="BR", help="Geo do Google Trends (default: BR)")
    args = parser.parse_args()

    template = TEMPLATES[args.template]
    print(f"🔍 Orquestrando pesquisa: {template['label']}", file=sys.stderr)
    print(f"   Fontes: last30days + Agent-Reach + Crawler BR", file=sys.stderr)

    # Dispara as 3 fontes
    l30d_result = None
    if not args.skip_l30d:
        print("   ⏳ last30days (30-120s)...", file=sys.stderr)
        l30d_result = run_last30days(template, args.days)

    print("   ⏳ Agent-Reach (10-60s)...", file=sys.stderr)
    ar_items = run_agent_reach(template)

    print("   ⏳ Crawler BR (10-30s)...", file=sys.stderr)
    cr_items = run_crawler(template)

    brand = args.brand or args.company
    trends_payload = None
    reclame_payload = None
    cnpj_payload = None

    if brand:
        print(f"   ⏳ Google Trends ({brand})...", file=sys.stderr)
        trends_payload = run_google_trends(brand, period=args.trends_period, geo=args.trends_geo)
    if args.company:
        print(f"   ⏳ Reclame Aqui ({args.company})...", file=sys.stderr)
        reclame_payload = run_reclameaqui(args.company)
    if args.cnpj:
        print(f"   ⏳ CNPJ ({args.cnpj})...", file=sys.stderr)
        cnpj_payload = run_cnpj_source(args.cnpj)

    synthesis = synthesize(
        args.template,
        template,
        l30d_result,
        ar_items,
        cr_items,
        trends_payload=trends_payload,
        reclame_payload=reclame_payload,
        cnpj_payload=cnpj_payload,
    )

    if args.output == "json":
        output = {
            "template": args.template,
            "label": template["label"],
            "last30days": {
                "clusters": len(l30d_result.get("clusters", [])) if l30d_result else 0,
                "items_by_source": l30d_result.get("items_by_source", {}) if l30d_result else {},
            } if l30d_result else None,
            "agent_reach": {"count": len(ar_items)},
            "crawler_br": {"count": len(cr_items)},
            "structured_sources": {
                "google_trends": trends_payload,
                "reclameaqui": reclame_payload,
                "cnpj": cnpj_payload,
            },
            "synthesis": synthesis,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(synthesis)

    print(f"\n✅ Pesquisa concluída", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
