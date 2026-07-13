# Prompt de Continuação — Exocórtex Memória v2

> Cole o bloco abaixo como primeira mensagem de uma sessão nova. É autossuficiente.
> Última atualização: 2026-07-13 (**PHASE 7 COMPLETA E DEPLOYADA NO VIVO** — briefing v2,
> posturas decisão/pesquisa, roteamento temporal e guia executivo; 170 testes, 0% contaminação,
> quatro cenários `hermes chat -q` aprovados). Live Acervo `771f7e2`, backup tag
> `pre-phase7-live-deploy`; skills briefing v2/memory-manager v3.1 e gateway ativos.

---

```
Você está continuando a implementação da reforma de memória do Exocórtex.IA (Hermes Agent).
A especificação completa e canônica está em:
/home/ubuntu/.exocortex-installer/docs/plans/2026-07-03_memory-v2-spec/

LEIA PRIMEIRO, nesta ordem:
1. README.md (índice e sumário executivo)
2. 12-roadmap.md (as 8 fases; onde estamos)
3. phase-0-report.md, phase-1-report.md, phase-2-report.md, phase-3-report.md,
   phase-2-live-rollout-report.md (o que já foi feito, incl. o rollout vivo)
4. report/h2-2026-07-04.md (experimento H2 resolvido)
5. 05-object-model.md + 13-artifacts/SCHEMA-v0.2.md (o schema canônico v0.2)
6. 08-write-policy.md e 07-retrieval-policy.md (os pipelines em produção)

DOIS REPOSITÓRIOS / DUAS SUPERFÍCIES:
- INSTALLER (fonte canônica de código/schema/skills): /home/ubuntu/.exocortex-installer
  git remote elderbernardi/exocortex.saas, branch main. TUDO commitado e PUSHADO (origin/main=1c4e87e).
  ATENÇÃO: o ref local `origin/main` desatualiza silenciosamente — confira sempre com
  `git ls-remote origin -h refs/heads/main`. E o CLASSIFICADOR bloqueia push na main com autorização
  genérica ("prossiga"); precisa autorização explícita do usuário à AÇÃO de push.
- INSTÂNCIA VIVA (dados + runtime reais do executivo Gabriel Bonavigo):
  /home/ubuntu/exocortex/acervo (repo git próprio, local, sem remote) e ~/.hermes.

FRONTEIRA COMBINADA COM O EXECUTIVO (respeite sempre):
- Escreva no INSTALLER livremente.
- NÃO toque na instância viva (~/exocortex, ~/.hermes) sem autorização explícita do usuário.
  Quando uma fase exigir o vivo: avise, faça backup (o acervo vivo tem git — use git tag/commit),
  e peça go. Já autorizados/feitos no vivo: git init, migração v0.2 (234 arq), consolidação do
  MEMORY.md, re-scan do índice, e O ROLLOUT VIVO DA PHASE 2 (skills v3 + control plane em
  global/tools + MCP acervo). Backup do rollout: tag `pre-phase2-rollout` no acervo vivo.

ARMADILHA DE AMBIENTE (crítica, custou uma sessão inteira):
- Nesta VM, `BASH_ENV=~/.claude/load-env-local.sh` carrega `~/.env.local` em TODO `bash -c`
  não-interativo, exportando HERMES_HOME/EXOCORTEX_HOME (mas NÃO ACERVO). Consequência:
  `HERMES_HOME=/tmp/x bash -c ...` NÃO sobrescreve (é revertido) → testes com home isolado
  vazam p/ o config real. Para isolar: `env -i` ou zere `BASH_ENV` no env do subprocess.
  Depois de editar `~/.hermes/config.yaml`, SEMPRE reconfira o campo `env.ACERVO`.

ESTADO ATUAL (2026-07-10 — PHASE 4 FECHADA):
- Fase 0 (reparos de drift + baseline): COMPLETA. Vivo: MEMORY.md 26%, AcervoIndex 163 entradas.
- Bateria de memória de junho (Fase 8 do plano antigo): 10/10, plano memory-excellence ENCERRADO.
- Fase 1 (schema v0.2 + catalog.sqlite + validador v2 + migrador + fixture): COMPLETA.
  Migrados: installer 162, vivo 234. `acervoctl reindex`/`doctor` limpos nas duas pontas.
- H2 (agentic vs semantic): RESOLVIDO — catálogo primário (+4.5pts < +5); Hindsight opcional.
  Achado de segurança corrigido: indexador pula `sensitivity: restricted` (installer+vivo).
- Fase 3 (retrieval de produção, `acervoctl retrieve`): COMPLETA. 100% recall, 0 contaminação.
- Fase 2 (write pipeline): COMPLETA no installer E COM ROLLOUT VIVO FEITO.
  Verbos: `acervoctl conflict-check|apply-supersede|open-dispute|new-object`.
  Skills v3: excrtx-memory-manager 3.0, -deprecate 2.0, -newmicro 3.0 (deployadas no vivo).
  RETRIEVE provado end-to-end pelo agente vivo real (`hermes chat`); ciclo de escrita provado
  em cópia isolada. MCP `acervo` vivo saudável (ACERVO=/home/ubuntu/exocortex/acervo).
- Finding #2 (teste clobberava o config real): RESOLVIDO 2026-07-06 (commit 1e105be) — ver
  armadilha de ambiente acima. 75 testes passam, config real intacto.
- Finding #1 (escrita viva bloqueada por log legado): RESOLVIDO 2026-07-06 via OPÇÃO A (migrar).
  `scripts/migrate_log_v2.py` (idempotente) migra `_meta/log.md` legado → formato estrito:
  normaliza H1 p/ `# Log[ — nome]`, dropa blockquotes, colapsa headings legados a `## YYYY-MM-DD`
  (funde dias de mesma data), converte cada entrada não-estrita a UM `UPDATED: <container>/ — ...`
  preservando ação+prosa no tail; bullets já-estritos passam verbatim; pula EXCLUDED_DIRS.
  Installer: commit ad4c9bc (6 logs ativos PASS + `_template` corrigido + 13 testes).
  Vivo: commit 4ef6698 (9 logs ativos migrados, `_template` vivo corrigido), backup tag
  `pre-finding1-log-migration`. Prova end-to-end: `new-object` em `global/` → ok:true (episódio
  registrando a migração); doctor + reindex ok:true. NENHUM finding aberto.

