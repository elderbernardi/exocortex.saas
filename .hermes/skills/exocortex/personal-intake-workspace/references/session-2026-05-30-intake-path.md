# Session 2026-05-30 — caminho de ingestão amigável e multicanal

## Contexto

O usuário pediu um desenho orgânico para ingestão de arquivos no Exocórtex. A investigação mostrou que o sistema já tinha a metade de saída bem resolvida (`_artifacts/` + `artifact_publish.py` + receipts), mas não tinha a contraparte explícita de entrada.

## Achados relevantes

1. O Hermes já oferece superfícies multicanal nativas: Telegram, WhatsApp, email, webhook, api_server e outras.
2. O PRD já pressupõe onboarding voice-first e processamento de anexos.
3. O Acervo já diferencia memória semântica de área operacional.
4. O padrão `_artifacts/` já provou uma gramática boa: pacote autocontido + manifesto + receipt + rastreabilidade.

## Decisão de desenho

A entrada deve seguir a mesma lógica arquitetural da saída, mas sem publicar nada:

```text
input -> _inbox -> acervo semântico -> _artifacts -> publish
```

A nova área operacional proposta é:

```text
~/.hermes/acervo/_inbox/{intake_id}/
├── original/
├── derived/
├── manifest.json
├── routing.json
└── log.json
```

## Regra estrutural consolidada

Não usar `micro/{slug}/raw/` nem páginas semânticas como depósito de upload bruto. O destino semântico só é decidido depois da extração e triagem.

## Envelope unificado

Todo canal precisa convergir para um `IntakeEnvelope` com pelo menos:

- `intake_id`
- `channel`
- `received_at`
- `content_type`
- `original_filename`
- `mime_type`
- `local_cached_path`
- `user_caption`
- `correlation_id`
- `session_ref`

Lição durável: canal não decide workflow. Canal só entrega envelope.

## Fluxo recomendado

1. Receber e persistir bruto.
2. Gerar manifesto com hash, MIME, tamanho e status.
3. Extrair texto útil por tipo.
4. Fazer triagem cognitiva com hipótese de destino.
5. Promover para o Acervo, tarefa ou artifact workspace apenas se fizer sentido.

## Canais prioritários

Para MVP de menor atrito:

1. Telegram para captura espontânea do executivo.
2. GUI web com dropzone para upload formal e lote.

Depois expandir para WhatsApp, email forward, webhook e API.

## Posição arquitetural

A solução deve respeitar a arquitetura de produto do usuário:

```text
USER -> GUI -> SERVER -> HERMES
```

O servidor recebe e normaliza. O Hermes interpreta, triageia e promove.

## Pitfalls observados

- Fazer upload direto para Drive como inbox principal.
- Obrigar classificação manual antes do upload.
- Promover ZIP automaticamente.
- Misturar bruto com conhecimento canônico.
- Acoplar regras de negócio do intake ao canal específico.

## Relação com skills existentes

- `personal-artifact-workspace` cobre saída/publicação.
- `personal-intake-workspace` cobre entrada/triagem/promoção.
- Há complementaridade natural entre as duas. Pode haver consolidação futura sob uma skill mais ampla de workspaces operacionais do Exocórtex, se a biblioteca crescer nessa direção.
