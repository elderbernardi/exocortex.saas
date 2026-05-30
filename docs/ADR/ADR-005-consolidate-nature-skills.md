# ADR-005: Consolidar 7 Nature Skills em 1 Skill Unificada

> **Status:** Aceita
> **Data:** 2026-05-26
> **Decisor:** @elder
> **Contexto:** Sessão PDD P2_MEMORY — revisão de skills durante alinhamento wiki

---

## Contexto

O prompt 007 do PDD original criou 7 skills separadas (`nature-contexto`, `nature-conhecimento`, `nature-instrucao`, `nature-persona`, `nature-processo`, `nature-ferramenta`, `nature-reflexao`), cada uma responsável por ler/escrever o arquivo correspondente no Acervo Cognitivo.

Na revisão para integrar mecânicas wiki (lógica dual arquivo/diretório, filtro de domínio, firewall de acesso), ficou claro que as 7 skills têm o **mesmo procedimento**:

```
1. Identificar Microverso
2. Carregar ~/.hermes/acervo/micro/{slug}/{nature}.md
3. Operar sobre o conteúdo
```

A única diferença entre elas é o nome do arquivo lido. A semântica de cada Nature (o que é contexto vs. conhecimento vs. instrução) já está definida nos SCHEMAs e no frontmatter dos próprios arquivos — não precisa de skills separadas para isso.

## Decisão

**Substituir as 7 Nature skills por 1 skill unificada: `acervo-manager`.**

### O que `acervo-manager` faz

1. **Leitura:** Recebe Microverso + Nature → localiza o artefato (arquivo ou diretório) → carrega conteúdo
2. **Escrita:** Aplica Filtro de Domínio → escreve no local correto → loga em `log.md`
3. **Promoção:** Detecta Nature > ~150 linhas → promove arquivo para diretório
4. **Scope:** Consulta firewall (deny/allow com aliases) antes de qualquer operação

### O que as Natures passam a ser

Natures são uma **classificação de dados**, não comportamentos distintos. Definidas por:
- SCHEMA.md (convenções por camada)
- Frontmatter YAML (`nature: conhecimento`)
- Estrutura de diretórios (arquivo ou diretório com `_index.md`)

### Escopo de `acervo-manager`

| Operação | Descrição |
|---|---|
| `read` | Ler Nature de um Microverso (com lógica dual) |
| `write` | Escrever em Nature com filtro de domínio |
| `promote` | Converter Nature arquivo → diretório |
| `search` | Buscar em 4 camadas (absorve `exocortex-search`) |
| `scope` | Resolver firewall deny/allow (absorve `exocortex-task-scope` planejada) |

## Alternativas Rejeitadas

1. **Manter 7 skills + atualizar cada uma** — Rejeitada porque multiplica manutenção 7x para lógica idêntica (dual mode, filtro, firewall).
2. **Manter 7 skills + skill transversal** — Rejeitada porque cria dependência complexa (7 skills chamando 1 helper) sem benefício sobre consolidação.
3. **Remover skills, deixar só SCHEMA** — Rejeitada porque o agente precisa de um ponto de entrada procedural documentado para operar sobre o acervo.

## Consequências

### Criações
- `acervo-manager` — skill unificada com toda lógica de acervo

### Remoções
- `nature-contexto`, `nature-conhecimento`, `nature-instrucao`, `nature-persona`, `nature-processo`, `nature-ferramenta`, `nature-reflexao` — 7 skills substituídas
- `exocortex-search` — absorvida por `acervo-manager` (operação `search`)
- Não será necessário criar `nature-promote` nem `exocortex-task-scope` como skills separadas

### Atualizações necessárias
- `P2_MEMORY.md` — prompt 007B atualizado
- `PLAN.md` — tabela P2 atualizada
- `plan_wiki_alignment.md` — Fase 2 simplificada
- `MEMORY.md` — decisão logada

## Referências

- Nature skills atuais: `~/.hermes/skills/exocortex/nature-*/SKILL.md`
- ADR-003: Natures Híbridas (mecânica de promoção que entra no acervo-manager)
- ADR-004: LLM Wiki Alignment (mecânicas wiki que a skill unificada implementa)


## Atualização 2026-05-30

ADR-007 atualiza o acervo-manager para operar diretórios funcionais + Natures no frontmatter.
