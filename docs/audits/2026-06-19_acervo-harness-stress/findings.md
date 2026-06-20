---
type: reflection
title: Acervo Harness — Verificação Profunda & Teste de Estresse
description: Catálogo de exceções e achados da auditoria do harness do Acervo Cognitivo
tags: [audit, acervo, harness, stress-test, lifecycle]
timestamp: 2026-06-19
class: perene
created_at: 2026-06-19T20:15:00Z
nature: reflections
---

# Acervo Harness — Verificação Profunda & Teste de Estresse

**Data:** 2026-06-19 · **Executor:** Claude (Opus 4.8) · **Modo:** SOLO (exocortex.saas)

Auditoria completa do harness do Acervo Cognitivo: criação de microverso, inserção
orgânica, artefatos, geração de conhecimento, decisions, ciclo de vida (deprecação →
quarentena → purge), memória canônica e gestão semântica. Tools Python reais + runtime
Hermes ao vivo. Toda operação logada em `ops.log.jsonl`.

## Backups (restauráveis)
- `/tmp/hermes-config-backup-<STAMP>.tgz` — skills/excrtx, profiles, skill-bundles, config.yaml (sem blob do browser-use)
- `/tmp/exocortex-acervo-backup-<STAMP>.tgz` — `~/exocortex/acervo` completo (381 arquivos pré-update)

## Severidades
`P0` quebra/perda de dado · `P1` regra não enforçada / contradição · `P2` UX/precisão/ruído · `P3` melhoria de representação (KR)

---

## Sumário Executivo

Auditoria de 5 fases (update do runtime → baseline → simulação determinística → execução ao vivo →
adversarial/estresse) sobre o harness do Acervo Cognitivo. **19 achados + 8 resultados positivos.**

**Veredito:** a camada **determinística (validadores Python)** é sólida — 31/31 regras enforçadas, lifecycle
cross-field correto, escala bem (~250 µs/arquivo), artefatos conformes. A camada **semântica ao vivo**
(deprecação ADR-016) funciona end-to-end. Os defeitos concentram-se em **skills/template/docs/provisionamento
desatualizados** em relação ao schema OKF (de hoje) e à reestruturação 11-natures.

**Mais graves (P0):**
- **F-020** `excrtx-memory-newmicro` dessincronizado → cria microverso 100% inválido com falso-sucesso (grep de verificação usa tokens errados). **CORRIGIDO.**
- **F-032** escrita de memória relativa ao cwd ignora `$EXOCORTEX_HOME`/`$ACERVO` → quebra isolamento, pode poluir repositórios. (Recomendação.)
- **F-030** modelo default `MiniMax-M3` (case errado) → todo turn do agente falha out-of-the-box; gateway serve `minimax-m3`. (Recomendação.)

**Correções aplicadas neste PR (com testes):** F-040 (BOM no validador + teste), F-013 (nature do template),
F-020 (reescrita da skill newmicro + gate), F-002 (mensagem de sucesso falsa dos crons). 44 testes do acervo
verdes. **Recomendações (sem fix):** F-010/F-011 (migrar acervo vivo / escopo do validador), F-030/F-031
(config de modelo/provider), F-032 (ancorar caminhos), F-012/F-021/F-015/F-041 (template/artefato/robustez).

| Sev | Achados |
|-----|---------|
| P0  | F-020✅, F-032, F-030 |
| P1  | F-001, F-002✅, F-010, F-011, F-012, F-013✅, F-014, F-021, F-031 |
| P2  | F-003, F-015, F-016, F-040✅, F-041 |
| ✅  | corrigido neste PR |

---

## Achados

### Fase 0a — Update do runtime (setup.sh --yes)

#### F-001 — Runtime estava sem 3 skills de lifecycle (drift) · P1 · operacional
**Observado:** antes do update, `~/.hermes/skills/excrtx/` tinha 49 skills mas faltavam
`excrtx-memory-deprecate`, `excrtx-memory-quarantine` e `excrtx-harness-maintenance` —
exatamente as que implementam o núcleo da gestão semântica (ADR-014/015/018). O ciclo de
vida autônomo estava inoperante no runtime instalado.
**Esperado:** runtime em paridade com o seed do repo (49/49).
**Repro:** `comm -23 <(ls repo/skills|grep excrtx|sort) <(ls ~/.hermes/skills/excrtx|grep excrtx|sort)`
**Status:** corrigido pelo `setup.sh --yes` (agora 52 dirs, paridade total). **Causa-raiz a investigar:** por que um install anterior pulou exatamente as 3 skills mais novas? (possível ordering/timestamp no step-03).

