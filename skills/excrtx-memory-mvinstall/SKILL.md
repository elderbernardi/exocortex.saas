---
name: excrtx-memory-mvinstall
description: >-
  Install microverso structure from _fixture templates into the acervo. Scaffold microverso directories and base files.
version: 1.0.0
category: excrtx
platforms: [linux]
metadata:
  hermes:
    tags: [exocortex, memory, microverso, install, package, dependencies]
---

# Microverso Package Installer

> Microversos não são só arquivos. São skills, pacotes, dependências — um ecossistema.

## When to Use

Ativar quando:
- Executivo pede "instale o microverso X", "adicione o pacote Y"
- Setup.sh provisiona microversos base que contêm `microverso.yaml`
- Executivo importa um microverso de terceiros (diretório com manifesto)
- Comando `/xc mvinstall <path>` executado

**Don't use for:** Creating new microverso templates from scratch (use `excrtx-memory-newmicro`). Microverso setup and configuration (use `excrtx-memory-mvsetup`). Wiki or knowledge adaptation (use `excrtx-memory-wikiadapt`).

## Procedure

### 1. Ler Manifesto

Carregar `microverso.yaml` do diretório fonte. Validar schema `excrtx/v1`:

```yaml
apiVersion: excrtx/v1    # obrigatório
kind: Microverso          # obrigatório
metadata:
  name: <slug>            # obrigatório
  version: <semver>       # obrigatório
  description: <string>   # obrigatório
```

Se `microverso.yaml` ausente ou inválido → WARN + perguntar se instalar como microverso legado (sem verificação de dependências).

### 2. Verificar Dependências de Skills

Para cada skill em `requires.skills`:
- Verificar se existe em `$HERMES_HOME/skills/exocortex/<skill>/SKILL.md`
- Se presente → ✅
- Se ausente → WARN com lista de skills faltantes
- Oferecer: "Instalar skills faltantes?" (se disponíveis no bundle)
- Se não disponíveis → bloquear instalação com explicação

### 3. Verificar Pacotes Python

Para cada pacote em `requires.python_packages`:
- Verificar via `python3 -c "import <pkg>"` ou `uv pip show <pkg>`
- Se ausente e `uv` disponível → `uv pip install <spec>`
- Se ausente e `uv` não disponível → `pip install <spec>` com aviso
- Registrar pacotes instalados para possível rollback

### 4. Copiar Árvore

Copiar diretório do microverso para `$ACERVO/micro/<name>/`:
- Se já existe → perguntar: "Atualizar?" (merge, não overwrite)
- Preservar arquivos locais que o executivo tenha adicionado
- rsync com `--ignore-existing` para merge seguro

### 5. Executar Hooks

Se `hooks.post_install` definido:
- Validar que o path é relativo e dentro do diretório do microverso
- Rejeitar paths absolutos ou com `../` (segurança)
- Executar com timeout de 60 segundos
- Capturar stdout/stderr para relatório

Se `hooks.validate` definido:
- Executar após post_install
- Se falhar → WARN mas não desfazer instalação

### 6. Registrar no Manifest Global

Adicionar entrada em `$ACERVO/global/_meta/microversos.yaml`:

```yaml
installed:
  - name: <slug>
    version: <semver>
    installed_at: <ISO8601>
    path: micro/<slug>
    status: active
    requires_met: true|false
```

### 7. Relatório

Apresentar resumo:
- Microverso instalado: `<name>` v`<version>`
- Skills verificadas: X/Y presentes
- Pacotes instalados: lista
- Hooks executados: status
- Path: `$ACERVO/micro/<name>/`

## Pitfalls

- Hooks executam apenas scripts dentro do diretório do microverso — sem paths absolutos
- Pacotes instalados via ferramentas locais (uv, pip, npm) — sem `curl | bash`
- Microversos de terceiros requerem aprovação do executivo (Draft-First Protocol)
- Se o microverso já existe com mesma versão, skip silencioso
- Se versão superior, oferecer upgrade
- Manifest global é append-only (histórico preservado)

## Gotchas

- `uv` pode não estar instalado — fallback para `pip` com aviso
- `microverso.yaml` com `apiVersion` diferente de `excrtx/v1` → rejeitar com mensagem clara
- Hooks com permissões de execução ausentes → `chmod +x` antes de executar
- rsync pode não estar disponível → fallback para `cp -rn`

## Verification

- [ ] Manifesto lido e validado (schema excrtx/v1)
- [ ] Dependências de skills verificadas
- [ ] Pacotes Python/Node instalados (se necessário)
- [ ] Árvore copiada para $ACERVO/micro/<name>/
- [ ] Hooks executados com sucesso (se definidos)
- [ ] Registro no manifest global atualizado
- [ ] Relatório apresentado ao executivo
