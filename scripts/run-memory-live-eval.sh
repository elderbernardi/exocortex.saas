#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_QUESTIONS="$REPO_ROOT/tests/memory-eval/live/questions.local.yaml"

ACERVO_ROOT="${1:-${ACERVO:-}}"
QUESTIONS_FILE="${2:-${EXOCORTEX_MEMORY_EVAL_QUESTIONS:-$DEFAULT_QUESTIONS}}"

if [ -z "$ACERVO_ROOT" ]; then
  echo "BLOCKED: ACERVO root não informado. Passe como 1º argumento ou exporte ACERVO." >&2
  exit 2
fi

if [ ! -d "$ACERVO_ROOT" ]; then
  echo "BLOCKED: acervo root não existe: $ACERVO_ROOT" >&2
  exit 2
fi

if [ ! -f "$QUESTIONS_FILE" ]; then
  echo "BLOCKED: arquivo de perguntas live não encontrado: $QUESTIONS_FILE" >&2
  echo "Copie tests/memory-eval/live/questions.template.yaml para questions.local.yaml e preencha paths reais do seu acervo." >&2
  exit 2
fi

python3 "$REPO_ROOT/tests/memory-eval/run_eval.py" \
  --acervo-root "$ACERVO_ROOT" \
  --questions-file "$QUESTIONS_FILE" \
  --strategies catalog,production \
  --report-prefix live

FIXTURE_ROOT="$REPO_ROOT/tests/memory-eval/fixture/acervo"
if [ "$(realpath "$ACERVO_ROOT")" = "$(realpath "$FIXTURE_ROOT")" ]; then
  echo "INFO: fixture detectado — knowledge canônico não será materializado." >&2
  exit 0
fi

REPORT_JSON="$REPO_ROOT/tests/memory-eval/report/live-$(date -u +%F).json"
if [ ! -f "$REPORT_JSON" ]; then
  echo "BLOCKED: report JSON da execução atual não encontrado: $REPORT_JSON" >&2
  exit 2
fi

python3 "$REPO_ROOT/scripts/file_memory_eval_knowledge.py" \
  --acervo-root "$ACERVO_ROOT" \
  --report-json "$REPORT_JSON"
