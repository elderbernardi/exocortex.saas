---
name: excrtx-source-cnpj
description: Public CNPJ collector for Brazilian company registry data via BrasilAPI and ReceitaWS, with normalized JSON envelope and local cache.
version: 1.0.0
category: excrtx
platforms: [linux]
metadata:
  hermes:
    tags: [exocortex, cnpj, brasil, cadastro, company-intelligence, api]
    related_skills: [excrtx-crawler-brasil, excrtx-research-cpg-brasil]
compiled_rules: |
  # This skill does not inject runtime rules; it is a tool-only skill.
---
# excrtx-source-cnpj — Coletor cadastral de empresas brasileiras

## When to Use

Use quando o executivo precisa validar ou enriquecer uma empresa com dados cadastrais públicos:
- razão social e nome fantasia
- data de abertura
- capital social
- situação cadastral
- CNAEs
- quadro societário

**Don't use for:** histórico societário completo, malha de filiais nacional consolidada, dados protegidos por autenticação ou certidões oficiais pagas.

## Procedure

### 1. Executar a CLI

```bash
cd /home/elder/projetos/projetob/exocortex.saas
python3 -m tools.excrtx_source_cnpj.cli "33000167000101" --output json
```

### 2. Ler o envelope de saída

```json
{
  "source": "cnpj",
  "query": "33000167000101",
  "retrieved_at": "2026-06-25T20:24:45Z",
  "data": {
    "cnpj": "33000167000101",
    "razao_social": "...",
    "nome_fantasia": "...",
    "data_abertura": "YYYY-MM-DD",
    "capital_social": 0.0,
    "situacao_cadastral": "ATIVA",
    "cnaes": [],
    "socios": [],
    "filiais": []
  },
  "provenance": {
    "url": "https://brasilapi.com.br/api/cnpj/v1/33000167000101",
    "method": "api",
    "raw_cached": false
  },
  "errors": []
}
```

### 3. Forçar consulta sem cache

```bash
python3 -m tools.excrtx_source_cnpj.cli "33000167000101" --output json --no-cache
```

### 4. Saída textual rápida

```bash
python3 -m tools.excrtx_source_cnpj.cli "33000167000101" --output text
```

## Pitfalls

- **Filiais** — as APIs públicas consultadas retornam o cadastro do CNPJ consultado, não uma malha completa de filiais. O campo `filiais` hoje sai como lista vazia quando a fonte não expõe essa visão consolidada.
- **Rate limit** — ReceitaWS é mais sensível a limite de uso. O coletor tenta BrasilAPI primeiro e só cai para ReceitaWS em fallback.
- **Dados divergentes** — capital social, CNAEs e QSA podem variar levemente entre fontes ou estar defasados. Preserve a `provenance.url` ao citar.
- **Erro parseável** — falha de API ou CNPJ inválido retorna `errors[]` estruturado. Não trate stderr como fonte de verdade; leia o JSON.
- **Cache local** — TTL default de 24h em `/tmp/excrtx-source-cnpj-cache`. Para refresh total, use `--no-cache`.

## Verification

- [x] `python3 -m pytest tests/test_source_cnpj.py -q -m 'not slow'`
- [x] `python3 -m tools.excrtx_source_cnpj.cli --help`
- [x] `python3 -m tools.excrtx_source_cnpj.cli "33000167000101" --output json --no-cache`
- [ ] Integração explícita com `excrtx-research-cpg-brasil` quando a Fase 4 for conectada ao wrapper multi-fonte
