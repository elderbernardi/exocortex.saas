# Blueprint de Generalização — Skill-wrappers de pesquisa por domínio

> Documento canônico para a issue [#101](https://github.com/elderbernardi/exocortex.saas/issues/101).
> Referências canônicas: [#98](https://github.com/elderbernardi/exocortex.saas/issues/98) para fontes do crawler BR e [#99](https://github.com/elderbernardi/exocortex.saas/issues/99) para o wrapper CPG que serve de template.

---

## 1. Objetivo

Padronizar como criar uma nova skill `excrtx-research-{domain}` sem reengenharia. O wrapper de domínio não inventa um pipeline novo: ele reaproveita a arquitetura já consolidada em `excrtx-research-cpg-brasil` e troca apenas quatro superfícies:

1. **queries** por template
2. **fontes setoriais brasileiras**
3. **rótulos de síntese**
4. **vocabulário de briefing** do domínio

Tudo o resto deve permanecer o mais estável possível: CLI, contrato de síntese, output JSON, smoke tests e integração opcional com DocBrain.

---

## 2. Pré-requisitos e dependências

| Dependência | Papel | Estado esperado |
|---|---|---|
| `last30days` | Camada global de sinais difusos | Opcional, mas o wrapper deve suportar `--skip-l30d` |
| `excrtx-integrate-agent-reach` | Camada web/social | Disponível e com adapter funcional |
| `tools/excrtx_crawler_brasil/` | Camada setorial BR | Fontes do domínio já cadastradas ou claramente especificadas para cadastro via #98 |
| `scripts/docbrain_to_acervo.py` | Documentos locais promovidos | Opcional, mas o wrapper deve preservar os flags `--document*` se quiser suportar contexto local |
| `tests/test_research_{domain}.py` | Regressão mínima | Obrigatório |

**Regra de ouro:** se o novo domínio exige fontes novas, primeiro resolver o cadastro das fontes no crawler BR (#98). O wrapper (#101) não deve embutir scraping ad hoc dentro de `orchestrate.py`.

---

## 3. Anatomia mínima do wrapper

Estrutura replicável:

```text
skills/
└── excrtx-research-{domain}/
    ├── SKILL.md
    ├── scripts/
    │   └── orchestrate.py
    └── references/
        └── query-templates.md

tests/
└── test_research_{domain}.py
```

### 3.1 O que cada arquivo faz

| Arquivo | Obrigatório | Função |
|---|---|---|
| `SKILL.md` | Sim | Contrato humano-operacional: quando usar, arquitetura, comandos, pitfalls, verification |
| `scripts/orchestrate.py` | Sim | Dispatcher das três camadas (`last30days`, `Agent-Reach`, `crawler BR`) + síntese final |
| `references/query-templates.md` | Sim | Catálogo dos templates do domínio, queries por camada e foco analítico |
| `tests/test_research_{domain}.py` | Sim | Smoke e contrato do wrapper |
| `references/*.md` extras | Opcional | Contratos auxiliares (ex.: DocBrain, fontes especiais, dicionário do domínio) |

### 3.2 Contrato da CLI

O wrapper novo deve preservar a mesma superfície pública do CPG:

```bash
python3 skills/excrtx-research-{domain}/scripts/orchestrate.py --template <nome>
python3 skills/excrtx-research-{domain}/scripts/orchestrate.py --template <nome> --skip-l30d
python3 skills/excrtx-research-{domain}/scripts/orchestrate.py --template <nome> --output json
python3 skills/excrtx-research-{domain}/scripts/orchestrate.py \
  --template <nome> \
  --document /abs/path/dossie.pdf \
  --document-microverso <slug> \
  --document-acervo-root /abs/path/acervo
```

Flags obrigatórios a preservar:

- `--template`
- `--skip-l30d`
- `--output md|json`
- `--document`
- `--document-microverso`
- `--document-company`
- `--document-brand`
- `--document-acervo-root`

Se o domínio não usar documentos locais no primeiro dia, os flags podem seguir presentes e apenas não serem exercitados no dogfood inicial.

---

## 4. Contrato interno do `orchestrate.py`

O arquivo canônico atual fica em `skills/excrtx-research-cpg-brasil/scripts/orchestrate.py`.

### 4.1 Componentes que devem ser preservados

1. **Mapa `TEMPLATES`** como fonte única de configuração
2. **Funções separadas por camada**:
   - `run_last30days()`
   - `run_agent_reach()`
   - `run_crawler()`
   - `run_docbrain_adapter()` quando documentos locais estiverem habilitados
3. **`synthesize()`** como ponto único de saída executiva
4. **Bloco JSON final** com as chaves:
   - `template`
   - `label`
   - `last30days`
   - `agent_reach`
   - `crawler_br`
   - `structured_sources`
   - `synthesis`

### 4.2 Chaves mínimas por template

Cada entrada em `TEMPLATES` deve declarar, no mínimo:

```python
{
    "l30d_query": "...",
    "l30d_subreddits": "...",
    "l30d_search": "reddit,youtube",
    "ar_query": "...",
    "ar_channels": "web,youtube",
    "cr_domain": "...",
    "cr_sources": "fonte-a,fonte-b",
    "label": "Nome executivo do template",
}
```

Campos podem ser omitidos só quando houver default claro e já suportado pelo wrapper base.

### 4.3 Contrato de síntese

O wrapper novo herda o mesmo contrato textual do CPG:

1. **Badge** na primeira linha com nome do domínio, template e data
2. **`O que aprendemos`** como corpo narrativo, com links inline e atribuição de fonte
3. **`PADRÕES-CHAVE`** como lista numerada de padrões
4. **Emoji-footer** com as fontes ativas
5. **PT-BR sem slop**
6. **Atribuição por fonte** em cada insight (`[web·AR]`, `[crawled-source]`, `[docbrain]`, etc.)

O domínio muda o vocabulário; não muda o contrato.

---

## 5. Contrato de fontes por camada

### 5.1 Camada `last30days`

Use para sinais globais, comunidades, creators e debate difuso. Em domínios muito B2B, pode gerar pouco valor; por isso `--skip-l30d` é obrigatório para smoke test.

**Checklist de query:**
- termos internacionais do setor
- sinônimos do domínio
- subreddits plausíveis
- zero dependência de handles obscuros para o smoke inicial

### 5.2 Camada `Agent-Reach`

Use para busca web/social com query em PT-BR. O padrão de canais começa em `web,youtube`; RSS entra quando houver um feed de alta densidade e baixa sujeira.

**Checklist de query:**
- query em linguagem de negócio brasileira
- sem aspas excessivas
- com ano quando o tema pede recorte temporal
- canal `rss` apenas quando o feed fizer sentido para aquele template

### 5.3 Camada `crawler BR`

O crawler BR é a única camada que conhece fontes setoriais brasileiras com curadoria por slug. Toda nova skill deve decidir uma destas rotas:

1. **Reusar fontes já cadastradas** via `cr_domain` e `cr_sources`
2. **Pedir expansão do registro em `tools/excrtx_crawler_brasil/sources.py`** antes de ativar o domínio

O registro de fonte no crawler segue este contrato:

```python
Source(
    slug="identificador-kebab-case",
    name="Nome exibível",
    source_type="rss|api|html|browser",
    url="https://fonte.example/feed",
    domains=["agronegocio", "graos"],
    description="O que a fonte cobre",
)
```

**Regras para novas fontes:**
- zero-auth no primeiro momento
- sem paywall como dependência principal
- preferir RSS/API a HTML, e HTML a browser
- slug curto e estável
- `domains` descritivos o suficiente para permitir filtragem futura

---

## 6. Checklist de ativação de um novo domínio

### Etapa 1 — Delimitar o domínio

Defina:
- slug do domínio
- pergunta executiva principal
- 4 ou 5 ângulos recorrentes
- 5 a 10 fontes brasileiras plausíveis

### Etapa 2 — Auditar fontes

Para cada fonte candidata, classifique:
- tipo (`rss`, `api`, `html`, `browser`)
- existência de paywall
- confiabilidade institucional
- frequência de atualização
- aderência a um ou mais subdomínios

### Etapa 3 — Fechar a camada do crawler (#98)

Se a fonte ainda não existir em `tools/excrtx_crawler_brasil/sources.py`, cadastrar primeiro. O wrapper não deve mascarar ausência de fonte com scraping improvisado.

### Etapa 4 — Clonar o wrapper de referência (#99)

Parta de `skills/excrtx-research-cpg-brasil/` e replique:
- estrutura de diretórios
- assinatura da CLI
- shape do JSON
- contrato da síntese
- padrão de testes

### Etapa 5 — Reescrever `TEMPLATES`

Cada template precisa ter:
- nome executivo curto
- 1 query global (`last30days`)
- 1 query PT-BR (`Agent-Reach`)
- 1 seleção de domínio/slugs do crawler
- 1 foco explícito de síntese

### Etapa 6 — Escrever `references/query-templates.md`

Documente, por template:
- query `last30days`
- query/canais `Agent-Reach`
- `cr_domain` e `cr_sources`
- foco analítico
- o que entra e o que fica de fora

### Etapa 7 — Ajustar `SKILL.md`

Checklist mínimo:
- When to Use
- Don't use for
- Arquitetura
- Procedure
- Contrato de síntese
- Pitfalls
- Verification
- Referências cruzadas para #98 e #99

### Etapa 8 — Criar testes

No mínimo:
- `--help` funciona
- todos os templates aparecem no help ou em constante equivalente
- `--skip-l30d` gera briefing válido
- `--output json` retorna JSON parseável
- síntese vazia degrada graciosamente
- pelo menos 1 smoke real por template crítico

### Etapa 9 — Dogfood

Executar pelo menos:

```bash
python3 skills/excrtx-research-{domain}/scripts/orchestrate.py --template panorama --skip-l30d
python3 skills/excrtx-research-{domain}/scripts/orchestrate.py --template panorama --output json --skip-l30d
```

Se houver integração com documento local:

```bash
python3 skills/excrtx-research-{domain}/scripts/orchestrate.py \
  --template panorama \
  --output json \
  --skip-l30d \
  --document /abs/path/dossie.pdf \
  --document-microverso <slug> \
  --document-acervo-root /abs/path/acervo
```

---

## 7. Exemplo completo — Agronegócio Brasil

Este exemplo é a prova de generalização pedida em #101. Ele **não cria a skill**; ele mostra exatamente como ela deve nascer.

### 7.1 Nome e objetivo

- **Skill:** `excrtx-research-agronegocio-brasil`
- **Objetivo:** consolidar sinais institucionais, de mercado, pesquisa e mídia vertical do agronegócio brasileiro em briefing executivo unificado

### 7.2 Fontes institucionais reais

| Papel | Fonte | URL validada | Observação |
|---|---|---|---|
| Associação setorial | ABAG | `https://abag.com.br/` | Home oficial validada por busca de domínio |
| Representação institucional | CNA Brasil | `https://cnabrasil.org.br/` | Home oficial validada por busca de domínio |
| Pesquisa pública | Embrapa | `https://www.embrapa.br/` | Portal oficial validado |
| Estudos e indicadores | Cepea/Esalq-USP | `https://www.cepea.esalq.usp.br/` | Busca retornou materiais oficiais e widget institucional; a homepage deve ser priorizada no cadastro final |
| Mídia vertical | Notícias Agrícolas | `https://www.noticiasagricolas.com.br/` | Home oficial validada |

### 7.3 Templates recomendados

| Template | Foco | `cr_domain` proposto | `cr_sources` propostos |
|---|---|---|---|
| `panorama` | macro do agro, política setorial, produção, exportação | `agronegocio` | `abag,cna-brasil,embrapa,cepea,noticias-agricolas` |
| `graos` | soja, milho, clima, produtividade, preço | `graos` | `cepea,embrapa,noticias-agricolas` |
| `pecuaria` | boi, leite, sanidade, custos | `pecuaria` | `cna-brasil,cepea,embrapa,noticias-agricolas` |
| `insumos` | fertilizantes, defensivos, máquinas | `insumos` | `abag,embrapa,noticias-agricolas` |
| `comercio_exterior` | exportação, câmbio, barreiras, China | `agronegocio` | `abag,cna-brasil,cepea` |

### 7.4 Exemplo de configuração

Arquivo de referência: `docs/architecture/examples/agronegocio-research-config.yaml`

### 7.5 Esqueleto do `TEMPLATES`

```python
TEMPLATES = {
    "panorama": {
        "l30d_query": 'Brazil agribusiness trends OR agro export OR farm input costs',
        "l30d_subreddits": "agriculture,commodities,economics",
        "l30d_search": "reddit,youtube",
        "ar_query": "agronegócio Brasil tendências exportação produtividade 2026",
        "ar_channels": "web,youtube",
        "cr_domain": "agronegocio",
        "cr_sources": "abag,cna-brasil,embrapa,cepea,noticias-agricolas",
        "label": "Panorama Agronegócio Brasil",
    },
    "graos": {
        "l30d_query": 'soy corn brazil crop outlook logistics climate',
        "l30d_subreddits": "agriculture,commodities,weather",
        "l30d_search": "reddit,youtube",
        "ar_query": "soja milho Brasil safra clima logística 2026",
        "ar_channels": "web,youtube",
        "cr_domain": "graos",
        "cr_sources": "cepea,embrapa,noticias-agricolas",
        "label": "Grãos e Safra",
    },
}
```

### 7.6 O que precisa existir para o exemplo virar skill real

1. slugs cadastrados no crawler BR (`tools/excrtx_crawler_brasil/sources.py`)
2. `domains` coerentes para `agronegocio`, `graos`, `pecuaria` e `insumos`
3. `SKILL.md`, `scripts/orchestrate.py`, `references/query-templates.md` e `tests/test_research_agronegocio_brasil.py`
4. smoke test com `--skip-l30d`

---

## 8. Anti-deriva: o que não fazer

- Não criar lógica nova de scraping dentro do wrapper
- Não quebrar a assinatura da CLI porque “este domínio é diferente”
- Não trocar o contrato de síntese
- Não introduzir dependência autenticada como fonte principal do domínio
- Não misturar naming arbitrário (`agro`, `agribusiness`, `agroneg`) sem definir slug canônico
- Não abrir uma nova issue de wrapper sem antes explicitar as fontes que a sustentam

---

## 9. Definition of Done para novos wrappers

Um novo `excrtx-research-{domain}` só está pronto quando:

- [ ] a estrutura de diretórios bate com este blueprint
- [ ] o domínio tem fontes brasileiras reais e documentadas
- [ ] `orchestrate.py` preserva a CLI e o shape do JSON
- [ ] `references/query-templates.md` explica todos os templates
- [ ] existe `tests/test_research_{domain}.py`
- [ ] `--template panorama --skip-l30d` roda sem erro
- [ ] `--output json` retorna JSON parseável
- [ ] há pelo menos 1 dogfood real

---

## 10. Referências cruzadas

- Wrapper canônico atual: `skills/excrtx-research-cpg-brasil/`
- Orquestrador de referência: `skills/excrtx-research-cpg-brasil/scripts/orchestrate.py`
- Templates de referência: `skills/excrtx-research-cpg-brasil/references/query-templates.md`
- Testes de referência: `tests/test_research_cpg_brasil.py`
- Cadastro de fontes do crawler BR: `tools/excrtx_crawler_brasil/sources.py`
- Plano da META #97: `docs/plans/2026-06-24_pesquisa-setorial-arquitetura.md`
- Issue de fontes/crawler: [#98](https://github.com/elderbernardi/exocortex.saas/issues/98)
- Issue do wrapper CPG: [#99](https://github.com/elderbernardi/exocortex.saas/issues/99)
- Issue deste blueprint: [#101](https://github.com/elderbernardi/exocortex.saas/issues/101)
