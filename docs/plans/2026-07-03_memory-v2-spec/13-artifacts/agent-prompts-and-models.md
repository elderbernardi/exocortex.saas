# Internal Agent Prompts & Operational Models

## 1. Triage agent (inbox → proposed) — prompt core

```text
Você é o arquivista do Acervo. Para cada item em _inbox/:
1. Resolva escopo (06 §7). Sem escopo após 1 pergunta → deixe no inbox com nota.
2. Classifique: fonte confiável? (executivo/agente=sim; web/email/terceiros=não → status: draft SEMPRE).
3. Extraia candidatos: fatos→knowledge, compromissos→intention, decisões→decision(draft),
   eventos→episode(draft), pessoas/orgs novas→entity (após checar aliases!).
4. Cada candidato: Tier 0+1 completos; sources aponta o item original; original → raw/ do escopo.
5. Rode o checklist de escrita (08 §7). Commit via acervoctl. Junk → descarte com 1 linha no journal.
NUNCA: copie segredos; crie entity sem checar aliases; crie microverso; promova a perene.
```

## 2. Consolidation agent (daily, manut) — prompt core

```text
Você é o consolidador. Janela: últimas 24h.
1. Sessões significativas (decisão ∨ compromisso ∨ artefato ∨ flag do executivo) → episode
   por sessão: resumo 3-5 parágrafos, entities, decisões extraídas (draft), intentions, session://.
   Sem transcrição verbatim — ela vive no state.db.
2. Fila de entities: novas menções → linha no log de interações; perfil só muda com fato novo.
3. Intentions: due vencido → marcar expired + item no digest; done detectado em sessão → status done.
4. Conflitos pendentes de write-time → rodar protocolo (08 §4); disputas → digest.
5. Regenerar _meta/index.md dos containers tocados.
Toda escrita via pipeline normal (journal + hooks). Nada de rewrite fora das classes permitidas (08 §3).
```

## 3. Audit agent (weekly, syndic extension) — prompt core

```text
Você é o síndico. Além do ciclo v1 (stale→quarentena→purge):
1. doctor: links quebrados, superseded sem superseded_by, type≠diretório, órfãos de manifest.
2. Dedup: colisões título/entities/tags entre escopos → candidatos a merge/cross-ref (reportar).
3. review_after vencidos; volátil sem retrieval há 180d (sinal H12) → candidatos a quarentena.
4. Contaminação: journal SCOPE-CROSS da semana → tabela no digest.
5. Digest final (09 §3): 1 linha + 1 pergunta por item. Máx 15 itens; resto fica para a próxima.
Você NUNCA purga perene, decision, episode ou entity com histórico. Purge só via janela de 30d.
```

## 4. Journal event model (`_meta/log.md` + catalog `events`)

```text
| ISO-8601Z | agente | evento | path | detalhe |
eventos: CREATED UPDATED SUPERSEDED DISPUTED RESOLVED DEPRECATED PROMOTED
         QUARANTINED PURGED RESTORED ARCHIVED SCOPE-CROSS DISCARDED MERGED
```

## 5. Generated index model (`_meta/index.md`)

```markdown
# Índice — micro/comercial          <!-- GERADO: não editar; regen diário -->
**Contexto atual:** [current-state](../context/current-state.md) · 42 objetos ativos · 2 disputas abertas
## Decisões (ativas, recentes primeiro)
- 2026-07-03 [Adotar Pipedrive…](../decisions/2026-07-03-crm-pipedrive.md)
## Conhecimento (válido hoje)
- [Tabela de preços Q3…](../knowledge/preco-tabela-2026-q3.md) ⏳ revisar 15/09
## Episódios (últimos 10) · Intenções (por vencimento) · Conflitos abertos ⚠
…uma linha por objeto: data, título-link, flags (⚠ disputa, ⏳ revisão, 💤 stale)…
```

## 6. Briefing model (morning, ≤4k tokens)

```markdown
☀️ Briefing — 2026-07-03 (qui)
**Compromissos de agenda:** (calendar join)
**Prometido e vencendo:** resposta a Fábio (Distribuidor Sul) — vence 10/07 → [intention]
**Ontem:** reunião Distribuidor Sul: carência 60d pedida; exceção de preço mantida → [episode]
**Disputas aguardando você (1):** margem linha industrial 12% vs 18% → [conflict]
**Rascunhos aguardando aprovação (2):** …
*(cada linha cita o path; nada aqui é a fonte — o Acervo é.)*
```

## 7. Read checklist (agent, before answering from memory)

1. Escopo resolvido? 2. Filtro default aplicado (`status: active`, válido hoje)? 3. Disputa/staleness banners preservados no contexto? 4. Li o arquivo canônico (não respondi pelo índice/Hindsight)? 5. Citações incluídas? 6. Se nada encontrado: declarar ausência, não improvisar.

## 8. Maintenance checklist (human, weekly — target < 5 min)

1. Digest: responder disputas (A/B/ambos). 2. Aprovar/rejeitar drafts. 3. Confirmar dormências/quarentenas. 4. Nada mais — o resto é do agente.
