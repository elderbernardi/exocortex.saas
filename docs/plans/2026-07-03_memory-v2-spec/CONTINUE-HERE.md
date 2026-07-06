# Prompt de Continuação — Exocórtex Memória v2

> Cole o bloco abaixo como primeira mensagem de uma sessão nova. É autossuficiente.
> Última atualização: 2026-07-06 (Phase 2 live rollout concluído; findings #1 E #2 resolvidos;
> logs legados migrados ao formato estrito no installer E no vivo; installer commitado, não pushado).

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
  git remote elderbernardi/exocortex.saas, branch main. TUDO commitado e PUSHADO (HEAD 1e105be).
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

ESTADO ATUAL (2026-07-06):
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

SEM FINDINGS ABERTOS. PRÓXIMO PASSO RECOMENDADO (nesta ordem):
1. PHASE 4 (loop de consolidação): distilação diária de episódios + refresh de entidades +
   varredura de intenções + auditoria de dedup; digest semanal com disputas abertas.
   Construível sobre os verbos da Phase 2. Ver 04-architecture.md §4 e 08-write-policy.md §6.
2. PHASE 6 (harness de avaliação em CI): já existe tests/memory-eval/ (fixture 44 obj + 25
   goldens + run_eval.py). Falta o gate de CI e a regra de regressão (>10pts bloqueia).

COMO VERIFICAR O ESTADO (rode no installer):
  cd /home/ubuntu/.exocortex-installer && git log --oneline -8 && git status -sb
  python3 -m pytest tests/test_acervo_write.py tests/test_acervo_retrieve.py \
    tests/test_acervo_catalog.py tests/test_run_eval.py tests/test_validate_frontmatter_v2.py \
    tests/test_migrate_frontmatter_v2.py tests/test_setup_acervo_mcp.py -q   # ~135 passed
  ACERVO=$PWD/acervo python3 scripts/acervoctl.py doctor    # ok:true
  ACERVO=/home/ubuntu/exocortex/acervo python3 scripts/acervoctl.py doctor  # vivo, ok:true
  python3 -c "import yaml;print(yaml.safe_load(open('$HOME/.hermes/config.yaml'))['mcp_servers']['acervo']['env']['ACERVO'])"
    # deve imprimir /home/ubuntu/exocortex/acervo (se for /tmp/..., reaplique o fix)

APRENDIZADOS OPERACIONAIS (evitam retrabalho):
- BASH_ENV desta VM injeta HERMES_HOME/EXOCORTEX_HOME em todo subshell — ver armadilha acima.
- hindsight_client: `documents.delete_document` é CORROTINA (precisa asyncio.run); retain/recall
  são síncronos. Bank de produção é `exocortex`; em avaliação use bank DEDICADO (`eval-fixture`).
- Excludes canônicos vivem em SKIP_PARTS do indexador (acervo_hindsight_index.py); o catálogo
  herda. Inclui _retired,_template,_fixture,_inbox,_ops_snapshots,state,raw,_archive,.quarantine.
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

- `ad4c9bc` fix(phase2): migra logs legados _meta/log.md → formato estrito (finding #1) + fix _template
- `5526778` docs(memory): Phase 2 live-rollout report + prompt de continuação
- `1e105be` fix(phase2): step-11b + teste não clobberam mais o ~/.hermes real (finding #2)
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