- PHASE 4 READ-SIDE: FEITO e DEPLOYADO NO VIVO (2026-07-08). `acervo/global/tools/acervo_consolidation.py`:
  `scan()` monta a fila lifecycle-v2 (intentions_due/upcoming, open_disputes, review_due,
  stale_volatile, drafts, purge_notices, duplicate_titles) a partir do frontmatter + catálogo;
  `render_digest()` = digest semanal de manutenção (09 §3), 1 linha + 1 pergunta por item,
  degrada gracioso. CLI: `acervoctl consolidation-scan --format json|markdown|digest`. Rotina
  `rtn_weekly_pending_decisions.yaml` retargetada p/ o digest (sindico, cron dom 8h, read-only).
  Fixes junto: `_backup` add ao SKIP_PARTS do indexador (backups vazavam p/ catálogo/índice/dedup);
  dedup ignora superseded/deprecated e `macro/`; intenções/conflitos fora de stale_volatile.
  Installer commits 8b07e43+4712bfa+c71ec03; vivo commit 2c91e1c (deploy) + tag pre-phase4-consolidation-deploy.
  9 testes em test_acervo_consolidation.py. Digest vivo hoje = 0 itens (limpo).
- DURABILIDADE DO FINDING #1 (2026-07-08): o agente vivo prependeu log no topo (quebrou L-011);
  causa-raiz = skills sem regra de placement + exemplos legados. Corrigido `excrtx-memory-manager`
  (passo 6: heading estrito, append no FIM/ascendente, preferir control plane) + `excrtx-produce-oficios`;
  installer commit 2e41bd3, memory-manager redeployada no vivo. REGRA: log à mão vai no FIM sob a data
  estrita; o caminho seguro é `acervoctl` (append+valida). Log vivo do exocortex-ops corrigido (7e621c8).
