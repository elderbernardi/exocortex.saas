#!/usr/bin/env bash
set -euo pipefail

echo ''
echo '╔═══════════════════════════════════════════════════════════╗'
echo '║   Exocórtex.IA — FULL-RUN Validation                    ║'
echo '╚═══════════════════════════════════════════════════════════╝'
echo ''

echo '=== Environment ==='
echo "OS:       $(cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2)"
echo "Bash:     $(bash --version | head -1)"
echo "Git:      $(git --version)"
echo "Python:   $(python3 --version)"
echo "Node:     $(node --version)"
echo "npm:      $(npm --version)"
echo "rsync:    $(rsync --version | head -1)"
echo "uv:       $(uv --version 2>/dev/null || echo 'NOT FOUND')"
echo "hermes:   $(hermes --version)"

# Masking de API keys
if [ -n "${OPENROUTER_API_KEY:-}" ]; then
  echo "OPENROUTER_API_KEY: SET (${#OPENROUTER_API_KEY} chars, masked)"
else
  echo "OPENROUTER_API_KEY: NOT SET"
fi
if [ -n "${CONTEXT7_API_KEY:-}" ]; then
  echo "CONTEXT7_API_KEY:   SET (masked)"
else
  echo "CONTEXT7_API_KEY:   NOT SET"
fi
if [ -n "${TELEGRAM_BOT_TOKEN:-}" ]; then
  echo "TELEGRAM_BOT_TOKEN: SET (masked)"
else
  echo "TELEGRAM_BOT_TOKEN: NOT SET"
fi

echo ''
echo '=== Running setup.sh ==='
echo ''

cd /home/testuser/installer
HERMES_HOME=/home/testuser/.hermes \
EXOCORTEX_HOME=/home/testuser/exocortex \
EXOCORTEX_ENABLE_HINDSIGHT="${EXOCORTEX_ENABLE_HINDSIGHT:-0}" \
bash setup.sh 2>&1

echo ''
echo '=== POST-SETUP VERIFICATION ==='
echo ''

echo '--- File counts ---'
echo "Skills dirs:     $(find /home/testuser/.hermes/skills/exocortex -mindepth 1 -maxdepth 1 -type d | wc -l)"
echo "Acervo files:    $(find /home/testuser/exocortex/acervo -type f | wc -l)"
echo "  global:        $(find /home/testuser/exocortex/acervo/global -type f 2>/dev/null | wc -l)"
echo "  macro:         $(find /home/testuser/exocortex/acervo/macro -type f 2>/dev/null | wc -l)"
echo "  micro:         $(find /home/testuser/exocortex/acervo/micro -type f 2>/dev/null | wc -l)"
echo "  shared:        $(find /home/testuser/exocortex/acervo/shared -type f 2>/dev/null | wc -l)"
echo "  _tasks:        $(ls /home/testuser/exocortex/acervo/_tasks/ 2>/dev/null | wc -l)"
echo "  _routines:     $(ls /home/testuser/exocortex/acervo/_routines/ 2>/dev/null | wc -l)"
echo "  _automations:  $(ls /home/testuser/exocortex/acervo/_automations/ 2>/dev/null | wc -l)"
echo "  _inbox:        $(find /home/testuser/exocortex/acervo/_inbox -type d 2>/dev/null | wc -l) dirs"
echo "  _artifacts:    $(find /home/testuser/exocortex/acervo/_artifacts -type d 2>/dev/null | wc -l) dirs"
echo ''

echo '--- Symlink check ---'
ls -la /home/testuser/.hermes/acervo 2>/dev/null
echo ''

echo '--- SOUL.md integrity ---'
echo "Lines:    $(wc -l < /home/testuser/.hermes/SOUL.md 2>/dev/null || echo MISSING)"
echo "Sections: $(grep -c '^# ' /home/testuser/.hermes/SOUL.md 2>/dev/null || echo MISSING)"
grep '^# ' /home/testuser/.hermes/SOUL.md 2>/dev/null
echo ''

echo '--- Profile manut ---'
cat /home/testuser/.hermes/profiles/manut/profile.yaml 2>/dev/null | head -5
echo ''

echo '--- Bundle ---'
echo "Skills in bundle: $(grep -c '^ *- ' /home/testuser/.hermes/skill-bundles/exocortex-alpha.yaml 2>/dev/null || echo MISSING)"
echo ''

echo '--- Harness templates ---'
ls /home/testuser/exocortex/acervo/global/templates/harness-v0.4/ 2>/dev/null
echo ''

