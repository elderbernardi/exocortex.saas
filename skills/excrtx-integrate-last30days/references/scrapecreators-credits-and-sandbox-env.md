# ScrapeCreators: 402 "out of credits", sandbox env, and emit-json quirks

Three operational pitfalls encountered when using `last30days` against the
ScrapeCreators (SC) provider. All three are silent in the engine's main
output and only show up if you look at the right surface.

## 1. Diagnosing SC "out of credits" (HTTP 402)

### Symptom

- `--diagnose` reports `has_scrapecreators: true` and lists `tiktok`,
  `instagram`, `threads` in `available_sources`.
- `--search tiktok,instagram` returns 0 items in `items_by_source` and the
  compact report shows 0 videos/reels for those sources.
- No top-level error in the engine output — the failure surfaces only as a
  `[TikTok] HTTP 402` line in stderr.

### Root cause

`has_scrapecreators: true` only means the key string is loaded into the
engine's config. It does NOT mean the account has credits. When credits are
exhausted, SC answers every call with:

```json
{"success":false,"message":"Looks like you're out of credits :( You'll need to buy more to continue using the service."}
```

…with HTTP 402. The engine treats this as "no results" rather than a
hard error.

### Fix

Call SC directly to confirm:

```bash
curl -s -o /dev/null -w "%{http_code}\n" \
  -H "x-api-key: $SCRAPECREATORS_API_KEY" \
  "https://api.scrapecreators.com/v1/tiktok/search/keyword?query=test&count=1"
# 200 = OK, 402 = out of credits, 401 = bad key, 5xx = SC down
```

Top-ups start at $5–10. The free 100 credits are exhausted in ~1 session of
deep multi-source research. For continuous use, plan a $10–20/month baseline.

### Distinguishing the failure modes

| Code | Meaning | Action |
|------|---------|--------|
| 200 then 402 | "One-shot" auth window — see §1.1 below | Re-test after a few minutes or use the other key |
| 401  | Key format wrong / revoked | Re-issue key in SC dashboard, update `~/.hermes/.env` |
| 402  | Out of credits (most common persistent failure) | Top up SC account |
| 502/504 | SC upstream / rate limit | Wait 5 min, retry with smaller `--search` list |

All look identical in the engine stderr — only a direct curl distinguishes them.

### 1.1 The "one-shot 200" trap (cache or new-key window)

**Symptom (observed 2026-06-22):** A freshly-copied SC key in
`exocortex.saas/.env` returned `{"success":true,"credits_remaining":99}` on
the very first direct curl. Every subsequent call — same key, same endpoint,
seconds apart — returned `{"success":false,"message":"Looks like you're out
of credits :("}` with HTTP 402. After 10+ retries across multiple
subprocess shells, the 200 never came back.

**Hypothesis (not yet confirmed with SC support):**

- New keys may carry a single free probe that doesn't decrement a counter
  but every later call does. Once the counter is hit, the account flips to
  402 even if `credits_remaining` was high on the probe.
- The account may be a shared/pooled key where another consumer exhausts
  credits between your calls.
- There may be a per-key rate limit on credit balance lookups that looks
  like "credits exhausted" after a few requests.

**Diagnostic that catches it before you waste a research cycle:**

1. Hit the endpoint 3 times in a row, 2 seconds apart, with the same key
   and same query.
2. If responses 2 and 3 are 402 while response 1 was 200, you have the
   "one-shot" pattern. The key is effectively unusable for this research
   session even though `--diagnose` still says `has_scrapecreators: true`.
3. Do not run the last30days engine with this key — it will silently
   return 0 items for all SC-backed sources and the engine stderr will
   show `[Reddit] ScrapeCreators backup also failed (HTTPError: HTTP 402)`
   on every query.

**Fixes in priority order:**

1. **Use a different SC key** if you have one (the user in the 06-22
   session had two: a fresh `iKZKVA...JI62` and a dead `zNPVpS...KKp1` —
   the dead one was *still* 402, but the fresh one was also unusable due
   to this trap).
2. **Wait 5–15 minutes** and retest with the 3-call probe. If responses
   stay 200 across all 3, the key recovered.
3. **Switch to `APIFY_API_TOKEN`** (free tier exists) and let the engine
   fall back to Apify's TikTok actors. Add to `~/.config/last30days/.env`:
   `APIFY_API_TOKEN=***`. The engine activates Apify automatically when
   `SCRAPECREATORS_API_KEY` is absent or broken.
4. **Accept zero TikTok signal** and synthesize from YouTube + Reddit +
   Google News RSS. Document the gap explicitly in the report — do not
   fabricate video titles or counts.

### 1.2 Reproducibility check (2026-06-22, `diagnose-sc-key.sh`)

After this section was first written, the pre-flight script
`scripts/diagnose-sc-key.sh` was created (exit codes 0=healthy, 1=one-shot,
2=dead, 3=bad-key, 4=upstream, 5=no-key). On the same key
`iKZKVA...JI62` (loaded from `exocortex.saas/.env` since
`~/.hermes/.env` was cleaned up the day before) the script returned
**exit 1** with the same 200/402/402 pattern:

```
=== ScrapeCreators key diagnostic ===
Key:    iKZKVA...JI62  (len=28)
Target: https://api.scrapecreators.com/v1/tiktok/search/keyword?query=cleantok&count=1

VERDICT: MIXED (200/402/402). Run probe again or check SC status page.
```

