# Composio Connect via Hermes MCP OAuth

Use this as the concrete example for the broader `hermes-mcp-oauth-integrations` skill.

## Provider-specific facts

- Hermes-specific setup page: `https://composio.dev/hermes`
- Remote MCP endpoint: `https://connect.composio.dev/mcp`
- Auth model for Hermes: OAuth, no manual auth headers
- Discovery result in this session: 7 meta-tools

## Durable workflow

1. Prefer the Hermes-specific provider page over Composio's generic docs.
2. Add the server with Hermes-native OAuth:

```bash
hermes mcp add composio --url https://connect.composio.dev/mcp --auth oauth
```

3. Complete the OAuth browser flow.
4. Explicitly confirm tool enablement when Hermes prompts after discovery.
5. Validate with:

```bash
hermes mcp list
hermes mcp test composio
```

6. If needed, start a new session or run `/reload-mcp` before expecting the tools in chat.

## Persisted config shape

```yaml
mcp_servers:
  composio:
    url: https://connect.composio.dev/mcp
    auth: oauth
    enabled: true
```

## What mattered

- Composio's generic examples may mention custom headers such as `x-consumer-api-key`. That is not the Hermes path used here.
- Hermes already supports the right flow directly through `hermes mcp add ... --auth oauth`.
- Successful OAuth is not the final step if Hermes still asks whether to enable the discovered tools.

## Validation markers seen in practice

- `hermes mcp list` showed `composio` as enabled.
- `hermes mcp test composio` reported HTTP transport, OAuth 2.1 PKCE, successful connection, and 7 discovered tools.

## Candidate first apps to connect

Good first picks when the operator is a technical executive or staff workflow owner:
- GitHub
- Google Calendar
- Gmail
- Google Docs / Drive
- Telegram
- Discord
- Notion
- Linear

## Documentation pattern for Hermes project

When documenting this class of integration in Hermes docs:
- explain the exact `hermes mcp add` command,
- state that OAuth is automatic for this provider path,
- warn against copying header-based examples from generic provider docs,
- include validation commands,
- include the need to reopen the session or reload MCP tools.
