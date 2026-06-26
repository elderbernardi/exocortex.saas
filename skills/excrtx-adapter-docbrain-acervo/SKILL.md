---
name: excrtx-adapter-docbrain-acervo
description: Use when Exocórtex precisa transformar a saída estruturada do DocBrain em markdown com provenance pronto para entrada no Acervo.
version: 1.0.0
category: excrtx
platforms: [linux]
metadata:
  hermes:
    tags: [exocortex, docbrain, acervo, intake, documents]
    related_skills: [excrtx-integrate-docbrain, excrtx-memory-manager, excrtx-research-cpg-brasil]
---
# excrtx-adapter-docbrain-acervo — DocBrain → Acervo

## When to Use

Use quando o executivo já tem um arquivo local e precisa do menor caminho verificável entre parse documental e material promocionável no Acervo:
- PDF, DOCX, XLSX, CSV, TXT ou Markdown já disponíveis localmente
- necessidade de preservar `document_id`, `job_id`, `extractor` e arquivo-fonte
- preparação de artefato intermediário em `micro/{slug}/knowledge/` antes de curadoria adicional

**Don't use for:** classificação automática de empresa/produto, criação de microverso novo, ingestão remota via URL sem baixar o arquivo, ou publicação direta em contexto compartilhado.

## Precondições

1. O workspace DocBrain precisa passar em:
   ```bash
   npm run --silent cli -- api health --output json
   ```
2. O microverso de destino já deve existir em `acervo/micro/{slug}/` com `_meta/index.md` e `_meta/log.md`.
3. O arquivo de entrada deve existir localmente.

## Procedure

### Comando principal

```bash
cd /home/elder/projetos/projetob/exocortex.saas
python3 scripts/docbrain_to_acervo.py \
  --input /abs/path/documento.pdf \
  --microverso comercial \
  --acervo-root /abs/path/acervo \
  --docbrain-dir /abs/path/docbrain

# Ou resolver o destino por entidade quando o microverso explícito não vier do chamador
python3 scripts/docbrain_to_acervo.py \
  --input /abs/path/documento.pdf \
  --company "Girando Sol" \
  --acervo-root /abs/path/acervo
```

Saída esperada em stdout:

```json
{
  "ok": true,
  "docbrain_dir": "/abs/path/docbrain",
  "output_file": "/abs/path/acervo/micro/comercial/knowledge/documento.md",
  "relative_output": "micro/comercial/knowledge/documento.md",
  "microverso": "comercial",
  "document_id": "sha256:...",
  "job_id": "job_...",
  "entity_candidates": [
    {"source": "microverso", "value": "comercial", "slug": "comercial"}
  ],
  "sections_count": 12,
  "tables_count": 3,
  "summary_excerpt": "Primeira linha útil do documento"
}
```

## O que o adaptador faz

1. Resolve um workspace DocBrain válido via `api health`.
2. Executa `api parse create --input ... --include tables,sections --output json`.
3. Renderiza markdown estruturado com:
   - frontmatter OKF/Acervo compatível;
   - provenance (`document_id`, `job_id`, `request_id`, `extractor`, `sources`);
   - seções e tabelas em markdown.
4. Grava em `knowledge/` do microverso informado.
5. Atualiza `_meta/index.md` e `_meta/log.md`.
6. Valida o frontmatter com `scripts/validate_frontmatter.py`.

## Verificações

```bash
cd /home/elder/projetos/projetob/exocortex.saas
python3 -m pytest tests/test_docbrain_to_acervo.py -q -m 'not slow'
python3 -m pytest tests/test_docbrain_to_acervo.py -q -m slow
python3 scripts/skill_judge.py --skill excrtx-adapter-docbrain-acervo --d1-only
```

## Pitfalls

1. **Microverso ausente** — o script falha de propósito se `acervo/micro/{slug}` não existe. Não inventa destino.
2. **Workspace errado do DocBrain** — não assumir path fixo. Use `--docbrain-dir` quando houver mais de um checkout.
3. **Frontmatter inválido** — a escrita só é considerada válida se `validate_frontmatter.py` retornar exit code 0.
4. **Sem LLM não é sem parse** — health check e `parse.create` determinístico funcionam sem chave LLM; a chave só importa para caminhos com `--llm`.
5. **Classificação semântica ainda mínima** — agora o adaptador aceita `--entity-slug`, `--company` e `--brand` para resolver o destino; ainda assim a resolução é conservadora por slug e não substitui curadoria de microverso.

## Verification Checklist

- [ ] `api health` respondeu `ok=true` e `api_version=docbrain.cli.v1`
- [ ] o adaptador gerou arquivo `.md` em `micro/{slug}/knowledge/`
- [ ] `_meta/index.md` recebeu a referência do novo arquivo
- [ ] `_meta/log.md` registrou `CREATED:`
- [ ] `scripts/validate_frontmatter.py --file <arquivo>` passou
