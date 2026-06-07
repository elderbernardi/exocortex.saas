# DRAFT — EX-30 Browser automation dependency and path contract

Status proposto: BLOCKED

Resumo
- O wrapper real existe em `skills/excrtx-integrate-browser/scripts/browser-use.sh`.
- O `FEATURES.md` aponta para um comando/path divergente: `.agent/skills/excrtx-integrate-browser/scripts/excrtx-integrate-browser.sh`.
- A dependência `uv` está ausente neste ambiente, e o wrapper aborta imediatamente antes de qualquer navegação.
- Há fallback manual documentado na skill (`curl -LsSf https://astral.sh/uv/install.sh | sh`), então o caso é bloqueio por dependência ausente, não PASS.

Reprodução local
1. Verificar `uv`:
   `command -v uv || true`
   Resultado: sem saída.
2. Executar o wrapper real:
   `./skills/excrtx-integrate-browser/scripts/browser-use.sh open file:///tmp/ex30-smoke.html`
   Resultado:
   `❌ uv not found. Install it first: curl -LsSf https://astral.sh/uv/install.sh | sh`
3. Conferir `FEATURES.md`:
   EX-30 usa `.agent/skills/excrtx-integrate-browser/scripts/excrtx-integrate-browser.sh open <url>`.
4. Conferir path real no repositório:
   `skills/excrtx-integrate-browser/scripts/browser-use.sh`

Esperado
- `FEATURES.md` deve apontar para o wrapper real.
- O teste deve marcar BLOCKED quando `uv` não existir.
- PASS só com navegação real ou fallback realmente exercido.

Atual
- Path divergente em documentação/contrato.
- Execução bloqueada por ausência de `uv`.

Sem ação externa executada. Aguardando aprovação para qualquer correção fora desta sandbox.
