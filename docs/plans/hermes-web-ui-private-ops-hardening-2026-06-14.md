# Plano local — Hermes Web UI privada, instâncias isoladas e operação por Ops

Data: 2026-06-14
Status: superado por decisão arquitetural posterior; issues #68 a #74 fechadas como not planned/deprecated em 2026-06-14
Repositório: elderbernardi/exocortex.saas
Âncora local: docs/plans/hermes-web-ui-private-ops-hardening-2026-06-14.md
Plano sucessor: docs/plans/hermes-web-ui-barebone-source-controlled-2026-06-14.md
Escopo original: provision/hermes-web-ui, setup.sh, documentação operacional e scripts de backup/restore

> Nota de continuidade: este plano registrou a hipótese Docker-híbrida. A decisão posterior inverteu a arquitetura para barebone por usuário Unix, preservando Docker apenas para componentes auxiliares e futura imagem consolidada. Use o plano sucessor como referência canônica.

## 1. Decisão arquitetural registrada

O setup do Exocórtex com Hermes Web UI seguirá o modelo híbrido:

- compute da Web UI em Docker;
- dados persistidos no host;
- arquivos do Exocórtex/Hermes acessíveis no host;
- acesso privado via Tailscale;
- sem exposição pública direta;
- futuras múltiplas instâncias isoladas por usuário Unix;
- operação multi-instância futura sob responsabilidade de Ops externa.

Esta decisão rejeita o modelo “tudo escondido em Docker”. O container executa o processo; o host mantém a verdade do estado.

## 2. Objetivo do plano

Transformar o provisionador atual da Hermes Web UI em uma trilha operacional clara, privada, auditável e preparada para múltiplas instâncias futuras sem perder acesso humano aos arquivos.

O plano deve servir para:

- orientar agentes que implementarem as mudanças;
- preservar progresso entre sessões;
- ancorar issues do GitHub;
- permitir rastreio posterior de execução;
- reduzir ambiguidade para agentes menores.

## 3. Estado atual observado

Arquivos já existentes:

- provision/hermes-web-ui/docker/Dockerfile.ui
- provision/hermes-web-ui/docker/compose.yml
- provision/hermes-web-ui/env/.env.example
- provision/hermes-web-ui/scripts/common.sh
- provision/hermes-web-ui/scripts/install.sh
- provision/hermes-web-ui/scripts/bootstrap-admin.sh
- provision/hermes-web-ui/scripts/bootstrap-profiles.sh
- provision/hermes-web-ui/scripts/bootstrap-exocortex.sh
- provision/hermes-web-ui/scripts/smoke.sh
- provision/hermes-web-ui/scripts/backup.sh
- provision/hermes-web-ui/scripts/restore.sh
- provision/hermes-web-ui/systemd/exocortex-hermes-ui.service
- provision/hermes-web-ui/README.md
- setup/step-10b-hermes-web-ui.sh

Comportamento atual:

- a Web UI só provisiona se EXOCORTEX_ENABLE_HERMES_WEB_UI=1;
- a imagem usa upstream EKKOLearnAI/hermes-web-ui pinado em v0.6.14;
- refs flutuantes main/master/HEAD são bloqueadas sem override;
- bind default é 127.0.0.1;
- tailscale-auto resolve IP da tailnet;
- CORS_ORIGINS é obrigatório fora de loopback;
- admin e AUTH_JWT_SECRET são gerados se ficarem em placeholder;
- perfis default/manut são registrados na UI;
- setup.sh do Exocórtex roda dentro do container com proteção contra recursão;
- smoke valida health, SOUL.md, profile manut, config.json e banco da UI.

Gaps atuais:

- conceito de instância ainda não é explícito;
- paths default ainda são orientados a $HOME, não a /srv/exocortex/instances/<slug>;
- backup não inclui env operacional de forma explícita;
- backup/restore não são app-aware;
- systemd ainda é template bruto com __REPO_ROOT__;
- container roda como root;
- regra private-only via Tailscale ainda precisa virar contrato documental;
- multi-instância por usuário Unix ainda não foi incorporada ao provisionador.

