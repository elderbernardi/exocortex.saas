## Setup Hindsight — Memória Operacional

### Pré-requisitos

- Docker
- Chave Hindsight (`HINDSIGHTS_API_KEY`) — obter em https://ui.hindsight.vectorize.io
- Chave de LLM backend para o Hindsight processar embeddings/raciocínio

### Configuração

1. **Variáveis de ambiente** (`~/.hermes/.env`):

   ```
   HINDSIGHT_API_KEY=hsk_.....
   HINDSIGHT_LLM_API_KEY=<mesma ou chave de LLM OpenAI-compatível>
   # Se usar provedor OpenAI-compatível como DeepSeek:
   HINDSIGHT_API_LLM_MODEL=deepseek-v4-flash
   HINDSIGHT_API_LLM_BASE_URL=https://api.deepseek.com/v1
   ```

2. **Container Docker**:

   ```bash
   docker run -d \
     --name exocortex-hindsight \
     --restart unless-stopped \
     -p 8888:8888 \
     -p 9999:9999 \
     -v ~/.hermes/hindsight-local/data:/home/hindsight/.pg0 \
     --env HINDSIGHT_API_LLM_PROVIDER=openai \
     --env HINDSIGHT_API_LLM_API_KEY=<chave> \
     --env HINDSIGHT_API_LLM_MODEL=deepseek-v4-flash \
     --env HINDSIGHT_API_LLM_BASE_URL=https://api.deepseek.com/v1 \
     ghcr.io/vectorize-io/hindsight:latest
   ```

   Ou via `EXOCORTEX_ENABLE_HINDSIGHT=1 bash setup.sh` no repositório.

3. **Config do plugin** (`~/.hermes/hindsight/config.json`):

   ```json
   {
     "mode": "local_external",
     "api_url": "http://localhost:8888",
     "bank_id": "exocortex",
     "memory_mode": "hybrid",
     "auto_recall": true,
     "auto_retain": true,
     "retain_async": true,
     "retain_every_n_turns": 2,
     "recall_budget": "low",
     "recall_prefetch_method": "recall",
     "recall_types": "observation",
     "recall_max_tokens": 1200,
     "recall_max_input_chars": 800
   }
   ```

4. **Ativar no Hermes**:

   ```bash
   hermes config set memory.provider hindsight
   hermes config set memory.memory_enabled false
   hermes config set memory.user_profile_enabled false
   ```

5. **Reiniciar gateway** para carregar o provider:

   ```bash
   # De fora do gateway (outro terminal):
   hermes gateway restart
   ```

### Validação

```bash
hermes memory status
# Provider: hindsight
# Status: available ✓
```

### Arquivos envolvidos

| Caminho | Função |
|---------|--------|
| `~/.hermes/.env` | `HINDSIGHT_API_KEY`, `HINDSIGHT_LLM_API_KEY` |
| `~/.hermes/config.yaml` | `memory.provider=hindsight` |
| `~/.hermes/hindsight/config.json` | Configuração do plugin |
| `~/.hermes/hindsight-local/` | Container Docker + dados persistentes |

### Notas

- `local_external` = usado para conectar ao container Docker local (http://localhost:8888). `local_embedded` tentaria iniciar um daemon Python nativo no host.
- Memorial: https://ui.hindsight.vectorize.io (porta 9999 local)
- Reset destrutivo requer: `EXOCORTEX_HINDSIGHT_RESET_DATA=1` e `EXOCORTEX_HINDSIGHT_CONFIRM_DELETE=DELETE_HINDSIGHT_MEMORY`
