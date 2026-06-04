# DocBrain parser-engine case

Contexto: auditoria e hardening do DocBrain para servir como engine documental do intake server, sem abandonar sua função original de wiki.

## Veredito usado

- suficiente como base exploratória de ingestão
- insuficiente, no estado inicial, como engine de parser para o intake server
- boa fundação para evoluir rápido se o contrato operacional for separado da projeção wiki

## Sinais fortes positivos

- estratégia de escalada entre parsers era conceitualmente boa
- LiteParse agregava valor próprio em PDF: OCR, reconstrução espacial, heurística de legibilidade e cifra
- preocupação com provenance já existia
- separação razoável entre adapters, pipeline, wiki, scraper e query
- build, lint e testes passavam após correções

## Gaps estruturais encontrados

### 1. Produto wiki-first, não engine-first

O output principal era `WikiPageDraft` e markdown persistido. Para intake server, o contrato principal precisa ser um resultado estruturado de parsing.

Correção aplicada como padrão: manter `pages[]` para backward compatibility e adicionar `documents[]` com um contrato canônico (`DocumentParseResult` ou equivalente).

### 2. Falta de modo process-only

Uma engine precisa poder processar e retornar JSON sem escrever na projeção wiki.

Correção aplicada como padrão: flag/config `processOnly` + saída `--json`, preservando o fluxo antigo quando o modo não está ativo.

### 3. Chunking cosmético

O sistema aparentava suportar documentos longos, mas a orquestração real não agregava múltiplos chunks em todos os caminhos.

Lição: sempre verificar se há agregação real entre chunks, não apenas split local.

### 4. Governança declarativa fora do runtime

`purpose.md` e `schema.md` eram descritos como orientadores do LLM, mas não eram carregados pela pipeline analisada.

Lição: procurar a leitura efetiva dos arquivos prometidos; documentação sem consumo runtime não é contrato operacional.

### 5. Escalada crítica quebrada por integração

O adapter de Docling apontava para caminho incorreto do script Python. A ideia da escalada era válida; o degrau estava quebrado.

Lição: distinguir falha de integração de falha de desenho. Corrigir o path/adapter antes de descartar a arquitetura.

### 6. Vision fallback prometido, mas não entregue

A pipeline procurava `pdf_to_images.py`, mas o arquivo não existia no repo.

Lição: validar cada degrau até o fim; fallback ausente invalida a promessa operacional.

### 7. Provenance web degradada ao virar arquivo local

A origem web era capturada, mas o caminho local passava a dominar o fluxo.

Lição: separar `source_origin` de `source_artifact_path` e registrar lineage.

### 8. Ausência de idempotência por hash

Para engine de intake, idempotência é requisito estrutural. Sem isso, o mesmo documento renomeado vira múltiplos processamentos e a automação perde previsibilidade.

Correção aplicada como padrão:

- calcular `document_id` por `sha256` do conteúdo quando a fonte é arquivo local
- derivar identidade estável para web a partir de URL/conteúdo
- persistir resultados em store próprio fora da projeção wiki
- tornar a política de reprocessamento explícita

## Padrão de implementação que funcionou

### Contrato canônico

Criar `DocumentParseResult` com, no mínimo:

- identidade/provenance do documento
- texto e markdown normalizados
- seções
- tabelas extraídas
- tentativas de parser (`parser_attempts`)
- qualidade/diagnóstico (`quality`)
- entidades/imagens quando houver suporte real

### Store de jobs

Criar store local com layout previsível:

`.docbrain/parse-jobs/<document_id>/revision-N.json`

Resumo operacional recomendado:

- `job_id`
- `document_id`
- `revision`
- `status`
- `policy`
- `created_at`
- `updated_at`

### Políticas de reprocessamento

- `skip`: se existe job completed para o mesmo hash, retorna resultado persistido e marca como skipped
- `reprocess`: processa novamente e atualiza a revisão corrente
- `new_revision`: processa novamente e cria nova revisão incremental

### CLI/config

Expor a política como flag/config, por exemplo:

`--reprocess-policy skip|reprocess|new_revision`

Manter `--process-only --json` como caminho limpo para consumo por servidor/worker.

### TDD mínimo

Antes de considerar pronto:

- teste do store salvando e recuperando latest por `document_id`
- teste de nova revisão
- teste da pipeline com `skip` sem reprocessar
- teste de regressão garantindo que o modo wiki antigo ainda funciona
- build/lint/test completos

## Mudanças recomendadas que viraram padrão

Quando um repo wiki/CLI local precisar virar engine:

1. separar core engine de projeções downstream
2. criar `DocumentParseResult` ou equivalente
3. mover wiki/search/viewer para consumers posteriores
4. adicionar jobs, status, retries e idempotência
5. persistir parser attempts e artifacts intermediários
6. endurecer chunk aggregation real
7. validar fallbacks por smoke test
8. expor API/worker só depois do contrato engine estabilizado

## Frases úteis de síntese

- “o problema não está na ideia; está no contrato operacional”
- “boa fundação, engine ainda não endurecida”
- “serve como núcleo promissor, não como serviço pronto”
- “não basta ligar a CLI no servidor”
- “preserve a wiki como projeção; promova o parser a contrato primário”