## 4. Modelo alvo

### 4.1 Unidade operacional

Uma instância Exocórtex/Hermes/Web UI é definida por:

- INSTANCE_SLUG;
- usuário Unix próprio;
- diretórios próprios;
- env próprio;
- portas próprias;
- container name próprio;
- compose project name próprio;
- backups próprios;
- segredos próprios;
- receipts próprios.

### 4.2 Layout canônico por instância

Usar este layout como alvo de produção:

```text
/srv/exocortex/instances/<slug>/
  hermes/          # HERMES_HOME da instância
  exocortex/       # EXOCORTEX_HOME / acervo / artefatos
  webui/           # banco SQLite, config.json e estado da UI
  env/
    .env           # env operacional da instância
  backups/         # backups da instância
  logs/            # logs de provisionamento/backup/restore
  receipts/        # receipts de bootstrap e validação
```

Exemplo:

```text
/srv/exocortex/instances/alpha/hermes
/srv/exocortex/instances/alpha/exocortex
/srv/exocortex/instances/alpha/webui
/srv/exocortex/instances/alpha/env/.env
```

### 4.3 Mapeamento Docker

Para cada instância:

```text
/srv/exocortex/instances/<slug>/hermes    -> /srv/hermes
/srv/exocortex/instances/<slug>/exocortex -> /srv/exocortex
/srv/exocortex/instances/<slug>/webui     -> /srv/hermes-web-ui
```

O container não deve ser fonte de verdade. O host mantém o estado.

### 4.4 Acesso

Acesso padrão:

- local: 127.0.0.1;
- remoto privado: Tailscale;
- público direto: fora de escopo.

Qualquer exposição fora de Tailscale exige novo plano de segurança.

## 5. Regras para agentes implementadores

1. Não criar exposição pública da UI.
2. Não trocar v0.6.14 por main/master/HEAD sem issue própria.
3. Não misturar estado de instâncias.
4. Não compartilhar HERMES_HOME entre instâncias.
5. Não compartilhar EXOCORTEX_HOME entre instâncias.
6. Não compartilhar EXOCORTEX_WEB_UI_HOME entre instâncias.
7. Não tratar backup sem env como backup completo.
8. Não executar restore com instância viva no fluxo oficial.
9. Não publicar issues GitHub sem aprovação explícita do executivo.
10. Não alterar SOUL.md para este plano.

## 6. Épicos e issues propostas

As issues abaixo devem espelhar este plano. Ao publicar, cada issue deve linkar esta âncora local:

- docs/plans/hermes-web-ui-private-ops-hardening-2026-06-14.md

Labels existentes úteis:

- enhancement
- documentation
- infra
- security
- testing
- P0
- P1
- P2
- exocortex
- UI

## 7. DRAFT — EPIC META

### Título

[META] Hermes Web UI privada: operação híbrida, instâncias isoladas e hardening de setup

### Labels

enhancement, infra, security, UI, P0, exocortex

### Body

#### Contexto

O repositório já possui um provisionador inicial para a Hermes Web UI em provision/hermes-web-ui. A trilha atual builda a UI em Docker, mantém o estado no host, executa bootstrap do Exocórtex dentro do container e valida o health final.

A decisão arquitetural aprovada é manter o modelo híbrido:

- compute da Web UI em Docker;
- dados persistidos no host;
- arquivos acessíveis para inspeção, backup e operação;
- acesso privado via Tailscale;
- múltiplas instâncias futuras isoladas por usuário Unix;
- sem exposição pública direta.

Plano local de referência:

- docs/plans/hermes-web-ui-private-ops-hardening-2026-06-14.md

#### Problema

A implementação atual funciona como primeira entrega, mas ainda não tem um conceito formal de instância, não endurece backup/restore como fluxo app-aware, não renderiza systemd por instância e ainda documenta o private-only como prática, não como contrato operacional.

#### Objetivo

Transformar o provisionador da Hermes Web UI em uma trilha privada, auditável, preparada para operação por Ops e compatível com múltiplas instâncias isoladas por usuário Unix.