#### F-002 — Provisionamento de crons do síndico falha mas reporta sucesso · P1 · accuracy
**Observado:** `step-17-maintenance-crons.sh` emite 4× `⚠ Falha ao criar cron '<id>' — configure
manualmente` (maintenance-weekly, inbox-triage, artifact-audit, publication-check) e em seguida
imprime `✓ Cron jobs de manutenção configurados (03h–05h)`. Mensagem de sucesso contradiz as falhas.
**Impacto:** o síndico autônomo (ADR-018) NÃO é agendado; a quarentena/purge automática nunca roda,
e o operador é levado a crer que sim. Viola EX-49 (nunca afirmar sucesso sem verificação).
**Esperado:** se algum cron falha, status final = WARN/FAIL com instrução clara; não "✓ configurados".
**Repro:** `grep -A1 "Falha ao criar cron" reports/setup-run.log`

#### F-003 — `step-04` injeta artefato de teste na memória canônica real · P2
**Observado:** o full setup adicionou `_artifacts/items/provisioning-test-2026-06-19-201151.md`
ao acervo VIVO (`~/exocortex/acervo`), além de 2 arquivos em `micro/exocortex-dev/`. 381→384 arquivos.
**Impacto:** provisionamento polui memória real com dado de teste. Nenhum arquivo foi removido (diff só additions).
**Esperado:** testes de provisionamento usam acervo descartável, não o canônico.

#### F-004 — Validador reprova 177/384 arquivos do acervo real (baseline) · P1 · a triar na Fase 1
**Observado:** a verificação final do setup rodou `validate_frontmatter.py` sobre `~/exocortex/acervo`
e marcou **177 FAIL**, muitos por `[V-001] File must start with '---'` em `README.md`,
`.quarantine/README.md` e `_artifacts/items/*/source.md`.
**A investigar (Fase 1):** quantos são arquivos não-semânticos que o validador NÃO deveria validar
(README, sources de artefato, raw/) vs. violações reais de páginas canônicas. Possível bug de escopo
do validador (falta de exclusão de `_artifacts/`, `raw/`, `README.md`, `.quarantine/`).

### Fase 1 — Baseline read-only dos acervos reais

#### F-010 — 177/250 arquivos do acervo VIVO reprovam o próprio validador · P1
**Observado:** `validate_frontmatter.py --dir ~/exocortex/acervo` → 73 PASS / 177 FAIL.
Decomposição: 91× V-001 (sem frontmatter), ~71× cada de V-040/V-042/V-014/V-010/V-012
(frontmatter legado sem os campos OKF obrigatórios `class`/`created_at`/`timestamp`/`type`/`description`).
**Causa-raiz:** o schema OKF v0.1 é de HOJE (2026-06-19) e a `migrate_frontmatter.py` nunca foi
aplicada à memória canônica viva. A memória precede o schema.
**Teste de hipótese (sandbox):** rodar a migração elevou PASS 73→165 (FAIL 177→85). Confirma:
a maior parte é só "não migrado", não "corrompido".
**Recomendação:** rodar a migração no acervo real (com backup) ou adicionar gate de CI; documentar
que `setup.sh` deveria migrar o acervo no provisionamento.

#### F-011 — Validador valida arquivos NÃO-semânticos (escopo amplo demais) · P1 · missing-scope
**Observado:** dos 85 fails pós-migração, 60 são `_artifacts/items/**` (source.md, deliverables .md),
+ `README.md`, `.quarantine/README.md`, `_inbox/*`. Esses não são páginas semânticas do acervo e não
deveriam carregar frontmatter OKF, mas `--dir` os valida recursivamente e os reprova.
**Impacto:** ruído massivo (60+ falsos-positivos) que mascara violações reais; impossível usar exit code
em CI sem exclusões. **Recomendação:** validador deve pular `_artifacts/`, `raw/`, `_inbox/`,
`.quarantine/`, `README.md` e arquivos `_archive/` por padrão (ou aceitar `--exclude`).

