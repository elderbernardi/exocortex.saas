# Agent-Reach vs last30days — capability map and platform coverage

Two research CLIs are commonly invoked for "what are people saying about X on
social media" tasks. They are **not interchangeable** — they cover different
platforms, with different cost profiles, and different bot-detection
resistance. This reference maps what each does well, where each fails, and
when to use which.

## Quick decision table

| Need | Tool | Notes |
|------|------|-------|
| Reddit, HN, GitHub, Polymarket, web, YouTube (no auth) | **last30days** | Free, fast, well-maintained |
| X/Twitter (real-time posts) | **last30days** with `XAI_API_KEY` or `AUTH_TOKEN` | Last30days is the only one that handles X cleanly |
| TikTok | **last30days** with `SCRAPECREATORS_API_KEY` (pay-per-credit) | Agent-Reach has no TikTok channel (see below) |
| Instagram, Threads, Pinterest | **last30days** with `SCRAPECREATORS_API_KEY` | Same SC key powers all three |
| YouTube transcripts | **last30days** (uses yt-dlp) | Agent-Reach YouTube channel is shell-only, no transcript extraction |
| Bilibili, Xiaohongshu (XHS), V2EX, Xueqiu, Xiaoyuzhou | **Agent-Reach** | last30days does not cover any of these |
| LinkedIn | **Agent-Reach** | last30days has no LinkedIn module |
| Web search (Brave, Exa, Serper) | **last30days** (with `BRAVE_API_KEY` or `EXA_API_KEY`) | Agent-Reach has Exa only |
| Multi-source synthesis with LLM rerank | **last30days** | Agent-Reach does not synthesize; it just collects |

## last30days — full source list

`mvanhorn/last30days-skill` v3.x. Engine at `scripts/last30days.py`.

### Free sources (no API key)
- Reddit (RSS, no auth required — falls back from SC public API automatically)
- Hacker News (Algolia)
- YouTube (yt-dlp transcript extraction)
- Polymarket (public API)
- GitHub (gh CLI)

### Sources requiring API key
- `XAI_API_KEY` → X/Twitter (Grok API; fastest breaking-news signal)
- `SCRAPECREATORS_API_KEY` → TikTok, Instagram, Threads, Pinterest, YouTube comments
- `BSKY_HANDLE` + `BSKY_APP_PASSWORD` → Bluesky
- `AUTH_TOKEN` + `CT0` → X/Twitter via browser cookie (alternative to Grok)
- `BRAVE_API_KEY` / `EXA_API_KEY` / `SERPER_API_KEY` / `PARALLEL_API_KEY` → Web search backends
- `OPENROUTER_API_KEY` → Perplexity Deep Research mode (~$0.90/query, opt-in via `--deep-research`). Seeded from the central **default** LLM role (`EXOCORTEX_DEFAULT_*`) by `lib/env.py` when its provider is `openrouter`; not set by hand in last30days.

### Cost profile
- 100 free SC credits at signup, then pay-as-you-go starting at $5
- A typical 3-subquery plan touches 4-6 sources and uses ~10-20 SC credits for SC-backed sources

## Agent-Reach — full source list

`Panniantong/Agent-Reach` v1.4.2+. Channels at
`agent_reach/channels/` — definitive list (verified 2026-06-23):

| Channel | File | Notes |
|---------|------|-------|
| `web` | `web.py` | Generic web search via DuckDuckGo/Google scraper; captcha-prone |
| `youtube` | `youtube.py` | YouTube video metadata; no transcript extraction |
| `reddit` | `reddit.py` | Reddit public JSON; no auth required for read |
| `twitter` | `twitter.py` | X/Twitter via cookie auth; needs `AUTH_TOKEN` + `CT0` |
| `github` | `github.py` | GitHub search via gh CLI; needs `gh` auth |
| `linkedin` | `linkedin.py` | LinkedIn public profile/search; captcha-prone |
| `bilibili` | `bilibili.py` | B站 (Chinese video) |
| `xiaohongshu` | `xiaohongshu.py` | XHS / 小红书 (Chinese social) — needs `OpenCLI` browser extension |
| `xueqiu` | `xueqiu.py` | 雪球 (Chinese finance) |
| `xiaoyuzhou` | `xiaoyuzhou.py` | 小宇宙 (Chinese podcast) |
| `v2ex` | `v2ex.py` | V2EX (Chinese tech forum) |
| `rss` | `rss.py` | Generic RSS feed reader |
| `exa_search` | `exa_search.py` | Exa web search (needs `EXA_API_KEY`) |

