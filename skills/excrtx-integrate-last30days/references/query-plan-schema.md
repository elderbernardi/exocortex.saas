# last30days Query Plan JSON Schema

The `--plan` flag accepts a JSON file (never inline JSON — apostrophes in search strings break shell parsing). The engine uses this plan to run targeted subqueries against specific platforms.

## Schema

```json
{
  "topic": "human-readable topic string",
  "target_languages": ["en"],
  "subqueries": [
    {
      "query": "specific subquery targeting a platform",
      "platforms": ["reddit", "x", "youtube", "web", "news"]
    }
  ],
  "reddit_keywords": ["keyword1", "keyword2"],
  "x_keywords": ["keyword1", "keyword2"]
}
```

## Fields

| Field | Required | Description |
|---|---|---|
| `topic` | Yes | Human-readable topic string. Used for file naming and logging. |
| `target_languages` | No | Language codes (default: `["en"]`). |
| `subqueries` | Yes | Array of 2–4 subquery objects. Each runs independently against its platforms. |
| `subqueries[].query` | Yes | The search string for this subquery. |
| `subqueries[].platforms` | Yes | Array of platform codes: `reddit`, `x`, `youtube`, `web`, `news`, `hackernews`, `github`, `polymarket`. |
| `reddit_keywords` | No | Keywords for Reddit search refinement. |
| `x_keywords` | No | Keywords for X/Twitter search refinement. |

## Example: CPG Manufacturing (2026-06-17 session)

```json
{
  "topic": "consumer goods manufacturing industry trends",
  "target_languages": ["en"],
  "subqueries": [
    {
      "query": "consumer packaged goods manufacturing automation industry 4.0 smart factory trends 2026",
      "platforms": ["reddit", "x", "youtube", "web"]
    },
    {
      "query": "FMCG supply chain reshoring near-shoring domestic production manufacturing 2026",
      "platforms": ["reddit", "x", "news"]
    },
    {
      "query": "consumer goods manufacturing sustainability packaging regulations circular economy 2026",
      "platforms": ["reddit", "x", "youtube", "web"]
    }
  ],
  "reddit_keywords": [
    "consumer goods manufacturing",
    "CPG production automation",
    "FMCG supply chain",
    "packaging sustainability regulations"
  ],
  "x_keywords": [
    "CPG manufacturing",
    "FMCG industry trends",
    "reshoring manufacturing",
    "Industry 4.0 consumer goods"
  ]
}
```

## Companion flags

When using `--plan`, also pass targeting flags resolved in Step 0.55:

```bash
--subreddits "supplychain,manufacturing,logistics,industrialengineering,business"
--x-handle "@CGTmagazine"              # if resolved
--tiktok-hashtags "cpg,fmcg"           # if resolved
--ig-creators "consumer_goods_today"   # if resolved
```

Omit any flag whose value was not resolved — empty flags break the engine.

## Pitfalls

- **Never inline `--plan '$JSON'`** — apostrophes in search strings break shell parsing. Always write to a tmpfile and pass `--plan "$QUERY_PLAN_FILE"`.
- **Never skip `--plan` on named-entity topics** — the engine falls back to deterministic single-word queries that produce visibly thinner results.
- **Platform codes are case-sensitive** — use lowercase: `reddit`, `x`, `youtube`, `web`, `news`, `hackernews`, `github`, `polymarket`.
