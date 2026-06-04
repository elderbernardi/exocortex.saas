# Hindsight local_embedded vs key requirement (Hermes)

Contexto operacional observado:
- Hermes com `memory.provider: hindsight` e `mode: local_embedded` em `~/.hermes/hindsight/config.json`.
- `hermes memory status` reportou plugin instalado, porém `not available`.
- Missing keys reportadas: `HINDSIGHT_API_KEY` e `HINDSIGHT_LLM_API_KEY`.

Leitura correta:
1. `local_embedded` descreve onde roda o storage/serviço de memória.
2. Não garante ausência de autenticação da plataforma no plugin Hermes.
3. Backend LLM (model/base_url/key) é uma camada separada da autenticação do provider.

Checklist de ativação (sem ambiguidade):
1. Configurar backend LLM (`llm_base_url`, `llm_model`, chave do backend).
2. Rodar `hermes memory status`.
3. Se `HINDSIGHT_API_KEY` estiver em Missing, considerar bloqueio real de ativação do provider.
4. Escolher entre:
   - provisionar chave da plataforma Hindsight, ou
   - trocar provider para alternativa local-first sem essa exigência.

Mensagem recomendada ao usuário:
- Evitar "está local, então não precisa chave".
- Usar: "local_embedded = storage local; plugin pode exigir autenticação própria; backend LLM é outra camada".
