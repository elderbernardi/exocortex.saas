#!/usr/bin/env bash
# package-deck.sh — package a Markdown-sourced HTML deck as a reproducible ZIP
#
# Usage:
#   package-deck.sh --source source.md --html deck.html --out deck.zip [--pdf deck.pdf] [--assets assets_dir] [--manifest manifest.json]
set -euo pipefail

SOURCE=""
HTML=""
PDF=""
ASSETS=""
MANIFEST=""
OUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source) SOURCE="${2:-}"; shift 2 ;;
    --html) HTML="${2:-}"; shift 2 ;;
    --pdf) PDF="${2:-}"; shift 2 ;;
    --assets) ASSETS="${2:-}"; shift 2 ;;
    --manifest) MANIFEST="${2:-}"; shift 2 ;;
    --out) OUT="${2:-}"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$SOURCE" || -z "$HTML" || -z "$OUT" ]]; then
  cat >&2 <<'USAGE'
Usage:
  package-deck.sh --source source.md --html deck.html --out deck.zip [--pdf deck.pdf] [--assets assets_dir] [--manifest manifest.json]
USAGE
  exit 2
fi

for f in "$SOURCE" "$HTML"; do
  [[ -f "$f" ]] || { echo "Required file not found: $f" >&2; exit 1; }
done
[[ -z "$PDF" || -f "$PDF" ]] || { echo "PDF not found: $PDF" >&2; exit 1; }
[[ -z "$MANIFEST" || -f "$MANIFEST" ]] || { echo "Manifest not found: $MANIFEST" >&2; exit 1; }
[[ -z "$ASSETS" || -d "$ASSETS" ]] || { echo "Assets dir not found: $ASSETS" >&2; exit 1; }

TMP_DIR="$(mktemp -d)"
cleanup() { rm -rf "$TMP_DIR"; }
trap cleanup EXIT

mkdir -p "$TMP_DIR/source" "$TMP_DIR/exports" "$TMP_DIR/assets"
cp "$SOURCE" "$TMP_DIR/source/$(basename "$SOURCE")"
cp "$HTML" "$TMP_DIR/exports/$(basename "$HTML")"
[[ -z "$PDF" ]] || cp "$PDF" "$TMP_DIR/exports/$(basename "$PDF")"
[[ -z "$MANIFEST" ]] || cp "$MANIFEST" "$TMP_DIR/manifest.json"
[[ -z "$ASSETS" ]] || cp -R "$ASSETS"/. "$TMP_DIR/assets/"

mkdir -p "$(dirname "$OUT")"
(
  cd "$TMP_DIR"
  zip -qr "$OUT" .
)

[[ -s "$OUT" ]] || { echo "ZIP was not created: $OUT" >&2; exit 1; }
BYTES=$(wc -c < "$OUT" | tr -d ' ')
printf 'Packaged deck ZIP: %s (%s bytes)\n' "$OUT" "$BYTES"
