
---
title: Personal Intake Workspace Tool
created: 2026-05-30
updated: 2026-05-30
nature: ferramentas
kind: tool
scope_mode: global
scope_slug: null
applies_to: [exocortex, hermes, acervo, intake, inbox]
authority: canonical
operational_mode: executable
stability: experimental
sources:
  - global/contracts/personal-intake-workspace.md
derived_from: []
confidence: high
promotion_policy: none
upstream:
  source_skill: exocortex/personal-intake-workspace
  assumed_version: 1.0.0
  coupling: adapter-only
tags: [intake, inbox, extraction, triage, promotion]
---

# Personal Intake Workspace Tool

Ferramenta local para receber, extrair, triar e promover arquivos e mídias para o Acervo.

## Local

```text
~/.hermes/acervo/global/tools/intake_ingest.py
```

## Subcomandos

### Ingestão mínima

```bash
python ~/.hermes/acervo/global/tools/intake_ingest.py ingest   --input /caminho/arquivo.pdf   --channel telegram   --caption "Plano de ensino de SW"
```

### Mostrar manifesto e rota sugerida

```bash
python ~/.hermes/acervo/global/tools/intake_ingest.py show   --intake-id int_20260530_120000_plano-de-ensino
```

### Reanalisar um intake existente

```bash
python ~/.hermes/acervo/global/tools/intake_ingest.py analyze   --intake-id int_20260530_120000_plano-de-ensino
```

### Promover para o Acervo

```bash
python ~/.hermes/acervo/global/tools/intake_ingest.py promote   --intake-id int_20260530_120000_plano-de-ensino   --microverso ensino
```

## Comportamento

- cria pacote em `_inbox/`
- preserva o original em `original/`
- gera `manifest.json`, `routing.json` e `log.json`
- tenta extrair texto útil por tipo
- sugere microverso e diretório funcional
- promove para página semântica em microverso existente
- atualiza `index.md` e `log.md` do escopo alvo

## Extratores locais

A ferramenta usa apenas dependências locais ou opcionais disponíveis no host:

- texto/markdown/json/csv/html/xml/yaml -> leitura direta
- PDF -> `pypdf` com fallback `pdftotext`
- imagem -> `tesseract` + `Pillow`
- ZIP -> inventário via `zipfile`
- áudio/vídeo -> metadados via `ffprobe`

## Limites assumidos

- transcrição de áudio/vídeo continua plugável; hoje a ferramenta registra metadados e placeholder
- não cria microversos novos; promoção exige microverso já existente
- não publica externamente; isso continua fora do escopo da ferramenta
