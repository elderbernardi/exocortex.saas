# Intake Control Plane

Referência mínima para encaixar o Personal Intake Workspace em `USER -> GUI -> SERVER -> HERMES`.

Não é a GUI final. É o trilho canônico de server para:
- receber arquivo, texto ou link;
- normalizar para `IntakeEnvelope`;
- chamar `intake_ingest.py`;
- devolver JSON utilizável por GUI, bot ou webhook.

## Endpoints

- `GET /health`
- `POST /v1/intake/upload` — `multipart/form-data`, campo `file`
- `POST /v1/intake/text` — JSON com `text`
- `POST /v1/intake/link` — JSON com `link`
- `GET /v1/intake/{intake_id}`
- `POST /v1/intake/{intake_id}/analyze`
- `POST /v1/intake/{intake_id}/promote`

## Metadata aceitos

Campos opcionais convergentes:
- `title`
- `channel`
- `caption`
- `content_type`
- `correlation_id`
- `session_ref`
- `microverso_hint`

## Rodar local

```bash
python apps/intake_control_plane/intake_http_server.py --host 127.0.0.1 --port 8765
```

## Smoke test — texto

```bash
curl -sS -X POST http://127.0.0.1:8765/v1/intake/text   -H 'content-type: application/json'   -d '{
    "text": "Ata curta sobre alinhamento do intake multicanal.",
    "title": "Ata intake",
    "channel": "dashboard"
  }' | jq
```

## Smoke test — arquivo

```bash
curl -sS -X POST http://127.0.0.1:8765/v1/intake/upload   -F file=@/caminho/arquivo.pdf   -F channel=dashboard   -F title='Plano de ensino' | jq
```

## Promote explícito

```bash
curl -sS -X POST http://127.0.0.1:8765/v1/intake/INTAKE_ID/promote   -H 'content-type: application/json'   -d '{
    "scope": "micro",
    "microverso": "ensino",
    "functional_dir": "knowledge"
  }' | jq
```

## Uso de canal

Sugestão de `channel`:
- `dashboard` para GUI web/dropzone
- `telegram_gateway` para bot
- `api_server` para integrações HTTP
- `email_bridge` para forward/ingestão por email

A regra continua a mesma: o canal só entrega envelope. A semântica nasce na triagem.
