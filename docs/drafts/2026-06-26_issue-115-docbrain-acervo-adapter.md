# DRAFT — comentário da issue #115

Implementei o menor avanço verificável do pipeline DocBrain → Acervo, com evidência real no runtime local.

## Entregáveis criados

- `scripts/docbrain_to_acervo.py`
- `skills/excrtx-adapter-docbrain-acervo/SKILL.md`
- `tests/test_docbrain_to_acervo.py`
- `pytest.ini` (registro do marker `slow`)
- migração do adaptador para o control plane oficial do Acervo (`acervoctl`)

## O que a primeira versão já faz

1. Resolve um workspace DocBrain válido via `api health`
2. Executa `api parse create --input ... --include tables,sections --output json`
3. Renderiza markdown com frontmatter + provenance
4. Escreve em `acervo/micro/{slug}/knowledge/{documento}.md`
5. Atualiza `_meta/index.md` e `_meta/log.md`
6. Valida o frontmatter com `scripts/validate_frontmatter.py`

## Evidência executada

### Testes automatizados

```bash
cd /home/elder/projetos/projetob/exocortex.saas
python3 -m pytest tests/test_docbrain_to_acervo.py -q
python3 scripts/skill_judge.py --skill excrtx-adapter-docbrain-acervo --d1-only
```

Resultado:
- `pytest`: `2 passed`
- `skill_judge --d1-only`: `PASS`

### Smoke real do adaptador

```bash
cd /home/elder/projetos/projetob/exocortex.saas
python3 scripts/docbrain_to_acervo.py \
  --input /home/elder/projetos/projetob/docbrain/purpose.md \
  --microverso exocortex-dev \
  --acervo-root /home/elder/projetos/projetob/exocortex.saas/acervo \
  --docbrain-dir /home/elder/projetos/projetob/docbrain \
  --output-name purpose-docbrain-smoke
```

Resultado validado:
- arquivo criado: `acervo/micro/exocortex-dev/knowledge/purpose-docbrain-smoke.md`
- `document_id`: `sha256:52bfcb6cb1319f92d289a873b5413322ea3d983d04d9c3bd6a1a5327c0c36f57`
- `job_id`: `job_507f7823-6db0-415c-9fb5-67622814f99e`
- `sections`: `4`
- `tables`: `0`
- `_meta/index.md` atualizado
- `_meta/log.md` registrou `CREATED:`

## Escopo entregue vs. escopo pendente

### Entregue agora
- pipeline mínimo funcional DocBrain → markdown no Acervo
- provenance explícita (`document_id`, `job_id`, `request_id`, `extractor`, `sources`)
- guarda de escrita no microverso informado
- teste fake end-to-end + smoke real contra DocBrain local

### Ainda pendente nesta issue
- classificação automática por entidade (empresa/produto/categoria)
- decisão automática de `micro/{empresa}`
- integração com o skill-wrapper CPG (#99)
- heurística de wikilinks e enriquecimento semântico
- ampliar smoke automatizado para fixture PDF/planilha, se quisermos cobrir mais de um extrator dentro da própria suite

## Ajustes correlatos de contrato/documentação

Para reduzir drift enquanto implementava o adaptador, alinhei também:
- `.harness/contracts/exocortex-to-docbrain.md`
- `README.md`
- `FEATURES.md`
- `skills/excrtx-integrate-docbrain/SKILL.md`
- `skills/excrtx-harness-surfaces/references/local-cli-api-contracts.md`

## Leitura objetiva

A issue ainda não está completa no sentido ambicioso original, mas agora existe base real, testada e utilizável para continuar a Fase 5 sem inventar arquitetura no vazio.