#### F-012 — Template do microverso nasce inválido (placeholders + descrição vazia) · P1
**Observado:** `micro/_template/**/_seed.md` contém `description: ""`, `timestamp: "{{CREATED_DATE}}"`,
`created_at: "{{CREATED_DATE}}T00:00:00Z"` → reprova V-024, V-029, V-043, V-045. Se
`excrtx-memory-newmicro` não substituir TODOS os placeholders E preencher `description`, o microverso
recém-criado já entra não-conformante. **A validar na Fase 2/3** (scaffold real). **Recomendação:**
template deve usar `description` placeholder não-vazio e o newmicro deve validar o resultado (gate).

#### F-013 — `nature:` divergente do diretório, inclusive no TEMPLATE · P1 · regra não enforçada
**Observado:** SCHEMA exige "nature == diretório". 4 violações reais:
`_template/prompts/_seed.md` (nature=contracts), `_template/skills/_seed.md` (nature=tools),
`_template/decisions/_seed.md` (nature=knowledge), e `estudio-criativo/decisions/create-estudio-criativo.md`
(nature=knowledge em decisions/). As 3 do template propagam para todo microverso novo.
**Impacto:** roteamento de Domain Filter / SEARCH por nature fica incorreto. **Nenhuma regra do validador
checa nature-vs-diretório** (V-074 só exige que seja string). **Recomendação:** corrigir os _seed.md +
adicionar regra de validação nature-vs-path.

#### F-014 — log-convention documentada mas NÃO enforçada; 5/11 logs já violam · P1
**Observado:** `log-convention.md` exige exatamente um H1 `# Log`, headings `## YYYY-MM-DD`, bullets de
linha única. 5/11 `log.md` violam: `global/_meta/log.md` (sem `# Log`, tem sub-bullet),
`shared/_meta/log.md`, `micro/{hermes-setup,projeto-alpha,_template}/_meta/log.md` (sem `# Log`).
**Impacto:** não há validador para o append-only log; a integridade do histórico de lifecycle é só
convencional. **Recomendação:** criar `validate_log.py` (D1) cobrindo §1–§3 da log-convention.

#### F-015 — `validate_artifact_manifest --all` trata qualquer subdir de items/ como artefato · P2
**Observado:** 7 "artefatos", 2 válidos, 5 com erro — 4 por `manifest.json not found`, sendo que
`patches/` e `repairs/` NÃO são artefatos (são outros diretórios sob `_artifacts/items/`).
Artefatos reais (`art_20260617_guimaraes_briefing`) estão órfãos (sem manifest/owner/provenance).
**Recomendação:** validador só deve considerar dirs com `manifest.json` (ou padrão `art_*`); reportar
não-artefatos separadamente.

#### F-016 — pytest: 16/185 falham (não relacionados ao acervo) · P2 · contexto
**Observado:** `test_last30days_integration.py` (13, precisam de engine/rede) e `test_sources_controlled.py`
(3, licenciamento hermes-webui). **Todos os testes do harness do acervo passam** (validate_frontmatter,
migrate_frontmatter, artifact_publish, runtime_enforcement, draftfirst). 169 passam.
**Nota:** falhas pré-existentes, fora do escopo do acervo; registradas para completude.

### Fase 2 — Simulação determinística de conformidade

#### F-020 — `excrtx-memory-newmicro` está dessincronizado do template (cria microverso 100% inválido + falso-sucesso) · P0
**Observado (simulação literal do SKILL.md):**
1. Step 5 manda substituir `{MICROVERSO_NAME}` e `{slug}`, e verificar com
   `grep -r '{MICROVERSO_NAME}\|{slug}'` → **NO RESULTS → skill conclui "clean"**.
   Mas o template real usa `{{DOMAIN_NAME}}` (25×), `{{CREATED_DATE}}` (58×), `{{DOMAIN_DESCRIPTION}}`,
   `{{NOME_CLIENTE}}`, `{{PRAZO}}`, `{{VALOR}}`. **86 placeholders sobrevivem sem detecção.**
2. Step 5 lista "7 Nature files: context.md, decisions.md, processes.md, tools.md, people.md, goals.md,
   constraints.md" — **TODOS inexistentes**. O template tem 14 diretórios (11 natures + _meta/raw/_archive),
   cada nature como diretório com `_seed.md`.
