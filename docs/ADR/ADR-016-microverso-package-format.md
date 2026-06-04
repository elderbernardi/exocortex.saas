---
adr: "016"
titulo: "Microverso Package Format"
status: aceito
data: 2026-06-04
decisores: ["executivo", "exocortex-team"]
---

# ADR-016: Microverso Package Format

## Contexto

O executivo observou: *"Microversos não são só os arquivos. São as skills, pacotes dependentes."* O RC1 instala microversos como diretórios soltos (`acervo/micro/{slug}/`), mas não declara nem verifica dependências. Um microverso que depende de `excrtx-produce-slides` para funcionar não tem como expressar essa dependência — se a skill estiver ausente, o agente falha silenciosamente.

Necessidades identificadas:
1. Instalar um microverso com um comando (ou pelo setup.sh)
2. Declarar e verificar dependências (skills, pacotes Python/Node, MCPs)
3. Validar integridade pós-instalação
4. Permitir extensões de terceiros (microversos distribuíveis)

## Decisão

### O `microverso.yaml` — Manifesto de Pacote

Cada microverso empacotado contém um `microverso.yaml` na raiz do diretório, seguindo o schema `excrtx/v1`:

```yaml
apiVersion: excrtx/v1
kind: Microverso
metadata:
  name: estudio-criativo
  version: 1.0.0
  description: "Microverso para produção criativa — slides, apresentações, design thinking"
  author: exocortex-team
  tags: [criativo, design, slides, produção]

requires:
  skills:
    - excrtx-produce-slides
    - excrtx-quality-designsys
    - excrtx-behavior-canvas
  python_packages:
    - python-pptx>=0.6.21
  node_packages: []
  mcps: []

tree:
  contracts/: "Contratos e manifestos"
  workflows/: "Workflows de produção"
  templates/: "Templates reutilizáveis"
  personas/: "Personas do microverso"
  prompts/: "Prompts testados"
  knowledge/: "Base de conhecimento"
  decisions/: "ADRs locais"
  reflections/: "Meta-reflexões"
  tools/: "Scripts utilitários"
  skills/: "Skills locais do microverso (se houver)"

hooks:
  post_install: "scripts/post_install.sh"
  validate: "scripts/validate.sh"
```

### Campos Obrigatórios

| Campo | Obrigatório | Descrição |
|-------|-------------|-----------|
| `apiVersion` | ✅ | Sempre `excrtx/v1` (versionamento futuro) |
| `kind` | ✅ | Sempre `Microverso` |
| `metadata.name` | ✅ | Slug único, lowercase, hifenizado |
| `metadata.version` | ✅ | SemVer |
| `metadata.description` | ✅ | Descrição curta |
| `requires.skills` | ❌ | Lista de skills necessárias (verificadas na instalação) |
| `requires.python_packages` | ❌ | Pacotes pip/uv (PEP 508 format) |
| `requires.node_packages` | ❌ | Pacotes npm |
| `requires.mcps` | ❌ | MCP servers necessários |
| `tree` | ❌ | Mapeamento dir → descrição (documentacional) |
| `hooks` | ❌ | Scripts de pós-instalação e validação |

### Fluxo de Instalação (skill `excrtx-memory-mvinstall`)

```
excrtx-memory-mvinstall
  ├── 1. Lê microverso.yaml
  ├── 2. Verifica requires.skills (existem no bundle?)
  │     └── Se falta → WARN + oferecer instalação
  ├── 3. Verifica requires.python_packages
  │     └── Se falta → uv pip install (se uv disponível)
  ├── 4. Copia árvore para $ACERVO/micro/{name}/
  ├── 5. Executa hooks.post_install (se existir)
  ├── 6. Registra no manifest global ($ACERVO/global/_meta/microversos.yaml)
  └── 7. Executa hooks.validate (se existir)
```

### Registro Global

Microversos instalados são registrados em `$ACERVO/global/_meta/microversos.yaml`:

```yaml
installed:
  - name: estudio-criativo
    version: 1.0.0
    installed_at: "2026-06-04T15:00:00Z"
    path: micro/estudio-criativo
    status: active
```

### Microversos sem `microverso.yaml`

Microversos legados (sem manifesto) continuam funcionando — são diretórios soltos no acervo. O sistema não exige `microverso.yaml` para operar. O manifesto é obrigatório apenas para:
- Verificação de dependências
- Distribuição como pacote
- Registro no manifest global
- Hooks de pós-instalação

### Segurança

- Hooks (`post_install`, `validate`) executam apenas scripts **dentro** do diretório do microverso — paths absolutos ou `../` são rejeitados
- Pacotes Python/Node são instalados via ferramentas locais (uv, npm) — sem `curl | bash`
- Microversos de terceiros requerem aprovação do executivo antes da instalação (Draft-First Protocol)

## Consequências

- Microversos passam de "pasta de arquivos" para "pacote com contrato"
- Dependências de skills ficam explícitas e verificáveis
- O Estúdio Criativo existente ganha `microverso.yaml` como primeiro exemplo
- Extensões de terceiros têm um formato padronizado para distribuição
- O setup.sh pode verificar integridade dos microversos durante instalação
