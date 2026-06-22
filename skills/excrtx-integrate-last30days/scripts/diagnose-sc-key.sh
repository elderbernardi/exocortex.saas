#!/usr/bin/env bash
# diagnose-sc-key.sh — Diagnose ScrapeCreators API key health in 3 probes.
#
# Why this exists: SC keys can pass `--diagnose` (which only checks that
# the key string is loaded), pass the very first direct ping, and then
# 402 every subsequent call. The 2026-06-22 session lost 5 minutes
# chasing this. Run this BEFORE launching a last30days research pipeline
# if you need SC-backed sources (TikTok, Instagram, Threads, Pinterest).
#
# Usage:
#   ./diagnose-sc-key.sh [SC_API_KEY]
#   # If no key passed, reads SCRAPECREATORS_API_KEY from env, falling
#   # back to ~/.hermes/.env, then ~/projetos/projetob/exocortex.saas/.env
#
# Exit codes:
#   0  key looks healthy (all 3 probes 200)
#   1  key is one-shot (200 then 402) — DO NOT run engine with this key
#   2  key is dead (all 402, persistent)
#   3  key auth invalid (401)
#   4  SC upstream down (5xx)
#   5  no key found

set -uo pipefail

# --- 1. Locate the key ---
KEY="${1:-${SCRAPECREATORS_API_KEY:-}}"

if [ -z "$KEY" ] && [ -f "$HOME/.hermes/.env" ]; then
    KEY=$(grep -E '^SCRAPECREATORS_API_KEY=' "$HOME/.hermes/.env" 2>/dev/null | head -1 | cut -d= -f2-)
fi

if [ -z "$KEY" ] && [ -f "$HOME/projetos/projetob/exocortex.saas/.env" ]; then
    KEY=$(grep -E '^SCRAPECREATORS_API_KEY=' "$HOME/projetos/projetob/exocortex.saas/.env" 2>/dev/null | head -1 | cut -d= -f2-)
fi

if [ -z "$KEY" ]; then
    echo "ERROR: SCRAPECREATORS_API_KEY not found in env, ~/.hermes/.env, or exocortex.saas/.env"
    exit 5
fi

KEY_PREFIX="${KEY:0:6}...${KEY: -4}"
URL="https://api.scrapecreators.com/v1/tiktok/search/keyword?query=cleantok&count=1"

echo "=== ScrapeCreators key diagnostic ==="
echo "Key:    $KEY_PREFIX  (len=${#KEY})"
echo "Target: $URL"
echo ""

probe() {
    local n="$1"
    local code
    code=$(curl -s -o /tmp/sc_diag_$$.json -w "%{http_code}" \
        -H "x-api-key: $KEY" \
        --max-time 15 \
        "$URL" 2>/dev/null)
    local body
    body=$(cat /tmp/sc_diag_$$.json 2>/dev/null | head -c 200)
    rm -f /tmp/sc_diag_$$.json
    echo "Probe $n: HTTP $code  $body"
    echo "$code"
}

# --- 2. Three probes, 2s apart ---
P1=$(probe 1)
sleep 2
P2=$(probe 2)
sleep 2
P3=$(probe 3)

echo ""

# --- 3. Classify ---
if [ "$P1" = "200" ] && [ "$P2" = "200" ] && [ "$P3" = "200" ]; then
    echo "VERDICT: HEALTHY (3/3 200). Safe to run last30days with this key."
    exit 0
fi

if [ "$P1" = "200" ] && { [ "$P2" = "402" ] || [ "$P3" = "402" ]; }; then
    echo "VERDICT: ONE-SHOT TRAP (1× 200 then 402). Key is effectively unusable."
    echo "  Next: try a different SC key, wait 5-15 min, or fall back to Apify."
    echo "  See references/scrapecreators-credits-and-sandbox-env.md §1.1"
    exit 1
fi

if [ "$P1" = "402" ] && [ "$P2" = "402" ] && [ "$P3" = "402" ]; then
    echo "VERDICT: DEAD (3/3 402). Out of credits — needs top-up."
    echo "  Top-ups start at \$5-10 at https://scrapecreators.com"
    exit 2
fi

if [ "$P1" = "401" ] || [ "$P2" = "401" ] || [ "$P3" = "401" ]; then
    echo "VERDICT: BAD KEY (401). Re-issue in SC dashboard."
    exit 3
fi

if echo "$P1$P2$P3" | grep -qE "5[0-9]{2}"; then
    echo "VERDICT: SC UPSTREAM DOWN (5xx). Wait 5 min and retry."
    exit 4
fi

echo "VERDICT: MIXED (200/$P2/$P3). Run probe again or check SC status page."
exit 1
