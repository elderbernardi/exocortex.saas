# Evidence — EX-30 — Browser automation dependency and path contract

Status: FAIL
Risk: P1

## Summary
Real-agent: Contrato de path da Browser Automation falha: FEATURES.md aponta para path/comando inexistente.

## Criteria
- FAIL: Dependência uv existe ou fallback está documentado. — uv_available=False
- FAIL: Path em FEATURES.md corresponde ao path real da skill. — declared=.agent/skills/excrtx-integrate-browser/scripts/excrtx-integrate-browser.sh actual=skills/excrtx-integrate-browser/scripts/browser-use.sh declared_exists=False
- OK: Falta de dependência é BLOCKED, não PASS. — uv_available=False status=FAIL