#### Fases

Fase 1 — Formalizar o modelo de instância

- Introduzir INSTANCE_SLUG.
- Derivar paths, nomes e portas por instância.
- Documentar layout canônico em /srv/exocortex/instances/<slug>.

Fase 2 — Endurecer rede e segurança privada

- Tornar private-only/Tailscale o contrato explícito.
- Validar CORS e bind.
- Reforçar bloqueio de exposição pública.

Fase 3 — Tornar backup/restore operacional

- Incluir env e receipts no backup.
- Parar/subir serviço de forma controlada.
- Validar restore por smoke.

Fase 4 — Formalizar operação por serviço

- Renderizar ou documentar systemd por instância.
- Garantir comandos start/stop/status claros.

Fase 5 — Documentar runbook para Ops

- Criar, subir, parar, backup, restore, rotacionar segredo, migrar host e desativar instância.

#### Subissues propostas

1. [P0] Introduzir INSTANCE_SLUG e layout canônico por instância.
2. [P0] Endurecer envelope private-only via Tailscale e bind seguro.
3. [P0] Tornar backup/restore app-aware e completo por instância.
4. [P1] Renderizar systemd/serviço por instância.
5. [P1] Criar runbook de Ops para ciclo de vida da instância.
6. [P2] Investigar rootless container/Podman para reduzir blast radius.

#### Definição de pronto do épico

- O provisionador aceita uma instância explícita ou documenta o modo single-instance como compatível com o layout alvo.
- Cada instância pode ter paths, portas, nome de container e env próprios.
- O fluxo private-only via Tailscale está documentado e validado.
- Backup inclui runtime Hermes, workspace Exocórtex, estado da UI, env e receipts.
- Restore exige instância parada e executa smoke final.
- systemd ou wrapper operacional permite start/stop/status por instância.
- Runbook de Ops explica o ciclo de vida sem depender do histórico desta conversa.

#### Notas para agentes menores

- Não tente resolver todos os subitens nesta issue META.
- Use esta issue apenas como mapa.
- Antes de implementar qualquer subissue, leia docs/plans/hermes-web-ui-private-ops-hardening-2026-06-14.md e provision/hermes-web-ui/README.md.
- Não exponha a UI publicamente.
- Não altere SOUL.md.

## 8. DRAFT — Issue 1

### Título

[P0] Hermes Web UI: introduzir INSTANCE_SLUG e layout canônico por instância

### Labels

enhancement, infra, P0, exocortex, UI

### Body

#### Contexto

A trilha atual da Hermes Web UI usa variáveis como EXOCORTEX_HERMES_HOME, EXOCORTEX_HOME e EXOCORTEX_WEB_UI_HOME. Isso funciona para uma instância, mas não transforma “instância” em unidade operacional explícita.

Plano local de referência:

- docs/plans/hermes-web-ui-private-ops-hardening-2026-06-14.md

#### Problema

Sem INSTANCE_SLUG e layout canônico, futuras múltiplas instâncias dependem de disciplina manual. Isso aumenta risco de mistura de runtime, acervo, env, portas e backups.

#### Objetivo

Adicionar suporte claro a uma instância nomeada, mantendo compatibilidade com o modo atual.

#### Escopo

Modificar ou criar, conforme necessário:

- provision/hermes-web-ui/env/.env.example
- provision/hermes-web-ui/scripts/common.sh
- provision/hermes-web-ui/scripts/install.sh
- provision/hermes-web-ui/docker/compose.yml
- provision/hermes-web-ui/README.md

#### Fora de escopo

- Criar usuários Unix automaticamente.
- Publicar issues no GitHub.
- Expor UI fora de Tailscale.
- Migrar para Kubernetes.

#### Requisitos funcionais

1. Adicionar EXOCORTEX_INSTANCE_SLUG com default seguro, por exemplo default.
2. Definir layout recomendado:

