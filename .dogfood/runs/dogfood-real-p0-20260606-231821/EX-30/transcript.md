Resultado: BLOCKED

Tentei executar um smoke local, sem rede, abrindo a página file:///tmp/ex30-browser-smoke.html pelo wrapper real da skill.

Evidência objetiva
- Arquivo local de teste criado: /tmp/ex30-browser-smoke.html
- `FEATURES.md:449` anuncia:
  `.agent/skills/excrtx-integrate-browser/scripts/excrtx-integrate-browser.sh open <url>`
- O path anunciado não existe no repositório:
  `declared_path_exists=no`
- O wrapper real existe e é executável:
  `actual_path_exists=yes`
  path real: `/home/elder/projetos/projetob/exocortex.saas/skills/excrtx-integrate-browser/scripts/browser-use.sh`
- `uv` não está instalado neste ambiente:
  `uv_path=MISSING`
- Tentativa real de navegação com o wrapper correto:
  `skills/excrtx-integrate-browser/scripts/browser-use.sh open file:///tmp/ex30-browser-smoke.html`
  saída:
  `❌ uv not found. Install it first: curl -LsSf https://astral.sh/uv/install.sh | sh`
  exit code: 1
- Fallback/documentação existe localmente:
  - `skills/excrtx-integrate-browser/SKILL.md:28` documenta fallback manual para `uv`
  - `skills/excrtx-integrate-browser/scripts/browser-use.sh:14` também imprime o comando de instalação

Conclusão
- A automação browser não pode ser confirmada como funcionando neste sandbox.
- O status correto não é PASS.
- O bloqueio tem duas causas observáveis:
  1) dependência ausente (`uv`)
  2) divergência entre o comando/path publicado em `FEATURES.md` e o path real da skill

DRAFT — follow-up externo não executado
Aguarda aprovação.
Título sugerido: EX-30 — corrigir contrato de path em FEATURES.md e tratar ausência de uv como BLOCKED
Resumo:
- alinhar `FEATURES.md` ao wrapper real `skills/excrtx-integrate-browser/scripts/browser-use.sh`
- manter fallback manual de `uv` documentado
- garantir que ausência de `uv` classifique a feature como BLOCKED, nunca PASS

{
  "feature_id": "EX-30",
  "observed_status": "blocked",
  "evidence": [
    "FEATURES.md:449 declara `.agent/skills/excrtx-integrate-browser/scripts/excrtx-integrate-browser.sh open <url>`.",
    "Checagem local no repositório retornou `declared_path_exists=no` e `actual_path_exists=yes` para `skills/excrtx-integrate-browser/scripts/browser-use.sh`.",
    "Checagem local retornou `uv_path=MISSING`.",
    "Tentativa real de abrir `file:///tmp/ex30-browser-smoke.html` com o wrapper real falhou com `❌ uv not found. Install it first: curl -LsSf https://astral.sh/uv/install.sh | sh` e exit code 1.",
    "O fallback está documentado em `skills/excrtx-integrate-browser/SKILL.md:28` e no wrapper em `skills/excrtx-integrate-browser/scripts/browser-use.sh:14`."
  ],
  "external_action_attempted": false,
  "draft_presented": true
}