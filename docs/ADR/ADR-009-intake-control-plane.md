# ADR-009: Intake Control Plane como camada canônica entre GUI/gateway e Hermes

> Status: Aceita
> Data: 2026-05-30
> Decisor: @elder
> Contexto: encaixar a capability de intake multicanal em uma superfície amigável sem romper a arquitetura USER -> GUI -> SERVER -> HERMES

## Contexto

O Personal Intake Workspace já definiu a semântica do `_inbox/`, do `IntakeEnvelope` e da promoção posterior para o Acervo. Faltava a camada prática de server para receber upload HTTP, texto ou link de forma uniforme e chamar a ferramenta cognitiva sem acoplar Telegram, dashboard ou futura GUI diretamente ao Hermes.

## Decisão

Adotar um Intake Control Plane mínimo como trilho canônico de entrada.

A arquitetura operacional fica:

```text
USER -> GUI/gateway -> intake control plane -> intake_ingest.py -> _inbox -> triagem -> promoção
```

### Regras

1. GUI, bot ou webhook falam HTTP com o control plane; não chamam `intake_ingest.py` diretamente.
2. O control plane normaliza inputs para o mesmo shape de metadata do `IntakeEnvelope`.
3. O Hermes continua responsável por extração, roteamento e promoção; o server não decide semântica.
4. Upload binário fica na camada de server; a camada cognitiva recebe caminho local temporário ou payload textual já normalizado.
5. A implementação de referência deve rodar sem dependências novas obrigatórias.

## Implementação de referência

Entram no projeto:

- `apps/intake_control_plane/intake_http_server.py`
- `apps/intake_control_plane/intake-envelope.schema.json`
- `apps/intake_control_plane/dropzone-demo.html`
- `apps/intake_control_plane/README.md`

Endpoints mínimos:

- `GET /health`
- `POST /v1/intake/upload`
- `POST /v1/intake/text`
- `POST /v1/intake/link`
- `GET /v1/intake/{intake_id}`
- `POST /v1/intake/{intake_id}/analyze`
- `POST /v1/intake/{intake_id}/promote`

## Consequências

- O caminho amigável para GUI web passa a existir já no projeto, sem exigir Next.js ou FastAPI neste estágio.
- Telegram, email bridge e outros canais agora podem ser meros adapters HTTP para o mesmo server.
- A futura branch Code pode trocar a implementação mínima por FastAPI sem quebrar o contrato externo.
- O rollout segue progressivo: primeiro server local e dropzone; depois adapters de gateway.
