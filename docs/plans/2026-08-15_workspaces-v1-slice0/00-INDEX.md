# Workspaces V1 — Slice 0 corretivo

## Estado

- **Base:** `origin/main@1268365230f646955deec95b2355b70b7fa1fc6a`
- **Branch:** `feat/workspaces-v1-slice0`
- **Status:** em execução
- **Escopo aprovado:** remapear Installer v2, canonicalizar ADR/contrato, definir schema e segurança mínima, criar testes RED e implementação mínima correspondente.

## Por que este Slice 0 existe

O planejamento local de 2026-08-05 aprovou a arquitetura mínima, mas apontava parte do provisionamento para scripts legados. `origin/main` já usa o Installer v2 como orquestrador. Este slice reconcilia o plano com o repo vivo antes de expandir a CLI.

## Fontes normativas do slice

1. `docs/ADR/ADR-026-workspaces-v1.md`
2. `docs/workspaces/WORKSPACE-SPEC-v1.md`
3. `acervo/global/contracts/workspace-boundary-v1.md`

Auditorias históricas do pacote local são evidência, não especificação ativa.

## Mapa do Installer v2

| Superfície | Delta do Slice 0/4 |
|---|---|
| `scripts/exocortex_install.py` | estágio obrigatório `workspaces`; raiz configurável; paths no estado |
| `scripts/verify_exocortex_install.py` | verificar core, wrapper, locator, registry e configuração |
| `setup/capabilities.json` | não criar capability `workspaces`; o stage deve selecionar, antes de mutar, um Python ≥3.11 que importe `yaml`, sem assumir o primeiro `python3` do `PATH` |
| `scripts/persist-env.sh` | capturar `EXOCORTEX_WORKSPACES_HOME` |
| `setup/step-04-install-acervo.sh` | excluir registry do rsync; seed somente se ausente |
| `install-state.json` | registrar `workspaces_home`, locator e registry |
| `tests/test_installer_v2.py` | ordem/seleção do estágio e paths reportados |
| testes de provisionamento | fresh, existing, rerun e preservação de hash |

O stage funcional completo pertence ao Slice 4. O Slice 0 fixa contrato e testes para impedir implementação no orquestrador errado.

## Sequência

### Slice 0 — contrato e primeira vertical

1. ADR e contrato DRAFT.
2. Schema estrito de manifesto.
3. Segurança mínima de YAML, fields, secrets e symlink.
4. Primeiro teste RED; implementação mínima GREEN.
5. Baseline focada e revisão independente.

### Slice 1 — validação read-only

`workspacectl validate`, sem locator, registry ou escrita.

### Slice 2 — resolução e registro

Locator/registry, `register`, `resolve`, `list` e `reconcile`.

### Slice 3 — criação e status

`init` e `set-status`, com ordem manifesto → locator → projeção e recuperação não destrutiva.

### Slice 4 — rollout

Installer v2, wrappers, env, skills, artifacts, paridade source/runtime e limpeza do DRAFT experimental.

## Fora do programa V1

MCP de workspace, promoção pela CLI, receipts de lifecycle, event store, estados extras, `.wspkg`, import Git especializado, scaffold universal, migração automática e autorização forte de tarefa.

## Evidência TDD do Slice 0

- RED inicial: `tests/test_workspace_schema.py` falhou porque `scripts/workspace_schema.py` ainda não existia.
- REDs incrementais foram observados antes das correções de campos desconhecidos, duplicatas YAML, composição YAML, secrets, symlinks, escrita atômica e tipos hostis.
- RED pós-revisão independente: 5/5 testes adversariais falharam para booleanos YAML 1.2, troca concorrente do root, `fsync` pós-replace e cleanup secundário.
- RED de hardening adicional: 2/2 testes falharam quando o root mudou depois da abertura dos descriptors; a correção passou a revalidar `device/inode` antes e depois das etapas críticas.
- RED de robustez pós-revisão: 10/12 probes novos falharam para vazamento de conteúdo em erros, limite de bytes/profundidade, paths malformados, `stat`/`fstat`, cleanup sanitizado e `fsync` do root; os dois controles já protegidos permaneceram verdes.
- RED de portabilidade fail-closed: ausência simulada de `O_NOFOLLOW` foi aceita; o gate passou a exigir primitivas POSIX seguras antes do I/O. Um primeiro detector interferiu em fault injection, produziu 3 falhas e foi corrigido para capturar capacidades no carregamento do módulo.
- RED de consistência de saída: `dump_manifest` gerava texto acima de 64 KiB que a leitura subsequente recusaria; o mesmo limite passou a valer antes de qualquer escrita.
- RED da revisão independente final: `resolve_workspace_root()` deixou escapar `PermissionError` com payload durante o `stat` final de diretório; a fronteira agora converte essa falha para `WorkspaceManifestError(code="invalid-workspace-root")` sem encadear o payload.
- RED da revisão de conformidade: 8/8 probes novos falharam para cobertura de secrets em `metadata.id`/slugs, encadeamento de `yaml.YAMLError`/`ValueError` de timestamp com conteúdo, `RepresenterError` cru de subclasse de `str` no dump/write e `cleanup-failed` pós-publicação; as correções aplicaram o gate de secret a todos os campos textuais, o padrão flag (sem `__cause__`/`__context__`), tipo exato de string + wrap de serialização e `partial-failure` quando a publicação já ocorreu.
- GREEN pós-correção: `74 passed` em `tests/test_workspace_schema.py`.

## Gate deste checkpoint

O Slice 0 só fecha com:

- testes do schema vistos falhar antes do código;
- testes focados verdes;
- contrato do Acervo validado;
- diff restrito ao slice;
- revisão independente;
- nenhum push ou mudança no runtime instalado.