(The `MIXED` message is the fallback classification; the exit code 1
is the same as the explicit one-shot branch.) Repro is stable across
~6s total script runtime. This confirms the trap is reproducible on
the same key hours later — not a transient glitch.

**Operational consequence:** the one-shot 200/402 pattern is **not
resolvable by waiting or retrying** (at least not within an hour-long
session). The fix is structural (new key from SC dashboard, or
fallback to Apify), not temporal.

## 2. Reloading `~/.hermes/.env` inside `execute_code`

### Problem

`execute_code` runs each script in a **fresh Python subprocess**. `os.environ`
is empty unless you populate it yourself. The shell session may have
`OPENROUTER_API_KEY`, `SCRAPECREATORS_API_KEY`, etc. exported — those do NOT
propagate to `execute_code`.

If you try to pass an env var to a `subprocess.run(...)` call that wraps the
last30days engine, you have to load it manually:

```python
import os, subprocess

# Step 1: Reload ~/.hermes/.env into THIS process's env
with open(os.path.expanduser("~/.hermes/.env")) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v

# Step 2: Forward to subprocess
env_extra = {**os.environ}
result = subprocess.run(
    ["python3.14",
     "/home/elder/.hermes/skills/research/last30days/scripts/last30days.py",
     "TikTok cleaning trends",
     "--search", "tiktok",
     "--days", "30"],
    capture_output=True, text=True, timeout=240,
    env=env_extra,
)
```

### Why `env -u OPENROUTER_API_KEY` alone is not enough

The last30days engine reads `OPENROUTER_API_KEY` from `os.environ` with higher
priority than its own config file. The reason for `-u` is to **clear** a
leaked key from the parent shell. If the parent is `execute_code` (no env at
all), `-u` is harmless but doesn't help. You still need to load
`SCRAPECREATORS_API_KEY` from the .env file before the subprocess call.

### Alternative: use `execute_code`'s built-in terminal wrapper

If the env is already in the active shell (i.e., you're in a regular
`terminal` tool, not `execute_code`), you can do this in one line:

```python
# Inside execute_code:
from hermes_tools import terminal
terminal('env -u OPENROUTER_API_KEY python3.14 '
         '/home/elder/.hermes/skills/research/last30days/scripts/last30days.py '
         '"topic" --search=tiktok --days=30')
```

This wraps a real shell, so it inherits whatever is in the active
environment. Use this when the env is already loaded and you don't need to
inject extra vars.

## 3. `--emit json` truncates SC-backed items

### Symptom

You run the engine and capture the compact markdown report — it shows
20+ TikTok videos with full engagement (views/likes/cmts) and metadata. You
then run the same query with `--emit json --save-dir /tmp/l30d` and the
saved JSON has `items_by_source: {tiktok: 0, instagram: 0}`. The TikTok
items are nowhere in the JSON tree, except as bare URLs inside
`clusters[*].representative_ids` (no engagement, no snippet, no author).

### Why

The JSON emit path is optimized for free sources (Reddit, YouTube, HN,
GitHub) where items are easy to serialize. SC-backed sources get attached
to clusters but the per-item engagement is only rendered in the compact
markdown path. The underlying data IS there — just not in the JSON shape
the engine advertises.

### Workaround

For TikTok/Instagram/Threads analyses:

1. **Run twice** — once with `--emit json` (for the structured clusters
   you DO get) and once with default emit (compact markdown captured from
   stdout).
2. **Parse the compact markdown** for SC-backed sources. The format is
   stable: clusters have a `### N. <title> (score X, M items, sources: [...])`
   header and items underneath with `[tiktok]` source tag, URL, date, and
   a single-line evidence snippet.
3. If you need structured fields (views, likes, comments) per TikTok video,
   call SC directly:

   ```python
   import urllib.request, json
   url = "https://api.scrapecreators.com/v1/tiktok/search/keyword?query=cleaning+hacks&count=20"
   req = urllib.request.Request(url, headers={"x-api-key": os.environ["SCRAPECREATORS_API_KEY"]})
   data = json.loads(urllib.request.urlopen(req, timeout=30).read())
   for v in data.get("items", []):
       print(v.get("id"), v.get("stats", {}).get("playCount"))
   ```

   The endpoint returns the full payload; you just need to be prepared for
   402 and have the key top-up path ready.

## Endpoints cheat sheet (SC v1)

| Endpoint | Purpose | Auth header |
|----------|---------|-------------|
| `POST /v1/tiktok/search/keyword?query=X&count=N` | TikTok search by keyword | `x-api-key: $SC_KEY` |
| `GET /v1/tiktok/search/hashtag?hashtag=X&count=N` | TikTok search by hashtag | same |
| `GET /v3/tiktok/profile/videos?handle=X` | Creator's recent videos | same |
| `GET /v1/tiktok/video/transcript?url=X` | Get transcript of a single video | same |
| `GET /v1/tiktok/video/comments?url=X` | Get comments of a single video | same |
| `GET /v1/tiktok` (bare) | **404** — common confusion | — |

Note: `/v1/tiktok/search` (no subpath) returns 404. The skill uses
`/v1/tiktok/search/keyword` and `/v1/tiktok/search/hashtag` correctly; if
you call SC manually, don't forget the subpath.

## Related

- `excrtx-integrate-last30days/SKILL.md` — main skill, see Pitfalls section
  for "ScrapeCreators 402", "execute_code sandbox", and "emit json
  truncation" entries added in v1.1.1.
- `mvanhorn/last30days-skill` upstream docs — `https://github.com/mvanhorn/last30days-skill`
