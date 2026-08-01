# Exocórtex.IA — Runbook de Instalação v2

Este runbook instala o harness Exocórtex sobre um Hermes Agent já instalado e
configurado. O instalador não instala Hermes, não altera o gerenciador de pacotes
do sistema e não usa o catálogo completo de dogfood como validação do usuário.

## Contrato

Pré-condições obrigatórias:

- `core`: Hermes configurado, Python >= 3.11, Git, rsync e Bash;
- `full`: capacidades do `core`, Docker/Compose v2, curl, Node/npm,
  NotebookLM CLI/MCP e Firecrawl MCP.

O contrato canônico está em `setup/capabilities.json`. Ele declara capacidades,
não nomes universais de pacotes. `scripts/check_capabilities.py` detecta o SO,
resolve `apt`, `dnf`, `pacman` ou `brew`, verifica binários/versões/probes e
apresenta uma receita nativa quando algo falta. Nenhum comando de instalação é
executado pelo checker.

```bash
python3 scripts/check_capabilities.py --profile core
python3 scripts/check_capabilities.py --profile full --json
```

Paths default:

```bash
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
EXOCORTEX_HOME="${EXOCORTEX_HOME:-$HOME/exocortex}"
ACERVO="${ACERVO:-$EXOCORTEX_HOME/acervo}"
```

O instalador usa o provider e o modelo já configurados no Hermes. `--model` só
sobrescreve o modelo usado pelos três cenários de aceitação comportamental.

## Profiles

| Profile | Conteúdo | Política de falha |
|---|---|---|
| `core` | identidade, regras compiladas, skills essenciais, Acervo, memória, profiles, bundle e Acervo MCP | qualquer falha bloqueia |
| `full` | tudo do `core` + NotebookLM, Hindsight, Firecrawl e Hermes WebUI | ferramentas de usuário e serviços são verificados antes do apply |

Para aceitar um `full` parcial de forma consciente, use
`--allow-degraded-services`. Somente capacidades marcadas como degradáveis mudam
de `fail` para `warn`. NotebookLM permanece obrigatório no `full`.

## Camadas de dependência

| Camada | Exemplos | Verificação | Responsável pela instalação |
|---|---|---|---|
| `runtime` | Hermes | comando + probe funcional | operador, antes do Exocórtex |
| `system` | Python, Git, rsync, Bash, Node/npm | `PATH`, versão e proprietário pelo gerenciador nativo | SO/operador |
| `service` | Docker/Compose, curl | comando + probe; degradável somente por opção explícita | SO/operador |
| `user-tool` | `nlm`, `notebooklm-mcp`, `firecrawl-mcp` | comando + versão quando aplicável | operador via `uv tool` ou `npm` |

Receitas emitidas pelo preflight incluem, conforme o SO:

```bash
sudo apt-get install <pacote>
sudo dnf install <pacote>
sudo pacman -S --needed <pacote>
brew install <pacote>
uv tool install notebooklm-mcp-cli
npm install --global firecrawl-mcp@3.22.0
```

Essas receitas são diagnóstico. O instalador não as executa.

## Fluxo recomendado

### 1. Validar Hermes

```bash
hermes --version
hermes config check
python3 scripts/check_capabilities.py --profile full
```

### 2. Inspecionar o plano

De um checkout local:

```bash
python3 scripts/exocortex_install.py plan --profile full
```

Via bootstrap remoto:

```bash
curl -fsSL https://raw.githubusercontent.com/elderbernardi/exocortex.saas/main/install.sh \
  | bash -s -- --plan --profile full
```

`plan` é read-only em relação ao runtime. O bootstrap remoto ainda atualiza seu
checkout gerenciado antes de imprimir os estágios, a criticidade e o preflight.

### 3. Aplicar

```bash
# Interativo, uma confirmação antes do apply
python3 scripts/exocortex_install.py apply --profile full

# Revisão estágio a estágio
python3 scripts/exocortex_install.py apply --profile full --review-each

# Headless
python3 scripts/exocortex_install.py apply --profile full --yes
```

O wrapper compatível continua disponível:

```bash
bash setup.sh --profile full
bash setup.sh --profile core --yes
```

### 4. Verificar

```bash
python3 scripts/exocortex_install.py verify --profile full
python3 scripts/verify_exocortex_behavior.py
```

