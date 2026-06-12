# Plano de provisionamento automático — hermes-web-ui para exocortex.saas/Hermes

Data: 2026-06-12
Repositório avaliado: `https://github.com/EKKOLearnAI/hermes-web-ui`
Checkout local: `/home/elder/work/repo-assessments/hermes-web-ui`

## 1. Veredito executivo

`hermes-web-ui` já está perto de um painel operacional de Hermes, não apenas de um chat web.
Ele expõe gestão de profiles, skills, memory, providers, MCP, jobs, logs, arquivos, terminal, TTS/STT, group chat, coding agents, runtime versions e write approvals.

Para o Exocórtex, isso significa duas coisas ao mesmo tempo:

1. **É uma boa base de superfície operacional** para `exocortex.saas/Hermes`.
2. **Não pode ser adotado como-is** sem um hardening e sem uma estratégia clara de fronteira, porque hoje a UI mistura:
   - console de operação do runtime Hermes,
   - camada de colaboração/usuários,
   - e uma opinião própria sobre sessões, auth, estado local e gateway.

Minha leitura: a melhor coalizão não é “substituir o Exocórtex pela UI”, mas **usar a UI como cockpit operacional do runtime** e deixar o Exocórtex como camada cognitiva, identitária e de governança.

## 2. Evidências executadas

Validação real executada no checkout local:

- `npm ci --ignore-scripts` → sucesso
- `npm run test` → sucesso
- `npm run build` → sucesso
- smoke de runtime com servidor buildado → sucesso
- `curl http://127.0.0.1:18648/health` → retorno `status=ok`

Saída relevante do smoke:

- `platform: hermes-agent`
- `webui_version: 0.6.14`
- `gateway: running`
- `agent_bridge.status: ready`

Isso confirma que a trilha crítica mínima **instala, testa, builda e sobe** neste ambiente.

## 3. Contrato declarado da solução

Pelo README, ARCHITECTURE, Docker e package manifests, a solução se apresenta como:

- monorepo TypeScript com client, server, desktop e website;
- distribuição web + desktop;
- interface de operação para Hermes Agent;
- bridge/proxy para runtime Hermes;
- camada própria de autenticação e multiusuário;
- recursos de observabilidade e administração além do chat.

Sinais concretos encontrados:

- `packages/desktop/package.json` descreve explicitamente uma distribuição desktop com Python runtime e `hermes-agent` embutidos.
- `packages/server/src/routes/index.ts` registra rotas para praticamente todo o plano operacional do Hermes.
- `docs/hermes-write-gate.md` e `packages/server/src/routes/hermes/write-gate.ts` mostram suporte de revisão/aprovação de writes de memory e skills.
- `docs/openapi.json` formaliza o contrato HTTP.

## 4. Contrato executável e fronteiras reais

### 4.1 Monorepo real

Partes relevantes:

- `packages/client`: frontend Vue/Vite
- `packages/server`: backend Koa/TypeScript
- `packages/desktop`: embalagem Electron + runtime bundle
- `bin/hermes-web-ui.mjs`: entrypoint/CLI

### 4.2 Fronteira UI/backend

A UI não conversa só com um backend genérico. Ela tem uma fronteira muito explícita com o runtime Hermes.

Em `packages/server/src/routes/index.ts`, o backend registra APIs para:

- sessions
- profiles
- skills
- plugins
- memory
- models
- providers
- config
- logs
- files/downloads
- jobs/cron history
- kanban
- TTS/STT/media
- MCP
- runtime versions
- write gate
- proxy Hermes

Conclusão: isso não é uma UI “plugável” superficial; é um **backend de orquestração do Hermes com UI acoplada**.

### 4.3 Fronteira com o Hermes runtime

A camada server executa `hermes` de verdade.

Evidências:

- `packages/server/src/services/hermes/hermes-process.ts` usa `execFile` e `spawn` para invocar o binário Hermes.
- `packages/server/src/services/hermes/hermes-cli.ts` encapsula operações como gateway, profiles e leitura de estado.
- `packages/server/src/services/hermes/agent-bridge/manager.ts` sobe bridge/processos auxiliares.

Conclusão: o deploy precisa tratar `hermes-web-ui` e `hermes-agent` como **componentes cooperantes**, não independentes.

### 4.4 Fronteira de estado

Há uma decisão arquitetural importante já codificada:

