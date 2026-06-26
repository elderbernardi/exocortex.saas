# Business Context Schema

Contrato de armazenamento para o bloco **Contexto de Negócio** do onboarding.

## Objetivo

Separar contexto operacional do executivo (**domínios de atuação**) de contexto de mercado (**indústria, empresas e concorrentes**) em um formato parseável por outras skills.

## Local de persistência

Salvar dentro de `SOUL.md`, na seção:

````markdown
## Contexto de Negócio
<!-- EXCRTX:BUSINESS_CONTEXT:BEGIN -->
```yaml
industry: bens de consumo domésticos
companies:
  - Girando Sol
  - Girando Sol Participações
competitors:
  - Ypê
  - Unilever
```
<!-- EXCRTX:BUSINESS_CONTEXT:END -->
````

## Schema mínimo

```yaml
industry: string | null
companies:
  - string
competitors:
  - string
```

## Regras

- As três chaves são obrigatórias: `industry`, `companies`, `competitors`
- `industry` pode ser `null` quando o executivo pular esse bloco
- `companies` e `competitors` podem ser listas vazias
- Preservar nomes como o executivo falou; normalizar apenas espaços laterais
- Remover duplicatas exatas ou case-insensitive
- Não inferir concorrentes, holdings, marcas ou subsidiárias não citadas

## Exemplo — bloco preenchido

```yaml
industry: bens de consumo domésticos
companies:
  - Girando Sol
  - Girando Sol Participações
competitors:
  - Ypê
  - Unilever
```

## Exemplo — bloco pulado

```yaml
industry: null
companies: []
competitors: []
```

## Consumo esperado

Skills de pesquisa e auto-configuração podem ler esse bloco para:

- sugerir companies padrão
- sugerir competitors padrão
- adaptar prompts por indústria
- gerar templates de pesquisa sem perguntar tudo de novo
