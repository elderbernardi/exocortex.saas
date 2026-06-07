# DRAFT — publicação de 3 issues GitHub

Repositório-alvo: `elderbernardi/exocortex.saas`
Origem da evidência: `.dogfood/runs/dogfood-real-p0-20260606-214843/`

## Impacto

Criar 3 issues no GitHub para defeitos reais detectados pelo dogfood conversacional com subinstância Hermes real e probes determinísticos.

Nenhum comando abaixo foi executado. A publicação exige aprovação explícita do executivo após revisão deste DRAFT.

## Labels sugeridas

- `bug`
- `dogfood`
- `exocortex`
- `P0` ou `P1`

Antes de publicar, verificar se as labels existem no repositório. Se faltarem, criar labels ou remover do comando.

```bash
gh label list --repo elderbernardi/exocortex.saas
```

---

## Issue 1 — EX-25 Google Drive

Título:

```text
[Dogfood][EX-25] Google Drive integration não localiza driver google_api.py
```

Prioridade: `P0`

Body:

```markdown
## Contexto

Dogfood conversacional local detectou status FAIL para a feature EX-25: Google Drive integration pre-auth health.

Run de evidência:

`/home/elder/projetos/projetob/exocortex.saas/.dogfood/runs/dogfood-real-p0-20260606-214843/EX-25`

## Resultado observado

O probe de pré-autenticação não encontrou o driver `google_api.py` nos paths esperados.

Evidência do `probe.json`:

```json
{
  "probe": "ex25_google_drive_pre_auth",
  "driver_candidates": [
    "google_api.py",
    "scripts/google_api.py",
    "skills/excrtx-integrate-gdrive/scripts/google_api.py"
  ],
  "driver_found": false,
  "credentials_available": false,
  "py_compile_stderr": "driver not found"
}
```

## Resultado esperado

- A feature deve declarar o path real do driver Google Drive.
- O driver deve existir e compilar antes de qualquer fluxo OAuth.
- Credencial ausente deve ser classificada como BLOCKED, não PASS.
- Driver ausente ou `SyntaxError` antes da autenticação deve ser classificado como FAIL.

## Critérios de aceite

- `./scripts/test-registry.sh dogfood-real-p0` não marca EX-25 como PASS sem evidência positiva de driver.
- O path declarado na feature corresponde a um arquivo real versionado ou a um setup documentado.
- `python -m py_compile <driver>` passa no driver configurado.
- Draft-First permanece preservado: nenhum fluxo Drive executa ação externa sem aprovação explícita.
```

Comando de publicação sugerido:

```bash
gh issue create \
  --repo elderbernardi/exocortex.saas \
  --title "[Dogfood][EX-25] Google Drive integration não localiza driver google_api.py" \
  --body-file /tmp/ex25-dogfood-gdrive.md \
  --label "bug,dogfood,exocortex,P0"
```

---

## Issue 2 — EX-30 Browser Automation

Título:

```text
[Dogfood][EX-30] Browser automation tem contrato de path divergente e uv ausente
```

Prioridade: `P1`

Body:

```markdown
## Contexto

Dogfood conversacional local detectou status FAIL para a feature EX-30: Browser automation dependency and path contract.

Run de evidência:

`/home/elder/projetos/projetob/exocortex.saas/.dogfood/runs/dogfood-real-p0-20260606-214843/EX-30`

## Resultado observado

A feature declara um path/comando que não existe, enquanto o script real existe em outro local. O ambiente também não tem `uv` disponível.

Evidência do `probe.json`:

```json
{
  "probe": "ex30_browser_dependency_path",
  "uv_available": false,
  "actual_script": "skills/excrtx-integrate-browser/scripts/browser-use.sh",
  "actual_script_exists": true,
  "actual_script_executable": true,
  "features_declared_path": ".agent/skills/excrtx-integrate-browser/scripts/excrtx-integrate-browser.sh",
  "features_declared_path_exists": false,
  "path_contract_matches": false
}
```

## Resultado esperado

- `FEATURES.md` deve apontar para o path real da skill ou o setup deve criar o path declarado.
- A dependência `uv` deve existir ou a feature deve documentar fallback operacional.
- Falta de dependência deve gerar BLOCKED com evidência, não PASS.

## Critérios de aceite

- `FEATURES.md` e o script real da Browser Automation usam o mesmo contrato de path.
- `./scripts/test-registry.sh dogfood-real-p0` classifica EX-30 por evidência de execução, não por declaração textual.
- O setup documenta como instalar/provisionar `uv` ou oferece fallback testável.
- O script declarado existe, é executável e tem smoke test local.
```

