---
name: excrtx-memory-mvinstall
description: Install a portable .mvpkg microverso package (manifest excrtx/v1) into the acervo — integrity
  check, OKF gate, compat preflight, dependency + skill-collision resolution, safe merge.
version: 1.1.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - memory
    - microverso
    - install
    - package
    - dependencies
    calibration:
    - feature_id: EX-15
      calibration_prompt: Você instala microversos empacotados com manifesto microverso.yaml (schema excrtx/v1). Verifica
        dependências de skills, pacotes Python/Node e MCPs. Executa hooks de pós-instalação e registra no manifest global.
        Merge seguro com rsync --ignore-existing.
      test_prompt: Instale o microverso empacotado que está em '/tmp/mv-consultoria-juridica/'. Verifique se tem tudo necessário
        antes de instalar.
      acceptance_criteria: '1. O agente verifica a existência e validade do microverso.yaml (schema excrtx/v1)

        2. Lista e verifica dependências (skills, pacotes, MCPs) antes de instalar

        3. Reporta dependências faltantes com ações para resolvê-las

        4. Usa merge seguro (rsync --ignore-existing) para não sobrescrever conteúdo existente'
      remediation_tip: 'FALHA: Instalação sem verificação de dependências. O manifesto microverso.yaml declara dependências
        que devem ser verificadas ANTES da cópia. Execute: ''cat /path/microverso.yaml'' para ler dependências, depois verifique
        cada uma. Se faltar alguma, reporte ao executivo antes de prosseguir.'
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

Executar a ferramenta determinística (contraparte de `excrtx-memory-mvexport`).
A estrutura de diretórios esperada segue o contrato canônico:
`global/contracts/microverso-directory-structure.md` (14 dirs: 11 natures + 3 infra).

```bash
python3 $ACERVO/global/tools/microverso_install.py <pkg.tar.gz | pkg-dir | git-url> [--install-deps] [--update-skills]
```

A ferramenta aplica, em ordem: **integridade** (`MANIFEST.sum`) → **manifesto** (`excrtx/v1`, via `microverso_schema.py`) → **gate OKF** (`validate_frontmatter.py` no conteúdo; bloqueia em erro) → **preflight de compat** (`compat` + `requires.system`) → **dependências/skills** → **merge seguro** → **hooks** → **registro global**. Os passos abaixo descrevem o contrato que a ferramenta implementa.

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

Antes do manifesto: verificar **integridade** via `MANIFEST.sum` (bloquear se houver mismatch) e o **gate OKF** sobre `acervo/` do pacote (`validate_frontmatter.py` — bloquear em erro). Depois, **preflight de compat**: comparar `compat.platforms` com a plataforma atual e checar `requires.system` (binários) — WARN com instruções se faltar.

### 2. Verificar Dependências de Skills

Para cada skill embutida em `skills/<name>/`, contra `$HERMES_HOME/skills/excrtx/<name>/`, aplicar **resolução de colisão**:
- Não existe → instalar
- Idêntica (hash) → skip
- Incoming com **semver maior** (mesma linhagem) → UPDATE (só com `--update-skills`; senão report)
- Divergente / não-upgrade → **renomear** incoming para `<name>-<slug>`, reescrever referências no microverso, manter a existente

Skills apenas declaradas (não embutidas) em `requires.skills` ausentes no alvo → WARN.

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

- [ ] Integridade verificada (`MANIFEST.sum` confere)
- [ ] Manifesto lido e validado (schema excrtx/v1)
- [ ] Gate OKF passou no conteúdo do pacote
- [ ] Preflight de compat (plataforma + `requires.system`) reportado
- [ ] Colisão de skills resolvida (skip/update/rename) e reportada
- [ ] Pacotes Python/Node instalados (se `--install-deps`)
- [ ] Árvore copiada para $ACERVO/micro/<name>/ (merge seguro)
- [ ] Hooks executados com sucesso (se definidos)
- [ ] Registro no manifest global atualizado + verificação OKF pós-install
