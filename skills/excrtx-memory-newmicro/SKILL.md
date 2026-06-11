---
name: excrtx-memory-newmicro
description: Criar novos Microversos no Acervo Cognitivo com estrutura wiki completa (SCHEMA, index, log, raw, 7 Natures).
version: 2.0.0
category: excrtx
platforms: [linux]
metadata:
  hermes:
    tags: [exocortex, microverso, acervo, creation, onboarding, wiki]
---

# Criar Novo Microverso

Provisiona um novo domínio de atuação no Acervo Cognitivo do executivo.
Gera estrutura wiki completa compatível com `excrtx-memory-manager`.

## Trigger

Ativar quando:
- O executivo menciona um novo domínio de atuação
- Uma tarefa requer contexto de domínio que ainda não existe no acervo
- O executivo solicita explicitamente criar um novo Microverso

## Procedure

### 1. Definir o Microverso

Pergunte ao executivo (se não especificado):
- **Nome:** Nome legível do domínio (ex: "Financeiro", "Produto Alpha", "Cliente ACME")
- **Slug:** Identificador em kebab-case (ex: `financeiro`, `produto-alpha`, `cliente-acme`)
- **Type:** Classificação para aliases de grupo. Opções: `client`, `project`, `domain`, `role`
- **Description:** Uma frase descrevendo o escopo do Microverso

### 2. Criar Estrutura

```bash
# Copiar template para novo Microverso
cp -r ~/.hermes/acervo/micro/_template/ ~/.hermes/acervo/micro/{slug}/
```

### 3. Preencher SCHEMA.md

Abrir `~/.hermes/acervo/micro/{slug}/SCHEMA.md` e preencher:

```yaml
---
domain: {nome}
slug: {slug}
type: {client|project|domain|role}
description: {description}
created: {YYYY-MM-DD}
---
```

Preencher seções de convenções, taxonomia de tags e regras de escrita específicas do domínio.

### 4. Preencher Contexto Inicial

Abrir `~/.hermes/acervo/micro/{slug}/context/` e:
- Substituir `{MICROVERSO_NAME}` pelo nome
- Substituir `{slug}` pelo slug
- Preencher "Cenário Atual" com informações fornecidas pelo executivo

Repetir substituição de placeholders em todos os 7 Nature files.

### 5. Inicializar Wiki Files

- **index.md:** Catálogo das 11 Natures com summaries (todas começam como "Vazio — aguardando contexto")
- **log.md:** Primeira entrada:
  ```
  ## [{YYYY-MM-DD}] create | Microverso {nome} criado
  Type: {type}. Natures: 7 (arquivo). Onboarding: {completo|parcial|mínimo}.
  ```
- **raw/:** Manter vazio (pronto para fontes)
- **_archive/:** Manter vazio

### 6. Entrevista de Onboarding (Opcional)

Se o executivo estiver disponível, coletar:
- **Ferramentas:** Quais MCPs/APIs usa neste domínio?
- **Persona:** Tom de voz diferente do global?
- **Regras:** Restrições específicas?
- **Processos:** Workflows recorrentes?
- **Estilo Visual:** Este domínio tem paleta visual própria diferente do padrão?
  - Se SIM → Ativar `brandkit` como guia → Criar `DESIGN.md` com `extends: global` e apenas overrides via `excrtx-quality-designsys`
  - Se NÃO → Não criar arquivo (herda `global/DESIGN.md` automaticamente)

Registrar respostas nos respectivos Nature files.

### 7. Registrar no Sistema

- Adicionar entry no `MEMORY.md` via skill `excrtx-harness-promptlog`
- Atualizar `~/.hermes/acervo/shared/glossario.md` com termos específicos do novo domínio
- Atualizar `~/.hermes/acervo/shared/groups.md`:
  - Adicionar slug ao alias de tipo correspondente (CLIENTS, PROJECTS, etc.)
  - Alias `ALL` se resolve automaticamente (lista diretórios)

## Verification

- [ ] Diretório `~/.hermes/acervo/micro/{slug}/` existe
- [ ] SCHEMA.md com frontmatter preenchido (domain, slug, type, description, created)
- [ ] index.md com catálogo das 7 Natures
- [ ] log.md com entrada de criação
- [ ] raw/ e _archive/ existem (vazios)
- [ ] 7 Nature files com frontmatter YAML
- [ ] Placeholders `{MICROVERSO_NAME}` e `{slug}` substituídos em todos os arquivos
- [ ] `context/` tem pelo menos o cenário atual preenchido
- [ ] `shared/groups.md` atualizado com o slug no tipo correto
- [ ] MEMORY.md registra a criação do Microverso

## Cleanup

Para remover um Microverso de teste:
```bash
rm -rf ~/.hermes/acervo/micro/{slug}/
```
Remover slug de `shared/groups.md`.
Registrar remoção no MEMORY.md.

## Pitfalls

- **Over-application**: Only activate when the skill's trigger conditions are met.
- **Missing context**: Ensure required dependencies and related skills are loaded.
