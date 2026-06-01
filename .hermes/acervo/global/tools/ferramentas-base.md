---
title: Ferramentas e Integrações — Configuração Global
created: 2026-05-28
updated: "2026-05-28"
nature: ferramenta
type: tool
tags: [hermes-core, tools, integrations, gmail, workspace, suap, telegram, github]
confidence: high
---

# Ferramentas e Integrações

## Hermes Core (sempre disponível)

### Filesystem
- **read_file** — Leitura paginada de arquivos
- **write_file** — Criação/sobrescrita de arquivos
- **patch** — Edição cirúrgica find-and-replace

### Terminal
- **terminal** — Execução de comandos shell (foreground e background)
- **process** — Gerenciamento de processos em background

### Search
- **search_files** — Busca em conteúdo e nomes de arquivo (ripgrep)
- **session_search** — Busca em sessões anteriores

### Web
- **browser_navigate** — Navegação e interação web
- **browser_snapshot** — Captura de estado da página

### Code
- **execute_code** — Execução de scripts Python com acesso a tools

## Integrações do Executivo

### Configuradas
- **Gmail** — comunicação institucional
- **Google Workspace** — documentos, planilhas, apresentações
- **Google Calendar** — gestão de agenda
- **Google Tasks** — tarefas e follow-ups
- **GitHub** — repositórios, issues, code review, CI/CD
- **Telegram** — comunicação, distribuição de conteúdo

### A Configurar
- **SUAP** — sistema acadêmico do IFSul (notas, frequências, diários)
- **Ferramentas de criação de conteúdo** — a definir pelo executivo

## Status de Integração

| Integração | Status | Microverso Principal |
|---|---|---|
| Gmail | configurado | gabinete |
| Google Calendar | configurado | gabinete |
| Google Workspace | configurado | gabinete, ensino |
| Google Tasks | configurado | gabinete |
| GitHub | configurado | dev |
| Telegram | configurado | pesquisa-ia |
| SUAP | pendente | gabinete, ensino |
| Content tools | pendente | pesquisa-ia |
