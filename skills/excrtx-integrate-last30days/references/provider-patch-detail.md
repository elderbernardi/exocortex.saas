# Provider Patch — DeepSeek V4 Flash for last30days

## Problem

The last30days engine supports four reasoning providers natively:
- `gemini` (Google Gemini)
- `openai` (OpenAI)
- `xai` (xAI Grok)
- `openrouter` (OpenRouter multi-model gateway)

Exocórtex uses DeepSeek V4 Flash, which is not a native provider. DeepSeek's API is OpenAI-compatible (`/v1/chat/completions`), identical to OpenRouter's endpoint format.

## Solution

Three targeted changes to `skills/last30days/scripts/lib/providers.py`:

### 1. Lazy URL resolution (`_openrouter_url`)

The original code hardcoded the OpenRouter URL as a module-level constant:

```python
# BEFORE
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
```

This was replaced with a lazy function that reads from env var or config file at call time:

```python
# AFTER (lines 22–40)
def _openrouter_url() -> str:
    """Resolve OpenRouter base URL from env or config file (lazy, reads at call time)."""
    prefix = "LAST30DAYS_OPENROUTER_BASE_URL="
    url = os.environ.get("LAST30DAYS_OPENROUTER_BASE_URL")
    if url:
        return url
    # Also check the config file directly (engine loads .env into a dict, not os.environ)
    for env_path in (
        Path.home() / ".config" / "last30days" / ".env",
        Path(".claude") / "last30days.env",
    ):
        try:
            for line in env_path.read_text().splitlines():
                if line.startswith(prefix):
                    return line[len(prefix):].strip().strip('"').strip("'")
        except (OSError, FileNotFoundError):
            continue
    return "https://openrouter.ai/api/v1/chat/completions"
```

**Why lazy:** The engine loads its `.env` file AFTER module imports. A module-level `os.environ.get(...)` evaluates at import time — before the config file is read — so it always returns the fallback. The lazy function evaluates at HTTP call time, after config is loaded.

**Why file fallback:** The engine's `env.py` loads `.env` into a config dict, not into `os.environ`. Even after config is loaded, `os.environ` may not contain the custom vars. The function falls back to reading the file directly.

### 2. Lazy model resolution (`_openrouter_default_model`)

Same pattern for the model name:

```python
# AFTER (lines 43–56)
def _openrouter_default_model() -> str:
    prefix = "LAST30DAYS_OPENROUTER_MODEL="
    model = os.environ.get("LAST30DAYS_OPENROUTER_MODEL")
    if model:
        return model
    for env_path in (
        Path.home() / ".config" / "last30days" / ".env",
        Path(".claude") / "last30days.env",
    ):
        try:
            for line in env_path.read_text().splitlines():
                if line.startswith(prefix):
                    return line[len(prefix):].strip().strip('"').strip("'")
        except (OSError, FileNotFoundError):
            continue
    return "google/gemini-3.1-flash-lite-preview"
```

### 3. Updated references

The `OpenRouterClient.generate_text()` method now calls `_openrouter_url()` instead of the old constant:

```python
# AFTER (line 242)
response = http.post(
    _openrouter_url(),  # was: OPENROUTER_URL
    payload,
    ...
)
```

The `_MODEL_DEFAULTS` dict uses the lazy function:

```python
# AFTER (line 257)
"openrouter": (_openrouter_default_model(), _openrouter_default_model()),
```

### 4. New imports

Added `from pathlib import Path` at line 9 to support file path resolution.

## Configuration

The reasoning provider/key is seeded from the central Exocórtex **default** role (`EXOCORTEX_DEFAULT_*`) by `lib/env.py` — you normally do not set the key here. Use `~/.config/last30days/.env` only to override the seeded provider/model:

```bash
LAST30DAYS_REASONING_PROVIDER=openrouter
LAST30DAYS_OPENROUTER_BASE_URL=https://api.deepseek.com/v1/chat/completions
LAST30DAYS_OPENROUTER_MODEL=deepseek-v4-flash
LAST30DAYS_PLANNER_MODEL=deepseek-v4-flash
LAST30DAYS_RERANK_MODEL=deepseek-v4-flash
```

## Key Isolation

`OPENROUTER_API_KEY` reaches the engine via `os.environ` (the default role exports it when its provider is `openrouter`) and overrides any provider-specific key pinned in the config file. When you pin a different key in `~/.config/last30days/.env`, run with:

```bash
env -u OPENROUTER_API_KEY python3.13 scripts/last30days.py "..."
```

## Model Verification

DeepSeek models available as of 2026-06-16:

```
deepseek-v4-flash    # Fast, recommended for planning/reranking
deepseek-v4-pro      # Higher quality, higher latency
```

Verify with:
```bash
curl -s https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" | python3 -m json.tool | grep '"id"'
```

Note: `deepseek-chat` is deprecated and will return 401.
