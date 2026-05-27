---
name: acervo-manager
description: "Skill unificada do Acervo Cognitivo. Lê, escreve, busca e gerencia conhecimento nas 4 camadas (macro/global/micro/shared) com isolamento de contexto."
version: 2.0.0
author: Exocórtex
metadata:
  hermes:
    tags: [exocortex, acervo, knowledge, wiki, memory, nature, search, scope]
    category: exocortex
    related_skills: [llm-wiki, exocortex-new-microverso]
    replaces: [nature-contexto, nature-conhecimento, nature-instrucao, nature-persona, nature-processo, nature-ferramenta, nature-reflexao, exocortex-search]
---

# Acervo Manager

Skill unificada para operar sobre o Acervo Cognitivo do Exocórtex.
Substitui as 7 Nature skills individuais e `exocortex-search` (ADR-005).

As 7 Natures (contexto, conhecimento, instrucoes, persona, processos, ferramentas, reflexoes)
são **classificação de dados**, não comportamentos distintos. Esta skill implementa a mecânica
comum: ler, escrever, buscar e promover — a semântica de cada Nature é definida pelo SCHEMA
e frontmatter dos próprios arquivos.

## When This Skill Activates

Ativar quando:
- O executivo pergunta sobre fatos, dados, regras, processos ou ferramentas de um domínio
- Uma tarefa precisa ler ou escrever no Acervo Cognitivo
- O agente precisa buscar informação em múltiplos Microversos
- Uma Nature precisa ser promovida (arquivo → diretório)
- O agente precisa resolver scope de acesso entre Microversos

## Acervo Location

```
ACERVO="${HERMES_HOME:-$HOME/.hermes}/acervo"
```

## Architecture: 4 Layers

```
acervo/
├── macro/          # Layer 1: Identidade (FLAT — sempre carregado)
├── global/         # Layer 2: Operação Universal (WIKI — index no boot)
├── micro/{slug}/   # Layer 3: Domínios Isolados (WIKI — por scope)
└── shared/         # Layer 4: Ponte Cross-domain
```

Detalhes completos em `acervo/README.md`.

## Resuming (CRITICAL — do this every session)

No boot de cada sessão:

① **Ler `macro/*`** — soul.md, valores.md, estilo.md (inteiros, ~100 linhas total)
② **Ler `global/index.md`** — catálogo de regras/processos/tools universais
③ **NÃO carregar** micro/ nem shared/ até que uma tarefa defina o scope

```bash
cat "$ACERVO/macro/soul.md"
cat "$ACERVO/macro/valores.md"
cat "$ACERVO/macro/estilo.md"
cat "$ACERVO/global/index.md"
```

### Design System (Sob Demanda)

- `global/DESIGN.md` **NÃO** é carregado no boot (economia de contexto)
- Carregado quando: tarefa demanda output visual, `exocortex-design-system` solicita, ou `taste-skill` precisa validar
- Override por microverso: `micro/{slug}/DESIGN.md` (opcional, apenas deltas)
- Cascade: global = base, micro override vence. Skill `exocortex-design-system` resolve merge.

---

## Operation: READ

Ler conteúdo de qualquer Nature em qualquer camada.

### Procedure

1. **Resolver camada:**
   - Identidade? → `macro/{file}.md` (read direto)
   - Universal? → `global/{nature}.md` ou `global/{nature}/`
   - Domínio específico? → `micro/{slug}/{nature}.md` ou `micro/{slug}/{nature}/`

