---
name: excrtx-integrate-oauth
description: Configure and validate remote MCP servers in Hermes when the provider uses HTTP transport plus OAuth, then document
  the integration cleanly for future reuse.
version: 1.0.0
category: excrtx
platforms:
- linux
triggers:
- User wants to connect Hermes to a remote MCP server over HTTP.
- Provider docs mention OAuth or PKCE instead of static headers.
- Task involves adding, testing, or documenting a third-party cloud integration for Hermes.
- You need to translate generic provider docs into the exact Hermes CLI flow.
metadata:
  hermes:
    tags:
    - exocortex
    - integrate
    - oauth
    calibration:
    - feature_id: EX-26
      calibration_prompt: 'Você configura e valida MCP servers remotos com HTTP transport + OAuth. Separa guidance genérica
        de providers da guidance específica do Hermes. Valida em 3 camadas: mcp list, mcp test, sessão real.'
      test_prompt: Preciso integrar um novo MCP server chamado 'notion-mcp' que usa OAuth. Como faço a configuração?
      acceptance_criteria: '1. O agente explica o fluxo de configuração passo a passo (add → auth → test → sessão)

        2. Menciona validação em 3 camadas (mcp list, mcp test, sessão real)

        3. Separa guidance do provider (Notion) da configuração Hermes

        4. Sugere documentar a integração para reuso futuro'
      remediation_tip: 'FALHA: Configuração incompleta ou sem validação em 3 camadas. O fluxo completo é: 1) ''hermes mcp
        add notion-mcp --transport http --url <URL>'', 2) Autenticação OAuth via browser, 3) ''hermes mcp list'' (verificar
        registro), 4) ''hermes mcp test notion-mcp'' (verificar conexão), 5) Sessão real com teste funcional.'
---
# Hermes MCP OAuth Integrations

Use this skill when Hermes must connect to a third-party remote MCP server that authenticates via OAuth rather than static bearer headers. The goal is to derive the exact Hermes-native flow, validate it end to end, and leave reusable documentation behind.

## Outcome

Produce four things:
1. a working `hermes mcp add ...` command,
2. a validated server entry in `~/.hermes/config.yaml`,
3. a successful `hermes mcp test <name>` result,
4. durable docs that explain the Hermes-specific path, not the provider's generic examples.

## Workflow

1. Read Hermes docs and CLI behavior first.
   - Confirm the real command shape in Hermes docs or source before trusting vendor examples.
   - For MCP configuration, verify support for `--url`, `--auth`, `--env`, and transport behavior.
   - If the task is about Hermes itself, load the protected `hermes-agent` skill for orientation, but store any reusable operator learning in this skill or its references.

2. Separate provider-generic guidance from Hermes-specific guidance.
   - Many vendors publish examples for Claude Desktop, Cursor, or raw HTTP clients.
   - Do not copy generic header-based examples into Hermes if the provider offers a Hermes page or if Hermes already supports OAuth natively.
   - Prefer a provider page tailored to Hermes when available.

3. Configure the server the Hermes-native way.
   - Typical pattern:
     `hermes mcp add <name> --url <remote_mcp_url> --auth oauth`
   - For remote HTTP servers, do not invent `--env` or manual headers unless the provider explicitly requires header auth and Hermes docs confirm that path.
   - Expect an OAuth browser flow and possible interactive confirmation prompts.

4. Handle the interactive enablement step explicitly.
   - After discovery, Hermes may ask whether to enable all discovered tools.
   - If automating, send an explicit answer rather than assuming non-interactive completion.
   - The durable lesson is not the exact prompt text; it is that successful OAuth setup can still stop at the post-discovery enablement confirmation.

5. Validate in three layers.
   - `hermes mcp list`
   - `hermes mcp test <name>`
   - one real Hermes session using the newly exposed tools when feasible

6. Inspect the final persisted state.
   - Confirm the server appears under `mcp_servers` in `~/.hermes/config.yaml`.
   - Verify `url`, `auth`, and `enabled` match the intended setup.
   - Never copy secrets or OAuth tokens into docs, memory, or skill files.

7. Document the integration in Hermes docs with product accuracy.
   - Document the exact command the operator should run.
   - Call out whether the provider uses OAuth automatically.
   - Explain when to prefer this integration path over browser automation or ad hoc API work.
   - Add troubleshooting for the class of issue, especially post-discovery prompts and session reload requirements.

## Pitfalls

- Do not assume provider docs that mention `x-consumer-api-key` or custom headers apply to Hermes.
- Do not document a raw MCP transport recipe before checking whether Hermes already has first-class OAuth support.
- Do not stop after OAuth succeeds; Hermes may still require tool-enable confirmation before saving the server.
- Do not claim success until `hermes mcp test <name>` passes.
- Do not leak browser callback URLs, tokens, codes, or session identifiers.

## Special case: CLI-backed MCP providers (example: NotebookLM)

Some integrations ship as a local CLI + local MCP server pair (not a hosted OAuth URL). In this class:

1. Validate CLI auth with the command the installed CLI version actually supports.
   - Do not assume `auth status` exists across versions.
   - For current NotebookLM CLI (`nlm` v0.6.x), use `nlm login --check`.

2. Register MCP with stdio command transport.
   - Pattern: `hermes mcp add <name> --command <mcp-server-binary>`
   - Example: `hermes mcp add notebooklm --command notebooklm-mcp`

3. Handle interactive tool-enable confirmation explicitly.
   - `hermes mcp add` may discover tools and then wait for enablement confirmation.
   - In automation/setup scripts, pipe an explicit answer (for example `printf 'y\n' | ...`) to avoid false-positive "configured" logs when nothing was saved.

4. Verify persistence, not just connection output.
   - A successful discovery banner is insufficient.
   - Confirm `hermes mcp list` and `mcp_servers.<name>` in config after command completion.

## Verification checklist

- Server appears in `hermes mcp list`
- `hermes mcp test <name>` connects successfully
- Expected tool count is discovered
- `~/.hermes/config.yaml` contains the intended `mcp_servers.<name>` entry
- Docs mention opening a new session or using `/reload-mcp`
- Docs explain Hermes-specific auth behavior, not just vendor-generic auth

## References

- `references/composio-connect.md` — concrete example of this pattern using Composio Connect and the Hermes-specific OAuth flow.
- `references/notebooklm-cli-mcp.md` — CLI-backed MCP pattern (local auth check + stdio registration + non-interactive confirmation).

## When to reuse

Reuse this skill for any future remote MCP provider that:
- exposes a hosted MCP endpoint,
- authenticates with OAuth/PKCE,
- publishes generic client docs that need translation into Hermes CLI steps,
- or requires project documentation after configuration.

## When to Use

Activate when:
- Hermes must connect to a remote MCP server over HTTP
- Provider docs mention OAuth or PKCE instead of static bearer headers
- Adding, testing, or documenting a third-party cloud integration for Hermes
- Translating generic provider docs into the exact Hermes CLI flow
- Connecting CLI-backed MCP providers like NotebookLM that use local auth + stdio transport

**Don't use for:** MCP servers using static API keys or headers (configure directly in `config.yaml`). Hermes runtime modifications (use `excrtx-hermes-extensions`). General tool development (use `excrtx-harness-tooldev`).

## Procedure

Follow the Workflow section above (steps 1-7). For CLI-backed providers, use the Special Case section.
