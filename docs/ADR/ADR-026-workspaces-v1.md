# ADR-026 — Workspaces de projeto separados do Acervo

- **Status:** DRAFT aprovado para implementação do Slice 0; aceite final pendente
- **Data:** 2026-08-15
- **Base:** `origin/main@1268365230f646955deec95b2355b70b7fa1fc6a`
- **Especificação normativa:** `docs/workspaces/WORKSPACE-SPEC-v1.md`
- **Contrato cognitivo:** `acervo/global/contracts/workspace-boundary-v1.md`

## Contexto

O Acervo é a memória canônica do Exocórtex, mas hoje também contém superfícies operacionais como `_tasks` e `_artifacts`. Projetos com código, fontes, assets e entregáveis próprios não devem transformar o Acervo em filesystem de trabalho nem entrar no recall por proximidade física.

A linguagem atual já separa microverso e tarefa, mas o repo não possui contrato físico para um workspace de projeto, locator local ou projeção reversa. O runtime instalado também contém um DRAFT experimental com gates e receipts rejeitados pela disposição executiva.

## Decisão

Adotar `excrtx-workspace/v1` com uma separação de autoridades:

| Preocupação | Autoridade |
|---|---|
| Arquivos, código, fontes e entregáveis | usuário; agente opera durante tarefa explícita |
| Identidade, objetivo, vínculo e status descritivo | `.exocortex/workspace.yaml` |
| `workspace_id → path` | locator local fora do Acervo |
| Projeção por microverso | registro reverso no Acervo, sem paths |
| Contexto e memória | Acervo/microversos |
| Promoção | controle semântico do Acervo |

O workspace é superfície operacional. O microverso fornece contexto. O Acervo preserva memória promovida e não mantém a árvore do projeto.

## Invariantes

1. `.exocortex/workspace.yaml` é o único arquivo contratual dentro da árvore do workspace. Locator e registro reverso são estado contratual da instalação e projeção do Acervo; não pertencem ao workspace do usuário.
2. Status `proposed | active | archived` é descritivo; não autoriza nem bloqueia ações.
3. `workspacectl` não executa comandos do projeto e não promove memória.
4. Descoberta, validação, registro, resolução e mudança de status não alteram o payload fora de `.exocortex/`.
5. Paths absolutos existem somente no locator local.
6. O registro do Acervo não contém paths, secrets, comandos ou configuração executável.
7. Não há scan automático, backfill, manifesto inferido ou migração do legado.
8. Working source e deliverable ficam no workspace. `_artifacts` recebe apenas snapshot institucional explícito.
9. Operações externas continuam Draft-First.
10. Fresh, existing e rerun preservam estado vivo; rollback de versão não apaga dados.

## Segurança mínima

A V1 usa YAML estrito, rejeita chaves duplicadas, anchors, aliases, merge keys e campos desconhecidos, valida secrets nos campos textuais e não segue `.exocortex` ou manifesto quando forem symlinks. Paths recebidos são resolvidos a partir do `cwd`; apenas o path real absoluto entra no locator. Escritas de estado usam arquivo temporário no mesmo diretório, `fsync`, replace atômico e lock curto para read-modify-write.

Esses controles protegem o write-set local. Não criam lifecycle transacional, receipts de negócio ou autorização forte de tarefa.

## Installer v2

A implementação canônica integra um estágio obrigatório `workspaces` em `scripts/exocortex_install.py`, com verificação em `scripts/verify_exocortex_install.py`, persistência de `EXOCORTEX_WORKSPACES_HOME`, paths no `install-state.json` e testes fresh/existing/rerun.

`setup.sh` é wrapper. O mapa histórico que tratava scripts legados como orquestrador está supersedido.

## Compatibilidade

`_tasks`, `_routines`, `_automations`, `_inbox`, `_artifacts` e o `workspaces.json` da WebUI continuam legíveis e não são migrados. “WebUI Space”, “Exocórtex Home/Cockpit” e “workspace de projeto” são conceitos distintos.

## Fora da V1

- MCP de workspace;
- `workspacectl promote`;
- receipts, event store, revisions e nonces de lifecycle;
- estados `paused` ou `detached`;
- `.wspkg` e import Git especializado;
- scaffold universal;
- migração automática do legado;
- execução de projeto pelo harness;
- autorização forte de tarefa.

## Consequências

O sistema ganha uma fronteira verificável entre ambiente operacional e memória durável. O custo é manter locator e registro reverso coerentes. A V1 assume uma instalação local e usa locks curtos apenas para integridade de arquivo.

## Gate de aceite

A ADR pode mudar para **Accepted** quando:

- schema e invariantes tiverem testes determinísticos;
- Installer v2 cobrir fresh/existing/rerun;
- runtime instalado não carregar o DRAFT experimental;
- skills comportamentais permitirem trabalho no workspace sem copiar o projeto para o Acervo;
- revisão independente confirmar ausência de controle rejeitado.
