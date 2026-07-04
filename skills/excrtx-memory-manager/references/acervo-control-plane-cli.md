# Acervo Control Plane — CLI (`acervoctl`)

Referência operacional curta da superfície local oficial para mutações semânticas do
Acervo (ADR-022 — `acervo/micro/exocortex-dev/decisions/adr-022-acervo-mcp-control-plane.md`).

Modelo: **filesystem = verdade física; core semântico (`scripts/acervo_semantic_core.py`) =
verdade operacional; CLI e MCP (`scripts/acervo_mcp_server.py`) são superfícies finas sobre o
mesmo core.** Qualquer tool futura do MCP deve ter equivalente local nesta CLI.

## Invocação

```bash
python3 scripts/acervoctl.py <comando> [opções]
```

- Toda saída é **JSON** (indentado, `ensure_ascii=False`) com campo `ok`.
- Sucesso → `ok: true`, exit 0. Erro → `{"ok": false, "error": "..."}`, exit 1.
- `--acervo-root` é opcional nos comandos que o aceitam; quando omitido, o core resolve a raiz do Acervo.

## Comandos

### `list-microversos` — lista microversos disponíveis

```bash
python3 scripts/acervoctl.py list-microversos [--acervo-root PATH]
```

Retorna `{ok, microversos: [...], count}`.

### `search` — busca simples em markdown do Acervo

```bash
python3 scripts/acervoctl.py search --query "texto" [--limit 20] [--acervo-root PATH]
```

Retorna `{ok, query, count, matches}`.

### `prepare-write` — prepara uma mutação semântica (fase 1 de 2)

```bash
python3 scripts/acervoctl.py prepare-write \
  --microverso <slug> --nature <nature> --title "Título" \
  [--filename nome.md] [--active-microverso <slug>] \
  [--receipt-out receipt.json] [--acervo-root PATH]
```

- Resolve destino, valida escopo (scope guard) e monta o **receipt** da mutação.
- `--filename` sobrescreve o nome derivado de `slugify(title)`.
- `--active-microverso` default é o próprio `--microverso`.
- `--receipt-out` grava o receipt JSON em arquivo para o `commit-write`.

### `commit-write` — efetiva uma mutação preparada (fase 2 de 2)

```bash
python3 scripts/acervoctl.py commit-write \
  --receipt receipt.json \
  --content-file corpo.md \
  --description "descrição para o log" \
  [--entry-type CREATED] [--class-name volátil]
```

- `--receipt` aceita caminho de arquivo **ou** JSON inline.
- Conteúdo: `--content-file` (arquivo markdown) ou `--content` (inline) — um dos dois é obrigatório.
- `--entry-type` default `CREATED`; `--class-name` default `volátil` (`perene` | `volátil`).
- O commit grava no path final, revalida frontmatter, atualiza `_meta/index.md` e
  `_meta/log.md`, e retorna receipt verificável.

### `validate-frontmatter` — valida frontmatter de um arquivo

```bash
python3 scripts/acervoctl.py validate-frontmatter --path <arquivo.md>
```

### `export-microverso` — empacota um microverso

```bash
python3 scripts/acervoctl.py export-microverso --slug <slug> --out <dir> [--tar] [--acervo-root PATH]
```

## Quando usar (regra da skill)

- **Agentes/automações** fazendo mutação semântica canônica → preferir `prepare-write` + `commit-write` (nunca `write_file` direto).
- **Humano, infra e manutenção corretiva** → escrita direta em arquivo continua permitida.
- Racional completo, invariantes e superfície MCP: ADR-022.