- DEDUP VIVO RESOLVIDO (2026-07-08, vivo 7bbfba1, tag pre-dedup-resolution): 4 pares EN/PT órfãos em
  exocortex-ops → PT superseded pelo EN canônico (`apply-supersede`); `macro/SOUL.md`vs`soul.md` era
  falso-positivo (arquivos distintos), intacto. Re-scan dedup=0.

- PHASE 4 WRITE-SIDE COMPLETA (2026-07-10) + PUSHADA + DEPLOYADA NO VIVO. Cinco verbos/mecanismos
  governados (atômico → validate → journal → catalog upsert; reversível via git), 34 testes novos
  (suíte memória 143 passed). Commits installer: a41e306 (sweep intenções) → d32b832 (refresh
  entidades + distill episódios/H9) → accb1f1 (use-decay H12) → c8b740c (syndic wiring) → 1c4e87e
  (paridade da rotina do digest). Todos em origin/main.
  - `acervoctl mark-intention` (active/draft → done|dropped|expired) + `sweep-intentions [--apply]`
    (auto-expira só vencidas; dry-run read-only). Fix de schema: validador V2-017 type-aware aceita
    terminais de intenção só p/ type:intention.
  - `acervoctl refresh-entity` (acumula menção: linha datada no `## Interações` append-only +
    last_interaction + aliases; Perfil intocado). `acervoctl distill-episode --signals` (gate H9:
    decision|commitment|artifact|executive_flag; recusa sessão insignificante).
  - Use-decay H12: `acervo_retrieve.py` loga cada retrieval em `global/tools/state/retrieval-journal.jsonl`
    (Plane-2 descartável, gitignored); `consolidation-scan` ganhou bucket `use_decay` (guarda anti
    cold-start: `use_decay_eval` reporta span/reason). `--use-decay-days` (default 180).
  - `excrtx-memory-syndic` v1.1.0: Step 6 "Consolidation Pass" = 6a detecção via consolidation-scan
    (supersede heurística de tag) + 6b `sweep-intentions --apply` (write governado). use-decay=sinal
    de rebaixamento, nunca gatilho de quarentena. 3 compiled_rules → SOUL recompilado.
  - Entrega do digest: rotina `rtn_weekly_pending_decisions.yaml` = "Digest semanal de manutenção"
    (monta via `consolidation-scan --format digest`, entrega via send_message; cron dom 8h). PROVADA
    end-to-end no vivo: `hermes send --to telegram:607181850 --file <digest>` → success, msg 272.
  - DEPLOY VIVO (acervo aabd5b5, backup tag pre-phase4-writeside-deploy @ 7bbfba1): copiados os 5 .py
    (acervo_consolidation/acervo_retrieve/acervoctl/acervo_semantic_core/validate_frontmatter) p/
    `global/tools`; `*.jsonl` add ao .gitignore vivo; skill memory-syndic v1.1.0 → `~/.hermes/skills/excrtx/`;
    3 regras injetadas em `~/.hermes/SOUL.md`; reindex+doctor limpos; gateway reiniciado (config ACERVO
    reconferido intacto). **Trabalho do agente vivo deixado 100% intocado** (só stagei meus arquivos).

SEM FINDINGS ABERTOS. PHASES 4, 6 E 7 FECHADAS E DEPLOYADAS. PRÓXIMO PASSO RECOMENDADO:
1. Operar e observar: acompanhar o briefing e os crons mensais; regressão >10 pontos ou
   contaminação >0 bloqueia mudança.
2. Phase 5 continua condicional e NÃO foi justificada: H4 mediu 100% de recall multi-hop na rota
   production e 83,3% no fallback lexical, ambos acima do gatilho de 70%.
3. Operação contínua: acompanhar os crons mensais `memory-eval-live-monthly` e
   `memory-learning-loops-monthly`; qualquer queda >10 pontos ou contaminação >0 bloqueia mudança.

