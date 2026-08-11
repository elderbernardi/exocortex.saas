# Single-stage low-cost editorial self-gate

## Objetivo

Usar **uma única chamada de LLM barata** na borda editorial micro para fazer duas coisas em sequência lógica:

1. julgar se o candidato faz sentido para aquele cliente;
2. **só se fizer sentido**, redigir headline, resumo e justificativa curta.

Isso reduz complexidade operacional sem abrir mão da trava semântica final.

## Quando usar

Use quando o pipeline determinístico já resolveu:
- carteira congelada
- matching mínimo
- dedupe
- frescor
- lookup/guard read-before-write

A LLM não entra no universo bruto. Ela recebe apenas `pre_llm_publishable.json` ou subconjunto equivalente.

## Princípio

A LLM **não corrige identidade estrutural do pipeline**. Ela atua como:
- trava contra absurdo
- filtro de colisão semântica
- borda editorial que só escreve quando a relação cliente↔sinal é plausível e comercialmente relevante

Exemplos de absurdo que ela deve barrar:
- pessoa com mesmo nome do cliente
- lugar/conceito com o mesmo token da marca
- notícia genérica sem implicação comercial clara
- menção fraca sem vínculo com a rede alvo

## Contrato de entrada recomendado

Para cada item, enviar um envelope autocontido com:

```json
{
  "cliente": {
    "cliente_id": "uuid",
    "nome": "SUPERMERCADO BRUDA LTDA",
    "nome_fantasia": "CD BRUDA",
    "cidade": "CANOINHAS",
    "uf": "SC",
    "access_types": ["titular"],
    "tabela_atual": "198 - BRUDA FOB 10% 2026",
    "rfm_label": "Cliente fiel"
  },
  "sinal": {
    "title": "Bruda inaugura duas novas lojas em uma semana",
    "snippet": "...",
    "fonte": "samais",
    "url": "https://...",
    "publicado_em": "2026-08-05",
    "match_score": 95,
    "match_reasons": ["brand:bruda", "alias:bruda"]
  },
  "task_context": {
    "goal": "decidir se o item deve virar notícia micro para este cliente e só então redigir",
    "rules": [
      "não pesquisar",
      "não inventar fatos",
      "não assumir vínculo fraco",
      "descartar colisão de nome sem relação comercial",
      "escrever apenas se a decisão for publica"
    ]
  }
}
```

## Contrato de saída recomendado

A saída deve ser JSON estrito. Regra: se `decision != publica`, os campos editoriais ficam `null`.

```json
{
  "decision": "publica|revisa|descarta",
  "confidence": "alta|media|baixa",
  "reason": "1 linha objetiva",
  "headline": "string|null",
  "summary": "string|null",
  "commercial_why": "string|null",
  "impacto": "positivo|negativo|neutro|null"
}
```

## Política de decisão

### `publica`
Use quando:
- o vínculo cliente↔sinal parece plausível no próprio envelope;
- o item representa expansão, investimento, mudança estrutural, movimento competitivo, logística, sortimento, canal ou sinal comercial útil;
- não há indício forte de colisão de nome.

### `revisa`
Use quando:
- existe alguma plausibilidade, mas falta segurança semântica;
- o item parece potencialmente relevante, porém ambíguo;
- a notícia pode ser verdadeira para a rede, mas o envelope não está suficientemente claro.

### `descarta`
Use quando:
- o item é absurdo para o cliente;
- o token da marca apareceu por coincidência;
- o item não tem implicação comercial clara;
- a notícia é curiosidade, institucional ou genérica demais.

## Prompt canônico

```text
Você é a borda editorial micro do pipeline de notícias.

Receba apenas o envelope fornecido. Não pesquise, não invente, não use conhecimento externo.

Sua tarefa ocorre em duas etapas obrigatórias:
1. decidir se esta notícia realmente faz sentido para este cliente e se tem relevância comercial suficiente;
2. só se fizer sentido, escrever headline curta, resumo curto e justificativa comercial de uma linha.

Regras duras:
- se houver colisão de nome, dúvida semântica ou vínculo fraco, não force publicação;
- use `descarta` para absurdo claro;
- use `revisa` quando houver alguma plausibilidade mas a segurança não for suficiente;
- use `publica` apenas quando o envelope já sustentar o vínculo e a relevância;
- se `decision` não for `publica`, `headline`, `summary`, `commercial_why` e `impacto` devem ser null;
- responda somente em JSON válido.
```

## Posição no pipeline

Sequência recomendada:
1. coleta ampla
2. freeze de carteira
3. matching determinístico
4. lookup/guard exato
5. **single-stage self-gate da LLM barata**
6. DRAFT para o executivo
7. publicação aprovada

## Regra de governança

Esta etapa decide e redige, mas **não publica**. Ela só produz artefato editorial governado.

## Trade-off

### Vantagem
- menos complexidade que juiz+redator separados
- custo baixo
- boa trava de absurdo na borda

### Limite
- se o matcher upstream estiver frouxo, a LLM vira paliativo caro
- por isso, manter o trabalho de precisão determinística em paralelo
