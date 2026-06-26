# Plano — concluir #115 e integrar com o wrapper #99

## Situação de partida

- `#115` agora tem um caminho mínimo funcional real:
  - `scripts/docbrain_to_acervo.py`
  - `skills/excrtx-adapter-docbrain-acervo/SKILL.md`
  - `tests/test_docbrain_to_acervo.py`
- O wrapper `#99 excrtx-research-cpg-brasil` **já existe e está concluído**.
- A convenção explícita do plano operacional diz: integrações novas devem seguir o padrão do wrapper `#99`, não criar um segundo padrão (`docs/plans/prompt-fase4-start.md`).

## Leitura objetiva

Para fechar `#115`, falta sair de "ingestão mínima por microverso explícito" para "ingestão operacional usável pelo pipeline setorial".

O gap principal não é mais parse documental. É **orquestração e resolução de destino**:
1. como o adaptador decide `micro/{empresa}`;
2. como o wrapper `#99` consome documentos como mais uma fonte estruturada;
3. como a síntese final referencia o artefato promovido ao Acervo sem quebrar o contrato atual do briefing.

## Decisão de integração

Integrar `#115` ao **wrapper existente** `skills/excrtx-research-cpg-brasil/scripts/orchestrate.py`.

Não criar um segundo orquestrador para documentos.

### Razão

O wrapper `#99` já sabe consolidar:
- fontes globais (`last30days`)
- fontes web/social (`Agent-Reach`)
- fontes estruturadas públicas (`Google Trends`, `Reclame Aqui`, `CNPJ`)

DocBrain deve entrar como a próxima classe de fonte estruturada: **documentos locais/baixados**.

## Escopo para concluir #115

### Etapa 1 — fechar o contrato do adaptador

Adicionar ao `docbrain_to_acervo.py` um modo de saída estável para consumo por máquina.

### Entrega esperada

- manter a escrita no Acervo;
- retornar JSON final com, no mínimo:
  - `output_file`
  - `relative_output`
  - `document_id`
  - `job_id`
  - `microverso`
  - `entity_candidates` (mesmo que inicialmente simples)
  - `sections_count`
  - `tables_count`
  - `summary_excerpt`

### Observação

A primeira heurística de entidade pode ser conservadora:
- `--microverso` explícito continua tendo precedência;
- sem `--microverso`, aceitar apenas resolução assistida por metadado/argumento simples (`--company`, `--brand`, `--entity-slug`);
- não tentar NER "mágico" ainda.

## Escopo de integração com #99

### Etapa 2 — conectar documentos ao wrapper setorial

Estender `skills/excrtx-research-cpg-brasil/scripts/orchestrate.py` com argumentos como:

```bash
--document /abs/path/doc.pdf          # repetível
--document-microverso comercial       # opcional
--document-company "Girando Sol"     # opcional
--document-output-mode acervo         # default
```

### Comportamento esperado

Para cada documento informado:
1. chamar `scripts/docbrain_to_acervo.py`;
2. capturar o JSON de retorno;
3. incluir o documento como `structured_source` na síntese final;
4. citar o artefato promovido ao Acervo no briefing.

## Contrato de síntese no wrapper #99

### Etapa 3 — novo bloco de fonte estruturada

Hoje o wrapper já agrega:
- Google Trends
- Reclame Aqui
- CNPJ

Adicionar DocBrain como quarta fonte estruturada quando houver documento.

### Resultado esperado no briefing

Exemplo de padrão:

```md
**[docbrain]** Relatório X promoveu 12 seções e 3 tabelas para o Acervo em `micro/empresa/knowledge/arquivo.md`. [↗](file:///...)
```

E em `PADRÕES-CHAVE`:

```md
4. **Documentos promovidos:** 1 documento(s) parseado(s) via DocBrain e anexado(s) ao Acervo.
```

## Testes mínimos para considerar #115 realmente concluída

### Adaptador

- [ ] teste fake existente continua passando
- [ ] teste real com DocBrain local continua passando
- [ ] novo teste cobre retorno JSON para consumo por wrapper
- [ ] novo teste cobre precedência: `--microverso` > heurística/argumento auxiliar

### Wrapper #99

- [ ] teste de CLI com `--document` usando fake adapter
- [ ] teste de síntese inclui bloco `[docbrain]`
- [ ] teste JSON do wrapper expõe `structured_sources.docbrain`
- [ ] smoke local com documento `.md` ou `.pdf` pequeno

## Arquivos-alvo

### Adaptador
- `scripts/docbrain_to_acervo.py`
- `tests/test_docbrain_to_acervo.py`
- `skills/excrtx-adapter-docbrain-acervo/SKILL.md`

### Wrapper #99
- `skills/excrtx-research-cpg-brasil/scripts/orchestrate.py`
- `tests/test_research_cpg_brasil.py`
- `skills/excrtx-research-cpg-brasil/SKILL.md`

## Sequência de execução recomendada

1. estabilizar payload JSON do adaptador;
2. adicionar testes do adaptador para consumo por máquina;
3. plugar `--document` no wrapper #99 com fake adapter em teste;
4. ajustar síntese;
5. rodar testes do wrapper;
6. rodar smoke local com documento pequeno real;
7. só então declarar `#115` concluída.

## Critério real de fechamento

`#115` fecha quando o pipeline completo abaixo estiver verificado:

```text
arquivo local
→ DocBrain parse.create
→ docbrain_to_acervo.py
→ acervo/micro/{slug}/knowledge/*.md
→ wrapper #99 consome o resultado
→ briefing final cita o documento promovido
```

Sem isso, `#115` continua sendo base pronta, não integração concluída.
