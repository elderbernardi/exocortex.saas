Resultado do dogfood conversacional para EX-30: BLOCKED

O que observei
- A navegação real não aconteceu.
- O bloqueio foi por dependência ausente (`uv`), com evidência local.
- O contrato de path em `FEATURES.md` diverge do path real da skill/wrapper.
- Há fallback manual documentado para `uv`, então não é ausência de documentação; é ausência de pré-requisito no ambiente.

Evidência local
- `FEATURES.md:449` anuncia:
  `.agent/skills/excrtx-integrate-browser/scripts/excrtx-integrate-browser.sh open <url>`
- Path real encontrado:
  `/home/elder/projetos/projetob/exocortex.saas/skills/excrtx-integrate-browser/scripts/browser-use.sh`
- A própria skill canônica mostra:
  `skills/excrtx-integrate-browser/scripts/browser-use.sh open https://example.com`
- Verificação de dependência:
  `command -v uv` retornou vazio
- Tentativa real de execução:
  `/home/elder/projetos/projetob/exocortex.saas/skills/excrtx-integrate-browser/scripts/browser-use.sh open https://example.com`
- Saída real:
  `❌ uv not found. Install it first: curl -LsSf https://astral.sh/uv/install.sh | sh`

Leitura do contrato
- Dependência `uv`:
  BLOCKED, não PASS.
- Fallback:
  existe e está documentado na skill e no wrapper.
- Path contract:
  inconsistente entre `FEATURES.md` e o arquivo real.

DRAFT local gerado
- `/home/elder/projetos/projetob/exocortex.saas/acervo/_artifacts/items/draft-issue-dogfood-ex-30-2026-06-06.md`

DRAFT
- Corrigir `FEATURES.md` para apontar para:
  `skills/excrtx-integrate-browser/scripts/browser-use.sh`
- Manter a classificação BLOCKED quando `uv` não existir.
- Só depois de instalar o pré-requisito repetir o teste de navegação (`open` + `state`) para poder marcar PASS.

{
  "feature_id": "EX-30",
  "observed_status": "blocked",
  "evidence": [
    "FEATURES.md:449 aponta para `.agent/skills/excrtx-integrate-browser/scripts/excrtx-integrate-browser.sh open <url>`",
    "O path real existente é `/home/elder/projetos/projetob/exocortex.saas/skills/excrtx-integrate-browser/scripts/browser-use.sh`",
    "A skill canônica também referencia `skills/excrtx-integrate-browser/scripts/browser-use.sh open https://example.com`",
    "`command -v uv` retornou vazio no ambiente local",
    "A execução real do wrapper falhou com: `❌ uv not found. Install it first: curl -LsSf https://astral.sh/uv/install.sh | sh`",
    "Fallback manual para instalar `uv` está documentado; navegação não ocorreu nesta sandbox"
  ],
  "external_action_attempted": false,
  "draft_presented": true
}