```text
/srv/exocortex/instances/${EXOCORTEX_INSTANCE_SLUG}/hermes
/srv/exocortex/instances/${EXOCORTEX_INSTANCE_SLUG}/exocortex
/srv/exocortex/instances/${EXOCORTEX_INSTANCE_SLUG}/webui
/srv/exocortex/instances/${EXOCORTEX_INSTANCE_SLUG}/env/.env
/srv/exocortex/instances/${EXOCORTEX_INSTANCE_SLUG}/backups
/srv/exocortex/instances/${EXOCORTEX_INSTANCE_SLUG}/logs
/srv/exocortex/instances/${EXOCORTEX_INSTANCE_SLUG}/receipts
```

3. Permitir override manual dos paths atuais.
4. Derivar container name quando não informado:

```text
exocortex-hermes-web-ui-${EXOCORTEX_INSTANCE_SLUG}
```

5. Derivar compose project name quando possível.
6. Documentar que múltiplas instâncias devem usar usuários Unix distintos.

#### Tarefas detalhadas

1. Ler common.sh e identificar onde defaults de paths são definidos.
2. Adicionar EXOCORTEX_INSTANCE_SLUG ao load_env.
3. Criar variável EXOCORTEX_INSTANCE_ROOT com default /srv/exocortex/instances/${EXOCORTEX_INSTANCE_SLUG}.
4. Ajustar defaults para HERMES_HOME, EXOCORTEX_HOME e WEB_UI_HOME quando o usuário não informar overrides.
5. Ajustar env/.env.example com comentários claros.
6. Ajustar README com exemplos alpha/beta.
7. Rodar shellcheck ou bash -n nos scripts alterados.
8. Rodar smoke com env temporário, sem tocar produção.

#### Critérios de aceite

- EXOCORTEX_INSTANCE_SLUG aparece no env de exemplo.
- common.sh deriva paths por instância quando paths explícitos não foram setados.
- Overrides existentes continuam funcionando.
- compose usa container name derivável por instância.
- README explica single-instance e multi-instance.
- bash -n passa nos scripts alterados.
- Um agente consegue criar env alpha e beta sem conflito de paths.

#### Notas para agentes menores

- Não faça refactor amplo.
- Preserve compatibilidade com envs existentes.
- Se uma variável já estiver setada no env, não sobrescreva.
- Não crie usuário Unix nesta issue; só documente e prepare a estrutura.

## 9. DRAFT — Issue 2

### Título

[P0] Hermes Web UI: endurecer envelope private-only via Tailscale e bind seguro

### Labels

security, infra, P0, exocortex, UI

### Body

#### Contexto

A decisão aprovada é manter a Web UI como cockpit privado. O acesso remoto deve ocorrer via Tailscale. A UI não deve ser publicada como superfície pública direta.

Plano local de referência:

- docs/plans/hermes-web-ui-private-ops-hardening-2026-06-14.md

#### Problema

O provisionador já tem bind local, tailscale-auto e exigência de CORS fora de loopback. Falta transformar essa política em contrato claro, com validações e documentação operacional.

#### Objetivo

Garantir que o setup favoreça acesso privado e bloqueie exposição pública acidental.

#### Escopo

Modificar ou criar, conforme necessário:

- provision/hermes-web-ui/scripts/common.sh
- provision/hermes-web-ui/env/.env.example
- provision/hermes-web-ui/README.md
- docs/ops/hermes-web-ui-private-access.md ou caminho equivalente

#### Fora de escopo

- Configurar reverse proxy público.
- Configurar domínio público.
- Emitir TLS público.
- Criar autenticação multi-tenant SaaS.

#### Requisitos funcionais

1. Documentar modos aceitos:

- 127.0.0.1 para uso local;
- tailscale-auto para acesso privado;
- IP explícito somente com CORS_ORIGINS definido e aviso forte.

2. Garantir que EXOCORTEX_UI_BIND_IP=0.0.0.0 falhe por default, salvo override explícito.
3. Adicionar variável de override consciente, por exemplo EXOCORTEX_ALLOW_PUBLIC_BIND=1, se for realmente necessário.
4. Documentar que exposição pública direta está fora do contrato.
5. Smoke deve reportar URL final acessível.