- `packages/server/src/services/hermes/session-sync.ts` declara que a importação de sessões do Hermes para o banco local da UI está **intencionalmente desativada**.
- O `state.db` do Hermes fica como fonte read-only para APIs específicas.
- A UI mantém banco/local state próprio para sessões dela.

Isso evita mistura destrutiva de ownership, mas cria um ponto de tensão para o Exocórtex: **duas narrativas de sessão** coexistem.

## 5. Riscos e gaps que impedem adoção direta

### 5.1 Credenciais default inseguras

Em `packages/server/src/db/hermes/users-store.ts` existe bootstrap explícito com:

- `DEFAULT_USERNAME = 'admin'`
- `DEFAULT_PASSWORD = '[REDACTED]'`

Isso sozinho já exige que o provisionamento automático:

- troque a senha no primeiro boot; ou
- desabilite bootstrap default; ou
- injete admin inicial via secret seguro.

Sem isso, a solução não pode ser exposta em ambiente SaaS.

### 5.2 Dependências com vulnerabilidades abertas

`npm audit --json` retornou:

- 4 vulnerabilidades críticas
- 2 moderadas

Destaques:

- `vitest < 3.2.6`
- `concurrently` via `shell-quote`
- `dompurify` transitivo via `monaco-editor`

Parte disso é dev-time, mas para um pipeline corporativo isso precisa entrar na esteira de remediação antes de promover a stack.

### 5.3 Bundle frontend pesado

`npm run build` emitiu warning de chunks > 1000 kB.

Destaques do build:

- `monaco-editor` ~4.3 MB
- `mermaid` ~3.2 MB
- `vendor` ~1.8 MB
- `index` ~977 kB

Não bloqueia uso, mas impacta:

- cold start do browser
- consumo de banda
- UX em acesso remoto
- custo quando empacotado em setup mais amplo

### 5.4 Licença e governança de distribuição

`packages/desktop/package.json` declara `BSL-1.1`.

Antes de incorporar no `exocortex.saas/Hermes`, precisa fechar:

- compatibilidade com a estratégia comercial/distribuição do Exocórtex;
- regras de modificação e redistribuição;
- se faremos fork privado, contribuição upstream ou camada overlay.

### 5.5 Acoplamento operacional alto

A solução assume detalhes concretos do runtime:

- `HERMES_HOME`
- `HERMES_WEB_UI_HOME`
- `HERMES_WEBUI_STATE_DIR`
- `HERMES_BIN`
- políticas de autostart de gateway
- recuperação de orphan processes em desktop/Windows

Isso é bom para operação profunda, mas significa que o Exocórtex precisa escolher: **ou abraça esse acoplamento, ou cria uma façade própria sobre ele**.

## 6. Oportunidades reais de coalizão Exocórtex × UI

## 6.1 Melhor encaixe: cockpit operacional + camada cognitiva separada

Arquitetura recomendada:

- `hermes-web-ui` = cockpit técnico e administrativo
- `Exocórtex` = camada cognitiva, memória, governança, drafting, microversos, estilo e protocolos

Em termos simples:

- a UI opera a máquina;
- o Exocórtex opera o executivo.

## 6.2 Coalizão imediata já suportada pelo código

### A. Write approvals para memory/skills

Esse é o melhor ponto de convergência já pronto.

Evidências:

- rotas: `/api/hermes/write-gate/pending/...`
- testes: `tests/client/pending-write-approvals.test.ts`
- i18n já fala explicitamente em aprovar/rejeitar writes de memory e skills

Coalizão proposta:

- todo write sensível do Exocórtex em memória/skills passa pela UI em modo review quando estiver em ambiente governado;
- o Exocórtex continua propondo a mudança;
- a UI oferece diff, aprovação, rejeição e trilha auditável.

Isso casa perfeitamente com o Draft-First e com governança operacional.

### B. Profiles como ambientes cognitivos

A UI já opera profiles do Hermes.

Coalizão proposta:

- mapear `exec`, `evol`, `manut` como perfis operacionais visíveis na UI;
- expor status, credenciais, gateway, plugins e MCP por perfil;
- usar a UI para observabilidade e troca controlada de contexto.

### C. Jobs/Cron + rotinas de manutenção do Exocórtex

A UI já tem jobs e cron history.

Coalizão proposta:

- plugar briefings, manutenção de inbox, health checks de microversos e reconciliações como rotinas nativas visíveis na UI;
- manter a inteligência da rotina no Exocórtex e usar a UI para agenda, auditoria e replay.

