# Exocórtex.IA

> Exoesqueleto para o pensamento. A IA não tem alma. Você tem.

## Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/elderbernardi/exocortex.saas/main/install.sh | bash
```

### Com Telegram

```bash
TELEGRAM_BOT_TOKEN="seu_token" curl -fsSL https://raw.githubusercontent.com/elderbernardi/exocortex.saas/main/install.sh | bash
```

### Versão específica

```bash
VERSION=v1.0.0-rc2 curl -fsSL https://raw.githubusercontent.com/elderbernardi/exocortex.saas/main/install.sh | bash
```

## O que é instalado

O instalador faz tudo automaticamente:

1. **Hermes Agent** — runtime de IA (se não estiver instalado)
2. **35 skills** do Exocórtex — organizadas em 9 categorias (`excrtx-{TYPE}-{NAME}`)
3. **Acervo cognitivo** — estrutura de 4 camadas (macro/global/micro/shared)
4. **SOUL.md** — contrato de identidade
5. **Profiles** — default (interativo) + manut (background)
6. **Integrações** — NotebookLM, DocBrain, Context7, Google Drive

## Requisitos

- Linux ou macOS
- `git`, `curl`, `rsync`
- Python 3.11+

## Uso

```bash
hermes                    # sessão interativa
hermes -p manut           # modo manutenção (background)
```

## Re-instalar / Atualizar

```bash
bash ~/.exocortex-installer/install.sh
# ou com nova versão:
VERSION=<tag> bash ~/.exocortex-installer/install.sh
```

## Licença

MIT — veja [LICENSE](LICENSE).
