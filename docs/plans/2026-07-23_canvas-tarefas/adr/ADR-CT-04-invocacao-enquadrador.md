# ADR-CT-04 — Invocação do enquadrador: turno síncrono streamado vs job+poll

status: decidida
data: 2026-07-23
contexto: meta issue #130 · F0-PLANO.md T3/T6 · questão herdada do RFC acervo-studio §6.2

## Questão

Como a WebUI invoca o turno estruturado do enquadrador (1 frase → núcleo do canvas)?
- **(a) Síncrono streamado**: thread + fila SSE na mesma conexão (como o spike implementa via seam).
- **(b) Job + poll**: registrar job, UI consulta estado (padrão dispatcher do kanban).

## Regra de decisão (aplicar aos números medidos em `scripts/spike_canvas_latency.py`)

- Se **p50 de `done` ≤ 20s** e **first_delta ≤ 8s** nas 3 frases, e a conexão SSE permaneceu estável (nenhuma queda no teste): **(a) síncrono streamado com heartbeat** — menor complexidade, UX de streaming nativa.
- Caso contrário: **(b) job+poll** com endpoint de estado (`/api/canvas/job?id=`) e re-attach de stream.
- Em ambos os casos, a integração definitiva com o runtime in-process (substituir o seam `CANVAS_LLM_CMD`) entra na F1, usando o achado da investigação T3/Step 1.

## Decisão

**(b) job + poll**, com endpoint de estado (`/api/canvas/job?id=`) e re-attach de stream.

Medição real (`scripts/spike_canvas_latency.py`, LLM real via `CANVAS_LLM_CMD=python3 scripts/spike_llm_cmd.py`, DeepSeek `deepseek-v4-pro`, 2026-07-24):

```
'Preparar ofício de renegociação do contrato '   first_delta=18.5s done=18.5s valido=True
'Estou pensando em como estruturar o lançamen'   first_delta=18.4s done=18.4s valido=True
'Revise as pendências do microverso exocortex'   first_delta=13.4s done=13.4s valido=True
```

- `p50(done)` = 18.4s → **≤ 20s, OK**.
- `first_delta` = 18.5s / 18.4s / 13.4s → **nenhuma das 3 ≤ 8s** (o mais rápido, 13.4s, já excede em ~5s). A regra exige as duas condições simultaneamente; a de `first_delta` falha nas 3 frases.
- A conexão SSE permaneceu estável nas 3 (0 erros/drops no log do servidor; as 3 leituras concluíram normalmente até `canvas_done`).

Causa raiz do `first_delta` alto: o seam `spike_llm_cmd.py` faz uma chamada **bloqueante e não-streaming** à API OpenAI-compatible do DeepSeek (sem `stream: true`) — a resposta inteira só chega ao processo depois que o modelo termina de gerar, então `canvas_delta` e `canvas_done` disparam juntos, no fim da latência total do LLM (13-18s). Não há entrega incremental para a UI antes disso. Como a regra exige `first_delta ≤ 8s` para justificar a complexidade extra de manter uma conexão síncrona streamada, e essa condição não se sustenta com o seam atual, a decisão cai no "Caso contrário" da regra escrita: **(b) job+poll**.

## Consequências

- F1 introduz `POST /api/canvas/job` (ou reaproveita `/api/canvas/draft` retornando `job_id`) + `GET /api/canvas/job?id=` para consulta de estado (pending/running/done/error), no padrão dispatcher do kanban já usado no fork.
- A UI faz poll do job e, quando o job sinalizar que há stream disponível (ex. já entrou em execução), pode se re-anexar a um SSE (`/api/canvas/stream?canvas_id=`) para receber os deltas finais — mantendo o mesmo formato de evento (`canvas_snapshot`/`canvas_delta`/`canvas_done`) já validado no spike, só que agora acessado via re-attach em vez de conexão única desde o disparo.
- Timeout do job: medimos até 18.5s numa única chamada real de enquadramento; recomenda-se um timeout de job folgado (sugestão: 60s) para acomodar variância de latência do provider e prompts mais longos que os 3 testados.
- A integração definitiva com o runtime in-process (substituir o seam `CANVAS_LLM_CMD`) fica para a F1 (achado da investigação T3/Step 1), e é o gatilho natural para reavaliar streaming real: se o runtime in-process suportar `stream: true` token-a-token, o cenário (a) síncrono streamado pode ser revisitado então — fora do escopo desta decisão de F0.
