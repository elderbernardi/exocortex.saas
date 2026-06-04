# Intake Control Plane Seed

Resumo da lição operacional consolidada nesta sessão.

## Quando aplicar

Quando o Exocórtex já tem a capability cognitiva de intake, mas ainda não tem GUI final ou adapter de gateway pronto.

## Padrão

Interpor uma camada HTTP mínima entre o canal e `intake_ingest.py`.

```text
USER -> GUI/gateway -> intake control plane -> intake_ingest.py -> _inbox -> triagem -> promoção
```

## Contrato mínimo

Endpoints úteis para seed:

- `GET /health`
- `POST /v1/intake/upload`
- `POST /v1/intake/text`
- `POST /v1/intake/link`
- `GET /v1/intake/{intake_id}`
- `POST /v1/intake/{intake_id}/analyze`
- `POST /v1/intake/{intake_id}/promote`

Metadata convergente:

- `title`
- `channel`
- `caption`
- `content_type`
- `correlation_id`
- `session_ref`
- `microverso_hint`

## Regra de separação

- o canal recebe o gesto humano;
- o server normaliza upload e metadata;
- a tool cognitiva decide extração, roteamento e promoção.

Não deixar bot, GUI ou webhook chamar a tool cognitiva diretamente.

## Heurística de rollout

1. Validar primeiro o contract HTTP e o `_inbox`.
2. Plugar uma dropzone simples ou adapter de bot.
3. Só depois sofisticar com framework web, auth, fila ou persistência adicional.

## Valor da seed

Esse seed reduz risco de arquitetura prematura: permite uso real agora e preserva a possibilidade de migrar a implementação sem quebrar o contrato do intake.