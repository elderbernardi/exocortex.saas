## Setup Hindsight — Memória Operacional

### Pré-requisitos

- Docker
- Chave Hindsight (`HINDSIGHT_API_KEY`, serviço cloud) — obter em https://ui.hindsight.vectorize.io
- Um papel LLM configurado para o backend que processa embeddings/raciocínio (papel **default** ou um **auxiliar** específico)

### Configuração

1. **Variáveis de ambiente** (`~/.hermes/.env`):

   O backend LLM do Hindsight é configurado pelo **papel auxiliar** (`aux`) do
   modelo de 3 papéis. Você **não** define mais `HINDSIGHT_LLM_API_KEY`,
   `DEEPSEEK_API_KEY` nem `OPENROUTER_API_KEY` para o Hindsight: basta ter o
   papel `default` configurado (o `aux` herda o `default` campo a campo quando
   vazio) ou definir um `aux` específico.

   ```
   # Serviço Hindsight (cloud) — permanece como está:
   HINDSIGHT_API_KEY=hsk_.....

   # Backend LLM — papel default (sempre usado; obrigatório):
   EXOCORTEX_DEFAULT_PROVIDER=deepseek
   EXOCORTEX_DEFAULT_MODEL=deepseek-v4-flash
   EXOCORTEX_DEFAULT_API_KEY=<chave LLM OpenAI-compatível>
   EXOCORTEX_DEFAULT_BASE_URL=          # vazio → resolvido por setup/providers.json

   # Opcional: backend LLM dedicado ao Hindsight (papel auxiliar).
   # Qualquer campo vazio herda o default.
   # EXOCORTEX_AUX_PROVIDER=...
   # EXOCORTEX_AUX_MODEL=...
   # EXOCORTEX_AUX_API_KEY=...
   # EXOCORTEX_AUX_BASE_URL=...
   ```

   O `setup/step-01-hindsight.sh` resolve o papel `aux` (com herança do
   `default`) e gera o `.env` interno do Hindsight com as variáveis de contrato
   do container — `HINDSIGHT_API_LLM_API_KEY`, `HINDSIGHT_API_LLM_MODEL` e
   `HINDSIGHT_API_LLM_BASE_URL` (esta derivada do provider do papel). Essas
   variáveis continuam existindo, mas agora são **geradas a partir do papel
   `aux`** — você não as edita à mão.

   > Instalações antigas (com `HINDSIGHT_LLM_API_KEY`/`DEEPSEEK_API_KEY` etc.)
   > são migradas automaticamente para os papéis por `scripts/migrate-env-roles.py`,
   > executado pelo `setup.sh`.

2. **Container Docker** (as variáveis `HINDSIGHT_API_LLM_*` abaixo são geradas
   pelo `step-01-hindsight.sh` a partir do papel `aux` — mostradas aqui apenas
   para referência do contrato do container):

   ```bash
   docker run -d \
     --name exocortex-hindsight \
     --restart unless-stopped \
     -p 8888:8888 \
     -p 9999:9999 \
     -v ~/.hermes/hindsight-local/data:/home/hindsight/.pg0 \
     --env HINDSIGHT_API_LLM_PROVIDER=openai \
     --env HINDSIGHT_API_LLM_API_KEY=<chave do papel aux> \
     --env HINDSIGHT_API_LLM_MODEL=<modelo do papel aux> \
     --env HINDSIGHT_API_LLM_BASE_URL=<base URL derivada do provider do papel aux> \
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
   hermes config set memory.memory_enabled true
   hermes config set memory.user_profile_enabled true
   ```

   > Mantenha a memória built-in ativa. O provider `hindsight` complementa o runtime; ele não substitui a tool `memory(...)`. Se os flags acima ficarem `false`, `hindsight_*` continua funcionando, mas `memory(...)` fica indisponível até abrir uma nova sessão com os flags corrigidos.

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
| `~/.hermes/.env` | `HINDSIGHT_API_KEY` (serviço cloud) + papéis LLM `EXOCORTEX_DEFAULT_*` / `EXOCORTEX_AUX_*` (backend LLM) |
| `~/.hermes/config.yaml` | `memory.provider=hindsight` |
| `~/.hermes/hindsight/config.json` | Configuração do plugin |
| `~/.hermes/hindsight-local/` | Container Docker + dados persistentes |

### Notas

- `local_external` = usado para conectar ao container Docker local (http://localhost:8888). `local_embedded` tentaria iniciar um daemon Python nativo no host.
- Memorial: https://ui.hindsight.vectorize.io (porta 9999 local)
- Reset destrutivo requer: `EXOCORTEX_HINDSIGHT_RESET_DATA=1` e `EXOCORTEX_HINDSIGHT_CONFIRM_DELETE=DELETE_HINDSIGHT_MEMORY`
