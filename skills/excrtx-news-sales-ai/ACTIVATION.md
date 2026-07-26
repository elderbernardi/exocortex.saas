# Ativação do produtor de notícias (modo auto) — handoff para a instância Hermes

> ⚠️ **Executar na instância Hermes de runtime correta** (o host do agente — por `deployment-topology`, a VPS Oracle onde o Hermes roda). **NÃO** no host de desenvolvimento: este host não roda o Hermes. Os passos abaixo ficam **programados** para a instância correta compreender e executar quando o owner autorizar.
>
> Status atual: a skill `excrtx-news-sales-ai` (modo auto macro + modo manual) já está em produção no repo (exocortex `main`). Falta apenas **ativar** o pipeline na instância — provisionar credenciais, fazer o smoke, e criar o cron. Nada aqui foi executado.

## 0. Onde isto roda
- Runtime: a instância Hermes (VPS Oracle `137.131.135.88`, ver memória `deployment-topology`).
- Publicação é **DataBrain-free**: a DataBrain **não** precisa estar up. Escrita só via MCP `sales-ai` com o principal least-privilege `hermes-publisher`.

## 1. Pré-requisitos na instância (checklist)
- [ ] Skill presente e carregável: `python3 scripts/skill_judge.py --skill excrtx-news-sales-ai --d1-only` → PASS.
- [ ] **Credenciais do publisher** no env do runtime (ver `.env.example` desta skill — só chaves; a senha vem do owner, nunca versionada): `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SALES_AI_MCP_AUTH_MODE=password`, `SUPABASE_USER_EMAIL` (hermes-publisher), `SUPABASE_USER_PASSWORD`, `NEWS_CADENCE_STATE`. **PROIBIDO** `SUPABASE_SERVICE_ROLE_KEY` no caminho de publicação.
- [ ] **MCP `sales-ai` wired** (writer v3.1.0, com `skipped_retired`): `hermes mcp add sales-ai --command "node <path>/sales-AI/mcp-server/dist/index.js"` (build `npm run build` antes).
- [ ] Skill de pesquisa operante: `excrtx-research-cpg-brasil` (deps do `crawler-brasil` + `last30days` + `agent-reach`).
- [ ] Estado de cadência: arquivo apontado por `NEWS_CADENCE_STATE` (acervo `exocortex-ops`), criado vazio (`{}`) na 1ª vez.

## 2. Smoke dry-run (antes de publicar — não escreve nada)
```bash
cd skills/excrtx-news-sales-ai
# quais áreas estão vencidas
python3 scripts/news_dispatch.py --config config/noticias.toml --state "$NEWS_CADENCE_STATE" --now $(date +%s)
# pesquisa de uma área (sem DocBrain)
python3 ../excrtx-research-cpg-brasil/scripts/orchestrate.py --template varejo --output json --skip-l30d > /tmp/research.json
# dossier determinístico (reusa build_dossier; NÃO passar --docbrain)
python3 scripts/build_dossier.py --job-context /tmp/ctx.json --crawler /tmp/research.json --agent-reach /tmp/research.json --output-file /tmp/dossier.json
```
Verificar: os candidatos curados têm `url`/`fonte` **reais**; nenhum item inventado; `valido_ate` preenchido (default +30d).

## 3. Publicar 1 área (macro) — ação externa, aprovar via `excrtx-govern-draftfirst`
- Rodar o pipeline do Modo A da `SKILL.md` (passos 1–8). O guard read-before-write (`news_guard.partition`) descarta url já ativa/retirada; o writer `publish_noticia` v3.1.0 é o backstop (`skipped_retired`).
- Conferir `resultado ∈ {created, updated, skipped_retired}` em cada publish.
- **Verificação live**: a notícia aparece no feed "Notícias do Setor" do app Sales-AI. Re-run da mesma área = idempotente (updated/skip, sem duplicar). `expire_noticia` retira uma vencida.

## 4. Criar o cron despachante — ação externa, DRAFT a aprovar na instância
Comando (a instância aprova via Draft-First antes de executar; ajuste hora/persona conforme o runtime):
```bash
hermes cron create \
  --name news-producer-dispatch \
  --schedule "0 6 * * *" \
  --command "<sessão Hermes que carrega excrtx-news-sales-ai no modo auto>"
```
- Cadência do SO **≤** a menor `cadence` da config (áreas hoje = `weekly`; um cron diário serve). O `news_dispatch.py` é o **árbitro real** de quando cada área roda (via `last_run_at`).
- Preencher o `job_id` na entrada `news-producer-dispatch` de `acervo/micro/exocortex-ops/knowledge/cron-registry.md` (hoje "Atribuído na ativação").

## 5. Reversão
- Pausar/remover o cron: `hermes cron delete news-producer-dispatch` (e atualizar o registro).
- Retirar notícias publicadas: `expire_noticia` (nunca DELETE). Não há reativação: re-publicar url retirada = `skipped_retired`.

## Notas
- **Micro (notícias por cliente)** = v2 (fora desta ativação); config + guard já chaveados por `cliente_id`.
- Contrato de referência: `projetob/.harness/contracts/databrain-to-sales-ai.md` v1.24 (seção Noticias). Spec/plano: `docs/plans/2026-07-24_noticias-producer-skill/`.