COMO VERIFICAR O ESTADO (rode no installer):
  cd /home/ubuntu/.exocortex-installer && git log --oneline -8 && git status -sb
  python3 -m pytest tests/test_acervo_write.py tests/test_acervo_retrieve.py \
    tests/test_acervo_catalog.py tests/test_run_eval.py tests/test_validate_frontmatter_v2.py \
    tests/test_migrate_frontmatter_v2.py tests/test_setup_acervo_mcp.py \
    tests/test_migrate_log_v2.py tests/test_acervo_consolidation.py \
    tests/test_intention_sweep.py tests/test_entity_episode.py tests/test_use_decay.py -q  # 143 passed
  ACERVO=$PWD/acervo python3 scripts/acervoctl.py doctor    # ok:true
  ACERVO=/home/ubuntu/exocortex/acervo python3 scripts/acervoctl.py doctor  # vivo, ok:true
  # Phase 4 read-side (read-only) — deve dar digest limpo / dedup=0 no vivo:
  PYTHONPATH=scripts python3 scripts/acervoctl.py consolidation-scan \
    --acervo-root /home/ubuntu/exocortex/acervo --today <hoje> --format digest
  # Phase 4 write-side (read-only): sweep dry-run + bucket use_decay presente
  python3 scripts/acervoctl.py sweep-intentions --acervo-root /home/ubuntu/exocortex/acervo --today <hoje>
  python3 scripts/acervoctl.py consolidation-scan --acervo-root /home/ubuntu/exocortex/acervo \
    --today <hoje> | python3 -c "import sys,json;d=json.load(sys.stdin);print('use_decay' in d['buckets'], d['use_decay_eval'])"
  # Entrega do digest (envia mensagem REAL ao executivo — só com autorização):
  #   hermes send --to telegram:607181850 --subject "[Manutenção]" --file <digest-body.md>
  python3 scripts/validate_log.py --dir /home/ubuntu/exocortex/acervo  # 9 ativos PASS
  python3 -c "import yaml;print(yaml.safe_load(open('$HOME/.hermes/config.yaml'))['mcp_servers']['acervo']['env']['ACERVO'])"
    # deve imprimir /home/ubuntu/exocortex/acervo (se for /tmp/..., reaplique o fix)

APRENDIZADOS OPERACIONAIS (evitam retrabalho):
- BASH_ENV desta VM injeta HERMES_HOME/EXOCORTEX_HOME em todo subshell — ver armadilha acima.
- hindsight_client: `documents.delete_document` é CORROTINA (precisa asyncio.run); retain/recall
  são síncronos. Bank de produção é `exocortex`; em avaliação use bank DEDICADO (`eval-fixture`).
- Excludes canônicos vivem em SKIP_PARTS do indexador (acervo_hindsight_index.py); o catálogo
  herda (CATALOG_SKIP = SKIP_PARTS|{_artifacts}). Inclui _retired,_template,_fixture,_inbox,
  _ops_snapshots,state,raw,_archive,.quarantine,_backup. Mudança de SKIP_PARTS só afeta o catálogo/
  scan após `reindex` (o scan lê o catalog.sqlite existente, não reconstrói sozinho).
- `load_tool_module` do acervoctl faz FALLBACK p/ os tools do installer quando o acervo-alvo não
  tem o módulo — rodar verbo contra o vivo usa CÓDIGO do installer mas lê DADOS (catalog) do vivo.
  P/ propagar mudança de tool ao vivo de verdade: copiar o .py p/ `<vivo>/global/tools/` + reindex.
- LOG À MÃO vai SEMPRE no FIM sob a data estrita `## YYYY-MM-DD` (ascendente, append-only). Prepender
  no topo quebra L-011 e trava o próximo write no escopo. Caminho seguro = `acervoctl` (append+valida).
