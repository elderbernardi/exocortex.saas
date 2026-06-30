---
name: excrtx-integrate-last30days
description: Operate and maintain the last30days research skill — a multi-platform
  search engine that scans 15 sources across the last 30 days. Covers installation,
  provider configuration, env isolation, patching, testing, and SC credit/JSON quirks.
version: 1.2.0
category: excrtx
platforms:
- linux
author: Exocórtex
metadata:
  hermes:
    tags:
    - exocortex
    - last30days
    - research
    - integration
    - deepseek
    - multi-source
    related_skills:
    - excrtx-memory-manager
    - excrtx-govern-tools
---
# last30days Integration
v1.2.0 changelog: added SC "one-shot 200" trap diagnostic (§1.1 of references/scrapecreators-credits-and-sandbox-env.md), new pre-flight probe script `scripts/diagnose-sc-key.sh`, and corresponding pitfall in SKILL.md.
# last30days Integration

Operate the `mvanhorn/last30days-skill` (43k⭐, MIT) within the Exocórtex ecosystem.
This is a **community skill** integrated as a canonical research tool (EX-57).

## When to Use

Activate when:
- The executive asks to research a topic across social media and web sources
- The executive asks about last30days configuration, sources, or keys
- last30days needs provider reconfiguration (model, API key, endpoint)
- last30days engine fails with HTTP errors (401, 402, timeout)
- The executive wants to audit which sources are active and which are missing

**Don't use for:** General web search (use browser/search tools). DocBrain document processing (use `excrtx-integrate-docbrain`). NotebookLM research workflows (use `excrtx-integrate-nlmops`).

## Architecture

```
skills/last30days/            # Canonical copy (versioned in repo)
├── SKILL.md                  # 1735-line skill contract
├── scripts/
│   ├── last30days.py         # 1042-line CLI engine (Python 3.12+)
│   └── lib/                  # 60+ source modules
├── .env.example              # All optional keys documented
└── agents/                   # AI agent configs
```

Symlink: `~/.hermes/skills/research/last30days` → repo canonical.

**Pre-flight probe:** before launching a research pipeline that needs
ScrapeCreators-backed sources (TikTok/Instagram/Threads/Pinterest), run
`scripts/diagnose-sc-key.sh` to confirm the key is healthy. The script
fires 3 sequential pings 2s apart and classifies the result
(healthy / one-shot / dead / bad-key / upstream-down) with an exit code
the agent can branch on. Exit code 1 = "one-shot 200 trap" — do NOT run
the engine with that key.

## Procedure

### 1. Verify Installation

```bash
# Check Hermes sees the skill
hermes skills list | grep last30days
```bash
# Check engine works
python3.14 skills/last30days/scripts/last30days.py --help

# Diagnose available sources
python3.14 skills/last30days/scripts/last30days.py --diagnose
```

### 2. Configure Provider (central Exocórtex roles)

The engine requires an LLM for planning/reranking (reasoning) and, optionally, vision. **You do not configure these keys here.** `skills/last30days/scripts/lib/env.py` seeds the engine's reasoning/vision config from the central Exocórtex LLM roles when last30days' own keys are absent:

- **reasoning** ← **default** role (`EXOCORTEX_DEFAULT_{PROVIDER,MODEL,API_KEY,BASE_URL}`). When `LAST30DAYS_REASONING_PROVIDER` is `auto`/unset, the default role drives the provider and fills the matching key slot (e.g. `openrouter`→`OPENROUTER_API_KEY`).
- **vision** ← **vision** role (`EXOCORTEX_VISION_*`), which inherits the default role field-by-field when empty.

Providers last30days cannot serve (e.g. `deepseek`) are simply skipped — no regression; reasoning stays on its existing path or local fallback. Configure the roles via `bash setup.sh` or `.env.local`; the resolvers are `scripts/lib/llm_roles.py` / `setup/lib/llm-roles.sh`.

**Config file:** `~/.config/last30days/.env` — reserve this for last30days' own model/source tuning and the scraping keys below. Pin model/provider here only to override the seeded role:

```bash
# Optional: override the role-seeded reasoning provider/model
LAST30DAYS_REASONING_PROVIDER=openrouter
LAST30DAYS_OPENROUTER_BASE_URL=https://api.deepseek.com/v1/chat/completions
LAST30DAYS_OPENROUTER_MODEL=deepseek-v4-flash
LAST30DAYS_PLANNER_MODEL=deepseek-v4-flash
LAST30DAYS_RERANK_MODEL=deepseek-v4-flash
```

**Python version:** The engine requires Python 3.12+. On Arch Linux (rolling), the system package provides:
```bash
/usr/sbin/python3.14
```
Verify with `python3.14 --version`. uv-managed Pythons (e.g., `~/.local/share/uv/python/`) may lag behind the system package on rolling distros — prefer the system binary when available.

### 3. Run Research

**Quick smoke test (~6s):**
```bash
env -u OPENROUTER_API_KEY python3.14 skills/last30days/scripts/last30days.py \
  "AI coding tools" --days=7 --search=reddit --emit=json
