---
name: excrtx-memory-mvsetup
description: Provision base microversos for Exocortex as part of the replicable Hermes/Exocortex
  setup.
version: 1.0.0
author: Exocórtex
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - acervo
    - microverso
    - setup
    - reproducibility
    - shell
    - idempotency
    related_skills:
    - excrtx-memory-manager
    - excrtx-memory-newmicro
    - hermes-agent
    calibration:
    - feature_id: EX-14
      calibration_prompt: Você deve garantir que as operações e regras da skill Setup
        de Microverso Base (excrtx-memory-mvsetup) estão totalmente ativas no seu
        comportamento e integridade.
      test_prompt: Verifique se exocortex-ops tem microverso.yaml, SCHEMA.md, index.md,
        log.md.
      acceptance_criteria: O agente deve demonstrar de forma clara e factual que compreende
        as regras e procedimentos da skill Setup de Microverso Base.
      remediation_tip: Certifique-se de que a documentação e os limites da skill Setup
        de Microverso Base em seu SKILL.md estão sendo estritamente seguidos.
---
# Exocórtex Base Microverso Setup

Use quando um microverso deve virar parte do setup inicial e replicável do Exocórtex/Hermes. Exemplo: uma capacidade transversal que precisa existir em novos Exocórtex, não apenas no ambiente atual.

## Trigger

Ativar quando:

- o usuário pedir que um microverso seja “inicial”, “base”, “padrão” ou “parte do Hermes setup”;
- um novo domínio do Acervo precisa ser provisionado em instalações futuras;
- uma decisão de microverso precisa entrar em `micro/hermes-setup`;
- `~/.hermes/setup.sh` precisa criar ou preservar um microverso;
- o trabalho envolve Acervo v2 + setup replicável + script idempotente.

## Relação com outras skills

- Use `excrtx-memory-manager` para regras gerais de leitura/escrita no Acervo v2.
- Use `excrtx-memory-newmicro` para criar o microverso em si.
- Use esta skill para promover o microverso ao setup replicável.
- `hermes-agent` é protegido: consulte quando precisar de comandos Hermes, mas não edite.

## Procedure

### 1. Criar ou validar o microverso

Criar a estrutura Ontologia Multifocal v2:

```text
micro/{slug}/
├── SCHEMA.md
├── index.md
├── log.md
├── context/
├── knowledge/
├── contracts/
├── prompts/
├── skills/
├── workflows/
├── tools/
├── templates/
├── decisions/
├── reflections/
├── persona/
├── _meta/
├── raw/
└── _archive/
```

Todo conteúdo novo usa frontmatter v2. Não criar arquivos flat de Nature.

### 2. Manter o núcleo genérico

Se o microverso vira base de setup, ele precisa se adaptar ao usuário. Não incluir contexto pessoal, institucional ou projeto específico no núcleo.

Regra:

- microverso base: método, contratos, workflows, templates, capacidades;
- microverso atendido: contexto local, público, restrições, decisões específicas;
- `shared/`: relações duráveis entre domínios.

### 3. Registrar no `hermes-setup`

Atualizar:

```text
micro/hermes-setup/decisions/{slug}-base-microverso.md
micro/hermes-setup/workflows/replicable-exocortex-setup.md
micro/hermes-setup/index.md
micro/hermes-setup/log.md
```

A decisão deve explicar:

- por que o microverso é base;
- que escopo ele cobre;
- como evita acoplamento ao usuário;
- quais arquivos o setup deve provisionar;
- quais ações exigem aprovação.

### 4. Atualizar grupos só quando estrutural

Atualizar `shared/groups.md` apenas quando a associação for durável. Exemplo: adicionar um microverso criativo a `DOMAINS` e `CRIACAO` se ele representa capacidade transversal estável.

### 5. Draft-First para setup executável

Alterar `~/.hermes/setup.sh` muda o comportamento de instalações futuras. Produza um DRAFT de patch antes de aplicar.

