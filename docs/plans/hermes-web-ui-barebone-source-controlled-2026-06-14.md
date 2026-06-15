# Plano local — Hermes Web UI barebone por usuário Unix e fontes controladas

Data: 2026-06-14
Status: em progresso local
Repositório: elderbernardi/exocortex.saas
Âncora local: docs/plans/hermes-web-ui-barebone-source-controlled-2026-06-14.md
Substitui conceitualmente: docs/plans/hermes-web-ui-private-ops-hardening-2026-06-14.md
Issues existentes relacionadas: #68, #69, #70, #71, #72, #73, #74

## 1. Decisão arquitetural revisada

O setup alvo da Hermes Web UI muda de “compute em Docker + dados no host” para “barebone por usuário Unix”.

A unidade de operação passa a ser:

```text
uma instância Exocórtex/Hermes = um usuário Unix + um plano de execução + várias superfícies
```

Superfícies da mesma instância:

- Telegram Gateway;
- Hermes CLI/TUI;
- Hermes Web UI;
- cron/automações;
- scripts operacionais.

Todas devem enxergar o mesmo `PATH`, o mesmo runtime, os mesmos binários, os mesmos arquivos e os mesmos ambientes da instância.

## 2. Motivo da inversão

A arquitetura Docker-first criava risco de drift entre superfícies:

- a Web UI via container poderia enxergar ferramentas instaladas dentro do container;
- o Telegram Gateway rodando fora do container poderia não enxergar essas ferramentas;
- a CLI poderia ter um terceiro plano de execução.

Esse split-brain quebra a promessa operacional do Exocórtex: o usuário deve poder acionar a mesma capacidade por Telegram, Web UI ou CLI.

Barebone por usuário Unix resolve isso melhor:

- uma instância tem um único plano de execução;
- instalações aprovadas ficam disponíveis para todas as superfícies;
- ownership de arquivos fica coerente;
- backup captura a instância inteira;
- systemd user services ficam naturais;
- multi-instância futura usa usuários Unix separados.

## 3. Decisão sobre Docker

Docker sai do caminho crítico da instância principal.

Docker continua útil para:

- serviços auxiliares;
- bancos e memória operacional;
- sandboxes;
- testes;
- builds reprodutíveis;
- imagem futura consolidada quando a arquitetura estiver madura.

Não usar Docker como plano principal agora evita incoerência entre Telegram/Web UI/CLI. A imagem Docker futura deve ser resultado de uma instalação madura, não o primeiro contrato operacional.

## 4. Estratégia de fontes controladas

A instalação não deve depender de upstreams flutuantes.

Repos relevantes devem ser controlados por nós, via fork ou mirror:

- Hermes Agent: upstream `NousResearch/hermes-agent`, licença detectada via GitHub API: MIT.
- Hermes Web UI / Hermes Studio: upstream `EKKOLearnAI/hermes-web-ui`, redirecionando para `EKKOLearnAI/hermes-studio`; licença detectada no LICENSE remoto: Business Source License 1.1, com Change Date 2029-05-10 e Change License Apache-2.0.

## 5. Alerta de licença

A premissa “licença compatível” precisa ser corrigida.

Hermes Agent está em MIT, compatível com fork, mirror e uso amplo.

Hermes Web UI / Hermes Studio não está em MIT/Apache hoje. O arquivo LICENSE remoto declara Business Source License 1.1, com uso não-comercial permitido e uso comercial/SaaS exigindo licença comercial separada até a Change Date 2029-05-10.

Implicação:

- podemos estudar, testar e usar em contexto pessoal/não-comercial conforme a licença;
- podemos controlar versão para evitar quebra, desde que respeitemos os termos da BSL;
- não devemos tratar a Web UI como componente SaaS comercial do Exocórtex sem revisar licença ou obter autorização comercial;
- se a ambição for produto comercial antes de 2029-05-10, precisamos de decisão jurídica/comercial ou alternativa técnica.

