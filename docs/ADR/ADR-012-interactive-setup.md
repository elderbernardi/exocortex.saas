# ADR-012: Setup Interativo com Validação de Environment

**Status:** Aceito
**Data:** 2026-06-15
**Decisão por:** Elder Bernardi

## Contexto

O `setup.sh` do Exocórtex depende de variáveis de ambiente (API keys, paths) que
devem ser definidas **antes** da execução. O fluxo atual:

1. Não mostra quais variáveis estão disponíveis/configuradas antes de rodar
2. Não permite edição inline — requer re-invocação com novos exports
3. Não valida pré-requisitos do sistema (binários, módulos Python) de forma centralizada
4. Não diferencia entre dependências obrigatórias, recomendadas e opcionais
5. Não persiste configurações entre execuções

Isso gera fricção significativa para novos usuários e re-instalações.

## Decisão

Adotar um fluxo interativo estilo `npm init` com 3 estágios pré-execução:

### Estágio 1 — Validação de Environment
Script standalone (`scripts/validate-environment.sh`) que verifica:
- Binários do sistema (16 itens, classificados por criticidade)
- Módulos Python (5 itens)
- Conectividade de rede
- Versões mínimas

Oferece: instalar faltantes, continuar, ou abortar.

### Estágio 2 — Configuração Interativa
Para cada variável/chave:
- Mostra valor atual (chaves mascaradas: `sk-or-...356f`)
- Permite confirmar (Enter) ou editar
- Persiste valores em `.env.local` (não commitado)

### Estágio 3 — Preview + Confirmação
Tabela consolidada de toda a config, com confirmação explícita antes de prosseguir.

### Flags de controle
- `--yes`: Aceita todos os defaults (modo CI/CD)
- `--init-only`: Para após confirmação, não executa steps
- `--skip-env-check`: Pula validação de environment
- `--lang=en`: Interface em inglês (default: português)

## Consequências

### Positivas
- Zero-friction para novos usuários
- Visibilidade total das configurações antes da execução
- Persistência de config sem re-export manual
- Validação proativa evita falhas silenciosas nos steps
- Compatível com CI/CD via `--yes`

### Negativas
- Complexidade adicional no setup.sh (3 novos arquivos)
- `.env.local` pode conter chaves sensíveis (mitigado: permissão 600, .gitignore)

### Neutras
- Steps existentes (00-15) não são alterados
- install.sh não é alterado (ele invoca setup.sh, que herda o novo fluxo)

## Alternativas Consideradas

1. **Wizard Python (TUI)**: Descartado por adicionar dependência de `prompt_toolkit` ou `rich`
2. **Config YAML interativo**: Descartado por complexidade de parsing em bash puro
3. **Apenas --help melhorado**: Insuficiente — não resolve persistência nem validação

## Referências
- ADR-010: Layered Deployment
- `.env.example`: Template de variáveis existente