### D. Kanban como superfície de pendências do executivo

Há suporte explícito a kanban.

Coalizão proposta:

- sincronizar itens de manutenção, decisões pendentes e tarefas operacionais do Exocórtex com o quadro da UI;
- usar o kanban como superfície humana; o Acervo Cognitivo continua como fonte semântica.

### E. Group chat e colaboração assistida

A UI tem group chat e identidades de agentes/membros.

Coalizão proposta:

- usar group chat para times internos operarem junto do Exocórtex sem transformar o núcleo cognitivo em chat público indiscriminado;
- Exocórtex entra como agente nomeado, com regras de draft/governança preservadas.

## 6.3 Onde NÃO coalizar sem redesenho

### A. Banco de sessões local da UI como fonte primária do Exocórtex

Não recomendo.

O próprio projeto já reconhece o risco e desabilita sync destrutivo.

O Exocórtex deve manter como fonte primária:

- memória persistente própria
- session DB do Hermes
- acervo/microversos

A UI pode consumir e visualizar, mas não deve redefinir ownership dessa memória.

### B. Auth padrão da UI como modelo final de identidade SaaS

Também não recomendo adotar sem refatoração.

Motivos:

- bootstrap admin default
- necessidade de secrets mais fortes
- integração futura com identidade do Exocórtex ainda não modelada

### C. Desktop distribution como primeira aposta do setup Exocórtex SaaS

O desktop é útil, mas para `exocortex.saas/Hermes` eu não começaria por ele.

Motivos:

- empacota Node/Python/Hermes e adiciona muita superfície operacional;
- updater, feeds e runtime bundles aumentam a matriz de manutenção;
- web server/container é melhor primeiro degrau para provisionamento automático.

## 7. Estratégia recomendada de adoção

### Fase 0 — avaliação/fork controlado

Objetivo: criar baseline reproduzível.

Ações:

1. fixar commit upstream usado pela integração;
2. criar fork/espelho controlado;
3. registrar patchset do Exocórtex separado do upstream;
4. automatizar build/test/smoke em CI.

### Fase 1 — hardening mínimo obrigatório

Objetivo: torná-lo aceitável para ambiente interno governado.

Ações:

1. remover/admin default inseguro ou forçar bootstrap por secret;
2. exigir `AUTH_JWT_SECRET` forte por ambiente;
3. definir política de cookies, sessões e CSRF;
4. revisar exposição das rotas de terminal, files, proxy e update;
5. resolver ou isolar vulnerabilidades do `npm audit`;
6. desligar qualquer autostart desnecessário por default em SaaS.

Gate de saída:

- nenhum default credencial exposto;
- smoke de login seguro funcionando;
- CI verde;
- checklist de exposição pública aprovado.

### Fase 2 — empacotamento container-first

Objetivo: provisionamento automático simples e reproduzível.

Ações:

1. construir imagem única `exocortex-hermes-ui` baseada em Node LTS suportado;
2. instalar `hermes-agent` explicitamente no build ou via camada controlada;
3. separar volumes:
   - `/data/hermes-home`
   - `/data/hermes-web-ui`
   - `/data/logs`
4. injetar env via secrets/config maps;
5. expor healthcheck HTTP;
6. desabilitar bootstrap inseguro;
7. parametrizar `HERMES_BIN`, `HERMES_HOME`, `HERMES_WEB_UI_HOME`, política de gateway.

### Fase 3 — provisionador Exocórtex

Objetivo: transformar setup em instalação automática do stack.

Ações:

1. script/Ansible/Terraform ou instalador shell para:
   - criar diretórios
   - injetar secrets
   - renderizar `.env`
   - renderizar compose/systemd/k8s manifest
   - rodar migração/boot inicial
2. bootstrap do macroverso e perfis `exec/evol/manut` após saúde da UI;
3. registrar skills centrais do Exocórtex;
4. opcionalmente criar admin inicial sem senha padrão.

### Fase 4 — coalizão funcional

Objetivo: fazer a UI operar o Exocórtex sem diluí-lo.

Ações:

1. expor write approvals como governança oficial;
2. mapear perfis do Exocórtex na UI;
3. integrar kanban/jobs/cron com manutenção e briefing;
4. criar superfícies específicas de Exocórtex na UI:
   - Macroverso
   - Microversos
   - Draft queue
   - Receipts/auditoria

### Fase 5 — produto

Objetivo: decidir se vira