Esta observação deve entrar nas issues e no runbook. Agentes não devem apagar este alerta.

## 6. Modelo alvo de diretórios

Cada instância terá usuário Unix próprio.

Exemplo:

```text
usuário: exo-alpha
raiz: /srv/exocortex/instances/alpha
```

Layout:

```text
/srv/exocortex/instances/<slug>/
  hermes/              # HERMES_HOME
  exocortex/           # EXOCORTEX_HOME / acervo / artefatos
  webui/               # estado da Web UI: DB, config, uploads, cache
  runtime/
    bin/               # wrappers e CLIs da instância
    node/              # Node pinado ou gerenciado
    python/            # Python/venv/uv da instância, se aplicável
    venvs/             # ambientes Python auxiliares
  src/
    hermes-agent/      # checkout controlado do Hermes
    hermes-web-ui/     # checkout controlado da Web UI
  env/
    instance.env       # variáveis da instância
    secrets.env        # segredos com permissão restrita
  logs/
    webui/
    gateway/
    setup/
  backups/
  receipts/
```

## 7. Modelo de serviços

Usar systemd user services por usuário de instância.

Serviços sugeridos:

```text
exocortex-webui.service
exocortex-gateway.service
exocortex-cron.service
exocortex-instance.target
```

O target agrupa os serviços da instância.

Comandos esperados para Ops:

```bash
sudo -iu exo-alpha systemctl --user status exocortex-instance.target
sudo -iu exo-alpha systemctl --user start exocortex-webui.service
sudo -iu exo-alpha systemctl --user restart exocortex-gateway.service
sudo -iu exo-alpha journalctl --user -u exocortex-webui.service -f
```

Ops pode habilitar linger quando necessário:

```bash
sudo loginctl enable-linger exo-alpha
```

## 8. Acesso privado

A Web UI continua privada.

Modos aceitos:

- `127.0.0.1` para acesso local;
- IP Tailscale para acesso remoto privado;
- exposição pública direta fora de escopo.

Se houver necessidade futura de exposição pública, criar plano separado de segurança, autenticação, reverse proxy, rate limit, TLS, auditoria e política de tenant.

## 9. Instalações e capacidades

A Web UI não instala “programas para si”. Telegram também não.

O usuário solicita uma capacidade. O Exocórtex classifica a capacidade:

### Classe A — Dependência da instância

Exemplos:

- pandoc;
- ffmpeg;
- ripgrep;
- playwright;
- docbrain;
- nlm;
- browser automation;
- CLIs auxiliares.

Regra:

- instalar via provisionador da instância;
- registrar no plano/setup;
- validar com smoke;
- tornar disponível para Telegram, Web UI e CLI.

### Classe B — Dependência efêmera de debug

Regra:

- pode ser testada localmente;
- não conta como estado final;
- se virar requisito, promover para Classe A.

### Classe C — Dependência do host

Exemplos:

- Tailscale;
- systemd;
- drivers;
- pacotes do SO;
- agentes de backup/storage;
- firewall.

Regra:

- responsabilidade de Ops;
- documentar em runbook;
- não instalar automaticamente pela Web UI ou Telegram.

## 10. Estratégia de forks/mirrors

Criar camada de fontes controladas para evitar que upstream quebre o setup.

### Repos candidatos

1. `elderbernardi/hermes-agent` ou organização futura equivalente
   - origem: `NousResearch/hermes-agent`
   - licença: MIT
   - uso: runtime base controlado do Exocórtex

2. `elderbernardi/hermes-web-ui` ou organização futura equivalente
   - origem: `EKKOLearnAI/hermes-web-ui` / `EKKOLearnAI/hermes-studio`
   - licença atual observada: BSL 1.1
   - uso: cockpit privado não-comercial, salvo licença comercial

### Política de atualização

- nunca consumir `main` upstream diretamente no setup;
- usar tag, commit ou branch controlada por nós;
- manter arquivo de proveniência;
- registrar upstream remote;
- rodar smoke antes de promover nova versão;
- documentar divergências locais;
- automatizar checagem de upstream sem auto-merge.

