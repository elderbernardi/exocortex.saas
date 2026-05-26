# Fase P2: Memory — Estrutura Cognitiva

> **Status:** ⬜ Não Iniciada  
> **Prompts:** 006–010  
> **Checkpoint:** self-test score ≥ 3/5  
> **Depende de:** P1 completo  
> **Estimated Time:** 1-2 horas

---

## Objetivo

Criar o Acervo Cognitivo (7 Natures), skills de gerenciamento de Microversos, e busca semântica.

---

## Prompts

### Prompt 006 — Acervo Cognitivo Structure

Criar diretórios em `HERMES_HOME`:

```
acervo/
├── macro/          # Macroverso (Identidade)
│   ├── soul.md, valores.md, estilo.md
├── micro/          # Microversos (Domínios)
│   └── _template/  # 7 arquivos (1 por Nature)
│       ├── contexto.md, conhecimento.md, instrucoes.md
│       ├── persona.md, processos.md, ferramentas.md, reflexoes.md
└── shared/         # Conhecimento transversal
    └── glossario.md
```

Cada template deve ter: Header, Purpose, Format, Examples.

**Validação:** `ls acervo/` mostra estrutura completa.

---

### Prompt 007 — 7 Nature Skills

Criar 7 skills (`nature-{nome}`), uma para cada Nature:
1. `nature-contexto` — injetar contexto de domínio
2. `nature-conhecimento` — indexar/buscar knowledge
3. `nature-instrucao` — aplicar regras condicionais
4. `nature-persona` — alternar personas por domínio
5. `nature-processo` — executar workflows multi-step
6. `nature-ferramenta` — gerenciar tools por domínio
7. `nature-reflexao` — registrar auto-aprendizados

Cada skill: frontmatter YAML + Trigger + Procedure + Verification.

**Validação:** `hermes skills list` mostra 7 nature skills.

---

### Prompt 008 — Microverso Creation Skill

Skill `exocortex-new-microverso`:
- Copia `_template/` para `micro/{slug}/`
- Preenche contexto.md
- Entrevista executivo (ferramentas, persona, regras)
- Registra em MEMORY.md

**Teste:** Criar `teste-financeiro`, verificar, deletar.

---

### Prompt 009 — Memory Indexing

Configurar busca semântica (sqlite-vec/FTS5) no Acervo:
- Segmentar documentos por parágrafos
- Embedar e armazenar com metadados (nature, microverso, timestamp)
- Skill `exocortex-search` para busca híbrida

**Teste:** 3 docs fictícios → busca por tema → resultados relevantes.

---

### Prompt 010 — P2 Checkpoint

self-test completo. Critérios:
1. `acervo/` completo
2. 7 Nature skills instaladas
3. `exocortex-new-microverso` funcional
4. Busca semântica funcional
5. MEMORY.md com log 006-010

Se OK → `current_phase: P3_TOOLS`

---

## Próximo

Após P2 → `P3_TOOLS.md`