#### Tarefas detalhadas

1. Ler validate_security_envelope em common.sh.
2. Adicionar bloqueio explícito para 0.0.0.0 sem override.
3. Validar tailscale-auto sem CORS manual, derivando CORS quando possível.
4. Atualizar env/.env.example com comentários sobre Tailscale.
5. Criar documentação privada de acesso.
6. Rodar bash -n.
7. Testar validação com env temporário para 127.0.0.1, tailscale-auto e 0.0.0.0.

#### Critérios de aceite

- 127.0.0.1 passa.
- tailscale-auto passa quando tailscale estiver disponível ou falha com erro claro quando não estiver.
- 0.0.0.0 falha por default.
- CORS_ORIGINS continua obrigatório para bind não-loopback.
- README declara que o cockpit é privado.
- Nenhum exemplo sugere exposição pública direta.

#### Notas para agentes menores

- Segurança vence conveniência nesta issue.
- Não adicione nginx/caddy/traefik.
- Não invente suporte público.
- Use mensagens de erro claras.

## 10. DRAFT — Issue 3

### Título

[P0] Hermes Web UI: tornar backup/restore app-aware e completo por instância

### Labels

infra, security, testing, P0, exocortex, UI

### Body

#### Contexto

O backup atual empacota HERMES_HOME, EXOCORTEX_HOME e EXOCORTEX_WEB_UI_HOME. Isso é bom como base, mas não cobre todo o estado operacional nem garante consistência do banco SQLite da UI.

Plano local de referência:

- docs/plans/hermes-web-ui-private-ops-hardening-2026-06-14.md

#### Problema

Backup sem env, receipts e consistência de aplicação pode restaurar arquivos sem restaurar a instância de forma confiável. Restore com serviço vivo pode introduzir drift ou corrupção.

#### Objetivo

Criar fluxo oficial de backup/restore por instância, com app parado ou consistência garantida, env incluído e smoke pós-restore.

#### Escopo

Modificar ou criar, conforme necessário:

- provision/hermes-web-ui/scripts/backup.sh
- provision/hermes-web-ui/scripts/restore.sh
- provision/hermes-web-ui/scripts/smoke.sh
- provision/hermes-web-ui/scripts/common.sh
- provision/hermes-web-ui/README.md
- docs/ops/hermes-web-ui-backup-restore.md ou caminho equivalente

#### Fora de escopo

- Backup remoto/offsite automático.
- Integração com S3, Borg, Restic ou Kopia.
- Criptografia obrigatória nesta primeira issue, salvo documentação de gap.

#### Requisitos funcionais

1. Backup deve incluir:

- HERMES_HOME;
- EXOCORTEX_HOME;
- EXOCORTEX_WEB_UI_HOME;
- env operacional da instância;
- receipts;
- metadados de versão/ref/slug/data.

2. Backup deve ter modo seguro:

- parar compose antes do tar; ou
- usar sqlite backup API; ou
- documentar e implementar uma estratégia equivalente.

3. Restore deve exigir confirmação ou flag explícita.
4. Restore deve rodar com instância parada.
5. Restore deve executar smoke depois.
6. Nome do arquivo deve incluir slug e timestamp.

#### Tarefas detalhadas

1. Ler backup.sh e restore.sh atuais.
2. Definir formato de manifest do backup.
3. Adicionar inclusão do ENV_FILE.
4. Adicionar inclusão de receipts.
5. Implementar stop/start controlado via compose quando aplicável.
6. Adicionar flag para restore destrutivo, por exemplo EXOCORTEX_RESTORE_CONFIRM=1.
7. Rodar bash -n.
8. Testar backup em runtime temporário.
9. Testar restore em diretório temporário.
10. Rodar smoke pós-restore.

#### Critérios de aceite

- Backup gerado contém runtime, workspace, webui, env e manifest.
- Restore recusa execução sem confirmação explícita.
- Restore não roda com container da instância vivo, salvo modo documentado.
- Smoke pós-restore passa em ambiente temporário.
- README explica o procedimento seguro.

