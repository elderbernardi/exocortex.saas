# ADR-013 — Arquitetura do Acervo v0.4 no Instalador

## Status

Aceita (2026-06-04)

## Contexto

O acervo nos artifacts do instalador (plans/pdd_v2/artifacts/acervo/) usa a estrutura flat v0.3 (arquivos como `conhecimento.md`, `ferramentas.md` na raiz de cada camada). O instalador futuro (setup.sh) já cria diretórios funcionais v0.4 (`knowledge/`, `tools/`, `contracts/`, etc.) no destino.

**Premissa central:** Estamos construindo um **instalador futuro**, não migrando o setup atual. O setup real (~/.hermes/setup.sh) é referência, não destino. O instalador deve refletir a arquitetura desejada (v0.4) desde a origem.

## Decisão

1. **Migrar os templates do acervo nos artifacts** de flat v0.3 para diretórios funcionais v0.4.
2. Os arquivos flat viram `_seed.md` dentro dos diretórios funcionais correspondentes.
3. A mesma estrutura se aplica a `global/`, `micro/_template/` e `shared/`.

### Mapeamento

| Arquivo flat (v0.3) | Diretório funcional (v0.4) | Destino |
|---------------------|---------------------------|---------|
| `conhecimento.md` | `knowledge/` | `knowledge/_seed.md` |
| `ferramentas.md` | `tools/` | `tools/_seed.md` |
| `instrucoes.md` | `contracts/` | `contracts/_seed.md` |
| `processos.md` | `workflows/` | `workflows/_seed.md` |
| `reflexoes.md` | `reflections/` | `reflections/_seed.md` |
| `contexto.md` | `context/` | `context/_seed.md` |
| `persona.md` | `persona/` | `persona/_seed.md` |
| `DESIGN.md` | `_meta/` | `_meta/DESIGN.md` |
| `SCHEMA.md` | `_meta/` | `_meta/SCHEMA.md` |
| `index.md` | `_meta/` | `_meta/index.md` |
| `log.md` | `_meta/` | `_meta/log.md` |

### Diretórios funcionais canônicos v0.4

Cada camada (global, micro, shared) contém:

```
context/        — estado contextual ativo
knowledge/      — conhecimento canônico persistente
contracts/      — contratos e acordos formais
prompts/        — prompts reutilizáveis
skills/         — skills locais ao contexto
workflows/      — processos e procedimentos
tools/          — ferramentas e scripts
templates/      — templates de artefatos
decisions/      — decisões documentadas
reflections/    — reflexões e aprendizados
persona/        — definição de persona do contexto
_meta/          — metadados (SCHEMA, index, log, DESIGN)
raw/            — material bruto não processado
_archive/       — material arquivado
```

## Consequências

- O instalador já distribui a estrutura v0.4 nos templates
- Novos microversos criados por `exocortex-new-microverso` herdam a estrutura v0.4
- Não há dependência do acervo flat v0.3
- Microversos pré-provisionados (ex: Estúdio Criativo) já usam v0.4

## Referências

- ADR-007 — Multifocal Acervo Ontology (conceito original)
- ADR-010 — Layered Deployment
- F01 da curadoria (ontologia v2 como padrão)
