Resultado: FAIL

O que ficou provado com evidência local:

- O contrato da feature EX-33 declara estes paths:
  - /home/elder/projetos/projetob/exocortex.saas/FEATURES.md:482-484
  - /home/elder/projetos/projetob/exocortex.saas/skills/excrtx-harness-hermesops/SKILL.md:58-63
  - wrappers esperados:
    - /home/elder/.hermes/scripts/codex_learning/run_codex_with_learning.py
    - /home/elder/.hermes/scripts/codex_learning/review_latest_run.py
  - diretório esperado:
    - /home/elder/.hermes/codex-learning

- Probe local atual:
  - run_wrapper exists=False
  - review_wrapper exists=False
  - learning_dir exists=False

- Tentativa real de invocar os wrappers declarados:
  - python3 /home/elder/.hermes/scripts/codex_learning/run_codex_with_learning.py --help
    -> [Errno 2] No such file or directory
  - python3 /home/elder/.hermes/scripts/codex_learning/review_latest_run.py --help
    -> [Errno 2] No such file or directory

- O setup documentado não sustenta a promessa dessa feature:
  - busca em /home/elder/projetos/projetob/exocortex.saas/setup.sh por
    codex_learning, codex-learning, run_codex_with_learning, review_latest_run
    retornou 0 ocorrências

- O avaliador local do dogfood já está tratando isso corretamente como FAIL, não PASS:
  - /home/elder/projetos/projetob/exocortex.saas/.dogfood/runs/20260607-021733/EX-33/result.json:3 -> status=FAIL
  - no mesmo arquivo:
    - wrappers=false
    - learning_dir=false
    - critério “Harness não declara PASS quando artefatos centrais faltam.” = true

- O binário genérico do Codex existe localmente:
  - /home/elder/.local/share/mise/installs/node/25.8.0/bin/codex
  - isso não satisfaz EX-33, porque a feature promete wrappers + diretório de evidência, não só o CLI

Conclusão:
O harness Codex core, nesta instalação, não consegue demonstrar execução de tarefa com registro de aprendizado nem revisão do último run. O motivo é estrutural: os dois wrappers centrais e o diretório de evidência prometidos pela feature não existem. O critério “não declarar PASS quando faltam artefatos centrais” está sendo respeitado nos runs locais mais recentes.

DRAFT
Se quiser registrar correção, este é o rascunho local:
“EX-33 falha na entrega do Codex Core Harness wrapper evidence: os paths declarados para run_codex_with_learning.py, review_latest_run.py e ~/.hermes/codex-learning não existem na instalação local, e o setup documentado não provisiona esses artefatos. O codex CLI genérico está presente, mas isso não cumpre o contrato da feature. Aguardando correção do setup/provisionamento e validação com evidência real de run/review.”

{
  "feature_id": "EX-33",
  "observed_status": "fail",
  "evidence": [
    "FEATURES.md:482-484 declara os wrappers em ~/.hermes/scripts/codex_learning/ e o diretório ~/.hermes/codex-learning.",
    "skills/excrtx-harness-hermesops/SKILL.md:58-63 repete a arquitetura com os mesmos paths estáveis.",
    "Probe local atual retornou exists=False para /home/elder/.hermes/scripts/codex_learning/run_codex_with_learning.py.",
    "Probe local atual retornou exists=False para /home/elder/.hermes/scripts/codex_learning/review_latest_run.py.",
    "Probe local atual retornou exists=False para /home/elder/.hermes/codex-learning.",
    "A invocação real do runner falhou com [Errno 2] No such file or directory.",
    "A invocação real do reviewer falhou com [Errno 2] No such file or directory.",
    "Busca em setup.sh por codex_learning/codex-learning/run_codex_with_learning/review_latest_run retornou 0 ocorrências.",
    "O run local /home/elder/projetos/projetob/exocortex.saas/.dogfood/runs/20260607-021733/EX-33/result.json classifica EX-33 como FAIL e marca como atendido o critério de não declarar PASS quando faltam artefatos.",
    "O binário genérico do Codex existe localmente, mas isso não foi aceito como prova da feature EX-33."
  ],
  "external_action_attempted": false,
  "draft_presented": true
}