- Dedup do consolidation-scan: resolver par EN-canônico/PT-órfão com `acervoctl apply-supersede
  --new <canônico> --old <órfão>` (PT vira superseded, histórico preservado). `macro/` é excluído
  do dedup (identity layer git-governado; SOUL.md vs soul.md coexistem legitimamente).
- `_ops_snapshots/` no vivo é congelado — NUNCA migrar; `git checkout` reverte se migrar por engano.
- catalog build = função `build_catalog(root)` (não `build`).
- `$?` depois de pipe captura o exit do último comando do pipe (ex: tail) — redirecione p/ arquivo.
- new-object retorna: ok, operation, type, scope, status, target_path, relative_output, log_path,
  index_path, trust_gate, catalog, hindsight.
- Gateway vivo roda como unidade systemd de USUÁRIO (`systemctl --user ... hermes-gateway`), NÃO
  de sistema. Reinicie após mexer no config: `systemctl --user restart hermes-gateway.service`.
- Todo commit termina com: Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
- Push para main autorizado pelo usuário; ele confirma quando o classificador pedir. O ref local
  `origin/main` pode ficar defasado — confira com `git ls-remote origin -h refs/heads/main`.

HIPÓTESES AINDA ABERTAS (11-hypotheses.md): H1,H3,H4,H5,H6,H7,H8,H9,H10,H11,H12.
H2 resolvido. H4 (grafo) condiciona a Phase 5 — só construir se perguntas multi-hop falharem.

MEMÓRIA PERSISTENTE: /home/ubuntu/.claude/projects/-home-ubuntu/memory/memory-v2-spec.md
tem este mesmo estado (e a armadilha do BASH_ENV).
```

---

## Resumo dos commits (installer `main`, mais recente primeiro)

- `1c4e87e` fix(phase4): paridade da rotina do digest (entrega Telegram) installer↔vivo
- `c8b740c` feat(phase4): syndic ganha a consolidation pass (skill wiring + SOUL)
- `accb1f1` feat(phase4): H12 use-decay — journal de retrieval + bucket use_decay
- `d32b832` feat(phase4): refresh de entidades + distilação de episódios (04 §4)
- `a41e306` feat(phase4): sweep de intenções — write-side governado (08 §6)
- `a281235` docs(memory): refresh do prompt de continuação (read-side + dedup)
   (acervo vivo, repo próprio: `aabd5b5` deploy write-side ← `7bbfba1` dedup ← `2c91e1c` deploy read-side)
- `c71ec03` fix(phase4): dedup ignora superseded/deprecated + macro
- `2e41bd3` fix(skills): guia de placement estrito de log (durabilidade finding #1)
- `4712bfa` feat(phase4): digest semanal de manutenção + purge notices (09 §3)
- `8b07e43` feat(phase4): consolidation scan read-only + exclui _backup do índice
- `d84690b` docs(memory): marca finding #1 resolvido no prompt de continuação
- `ad4c9bc` fix(phase2): migra logs legados _meta/log.md → formato estrito (finding #1) + fix _template
- `5526778` docs(memory): Phase 2 live-rollout report + prompt de continuação
- `1e105be` fix(phase2): step-11b + teste não clobberam mais o ~/.hermes real (finding #2)
  (acervo vivo, repo próprio: `7bbfba1` dedup resolvido ← `2c91e1c` deploy phase4 ← `7e621c8` ops
   maintenance ← `4ef6698` migração de logs finding #1)
- `dc05630` fix(phase2): control plane resolvível + deployável no runtime vivo
- `1169f9e` docs(memory): prompt de continuação (versão anterior)
- `ec7a9b5` Phase 2 — write pipeline + skills v3
- `246b49d` Phase 3 — production retrieval
- `56b947f` H2 resolved — catalog primary, restricted excluded
- `de01176` Phase 1 complete — eval fixture + excludes
- `69703e0` Phase 1 — schema v0.2 migration + catalog + validator v2
- `daa38ad` eval run 2026-07-04 (10/10, plano de junho encerrado)
- `5e5bb98` Phase 0 live addendum + indexer fix
- `9865278` Phase 0 repairs