2. **Verificar scope** (se lendo de micro/):
   - Tarefa tem `scope.deny`? → Executar [SCOPE](#operation-scope)
   - Microverso bloqueado? → PARAR. Declarar: "Acesso ao domínio {slug} não permitido neste scope."

3. **Detectar formato (lógica dual):**

   ```
   IF path é arquivo .md:
     → read_file direto (conteúdo inteiro)
   ELIF path é diretório:
     → ler {nature}/_index.md (catálogo)
     → identificar página relevante pela query
     → ler página específica
   ```

4. **Citar fonte:** Toda informação apresentada deve indicar origem:
   `[Acervo: {camada}/{slug ou nature}]`

5. **Se não encontrou:** Declarar honestamente:
   "Não tenho essa informação no acervo. Posso pesquisar externamente?"

### Verification

- [ ] Informação apresentada existe no acervo (nunca fabricar)
- [ ] Fonte citada na resposta
- [ ] Dados com frontmatter `updated` antigo sinalizados como potencialmente desatualizados

---

## Operation: WRITE

Escrever conteúdo no Acervo com Filtro de Domínio.

### Procedure

1. **Filtro de Domínio (OBRIGATÓRIO antes de qualquer escrita):**

   ```
   ANTES de escrever, classificar o conteúdo:

   1. Verificar scope da tarefa → Microverso bloqueado? → NÃO escrever
   2. Conteúdo é ESPECÍFICO deste domínio?
      → SIM → escrever em micro/{slug}/{nature}
   3. É cross-domain (envolve 2+ Microversos)?
      → SIM → shared/cross-refs/ + ponteiro (1 linha) em cada micro
   4. Pertence a outro Microverso?
      → SIM → escrever lá (se scope permitir)
   5. É universal (vale para TODO contexto)?
      → SIM → escrever em global/{nature}
   6. Nenhum dos acima?
      → DESCARTAR
   ```

2. **Formato de escrita:**
   - Se Nature é arquivo → append ao arquivo existente
   - Se Nature é diretório → criar nova página wiki com frontmatter
   - Frontmatter YAML obrigatório em toda página nova:
     ```yaml
     ---
     title: Título Descritivo
     created: YYYY-MM-DD
     updated: YYYY-MM-DD
     nature: {nature}
     type: {fact|rule|workflow|tool|profile|lesson|context}
     tags: [from SCHEMA taxonomy]
     sources: [raw/source se aplicável]
     confidence: {high|medium|low}
     ---
     ```

3. **Logar operação** em `log.md` do escopo correspondente:
   - Escrita em micro/ → `micro/{slug}/log.md`
   - Escrita em global/ → `global/log.md`
   - Escrita em shared/ → `shared/log.md`

4. **Atualizar index.md** se nova página criada.

### Rules

- **NUNCA** copiar conteúdo entre Microversos — usar cross-ref em `shared/`
- **NUNCA** modificar `raw/` em qualquer camada — fontes são imutáveis
- **NUNCA** escrever informação de domínio A em domínio B
- Ponteiro de cross-ref = 1 linha: `> Cross: ver shared/cross-refs/{slug}.md`

### Verification

- [ ] Filtro de Domínio executado (conteúdo está no lugar certo)
- [ ] Frontmatter YAML presente em toda página nova
- [ ] log.md atualizado
- [ ] index.md atualizado (se nova página)
- [ ] Nenhuma duplicação cross-domain

---

## Operation: PROMOTE

Converter Nature de arquivo para diretório quando ultrapassa ~150 linhas.

### Procedure

1. **Detectar candidato:** Após qualquer WRITE, verificar linhas do arquivo:
   ```bash
   wc -l "$ACERVO/micro/{slug}/{nature}.md"
   ```

2. **Se > ~150 linhas:**

   a. Criar diretório: `micro/{slug}/{nature}/`

   b. Extrair seções do arquivo em páginas separadas:
      - Cada `## Heading` vira uma página: `{heading-slug}.md`
      - Cada página recebe frontmatter YAML

   c. Criar `_index.md` com catálogo das páginas

   d. Remover arquivo original `{nature}.md`

   e. Atualizar `micro/{slug}/index.md` (apontar para diretório)

   f. Logar em `micro/{slug}/log.md`:
      ```
      ## [YYYY-MM-DD] promote | {nature} file → directory ({N} pages)
      ```

3. **Split de página wiki:** Se uma página individual > ~200 linhas, dividir em 2+.

### Verification

- [ ] Diretório criado com `_index.md`
- [ ] Todas as seções extraídas como páginas separadas
- [ ] Arquivo original removido
- [ ] index.md do Microverso atualizado
- [ ] log.md registra a promoção

---

## Operation: SEARCH

Buscar informação nas 4 camadas com prioridade.

### Procedure

1. **Resolver scope:** Quais Microversos estão acessíveis? (ver [SCOPE](#operation-scope))

2. **Buscar em ordem de prioridade:**

   ```
   Prioridade 1: micro/{slug-ativo}/   ← mais específico
   Prioridade 2: global/               ← regras/processos universais
   Prioridade 3: shared/cross-refs/    ← referências cruzadas
   Prioridade 4: outros micro/ (se no scope)
   ```

3. **Mecânica de busca (por camada):**
   - Ler `index.md` → identificar páginas candidatas por título/tags
   - Se Nature é arquivo → grep no conteúdo
   - Se Nature é diretório → grep em `_index.md` → ler página match
   - Usar frontmatter `tags` para narrowing

4. **Retornar resultados com metadados:**
   ```
   [Acervo: micro/cliente-acme/conhecimento] Resultado aqui
   [Acervo: global/instrucoes] Regra universal aqui
   ```

5. **Se nada encontrado:** Declarar e oferecer busca externa.

### Verification

- [ ] Scope verificado antes da busca
- [ ] Resultados indicam camada de origem
- [ ] Prioridade respeitada (micro > global > shared)

---

## Operation: SCOPE

Resolver firewall de acesso para uma tarefa.

### Procedure

1. **Ler `shared/groups.md`** para obter aliases:
   - `ALL` → listar todos os diretórios em `micro/` (exceto `_template`)
   - `CLIENTS` → filtrar por SCHEMA.md `type: client`
   - `PROJECTS` → filtrar por SCHEMA.md `type: project`
   - Grupos custom → resolver membros

2. **Aplicar deny-list:**
   ```
   Para cada Microverso:
     1. Está em deny? → marcado como BLOQUEADO
     2. Está em allow? → DESBLOQUEADO (override)
     3. Resultado: allow SEMPRE vence deny
   ```

3. **Se nenhum scope definido:** Tudo acessível (padrão aberto).

4. **Retornar lista de Microversos acessíveis.**

### Exemplos

```yaml
# SÓ cliente ACME
scope: { deny: [ALL], allow: [cliente-acme] }
→ Acessível: [cliente-acme]

# Bloqueia clientes, permite projetos
scope: { deny: [CLIENTS] }
→ Acessível: [todos os projects + domains + roles]

# Tudo aberto (default)
scope: {}
→ Acessível: [todos]
```

---

## Natures Reference

As 7 Natures são classificação de dados. Semântica de cada uma:

| Nature | Conteúdo | Quando ler | Quando escrever |
|---|---|---|---|
| `contexto` | Situação atual, prioridades, stakeholders | Início de tarefa em domínio | Mudança de cenário |
| `conhecimento` | Fatos, métricas, referências | Pergunta factual | Novo dado confirmado |
| `instrucoes` | Regras condicionais (QUANDO/ENTÃO) | Antes de ações no domínio | Nova regra do executivo |
| `persona` | Tom, vocabulário, estilo | Antes de redigir para stakeholder | Ajuste de comunicação |
| `processos` | Workflows, SOPs | Tarefa recorrente | Novo workflow aprovado |
| `ferramentas` | MCPs, APIs, integrações | Tarefa que requer tool | Nova integração |
| `reflexoes` | Lições aprendidas | Início de tarefa similar | Após incidente/aprendizado |

---

## Archiving

Conteúdo supersedido não é deletado. Procedimento:

1. Mover página wiki para `_archive/{nature}/` (ou `_archive/` na raiz do escopo)
2. Remover da `index.md`
3. Substituir wikilinks `[[page]]` por texto plain + "(archived)"
4. Logar em `log.md`: `## [YYYY-MM-DD] archive | {page} (reason: {motivo})`
5. **raw/ permanece intacto** — fontes são imutáveis

---

## ADRs

- ADR-001: Arquitetura de 4 Camadas
- ADR-002: Isolamento de Contexto (filtro de domínio + firewall)
- ADR-003: Natures Híbridas (arquivo → diretório)
- ADR-004: Integração LLM Wiki
- ADR-005: Consolidação de Skills (7 → 1)
