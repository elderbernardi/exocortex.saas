# Hermes WebUI — Provisioner do Exocórtex

Provisiona o `hermes-webui` (nesquena/hermes-webui) como cockpit web do Exocórtex.

## Stack

- Backend: Python HTTP server (SSE, WebSocket)
- Frontend: Vanilla JS + CSS (zero build step)
- Licença: **MIT** — uso comercial irrestrito

## Estrutura

```
provision/hermes-webui/
├── README.md           # Este arquivo
└── scripts/
    ├── install.sh      # Clona, instala deps, configura
    └── smoke.sh        # Verifica saúde do serviço
```

## Uso

### Provisionar durante o setup

```bash
EXOCORTEX_ENABLE_HERMES_WEBUI=1 HERMES_HOME=~/.hermes EXOCORTEX_HOME=~/exocortex bash setup.sh
```

### Provisionar standalone

```bash
bash provision/hermes-webui/scripts/install.sh
```

### Iniciar o serviço

```bash
cd ~/.hermes/hermes-webui
./ctl.sh start
```

### Acessar

- Local: `http://127.0.0.1:8787`
- Remoto via Tailscale: `http://<tailscale-ip>:8787`

## Variáveis de ambiente

| Variável | Default | Descrição |
|---|---|---|
| `EXOCORTEX_ENABLE_HERMES_WEBUI` | `0` | Ativa provisionamento durante setup |
| `EXOCORTEX_HERMES_WEBUI_HOME` | `$HERMES_HOME/hermes-webui` | Diretório de instalação do webui |
| `EXOCORTEX_HERMES_WEBUI_PORT` | `8787` | Porta do servidor |
| `EXOCORTEX_HERMES_WEBUI_HOST` | `127.0.0.1` | Bind address |

## Fonte controlada

- upstream: `nesquena/hermes-webui` (MIT)
- ref pinada: via `provision/sources/sources.lock.yaml`
- sync: `bash provision/sources/sync-upstreams.sh --source hermes-webui`
