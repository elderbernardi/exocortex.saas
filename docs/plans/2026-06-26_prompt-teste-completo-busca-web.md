# Prompt — teste completo do sistema de busca web + fontes estruturadas

Use este prompt quando quiser acionar o **fluxo completo de coleta e síntese** do Exocórtex para uma empresa, exercitando o máximo possível do que já foi desenvolvido: reconhecimento de entidade, coleta multi-camada, integração opcional com documentos via DocBrain, síntese executiva e evidência verificável.

---

Você está no repo `/home/elder/projetos/projetob/exocortex.saas` e deve executar um **teste completo do sistema de busca de dados web** do Exocórtex, sem pular etapas, sem improvisar fontes fora do fluxo definido e sem declarar sucesso sem evidência real.

## Objetivo

Executar um workflow completo de pesquisa e reconhecimento de empresa, usando **todas as camadas disponíveis que fizerem sentido**:

1. `last30days` para sinal difuso global
2. `Agent-Reach` para web/social/RSS
3. `crawler-brasil` para fontes setoriais brasileiras
4. `DocBrain` para documentos locais, se fornecidos
5. síntese final em PT-BR com contrato executivo do wrapper
6. output verificável em texto e, quando aplicável, em JSON estruturado

O teste deve validar tanto a **qualidade da coleta** quanto a **disciplina operacional do sistema**.

## Variáveis de entrada

Preencha antes de executar:

### `{{OBJETIVO_EXECUTIVO}}`
Texto curto explicando por que a pesquisa está sendo feita.

Exemplo:
`Quero entender posicionamento, sinais competitivos, maturidade digital e possíveis alavancas comerciais da empresa.`

### `{{DADOS_PRELIMINARES_EMPRESA}}`
Bloco livre com o máximo de pistas já conhecidas sobre a empresa. Esse bloco existe para **reconhecimento e desambiguação da entidade**, não para contaminar a conclusão.

Use de preferência este formato:

```yaml
nome_principal: ""
aliases: []
marcas: []
razao_social: ""
site: ""
dominio: ""
segmento: ""
subsegmento: ""
pais: "Brasil"
regiao: ""
cidade: ""
estado: ""
produtos_chave: []
clientes_ou_canais: []
executivos_citados: []
concorrentes_iniciais: []
palavras_criticas: []
restricoes_de_busca: []
observacoes: ""
```

### `{{MICROVERSO_DESTINO}}`
Slug do microverso, se já existir ou se quiser forçar destino.

Exemplo:
`girando-sol`

### `{{TEMPLATE_PRIORITARIO}}`
Template principal quando o caso cair no wrapper atual.

Valores típicos:
- `panorama`
- `varejo`
- `inovacao`
- `limpeza`
- `supply`

Se não houver certeza, usar `panorama` primeiro.

### `{{DOCUMENTOS_LOCAIS}}`
Lista opcional de arquivos para passar pelo DocBrain.

Exemplo:
```text
/home/elder/Downloads/catalogo.pdf
/home/elder/Downloads/apresentacao-comercial.pdf
```

Se estiver vazio, seguir sem DocBrain.

---

## Fontes de verdade a carregar antes de agir

Carregue e respeite estes artefatos antes de executar qualquer coleta:

1. `skills/excrtx-research-cpg-brasil/SKILL.md`
2. `skills/excrtx-integrate-docbrain/SKILL.md`
3. `docs/architecture/domain-research-blueprint.md`
4. `docs/plans/2026-06-26_prompt-proxima-sessao-fase5.md`
5. `tests/test_research_cpg_brasil.py`
6. `tests/test_docbrain_to_acervo.py`
7. `tests/test_domain_research_blueprint_contract.py`
8. `tests/test_onboard_business_context_contract.py`

Se algum desses arquivos divergir do código, reportar a divergência.

---

## Skills obrigatórias

Antes de responder ou executar, carregar:

1. `excrtx-research-cpg-brasil`
2. `excrtx-integrate-docbrain`
3. `excrtx-behavior-accuracy`
4. `excrtx-govern-tools`
5. `excrtx-quality-antislop`

Se a investigação sair do domínio CPG, deixar isso explícito. Ainda assim, preservar o workflow, o contrato de evidência e o relatório final.

---

## Restrições obrigatórias

- Não inventar cobertura, menção, concorrente, faturamento ou presença digital.
- Não tratar dado preliminar como fato validado. Confirmar por fonte ou marcar como hipótese.
- Não instalar dependências sem autorização explícita do executivo.
- Não publicar comentário, issue, push ou mensagem externa sem DRAFT e aprovação.
- Não citar o repo privado do DocBrain em documentação pública.
- Não encerrar com plano genérico. Entregar achados, evidências, lacunas e próximos passos concretos.
- Se uma camada falhar, registrar **comando, erro, impacto e fallback**.