echo '--- Harness tools ---'
ls /home/testuser/exocortex/acervo/global/tools/harness/ 2>/dev/null
echo ''

echo '--- Python tools syntax ---'
for f in /home/testuser/exocortex/acervo/global/tools/harness/*.py; do
  python3 -c "import py_compile; py_compile.compile('$f', doraise=True)" 2>&1 && \
    echo "  ✓ $(basename "$f")" || echo "  ✗ $(basename "$f") SYNTAX ERROR"
done
echo ''

echo '--- Estúdio Criativo microverso ---'
echo "Files: $(find /home/testuser/exocortex/acervo/micro/estudio-criativo -type f | wc -l)"
echo "Dirs:  $(find /home/testuser/exocortex/acervo/micro/estudio-criativo -type d | wc -l)"
echo ''

echo '--- MCP registry (stub) ---'
cat /home/testuser/.hermes/mcp-registry.txt 2>/dev/null
echo ''

echo '--- Hermes stub log ---'
cat /home/testuser/.hermes/hermes-stub.log 2>/dev/null
echo ''

echo '--- Reminders ---'
ls /home/testuser/.hermes/reminders/ 2>/dev/null
echo ''

echo '--- DocBrain status ---'
if [ -d /home/testuser/exocortex/tools/docbrain ]; then
  echo "DocBrain dir: EXISTS"
  ls /home/testuser/exocortex/tools/docbrain/ | head -5
else
  echo "DocBrain: NOT CLONED (expected if no network or clone failed)"
fi
echo ''

echo '--- nlm CLI ---'
which nlm 2>/dev/null && nlm --version 2>/dev/null || echo 'nlm: NOT INSTALLED (expected if uv not available)'
echo ''

echo '--- RC2: WELCOME.md ---'
if [ -f /home/testuser/exocortex/acervo/global/knowledge/WELCOME.md ]; then
  echo "  ✓ WELCOME.md present ($(wc -l < /home/testuser/exocortex/acervo/global/knowledge/WELCOME.md) lines)"
else
  echo "  ✗ WELCOME.md MISSING"
fi
echo ''

echo '--- RC2: microverso.yaml (Estúdio Criativo) ---'
if [ -f /home/testuser/exocortex/acervo/micro/estudio-criativo/microverso.yaml ]; then
  echo "  ✓ microverso.yaml present"
  grep 'name:' /home/testuser/exocortex/acervo/micro/estudio-criativo/microverso.yaml | head -1
else
  echo "  ✗ microverso.yaml MISSING"
fi
echo ''

echo '--- RC2: Telegram/Google reminders ---'
for reminder in telegram-setup google-credentials; do
  if [ -f "/home/testuser/.hermes/reminders/${reminder}.md" ]; then
    echo "  ✓ ${reminder}.md reminder created"
  else
    echo "  • ${reminder}.md not created (may be OK if creds provided)"
  fi
done
echo ''

echo '--- RC2: Skill naming convention ---'
OLD_STYLE=$(find /home/testuser/.hermes/skills/exocortex -mindepth 1 -maxdepth 1 -type d ! -name 'excrtx-*' 2>/dev/null | wc -l)
NEW_STYLE=$(find /home/testuser/.hermes/skills/exocortex -mindepth 1 -maxdepth 1 -type d -name 'excrtx-*' 2>/dev/null | wc -l)
echo "  excrtx-* skills: $NEW_STYLE"
echo "  non-excrtx-* skills: $OLD_STYLE"
if [ "$OLD_STYLE" -gt 0 ]; then
  echo "  ✗ STALE: old-style skill names detected!"
  find /home/testuser/.hermes/skills/exocortex -mindepth 1 -maxdepth 1 -type d ! -name 'excrtx-*' -printf '    %f\n'
else
  echo "  ✓ All skills follow excrtx-* convention"
fi
echo ''

echo '--- RC2: Zero stale references in key files ---'
STALE=0
for pattern in acervo-manager stop-slop taste-skill codex-harness exocortex-onboarding personal-artifact-workspace browser-use; do
  if grep -rq "$pattern" /home/testuser/.hermes/skill-bundles/ /home/testuser/.hermes/profiles/ /home/testuser/.hermes/SOUL.md 2>/dev/null; then
    echo "  ✗ Stale: $pattern"
    STALE=$((STALE + 1))
  fi
done
if [ $STALE -eq 0 ]; then
  echo "  ✓ Zero stale references in bundle/profile/SOUL"
else
  echo "  ✗ $STALE stale reference patterns found"
fi
echo ''

echo '=== FULL-RUN COMPLETE ==='
