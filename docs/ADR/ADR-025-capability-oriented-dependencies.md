# ADR-025 — Dependências orientadas a capacidades verificáveis

- **Status:** Accepted
- **Data:** 2026-07-30
- **Decisores:** Exocórtex.IA / executivo
- **Relacionada:** ADR-024 — Instalador v2 sobre Hermes pré-existente

## Contexto

O instalador v2 não administra o sistema operacional. Ainda assim, precisa declarar com precisão o que cada profile exige, reconhecer ferramentas instaladas por meios diferentes e produzir uma correção compatível com a distribuição quando uma capacidade estiver ausente.

Nomes de pacotes não formam um contrato portátil: Python é `python3` em Debian/Fedora e `python` em Arch; Docker e Compose também variam. O requisito real é a capacidade executável e, quando aplicável, sua versão ou probe funcional.

## Decisão

`setup/capabilities.json` é a fonte canônica das dependências do instalador.

Cada capacidade declara:

- identificador estável e descrição;
- profiles que a exigem;
- camada: `runtime`, `system`, `service` ou `user-tool`;
- comandos e probes funcionais;
- versão mínima quando necessária;
- mapeamentos de pacotes por gerenciador;
- receita explícita para ferramentas de usuário;
- se a ausência pode degradar com `--allow-degraded-services`.

`scripts/check_capabilities.py`:

1. detecta o SO por `/etc/os-release` ou Darwin;
2. resolve a família e o gerenciador (`apt`, `dnf`, `pacman`, `brew`);
3. verifica comandos, versões e probes sem instalar nada;
4. consulta, quando possível, o proprietário do binário pelo gerenciador nativo;
5. emite relatório humano ou JSON e uma receita acionável para cada falha.

O mesmo checker é chamado por `plan`, pelo gate anterior ao `apply` e por `verify`. Nenhum desses caminhos chama um gerenciador de pacotes.

Ferramentas como NotebookLM e Firecrawl MCP pertencem à camada `user-tool`. O instalador registra e testa suas integrações, mas a instalação permanece uma ação explícita do operador (`uv tool install ...` ou `npm install --global ...`).

## Profiles

- `core`: Hermes configurado, Python, Git, rsync e Bash.
- `full`: `core` + Docker/Compose, curl, Node/npm, NotebookLM CLI/MCP e Firecrawl MCP.

Somente capacidades marcadas como degradáveis mudam de `fail` para `warn` com `--allow-degraded-services`. NotebookLM continua obrigatório no `full`; serviços locais e o adapter Firecrawl podem degradar de forma explícita.

## Consequências

### Positivas

- contrato portátil entre distribuições;
- diagnóstico antes de qualquer mutação;
- proveniência distinguindo pacote do SO de runtime externo ou ferramenta do usuário;
- uma única fonte para `plan`, `apply`, `verify` e documentação;
- ausência de instalação silenciosa ou elevação de privilégio.

### Custos

- novos requisitos precisam ser adicionados ao manifesto e cobertos por teste;
- a proveniência é best-effort para runtimes gerenciados por mise, uv, npm ou ferramentas equivalentes;
- autenticação e saúde de serviços continuam sendo verificações funcionais posteriores, não capacidades do SO.

## Verificação

```bash
python3 scripts/check_capabilities.py --profile core
python3 scripts/check_capabilities.py --profile full --json
python3 -m pytest tests/test_installer_capabilities.py -q
```
