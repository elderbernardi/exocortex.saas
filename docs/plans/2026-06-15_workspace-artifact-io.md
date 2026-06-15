# Workspace de Input/Output de Artefatos — Web UI

**Data:** 2026-06-15
**Status:** planejamento
**Iniciativa:** Adaptar o workspace da Web UI (nesquena/hermes-webui, MIT) para gerenciar artefatos Exocórtex como cidadãos de primeira classe — visualização, edição, download, publicação no Drive — e para detectar arquivos depositados no inbox como input para o agente.

---

## Diagnóstico Atual

A Web UI tem um workspace funcional (tree view, preview, upload, drag-and-drop, git badges) mas genérico. Ele não reconhece:

- A estrutura de pacotes de artefato (`_artifacts/items/{id}/` com `manifest.json`, `source/`, `exports/`, `receipts/`)
- O conceito de inbox (`_inbox/`) como zona de intake
- Status de artefato (draft/ready/published/failed)
- Pipeline de publicação (Google Drive)

Além disso, o repositório local **não é um fork**: `origin` aponta direto para `nesquena/hermes-webui`. Já temos 5 arquivos modificados localmente (skin EXCRTX). Isso não escala para 7+ camadas de modificação adicionais.

---

## Fases

### Fase 0 — Fork e Versionamento (PRÉ-REQUISITO)

**Objetivo:** Estabelecer fork versionado com estratégia de rebase, catálogo de modificações documentado e automação de atualização — antes de qualquer nova modificação.

**Entregas:**
- Fork `elderbernardi/hermes-webui` no GitHub
- Remotes: `origin` → fork, `upstream` → `nesquena/hermes-webui`
- Branch `exocortex/stable` com modificações atuais consolidadas como commits limpos
- Arquivo `EXOCRTX_MODIFICATIONS.md` catalogando cada modificação (arquivo, propósito, versão base)
- Comando `ctl.sh update` para fetch + rebase + test + restart (ou rollback)
- Todas as modificações permanecem no fork — sem PRs upstream (divergência arquitetural elevada)

### Fase 1 — Input/Output de Alta Alavancagem

Três camadas de baixa complexidade, alto impacto, sem dependências entre si.

**1a. Inbox como conceito de primeira classe**
- Backend: `GET /api/inbox/status`, `POST /api/inbox/move`, ordenação por `mtime` decrescente
- Frontend: badge numérico no tree, tooltip, ação "Mover para microverso"
- **Governança:** mover arquivo do inbox para microverso requer confirmação explícita do usuário (diálogo de confirmação com destino) ou ordem direta — nunca move automático
- Arquivos: `api/workspace.py`, `ui.js`, `workspace.js`, `boot.js`, `style.css`

**1b. Download de arquivos**
- Backend: `GET /api/file/download?path=...`, `GET /api/artifact/zip?id=...`
- Frontend: botão ⬇ no painel de preview, "Baixar ZIP" para diretórios de artefato
- Arquivos: `api/workspace.py`, `workspace.js`

**1c. Auto-preenchimento do prompt ao inserir arquivo**
- Frontend: ao concluir upload no inbox, injetar no campo de chat: "Insira o seguinte no contexto: arquivo 'nome' foi adicionado à caixa de entrada."
- Toast de confirmação: "📎 precarregado no prompt"
- Arquivos: `workspace.js`, `messages.js`, `style.css`

### Fase 2 — Edição e Visualização de Artefatos

**2a. Edição inline de Markdown**
- Frontend: toggle preview/edição em arquivos `.md`, textarea com conteúdo raw, botão Salvar
- Backend: `POST /api/file/save` — recebe `{path, content}`, escreve, retorna hash SHA-256
- Arquivos: `api/workspace.py`, `workspace.js`, `style.css`

**2b. Status badges de artefato**
- Backend: `list_dir` lê `manifest.json` de cada subdiretório sob `_artifacts/items/` e retorna `status` e `title`
- Frontend: badges coloridos (draft=cinza, ready=azul, published=verde, failed=vermelho)
- Arquivos: `api/workspace.py`, `ui.js`, `style.css`

### Fase 3 — Publicação

**3. Publicar no Drive one-click**
- Backend: `POST /api/artifact/publish` → chama `artifact_publish.py`, `GET /api/artifact/receipt`
- Frontend: ação de contexto "Publicar no Drive", spinner, feedback com link
- Arquivos: `api/workspace.py`, `workspace.js`

### Fase 4 — Agente