```

**Full pipeline with query plan (60-180s):**
```bash
SKILL_DIR="$HOME/.hermes/skills/research/last30days"
QUERY_PLAN_FILE="/tmp/last30days_query_plan.json"
SAVE_DIR="$HOME/Documents/Last30Days"
mkdir -p "$SAVE_DIR"

# Write your query plan (see references/query-plan-schema.md)
# Then run with --plan, --subreddits, and save flags:
env -u OPENROUTER_API_KEY \
  LAST30DAYS_PYTHON=/usr/sbin/python3.14 \
  /usr/sbin/python3.14 "$SKILL_DIR/scripts/last30days.py" \
  "consumer goods manufacturing trends" \
  --plan "$QUERY_PLAN_FILE" \
  --subreddits "supplychain,manufacturing,logistics" \
  --emit compact \
  --save-dir "$SAVE_DIR" \
  --save-suffix v3
```

**Env var `LAST30DAYS_PYTHON`** tells the engine which Python binary to use. Set it once before the command — cleaner than hardcoding the path in every invocation. The engine respects it for subprocess calls.

### 4. Supplement Thin B2B/Regional Results

When the engine returns <5 relevant items (common for B2B, industrial, or regional Brazilian companies), **do not stop at the engine output**. Layer on a structured fallback pipeline:

**Trigger — false-positive clusters:** If ALL evidence clusters in the engine output carry annotations like `Why: No mention of [topic]`, the engine data is a false positive. Do NOT attempt to build a `What I learned:` narrative from zero-relevance items — you will fabricate insight from noise. Acknowledge the gap, explain why (wrong platform ecosystem for this topic class), and route to the fallback pipeline.

See `references/regional-brazilian-zero-signal.md` for a concrete session example (Zaffari supermarket chain).

#### 4a. Google News RSS (best fallback — no captcha, no JS)

```bash
# Format: URL-encode the query, set hl/pt-BR and gl/BR for Brazilian results
curl -s "https://news.google.com/rss/search?q=$(python3 -c 'import urllib.parse; print(urllib.parse.quote("\"Nome da Empresa\""))')&hl=pt-BR&gl=BR&ceid=BR:pt-419"
```

Parse items with regex — the RSS is clean XML, no captcha:
```python
import re
items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
for item in items:
    title = re.search(r'<title>(.*?)</title>', item)
    pubdate = re.search(r'<pubDate>(.*?)</pubDate>', item)
    source = re.search(r'<source[^>]*>(.*?)</source>', item)
```

**Coverage:** Google News indexes trade publications, local press, and industry portals — exactly the sources the social engine misses for B2B.

#### 4b. Direct trade/industry site access

For Brazilian companies: ACATS (acats.com.br), FIESC (fiesc.com.br), SEGS (segs.com.br), and regional news portals often serve clean HTML to curl with a desktop User-Agent. Prefer `curl` over `browser_navigate` — these sites are lighter on JS than global search engines.

#### 4c. When all web supplements fail

If Google News RSS returns irrelevant results and direct sites block: flag the research as "low digital surface area" in the synthesis, acknowledge the gap explicitly, and recommend the executive supplement with offline knowledge (trade show contacts, industry associations, direct outreach).

See `references/google-news-rss-fallback.md` for query templates and the parsing script.

For **competitive digital maturity assessment** — probing competitor websites with curl to map digital presence, IA adoption, and sector-wide gaps — see `references/competitive-digital-maturity.md`. Use this when the executive asks "what are competitors doing with AI/tech?" or needs a sales-visit competitive landscape for B2B companies in low-tech sectors.

### 5. Enable Social Sources (Optional)

Add keys to `~/.config/last30days/.env`:
- `XAI_API_KEY` → X/Twitter (fastest breaking-news signal)
- `SCRAPECREATORS_API_KEY` → TikTok, Instagram, Threads, Pinterest (free 100 credits)
- `BSKY_HANDLE` + `BSKY_APP_PASSWORD` → Bluesky
- `BRAVE_API_KEY` → Web search for auto-resolve

### 6. Verify Functioning

```bash
cd exocortex.saas && env -u OPENROUTER_API_KEY \
  python3 -m unittest tests.test_last30days_integration -v