---

## Workflow obrigatório

### Etapa 0 — classificação e escopo

1. Classifique o pedido como **Execução**.
2. Assuma que o objetivo é produzir um **teste operacional completo**, não uma conversa exploratória.
3. Declare internamente a hipótese de domínio:
   - `CPG/FMCG/household/varejo alimentar` -> usar wrapper atual como trilha principal
   - outro domínio -> usar a arquitetura como referência e declarar eventual desalinhamento do wrapper atual

### Etapa 1 — reconhecimento da entidade

Usando `{{DADOS_PRELIMINARES_EMPRESA}}`, monte um bloco de reconhecimento com:

- nome principal normalizado
- aliases e marcas candidatas
- domínio principal confirmado ou candidatos de domínio
- cidade/estado/país quando identificáveis
- segmento e subsegmento prováveis
- sinais de ambiguidade de nome
- concorrentes iniciais apenas como hipótese

Regras:
- separar `confirmado`, `provável` e `não confirmado`
- se houver colisão de nomes, resolver antes da coleta profunda
- se a entidade continuar ambígua, parar e explicar a ambiguidade antes de continuar

### Etapa 2 — inspeção do runtime e pré-check técnico

Verificar, com output real:

1. estado do repo `exocortex.saas`
2. disponibilidade do wrapper `skills/excrtx-research-cpg-brasil/scripts/orchestrate.py`
3. disponibilidade dos testes relevantes
4. se houver documentos locais, health check do DocBrain:

```bash
cd /home/elder/projetos/projetob/docbrain
npm run --silent cli -- api health --output json
```

Esperado:
- payload JSON com `ok: true`

Se o health falhar, diagnosticar em ordem:
1. `node --version`
2. existência do workspace correto
3. build/artefatos esperados
4. chaves necessárias
5. divergência entre paths reais e skills/docs

Se o DocBrain falhar, o resto do teste continua, mas a falha deve aparecer no relatório final como lacuna operacional real.

### Etapa 3 — escolha do template e plano de coleta

Escolher o template inicial com base na empresa:

- `panorama` -> default para reconhecimento geral
- `limpeza` -> empresas de household, saneantes, limpeza doméstica
- `varejo` -> supermercados, atacarejo, varejo alimentar, canal
- `inovacao` -> foco em embalagem, sustentabilidade, produto, branding
- `supply` -> logística, cadeia, distribuição, insumos

Regra:
- sempre rodar **ao menos um template amplo** (`panorama` ou equivalente)
- se o caso permitir, rodar **um segundo template mais específico**

### Etapa 4 — coleta principal via wrapper

Executar o wrapper em duas superfícies:

#### 4.1 Execução estruturada em JSON

```bash
python3 skills/excrtx-research-cpg-brasil/scripts/orchestrate.py \
  --template {{TEMPLATE_PRIORITARIO}} \
  --output json
```

#### 4.2 Execução executiva em Markdown

```bash
python3 skills/excrtx-research-cpg-brasil/scripts/orchestrate.py \
  --template {{TEMPLATE_PRIORITARIO}}
```

#### 4.3 Segundo template, quando fizer sentido

Rodar mais uma vez com template complementar.

Exemplos:
- `panorama` + `limpeza`
- `panorama` + `varejo`
- `panorama` + `inovacao`

### Etapa 5 — integração opcional com documentos locais

Se `{{DOCUMENTOS_LOCAIS}}` vier preenchido, processar cada documento via DocBrain e acoplar ao teste.

Fluxo esperado:

1. validar health do DocBrain
2. chamar o adaptador `scripts/docbrain_to_acervo.py`
3. promover saída para o microverso certo
4. reexecutar o wrapper com `--document` quando aplicável

Exemplo de comando:

```bash
python3 skills/excrtx-research-cpg-brasil/scripts/orchestrate.py \
  --template {{TEMPLATE_PRIORITARIO}} \
  --output json \
  --document /abs/path/arquivo.pdf \
  --document-microverso {{MICROVERSO_DESTINO}}
```

Se o microverso não vier pronto, resolver com base no nome da empresa, mas registrar a regra aplicada.

### Etapa 6 — leitura crítica por camada

Separar os achados em quatro grupos:

1. **Sinal global** (`last30days`)
2. **Web/social/RSS** (`Agent-Reach`)
3. **Fontes setoriais BR** (`crawler-brasil`)
4. **Documentos estruturados** (`DocBrain`), se existirem

Para cada camada, responder:
- quantos itens apareceram
- quais fontes dominaram
- o que agregou valor
- o que veio com ruído
- o que faltou

### Etapa 7 — reconciliação com os dados preliminares

Comparar o que foi coletado com `{{DADOS_PRELIMINARES_EMPRESA}}` e classificar cada pista como:

- `confirmada`
- `corrigida`
- `não encontrada`
- `ainda ambígua`

Isso é obrigatório. O teste não serve só para coletar; ele serve para medir se o sistema reconhece a empresa corretamente.

### Etapa 8 — saída final obrigatória

Entregar quatro blocos finais.

#### Bloco A — resumo executivo

Texto curto com:
- quem é a empresa
- qual é o posicionamento aparente
- quais sinais competitivos surgiram
- qual é a leitura de maturidade digital
- onde estão as oportunidades ou riscos comerciais

#### Bloco B — relatório operacional do teste

Tabela com colunas:
- camada
- ferramenta/skill
- comando acionado
- status
- evidência
- observações

Camadas mínimas:
- reconhecimento
- wrapper JSON
- wrapper Markdown
- last30days
- Agent-Reach
- crawler-brasil
- DocBrain, se aplicável

#### Bloco C — lacunas e falhas reais

Listar:
- o que não funcionou
- onde houve ruído alto
- que dados o sistema ainda não captura bem
- se houve desalinhamento entre skill, docs e runtime

#### Bloco D — artefatos gerados

Listar caminhos reais de saída:
- arquivos `.md`
- arquivos `.json`
- caminhos de microverso, se houve promoção de documento
- comandos de teste executados

---

## Critério de sucesso

O teste só conta como completo se entregar:

1. reconhecimento consistente da empresa
2. pelo menos uma execução real do wrapper em JSON
3. pelo menos uma execução real do wrapper em Markdown
4. uso das camadas disponíveis com contagem por camada
5. comparação explícita entre dado preliminar e dado confirmado
6. registro das falhas reais, sem teatro
7. conclusão final sobre a utilidade do sistema para esse caso

---

## Perguntas que a conclusão deve responder

1. O sistema identificou a empresa corretamente?
2. Quais camadas trouxeram sinal útil de verdade?
3. Qual camada mais agregou valor neste caso?
4. Onde o sistema ainda falha ou deriva?
5. O wrapper atual foi suficiente ou já pede generalização de domínio?
6. Se eu rodar isso de novo amanhã para outra empresa do mesmo setor, o workflow já está maduro?

---

## Prompt compacto para copiar e colar

```text
Você está no repo /home/elder/projetos/projetob/exocortex.saas e deve executar um teste completo do sistema de busca de dados web do Exocórtex para a empresa abaixo. Use o workflow completo, sem pular etapas, sem inventar cobertura e sem declarar sucesso sem evidência real.

OBJETIVO_EXECUTIVO:
{{OBJETIVO_EXECUTIVO}}

DADOS_PRELIMINARES_EMPRESA:
{{DADOS_PRELIMINARES_EMPRESA}}

MICROVERSO_DESTINO:
{{MICROVERSO_DESTINO}}

TEMPLATE_PRIORITARIO:
{{TEMPLATE_PRIORITARIO}}

DOCUMENTOS_LOCAIS:
{{DOCUMENTOS_LOCAIS}}

Antes de agir, carregue e siga:
- skills/excrtx-research-cpg-brasil/SKILL.md
- skills/excrtx-integrate-docbrain/SKILL.md
- docs/architecture/domain-research-blueprint.md
- docs/plans/2026-06-26_prompt-proxima-sessao-fase5.md
- tests/test_research_cpg_brasil.py
- tests/test_docbrain_to_acervo.py
- tests/test_domain_research_blueprint_contract.py
- tests/test_onboard_business_context_contract.py

Skills obrigatórias:
- excrtx-research-cpg-brasil
- excrtx-integrate-docbrain
- excrtx-behavior-accuracy
- excrtx-govern-tools
- excrtx-quality-antislop

Workflow obrigatório:
1. reconhecer a entidade usando os dados preliminares, separando confirmado/provável/não confirmado
2. verificar o runtime e a disponibilidade do wrapper
3. se houver documentos, rodar health check real do DocBrain
4. escolher o template correto e justificar
5. rodar o wrapper ao menos uma vez em JSON e uma vez em Markdown
6. se fizer sentido, rodar um segundo template complementar
7. integrar documentos locais se fornecidos
8. reconciliar o que foi coletado com os dados preliminares
9. entregar resumo executivo + relatório operacional do teste + falhas reais + artefatos gerados

Restrições:
- não instalar dependências sem autorização
- não tratar dado preliminar como fato
- não publicar nada externamente
- se uma camada falhar, mostrar comando, erro e impacto

Perguntas finais obrigatórias:
- O sistema identificou a empresa corretamente?
- Quais camadas trouxeram sinal útil?
- Onde o sistema falha hoje?
- O wrapper atual foi suficiente?
- O workflow está maduro para repetir em outra empresa do mesmo setor?
```
