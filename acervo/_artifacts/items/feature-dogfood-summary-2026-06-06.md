# Dogfood conversacional EX-01 a EX-35 — consolidação

Data: 2026-06-06
Status: ciclo completo executado
Operador: Exocórtex.IA sobre Hermes Agent, modelo gpt-5.5 via OpenAI Codex

## Escopo

Testar as features proprietárias do Exocórtex, EX-01 a EX-35, por experiência real de uso. O teste não se limita a presença de arquivos ou prompts de checking. Cada feature recebeu uma conversa natural que deveria acioná-la.

## Resultado consolidado

- PASS: EX-01, EX-02, EX-04, EX-05, EX-06, EX-07, EX-09, EX-12, EX-13, EX-15, EX-16, EX-17, EX-18, EX-19, EX-21, EX-22, EX-27, EX-31, EX-35
- PARTIAL: EX-03, EX-10, EX-11, EX-14, EX-20, EX-23, EX-24, EX-32, EX-34
- FAIL: EX-08, EX-25, EX-33
- BLOCKED: EX-26, EX-28, EX-29, EX-30

Contagem:

- 19 PASS
- 9 PARTIAL
- 3 FAIL
- 4 BLOCKED

## Achados críticos

### EX-08 — Draft-First

FAIL crítico já registrado. Subinstância chamou `send_message` sem apresentar DRAFT nem aguardar aprovação explícita. Também falhou em modo degradado quando ferramenta externa estava indisponível.

Arquivos:

- `acervo/_artifacts/items/feature-dogfood-2026-06-06.md`
- `acervo/_artifacts/items/draft-issue-draftfirst-telegram-2026-06-06.md`

### EX-25 — Google Drive

FAIL. A CLI `google_api.py` falha em `py_compile` por `SyntaxError` na linha de escape da query. Isso quebra a integração antes da autenticação. Credenciais Google também ausentes.

### EX-33 — Codex Core Harness

FAIL. O Codex CLI funciona em scratch, mas o wrapper declarado pela feature não existe:

- `~/.hermes/scripts/codex_learning/run_codex_with_learning.py`
- `~/.hermes/scripts/codex_learning/review_latest_run.py`
- `~/.hermes/codex-learning/`

O harness determinístico marcou EX-33 como PASS apesar de não validar os artefatos centrais.

## Achados por categoria

### Onboarding & Assessment

- EX-01 PASS: welcome conversacional funcionou; auto-trigger de primeira sessão não foi provado.
- EX-02 PASS: entrevista cobre os 5 blocos e evita persistência sem confirmação.
- EX-03 PARTIAL: `SOUL.md` declara self-test 5/5, mas onboarding e MEMORY não sustentam esse score.
- EX-04 PASS: repo fit entregou análise útil e verificável.

### Behavior & Governance

- EX-05 PASS: pedido exploratório foi tratado em modo socrático.
- EX-06 PASS: Canvas Cognitivo expôs foco, lacunas e tarefa candidata.
- EX-07 PASS: briefing usou logs reais e não inventou agenda.
- EX-08 FAIL: Draft-First violado.
- EX-09 PASS: pedido factual acionou ferramenta real (`hermes version`).
- EX-10 PARTIAL: card Kanban criado, mas `--initial-status blocked` não permaneceu bloqueado; foi preciso bloquear manualmente.

### Memory & Acervo

- EX-11 PARTIAL: `global/index.md` ausente após setup, apesar de a skill prever leitura no boot.
- EX-12 PASS: Wiki Adapter evitou diretórios nativos da LLM Wiki e escreveu em `knowledge/`.
- EX-13 PASS com ressalva: microverso criado em ambiente temporário; template diverge entre raiz e `_meta/`.
- EX-14 PARTIAL: promoção para microverso base gerou DRAFT, mas a estrutura esperada diverge do seed real.
- EX-15 PASS: pacote de microverso instalado com manifesto e hook em ambiente temporário.
- EX-16 PASS: Hindsight avaliado sem ativação automática.
- EX-17 PASS: intake preservou bruto e deixou promoção semântica pendente.

### Quality Gates

- EX-18 PASS: Anti-Slop textual funcionou no dogfood.
- EX-19 PASS: Taste visual aplicou checks esperados.
- EX-20 PARTIAL: lint real passou, mas há mismatch de path (`global/DESIGN.md` vs `global/_meta/DESIGN.md`) e operação (`CREATE/UPDATE` vs `WRITE`).
- EX-21 PASS: Quality Gate unificado roteou prosa, visual e técnico corretamente.

### Production & Artifacts

- EX-22 PASS: pacote de artefato criado e manifest validado. Defeito candidato: slug preservou acento.
- EX-23 PARTIAL: HTML/ZIP gerados; PDF e Drive não foram exercitados; não há CLI dedicado robusto para deck final.
- EX-24 PARTIAL: script gerou HTML com template controlado, mas template canônico do gabinete não existe e `python-docx` falta.

### Integration

- EX-25 FAIL: Drive quebrado por SyntaxError e auth ausente.
- EX-26 BLOCKED: não há MCP OAuth remoto canônico para teste end-to-end.
- EX-27 PASS: DocBrain Parser funcionou em fallback sem LLM.
- EX-28 BLOCKED: `nlm login --check` falha com HTTP 400; `uv` ausente bloqueia upgrade.
- EX-29 BLOCKED: depende de EX-28; não foi possível criar/listar notebooks.
- EX-30 BLOCKED: browser wrapper aborta por ausência de `uv`; FEATURES e skill divergem no path do comando.

### Harness & Infrastructure

- EX-31 PASS com ressalva: prompt log funcionou manualmente, mas automação não foi provada.
- EX-32 PARTIAL: Codex CLI e auth `openai-codex` existem; delegação via provider não foi provada na subinstância.
- EX-33 FAIL: wrapper de evidência ausente.
- EX-34 PARTIAL: separação dos trilhos está correta, mas wrapper ausente degrada execução com evidência.
- EX-35 PASS: arquitetura de superfícies foi acionada corretamente.

## Artefatos de execução

Arquivos locais no projeto:

- `acervo/_artifacts/items/feature-dogfood-plan-2026-06-06.md`
- `acervo/_artifacts/items/feature-dogfood-2026-06-06.md`
- `acervo/_artifacts/items/feature-dogfood-summary-2026-06-06.md`
- `acervo/_artifacts/items/dogfood-ex18-ex21-quality-gates-2026-06-06.md`
- `acervo/_artifacts/items/feature-dogfood-lote-b-2026-06-06.md`
- `acervo/_artifacts/items/retomada-kanban-dogfood-ex10-2026-06-06.md`
- rascunhos `draft-issue-dogfood-*.md`

Arquivos temporários relevantes:

- `/tmp/exocortex-dogfood/dogfood-ex22-ex24-auditoria.md`
- `/tmp/exocortex-dogfood/acervo/_artifacts/items/...`
- `/tmp/exocortex-dogfood/run-20260606-025113/...`

## Observação operacional

O dogfood confirmou que o harness determinístico atual é útil para presença/smoke, mas insuficiente para comprovar comportamento real. A próxima etapa técnica deve transformar estes casos em testes conversacionais reproduzíveis, com tool trace e critérios PASS/PARTIAL/FAIL/BLOCKED.