3. Step 4 manda preencher `{slug}/SCHEMA.md` com frontmatter `domain/slug/type/description/created` —
   schema legado; o real é `_meta/SCHEMA.md` com OKF (`type/title/description/tags/timestamp/class/created_at`).
4. Resultado: microverso recém-criado valida **0 PASS / 15 FAIL**, e a skill **reporta sucesso** (viola EX-49).
**Causa-raiz:** SKILL.md de `newmicro` precede a reestruturação 11-natures-diretório + migração OKF; nunca
foi atualizado. **Impacto:** todo novo microverso nasce quebrado e não detectado. **P0 — fix obrigatório.**
**Recomendação:** reescrever Procedure (tokens `{{...}}` corretos, lista de natures-diretório, schema OKF,
`_meta/SCHEMA.md`) e trocar o grep de verificação por `grep -rE '\{\{[A-Z_]+\}\}'` + gate `validate_frontmatter`.

#### POSITIVO P-01 — Pipeline de artefatos é conformante
`init_artifact_package.py` gera estrutura correta (id `art_YYYYMMDD_HHMMSS_slug`, subdirs source/exports/
assets/evaluations/receipts, `owner` ligado ao microverso, provenance). `validate_artifact_manifest.py`
passa em draft fresco e populado. **Sem defeito.** (Obs. menor: export adicionado em disco sem entrada
no manifest não é flagrado em status=draft — possível gate futuro, P3.)

#### POSITIVO P-02 — Regras cross-field de lifecycle são enforçadas corretamente
Testes determinísticos: V-065 (expiry < quarantined → ERROR ✓), V-071 (deprecated+quarantined → ERROR ✓),
V-072 (promoted+volátil → WARN ✓), quarentena válida e deprecação válida → PASS. **O validador é sólido
para os invariantes de gestão semântica de ciclo de vida.** Os defeitos concentram-se na camada de
skills/template/docs, não nos validadores determinísticos.

#### F-021 — `_meta/SCHEMA.md`, `index.md`, `log.md` e `_seed.md` do template sem frontmatter conforme · P1
**Observado:** com substituição 100% correta, o microverso ainda valida 0/15: `_meta/*` sem frontmatter
(V-001); 11× `_seed.md` com `description:""` (V-024); `contracts/exocortex-hermes-identity.md` legado.
**Conflito spec↔template:** schema-spec §3.2/§3.3 diz que `_meta/`/`index.md`/`log.md`/`_seed.md` recebem
`class: perene, type: context` — ou seja, DEVEM ter frontmatter. O template não os entrega assim.
**Recomendação:** adicionar frontmatter OKF aos arquivos estruturais do template e `description` não-vazia
(ou placeholder) aos `_seed.md`; rodar o validador como hook `validate` do `microverso.yaml`.

### Fase 3 — Execução ao vivo (Hermes + skills)

#### F-030 — Modelo default tem case errado → todo turn do agente falha out-of-the-box · P0 · provisioning
**Observado:** `config.yaml` tem `model.provider: minimax`, `model: MiniMax-M3`, base_url
`https://opencode.ai/zen/go/v1`. O gateway OpenCode Zen serve o id **`minimax-m3` (minúsculo)** e
rejeita `MiniMax-M3` com `ModelError: Model MiniMax-M3 is not supported`. Resultado: `hermes -z` falha
("no final response"). Só funcionou com `-m minimax-m3`.
**Impacto:** agente inutilizável após provisionamento padrão. **Recomendação:** corrigir o id do modelo no
config/setup para `minimax-m3`; idealmente validar o id contra `/v1/models` no `step-12-verify-keys`.

#### F-031 — Provider 'minimax' exige MINIMAX_API_KEY, mas só há OPENCODE_API_KEY · P1 · provisioning
**Observado:** com a key correta ausente, `hermes` aborta: "Provider 'minimax' ... no API key ... Set
MINIMAX_API_KEY". O gateway é OpenCode (aceita `OPENCODE_API_KEY`), mas o provider rotulado `minimax`
procura `MINIMAX_API_KEY`. Contornado com `MINIMAX_API_KEY=$OPENCODE_API_KEY`. `setup` avisou
"EXOCORTEX_MODEL não configurado" mas seguiu. **Recomendação:** reconciliar nome do provider/var de key
no provisionamento (provider `opencode` ou mapear a env var).

