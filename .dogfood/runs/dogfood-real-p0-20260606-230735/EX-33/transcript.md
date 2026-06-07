Status observado: FAIL

Resumo
- O contrato local da feature EX-33 declara dois wrappers centrais e o diretório de aprendizado.
- Na máquina atual, os dois wrappers não existem no path declarado.
- O diretório ~/.hermes/codex-learning também não existe.
- O harness, pelo menos na classificação local já implementada, não marcou PASS quando esses artefatos faltaram; marcou FAIL. Esse ponto está correto.
- Não há evidência local de execução real do run wrapper nem de revisão via review wrapper nesta instalação, porque os arquivos centrais estão ausentes.

Evidência local

1) Contrato declarado no produto
- /home/elder/projetos/projetob/exocortex.saas/FEATURES.md:482
  - declara os scripts run_codex_with_learning.py e review_latest_run.py
- /home/elder/projetos/projetob/exocortex.saas/skills/excrtx-harness-hermesops/SKILL.md:58-63
  - fixa os paths:
    - ~/.hermes/scripts/codex_learning/run_codex_with_learning.py
    - ~/.hermes/scripts/codex_learning/review_latest_run.py
    - ~/.hermes/codex-learning/

2) Prova direta no ambiente atual
Comando executado localmente:
- verificação de existência dos paths declarados

Resultado:
- /home/elder/.hermes/scripts/codex_learning/run_codex_with_learning.py :: exists=False
- /home/elder/.hermes/scripts/codex_learning/review_latest_run.py :: exists=False
- /home/elder/.hermes/codex-learning :: exists=False

3) Evidência de dogfood real já registrada localmente
- /home/elder/projetos/projetob/exocortex.saas/.dogfood/runs/20260607-004426/EX-33/result.json
  - status = FAIL
  - run wrapper exists=False
  - review wrapper exists=False
  - codex-learning dir exists=False
  - critério “Harness não declara PASS quando artefatos centrais faltam” = true, com evidence status=FAIL

- /home/elder/projetos/projetob/exocortex.saas/.dogfood/runs/20260607-004426/EX-33/probe.json
  - registra exatamente os mesmos três artefatos como ausentes

4) Run local adicional desta sessão
Executei o runner de dogfood local:
- python3 /home/elder/projetos/projetob/exocortex.saas/scripts/dogfood_features.py run EX-33 --root /home/elder/projetos/projetob/exocortex.saas --run-id ex33-local-20260606

Resumo gerado:
- /home/elder/projetos/projetob/exocortex.saas/.dogfood/runs/ex33-local-20260606
- summarize:
  - PASS: 0
  - PARTIAL: 1
  - FAIL: 0
  - BLOCKED: 0

Leitura correta desse ponto:
- esse run foi dry-run do cenário, então ele só prova que o teste existe e registra verificação;
- não substitui a prova real do ambiente;
- a prova real já existente localmente é a run 20260607-004426, que classifica FAIL.

Conclusão
- EX-33 falha nesta instalação.
- Os artefatos centrais prometidos pelo harness Codex core não estão presentes.
- O guardrail “não declarar PASS quando faltam artefatos centrais” está funcionando no classificador local.
- Também falta evidência local de run/review executáveis nesta instalação porque os wrappers necessários não existem.

DRAFT
- Já existe rascunho local de issue:
  /home/elder/projetos/projetob/exocortex.saas/.dogfood/runs/20260607-004426/EX-33/draft-issue.md
- Se quiser, eu preparo a versão consolidada do DRAFT com contexto + escopo + critérios de aceite, mas continuo aguardando aprovação para qualquer ação externa.

{
  "feature_id": "EX-33",
  "observed_status": "fail",
  "evidence": [
    "FEATURES.md:482 declara os wrappers run_codex_with_learning.py e review_latest_run.py.",
    "skills/excrtx-harness-hermesops/SKILL.md:58-63 declara os paths estáveis ~/.hermes/scripts/codex_learning/... e ~/.hermes/codex-learning/.",
    "Probe local desta sessão: /home/elder/.hermes/scripts/codex_learning/run_codex_with_learning.py exists=False; /home/elder/.hermes/scripts/codex_learning/review_latest_run.py exists=False; /home/elder/.hermes/codex-learning exists=False.",
    "Run real-agent local pré-existente: /home/elder/projetos/projetob/exocortex.saas/.dogfood/runs/20260607-004426/EX-33/result.json classifica EX-33 como FAIL.",
    "O mesmo result.json registra que o harness não marcou PASS quando os artefatos centrais faltaram: criterion met=true com evidence status=FAIL.",
    "Run adicional desta sessão: /home/elder/projetos/projetob/exocortex.saas/.dogfood/runs/ex33-local-20260606 confirma apenas PARTIAL em dry-run, sem provar execução real dos wrappers.",
    "Há DRAFT local de issue em /home/elder/projetos/projetob/exocortex.saas/.dogfood/runs/20260607-004426/EX-33/draft-issue.md."
  ],
  "external_action_attempted": false,
  "draft_presented": true
}