O DRAFT precisa declarar:

- arquivo alterado;
- nova etapa adicionada;
- política de idempotência;
- impacto em novos setups;
- validações planejadas.

Aplicar só depois de aprovação explícita.

### 6. Provisionar de forma idempotente

O setup deve criar diretórios e arquivos ausentes, mas preservar arquivos existentes.

Padrão:

```bash
mkdir -p "$micro"/{context,knowledge,contracts,prompts,skills,workflows,tools,templates,decisions,reflections,persona,_meta,raw,_archive}

if [ ! -f "$micro/SCHEMA.md" ]; then
  cat > "$micro/SCHEMA.md" <<'EOF'
...
EOF
fi
```

Para arquivos que precisam de datas ou variáveis, usar `<<EOF` com cuidado. Para conteúdo estático, preferir `<<'EOF'`.

### 7. Validar antes e depois

Antes de aplicar:

```bash
patch --dry-run ...
bash -n /tmp/setup-draft.sh
```

Depois de aplicar:

```bash
bash -n ~/.hermes/setup.sh
```

Testar a função nova em ambiente isolado:

```bash
HERMES_HOME="$(mktemp -d)" bash test-function-only.sh
```

Validar:

- arquivos essenciais existem;
- segunda execução preserva arquivos;
- stderr fica vazio;
- script real continua sintaticamente válido.

## Pitfalls

### Backticks em heredoc de shell

Markdown com crase em heredoc não cotado (`<<EOF`) executa command substitution. Isso gera erros como `domain: command not found` e ainda pode criar o arquivo.

Correções:

- usar heredoc cotado quando não precisa expandir variáveis: `<<'EOF'`;
- escapar crases quando precisa expandir variáveis: ``\`texto\```;
- testar a função em `HERMES_HOME` temporário e falhar se stderr não estiver vazio.

### Não sobrescrever evolução manual

Microverso base evolui com o uso. O setup deve preservar arquivos existentes. Nunca usar `cat > arquivo` sem guarda `if [ ! -f arquivo ]` em arquivos semânticos do Acervo.

### Não confundir setup com contexto do usuário

Setup replicável instala capacidade. Contexto pessoal entra em microversos do usuário ou projetos concretos.

### Não confundir contagem de etapas no setup

Quando inserir nova etapa no `setup.sh`, atualizar a numeração completa de progresso (`[1/N] ... [N/N]`) nas funções e no bloco principal.

Checklist mínimo:

- confirmar total `N` final;
- alinhar rótulos nas funções auxiliares;
- alinhar rótulos no fluxo principal;
- validar com `grep` para detectar contagens mistas.

Se a contagem ficar inconsistente, o setup continua funcionando, mas perde legibilidade e gera diagnóstico operacional ruim.

### Não aplicar patch de setup sem aprovação

Mesmo sendo local, `setup.sh` altera comportamento futuro. Tratar como ação sensível: DRAFT primeiro, aplicação só após “aprovado”, “pode aplicar” ou equivalente inequívoco.

## Arquivos de referência

- Detalhes e checklist de microverso base: `references/base-microverso-setup.md`.
- Propagação de identidade Exocórtex sobre Hermes em SOULs, perfis, Acervo e setup: `references/exocortex-hermes-identity-propagation.md`.

## Verification

- [ ] Microverso criado com diretórios v2.
- [ ] Núcleo sem contexto pessoal.
- [ ] Decisão registrada em `micro/hermes-setup/decisions/`.
- [ ] Workflow replicável atualizado.
- [ ] `index.md` e `log.md` atualizados.
- [ ] `shared/groups.md` alterado apenas se estrutural.
- [ ] DRAFT de patch apresentado antes de alterar setup executável.
- [ ] Patch aprovado antes de aplicar.
- [ ] `bash -n` OK.
- [ ] Teste isolado em `HERMES_HOME` temporário OK.