#### POSITIVO P-03 — Runtime sandboxado funciona e isola memória
`hermes status`/`-z` respeitam `HERMES_HOME`/`EXOCORTEX_HOME`/`ACERVO` do sandbox; smoke retornou
"ACERVO STRESS SMOKE OK". Isolamento confirmado (auth/sessions/acervo no `/tmp`).

#### F-032 — Escrita de memória é relativa ao cwd, ignora $EXOCORTEX_HOME/$ACERVO · P0 · isolamento/segurança
**Observado:** com `EXOCORTEX_HOME`/`ACERVO` apontados para o sandbox, o agente (excrtx-memory-manager)
gravou em caminho **relativo ao cwd**: `acervo/micro/exocortex-dev/knowledge/default-model.md`. Como o
`hermes` rodou com cwd no checkout do repo, o arquivo + `index.md`/`log.md` foram criados **no working tree
do repo `exocortex.saas`**, não no acervo configurado. (Revertido via `git stash`.)
**Impacto:** (1) quebra isolamento — rodar `hermes` de dentro de qualquer dir com `acervo/` escreve memória
ali; (2) risco de poluir/corromper repositórios; (3) a memória canônica real depende do diretório de
trabalho, não da configuração. **Recomendação:** skills de memória devem ancorar TODA escrita/leitura em
`$EXOCORTEX_HOME/acervo` (ou `$ACERVO`) absoluto, nunca relativo ao cwd; adicionar guard que recusa escrever
fora de `$ACERVO`.

#### POSITIVO P-04 — Comportamento da skill de memória é correto (conteúdo)
Apesar de F-032, o conteúdo produzido foi conformante: Domain Filter aplicado (roteou para
`micro/exocortex-dev/knowledge/`), frontmatter OKF completo, `class: volátil` justificado, hook de revisão
semântica (ADR-016) executado (buscou contradição → 0 matches → sem deprecação), e validação real
`validate_frontmatter --file ... PASS EXIT=0` (arquivo confirmado válido). Atualizou index.md + log.md.
Honra EX-49 (verificação empírica real, não alucinada).

### Fase 4 — Adversarial & estresse

#### POSITIVO P-05 — Validador enforça corretamente as 31 regras testadas (0 lacunas)
Harness adversarial (1 mutação por regra) sobre V-001..V-076: **31/31 disparam a regra esperada**, com
firings secundários corretos (V-070 em data malformada, V-052 junto de V-051, V-072 com promoted_at,
V-061/062 quando quarantined_at presente). **Implementação ≡ spec** para o conjunto testado; nenhuma
regra documentada ficou sem enforcement. (Fixtures em `fixtures/adversarial/`.)

#### POSITIVO P-06 — Validador escala bem
2003 arquivos validados em **~500 ms (~249 µs/arquivo)**. Arquivo de 500 KB, 300 tags e nesting de 8
níveis → todos tratados (PASS). Sem problema de performance/memória.

#### F-040 — BOM UTF-8 antes de `---` causa falso V-001 · P2 · robustez
**Observado:** arquivo válido com BOM (`\xEF\xBB\xBF`) no início → `[V-001] File must start with '---'`.
Editores que inserem BOM quebram a validação mesmo com frontmatter correto. **Recomendação:** remover BOM
antes da checagem V-001.

#### F-041 — `class` exige `volátil` acentuado; `volatil` é rejeitado · P2/P3 · robustez/KR
**Observado:** `class: volatil` (sem acento) → `[V-041]`. O enum exige o valor acentuado `volátil`, fácil
de digitar errado (sobretudo em geração programática/ASCII). **Recomendação:** aceitar `volatil` como alias
(normalizar) ou documentar enfaticamente; reduz fragilidade de um campo de ciclo de vida crítico.

#### NOTA edge — CRLF, flow-style YAML e tabs tratados corretamente
CRLF → PASS; frontmatter flow `{k: v, ...}` → PASS; tabs no YAML → `[V-003] Invalid YAML` (correto).

