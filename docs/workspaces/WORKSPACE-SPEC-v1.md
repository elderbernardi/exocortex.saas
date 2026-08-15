# Especificação normativa — `excrtx-workspace/v1`

> **Status:** DRAFT do Slice 0. Esta especificação define contrato e segurança; não autoriza execução implícita de projetos.

## 1. Manifesto

Path único interpretado pelo harness:

```text
<workspace>/.exocortex/workspace.yaml
```

```yaml
apiVersion: excrtx-workspace/v1
kind: Workspace
metadata:
  id: ws_example
  created_at: 2026-08-15T00:00:00Z
project:
  title: Projeto Exemplo
  objective: Resultado verificável do projeto.
  status: proposed
  status_changed_at: 2026-08-15T00:00:00Z
  status_reason: Manifesto criado.
cognitive_binding:
  primary_microverso: exocortex-ops
  related_microversos: []
```

### 1.1 Campos

| Campo | Regra |
|---|---|
| `apiVersion` | literal `excrtx-workspace/v1` |
| `kind` | literal `Workspace` |
| `metadata.id` | `^ws_[a-z0-9][a-z0-9-]{2,59}$` |
| `metadata.created_at` | UTC ISO 8601 terminado em `Z` |
| `project.title` | string não vazia; máximo 200 caracteres |
| `project.objective` | string não vazia; máximo 2.000 caracteres |
| `project.status` | `proposed`, `active` ou `archived` |
| `project.status_changed_at` | UTC ISO 8601 terminado em `Z` |
| `project.status_reason` | string não vazia; máximo 500 caracteres |
| `cognitive_binding.primary_microverso` | slug `^[a-z0-9][a-z0-9-]{2,59}$` |
| `cognitive_binding.related_microversos` | array opcional de slugs únicos; não inclui o principal |

Campos desconhecidos falham em qualquer nível. Chaves YAML duplicadas, anchors, aliases e merge keys falham. A leitura segue semântica booleana YAML 1.2: apenas `true` e `false` são booleanos; `yes`, `no`, `on` e `off` permanecem strings. O arquivo tem limite de 64 KiB e profundidade estrutural máxima de 32 níveis; excesso retorna, respectivamente, `manifest-too-large` e `manifest-too-complex` antes da construção do objeto. Erros públicos não reproduzem chaves, valores, snippets YAML nem mensagens do sistema controláveis pelo input, e nenhum erro encadeado transporta conteúdo do input (sem `__cause__` ou `__context__` no diagnóstico público). O manifesto não contém path, comando, hook, runtime, credencial ou valor de secret.

### 1.2 Códigos de erro da leitura e escrita

| Código | Significado |
|---|---|
| `missing` | workspace ou `.exocortex` ausente; nada é recriado |
| `invalid-workspace-root` | root não é diretório ou não pôde ser verificado |
| `invalid-manifest` | YAML inválido ou semântica bloqueada (duplicata, anchor, alias, merge) |
| `manifest-too-large` | manifesto excede 64 KiB |
| `manifest-too-complex` | profundidade estrutural excede 32 níveis ou recursão do parser |
| `secret-detected` | campo textual casa padrão de secret do Acervo |
| `unsafe-path` | symlink, troca concorrente de path ou componente inseguro |
| `unsupported-platform` | plataforma sem primitivas POSIX seguras exigidas |
| `write-failed` | falha antes da publicação |
| `partial-failure` | manifesto publicado, mas finalização ou durabilidade não confirmada; reler antes de repetir |
| `cleanup-failed` | limpeza de temporário/descriptores falhou sem que houvesse publicação |

## 2. Segurança de leitura e escrita

