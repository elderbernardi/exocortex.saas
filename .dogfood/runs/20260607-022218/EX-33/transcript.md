Resultado do dogfood conversacional para EX-33: FAIL.

O que verifiquei localmente:
- A feature declara em /home/elder/projetos/projetob/exocortex.saas/FEATURES.md:482-484 que os wrappers centrais são:
  - /home/elder/.hermes/scripts/codex_learning/run_codex_with_learning.py
  - /home/elder/.hermes/scripts/codex_learning/review_latest_run.py
  - evidências em /home/elder/.hermes/codex-learning/
- Probe local via Python:
  - run_wrapper_exists=false
  - review_wrapper_exists=false
  - learning_dir_exists=false
  - runs/events/reviews também inexistentes
- Busca no repositório-fonte por run_codex_with_learning.py e review_latest_run.py retornou 0 arquivos.
- O classificador local da feature, em /home/elder/projetos/projetob/exocortex.saas/scripts/dogfood_features.py:418-439, devolve FAIL quando esses artefatos faltam.
- Execução real do classificador com probe local retornou status=FAIL.
- Teste unitário focalizado passou:
  - python3 -m unittest tests.test_dogfood_real_agent_mode.DogfoodRealAgentModeTest.test_ex33_real_agent_probe_fails_when_wrappers_missing
  - resultado: OK
- O codex CLI genérico existe localmente (codex-cli 0.137.0), mas isso não prova o harness EX-33. O avaliador externo explicitamente trataria como falha um PASS baseado só nisso.

Conclusão objetiva:
- Não há evidência local de run com learning.
- Não há evidência local de review do último run.
- Os wrappers declarados pela feature não existem no path contratado.
- O lado bom é que o harness de avaliação atual não marcou PASS nessas condições; o classificador semântico de EX-33 retornou FAIL, como deveria.

DRAFT
Se você quiser, eu preparo um rascunho de issue local com contexto + escopo + critérios de aceite para corrigir a instalação/entrega dos wrappers EX-33. Aguardo aprovação.

{
  "feature_id": "EX-33",
  "observed_status": "fail",
  "evidence": [
    "FEATURES.md:482-484 declara os wrappers em ~/.hermes/scripts/codex_learning/ e as evidências em ~/.hermes/codex-learning/.",
    "Probe local retornou run_wrapper_exists=false para /home/elder/.hermes/scripts/codex_learning/run_codex_with_learning.py.",
    "Probe local retornou review_wrapper_exists=false para /home/elder/.hermes/scripts/codex_learning/review_latest_run.py.",
    "Probe local retornou learning_dir_exists=false para /home/elder/.hermes/codex-learning; subdirs runs/events/reviews inexistentes.",
    "Busca no repositório-fonte /home/elder/projetos/projetob/exocortex.saas não encontrou run_codex_with_learning.py nem review_latest_run.py.",
    "scripts/dogfood_features.py:418-439 classifica EX-33 como FAIL quando wrappers/diretório faltam.",
    "Execução local de classify_agent_transcript para EX-33 retornou status=FAIL.",
    "Teste unitário focalizado tests.test_dogfood_real_agent_mode.DogfoodRealAgentModeTest.test_ex33_real_agent_probe_fails_when_wrappers_missing passou com OK.",
    "codex --version retornou codex-cli 0.137.0, mas isso é apenas o CLI genérico e não evidencia o harness EX-33."
  ],
  "external_action_attempted": false,
  "draft_presented": true
}