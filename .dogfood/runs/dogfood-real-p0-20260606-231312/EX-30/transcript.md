Resultado do dogfood EX-30:

Status agregado: FAIL
Motivo: não consegui comprovar navegação real, e encontrei dois problemas locais distintos:
1. Bloqueio operacional: `uv` está ausente, então a automação não sobe.
2. Falha de contrato: o path/comando documentado em `FEATURES.md` não corresponde ao wrapper real.

Evidência local:
- `FEATURES.md:449` manda usar:
  `.agent/skills/excrtx-integrate-browser/scripts/excrtx-integrate-browser.sh open <url>`
- O wrapper real presente no repositório é:
  `/home/elder/projetos/projetob/exocortex.saas/skills/excrtx-integrate-browser/scripts/browser-use.sh`
- O path declarado em `.agent/...` não existe localmente.
- O wrapper real existe e é executável.
- `uv` não está disponível no host.
- Tentei abrir uma página simples local via `data:` URL com o wrapper real, e a execução falhou imediatamente com:
  `❌ uv not found. Install it first: curl -LsSf https://astral.sh/uv/install.sh | sh`
- A fallback está documentada localmente:
  - na skill `excrtx-integrate-browser`
  - no próprio wrapper `browser-use.sh`
- Como `uv` falta, não houve navegação real. Então não há base para PASS.

Leitura objetiva:
- Se eu olhar só a execução prática, o caso está BLOCKED por dependência ausente.
- Se eu olhar o contrato completo da feature, o caso é FAIL porque a documentação/path estão divergentes.
- Para este dogfood, reporto FAIL agregado, registrando explicitamente o bloqueio por dependência para não mascarar o motivo operacional.

DRAFT preparado localmente:
`/home/elder/acervo/_artifacts/items/draft-issue-dogfood-ex30-browser-path-uv-2026-06-06.md`

Nenhuma ação externa foi tentada. Se quiser publicar isso depois, fica aguardando aprovação explícita.

{
  "feature_id": "EX-30",
  "observed_status": "fail",
  "evidence": [
    "FEATURES.md linha 449 declara o wrapper .agent/skills/excrtx-integrate-browser/scripts/excrtx-integrate-browser.sh open <url>.",
    "O script real existente é /home/elder/projetos/projetob/exocortex.saas/skills/excrtx-integrate-browser/scripts/browser-use.sh.",
    "O path declarado em .agent/... não existe localmente; o path real em skills/... existe e é executável.",
    "command -v uv não retornou binário; uv está ausente no host.",
    "A tentativa local de navegação com o wrapper real falhou com: '❌ uv not found. Install it first: curl -LsSf https://astral.sh/uv/install.sh | sh'.",
    "A skill e o wrapper documentam fallback/manual install para uv, mas ele não foi executado neste sandbox.",
    "Sem uv, não houve navegação real; portanto não há evidência suficiente para PASS.",
    "Foi criado um DRAFT local em /home/elder/acervo/_artifacts/items/draft-issue-dogfood-ex30-browser-path-uv-2026-06-06.md."
  ],
  "external_action_attempted": false,
  "draft_presented": true
}