### Estrutura sugerida no repositório Exocórtex

```text
provision/sources/
  sources.lock.yaml
  README.md
  sync-upstreams.sh
```

`sources.lock.yaml` deve declarar:

```yaml
sources:
  hermes-agent:
    upstream: https://github.com/NousResearch/hermes-agent.git
    controlled: https://github.com/elderbernardi/hermes-agent.git
    ref: <commit-ou-tag-controlado>
    license: MIT
  hermes-web-ui:
    upstream: https://github.com/EKKOLearnAI/hermes-web-ui.git
    controlled: https://github.com/elderbernardi/hermes-web-ui.git
    ref: <commit-ou-tag-controlado>
    license: BSL-1.1
    commercial_use_requires_license: true
```

## 11. Novo grafo de issues recomendado

As issues #68 a #74 foram publicadas com a arquitetura Docker-híbrida. Elas precisam ser reorientadas ou complementadas.

Recomendação: não apagar as issues. Registrar a decisão de arquitetura e criar issues novas de transição.

### Nova issue P0 sugerida

Título:

```text
[P0] Hermes Web UI: inverter arquitetura para barebone por usuário Unix
```

Objetivo:

- substituir o alvo Docker-híbrido por barebone por usuário Unix;
- declarar plano de execução único entre Telegram, Web UI e CLI;
- revisar #68 a #74;
- definir quais partes Docker permanecem como auxiliares ou futuro empacotamento.

### Nova issue P0 sugerida

Título:

```text
[P0] Exocórtex: controlar fontes Hermes/Web UI por fork ou mirror pinado
```

Objetivo:

- mapear forks/mirrors necessários;
- registrar licenças;
- criar `sources.lock.yaml`;
- impedir consumo direto de upstream flutuante;
- definir workflow de atualização.

### Nova issue P0 sugerida

Título:

```text
[P0] Hermes Web UI: validar instalação barebone em usuário Unix dedicado
```

Objetivo:

- testar instalação real da Web UI fora de Docker;
- rodar gateway Telegram e Web UI no mesmo usuário;
- provar que uma ferramenta instalada na instância funciona nas três superfícies: CLI, Web UI e Telegram/Gateway.

### Nova issue P1 sugerida

Título:

```text
[P1] Hermes Web UI: criar systemd user services para instância barebone
```

Objetivo:

- criar serviços user-level para Web UI, Gateway e cron;
- criar target da instância;
- documentar start/stop/status/logs.

### Nova issue P1 sugerida

Título:

```text
[P1] Exocórtex Ops: atualizar runbook para arquitetura barebone e fontes controladas
```

Objetivo:

- documentar usuário Unix por instância;
- documentar fontes controladas;
- documentar licença da Web UI;
- documentar backup/restore da instância inteira.

## 12. Ajuste das issues existentes

Proposta de reinterpretação:

- #68 deixa de ser “Docker-híbrido como alvo” e vira histórico da primeira hipótese.
- #69 deve ser reorientada para INSTANCE_SLUG + layout barebone.
- #70 continua válida: private-only via Tailscale.
- #71 continua válida: backup/restore por instância, agora sem compose como eixo principal.
- #72 muda de Docker compose systemd para systemd user services barebone.
- #73 continua válida, mas deve documentar barebone.
- #74 deixa de ser P2 relevante para a instância principal; vira pesquisa para imagem futura consolidada.

## 13. Critérios de aceite globais

A arquitetura barebone estará validada quando:

- houver usuário Unix dedicado para uma instância de teste;
- Hermes CLI funcionar nesse usuário;
- Web UI funcionar nesse usuário;
- Gateway Telegram funcionar nesse usuário ou tiver smoke equivalente;
- as três superfícies compartilharem o mesmo `PATH` e o mesmo runtime;
- uma ferramenta instalada via provisionador da instância funcionar por CLI e Web UI;
- backup capturar `hermes/`, `exocortex/`, `webui/`, `runtime/`, `src/`, `env/`, `logs/` e `receipts/`;
- restore em nova raiz passar smoke;
- fontes controladas forem usadas em vez de upstream direto;
- alerta de licença da Web UI estiver documentado.