```

## Provider Patch Reference

Three custom functions in `skills/last30days/scripts/lib/providers.py` enable DeepSeek:

- `_openrouter_url()` — lazy-resolves `LAST30DAYS_OPENROUTER_BASE_URL` from env or config file
- `_openrouter_default_model()` — lazy-resolves `LAST30DAYS_OPENROUTER_MODEL`
- `_MODEL_DEFAULTS["openrouter"]` — uses the functions instead of hardcoded constants

These functions read from `os.environ` first, then fall back to reading the config file directly (because the engine loads `.env` into a dict, not `os.environ`).

## Available Sources

### Free (no API key)
Reddit (RSS), Hacker News (Algolia), YouTube (yt-dlp), Polymarket (API), GitHub (gh CLI)

### Requires API key
X/Twitter, TikTok, Instagram, Threads, Pinterest, Bluesky, TruthSocial, Web Search, Deep Research

## Pitfalls

- **OPENROUTER_API_KEY conflict:** the engine reads `OPENROUTER_API_KEY` from `os.environ` with higher priority than its own config file. This var can be present in the Hermes environment (the **default** role exports it when its provider is `openrouter`, and `env.py` also seeds it into the engine config from that role). If you pin a *different* provider key in `~/.config/last30days/.env`, run with `env -u OPENROUTER_API_KEY` to force the engine to read your config-file key instead of the inherited one.
- **Python version:** The engine requires `MIN_PYTHON = (3, 12)`. On Arch rolling, system python3 defaults to 3.11 but `/usr/sbin/python3.14` is available. Use it directly — do not assume uv-managed interpreters are present.
- **Model name `deepseek-chat` is deprecated:** Use `deepseek-v4-flash` for planning/reranking or `deepseek-v4-pro` for higher quality. Verify available models with: `curl -s https://api.deepseek.com/v1/models -H "Authorization: Bearer $DEEPS....
- **401 Unauthorized = wrong key:** The engine debug prints key prefix — if it shows `sk-or-v1...` (OpenRouter format, 73 chars) instead of `sk-9acc...` (DeepSeek format, 35 chars), the `OPENROUTER_API_KEY` from Hermes env is leaking.
- **402 Payment Required = no credits:** OpenRouter key has no credits. Switch to DeepSeek or add funds.
- **Reddit 403 Forbidden errors:** The engine attempts two Reddit access methods: `RedditPublic` (requires authenticated API key via SCRAPECREATORS) and `RedditKeyless` (uses RSS, no auth required). If you see `[RedditPublic] 403 forbidden` errors but `[RedditKeyless]` requests succeed, the SCRAPECREATORS_API_KEY is missing, invalid, or lacks Reddit scope. The engine automatically falls back to RedditKeyless when Public fails — check your `~/.config/last30days/.env` for a valid SCRAPECREATORS_API_KEY with Reddit permissions.
- **Hub install blocked:** `hermes skills install mvanhorn/last30days-skill` is blocked by the security scanner (50 findings, CRITICAL persistence/exfiltration). Install manually via the canonical copy in the repo.
- **`skill_view(name='last30days')` returns "ambiguous":** Two skills share the bare name — `excrtx/last30days` (the bare skill installed in `skills/excrtx/`) and `research/last30days` (the canonical copy in `skills/research/`). Hermes refuses to guess. Use the qualified path `excrtx-integrate-last30days` to load the integration skill, or `research/last30days` to load the upstream. When the executive asks to invoke "last30days", they mean the engine — reference the canonical copy path directly, not the integration skill, when constructing CLI commands.
- **Agent-Reach is NOT a TikTok fallback:** The community CLI at `Panniantong/Agent-Reach` (v1.4.2+) ships channels for web, youtube, reddit, twitter, github, linkedin, bilibili, xiaohongshu, xueqiu, xiaoyuzhou, v2ex, rss, exa — but **no TikTok or Douyin**. Douyin was explicitly removed in v1.4.2 ("诚实瘦身：移除失修渠道"). When a research question demands TikTok signal and SC credits are out, do NOT install Agent-Reach expecting it to fill the gap. Realistic TikTok fallbacks in priority order: (1) `APIFY_API_TOKEN` (last30days has an Apify integration), (2) Playwright with a real Chrome session logged into TikTok, (3) accept "low TikTok signal" and lean on YouTube/Reddit/Web as proxies. See `references/agent-reach-vs-last30days.md` for the full capability map.
- **TikTok blocks 4 unauthenticated paths:** Without a real msToken/session cookie, these all return 0 or 403 — (1) Playwright browser navigation (`browser_navigate` returns empty snapshot, "bot detection"), (2) `https://www.tiktok.com/api/tag/<hashtag>/` (returns `{"status_code":0,"status_msg":"url doesn't match"}`), (3) `https://m.tiktok.com/api/tag/<hashtag>/` (same), (4) `https://www.tiktok.com/node/share/tag/<hashtag>` (403). The official TikTok-Research-API is the only stable unauthenticated path and requires academic approval. For one-off pulls, ask the executive to log into TikTok in their local Chrome once, then `~/.config/google-chrome/Default/Cookies` will carry the session cookies (encrypted) — but the cookie is bound to the user's Chrome session and Playwright reuse requires a Chrome profile launched with `--user-data-dir` pointing at that profile.
- **ScrapeCreators returns 402 "out of credits" silently:** The engine reports `has_scrapecreators: true` in `--diagnose` (the key is loaded), but the SC API itself answers `{"success":false,"message":"Looks like you're out of credits :("}` with HTTP 402 on every call. The engine then returns 0 items for TikTok/Instagram/Threads/Pinterest with no top-level error — only a noisy line in stderr. **Symptom:** `--search tiktok,instagram` returns 0 videos despite working before. **Fix:** call SC directly with `curl -H "x-api-key: $SCRAPECREATORS_API_KEY" "https://api.scrapecreators.com/v1/tiktok/search/keyword?query=test&count=1"` — if it returns 402, the key needs a top-up. Top-ups start at $5–10 and last for a typical research month. **Distinguish from 401 (bad key format) and 502/504 (SC upstream down)** — they look identical in engine stderr. See `references/scrapecreators-credits-and-sandbox-env.md` for the full diagnostic recipe.
- **SC "one-shot 200" trap (2026-06-22):** A freshly-copied SC key can return `{"success":true,"credits_remaining":99}` on the very first direct ping and then 402 on every subsequent call — even with the same key, same endpoint, seconds apart. The `--diagnose` output still says `has_scrapecreators: true`, so you cannot rely on it. **Diagnostic:** hit the endpoint 3 times in a row; if 2/3 are 402, the key is unusable for this session. **Fixes in order:** (1) try a different SC key, (2) wait 5–15 min and re-probe, (3) add `APIFY_API_TOKEN` and let the engine use Apify's TikTok actors, (4) accept zero TikTok signal and synthesize from YouTube+Reddit+Google News RSS. Do NOT run the engine with a one-shot key expecting it to work — the engine will silently return 0 items and waste a 60–180s pipeline run. Full reproduction recipe and hypothesis list in `references/scrapecreators-credits-and-sandbox-env.md` §1.1.
- **execute_code sandbox does not inherit Hermes env:** Each `execute_code` call runs in a fresh Python process — `os.environ` does NOT persist between calls. To pass `SCRAPECREATORS_API_KEY`, `OPENROUTER_API_KEY`, or other keys from `~/.hermes/.env` to a `subprocess.run(...)` that calls the last30days engine, reload the file at the start of every script. See `references/scrapecreators-credits-and-sandbox-env.md` for the working pattern and why `env -u OPENROUTER_API_KEY` alone is not enough.
- **`--emit json` truncates TikTok items even when engine retrieved them:** The compact markdown report shows 20+ TikTok videos with full metadata (views/likes/cmts), but `--emit json` (with `--save-dir` or stdout) often puts `tiktok: 0` in `items_by_source` and lists those same items only inside `clusters[*].representative_ids` (URLs only, no engagement). For TikTok/Instagram analyses, prefer the default compact markdown output captured from stdout and parse clusters from there. The JSON path is reliable for Reddit/YouTube/GitHub/HN; for SC-backed sources, use the markdown report and re-derive with `youtube-dl`/SC if you need structured fields.
- **Engine timeout on first run:** The full pipeline with LLM planning takes 60–180s depending on sources and network (93s observed for a 3-subquery plan with subreddit targeting). Use `--search=reddit` and `--emit=json` for quick smoke tests (~6s). For the full pipeline, set terminal timeout to at least 300s to avoid truncation. If timing out during "Organizing findings" or "Processing Scoring and ranking", the engine may have already retrieved source data — try adding `--emit=json` to see structured output even if the pipeline doesn't complete.
- **yt-dlp not in PATH for engine:** The engine expects `yt-dlp` on PATH. If installed via system package manager, it's at `/usr/sbin/yt-dlp` which is fine.
- **Web search supplements blocked:** Google, Bing, DuckDuckGo, and Brave Search all return captchas when called via curl or browser from this host. The engine's social crawl still works, but post-engine web supplements are unreliable. Use **Google News RSS** as the primary fallback (see Procedure §4a) — it bypasses captcha entirely and indexes trade publications that the social engine misses. The `--auto-resolve` flag enables the engine's own web resolver internally if `BRAVE_API_KEY` or equivalent is configured.
- **Google News RSS date filtering:** The RSS feed returns items across all time, not just the last 30 days. Filter by `<pubDate>` in your parsing step — items older than 30 days should be flagged with `[date:low]` and used only for historical context, not as signals of current activity.
- **Thin results for B2B/industrial topics:** (Reddit, YouTube, X, TikTok). Topics like "consumer goods manufacturing trends" produce sparse results because the conversation happens in trade publications and consulting reports, not social media. When the engine returns <5 relevant items, flag the topic as "low social surface area" in the synthesis, supplement with domain knowledge, and recommend adding `XAI_API_KEY` (X/Twitter) and `SCRAPECREATORS_API_KEY` (TikTok/Instagram) for broader coverage.
- **Step 2.5 file append risk:** The skill contract requires APPENDING to the saved raw file — never overwrite it. Using `write_file` on the raw file will destroy the engine output. Use `patch` with `mode='patch'` or `execute_code` to read + append + write. The raw file path is printed in the engine's `[last30days] Saved output to {path}` log line.

