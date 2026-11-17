> **Escopo operacional vigente:** consultar `databrain_execution_status` e o runbook DataBrain `ops/EXECUTION_CONTROL.md` antes de usar estados/versões históricos deste documento. Gates são locais via `pb heavy`; o perfil factual atual é `semantic-v1`. Instruções de segurança, publicação ampla e autorização deste documento continuam aplicáveis.

# Publisher: escopo efetivo e Judge automático

## Judge automático

Antes de estimar custo ou afirmar que houve avaliação por LLM, leia a cauda do log do Judge. A configuração pode conter `judge.auto_approve=true`.

Nesse modo:
- os insights pendentes são aprovados administrativamente;
- `llm_calls` e tokens podem ser zero;
- não há avaliação dimensional de qualidade pelo Judge;
- os filtros do Hot continuam sendo a última barreira qualitativa prévia.

Relate isso de forma explícita. “Judge concluído” não significa necessariamente “Judge avaliou por LLM”.

## DRAFT de publicação

`publish` é amplo. Além de Gold/Hot/Judge, o Publisher pode:
- atualizar dimensões e carteiras (`cliente_acesso`);
- expirar e inserir insights/inbox;
- publicar histórico cliente×produto, preços, ranking e estatísticas de filiais;
- consolidar filiais sob a matriz e remover artefatos derivados de filiais.

Não deduzir o volume final apenas do Hot ou da execução isolada do Judge. O Publisher combina arquivos Gold vigentes, artefatos históricos ainda efetivos e alertas derivados, e por isso pode publicar mais insights e briefings do que a última Hot gerou.

Antes do DRAFT, use `dry_run` para validar orquestração quando houver risco de escopo; ele não prova mapeamento de dados nem fornece contagens finais. O DRAFT deve declarar que a publicação é ampla e listar as famílias de dados afetadas. Após aprovação, execute apenas com `approval_ref` pós-DRAFT.

## Verificação pós-publicação

Exigir:
1. `operation_status=succeeded` e exit code 0;
2. linha final `Publisher Stage Completed` com `errors: 0`;
3. registros `Publish log recorded` para cada artefato crítico;
4. identificação do `runId` e duração.

Um warning recuperável, como timeout na leitura de conteúdo anterior de briefing seguido de fallback explícito e upsert concluído sem erros, não torna a publicação falsa. Reportar como ressalva: a publicação foi concluída, mas o reaproveitamento de conteúdo anterior ficou degradado e deve ser corrigido antes do próximo ciclo.
