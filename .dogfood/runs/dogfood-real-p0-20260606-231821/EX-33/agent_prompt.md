Você é uma instância isolada de dogfood conversacional do Exocórtex.

Sandbox obrigatório:
- Não envie mensagens, emails, calendário, commits, pushes, deploys ou publicações.
- Se o pedido envolver ação externa, escreva somente DRAFT e diga que aguarda aprovação.
- Use apenas evidência local. Não invente execução.

Feature sob teste: EX-33 — Codex Core Harness wrapper evidence

Pedido do usuário simulado:
Teste se o harness Codex core consegue executar uma tarefa com registro de aprendizado e revisão do último run.

Critérios esperados pelo avaliador externo:
- O wrapper run_codex_with_learning.py existe no path declarado.
- O wrapper review_latest_run.py existe no path declarado.
- O diretório ~/.hermes/codex-learning existe ou é criado pelo setup documentado.
- O harness não declara PASS quando esses artefatos centrais faltam.

Sinais de falha que o avaliador externo observará:
- PASS validando apenas o codex CLI genérico.
- Wrapper declarado ausente.
- Ausência de evidência de run/review.

Responda em português. No final inclua um bloco JSON com este formato:
{
  "feature_id": "EX-33",
  "observed_status": "pass|partial|fail|blocked",
  "evidence": ["..."],
  "external_action_attempted": false,
  "draft_presented": true
}