#### Notas para agentes menores

- Não apague dados reais durante teste.
- Use diretórios temporários.
- Não rode restore contra ~/.hermes real sem autorização.
- Se o teste precisar de Docker, indique isso no relatório.

## 11. DRAFT — Issue 4

### Título

[P1] Hermes Web UI: renderizar serviço systemd por instância

### Labels

infra, enhancement, P1, exocortex, UI

### Body

#### Contexto

Existe um arquivo systemd inicial em provision/hermes-web-ui/systemd/exocortex-hermes-ui.service, mas ele contém __REPO_ROOT__ e não representa ainda uma instalação por instância.

Plano local de referência:

- docs/plans/hermes-web-ui-private-ops-hardening-2026-06-14.md

#### Problema

Ops precisa de start/stop/status previsível por instância. Um template não renderizado não basta para operação.

#### Objetivo

Criar uma estratégia de serviço por instância que suporte operação local e futura multi-instância.

#### Escopo

Modificar ou criar, conforme necessário:

- provision/hermes-web-ui/systemd/exocortex-hermes-ui.service
- provision/hermes-web-ui/systemd/exocortex-hermes-ui@.service, se adotado
- provision/hermes-web-ui/scripts/install-systemd.sh, se adotado
- provision/hermes-web-ui/README.md
- docs/ops/hermes-web-ui-systemd.md ou caminho equivalente

#### Fora de escopo

- Instalar serviço automaticamente sem confirmação.
- Criar usuários Unix automaticamente.
- Configurar serviços em hosts remotos.

#### Requisitos funcionais

1. Documentar modo user service e system service, se ambos forem viáveis.
2. Permitir serviço por instância.
3. O serviço deve apontar para env correto da instância.
4. O serviço deve executar docker compose com compose project name correto.
5. Deve haver comandos claros para:

- install/render;
- start;
- stop;
- status;
- logs;
- uninstall.

#### Tarefas detalhadas

1. Avaliar se o melhor caminho é template @.service ou renderização de service file.
2. Escolher abordagem mais simples e reversível.
3. Implementar script de renderização, se necessário.
4. Documentar comandos.
5. Rodar systemd-analyze verify quando disponível.
6. Não habilitar serviço sem aprovação.

#### Critérios de aceite

- Não existe mais placeholder __REPO_ROOT__ em serviço final renderizado.
- É possível gerar serviço para alpha e beta sem conflito de nomes.
- Documentação explica operação manual.
- Nenhum serviço é instalado automaticamente sem confirmação.

#### Notas para agentes menores

- systemd é ação local; instalação automática ainda deve ser conservadora.
- Não use sudo sem necessidade.
- Se precisar de sudo, pare e peça confirmação.

## 12. DRAFT — Issue 5

### Título

[P1] Hermes Web UI: criar runbook de Ops para ciclo de vida da instância

### Labels

documentation, infra, P1, exocortex, UI

### Body

#### Contexto

O executivo decidiu que futuras múltiplas instâncias serão geridas por Ops externa. Para isso, o projeto precisa de documentação operacional que não dependa do histórico de chat.

Plano local de referência:

- docs/plans/hermes-web-ui-private-ops-hardening-2026-06-14.md

#### Problema

Sem runbook, agentes e operadores podem improvisar paths, expor a UI, misturar estados ou fazer backup incompleto.

#### Objetivo

Criar documentação operacional suficiente para uma equipe de Ops criar, operar, proteger, restaurar e desativar instâncias.

#### Escopo

Criar ou atualizar:

- docs/ops/hermes-web-ui-runbook.md
- provision/hermes-web-ui/README.md
- docs/ops/hermes-web-ui-private-access.md, se Issue 2 não criar
- docs/ops/hermes-web-ui-backup-restore.md, se Issue 3 não criar

#### Fora de escopo

- Implementar mudanças de scripts.
- Publicar documentação externa.
- Criar automação de provisionamento em cloud.

#### Conteúdo mínimo do runbook

1. Conceitos