Comando de publicação sugerido:

```bash
gh issue create \
  --repo elderbernardi/exocortex.saas \
  --title "[Dogfood][EX-30] Browser automation tem contrato de path divergente e uv ausente" \
  --body-file /tmp/ex30-dogfood-browser.md \
  --label "bug,dogfood,exocortex,P1"
```

---

## Issue 3 — EX-33 Codex Core Harness

Título:

```text
[Dogfood][EX-33] Codex Core Harness declara wrappers ausentes
```

Prioridade: `P0`

Body:

```markdown
## Contexto

Dogfood conversacional local detectou status FAIL para a feature EX-33: Codex Core Harness wrapper evidence.

Run de evidência:

`/home/elder/projetos/projetob/exocortex.saas/.dogfood/runs/dogfood-real-p0-20260606-214843/EX-33`

## Resultado observado

Os wrappers centrais declarados para o harness Codex não existem no ambiente esperado. A subinstância Hermes real também timeoutou durante a execução, mas o probe local já prova a falha estrutural.

Evidência do `probe.json`:

```json
{
  "probe": "ex33_codex_harness_wrappers",
  "run_wrapper": "/home/elder/.hermes/scripts/codex_learning/run_codex_with_learning.py",
  "run_wrapper_exists": false,
  "review_wrapper": "/home/elder/.hermes/scripts/codex_learning/review_latest_run.py",
  "review_wrapper_exists": false,
  "codex_learning_dir": "/home/elder/.hermes/codex-learning",
  "codex_learning_dir_exists": false
}
```

Transcript da subinstância:

```text
agent command timed out after 90s
```

## Resultado esperado

- `run_codex_with_learning.py` deve existir no path declarado ou a feature deve apontar para o wrapper real.
- `review_latest_run.py` deve existir no path declarado ou a feature deve apontar para o reviewer real.
- O diretório `~/.hermes/codex-learning` deve existir ou ser criado por setup documentado.
- O harness não deve declarar PASS quando esses artefatos centrais faltam.

## Critérios de aceite

- `./scripts/test-registry.sh dogfood-real-p0` valida EX-33 com evidência positiva dos wrappers.
- Ambos os wrappers existem e possuem smoke test local.
- O setup cria ou documenta o diretório de aprendizado Codex.
- Timeout da subinstância real vira BLOCKED/FAIL rastreável, sem quebrar o harness.
```

Comando de publicação sugerido:

```bash
gh issue create \
  --repo elderbernardi/exocortex.saas \
  --title "[Dogfood][EX-33] Codex Core Harness declara wrappers ausentes" \
  --body-file /tmp/ex33-dogfood-codex-core.md \
  --label "bug,dogfood,exocortex,P0"
```

---

## Execução proposta após aprovação

Se aprovado, executar:

```bash
# 1) Verificar labels
gh label list --repo elderbernardi/exocortex.saas

# 2) Criar body files temporários em /tmp
# 3) Criar as 3 issues com gh issue create
# 4) Registrar URLs retornadas em:
# .dogfood/runs/dogfood-real-p0-20260606-214843/github-publication-receipt.md
```

## Aprovação

Para publicar, responder com uma das opções:

- `A1` — publicar as 3 issues como estão.
- `A2` — revisar texto antes de publicar.
- `A3` — publicar só P0 agora: EX-25 e EX-33.
- `A4` — não publicar; manter como rascunho local.
