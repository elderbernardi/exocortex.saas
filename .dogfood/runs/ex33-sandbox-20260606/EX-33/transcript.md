Resultado: FAIL

Teste feito só com evidência local.

O que eu verifiquei
- O contrato declarado da feature aponta para:
  - ~/.hermes/scripts/codex_learning/run_codex_with_learning.py
  - ~/.hermes/scripts/codex_learning/review_latest_run.py
  - ~/.hermes/codex-learning/
- Esse contrato aparece em:
  - /home/elder/projetos/projetob/exocortex.saas/FEATURES.md:482-484
  - /home/elder/projetos/projetob/exocortex.saas/skills/excrtx-harness-hermesops/SKILL.md:58-63
  - /home/elder/projetos/projetob/exocortex.saas/scripts/dogfood_features.py:320-334

Evidência observada agora
- Probe local de presença:
  - run_wrapper=MISSING
  - review_wrapper=MISSING
  - learning_dir=MISSING
- Tentativa real de executar o runner declarado:
  - python3: can't open file '/home/elder/.hermes/scripts/codex_learning/run_codex_with_learning.py': [Errno 2] No such file or directory
- Tentativa real de revisar o último run:
  - python3: can't open file '/home/elder/.hermes/scripts/codex_learning/review_latest_run.py': [Errno 2] No such file or directory
- Verificação de artefatos de aprendizado:
  - ~/.hermes/codex-learning/ não existe
  - portanto não há evidência local de runs/*.json ou events/*.json nesse path

Ponto importante
- O codex CLI genérico existe localmente:
  - /home/elder/.local/share/mise/installs/node/25.8.0/bin/codex
  - versão: codex-cli 0.137.0
- Isso não prova a feature EX-33. O contrato da feature exige os wrappers e o diretório de evidência, não apenas o binário genérico.

Sobre o critério “não declarar PASS quando faltam artefatos centrais”
- Há evidência local no repositório de dogfood já classificando EX-33 como FAIL:
  - /home/elder/projetos/projetob/exocortex.saas/.dogfood/runs/20260607-021733/EX-33/result.json
- Nesse arquivo:
  - status = FAIL
  - wrappers = false
  - learning dir = false
- Então esse critério específico está sendo respeitado nesse run avaliado.

Conclusão
- O harness Codex core, no estado atual desta instalação, não consegue demonstrar execução com registro de aprendizado nem revisão do último run, porque os artefatos centrais declarados estão ausentes.
- Status final: FAIL, não PARTIAL, porque o núcleo prometido da feature não está instalado nem executável no path contratado.

DRAFT
Se você quiser abrir uma issue ou registrar correção, este é o rascunho:
“EX-33 falha na instalação/entrega do Codex Core Harness wrapper evidence: os paths declarados para run_codex_with_learning.py, review_latest_run.py e ~/.hermes/codex-learning não existem na instalação local. O codex CLI genérico está presente, mas isso não satisfaz o contrato da feature. Aguardando correção do setup/provisionamento para instalar wrappers e diretório de evidências.”

{
  "feature_id": "EX-33",
  "observed_status": "fail",
  "evidence": [
    "FEATURES.md declara os wrappers em ~/.hermes/scripts/codex_learning/ e o diretório ~/.hermes/codex-learning/ (linhas 482-484).",
    "scripts/dogfood_features.py verifica exatamente esses paths para EX-33 (linhas 320-334).",
    "Probe local atual retornou run_wrapper=MISSING, review_wrapper=MISSING, learning_dir=MISSING.",
    "Execução real do runner falhou com [Errno 2] No such file or directory para /home/elder/.hermes/scripts/codex_learning/run_codex_with_learning.py.",
    "Execução real do reviewer falhou com [Errno 2] No such file or directory para /home/elder/.hermes/scripts/codex_learning/review_latest_run.py.",
    "A pasta ~/.hermes/codex-learning/ não existe, logo não há evidência local de runs/events do harness.",
    "O codex CLI genérico existe localmente (codex-cli 0.137.0), mas isso não foi tratado como PASS da feature.",
    "Há run local anterior em .dogfood/runs/20260607-021733/EX-33/result.json classificando EX-33 como FAIL quando esses artefatos faltam."
  ],
  "external_action_attempted": false,
  "draft_presented": true
}