# Fase P2: Memory — Estrutura Cognitiva

> **Status:** 🟡 Em Reestruturação (alinhamento LLM Wiki)
> **Prompts:** 006–010 (concluídos) + 006B–010B (reestruturação)
> **Checkpoint:** self-test score ≥ 3/5
> **Depende de:** P1 completo
> **ADRs:** ADR-001 (4 Camadas), ADR-002 (Isolamento), ADR-003 (Natures Híbridas), ADR-004 (LLM Wiki)

---

## Objetivo

Criar o Acervo Cognitivo com **4 camadas** (macro, global, micro, shared), integrar mecânicas da LLM Wiki (index, log, raw, frontmatter, wikilinks), e garantir isolamento de contexto entre Microversos.

---

## Prompts Originais (006–010) — Concluídos ✅

Estabeleceram a estrutura base de 3 camadas (macro/micro/shared), 7 Nature skills, skill de criação de Microversos e busca semântica.

---

## Prompts de Reestruturação (006B–010B) — Pendentes

### Prompt 006B — Reestruturar para 4 Camadas + Wiki

Atualizar estrutura do Acervo para a arquitetura de 4 camadas com mecânicas wiki:

```
acervo/
├── macro/                      # Camada 1: Identidade (FLAT, sempre carregado)
│   ├── soul.md
│   ├── valores.md
│   └── estilo.md
│
├── global/                     # Camada 2: Operação Universal (WIKI)
│   ├── SCHEMA.md               # Convenções globais
│   ├── index.md                # Catálogo (carregado no boot)
│   ├── log.md                  # Log append-only
│   ├── raw/                    # Fontes brutas universais
│   │   ├── articles/
│   │   ├── documents/
│   │   └── assets/
│   ├── _archive/               # Páginas supersedidas
│   ├── instrucoes.md           # Regras universais
│   ├── processos.md            # Workflows globais
│   ├── ferramentas.md          # Tools de todo contexto
│   ├── conhecimento.md         # Compliance, legal
│   └── reflexoes.md            # Lições transversais
│
├── micro/                      # Camada 3: Domínios Isolados (WIKI)
│   ├── _template/              # Template wiki completo
│   │   ├── SCHEMA.md           # Com regras de isolamento
│   │   ├── index.md
│   │   ├── log.md
│   │   ├── raw/
│   │   ├── _archive/
│   │   └── {7 Nature files}    # Arquivos únicos iniciais
│   └── {slug}/                 # Microverso instanciado
│
└── shared/                     # Camada 4: Ponte Cross-domain
    ├── SCHEMA.md               # Convenções de cross-ref
    ├── index.md                # Catálogo de cross-refs
    ├── log.md                  # Log cross-domain
    ├── glossario.md            # Vocabulário comum
    ├── groups.md               # Grupos de aliases (ALL, CLIENTS, PROJECTS)
    └── cross-refs/             # Referências cruzadas pragmáticas
```

**Validação:** `tree acervo/ -L 2` mostra 4 camadas com wiki structure.

---

### Prompt 007B — Atualizar Nature Skills (Lógica Dual)

Atualizar 7 Nature skills para operar em **modo dual** (arquivo OU diretório):

1. Detectar se Nature é arquivo `.md` ou diretório
2. Arquivo → `read_file` direto
3. Diretório → ler `_index.md`, depois página específica
4. **Filtro de Domínio** antes de qualquer escrita:
   - Conteúdo específico do domínio? → escrever aqui
   - Cross-domain? → shared/cross-refs/
   - Universal? → global/
   - De outro micro? → escrever lá (se scope permitir)
5. Frontmatter YAML obrigatório em toda página wiki criada

**Validação:** Nature skill opera corretamente sobre arquivo E diretório.

---

### Prompt 008B — Firewall de Acesso + Cross-Reference

1. Criar `shared/groups.md` com aliases:
   - `ALL` = todos os Microversos
   - `CLIENTS` = type: client
   - `PROJECTS` = type: project
2. Implementar lógica de scope em tarefas:
   - `deny: [alias]` bloqueia leitura E escrita
   - `allow: [slug]` sobrescreve deny (SEMPRE)
3. Criar template de cross-ref em `shared/cross-refs/`
4. Atualizar `exocortex-new-microverso` para nova estrutura wiki

**Validação:** Tarefa com `deny: [ALL], allow: [X]` acessa SOMENTE X.

---

### Prompt 009B — Atualizar Busca Multi-Camada

Atualizar `exocortex-search` para busca em 4 camadas:

1. **Boot:** Ler `global/index.md` + `micro/{scope}/index.md`
2. **Busca:** grep + index.md + wikilinks + frontmatter
3. **Cross-domain:** Buscar em `shared/` quando resultado parcial
4. **Prioridade:** micro (mais específico) > global > shared

**Validação:** Busca retorna resultados com indicação de camada de origem.

---

### Prompt 010B — P2 Checkpoint (Reestruturação)

Self-test atualizado. Critérios:

1. `acervo/` com 4 camadas (macro, global, micro, shared)
2. `global/` com SCHEMA + index + log + raw + _archive
3. `_template/` com estrutura wiki completa
4. 7 Nature skills com lógica dual (arquivo/diretório)
5. Filtro de Domínio ativo em toda escrita
6. `shared/groups.md` com aliases
7. Busca multi-camada funcional
8. MEMORY.md com log 006B-010B
9. ADRs documentadas em `docs/ADR/`

Se OK → Confirmar avanço para `P3_TOOLS`

---

## Decisões Arquiteturais

| ADR | Decisão |
|---|---|
| [ADR-001](../../docs/ADR/ADR-001-four-layer-acervo.md) | 4 camadas: macro (flat) + global (wiki) + micro (wiki isolado) + shared (ponte) |
| [ADR-002](../../docs/ADR/ADR-002-context-isolation.md) | Isolamento via filtro de domínio + deny-list com aliases, allow > deny |
| [ADR-003](../../docs/ADR/ADR-003-hybrid-natures.md) | Natures começam arquivo, promovem para dir em ~150 linhas |
| [ADR-004](../../docs/ADR/ADR-004-llm-wiki-alignment.md) | Mecânicas da LLM Wiki + ontologia das 7 Natures |

---

## Próximo

Após P2 (reestruturação) → `P3_TOOLS.md`
