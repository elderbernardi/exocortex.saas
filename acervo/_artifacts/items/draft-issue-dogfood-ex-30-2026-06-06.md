# DRAFT — EX-30 Browser automation dependency and path contract

Status proposto: BLOCKED

Resumo
- A automação browser não pôde ser validada end-to-end porque `uv` está ausente no ambiente local.
- O contrato de path em `FEATURES.md` diverge do path real da skill/wrapper.
- Há fallback manual documentado para instalar `uv`, mas ele não foi executado nesta sandbox.

Prompt natural usado
- "Abra uma página simples no navegador autônomo e confirme que a automação browser funciona."

Contrato esperado
- Dependência `uv` presente ou fallback documentado.
- Path do comando em `FEATURES.md` igual ao path real da skill.
- Ausência de dependência classificada como BLOCKED, nunca PASS.

Evidências
1. `FEATURES.md:449`
   - `.agent/skills/excrtx-integrate-browser/scripts/excrtx-integrate-browser.sh open <url>`
2. Path real encontrado
   - `/home/elder/projetos/projetob/exocortex.saas/skills/excrtx-integrate-browser/scripts/browser-use.sh`
3. Skill canônica (`skills/excrtx-integrate-browser/SKILL.md:40`)
   - `skills/excrtx-integrate-browser/scripts/browser-use.sh open https://example.com`
4. Verificação local de dependência
   - `command -v uv` retornou vazio
5. Tentativa real de execução local
   - `/home/elder/projetos/projetob/exocortex.saas/skills/excrtx-integrate-browser/scripts/browser-use.sh open https://example.com`
   - saída: `❌ uv not found. Install it first: curl -LsSf https://astral.sh/uv/install.sh | sh`
6. Fallback documentado, mas manual
   - `skills/excrtx-integrate-browser/SKILL.md` informa fallback: `curl -LsSf https://astral.sh/uv/install.sh | sh`

Passos para reproduzir
1. Em ambiente sem `uv`, rodar o wrapper real:
   - `skills/excrtx-integrate-browser/scripts/browser-use.sh open https://example.com`
2. Observar falha imediata por dependência ausente.
3. Comparar o path anunciado em `FEATURES.md` com o arquivo real na skill.

Esperado
- `FEATURES.md` aponta para o wrapper real.
- Se `uv` faltar, a feature é reportada como BLOCKED com fallback explícito.
- Depois da instalação do pré-requisito, o wrapper deve abrir a página e permitir ao menos `state` como prova mínima.

Atual
- Path publicado está incorreto.
- Execução real bloqueada por `uv` ausente.
- Não há evidência local de navegação bem-sucedida nesta sandbox.

Sugestão de correção
A. Corrigir `FEATURES.md` para o wrapper real `skills/excrtx-integrate-browser/scripts/browser-use.sh`.
B. Manter a classificação BLOCKED quando `uv` estiver ausente.
C. Opcional: endurecer o wrapper/feature docs com check de pré-requisito e mensagem de fallback mais explícita.

Sem ação externa executada. Aguarda aprovação para qualquer mudança fora da sandbox.