1. O path fornecido pode ser relativo; é resolvido contra o `cwd` e canonicalizado uma vez.
2. Cada componente do path real canonicalizado é aberto, a partir da raiz do sistema, por descritores relativos com `O_DIRECTORY | O_NOFOLLOW`; a identidade `device/inode` do root e de `.exocortex` é revalidada antes e depois das etapas críticas, e troca concorrente falha fechada. Plataforma sem essas primitivas POSIX, `dir_fd`, `follow_symlinks=False` ou `O_CLOEXEC` retorna `unsupported-platform`, sem fallback inseguro.
3. O locator armazena somente o path real absoluto.
4. O root pode ser alcançado por um symlink fornecido pelo usuário, mas todas as operações posteriores usam o path real canonicalizado e descritores já ancorados.
5. `.exocortex` e `workspace.yaml` devem ser diretório/arquivo regulares; symlink é erro.
6. O manifesto resolvido precisa permanecer contido no root canonicalizado.
7. A criação de `.exocortex` é confirmada com `fsync` no root; a escrita do manifesto usa temp no mesmo diretório, flush, `fsync` e `os.replace`.
8. Se `os.replace` concluir e o `fsync` do diretório falhar, o erro é `partial-failure`: o manifesto já está publicado e precisa ser relido antes de repetir. Falha de cleanup não mascara o erro primário e é anexada ao diagnóstico.
9. Locator e registry usam lock curto durante read-modify-write.
10. O diretório do locator usa modo `0700`; o arquivo usa `0600`.
11. Todos os campos textuais — incluindo `metadata.id`, `project.title`, `project.objective`, `project.status_reason`, `cognitive_binding.primary_microverso` e itens de `related_microversos` — são verificados contra os padrões de secret já usados pelo Acervo: OpenAI, GitHub, AWS, Slack, private key e token de bot do Telegram.
12. Validação, resolução e registro nunca executam conteúdo do workspace.

## 3. Identidade e criação

`workspacectl init <slug>` aceita apenas:

```regex
^[a-z0-9][a-z0-9-]{2,59}$
```

O ID é derivado como `ws_<slug>`. Não há `--id` nem normalização implícita.

Sem `--path`, o target é `$EXOCORTEX_WORKSPACES_HOME/<slug>`, com fallback `~/workspace/<slug>`. Com `--path`, o input é resolvido contra o `cwd` e o path real torna-se a localização registrada.

Antes de escrever:

- mesmo ID/path e manifesto válido: idempotente;
- ID registrado em outro path: erro;
- manifesto existente com outro ID: erro;
- manifesto inválido: erro;
- diretório existente sem manifesto: adoção permitida sem alterar o payload;
- diretório ausente: criação permitida.

Antes da primeira escrita, a operação valida argumentos, estado existente, colisões, locator e registro. Falha previsível de preflight produz zero escritas. Manifesto, locator e registro usam replace atômico individual, mas a V1 não promete transação entre raízes.

Ordem de `init`:

```text
criar diretórios ausentes → manifesto → locator → registro reverso
```

`register` escreve locator e depois registro. `reconcile` escreve somente o registro. O registro nunca é escrito antes do locator.

Falha inesperada após alguma etapa retorna `partial-failure`, declara `completed` e `pending` e não desfaz etapas concluídas:

- manifesto escrito e locator pendente: `workspacectl register <path>`;
- locator escrito e registro pendente: `workspacectl reconcile <workspace_id>`.

Não há rollback destrutivo nem receipt persistente. Payload preexistente nunca é removido.

## 4. Locator local

```text
$EXOCORTEX_HOME/.state/workspaces/locators.yaml
```

```yaml
schema: excrtx-workspace-locators/v1
workspaces:
  ws_example:
    path: /home/user/workspace/example
    registered_at: 2026-08-15T00:00:00Z
```

Regras:

- mapa unitário `workspace_id → localização atual`, com cardinalidade máxima de um path por ID;
- cada entrada contém path real absoluto e `registered_at` da operação que estabeleceu o path atual;
- path local nunca entra no Acervo ou em pacote;
- mesmo ID/path é idempotente e preserva `registered_at`;
- relocação exige `register --relocate`, manifesto com mesmo ID e path anterior ausente;
- somente `init` concluído até o registro e `register` alteram o locator;
- chave duplicada, campo desconhecido, schema inválido ou path não absoluto produzem `invalid-locator`;
- manifesto ausente é `missing`, sem recriação;
- não há fallback para registry nem scan automático.

## 5. Registro reverso

