# DocBrain como engine de processamento para Intake

Contexto: o DocBrain nasceu para o DataBrain antes da adoção Hermes + Exocórtex. Ele trazia wiki própria, mas o Exocórtex já possui acervo/wiki semântica. O ajuste correto foi evitar fork imediato e adicionar modo de somente processamento, mantendo wiki como projeção opcional.

## Decisão durável

Quando um processador documental legado também possui wiki própria, preferir:

```text
parser/processador -> resultado estruturado -> projeções opcionais
```

Em vez de:

```text
parser/processador -> wiki própria -> intake server
```

A wiki do processador pode continuar existindo, mas deve ser uma projeção downstream. O intake server deve consumir um contrato de engine.

## Padrão aplicado no DocBrain

- `IngestPipeline.ingest(input, { persistWiki: false })` retorna resultado sem gravar `wiki/topics` nem reconstruir índice.
- CLI: `docbrain ingest <path> --process-only --json`.
- Modo antigo continua como default para compatibilidade.
- `IngestResult` mantém `pages` para compatibilidade e adiciona `documents[]` como contrato canônico de engine.
- Corrigir caminhos internos de adapters antes de confiar na cadeia de fallback. No caso observado, o `DoclingAdapter` apontava um diretório acima do projeto.
- A camada TypeScript/CLI precisa encaminhar `scraper.mode` até o script Python; suporte escondido só no script não basta.

## Contrato `DocumentParseResult`

Shape inicial recomendado para o intake server:

- `document_id`: hash sha256 quando disponível.
- `source`: provenance do documento.
- `source_artifact_path`: artefato bruto preservado.
- `mime_type`: tipo inferido ou detectado.
- `parser_attempts[]`: parser, status, início/fim, duração, tamanho de texto, qualidade e erro.
- `selected_parser`: último parser bem-sucedido.
- `raw_text`: texto extraído pelo parser selecionado.
- `normalized_markdown`: markdown normalizado para consumo humano/agentes.
- `sections[]`: headings extraídos do markdown.
- `tables[]`: tabelas markdown como objetos `{ columns, rows }`.
- `images[]`, `entities[]`, `citations[]`: listas estruturadas, mesmo que vazias na primeira versão.
- `quality`: status, confiança, tamanho e warnings.
- `warnings[]`, `errors[]`: problemas de parsing e qualidade.
- `llm_enrichment`: `enabled`, `mode`, `model` quando aplicável.
- `projections.wiki_pages`: páginas wiki derivadas, sem obrigar persistência.

Regra: `WikiPageDraft` é projeção. `DocumentParseResult` é contrato.

## Web ingestion policy

Para páginas web:

- `urllib`/fetch: páginas simples e estáticas, sem JS relevante.
- Playwright: renderização determinística, sem consumo de tokens.
- `browser-use`: páginas com interação, consent/cookie banners, navegação dinâmica, login assistido ou extração semântica com LLM.
- `auto`: política configurável de escalada, com logging do caminho escolhido.

`browser-use` não deve substituir todo scraping. Ele é trilho semântico com custo explícito.

## Próximo endurecimento

Depois do modo `process-only` e do `DocumentParseResult`, implementar:

1. `ParseJobStore` próprio antes da projeção wiki.
2. Idempotência por hash.
3. Política `skip | reprocess | new_revision`.
4. Status de job: `pending | processing | completed | failed | partial`.
5. Persistência dos artefatos intermediários por parser.
6. Smoke tests para fallbacks declarados: Docling e Vision.

## Pitfalls

1. Forkar cedo antes de tentar `process-only` aumenta custo sem entregar valor imediato.
2. Fazer o intake server depender de arquivos wiki acopla o produto novo ao drift legado.
3. Ter chunking superficial não significa processar documentos longos; verificar se todos os chunks entram em análise e síntese.
4. Declarar fallback Vision ou Docling sem smoke test cria falsa confiança.
5. Browser-use deve ser trilho semântico com custo explícito, não substituto invisível para todo scraping.
6. Manter `pages` como contrato primário após criar `documents[]` perpetua o drift; migre consumers novos para `documents[]`.