### Channels Agent-Reach does NOT have (verified)

- **TikTok** — no channel file in `agent_reach/channels/`. Confirmed absent.
- **Douyin** — explicitly removed in v1.4.2 (CHANGELOG: "诚实瘦身：移除失修渠道，新增转写与 doctor --json")
- **Instagram** — no channel
- **Threads** — no channel
- **Pinterest** — no channel
- **Bluesky** — no channel
- **Polymarket** — no channel
- **Hacker News** — no channel
- **Mastodon** — no channel

Do NOT install Agent-Reach expecting it to fill a TikTok gap. It will not.

## When last30days cannot deliver

Real session example (2026-06-23, executive asked "TikTok cleaning tips
trends"):

1. **SC credits exhausted** — `SCRAPECREATORS_API_KEY` in `~/.hermes/.env`
   valid format but account at 0 credits. All SC endpoints return HTTP 402
   `{"success":false,"message":"Looks like you're out of credits :("}`.
   `--diagnose` still reports `has_scrapecreators: true` (key loaded ≠
   credits available). Last30days silently returns 0 TikTok/Instagram/Threads
   items. **Diagnostic recipe:** `curl -s -o /dev/null -w "%{http_code}\n"
   -H "x-api-key: $SCRAPECREATORS_API_KEY"
   "https://api.scrapecreators.com/v1/tiktok/search/keyword?query=test&count=1"`
   — 200 = OK, 402 = out of credits.

2. **Agent-Reach as alternative** — checked v1.4.2 channel list, no TikTok.
   Rejected as fallback. Installing it for this query wastes time.

3. **Browser automation (Playwright via Hermes `browser_navigate`)** — TikTok
   detects bot, returns empty page. Stealth features listed as `["local"]`
   (no residential proxy). Bot detection in 2026 is more aggressive.

4. **Public JSON endpoints** — `https://www.tiktok.com/api/tag/cleantok/`
   returns `{"status_code":0,"status_msg":"url doesn't match"}` without a
   valid `msToken` (msToken comes from a logged-in session, not from
   `User-Agent` spoofing). `https://www.tiktok.com/node/share/tag/cleantok`
   returns 403 Forbidden from a `TLB` (TikTok Load Balancer) block.

5. **Honest acknowledgment** — reported "low TikTok signal" with the
   5 videos first-call last30days retrieved before credits ran out
   (the only defensible primary source). YouTube reviewers testing TikTok
   hacks and Reddit discussions on cleaning routines used as proxies. Did
   not fabricate additional TikTok videos.

## When Agent-Reach IS the right call

- Research on Chinese platforms (XHS, B站, 雪球, 小宇宙, V2EX) — last30days
  covers none of these.
- Cross-language social research where the same query needs to hit both
  Chinese and Western platforms — Agent-Reach covers XHS, last30days covers
  Reddit, both can run in parallel.
- LinkedIn public profile mining (company research, candidate sourcing) —
  last30days has no LinkedIn module.

## Skill loading: avoid the name collision

`services/agent.py` refuses to load a bare `last30days` name because two
skills share it:

```
Ambiguous skill name 'last30days': 2 skills match
matches:
  /home/elder/.hermes/skills/excrtx/last30days/SKILL.md
  /home/elder/.hermes/skills/research/last30days/SKILL.md
hint: Pass the full relative path instead of the bare name
```

- Use `research/last30days` to load the **engine** skill (the one whose
  `scripts/last30days.py` you run).
- Use `excrtx-integrate-last30days` to load the **integration** skill
  (operator/maintenance guide for the engine in the Exocórtex ecosystem).

When you tell the user "I'll run last30days" you're invoking the engine, not
the integration skill — but the integration skill is the one that knows the
correct Python binary, the env-isolation recipe, and the SC credit/JSON
quirks. Load it first, then run the engine via `terminal` or
`execute_code`+`subprocess`.

## Related

- `excrtx-integrate-last30days/SKILL.md` — main integration skill
- `references/scrapecreators-credits-and-sandbox-env.md` — SC 402
  diagnostic + `execute_code` env reload recipe
- `references/regional-brazilian-zero-signal.md` — synthesis pattern when
  no engine signal is available
- `mvanhorn/last30days-skill` upstream — engine reference
- `Panniantong/Agent-Reach` upstream — channels reference