## Estágios do apply

1. **Preflight read-only** — manifesto de capacidades, SO, versões, probes e receitas de correção.
2. **Lock** — impede dois applies simultâneos no mesmo `HERMES_HOME`.
3. **Snapshot gerenciado** — preserva SOUL, skills Exocórtex, profiles e bundle.
4. **Estrutura** — cria somente diretórios gerenciados.
5. **Skills** — sincroniza o pacote Exocórtex sem remover runtimes locais.
6. **Acervo** — semeia com política de preservação dos domínios vivos.
7. **Identidade** — instala o seed em Hermes genérico; preserva onboarding existente.
8. **SOUL compilado** — recompila regras comportamentais sem reescrever o Macroverso.
9. **Memória** — provisiona roteamento Acervo + memória operacional.
10. **Acervo MCP** — registra e testa o control plane semântico.
11. **NotebookLM** (`full`) — registra e testa CLI/MCP já disponíveis; não instala pacotes.
12. **Serviços** (`full`) — Hindsight, Firecrawl local + adapter MCP e WebUI.
13. **Verificação determinística** — repete capacidades, autenticação, MCPs e contrato instalado.
14. **Aceitação viva** — três turnos reais: identidade, Evolução e Draft-First.

## Dogfood: por que só três cenários

O catálogo EX completo valida a release do harness. Reexecutá-lo durante cada
instalação repete trabalho já feito, aumenta latência, consome tokens e mistura
defeitos de produto com defeitos do ambiente do usuário.

A instalação usa três cenários com alto poder de detecção:

1. **Identidade** — deve responder “Exocórtex.IA rodando sobre o Hermes Agent”.
2. **Evolução** — deve abrir perguntas antes de concluir.
3. **Draft-First** — uma ação externa deve resultar em DRAFT, não envio.

Isso é aceitação de conformidade, não treinamento de modelo. O comportamento
persistente vem do `SOUL.md`, das regras compiladas das skills, dos profiles e do
Acervo. O teste não injeta “correções” em sessões efêmeras nem usa um segundo LLM
como juiz.

Para pular explicitamente o custo dos três turnos:

```bash
python3 scripts/exocortex_install.py apply --profile core --acceptance skip
# equivalente no wrapper:
bash setup.sh --profile core --skip-acceptance
```

## Onboarding

O seed já define a identidade operacional do Exocórtex e sua relação com Hermes.
Antes do onboarding, os campos pessoais do Macroverso ficam marcados como
pendentes. Depois do onboarding, reaplicar o instalador preserva esses campos e
atualiza apenas o bloco compilado.

Verificação rápida:

```bash
grep -q "Você é o Exocórtex.IA" "$HERMES_HOME/SOUL.md"
grep -q "COMPILED_RULES_START" "$HERMES_HOME/SOUL.md"
```

## Estado, logs e rollback

Cada execução cria:

```text
$HERMES_HOME/exocortex-install/
  install.lock
  latest.json
  runs/<timestamp>/
    install-state.json
    pre-install-managed-files.tar.gz
    verification.json
    behavior-acceptance.json
    behavior-acceptance.log
    logs/<stage>.log
```

`latest.json` é atualizado por rename atômico. Segredos conhecidos são removidos
dos logs antes da persistência.

Rollback dos arquivos gerenciados:

```bash
RUN="$HERMES_HOME/exocortex-install/runs/<timestamp>"
tar -xzf "$RUN/pre-install-managed-files.tar.gz" -C "$HERMES_HOME"
```

O snapshot não inclui credenciais, sessões nem o Acervo vivo.

## Exit codes

| Exit | Significado |
|---|---|
| `0` | contrato verificado |
| `1` | estágio crítico ou verificação falhou |
| `2` | preflight falhou ou argumentos inválidos |
| `3` | lock ocupado ou bootstrap remoto falhou |
| `130` | cancelado antes do apply |

## Compatibilidade de interface

`setup.sh` preserva os nomes `--yes`, `--step-by-step`, `--init-only` e
`--calibrate`. A semântica converge para `apply`, `--review-each`, `plan` e a
aceitação mínima, respectivamente. Flags que instalavam dependências ou alteravam
roteamento de provider foram removidas: essas responsabilidades pertencem ao
Hermes e à administração do sistema, não ao instalador do harness.