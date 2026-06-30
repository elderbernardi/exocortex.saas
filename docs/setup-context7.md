## Setup Context7 — Documentação de Tech Stacks via MCP

Context7 é um MCP server cloud que provê ao agente Hermes documentação sempre
atualizada de bibliotecas e frameworks (Next.js, React, Vue, Python libs, etc.),
evitando que o modelo opere com docs desatualizadas da janela de treino.

### Pré-requisitos

- Conta e API key em https://context7.com
- Hermes Agent instalado e no PATH

### Configuração

1. **Variável de ambiente**:

   ```bash
   CONTEXT7_API_KEY=ctx7-...
   ```

   Adicione a `~/.hermes/.env` ou passe inline:

   ```bash
   CONTEXT7_API_KEY=ctx7-... EXOCORTEX_ENABLE_CONTEXT7=1 bash setup.sh
   ```

2. **Flag de ativação** (toggle explícito recomendado):

   ```bash
   EXOCORTEX_ENABLE_CONTEXT7=1
   ```

   Ou via `bash setup.sh` (modo interativo) — o prompt aparece na seção
   **Features Opcionais**.

   > **Back-compat**: instalações que já têm `CONTEXT7_API_KEY` definida
   > funcionam sem o flag. O `step-11` procede quando a chave estiver presente,
   > mesmo sem `EXOCORTEX_ENABLE_CONTEXT7=1`.

3. **Setup automático** — o step-11 registra o MCP server no Hermes:

   ```bash
   hermes mcp add context7 --command "npx -y @context7/mcp" --env CONTEXT7_API_KEY=<key>
   ```

### Verificação

```bash
# Deve listar 'context7':
hermes mcp list

# Smoke test completo (checagem estrutural + opcional live call):
bash provision/context7/scripts/smoke.sh
```

### Troubleshooting

| Sintoma | Causa provável | Ação |
|---|---|---|
| `context7` ausente em `hermes mcp list` | Step-11 não rodou ou flag desativado | `EXOCORTEX_ENABLE_CONTEXT7=1 bash setup.sh` |
| Lembrete em `$HERMES_HOME/reminders/context7-api-key.md` | `CONTEXT7_API_KEY` não estava definida no momento do setup | Defina a chave e reprocesse: `CONTEXT7_API_KEY=<key> EXOCORTEX_ENABLE_CONTEXT7=1 bash setup.sh` |
| Tool call falha (offline) | Serviço Context7 inacessível | Verifique conectividade e validade da API key em https://context7.com |

**Caminho do lembrete de chave pendente:**

```
$HERMES_HOME/reminders/context7-api-key.md
```

Se esse arquivo existir, o MCP não foi configurado com chave. Após adicionar a
chave e re-rodar o setup, o arquivo permanece (é uma nota para o usuário — não é
apagado automaticamente).

### Arquivos envolvidos

| Caminho | Função |
|---------|--------|
| `~/.hermes/.env` | `CONTEXT7_API_KEY` |
| `setup/step-11-integration-context7.sh` | Registra o MCP server no Hermes |
| `provision/context7/scripts/smoke.sh` | Smoke test estrutural + optional live call |
| `~/.hermes/reminders/context7-api-key.md` | Lembrete gerado quando a chave não foi fornecida |
