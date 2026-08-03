# Canvas de Tarefas — Primer do Agente

O **Canvas de Tarefas** é a superfície de execução do Exocortex: cada Tarefa é uma
**sala viva** (EX-06) — um espaço isolado que contém a definição do trabalho, o
trilho de conduta (`conduct.jsonl`) e os artefatos produzidos durante a execução.
O agente lançado nessa sala é o condutor; o Cockpit (hermes-webui) é a janela de
observação em tempo real.

Uma Tarefa existe em três vetores (ver `## Método`) e percorre um loop estrito de
sete fases (ver `## Loop de condução`). O Cockpit reflete o estado do agente
exclusivamente via eventos estruturados publicados no trilho — nunca via prosa
narrada (ver `## Eventos da Sala`). O `## Contrato de consciência` lista o que o
agente lançado DEVE e NÃO DEVE fazer. A integração com colheita e receita é
descrita na seção final deste documento.

---

## Método

Uma Tarefa do Canvas é descrita por um conjunto de campos canônicos:

| Campo | Significado |
|---|---|
| `title` | Nome curto da tarefa |
| `vetor` | `execução` · `evolução` · `manutenção` |
| `done_criteria` | Critério objetivo de conclusão |
| `verification` | Nome da verificação nomeada que o agente DEVE executar |
| `shape` | Formato do entregável (`text` · `file` · `shell_output` · `diff` · …) |

### Vetores

- **execução** — trabalho de objeto externo (redigir ofício, publicar dados, gerar relatório); a verificação é sobre o artefato produzido.
- **evolução** — mudança num componente do próprio ecossistema (skill nova, spec, migração de schema); a verificação é sobre o estado pós-mudança (testes, hash de arquivo, smoke-check).
- **manutenção** — tarefa recorrente, limpeza, rotação de estado; a verificação é sobre a condição-alvo ter sido atingida (contagem, ausência de registros, diff vazio).

### done_criteria e verification

O `done_criteria` define o QUÊ. A `verification` define o COMO provar — é uma
verificação nomeada que o agente executa no passo `verify` do loop. Nunca declarar
"verificado" sem executar a verificação e colar sua saída bruta no trilho (EX-49,
EX-60). A verificação nunca é enfraquecida para passar.

### shape

O `shape` indica ao Cockpit como renderizar o entregável principal. Exemplos:
`text` (resposta em prosa), `file` (artefato salvo no acervo), `shell_output`
(saída de comando colada), `diff` (patch diff), `yaml` / `json` (estruturado).

---

## Loop de condução

O agente conduz a sala usando o método fable com **sete fases** de tokens exatos
(lowercase, sem espaços):

```
classify → define_done → evidence → decide → act → verify → report
```

**Regra fundamental (EX-60):** o **primeiro ato de cada fase** é um append em
`$ACERVO/_tasks/<task_id>/conduct.jsonl` via shell — nunca prosa na resposta.

```bash
printf '%s\n' '{"t":"phase","phase":"<token>","seq":N}' \
  >> "$ACERVO/_tasks/<task_id>/conduct.jsonl"
```

Após o primeiro append, auto-verificar uma vez: `wc -l "$ACERVO/_tasks/<id>/conduct.jsonl"`.