```text
$ACERVO/global/_meta/workspaces.yaml
```

```yaml
schema: excrtx-workspace-registry/v1
updated_at: 2026-08-15T00:00:00Z
workspaces:
  ws_example:
    title: Projeto Exemplo
    primary_microverso: exocortex-ops
    related_microversos: []
    status_observed: proposed
    manifest_digest: sha256:...
    reconciled_at: 2026-08-15T00:00:00Z
    health: healthy
```

É projeção derivada, nunca fonte de path, resolução ou descoberta local. Não contém path, histórico, comando, runtime, secret ou permissão. O manifesto vence em divergência. `init`, `register` e `reconcile` são os únicos escritores.

`reconcile <id>` resolve somente pelo locator. Com manifesto válido, atualiza os campos derivados e `health: healthy`. Para `missing` ou `invalid-manifest`, atualiza apenas `health` e `reconciled_at`, preservando descrições anteriores. Registry inválido produz `invalid-registry` e bloqueia somente operações que precisem escrevê-lo; não invalida locator saudável nem impede `resolve` ou `list`.

## 6. Comandos e semântica

| Comando | Escrita |
|---|---|
| `validate [path]` | nenhuma |
| `resolve <id>` | nenhuma; valida que o manifesto atual mantém o ID |
| `list` | nenhuma; enumera o locator e anota saúde pela validação atual |
| `status [path|id]` | nenhuma |
| `register [path]` | locator + registro reverso |
| `reconcile <id>` | registro reverso; resolve somente pelo locator e não recria manifesto |
| `init <slug>` | diretório, manifesto, locator e registro reverso |
| `set-status <status>` | somente manifesto |

`list` enumera todas as entradas de um locator válido, ordenadas por `workspace_id`. Cada entrada recebe diagnóstico `healthy`, `missing`, `invalid-manifest` ou `id-mismatch`; uma entrada ruim não interrompe as demais. Locator inválido falha fechado, sem enumeração parcial apresentada como confiável.

`resolve <id>` consulta somente o locator, exige root disponível, manifesto regular e válido e igualdade entre o ID pedido e `metadata.id`. Em sucesso retorna path real absoluto. Seus erros V1 são `unknown-id`, `missing`, `invalid-manifest`, `id-mismatch` e `invalid-locator`. `ambiguous-id` não existe: uma segunda localização é rejeitada no registro.

Status é descritivo. Nenhum comando concede acesso, executa o projeto, publica, promove memória ou move arquivos do usuário.

## 7. Promoção

Não existe `workspacectl promote`. Promoção usa `acervoctl` ou MCP semântico do Acervo, preservando referência relativa:

```text
workspace://ws_example/docs/decision.md
```

Working source e deliverable permanecem no workspace. Snapshot em `_artifacts` exige publicação ou promoção explícita.

## 8. Installer v2

A feature é obrigatória nos perfis `core` e `full`:

- estágio `workspaces` após `acervo` e antes de `identity`;
- persistência de `EXOCORTEX_WORKSPACES_HOME`;
- `workspacectl` em `$EXOCORTEX_HOME/bin`;
- core em `$EXOCORTEX_HOME/tools/workspaces`;
- stage seleciona antes de mutar um Python ≥3.11 capaz de importar `yaml`, sem confiar no primeiro `python3` do `PATH`;
- locator e registry criados somente se ausentes;
- `global/_meta/workspaces.yaml` excluído do rsync genérico;
- verificação determinística no Installer v2;
- paths registrados em `install-state.json`.

Fresh cria estados vazios. Existing preserva sentinels. Rerun não altera hashes do estado vivo. Rollback de versão remove executáveis gerenciados quando solicitado, mas preserva manifesto, locator e registro.

## 9. Compatibilidade e fora de escopo

`_tasks`, `_routines`, `_automations`, `_inbox`, `_artifacts` e WebUI Spaces permanecem como estão. Não há migração automática.

Fora da V1: MCP de workspace, promoção pela CLI, receipts de lifecycle, event store, estados extras, `.wspkg`, import Git especializado, scaffold universal, migração legada e autorização forte de tarefa.