- fork opinado do `hermes-web-ui`, ou
- plugin/theme/overlay do Exocórtex, ou
- backend do Hermes com frontend próprio do Exocórtex.

Minha recomendação hoje: **fork opinado com overlay do Exocórtex**, não rewrite e não white-label superficial.

## 8. Blueprint de provisionamento automático

## 8.1 Topologia recomendada

Componentes:

- `reverse-proxy` (Caddy/Nginx/Traefik)
- `exocortex-hermes-ui` (server + client buildado)
- `hermes-agent runtime` no mesmo container ou sidecar controlado
- volumes persistentes
- secrets manager

Para primeira versão, prefiro:

- **um container de app + volumes persistentes**, desde que o binário Hermes esteja estável;
- separar em sidecars só quando houver dor real de isolamento/escala.

## 8.2 Variáveis mínimas a modelar no provisionador

Obrigatórias:

- `PORT`
- `AUTH_JWT_SECRET`
- `HERMES_BIN`
- `HERMES_HOME`
- `HERMES_WEB_UI_HOME`
- `HERMES_WEBUI_STATE_DIR`
- `HERMES_WEB_UI_MANAGED_GATEWAY`
- `HERMES_WEB_UI_DISABLE_GATEWAY_AUTOSTART`

Desejáveis:

- política de bootstrap admin
- origem pública/base URL
- TLS/proxy headers
- política de logs
- política de uploads
- feature flags Exocórtex

## 8.3 Sequência de instalação automática recomendada

1. Resolver versão/commit do fork
2. Buildar imagem
3. Criar volumes persistentes
4. Injetar secrets
5. Subir container com gateway autostart controlado
6. Esperar `/health`
7. Executar bootstrap seguro:
   - admin inicial
   - perfis `exec/evol/manut`
   - skills/core config
8. Rodar smoke funcional:
   - login
   - listar profiles
   - listar skills
   - health bridge
   - write-gate capability
9. Liberar tráfego externo

## 8.4 Smoke suite mínima que deve virar gate de setup

- `/health` retorna `ok`
- login funciona com credencial não-default
- `hermes profile list` via backend responde
- bridge `ready=true`
- rotas de skills/memory respondem
- write approvals listam vazio sem erro
- um job de teste cria histórico
- gateway stop/start controlado funciona no ambiente escolhido

## 9. Plano profundo de instalação para o setup do Exocórtex

## 9.1 Entregável esperado

Gerar um instalador idempotente que produza:

- runtime Hermes pronto
- UI operacional
- perfis do Exocórtex
- governança básica
- health checks
- rollback simples

## 9.2 Estrutura sugerida do repositório de provisionamento

```text
provision/
  docker/
    Dockerfile.ui
    compose.yml
  env/
    .env.example
    secrets.schema
  scripts/
    install.sh
    bootstrap-admin.sh
    bootstrap-profiles.sh
    bootstrap-exocortex.sh
    smoke.sh
    backup.sh
    restore.sh
  systemd/
    exocortex-hermes-ui.service
  patches/
    upstream/
    exocortex/
  manifests/
    caddy/
    k8s/
```

## 9.3 Ordem de implementação

1. Container web-only reproduzível
2. Hardening de auth/defaults
3. Bootstrap de perfis Exocórtex
4. Integração write-gate
5. Integração jobs/kanban
6. Superfícies próprias de microversos/macroverso
7. Otimização de bundles e UX

## 10. Recomendação final

### O que eu faria agora

1. **Adotaria o `hermes-web-ui` como base operacional**.
2. **Não o exporia publicamente sem hardening**.
3. **Faria um fork controlado do Exocórtex**.
4. **Usaria container-first, não desktop-first**.
5. **Transformaria write approvals, profiles e jobs nos primeiros pontos de coalizão**.

### Frase curta do veredito

A solução é boa o bastante para virar o cockpit do `exocortex.saas/Hermes`, mas ainda não é boa o bastante para virar produto exposto sem um ciclo sério de hardening, recorte de ownership e integração opinada com a camada cognitiva do Exocórtex.

## 11. Próximo passo objetivo

O próximo passo certo é produzir um **plano executável de fork + hardening + containerização**, já convertido em:

- árvore de diretórios do provisionador
- `.env.example`
- `docker-compose.yml`
- `Dockerfile`
- scripts de bootstrap
- smoke suite

Se seguirmos, eu parto disso direto para os artefatos de provisionamento.