O `task_id` é resolvido UMA VEZ no brief de lançamento ("Task ID para o
conduct.jsonl: `<id>`") e reutilizado em toda a sessão.

### Fases

| Fase | O que acontece | Linha obrigatória no trilho |
|---|---|---|
| `classify` | Identifica vetor e intenção | `{"t":"phase","phase":"classify","seq":N}` |
| `define_done` | Lê `done_criteria` + `verification` nomeada | `{"t":"phase","phase":"define_done","seq":N}` |
| `evidence` | Coleta informação/artefatos necessários | `{"t":"phase","phase":"evidence","seq":N}` + linhas `trace` |
| `decide` | Escolhe abordagem; se ação externa → Draft-First | `{"t":"phase","phase":"decide","seq":N}` |
| `act` | Executa o trabalho; registra artefatos | `{"t":"phase","phase":"act","seq":N}` + linhas `artifact` |
| `verify` | Executa a verificação nomeada; cola saída bruta | `{"t":"phase","phase":"verify","seq":N}` |
| `report` | Entrega resultado; outcome primeiro | `{"t":"phase","phase":"report","seq":N}` |

### Schema das linhas de conduta

```jsonc
// Fase (obrigatória em cada transição)
{"t":"phase","phase":"<token>","seq":N}

// Artefato produzido
{"t":"artifact","title":"…","atype":"…","path":"…","tool":"…"}

// Traço de rastreabilidade
{"t":"trace","kind":"intent|twins|pending","title":"…","evidence":{…}}

// Próximo movimento anunciado
{"t":"next_move","text":"…"}

// Ação externa — Draft-First (EX-08)
{"t":"draft","action":"…","draft_text":"…"}

// Verificação falha (registra cada ciclo; bound A conta a partir do 3º)
{"t":"verify","subject":"…","ok":false,"tried":"…","output":"…","hypothesis":"…"}

// Busca vazia (bound B: para na 2ª)
{"t":"search","query":"…","query_sig":"…","empty":true}

// Surpresa (divergência código/check/spec)
{"t":"surprise","subject":"…","code":"…","check":"…","spec":"…","resolution":"…"}
```

Para a especificação completa das regras de condução, ver **EX-60**
(`skills/excrtx-conduct-loop/SKILL.md`).

---

## Eventos da Sala

O Cockpit (hermes-webui) consome o `conduct.jsonl` via SSE e renderiza cards em
tempo real. Os eventos `sala_*` que a UI reflete são:

| Evento SSE | O que renderiza |
|---|---|
| `sala_phase` | Transição de fase (banner/chip na timeline) |
| `sala_artifact` | Card de artefato (tipo, título, link para path) |
| `sala_finding` | Card de achado relevante durante `evidence` |
| `sala_trace` | Card de rastreabilidade (intent / twins / pending) |
| `sala_gap` | Card de lacuna registrada (bound B ou lacuna de conhecimento) |
| `sala_interrupt` | Card de interrupção sancionada (bound A / escalação) |
| `sala_next_move` | Banner de próximo passo anunciado |
| `sala_kanban` | Atualização do kanban de tarefas (fase → coluna) |
| `sala_draft` | Card de rascunho de ação externa (Draft-First) |

### Draft-First (EX-08)

Quando o agente precisa realizar uma **ação externa** (enviar mensagem, publicar
documento, chamar API com efeito colateral), ele DEVE declarar a ação como uma
linha `draft` **antes** de executá-la:

```jsonc
{"t":"draft","action":"send_email","draft_text":"Prezado …\n\nTexto completo…"}
```

Isso gera um card `sala_draft` visível no Cockpit, permitindo que o executivo
interrompa antes da ação ocorrer. Só após o draft registrado o agente prossegue
(ou aguarda aprovação, dependendo da configuração da sala).

---

## Contrato de consciência

O agente lançado numa sala DO Canvas de Tarefas DEVE:

1. **Escrever conduct por fase** — cada transição de fase gera imediatamente um
   append shell a `conduct.jsonl`; a resposta ao usuário contém o trabalho, não
   a narração do loop.

2. **Nunca narrar fases** — "Classificação:", "Estou na fase verify:", "Fase X:"
   são proibidos na resposta. A fase é sinal out-of-band exclusivamente.

3. **Respeitar Draft-First (EX-08)** — toda ação externa é declarada como linha
   `{"t":"draft",…}` no trilho antes de ser executada. Sem draft, sem ação.

4. **Honrar os bounds (EX-61)**:
   - **Bound A**: após 3 ciclos falha-conserto na MESMA verificação → parar,
     registrar hipótese, invocar `clarify(kind="bound_interrupt")`. Nunca tentar
     um 4º conserto às cegas. Nunca responder um `bound_interrupt` com "use bom
     senso" — re-levantar.
   - **Bound B**: após 2 buscas consecutivas sem informação nova → parar de
     buscar, registrar a lacuna com `{"t":"search",…,"empty":true}`.
   - **Surpresa (código/check/spec)**: registrar `{"t":"surprise",…}` e resolver
     pela ordem de autoridade: executivo > spec > tests > código.

5. **Não fabricar** — nunca declarar uma verificação cumprida sem executá-la e
   colar sua saída bruta no trilho. Se não for possível verificar, dizer isso
   claramente e parar.

6. **Interromper só pelas 3 classes sancionadas** — lacuna só-executivo, mudança
   de rumo, melhoria clara. Canais: `clarify` / `approval`. Nenhum outro canal.

Para a especificação completa dos bounds, ver **EX-61**
(`skills/excrtx-conduct-bounds/SKILL.md`).

---

## Colheita → Receita

Coberto na **Slice B**, após a F4 landar.

> Esta seção será preenchida quando a F4 (Colheita) estiver integrada e os
> endpoints de colheita/receita do Canvas estiverem estabilizados. Por ora, não
> há contrato de colheita documentado aqui.
