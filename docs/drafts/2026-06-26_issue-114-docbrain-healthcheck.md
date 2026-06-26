# DRAFT — comentário da issue #114

Executei o health check do DocBrain no runtime atual e validei um smoke real de parse.

## Evidência executada

```bash
cd /home/elder/projetos/projetob/docbrain
npm run --silent cli -- api health --output json
node --version
python3 --version
npm run --silent cli -- api parse create \
  --input /home/elder/projetos/projetob/docbrain/raw/documents/ABAAS_RANKING_MAR_26.pdf \
  --include tables,sections \
  --output json
```

## Resultado

- `api health` respondeu `ok=true` e `api_version=docbrain.cli.v1`
- capabilities reportadas: `parse.create`
- Node no runtime: `v25.8.0`
- Python no runtime: `3.11.15`

Smoke do PDF `ABAAS_RANKING_MAR_26.pdf`:
- `document_id`: `sha256:bc4b52649ca715a55998817efe717d8b0c925e63533724689992893323f2fc26`
- `extractor`: `liteparse`
- `sections`: `35`
- `tables`: `26`
- `job_id`: `job_ca1ca426-5a96-4d33-8995-5b87d2a6989f`

## Diagnóstico

O runtime está funcional para o caminho que interessa à Fase 5: health check + parse determinístico real.

Pontos de drift encontrados:

1. **Workspace/path**
   - A documentação e a skill tratavam `~/exocortex/tools/docbrain` como caminho canônico único.
   - Na prática, o consumo atual precisa resolver o workspace ativo antes de usar a engine (repo-local ou clone gerenciado).

2. **LLM key**
   - O contrato antigo ainda sugeria `OPENROUTER_API_KEY` como default.
   - O `.env.example` atual do DocBrain usa precedência `DOCBRAIN_LLM_API_KEY -> DEEPSEEK_API_KEY`.
   - Health check e `parse.create` com `llm=false` passaram sem chave LLM preenchida no `.env` local.

3. **Python 3.12+**
   - README/`python/pyproject.toml` do DocBrain continuam declarando Python `>=3.12` para a toolchain Python.
   - Mesmo assim, o health check e este smoke PDF passaram com Python `3.11.15` no runtime atual.
   - Conclusão: `3.12+` segue sendo requisito documentado para a stack Python do projeto, mas **não bloqueou** o caminho validado nesta issue. O requisito parece afetar extratores/tooling Python específicos, não o baseline `api health` + parse PDF via LiteParse.

## Ajustes locais aplicados no lado Exocortex

Corrigi o drift documental local em:
- `.harness/contracts/exocortex-to-docbrain.md`
- `README.md`
- `FEATURES.md`
- `skills/excrtx-integrate-docbrain/SKILL.md`
- `skills/excrtx-harness-surfaces/references/local-cli-api-contracts.md`

## Status

Critério funcional desta issue atendido: DocBrain está operacional no runtime atual e desbloqueia a Fase 5b.
