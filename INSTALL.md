# Exocórtex.IA — Manual de Instalação

> **Versão:** 3.0.1
> **Última atualização:** 2026-05-29
> **Repositório:** [github.com/elderbernardi/exocortex.saas](https://github.com/elderbernardi/exocortex.saas)

---

## Índice

- [Visão Geral](#visão-geral)
- [Pré-requisitos](#pré-requisitos)
- [Instalação Rápida](#instalação-rápida)
- [Modos de Instalação](#modos-de-instalação)
  - [Modo Local](#modo-local)
  - [Modo Docker](#modo-docker)
- [Referência de Parâmetros](#referência-de-parâmetros)
- [Credenciais LLM](#credenciais-llm)
- [PDD — Prompt-Driven Development](#pdd--prompt-driven-development)
- [Superfícies Operacionais](#superfícies-operacionais)
- [Exemplos de Uso](#exemplos-de-uso)
- [Verificação](#verificação)
- [Troubleshooting](#troubleshooting)
- [Desinstalação](#desinstalação)

---

## Visão Geral

O instalador do Exocórtex.IA transforma uma instância do [Hermes Agent](https://github.com/NousResearch/hermes-agent) em um assistente cognitivo pessoal completo. O processo consiste em:

1. **Instalação do Hermes Agent** (se necessário)
2. **Configuração de credenciais LLM** (autenticação com o modelo de linguagem)
3. **Aplicação da Golden Image** — copia 15 skills, 4 camadas de acervo, 2 profiles e 1 bundle
4. **Execução do PDD** (opcional) — 27 prompts conversacionais que configuram a identidade e comportamento

O instalador é **totalmente autônomo** — pode ser executado remotamente via SSH, em pipelines CI/CD, ou manualmente com interação mínima.

---

## Pré-requisitos

### Modo Local

| Dependência | Versão Mínima | Verificação | Obrigatório |
|-------------|---------------|-------------|-------------|
| **bash** | 4.0+ | `bash --version` | ✅ |
| **curl** | qualquer | `curl --version` | ✅ |
| **tar** | qualquer | `tar --version` | ✅ (apenas download remoto) |
| **Python** | 3.11+ | `python3 --version` | ✅ (para o Hermes) |
| **git** | qualquer | `git --version` | Recomendado |

### Modo Docker

| Dependência | Versão Mínima | Verificação | Obrigatório |
|-------------|---------------|-------------|-------------|
| **Docker** | 20.0+ | `docker --version` | ✅ |
| **Docker Compose** | v2 | `docker compose version` | Recomendado |
| **curl** | qualquer | `curl --version` | ✅ (apenas download remoto) |

---

## Instalação Rápida

### One-liner (recomendado)

```bash
curl -fsSL https://raw.githubusercontent.com/elderbernardi/exocortex.saas/main/install-exocortex.sh | bash
```

Isso executa a instalação local com todos os defaults: instala o Hermes (se necessário), aplica a golden image em `~/.hermes`, e pergunta sobre credenciais LLM.

### One-liner não-interativo (para automação)

```bash
curl -fsSL https://raw.githubusercontent.com/elderbernardi/exocortex.saas/main/install-exocortex.sh \
  | bash -s -- --api-key sk-or-YOUR_KEY --non-interactive
```

### A partir do repositório clonado

```bash
git clone https://github.com/elderbernardi/exocortex.saas.git
cd exocortex.saas
bash install-exocortex.sh
```

---

## Modos de Instalação

### Modo Local

> **Flag:** `--mode local` (default — não precisa especificar)

Instala diretamente na máquina do usuário. O Hermes Agent e todos os artefatos do Exocórtex ficam em `~/.hermes` (ou no path especificado por `--hermes-home`).

**Fluxo:**

```
1. Preflight checks (curl, python3)
2. Instalação do Hermes Agent (se necessário)
3. Configuração de credenciais LLM (interativo ou via --api-key)
4. Cópia da Golden Image para HERMES_HOME
5. Verificação estrutural (15 skills, 4 layers, 2 profiles)
6. Execução do PDD (se --with-pdd)
```

**Exemplo completo:**

```bash
bash install-exocortex.sh \
  --mode local \
  --api-key sk-or-v1-xxxxxxxxxxxx \
  --hermes-home ~/.hermes \
  --non-interactive
```

**O que é instalado:**

```
~/.hermes/
├── SOUL.md                           # Identidade do Exocórtex
├── skills/exocortex/                 # 15 skills
│   ├── exocortex-self-test/          # Core: auto-diagnóstico
│   ├── exocortex-prompt-log/         # Core: log de prompts
│   ├── stop-slop/                    # Quality: anti-slop textual
│   ├── taste-skill/                  # Quality: estética visual
│   ├── exocortex-design-system/      # Quality: tokens visuais
│   ├── acervo-manager/              # Memory: gerenciador do acervo
│   ├── exocortex-new-microverso/    # Memory: criação de microversos
│   ├── exocortex-draft-first/       # Behavior: protocolo draft-first
│   ├── exocortex-vetor-ativo/       # Behavior: classificador de vetores
│   ├── exocortex-canvas/            # Behavior: extrator cognitivo
│   ├── exocortex-briefing/          # Behavior: morning briefing
│   ├── exocortex-onboarding/        # Behavior: onboarding
│   ├── exocortex-output-quality-gate/ # Behavior: quality gate
│   ├── exocortex-tool-governance/   # Behavior: governança
│   └── browser-use/                 # External: automação de browser
├── acervo/                           # 4 camadas de memória
│   ├── macro/                        # Identidade, valores, estilo
│   ├── global/                       # Índice global, DESIGN.md
│   ├── micro/                        # Microversos por domínio
│   └── shared/                       # Cross-refs, glossário
├── profiles/                         # 2 profiles
│   ├── exec/                         # Vetor de Execução
│   └── evol/                         # Vetor de Evolução
└── skill-bundles/
    └── exocortex-alpha.yaml          # Bundle com todas as skills
```

---

### Modo Docker

> **Flag:** `--mode docker`

Executa o Exocórtex em um container Docker isolado. Ideal para:
- Testar sem alterar o sistema local
- Ambientes de servidor/produção
- Múltiplas instâncias simultâneas

**Fluxo:**

```
1. Preflight checks (docker disponível e rodando)
2. Build da imagem Docker (python:3.12-slim + Hermes)
3. Criação do container com volume persistente
4. Injeção de credenciais (env var e/ou mount de arquivo)
5. Provisioning da Golden Image dentro do container
6. Verificação estrutural
7. Execução do PDD (se --with-pdd ou AUTORUN=true)
```

**Exemplo:**

```bash
bash install-exocortex.sh \
  --mode docker \
  --api-key sk-or-v1-xxxxxxxxxxxx \
  --docker-data exocortex-data
```

**Opções Docker-específicas:**

| Parâmetro | Default | Descrição |
|-----------|---------|-----------|
| `--docker-image <name>` | `exocortex-provisioner:latest` | Nome da imagem Docker |
| `--docker-data <name>` | `exocortex-data` | Nome do volume persistente |
| `--docker-detach` | `false` | Rodar container em background |

**Credenciais no Docker:**

O container aceita credenciais de duas formas (ambas suportadas simultaneamente):

```bash
# Via env var (recomendado para automação)
bash install-exocortex.sh --mode docker --api-key sk-or-v1-xxx

# Via mount de arquivo (usa ~/.hermes/.env do host)
# Acontece automaticamente se ~/.hermes/.env existir e --api-key não for fornecido
```

**Acessando o container:**

```bash
# Chat interativo
docker exec -it exocortex-provisioner hermes chat

# Ativar profile
docker exec -it exocortex-provisioner hermes profile use exec

# Shell no container
docker exec -it exocortex-provisioner bash
```

**Docker Compose (alternativa):**

```bash
cd plans/pdd_v2/provisioner/docker

# Com variáveis de ambiente
OPENROUTER_API_KEY=sk-or-xxx docker compose up -d

# Verificar
docker exec exocortex-provisioner hermes chat -q "self-test"
```

---

## Referência de Parâmetros

### Modo de Instalação

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `--mode` | `local\|docker` | `local` | Modo de instalação |

### Credenciais

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `--provider` | string | auto-detect | Provider do LLM: `openrouter`, `anthropic`, `openai`, `nous` |
| `--api-key` | string | — | Chave de API. Provider auto-detectado pelo prefixo |
| `--skip-auth` | flag | `false` | Pular configuração de autenticação |

**Auto-detecção de provider pela chave:**

| Prefixo da chave | Provider detectado |
|-------------------|--------------------|
| `sk-or-...` | OpenRouter |
| `sk-ant-...` | Anthropic |
| `sk-...` | OpenAI |
| Outro | OpenRouter (fallback) |

### Controle de Fluxo

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `--with-pdd` | flag | `false` | Executar os 27 prompts PDD após golden image |
| `--phase` | `P1..P5` | — | Executar PDD apenas até esta fase (implica `--with-pdd`) |
| `--skip-install` | flag | `false` | Não instalar o Hermes (assume já instalado) |
| `--skip-golden-image` | flag | `false` | Não copiar golden image (apenas PDD) |

### Caminhos

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `--hermes-home` | path | `~/.hermes` | Diretório raiz do Hermes |
| `--repo-dir` | path | auto-detect | Path do repositório local |

### Comportamento

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `--non-interactive` | flag | `false` | Sem perguntas, usa defaults para tudo |
| `--verbose` | flag | `false` | Output detalhado com debug |
| `--dry-run` | flag | `false` | Mostra o que faria sem executar |
| `--force` | flag | `false` | Sobrescreve sem backup |
| `--no-color` | flag | `false` | Desabilita cores (para pipes/logs) |
| `--version` | flag | — | Mostra versão e sai |
| `--help` | flag | — | Mostra ajuda e sai |

### Exit Codes

| Código | Significado |
|--------|-------------|
| `0` | Sucesso |
| `1` | Erro geral |
| `2` | Pré-requisito faltando |
| `3` | Falha de autenticação |
| `4` | Falha no PDD |

---

## Credenciais LLM

O Exocórtex precisa de um LLM para funcionar. O instalador suporta múltiplos providers:

### OpenRouter (recomendado)

```bash
# Obtenha sua key em https://openrouter.ai/keys
bash install-exocortex.sh --api-key sk-or-v1-YOUR_KEY
```

### Anthropic

```bash
bash install-exocortex.sh --api-key sk-ant-YOUR_KEY
```

### OpenAI

```bash
bash install-exocortex.sh --api-key sk-YOUR_KEY --provider openai
```

### OAuth (interativo)

Se nenhuma `--api-key` for fornecida e `--non-interactive` não estiver ativo, o instalador oferece autenticação via OAuth:

```
How do you want to authenticate with the LLM?
  1. OpenAI / ChatGPT (OAuth — opens browser)
  2. Nous Research (OAuth — opens browser)
  3. API Key (OpenRouter, Anthropic, etc.)
  4. Skip — I'll configure later
```

### Configuração posterior

Se você pulou a autenticação durante a instalação:

```bash
# Adicionar credentials manualmente
echo "OPENROUTER_API_KEY=sk-or-xxx" >> ~/.hermes/.env

# Ou via Hermes CLI
hermes auth add openrouter --api-key sk-or-xxx
```

---

## PDD — Prompt-Driven Development

O PDD é um processo de 27 prompts conversacionais que configuram a **identidade e comportamento** do Exocórtex. É **opcional** — a golden image já instala todas as skills e artefatos estruturais.

### Quando usar

| Cenário | Recomendação |
|---------|--------------|
| Primeira instalação para uso pessoal | `--with-pdd` |
| Teste rápido / CI/CD | Sem PDD (default) |
| Reinstalação após update | `--skip-golden-image --with-pdd` |
| Debug de uma fase específica | `--with-pdd --phase P2` |

### Fases do PDD

| Fase | Prompts | Nome | Gate | Descrição |
|------|---------|------|------|-----------|
| P1 | 001–005 | Identity | self-test ≥ 2/5 | SOUL.md, quality skills |
| P2 | 006–012 | Memory | self-test ≥ 3/5 | Acervo 4 camadas |
| P3 | 013–021 | Behavior | self-test ≥ 4/5 | Skills de negócio |
| P4 | 022–026 | Validation | self-test = 5/5 | Smoke tests |
| P5 | 027 | Production | GRADUATION | Golden image final |

### Idempotência

O PDD é idempotente — re-executar é seguro. Cada fase concluída cria um arquivo `state/P{N}.done` que impede re-execução:

```bash
# Executar todas as fases
bash install-exocortex.sh --with-pdd

# Re-executar (fases já concluídas são puladas)
bash install-exocortex.sh --skip-install --skip-golden-image --with-pdd

# Forçar re-execução de uma fase
rm plans/pdd_v2/provisioner/state/P2.done
bash install-exocortex.sh --skip-install --skip-golden-image --with-pdd --phase P2
```

---

## Superfícies Operacionais

Para setup entregue a um executivo, o Exocórtex deve separar **interface principal do usuário** de **superfície de operação/administração**.

### Interface principal recomendada

- **Telegram + Hermes Gateway** como canal primário do executivo
- Fricção mínima: sem URL, sem login extra, sem navegação por abas
- O dashboard não substitui esse canal; ele complementa a operação

### Superfície operacional recomendada

- **Hermes Dashboard** como cockpit de administração
- **TUI embutida** habilitada para recuperação de sessão e operação técnica via browser
- Uso esperado: operador/configurador, não usuário final

### Habilitando dashboard com TUI

Pré-requisitos práticos:

```bash
# Dependências recomendadas pelo Hermes para dashboard + chat embutido
pip install 'hermes-agent[web,pty]'
```

Execução manual:

```bash
hermes dashboard --tui --no-open
```

Comportamento observado no setup atual:

- `--tui` expõe a aba `CHAT` dentro do dashboard
- o frontend web pode fazer build automático na primeira subida
- após o primeiro build, `--skip-build` reduz atrito em reinícios futuros

### Persistência via systemd user service

Em ambientes Linux com `systemd --user`, o dashboard pode ser persistido como serviço de sessão:

```ini
[Unit]
Description=Hermes Agent Dashboard with embedded TUI
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/home/USER/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main dashboard --tui --no-open --skip-build
WorkingDirectory=/home/USER/.hermes/hermes-agent
Environment="PATH=/home/USER/.hermes/hermes-agent/venv/bin:/usr/bin:/home/USER/.local/bin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="VIRTUAL_ENV=/home/USER/.hermes/hermes-agent/venv"
Environment="HERMES_HOME=/home/USER/.hermes"
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

Fluxo de ativação:

```bash
systemctl --user daemon-reload
systemctl --user enable --now hermes-dashboard.service
systemctl --user status hermes-dashboard.service
```

No ambiente de referência, o serviço ficou em:

```bash
~/.config/systemd/user/hermes-dashboard.service
```

### Segurança: nunca expor o dashboard bruto na internet

O dashboard concentra sessão, config, logs, skills e chaves do Hermes. Por isso:

- não publicar com `--host 0.0.0.0` como default
- não abrir a porta `9119` publicamente
- não colocar atrás de reverse proxy público sem camada forte de controle de acesso

Padrão recomendado para acesso remoto:

- manter o dashboard em `127.0.0.1:9119`
- acessar por **Tailscale** ou túnel SSH
- tratar Tailscale como requisito de segurança do setup, não opcional de conveniência

Exemplos:

```bash
# acesso local
http://127.0.0.1:9119

# túnel SSH temporário
ssh -L 9119:127.0.0.1:9119 user@host

# com Tailscale, expor apenas na rede privada tailnet
# preferir ACLs e device approval para limitar quem vê o serviço
```

Resumo operacional:

- executivo usa Telegram
- operador usa dashboard
- dashboard fica privado
- acesso remoto passa por Tailscale

---

## Exemplos de Uso

### 1. Instalação mínima local

```bash
curl -fsSL https://raw.githubusercontent.com/elderbernardi/exocortex.saas/main/install-exocortex.sh | bash
```

### 2. Instalação remota via SSH

```bash
ssh user@server 'curl -fsSL https://raw.githubusercontent.com/elderbernardi/exocortex.saas/main/install-exocortex.sh | bash -s -- --api-key sk-or-xxx --non-interactive'
```

### 3. Docker com tudo automático

```bash
bash install-exocortex.sh \
  --mode docker \
  --api-key sk-or-v1-xxxxxxxxxxxx \
  --docker-detach \
  --non-interactive
```

### 4. PDD completo

```bash
bash install-exocortex.sh \
  --with-pdd \
  --api-key sk-or-v1-xxxxxxxxxxxx \
  --non-interactive
```

### 5. Apenas PDD (Hermes e golden image já instalados)

```bash
bash install-exocortex.sh \
  --skip-install \
  --skip-golden-image \
  --with-pdd
```

### 6. PDD até fase específica

```bash
bash install-exocortex.sh --with-pdd --phase P2 --api-key sk-or-xxx
```

### 7. Dry run (ver sem executar)

```bash
bash install-exocortex.sh --dry-run --verbose --non-interactive
```

### 8. HERMES_HOME customizado

```bash
bash install-exocortex.sh --hermes-home /opt/exocortex --api-key sk-or-xxx
```

### 9. Docker com volume customizado

```bash
bash install-exocortex.sh \
  --mode docker \
  --docker-data /mnt/data/exocortex \
  --docker-image my-exocortex:v3
```

### 10. Pipeline CI/CD

```yaml
# GitHub Actions
- name: Install Exocórtex
  run: |
    curl -fsSL https://raw.githubusercontent.com/elderbernardi/exocortex.saas/main/install-exocortex.sh \
      | bash -s -- --non-interactive --skip-auth --no-color
```

### 11. Persistir dashboard com TUI para operação

```bash
# subir uma vez para gerar o build web, se necessário
hermes dashboard --tui --no-open

# criar o serviço user systemd
systemctl --user daemon-reload
systemctl --user enable --now hermes-dashboard.service

# validar
systemctl --user status hermes-dashboard.service
curl http://127.0.0.1:9119/
```

### 12. Acesso remoto seguro ao dashboard

```bash
# opção 1: túnel SSH
ssh -L 9119:127.0.0.1:9119 user@host

# opção 2: Tailscale
# manter o dashboard bindado em localhost e publicar o host apenas na tailnet
```

---

## Verificação

### Pós-instalação

```bash
# Verificar skills instaladas
ls ~/.hermes/skills/exocortex/
# Deve listar 15 diretórios

# Verificar acervo
ls ~/.hermes/acervo/
# macro/ global/ micro/ shared/

# Verificar estrutura completa
bash plans/pdd_v2/provisioner/lib/verify.sh --post-provision
# Deve reportar "All 13 checks passed ✅"

# Verificar drift
bash plans/pdd_v2/provisioner/lib/drift_audit.sh ALL
```

### Chat de teste

```bash
hermes chat -q "Execute o self-test do Exocórtex."
```

### Usar profiles

```bash
hermes profile use exec    # Modo execução (foco em ação)
hermes profile use evol    # Modo exploração (foco em reflexão)
```

### Dashboard operacional

```bash
systemctl --user status hermes-dashboard.service
curl http://127.0.0.1:9119/
```

Checklist esperado:
- serviço `hermes-dashboard.service` em `active (running)`
- dashboard respondendo em `127.0.0.1:9119`
- aba `CHAT` visível quando iniciado com `--tui`
- acesso remoto somente por Tailscale ou túnel SSH

---

## Troubleshooting

### "hermes: command not found" após instalação

```bash
# Verificar se está no PATH
which hermes

# Se instalado via pip/pipx, pode estar em ~/.local/bin
export PATH="$HOME/.local/bin:$PATH"

# Adicionar permanentemente
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### "Python 3 not found"

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip

# macOS
brew install python3

# Verificar
python3 --version  # Deve ser 3.11+
```

### "Docker daemon not running"

```bash
# Verificar status
sudo systemctl status docker

# Iniciar
sudo systemctl start docker

# Adicionar seu usuário ao grupo docker (evita sudo)
sudo usermod -aG docker $USER
# Faça logout e login novamente
```

### "Artifacts directory incomplete"

O repositório pode estar incompleto. Clone novamente:

```bash
git clone https://github.com/elderbernardi/exocortex.saas.git
cd exocortex.saas
bash install-exocortex.sh
```

### Golden image sem skills (0 skills instaladas)

```bash
# Verificar se artifacts existem
ls plans/pdd_v2/artifacts/skills/
# Deve listar 15 diretórios

# Re-aplicar manualmente
bash plans/pdd_v2/artifacts/setup.sh
```

### PDD falha em uma fase

```bash
# Verificar qual fase falhou
ls plans/pdd_v2/provisioner/state/

# Re-executar apenas a fase faltante
rm plans/pdd_v2/provisioner/state/P3.done  # Exemplo: P3 falhou
bash install-exocortex.sh --skip-install --skip-golden-image --with-pdd --phase P3
```

### Container Docker não inicia

```bash
# Ver logs
docker logs exocortex-provisioner

# Remover e recriar
docker rm -f exocortex-provisioner
bash install-exocortex.sh --mode docker --api-key sk-or-xxx
```

### Dashboard acessível demais na rede

Se o dashboard estiver escutando fora de `127.0.0.1`, trate como incidente de configuração.

```bash
# verificar serviço
systemctl --user cat hermes-dashboard.service

# o ExecStart deve manter --no-open e não deve usar --insecure por padrão
# o host esperado é localhost

# reiniciar após correção
systemctl --user daemon-reload
systemctl --user restart hermes-dashboard.service
```

Se houver necessidade de acesso remoto contínuo, use Tailscale. Não substitua esse controle por exposição direta da porta 9119.

---

## Desinstalação

### Local

```bash
# Remover skills do Exocórtex (mantém Hermes intacto)
rm -rf ~/.hermes/skills/exocortex
rm -rf ~/.hermes/acervo
rm -rf ~/.hermes/profiles
rm -rf ~/.hermes/skill-bundles/exocortex-alpha.yaml
rm -f ~/.hermes/SOUL.md

# Remover Hermes completamente
pip uninstall hermes-agent
rm -rf ~/.hermes
```

### Docker

```bash
# Parar e remover container
docker rm -f exocortex-provisioner

# Remover volume (dados persistentes)
docker volume rm exocortex-data

# Remover imagem
docker rmi exocortex-provisioner:latest
```