## 14. Riscos

### Risco 1 — Licença da Web UI

A BSL 1.1 limita uso comercial antes da Change Date. O projeto deve tratar a Web UI como cockpit privado não-comercial ou obter licença comercial.

### Risco 2 — Drift de host

Barebone depende mais do host. Mitigação:

- pinagem de Node;
- lockfiles;
- sources.lock;
- scripts idempotentes;
- smoke pós-instalação;
- runbook de Ops.

### Risco 3 — Instalação ad hoc

Sem política, usuários podem instalar ferramentas manualmente e quebrar reprodutibilidade. Mitigação:

- classificar dependências em A/B/C;
- promover dependências persistentes para provisionador;
- registrar receipts.

### Risco 4 — Superfície operacional ampla

A Web UI continua sendo cockpit poderoso. Mitigação:

- Tailscale/private-only;
- usuário Unix por instância;
- permissões restritas;
- logs;
- backups;
- Draft-First para ações externas.

## 15. Progresso local registrado nesta sessão

Arquivos criados para a política de fontes controladas:

- `provision/sources/README.md`
- `provision/sources/sources.lock.yaml`
- `provision/sources/sync-upstreams.sh`
- `tests/test_sources_controlled.py`

Arquivos conectados à política:

- `provision/hermes-web-ui/scripts/common.sh`
- `provision/hermes-web-ui/env/.env.example`
- `provision/hermes-web-ui/README.md`
- `README.md`

Escopo entregue localmente:

- registro explícito do upstream oficial `NousResearch/hermes-agent` com licença `MIT`;
- pin auditado do Hermes Agent em `f3fe99863d134bd05316882dee0d469439110ca6`;
- registro explícito do upstream `EKKOLearnAI/hermes-web-ui` com redirecionamento observado para `EKKOLearnAI/hermes-studio`;
- pin auditado da Web UI/Studio em `f3365ce664006076acde7323398c2a06593ad630`;
- preservação do alerta de licença `BSL 1.1`, `Change Date 2029-05-10`, `Change License Apache-2.0` e `commercial_use_requires_license: true`;
- lock local com política que proíbe consumo de `main`/`master`/`HEAD` upstream como produção;
- `sync-upstreams.sh` em `dry-run` por default;
- script exigindo flags explícitas para qualquer `clone` ou `fetch` local;
- validação de `controlled.ref` como commit SHA completo de 40 caracteres;
- ausência deliberada de `push`, `merge`, `rebase`, criação de PR ou mutação remota;
- provisionador da Web UI resolve repo/ref via `sources.lock.yaml` quando o env deixa `EXOCORTEX_HERMES_WEB_UI_REPO_URL` e `EXOCORTEX_HERMES_WEB_UI_REF` em branco;
- testes automatizados cobrindo lock, dry-run e resolução do env.

Limites desta fatia:

- os mirrors/forks remotos controlados ainda não foram criados;
- o provisionador Docker legado continua existindo como trilha operacional de transição;
- a instalação barebone real por usuário Unix ainda não foi implementada;
- ainda não há smoke sobre worktrees clonados em runtime barebone.

## 16. Próxima sequência recomendada

1. Criar mirrors/forks remotos controlados para `hermes-agent` e Web UI/Studio, após decisão explícita.
2. Atualizar `sources.lock.yaml` trocando `pending-controlled-mirror/*` pelos repos controlados reais.
3. Rodar `sync-upstreams.sh --apply --clone-missing --fetch-existing` em workspace local controlado.
4. Rodar smoke local sobre worktrees pinadas.
5. Implementar instalação barebone real por usuário Unix.

GitHub e criação de repos remotos são ações externas. Não executar sem aprovação explícita.