#### POSITIVO P-07 — Agente ao vivo compensa a skill quebrada (newmicro) e gera microverso válido
Ao criar `projeto-gamma` ao vivo, o agente **detectou a divergência skill↔template** e seguiu o template
real (11 natures-diretório), preencheu `description` vazias, adicionou frontmatter a `_meta/*` e ao
contrato de identidade, e corrigiu V-070 → resultado **PASS=15/FAIL=0**. O próprio agente registrou:
"a skill descreve 7 Natures... o template real usa 11... criei seguindo o template real... vale patch".
**Conclusão dupla:** (a) confirma F-020 (skill errada); (b) o validador/template é a fonte de verdade
efetiva e modelos capazes contornam a skill. Um executor estrito produziria o microverso quebrado da
Fase 2a. **Reforça a recomendação de F-020 + usar `validate_frontmatter` como gate no newmicro.**
**Imprecisão menor (P3):** agente afirmou "zero placeholders restantes" mas 3 `{{...}}` sobraram no corpo
do contrato (não quebram validação) — pequeno desvio de EX-49.

#### POSITIVO P-08 — Revisão semântica / deprecação ao vivo funciona end-to-end (ADR-016)
WRITE contraditório (default DeepSeek-V3 → minimax-m3) acionou corretamente o hook: o fato anterior
`modelo-default.md` recebeu `deprecated: true` + `deprecated_at` + `deprecated_reason` ("Superseded by
modelo-default-m3.md"); novo arquivo criado com link `Supersedes:`; `created_at`/`tags`/`title`/`class`/
body originais preservados; `log.md` append-only íntegro; isolamento de domínio respeitado; e o agente
raciocinou que o SEARCH passa a excluir o deprecado. **Núcleo da gestão semântica: conforme.**
**Obs (F-032):** resolução de caminho variou entre testes (cwd-relativo vs `$HERMES_HOME/acervo`); reforça
a necessidade de ancorar caminhos. **Obs útil:** o agente apontou que a decisão conceitual no Acervo não
propaga para `config.yaml`/perfis (config de runtime é separada) — alinhado com F-030.

### Fase 5 — Correções aplicadas (com verificação)

Política: corrigir apenas bugs **inequívocos** + teste de regressão; deixar decisões de design como recomendação.

| Fix | Achado | Arquivo(s) | Verificação |
|-----|--------|-----------|-------------|
| BOM strip no validador | F-040 | `scripts/validate_frontmatter.py` | fixture `valid-bom.md` + teste `test_valid_with_utf8_bom`; suíte 13/13 ✅ |
| nature == diretório no template | F-013 | `acervo/micro/_template/{prompts,skills,decisions}/_seed.md` | sweep nature-vs-dir do template = 0 mismatches ✅ |
| reescrita skill newmicro | F-020 | `skills/excrtx-memory-newmicro/SKILL.md` | tokens `{{...}}`, 11 natures-diretório, schema OKF, grep correto `\{\{[A-Z_]+\}\}`, gate `validate_frontmatter`; D1=PASS; `compile_soul` ✅ |
| status honesto dos crons | F-002 | `setup/step-17-maintenance-crons.sh` | `CRON_FAILURES` + mensagem condicional; `bash -n` OK ✅ |

**Não corrigidos (recomendação — design/operacional/fora do repo):** F-010 (migrar acervo vivo — toca memória
real, decisão do executivo), F-011 (escopo do validador: excluir `_artifacts/`/`raw/`/`_archive/`/`.quarantine/`/
`README.md` — mudança de comportamento), F-012/F-021 (template `_meta`/`_seed` born-valid — parcialmente mitigado
pelo gate do newmicro), F-015 (escopo do `validate_artifact_manifest`), F-030/F-031 (id do modelo `minimax-m3` +
provider/key — em `~/.hermes/config.yaml`, runtime do usuário), F-032 (ancorar escrita de memória em `$ACERVO`
absoluto — auditoria ampla de skills), F-041 (aceitar `volatil` sem acento — decisão de schema).

## Restauração (rollback do update da Fase 0a)
```bash
tar xzf /tmp/hermes-config-backup-<STAMP>.tgz   -C ~/.hermes
tar xzf /tmp/exocortex-acervo-backup-<STAMP>.tgz -C ~/exocortex
```

### Fase 6 — Recomendações implementadas (segunda rodada)

| Fix | Achado | Arquivo(s) | Verificação |
|-----|--------|-----------|-------------|
| Escopo do validador (pula `_artifacts/`/`raw/`/`_archive/`/`.quarantine/`/`_inbox/`/README) + `--no-exclude` | F-011 | `scripts/validate_frontmatter.py` | real acervo 250→186 escaneados, invalid 177→113; 2 testes novos; suíte 15/15 ✅ |
| Template born-valid | F-012/F-021 | `_template/_meta/{SCHEMA,index,log}.md` (+frontmatter), 11× `_seed.md` (description preenchida), `contracts/exocortex-hermes-identity.md` (+campos OKF) | scaffold+substituição → **15/15 PASS, 0 FAIL** ✅ |
| Escopo do validador de artefatos | F-015 | `acervo/global/tools/harness/validate_artifact_manifest.py` | só valida dirs com `manifest.json`/`art_*`; 7→4 artefatos, 3 não-artefatos pulados (patches/repairs/...) ✅ |
| Resolução do ACERVO em 4 skills | F-032 | `excrtx-memory-{manager,syndic,quarantine}`, `excrtx-quality-designsys` | resolve `$ACERVO`→`$EXOCORTEX_HOME/acervo` (não o scaffold vazio `~/.hermes/acervo`); proíbe path relativo ao cwd; D1 PASS ✅ |

#### F-032b — 4 skills ancoravam o ACERVO no scaffold vazio `~/.hermes/acervo` · P1 · raiz de F-032
**Observado:** `excrtx-memory-{manager,syndic,quarantine}` e `excrtx-quality-designsys` definiam
`ACERVO="${HERMES_HOME:-$HOME/.hermes}/acervo"` — `~/.hermes/acervo` (scaffold vazio), **conflitando** com
`setup/common.sh` que usa `$EXOCORTEX_HOME/acervo` (memória real). Os skills de lifecycle (syndic/quarantine)
varreriam o local errado/vazio. **CORRIGIDO** (resolução consistente + fallback). 

#### F-050 — 4 páginas semânticas reais com YAML inválido (V-003) · P1 · não auto-corrigível
**Observado (revelado pela F-011):** `global/_meta/DESIGN.md`, `micro/exocortex-dev/decisions/skill-vs-mcp-selection.md`,
`.../workflows/create-custom-skill.md`, `.../workflows/run-preflight-checks.md` têm frontmatter YAML malformado
(`mapping values are not allowed here` / `while scanning a simple key`). A migração **não** conserta isso.
**Recomendação:** correção manual do YAML nessas 4 páginas.

#### F-030/F-031 — não corrigível no repo
O id `MiniMax-M3` está em `~/.hermes/config.yaml` (escrito pelo runtime Hermes, **não** pelo exocortex.saas);
`skill_judge.py` já documenta a nuance `minimax-m3`. Recomendação: rodar `hermes model` para reconfigurar, ou
adicionar no `step-12-verify-keys` uma checagem do id contra `/v1/models`. **Sem patch no repo.**

#### F-010 — migração do acervo vivo: PENDENTE de autorização explícita
Dry-run no acervo real: 165 em escopo, 138 modificáveis, **0 erros**. Backup fresco em
`/tmp/exocortex-acervo-premigration-<STAMP2>.tgz`. **Bloqueado pelo guard de segurança** (reescrever memória
canônica viva exige autorização explícita do executivo). Aguardando confirmação.

### Fase 7 — Migração do acervo vivo aplicada (autorizada pelo executivo)

**F-010 RESOLVIDO.** `migrate_frontmatter.py --dir ~/exocortex/acervo` aplicado (138 modificados, 0 erros).
Resultado: **conformes 73 → 164, inválidos 113 → 4** (a migração também corrigiu as 4 páginas com YAML
malformado da F-050). Backup: `/tmp/exocortex-acervo-premigration-20260619_211018.tgz`.

Refinamento adicional do validador (F-011): `_template` e `_fixture` adicionados aos excludes (scaffolds com
placeholders, não são páginas vivas). Estado final: **168 escaneados, 164 válidos, 4 inválidos, 82 pulados.**

#### F-060 — `macro/*` sem frontmatter (decisão de design pendente) · P2
**Observado:** os 4 inválidos restantes são `macro/{SOUL.md,soul.md,estilo.md,valores.md}` — a constituição
do executivo, **intencionalmente sem frontmatter** (FLAT, sempre carregada, versionada só no git, sem log
por convenção). O validador os reprova por V-001.
**Decisão necessária (executivo):** ou (a) **isentar `macro/`** do validador (adicionar aos excludes — coerente
com "macro é especial"), ou (b) **adicionar frontmatter OKF** aos arquivos macro. Não decidido unilateralmente.
