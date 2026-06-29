# Acervo MCP Server

Servidor MCP local e fino para o Acervo Control Plane.

## Objetivo

Expor o core semântico do Acervo para agentes via MCP **sem duplicar regra**.
A autoridade continua nesta ordem:

1. `scripts/acervo_semantic_core.py`
2. `scripts/acervoctl.py`
3. `scripts/acervo_mcp_server.py`

Se o servidor tiver mais regra que o core, a arquitetura regrediu.

## Transporte inicial

- `stdio`
- comando local: `python3 scripts/acervo_mcp_server.py`
- smoke test: `python3 scripts/acervo_mcp_server.py --self-test --acervo-root "$PWD/acervo"`

## Tools expostas no corte inicial

- `acervo_list_microversos`
- `acervo_search`
- `acervo_read_page`
- `acervo_prepare_write`
- `acervo_commit_write`
- `acervo_create_entry`
- `acervo_update_entry`
- `acervo_validate_scope`
- `acervo_validate_frontmatter`
- `acervo_export_microverso`

## Contrato

- respostas estruturadas com `status`, `message`, `warnings`
- quando aplicável, incluir `path`, `receipt`, `result`, `matches` ou `content`
- falha de escopo deve ser explícita e verificável
- `prepare_write` e `commit_write` devem espelhar o comportamento da CLI

## Verificação local

```bash
pytest -q tests/test_acervo_mcp_server.py tests/test_setup_acervo_mcp.py
python3 scripts/acervo_mcp_server.py --self-test --acervo-root "$PWD/acervo"
hermes mcp test acervo
```

## Registro no instalador

O setup agora executa `setup/step-11b-integration-acervo-mcp.sh` para:

1. rodar o self-test local do servidor
2. registrar `acervo` via `hermes mcp add`
3. reconciliar `config.yaml` com `ACERVO`, `EXOCORTEX_HOME` e `HERMES_HOME`
4. validar saúde com `hermes mcp test acervo`
5. cair explicitamente para modo degradado (`acervoctl` + acesso direto a arquivos) se o MCP falhar

## Notas de governança

- humano, infra e manutenção continuam com acesso direto ao filesystem
- escrita agentic semântica deve preferir CLI/MCP
- não adicionar tools genéricas de edição de arquivo neste servidor
