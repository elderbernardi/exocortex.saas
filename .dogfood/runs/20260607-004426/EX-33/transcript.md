Resultado: FAIL

O harness Codex core não passa no teste solicitado neste ambiente local.

Evidência observada:
- A feature declara estes artefatos como centrais:
  - /home/elder/.hermes/scripts/codex_learning/run_codex_with_learning.py
  - /home/elder/.hermes/scripts/codex_learning/review_latest_run.py
  - /home/elder/.hermes/codex-learning
  Fonte: /home/elder/projetos/projetob/exocortex.saas/FEATURES.md:478-486
- Probe local executado agora:
  - run_wrapper_exists=false
  - review_wrapper_exists=false
  - codex_learning_dir_exists=false
  - codex_cli_present=true
  - codex-cli 0.137.0
  Isso mostra o problema exato que o avaliador quer evitar: a CLI genérica existe, mas o wrapper/evidência do harness não.
- Há evidência histórica local do mesmo achado:
  - /home/elder/projetos/projetob/exocortex.saas/.dogfood/runs/20260607-004426/EX-33/probe.json
  - conteúdo: run_wrapper_exists=false, review_wrapper_exists=false, codex_learning_dir_exists=false
- O baseline local já registra EX-33 como FAIL:
  - /home/elder/projetos/projetob/exocortex.saas/.dogfood/baselines/2026-06-06-summary.md:20-32
- O sumário de dogfood também registra:
  - /home/elder/projetos/projetob/exocortex.saas/acervo/_artifacts/items/feature-dogfood-summary-2026-06-06.md:40-48
  - texto: o Codex CLI funciona em scratch, mas os wrappers declarados não existem
- O teste automatizado local que protege contra falso PASS está verde:
  - /home/elder/projetos/projetob/exocortex.saas/tests/test_dogfood_real_agent_mode.py:92-99
  - execução real: PYTHONPATH=. python3 tests/test_dogfood_real_agent_mode.py
  - resultado: Ran 6 tests in 0.020s / OK
  - esse teste afirma que EX-33 deve retornar FAIL quando wrappers e diretório centrais faltam

Conclusão:
- Não há evidência local de run com learning log.
- Não há evidência local de review do último run via wrapper.
- O ambiente tem o codex CLI, mas não tem o harness central prometido pela feature.
- Portanto, EX-33 falha no objetivo funcional, embora a proteção contra falso PASS pareça estar implementada nos testes atuais.

DRAFT
Nenhuma ação externa foi tentada. Se você quiser, eu preparo um DRAFT de issue com contexto + escopo + critérios de aceite, mas não publico nada sem aprovação.

{
  "feature_id": "EX-33",
  "observed_status": "fail",
  "evidence": [
    "FEATURES.md declara os wrappers em ~/.hermes/scripts/codex_learning/ e as evidências em ~/.hermes/codex-learning: /home/elder/projetos/projetob/exocortex.saas/FEATURES.md:478-486",
    "Probe local atual: run_wrapper_exists=false, review_wrapper_exists=false, codex_learning_dir_exists=false, codex_cli_present=true, codex-cli 0.137.0",
    "Probe histórico local confirma ausência dos artefatos: /home/elder/projetos/projetob/exocortex.saas/.dogfood/runs/20260607-004426/EX-33/probe.json",
    "Baseline local marca EX-33 como FAIL: /home/elder/projetos/projetob/exocortex.saas/.dogfood/baselines/2026-06-06-summary.md:20-32",
    "Resumo de dogfood registra que o Codex CLI funciona, mas os wrappers declarados não existem: /home/elder/projetos/projetob/exocortex.saas/acervo/_artifacts/items/feature-dogfood-summary-2026-06-06.md:40-48",
    "Teste automatizado local confirma que o harness não deve declarar PASS quando wrappers faltam: /home/elder/projetos/projetob/exocortex.saas/tests/test_dogfood_real_agent_mode.py:92-99; execução real: PYTHONPATH=. python3 tests/test_dogfood_real_agent_mode.py -> OK"
  ],
  "external_action_attempted": false,
  "draft_presented": true
}