# Fase P2: Memory — Estrutura Cognitiva

> **Status:** ✅ Completa (2026-05-26, incl. reestruturação wiki)
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

## Prompts de Reestruturação (006B–010B) — Concluídos ✅

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

### Prompt 007B — Criar Skill `acervo-manager` (substitui 7 Nature skills + search)

> ADR-005: As 7 Nature skills tinham procedimento idêntico (ler arquivo do acervo).
> Consolidadas em 1 skill unificada. Natures são classificação de dados, não comportamentos.

Criar skill `acervo-manager` com as seguintes operações:

1. **read** — Ler Nature de qualquer camada (macro/global/micro)
   - Detectar se Nature é arquivo `.md` ou diretório
   - Arquivo → `read_file` direto
   - Diretório → ler `_index.md`, depois página específica
2. **write** — Escrever com Filtro de Domínio:
   - Conteúdo específico do domínio? → micro/{slug}/{nature}
   - Cross-domain? → shared/cross-refs/
   - Universal? → global/{nature}
   - De outro micro? → escrever lá (se scope permitir)
   - Frontmatter YAML obrigatório em toda página wiki criada
3. **promote** — Detectar Nature > ~150 linhas → converter arquivo para diretório
4. **search** — Busca em 4 camadas (micro > global > shared)
5. **scope** — Resolver firewall deny/allow com aliases de `shared/groups.md`

Remover 7 skills obsoletas: `nature-contexto`, `nature-conhecimento`, `nature-instrucao`,
`nature-persona`, `nature-processo`, `nature-ferramenta`, `nature-reflexao`.
Remover `exocortex-search` (absorvida).

**Validação:** `acervo-manager` opera sobre arquivo E diretório em qualquer camada.

---

### Prompt 008B — Atualizar `exocortex-new-microverso` + Cross-Reference

1. Atualizar `exocortex-new-microverso` para gerar estrutura wiki completa:
   - SCHEMA.md, index.md, log.md, raw/, _archive/ + 7 Nature files com frontmatter
   - Substituir placeholders em SCHEMA.md (domain, type, description)
   - Registrar tipo (client/project/domain/role) para resolução de aliases
2. Criar template de cross-ref em `shared/cross-refs/`

**Validação:** Novo Microverso tem estrutura wiki completa + SCHEMA preenchido.

---

### Prompt 009B — Integração e Smoke Test

Testar `acervo-manager` end-to-end:

1. **Criar** Microverso de teste via `exocortex-new-microverso`
2. **Write:** Escrever conteúdo em 3 Natures distintas via `acervo-manager`
3. **Read:** Ler de volta via `acervo-manager` (validar lógica dual)
4. **Search:** Buscar em 4 camadas (micro > global > shared)
5. **Scope:** Testar deny/allow com aliases
6. **Cleanup:** Remover Microverso de teste

**Validação:** Todas as operações (read/write/search/scope) funcionais.

---

### Prompt 010B — P2 Checkpoint (Reestruturação)

Self-test atualizado. Critérios:

1. `acervo/` com 4 camadas (macro, global, micro, shared)
2. `global/` com SCHEMA + index + log + raw + _archive
3. `_template/` com estrutura wiki completa (SCHEMA + index + log + raw + 7 Natures)
4. `acervo-manager` funcional (read/write/promote/search/scope)
5. 7 Nature skills antigas removidas + `exocortex-search` removida
6. Filtro de Domínio ativo em toda escrita via `acervo-manager`
7. `shared/groups.md` com aliases (ALL, CLIENTS, PROJECTS)
8. `exocortex-new-microverso` gera estrutura wiki completa
9. MEMORY.md com log 006B-010B
10. ADRs 001-005 documentadas em `docs/ADR/`

Se OK → Confirmar avanço para `P3_TOOLS`

---

## Decisões Arquiteturais

| ADR | Decisão |
|---|---|
| [ADR-001](../../docs/ADR/ADR-001-four-layer-acervo.md) | 4 camadas: macro (flat) + global (wiki) + micro (wiki isolado) + shared (ponte) |
| [ADR-002](../../docs/ADR/ADR-002-context-isolation.md) | Isolamento via filtro de domínio + deny-list com aliases, allow > deny |
| [ADR-003](../../docs/ADR/ADR-003-hybrid-natures.md) | Natures começam arquivo, promovem para dir em ~150 linhas |
| [ADR-004](../../docs/ADR/ADR-004-llm-wiki-alignment.md) | Mecânicas da LLM Wiki + ontologia das 7 Natures |
| [ADR-005](../../docs/ADR/ADR-005-consolidate-nature-skills.md) | 7 Nature skills → 1 `acervo-manager` (Natures são dados, não comportamentos) |

---

## Próximo

Após P2 (reestruturação) → `P3_TOOLS.md`
