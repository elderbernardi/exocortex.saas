
# ADR-008: Personal Intake Workspace para ingestão multicanal

> **Status:** Aceita  
> **Data:** 2026-05-30  
> **Decisor:** @elder  
> **Contexto:** Criar um caminho orgânico e repetível para entrada de arquivos, mídias e links no Exocórtex sem contaminar o Acervo semântico com bruto não curado

## Contexto

O Exocórtex já possuía uma gramática sólida para saída: `_artifacts/`, `artifact_publish.py`, manifesto, receipt e publicação privada no Drive. A metade simétrica de entrada ainda não existia como capability explícita. O PRD já pressupunha onboarding voice-first e processamento de anexos, e o Hermes já oferecia superfícies multicanal nativas. Faltava a área operacional e o workflow que transformam upload espontâneo em memória curada.

## Decisão

Adotar um **Personal Intake Workspace** centrado em `_inbox/`.

A gramática canônica passa a ser:

```text
input -> _inbox -> acervo semântico -> _artifacts -> publish
```

### Regras estruturais

1. Todo arquivo, áudio, imagem, ZIP, link ou lote recebido entra primeiro em `~/.hermes/acervo/_inbox/{intake_id}/`.
2. O canal de entrada não decide o workflow. Todo canal converge para um `IntakeEnvelope` comum.
3. O bruto não entra direto em `knowledge/`, `context/`, `contracts/` ou páginas equivalentes do Acervo.
4. A promoção para memória semântica só ocorre depois de extração e triagem.
5. O caminho de entrada respeita a arquitetura do produto: `USER -> GUI -> SERVER -> HERMES`.

### Estrutura do `_inbox/`

```text
~/.hermes/acervo/_inbox/{intake_id}/
├── original/
├── derived/
├── manifest.json
├── routing.json
└── log.json
```

### Envelope mínimo

```json
{
  "intake_id": "int_YYYYMMDD_HHMMSS_slug",
  "channel": "telegram|whatsapp|email|webhook|api_server|dashboard|cli",
  "received_at": "ISO-8601",
  "content_type": "document|image|audio|video|zip|link|text",
  "original_filename": "...",
  "mime_type": "...",
  "local_cached_path": "...",
  "user_caption": "...",
  "correlation_id": "...",
  "session_ref": "..."
}
```

## Consequências

- Surge uma área operacional explícita para entrada, análoga a `_artifacts/`.
- A ingestão ganha manifesto, hash, MIME, tamanho, roteamento e trilha de promoção.
- O servidor passa a ser o lugar de normalização de upload; o Hermes continua como camada de classificação, triagem e promoção.
- `setup.sh`, bundle e skills do projeto precisam incluir `personal-intake-workspace` para repetibilidade.
- A documentação do projeto e do microverso `hermes-setup` precisa registrar a capability como parte do harness replicável.