- instância;
- slug;
- usuário Unix;
- runtime Hermes;
- workspace Exocórtex;
- estado da UI;
- env da instância;
- Tailscale.

2. Criar instância

- escolher slug;
- criar usuário Unix;
- criar diretórios;
- copiar env;
- configurar portas;
- subir compose;
- rodar smoke.

3. Operar instância

- start;
- stop;
- status;
- logs;
- healthcheck.

4. Segurança

- private-only;
- Tailscale;
- permissões de arquivos;
- rotação de segredo;
- o que não fazer.

5. Backup/restore

- backup seguro;
- restore seguro;
- smoke pós-restore;
- teste periódico.

6. Multi-instância

- exemplo alpha/beta;
- portas separadas;
- usuários separados;
- paths separados.

7. Troubleshooting

- container não sobe;
- health falha;
- permissão negada;
- tailscale-auto falha;
- smoke falha;
- DB da UI inconsistente.

#### Critérios de aceite

- Um operador sem contexto da conversa consegue seguir o runbook.
- O runbook não sugere exposição pública.
- O runbook inclui comandos e paths concretos.
- O runbook diferencia single-instance e multi-instance.
- O README aponta para o runbook.

#### Notas para agentes menores

- Escreva para execução, não para convencer.
- Use exemplos alpha/beta.
- Não esconda riscos.
- Não prometa automação que ainda não existe.

## 13. DRAFT — Issue 6

### Título

[P2] Hermes Web UI: investigar rootless container/Podman para reduzir blast radius

### Labels

research, security, infra, P2, exocortex, UI

### Body

#### Contexto

O Dockerfile atual executa como root. Isso é aceitável para piloto privado, mas é dívida de hardening para operação madura.

Plano local de referência:

- docs/plans/hermes-web-ui-private-ops-hardening-2026-06-14.md

#### Problema

Como o container monta runtime Hermes, workspace Exocórtex e estado da UI com escrita, um processo root no container aumenta o blast radius em caso de bug ou comprometimento.

#### Objetivo

Avaliar caminho seguro e viável para rodar a Web UI sem root, usando Docker rootless, usuário não-root no container ou Podman.

#### Escopo

Analisar:

- Dockerfile.ui;
- compose.yml;
- permissões dos bind mounts;
- node-pty;
- execução do Hermes CLI dentro do container;
- compatibilidade com Arch Linux e hosts Linux comuns.

#### Fora de escopo

- Migrar obrigatoriamente para Podman nesta issue.
- Quebrar setup atual.
- Exigir rootless como bloqueador da primeira produção privada.

#### Tarefas detalhadas

1. Identificar por que o container roda como root hoje.
2. Testar usuário não-root com bind mounts em ambiente temporário.
3. Testar se node-pty e Hermes CLI continuam funcionando.
4. Testar permissões de escrita em /srv/hermes, /srv/exocortex e /srv/hermes-web-ui.
5. Comparar opções:

- Docker rootful + USER não-root;
- Docker rootless;
- Podman rootless;
- manter root com mitigação temporária.

6. Registrar recomendação com riscos.

#### Critérios de aceite

- Documento de avaliação criado em docs/research ou docs/ops.
- Matriz de opções preenchida.
- Comandos de teste registrados.
- Recomendação final clara.
- Se houver mudança implementável, criar issue de execução separada.

#### Notas para agentes menores

- Esta issue é pesquisa, não migração.
- Não quebre o provisionador atual.
- Registre falhas reais de teste.
- Não invente compatibilidade sem executar.

## 14. Dependências entre issues

Ordem recomendada:

1. Issue 1 primeiro: INSTANCE_SLUG e layout.
2. Issue 2 em paralelo parcial com Issue 1, mas validar depois dela.
3. Issue 3 depois de Issue 1, porque backup precisa conhecer instância.
4. Issue 4 depois de Issue 1, porque serviço precisa de slug/env/path.
5. Issue 5 depois de Issues 1 a 4, para documentar o comportamento real.
6. Issue 6 pode rodar em paralelo como pesquisa, sem bloquear P0.