**4. Comando explícito de verificação de inbox**
- Skill `excrtx-memory-intake`: trigger "verifique o inbox" lista, classifica, propõe destino
- Prompt "inseri arquivo X no inbox": confirma existência, extrai texto, processa conforme tipo
- Sem polling automático — sempre explícito
- Arquivos: `excrtx-memory-intake/SKILL.md`

---

## Grafo de Dependências

```
Fase 0 (Fork) ───┬──► Fase 1a (Inbox)
                  ├──► Fase 1b (Download)
                  ├──► Fase 1c (Auto-preenchimento)
                  │
                  ├──► Fase 2a (Edição inline) ── (independente)
                  ├──► Fase 2b (Badges) ───────── (independente)
                  │
                  ├──► Fase 3 (Drive) ──────────── (independente, requer Fase 2b para UX)
                  │
                  └──► Fase 4 (Agente inbox) ───── (independente)
```

Fase 0 bloqueia todas as demais (precisamos do fork antes de modificar).

Demais fases são majoritariamente independentes entre si. A Fase 3 se beneficia da Fase 2b (badges dão feedback visual de status pós-publicação) mas não é bloqueada por ela.

---

## Estratégia de Fork (Fase 0 em detalhe)

### Estrutura de branches

```
elderbernardi/hermes-webui
├── upstream/master          (track nesquena/hermes-webui master)
├── exocortex/stable         (produção — o que roda na porta 8787)
├── feature/inbox-badges     (por camada de modificação)
├── feature/inline-edit
├── feature/download
├── feature/artifact-badges
├── feature/drive-publish
├── feature/auto-prefill
└── feature/inbox-command
```

### Catálogo de modificações

Arquivo `EXOCRTX_MODIFICATIONS.md` na raiz do fork. Cada entrada:

```markdown
## MOD-XXX: Título (vX.Y.Z base)
- **Arquivos:** path/arquivo.py, static/arquivo.js
- **Tipo:** backend | frontend | CSS
- **Propósito:** o que faz e por que
- **Reaplicar se:** condição que indica que o upstream mexeu na mesma área
- **Conflito provável:** arquivos com maior probabilidade de conflito em rebase
```

### Workflow de atualização

```bash
git fetch upstream
git checkout exocortex/stable
git rebase upstream/master
# resolver conflitos guiado pelo EXOCRTX_MODIFICATIONS.md
pytest tests/ -x -q
./ctl.sh start && curl -s http://127.0.0.1:8787/health
# Se falhar: git rebase --abort && ./ctl.sh restart
```

### Automação: `ctl.sh update`

Estender `ctl.sh` com subcomando `update`:
1. fetch upstream
2. mostrar diff stat
3. pedir confirmação
4. rebase + test + restart (se passar) ou rollback (se falhar)

### Política de modificação

Todas as modificações permanecem no fork. A divergência arquitetural (workspace orientado a artefatos vs file browser genérico) é grande demais para PRs upstream — o upstream provavelmente rejeitaria ou exigiria redesign completo. O custo de manter patches localmente é compensado pelo catálogo `EXOCRTX_MODIFICATIONS.md` + `ctl.sh update`.

---

## Definition of Done

- [ ] Fork criado e remotes configurados
- [ ] `exocortex/stable` rodando na porta 8787 com todas as modificações
- [ ] `EXOCRTX_MODIFICATIONS.md` atualizado para cada modificação
- [ ] `ctl.sh update` funcional (fetch + rebase + test + restart)
- [ ] Inbox com badge numérico e ação "Mover para microverso"
- [ ] Download de arquivos e ZIP de artefatos funcional
- [ ] Upload no inbox → auto-preenchimento do prompt
- [ ] Edição inline de .md com toggle preview/edição
- [ ] Badges de status em diretórios de artefato
- [ ] Publicação one-click no Drive com feedback inline
- [ ] Comando "verifique o inbox" processa e classifica arquivos
- [ ] Prompt com "inseri arquivo X" detecta e processa

---

## Notas para Execução

- **Fork primeiro, código depois.** Nenhuma modificação nova antes da Fase 0 concluída.
- **Testes upstream são aliados.** Rodar `pytest tests/ -x -q` a cada modificação para garantir que não quebramos funcionalidade existente.
- **Rebase é o mecanismo de atualização.** Sem PRs upstream — toda modificação vive no fork. O `EXOCRTX_MODIFICATIONS.md` é o mapa de conflitos; o `ctl.sh update` é o executor.
- **Commits atômicos.** Um commit por arquivo ou por funcionalidade — facilita rebase e `git bisect`.
