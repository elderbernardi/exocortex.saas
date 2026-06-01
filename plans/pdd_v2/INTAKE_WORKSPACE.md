
# Personal Intake Workspace

Addendum pós-P5 para o Exocórtex. Cria a contraparte de entrada do `ARTIFACT_WORKSPACE.md`.

## Tese

O Exocórtex já tinha um trilho claro para saída final. Faltava um trilho equivalente para entrada crua.

A nova gramática operacional é:

```text
input -> _inbox -> acervo semântico -> _artifacts -> publish
```

## Objetivo

Receber, preservar, extrair, triar e promover arquivos e mídias enviados por múltiplos canais sem usar o Acervo semântico como depósito bruto.

## Workspace canônico

```text
~/.hermes/acervo/_inbox/{intake_id}/
├── original/
│   └── <arquivo ou mídia original>
├── derived/
│   ├── transcript.md
│   ├── ocr.md
│   ├── extracted.md
│   └── preview.json
├── manifest.json
├── routing.json
└── log.json
```

## Arquivos de capability

```text
~/.hermes/acervo/global/contracts/personal-intake-workspace.md
~/.hermes/acervo/global/tools/personal-intake-workspace.md
~/.hermes/acervo/global/tools/intake_ingest.py
~/.hermes/acervo/_inbox/README.md
~/.hermes/skills/exocortex/personal-intake-workspace/SKILL.md
apps/intake_control_plane/intake_http_server.py
apps/intake_control_plane/intake-envelope.schema.json
apps/intake_control_plane/dropzone-demo.html
```

## Princípios

1. Entrada não é memória. Entrada é matéria-prima.
2. Canal não decide workflow. Canal entrega envelope.
3. O original sempre é preservado.
4. A extração tenta gerar Markdown/texto útil por tipo.
5. A promoção semântica é explícita e posterior.
6. Upload bruto não entra direto em `knowledge/`, `context/`, `contracts/` nem `raw/` de microverso.

## Trilhos de extração

- texto/markdown/json/csv/html/xml/yaml -> normalização para `derived/extracted.md`
- PDF -> extração textual local; fallback por utilitário externo quando preciso
- imagem -> OCR local + metadados visuais básicos
- ZIP -> inventário sem promoção automática
- áudio/vídeo -> metadados com `ffprobe`; transcrição fica plugável
- link -> envelope com URL preservada e snapshot simples

## Triagem cognitiva

A resposta esperada ao usuário é curta e útil:

```text
Recebi 1 PDF. Parece ser um plano de ensino.
Extraí 12 páginas.
Sugestão:
- microverso: ensino
- destino provável: knowledge/ ou contracts/
- próxima ação: resumir, arquivar bruto, ou promover para página semântica
```

## Promoção

A capability precisa suportar quatro desfechos:

1. ficar apenas em `_inbox/`
2. virar página semântica no Acervo
3. virar tarefa
4. virar artefato derivado em `_artifacts/`

## Canais priorizados

MVP recomendado:

1. Telegram para captura espontânea
2. GUI web com dropzone para lote e desktop

Expansão posterior:
- WhatsApp
- email forward
- webhook
- api_server

## Control plane de referência

Para preservar a arquitetura oficial `USER -> GUI -> SERVER -> HERMES`, o projeto passa a incluir uma camada HTTP mínima em `apps/intake_control_plane/`:

- `intake_http_server.py`: recebe upload/text/link e chama `intake_ingest.py`;
- `intake-envelope.schema.json`: contrato estável para GUI, gateways e webhooks;
- `dropzone-demo.html`: superfície mínima de teste para upload amigável.

A implementação é deliberadamente sem dependência nova obrigatória. Ela serve como referência executável agora e como contrato de migração para uma futura versão FastAPI.

## Repetibilidade

Para entrar na golden image futura, o projeto precisa preservar:

- contrato do `_inbox/`
- ferramenta `intake_ingest.py`
- skill `personal-intake-workspace`
- `_inbox/README.md`
- documentação no microverso `hermes-setup`
- atualização do `setup.sh` e do bundle
