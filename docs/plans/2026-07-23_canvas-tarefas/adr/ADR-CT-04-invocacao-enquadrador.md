# ADR-CT-04 — Invocação do enquadrador: turno síncrono streamado vs job+poll

status: proposta (decidir no F0/T6)
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

_(preencher no F0 com os números brutos e a escolha)_

## Consequências

_(preencher no F0: o que muda no desenho da F1 — endpoints, re-attach, timeout)_