## Verification

- [ ] `hermes skills list | grep last30days` shows `enabled`
- [ ] `python3.14 scripts/last30days.py --diagnose` returns valid JSON with 5 free sources
- [ ] `env -u OPENROUTER_API_KEY python3.14 scripts/last30days.py "test" --search=reddit --emit=json` completes with exit 0
- [ ] Planner shows `source=llm` (not `deterministic`) when the default role (or a config-file reasoning key) is configured
- [ ] `tests/test_last30days_integration.py` passes (11 core tests)
- [ ] `.env.example` in repo matches `~/.config/last30days/.env` structure

## References

- `references/provider-patch-detail.md` — full patch with line numbers and rationale
- `references/query-plan-schema.md` — JSON schema for `--plan` flag with example from CPG session
- `references/google-news-rss-fallback.md` — Google News RSS as captcha-free fallback for B2B/regional topics; includes query templates, parsing script, and Guimarães session example
- `references/competitive-digital-maturity.md` — Competitive digital maturity assessment methodology: curl probes, signal taxonomy, sector benchmarking, and "absence of signal as intelligence" pattern. Guimarães vs Copapel/Girando Sol session example.
- `references/regional-brazilian-zero-signal.md` — Concrete case study: Zaffari supermarket chain returns zero relevant results. Covers false-positive evidence clusters, correct synthesis pattern, and root cause classification for regional Brazilian companies with low social surface area.
- `references/scrapecreators-credits-and-sandbox-env.md` — Diagnosing SC "out of credits" 402 (silent in engine output), reloading `~/.hermes/.env` inside `execute_code` sandboxes, real SC endpoint paths, and the `--emit json` vs compact-markdown divergence for SC-backed sources.
- `references/agent-reach-vs-last30days.md` — Capability map comparing Agent-Reach and last30days coverage (Reddit/YouTube/LinkedIn/XHS/Bilibili/etc), the `skill_view` name-collision (`last30days` matches two skills), the 4 unauthenticated TikTok paths that all return empty, and a 2026-06-23 session showing the right TikTok fallback decision tree.