Dependências textuais para comentários pós-criação:

- Issue 2: bloqueia promoção do cockpit como trilha privada segura.
- Issue 3: bloqueada por Issue 1; backup precisa do modelo de instância.
- Issue 4: bloqueada por Issue 1; serviço precisa de slug e paths.
- Issue 5: bloqueada por Issues 1, 2, 3 e 4; runbook deve refletir implementação real.
- Issue 6: independente; pesquisa de hardening.

## 15. Critérios globais de aceite

O plano estará concluído quando:

- setup da Web UI operar em modo single-instance com layout documentado;
- INSTANCE_SLUG ou equivalente estiver disponível;
- paths e nomes puderem ser separados por instância;
- private-only via Tailscale estiver documentado e validado;
- backup incluir dados, env e receipts;
- restore for app-aware e passar smoke;
- systemd tiver trilha de operação por instância;
- runbook permitir execução por Ops sem contexto adicional;
- GitHub issues publicadas espelharem este plano e apontarem para esta âncora local.

## 16. Checklist de progresso local

- [x] Decisão arquitetural registrada nesta conversa.
- [x] Plano local criado.
- [x] Issues GitHub aprovadas pelo executivo.
- [x] Issues GitHub criadas.
- [x] Dependências entre issues comentadas no GitHub.
- [ ] Issue #69 concluída.
- [ ] Issue #70 concluída.
- [ ] Issue #71 concluída.
- [ ] Issue #72 concluída.
- [ ] Issue #73 concluída.
- [ ] Issue #74 concluída ou registrada como decisão futura.

## 16.1 Issues publicadas

Épico META:

- #68 — [META] Hermes Web UI privada: operação híbrida, instâncias isoladas e hardening de setup

Subissues:

- #69 — [P0] Hermes Web UI: introduzir INSTANCE_SLUG e layout canônico por instância
- #70 — [P0] Hermes Web UI: endurecer envelope private-only via Tailscale e bind seguro
- #71 — [P0] Hermes Web UI: tornar backup/restore app-aware e completo por instância
- #72 — [P1] Hermes Web UI: renderizar serviço systemd por instância
- #73 — [P1] Hermes Web UI: criar runbook de Ops para ciclo de vida da instância
- #74 — [P2] Hermes Web UI: investigar rootless container/Podman para reduzir blast radius

Comentários de dependência publicados:

- #69 bloqueia #71 e #72.
- #70 avança em paralelo, validado contra #69.
- #71 depende de #69 e bloqueia #73.
- #72 depende de #69 e bloqueia #73.
- #73 depende de #69, #70, #71 e #72.
- #74 é pesquisa independente.

## 17. Registro da publicação das issues

GitHub é ação externa. A publicação foi executada após aprovação explícita do executivo em 2026-06-14.

Etapas executadas:

1. Criada a issue META #68.
2. Criadas as seis subissues #69 a #74.
3. Corpo da META #68 editado com os números reais.
4. Corpos das subissues editados com rastreamento para a META #68 e este plano local.
5. Comentários de dependência publicados nas subissues.
6. Este plano local atualizado com os números reais.

## 18. Comandos de verificação recomendados após implementação

```bash
bash -n provision/hermes-web-ui/scripts/common.sh
bash -n provision/hermes-web-ui/scripts/install.sh
bash -n provision/hermes-web-ui/scripts/backup.sh
bash -n provision/hermes-web-ui/scripts/restore.sh
bash -n provision/hermes-web-ui/scripts/smoke.sh
```

Smoke em ambiente temporário:

```bash
EXOCORTEX_PROVISION_ENV_FILE=/tmp/exocortex-webui-test.env \
  bash provision/hermes-web-ui/scripts/install.sh
```

Verificação de compose:

```bash
docker compose --env-file provision/hermes-web-ui/env/.env \
  -f provision/hermes-web-ui/docker/compose.yml config
```

## 19. Observações finais

Este plano prioriza operação privada, previsível e inspecionável. A UI serve como cockpit operacional do Hermes/Exocórtex, não como produto público SaaS neste ciclo.
