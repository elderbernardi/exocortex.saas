# Concrete File Examples (schema v0.2)

## 1. Knowledge with validity window — `micro/comercial/knowledge/preco-tabela-2026-q3.md`

```markdown
---
schema: acervo/v0.2
type: knowledge
title: Tabela de preços 2026-Q3 aprovada com reajuste de 8%
description: Reajuste aprovado em 2026-06-28; vigora 01/07–30/09
tags: [pricing, tabela]
created_at: 2026-07-03T14:00:00Z
class: volátil
status: active
epistemic: fact
confidence: high
sources:
  - {type: conversation, ref: "session://tg-2026-06-28#dec-1"}
observed_at: 2026-06-28
valid_from: 2026-07-01
valid_until: 2026-09-30
extraction: agent
entities: [gpq]
supersedes: [micro/comercial/knowledge/preco-tabela-2026-q2.md]
review_after: 2026-09-15
---
Reajuste linear de 8% sobre a tabela Q2, aprovado pelo diretor em 2026-06-28.
Exceção: linha industrial mantém preço de Q2 até renegociação com [[distribuidor-sul]].
```

## 2. Decision — `micro/comercial/decisions/2026-07-03-crm-pipedrive.md`

```markdown
---
schema: acervo/v0.2
type: decision
title: Adotar Pipedrive como CRM da diretoria comercial
description: Substitui planilhas; decidido 2026-07-03; revisão em 6 meses
tags: [crm, ferramentas]
created_at: 2026-07-03T15:00:00Z
class: perene
status: active
epistemic: decision
confidence: high
sources: [{type: executive, ref: "session://tg-2026-07-03#turn-41"}]
observed_at: 2026-07-03
extraction: agent
entities: [gpq, pipedrive]
review_after: 2027-01-03
---
## Contexto
…
## Decisão
…
## Alternativas rejeitadas
- HubSpot: custo; - Planilhas: sem histórico de interação.
## Consequências
…
```

## 3. Episode — `micro/clientes/episodes/2026-07-02-reuniao-distribuidor-sul.md`

```markdown
---
schema: acervo/v0.2
type: episode
title: Reunião com Distribuidor Sul — renegociação linha industrial
description: Fábio pediu carência de 60d; ficou de responder até 10/07
tags: [negociacao]
created_at: 2026-07-03T05:10:00Z
class: perene
status: active
epistemic: observation
confidence: high
sources: [{type: conversation, ref: "session://tg-2026-07-02"}]
observed_at: 2026-07-02
extraction: pipeline
entities: [distribuidor-sul, fabio-mendes]
relates_to: [micro/comercial/knowledge/preco-tabela-2026-q3.md]
---
**Resumo.** …3 parágrafos, sem transcrição…
**Decisões:** manter preço Q2 na linha industrial (ver knowledge).
**Pendências geradas:** [[2026-07-02-resposta-carencia-distribuidor-sul]] (intention).
```

## 4. Entity — `shared/entities/fabio-mendes.md`

```markdown
---
schema: acervo/v0.2
type: entity
title: Fábio Mendes — diretor de compras, Distribuidor Sul
description: Contato principal na renegociação; prefere WhatsApp, manhãs
tags: [pessoa, cliente]
created_at: 2026-06-01T10:00:00Z
class: perene
status: active
epistemic: observation
confidence: high
sources: [{type: conversation, ref: "session://tg-2026-06-01"}]
observed_at: 2026-06-01
extraction: agent
aliases: ["Fábio", "Fabio Mendes", "diretor de compras do Sul"]
entities: [distribuidor-sul]
---
## Perfil          <!-- rewrite-in-place -->
Diretor de compras do [[distribuidor-sul]]. Direto, sensível a prazo, não a preço.
## Interações      <!-- append-only -->
- 2026-07-02 — renegociação linha industrial → [[2026-07-02-reuniao-distribuidor-sul]]
- 2026-06-01 — primeira reunião, apresentação de portfólio
```

## 5. Intention — `micro/clientes/intentions/2026-07-02-resposta-carencia-distribuidor-sul.md`

```markdown
---
schema: acervo/v0.2
type: intention
title: Responder a Fábio sobre carência de 60d até 10/07
description: Compromisso assumido na reunião de 02/07
tags: [compromisso]
created_at: 2026-07-03T05:12:00Z
class: volátil
status: active
epistemic: intention
confidence: high
sources: [{type: conversation, ref: "session://tg-2026-07-02"}]
observed_at: 2026-07-02
extraction: pipeline
entities: [fabio-mendes, distribuidor-sul]
due: 2026-07-10
owed_to: fabio-mendes
---
Prometido pessoalmente na reunião. Depende da decisão sobre fluxo de caixa (consultar financeiro).
```

## 6. Conflict — `micro/comercial/knowledge/conflito-margem-linha-industrial.md`

```markdown
---
schema: acervo/v0.2
type: conflict
title: Conflito — margem real da linha industrial (12% vs 18%)
description: BI aponta 12%; controladoria reportou 18% em maio
tags: [margem, industrial]
created_at: 2026-07-03T16:00:00Z
class: volátil
status: active
epistemic: hypothesis
confidence: possible
sources:
  - {type: document, ref: "micro/bi-inteligencia-comercial/knowledge/margens-2026-h1.md"}
  - {type: document, ref: "micro/comercial/raw/relatorio-controladoria-maio.pdf"}
observed_at: 2026-07-03
extraction: agent
entities: [gpq]
relates_to:
  - micro/bi-inteligencia-comercial/knowledge/margens-2026-h1.md
---
**Claim A (BI, 2026-06-30, confidence: high):** margem 12% — método: custo médio.
**Claim B (controladoria, 2026-05-15, confidence: likely):** 18% — método: custo padrão.
**Diferença provável:** critério de custeio. **Aguardando resolução do executivo.**
```

## 7. Cross-ref — `shared/cross-refs/comercial--clientes--distribuidor-sul.md`

```markdown
---
schema: acervo/v0.2
type: knowledge
title: Ponte — pricing comercial ↔ negociação Distribuidor Sul
description: Preço da linha industrial em Q3 é exceção negociada no cliente
tags: [cross-ref]
created_at: 2026-07-03T16:30:00Z
class: volátil
status: active
epistemic: fact
confidence: high
sources: [{type: agent-inference, ref: "consolidation-2026-07-03"}]
observed_at: 2026-07-03
extraction: pipeline
relates_to:
  - micro/comercial/knowledge/preco-tabela-2026-q3.md
  - micro/clientes/episodes/2026-07-02-reuniao-distribuidor-sul.md
---
A exceção de preço Q3 (comercial) origina-se da renegociação com o Distribuidor Sul
(clientes). Detalhes em cada escopo. **Somente ponteiro — sem conteúdo copiado.**
```
