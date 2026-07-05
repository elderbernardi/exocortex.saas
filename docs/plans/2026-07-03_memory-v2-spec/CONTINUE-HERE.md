# Prompt de Continuação — Exocórtex Memória v2

> Cole o bloco abaixo como primeira mensagem de uma sessão nova. É autossuficiente.
> Última atualização: 2026-07-05 (fim da Phase 2, installer).

---

```
Você está continuando a implementação da reforma de memória do Exocórtex.IA (Hermes Agent).
A especificação completa e canônica está em:
/home/ubuntu/.exocortex-installer/docs/plans/2026-07-03_memory-v2-spec/

LEIA PRIMEIRO, nesta ordem:
1. README.md (índice e sumário executivo)
2. 12-roadmap.md (as 8 fases; onde estamos)
3. phase-0-report.md, phase-1-report.md, phase-2-report.md, phase-3-report.md (o que já foi feito)
4. report/h2-2026-07-04.md (experimento H2 resolvido)
5. 05-object-model.md + 13-artifacts/SCHEMA-v0.2.md (o schema canônico v0.2)
6. 08-write-policy.md e 07-retrieval-policy.md (os pipelines em produção)

DOIS REPOSITÓRIOS / DUAS SUPERFÍCIES:
- INSTALLER (fonte canônica de código/schema/skills): /home/ubuntu/.exocortex-installer
  git remote elderbernardi/exocortex.saas, branch main. TUDO já commitado e pushado.
- INSTÂNCIA VIVA (dados + runtime reais do executivo Gabriel Bonavigo):
  /home/ubuntu/exocortex/acervo (agora é repo git próprio, local, sem remote) e ~/.hermes.

FRONTEIRA COMBINADA COM O EXECUTIVO (respeite sempre):
- Escreva no INSTALLER livremente.
- NÃO toque na instância viva (~/exocortex, ~/.hermes) sem autorização explícita do usuário.
  Quando uma fase exigir o vivo: avise, faça backup (o acervo vivo tem git — use git tag/commit),
  e peça go. Já foram autorizados e feitos no vivo: git init, migração v0.2 (234 arq),
  consolidação do MEMORY.md, re-scan do índice. O ROLLOUT VIVO DA PHASE 2 (skills v3 +
  control plane) AINDA NÃO foi autorizado — as skills governam o agente real.

ESTADO ATUAL (2026-07-05):
- Fase 0 (reparos de drift + baseline): COMPLETA. Vivo: MEMORY.md 26%, AcervoIndex 163 entradas.
- Bateria de memória de junho (Fase 8 do plano antigo): 10/10, plano memory-excellence ENCERRADO.
- Fase 1 (schema v0.2 + catalog.sqlite + validador v2 + migrador + fixture de avaliação): COMPLETA.
  Migrados: installer 162, vivo 234. `acervoctl reindex`/`doctor` limpos nas duas pontas.
- H2 (agentic vs semantic): RESOLVIDO — catálogo é primário (+4.5pts < +5); Hindsight opcional.
  Achado de segurança corrigido: AcervoIndex vazava conteúdo `sensitivity: restricted` entre
  escopos → indexador agora pula restricted (installer+vivo).
- Fase 3 (retrieval de produção, `acervoctl retrieve`): COMPLETA. 100% recall, 0 contaminação,
  2/3 abstenção nas 25 perguntas-ouro.
- Fase 2 (write pipeline): COMPLETA NO INSTALLER (rollout vivo pendente de go).
  Verbos: `acervoctl conflict-check|apply-supersede|open-dispute|new-object`.
  Skills v3: excrtx-memory-manager v3.0, -deprecate v2.0, -newmicro v3.0.

PRÓXIMO PASSO RECOMENDADO (nesta ordem):
1. ROLLOUT VIVO DA PHASE 2 (pedir go ao usuário): sincronizar para ~/.hermes as skills
   excrtx-memory-{manager,deprecate,newmicro} + rtn_inbox_triage + compile_soul, e para
   /home/ubuntu/exocortex/acervo/global/tools os scripts do control plane; rodar
   `hermes chat -q` provando um ciclo real (new-object intention → conflict-check → retrieve).
   Fazer backup git no vivo antes. Verificar que compiled_rules entraram no SOUL vivo.
2. PHASE 4 (loop de consolidação): distilação diária de episódios + refresh de entidades +
   varredura de intenções + auditoria de dedup; digest semanal com disputas abertas.
   Construível sobre os verbos da Phase 2. Ver 04-architecture.md §4 e 08-write-policy.md §6.
3. PHASE 6 (harness de avaliação em CI): já existe tests/memory-eval/ (fixture 44 obj + 25
   goldens + run_eval.py). Falta o gate de CI e a regra de regressão (>10pts bloqueia).

COMO VERIFICAR O ESTADO (rode no installer):
  cd /home/ubuntu/.exocortex-installer && git log --oneline -8
  python3 -m pytest tests/test_acervo_write.py tests/test_acervo_retrieve.py \
    tests/test_acervo_catalog.py tests/test_run_eval.py tests/test_validate_frontmatter_v2.py \
    tests/test_migrate_frontmatter_v2.py -q          # deve dar ~133 passed
  ACERVO=$PWD/acervo python3 scripts/acervoctl.py doctor    # ok:true
  ACERVO=/home/ubuntu/exocortex/acervo python3 scripts/acervoctl.py doctor  # vivo, ok:true

APRENDIZADOS OPERACIONAIS (evitam retrabalho):
- hindsight_client: `documents.delete_document` é CORROTINA (precisa asyncio.run); retain/recall
  são síncronos. Suprima ruído de aiohttp "unclosed session".
- Bank Hindsight de produção é `exocortex`; para avaliação use bank DEDICADO (`eval-fixture`),
  nunca escreva no `exocortex` em testes.
- Excludes canônicos vivem em SKIP_PARTS do indexador (acervo_hindsight_index.py); o catálogo
  herda. Inclui _retired, _template, _fixture, _inbox, _ops_snapshots, state, raw, _archive, .quarantine.
- `_ops_snapshots/` no vivo é congelado — NUNCA migrar; se migrar por engano, `git checkout` reverte.
- catalog build = função `build_catalog(root)` (não `build`).
- `$?` depois de um pipe captura o exit do último comando do pipe (ex: tail) — redirecione p/ arquivo.
- new-object retorna chaves: ok, operation, type, scope, status, target_path, relative_output,
  log_path, index_path, trust_gate, catalog, hindsight.
- Agentes delegados batem no limite Fable 5 em tarefas longas; para trabalho longo, prefira
  fazer inline ou fatiar em subtarefas menores. Retomar agente: SendMessage com o agentId.
- Todo commit termina com: Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
- Push para main foi autorizado pelo usuário; ele confirma pushes quando o classificador pedir.

HIPÓTESES AINDA ABERTAS (11-hypotheses.md): H1,H3,H4,H5,H6,H7,H8,H9,H10,H11,H12.
H2 resolvido. H4 (grafo) condiciona a Phase 5 — só construir se perguntas multi-hop falharem.

MEMÓRIA PERSISTENTE: há um arquivo em
/home/ubuntu/.claude/projects/-home-ubuntu/memory/memory-v2-spec.md com este mesmo estado.
```

---

## Resumo dos commits (installer `main`, mais recente primeiro)

- `ec7a9b5` Phase 2 — write pipeline + skills v3
- `246b49d` Phase 3 — production retrieval
- `56b947f` H2 resolved — catalog primary, restricted excluded
- `de01176` Phase 1 complete — eval fixture + excludes
- `69703e0` Phase 1 — schema v0.2 migration + catalog + validator v2
- `daa38ad` eval run 2026-07-04 (10/10, plano de junho encerrado)
- `5e5bb98` Phase 0 live addendum + indexer fix
- `9865278` Phase 0 repairs
