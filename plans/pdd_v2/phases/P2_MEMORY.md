# P2: Memory — Acervo Cognitivo

> **Prompts:** 006–012
> **Gate:** self-test ≥ 3/5
> **Depende de:** P1 completo
> **Drift Audit:** Obrigatório ao final (Prompt 012)

---

## Propósito

Implementar o sistema de memória do Exocórtex com **arquitetura de 4 camadas
projetada desde o início** e `acervo-manager` como skill unificada.

### Mudanças fundamentais em relação ao v1

1. **4 camadas desde o design** (v1 descobriu `global/` e `shared/` durante a execução)
2. **acervo-manager como skill única** (v1 tentou 7 Nature skills e consolidou depois)
3. **Wiki architecture nativa** (index.md, promoção arquivo→diretório, archiving)

---

## Arquitetura de 4 Camadas

```
acervo/
├── macro/              # Macroverso — identidade permanente
│   ├── soul.md         # Espelho do SOUL.md (Constituição)
│   ├── valores.md      # Valores explícitos (tatuagens do Memento)
│   └── estilo.md       # Tom, voz, preferências de comunicação
│
├── global/             # Regras e conhecimento universal
│   ├── index.md        # Índice de tudo que é global
│   └── {nature}/       # Artefatos de qualquer Nature que se apliquem a tudo
│
├── micro/              # Microversos — domínios contextuais
│   ├── _template/      # Template para novos microversos
│   │   ├── index.md    # Índice do microverso (gerado pelo template)
│   │   ├── SCHEMA.md   # Schema YAML para frontmatter
│   │   └── README.md   # Guia de uso
│   └── {slug}/         # Microverso concreto (herda de macro + global)
│       ├── index.md    # Índice deste microverso
│       └── {artefatos} # Artefatos com frontmatter (Nature, tags, etc.)
│
└── shared/             # Cross-referências e agrupamentos
    ├── groups.md       # Agrupamentos de microversos
    └── cross-refs/     # Links entre artefatos de microversos diferentes
```

### 7 Natures (frontmatter, NÃO skills)

| Nature | Ícone | Descrição |
|---|---|---|
| Contexto | 🏷️ | Quem sou, onde estou |
| Conhecimento | 📚 | O que sei — já tinha ou aprendi |
| Instrução | 📝 | Prompt refinado, template |
| Persona | 🎭 | Perfil de comportamento |
| Processo | ⚙️ | Workflow, sequência de passos |
| Ferramenta | 🔧 | Capacidade descoberta |
| Reflexão | 🪞 | Meta-reflexão, o que funcionou |

---

## Prompts

### Prompt 006 — Acervo Architecture + acervo-manager

**Artefato-semente:** `artifacts/ACERVO_MANAGER.md`

**Prompt:**
```
Instale o acervo-manager a partir do artefato fornecido.

O acervo-manager é a skill ÚNICA de gestão de memória. Ele suporta:
- READ: buscar artefato por path ou query
- WRITE: criar/atualizar artefato com frontmatter (Nature, tags, scope)
- SEARCH: buscar por Nature, tags, ou texto livre
- PROMOTE: mover artefato de micro para global (ou shared)
- SCOPE: listar o que existe em uma camada

Crie a estrutura de 4 camadas:
  acervo/macro/
  acervo/global/
  acervo/micro/_template/
  acervo/shared/cross-refs/

Execute smoke test: SCOPE em cada camada (deve retornar vazio ou com seed files).
```

**Verificação:** `hermes skills list` mostra `acervo-manager` + 4 diretórios existem

---

### Prompt 007 — Macroverso Bootstrap

**Prompt:**
```
Usando o acervo-manager, popule o Macroverso:

WRITE acervo/macro/soul.md
  Nature: contexto
  Source: SOUL.md (espelho)

WRITE acervo/macro/valores.md
  Nature: reflexão
  Content: Os 7 Values do SOUL.md, expandidos com contexto

WRITE acervo/macro/estilo.md
  Nature: instrução
  Content: Regras de tom e voz (direto, sem slop, socrático quando evolução)

Verifique com SCOPE macro — deve retornar 3 artefatos.
```

---

### Prompt 008 — Global Layer + Index

**Prompt:**
```
Usando o acervo-manager, popule a camada Global:

WRITE acervo/global/index.md
  Content: Índice da camada global com links para cada Nature

Crie artefatos globais para Natures que se apliquem a todos os domínios:
- acervo/global/ferramentas-base.md (Nature: ferramenta) — ferramentas que todo microverso usa
- acervo/global/processos-transversais.md (Nature: processo) — workflows universais

Verifique com SCOPE global — deve retornar 3 artefatos (index + 2 Natures).
```

---

### Prompt 009 — Microverso Template + new-microverso skill

**Prompt:**
```
Crie a skill exocortex-new-microverso que:

1. Recebe: nome do microverso (slug), descrição, domínio
2. Cria diretório: acervo/micro/{slug}/
3. Gera: index.md (com metadata), SCHEMA.md (frontmatter YAML spec)
4. Registra: o novo microverso no MEMORY.md
5. Retorna: confirmação com path e conteúdo do index.md

O template base vive em acervo/micro/_template/.

Execute smoke test: criar microverso "test-sandbox", verificar arquivos, deletar.
```

---

### Prompt 010 — Shared Layer + Cross-refs

**Prompt:**
```
Popule a camada Shared:

WRITE acervo/shared/groups.md
  Content: Agrupamentos de microversos (tags, domínios, projetos)

Crie acervo/shared/cross-refs/ como diretório para links entre microversos.

Documente no acervo-manager como usar PROMOTE para mover artefatos
de micro/{slug}/ para global/ ou shared/.

Verifique com SCOPE shared — deve retornar 1 artefato (groups.md) + 1 diretório.
```

---

### Prompt 011 — Smoke Test: Microverso CRUD

**Prompt:**
```
Execute o teste completo de Microverso CRUD:

1. CREATE: exocortex-new-microverso "smoke-test-micro"
2. WRITE: Criar artefato de cada Nature (7 artefatos) dentro do microverso
3. READ: Ler cada artefato pelo path
4. SEARCH: Buscar por Nature "conhecimento" — deve retornar artefato correto
5. PROMOTE: Mover 1 artefato para global/
6. SCOPE: Verificar que o artefato saiu do micro e está no global
7. DELETE: Remover o microverso de teste

Todos os passos devem funcionar. Registrar resultado no session log.
```

---

### Prompt 012 — P2 Checkpoint + Drift Audit

**Prompt:**
```
Execute o self-test. Resultado esperado: ≥ 3/5.

Drift Audit de P2:
1. Skills instaladas: esperado = 6 (4 de P1 + acervo-manager + new-microverso)
2. setup.sh: reflete as 6 skills + estrutura de 4 camadas?
3. MEMORY.md: entries para prompts 006-011?
4. Acervo: 4 camadas criadas e populadas?

Corrija qualquer drift antes de avançar.
Atualize Configuration State para P3_BEHAVIOR.
```

---

## Critérios de Saída

| Critério | Verificação |
|---|---|
| acervo-manager funcional | 5 operações testadas |
| 4 camadas criadas | SCOPE em cada camada retorna artefatos |
| new-microverso funcional | Cria microverso completo a partir de template |
| CRUD smoke test | 7/7 passos passam |
| self-test ≥ 3/5 | self-test skill output |
| Drift audit PASS | 4/4 checks ✅ |
| Configuration State | P3_BEHAVIOR |

---

> **Próxima fase:** P3 (Behavior)
