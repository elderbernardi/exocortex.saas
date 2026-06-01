---
title: Superfícies Operacionais — Dashboard, Gateway e Acesso Seguro
created: 2026-05-29
updated: 2026-05-29
nature: processos
type: workflow
tags: [workflow-global, seguranca, comunicacao, processo]
sources: [INSTALL.md, plans/DECISIONS.md, plans/KNOWLEDGE.md]
confidence: high
---

# Superfícies Operacionais

Define como o Exocórtex deve ser exposto e operado quando o objetivo é entregar baixa fricção ao executivo sem abrir mão de segurança operacional.

## Objetivo

Separar claramente:

- a interface principal do executivo
- a superfície de operação do administrador
- a camada de acesso remoto seguro

## Arquitetura Recomendada

### 1. Interface principal do executivo

Canal preferencial: **Telegram + Hermes Gateway**.

Motivo:
- menor fricção de uso
- não exige URL nem login adicional
- reduz carga cognitiva para uso cotidiano

Regra prática:
- o executivo conversa com o Exocórtex no canal de mensagem
- o dashboard não é a superfície primária do usuário final

### 2. Superfície operacional do administrador

Canal preferencial: **Hermes Dashboard com TUI embutida**.

Comando base:

```bash
hermes dashboard --tui --no-open
```

Uso esperado:
- recuperação e retomada de sessões
- inspeção de logs
- ajuste de configuração
- operação técnica do runtime

Após o primeiro build do frontend, preferir reinício com:

```bash
python -m hermes_cli.main dashboard --tui --no-open --skip-build
```

## Persistência Recomendada

Em Linux com `systemd --user`, persistir o dashboard como serviço de sessão.

Arquivo de referência:

```bash
~/.config/systemd/user/hermes-dashboard.service
```

Fluxo operacional:

```bash
systemctl --user daemon-reload
systemctl --user enable --now hermes-dashboard.service
systemctl --user status hermes-dashboard.service
```

Critério de pronto:
- serviço em `active (running)`
- dashboard respondendo em `127.0.0.1:9119`
- aba `CHAT` disponível quando iniciado com `--tui`

## Regra de Segurança

O dashboard expõe superfícies sensíveis do Hermes:
- sessões
- configurações
- logs
- skills
- chaves e integrações

Por isso, a regra global é:

- manter bind local em `127.0.0.1:9119`
- não expor a porta `9119` publicamente
- não usar `--insecure` como padrão
- não tratar reverse proxy público como default seguro

## Acesso Remoto

Padrão aceito:
- **Tailscale** para acesso recorrente e administrado
- túnel SSH para acesso pontual

Exemplos:

```bash
# túnel SSH temporário
ssh -L 9119:127.0.0.1:9119 user@host
```

Diretriz:
- Tailscale é requisito de segurança do setup remoto
- não é opcional de conveniência
- se o dashboard precisar sair do localhost, isso deve acontecer dentro de malha privada controlada

## Resumo Executivo

- executivo usa Telegram
- operador usa Dashboard
- Dashboard fica privado
- acesso remoto seguro passa por Tailscale ou túnel SSH

[Acervo: global/superficies-operacionais]
