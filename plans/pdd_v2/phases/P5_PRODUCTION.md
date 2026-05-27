# P5: Production — Golden Image

> **Prompts:** 027 (único)
> **Gate:** Todos os critérios anteriores + golden image exportável
> **Depende de:** P4 completo (self-test 5/5 + drift audit final PASS)

---

## Propósito

Estado final. O Hermes agora **é** o Exocórtex.IA.
A golden image está pronta para:
1. Uso real pelo executivo
2. Consumo pelo Provisioner Agent para criar novas instâncias

### Mudança em relação ao v1

No v1, P6 era uma fase separada para "Production". Na prática, P6 não tinha
ações — apenas declarava um estado. Em v2, P5 absorve esse estado final
e elimina a redundância.

---

## Prompt 027 — Graduação e Export

```
GRADUAÇÃO DO EXOCÓRTEX.IA

1. Verificação final:
   - Todos os smoke tests de P4 ainda passam? (re-executar)
   - self-test = 5/5?
   - Drift audit = PASS?

2. setup.sh definitivo:
   - Garantir que setup.sh reproduz 100% do estado:
     * 13 skills instaladas
     * 4 camadas do acervo criadas
     * Bundle e profiles configurados
     * SOUL.md com 7 Values
   - Testar: executar setup.sh em diretório limpo e comparar

3. BACKLOG_INTEGRATIONS.md:
   - Atualizar status de cada item
   - Documentar o que foi resolvido com alternativas (ex: DDG)
   - Manter critérios de reavaliação para itens pendentes

4. MEMORY.md:
   - Verificar que contém log completo de todos os 27 prompts
   - Adicionar entry de graduação

5. Configuration State:
   - Atualizar para PRODUCTION
   - Adicionar timestamp de graduação

RESULTADO:
  O Exocórtex.IA está em estado PRODUCTION.
  O setup.sh é a receita reproduzível.
  O Provisioner Agent pode consumir esta golden image.
```

---

## Estado Final Esperado

### Skills (13 no bundle `exocortex-alpha`)

| # | Skill | Categoria | Fase |
|---|---|---|---|
| 1 | `exocortex-self-test` | Core | P1 |
| 2 | `exocortex-prompt-log` | Core | P1 |
| 3 | `stop-slop` | Quality | P1 |
| 4 | `taste-skill` (gpt-taste, brandkit, brutalist) | Quality | P1 |
| 5 | `acervo-manager` | Memory | P2 |
| 6 | `exocortex-new-microverso` | Memory | P2 |
| 7 | `exocortex-draft-first` | Behavior | P3 |
| 8 | `exocortex-vetor-ativo` | Behavior | P3 |
| 9 | `exocortex-canvas` | Behavior | P3 |
| 10 | `exocortex-briefing` | Behavior | P3 |
| 11 | `exocortex-onboarding` | Behavior | P3 |
| 12 | `exocortex-output-quality-gate` | Behavior | P3 |
| 13 | `exocortex-tool-governance` | Behavior | P3 |

### Profiles
- `exec` — Vetor de Execução (agente especialista, artefato tangível)
- `evol` — Vetor de Evolução (tutor socrático, expansão cognitiva)

### Acervo (4 camadas)
```
acervo/
├── macro/          # soul.md, valores.md, estilo.md
├── global/         # index.md + Natures universais
├── micro/          # {slug}/ por domínio + _template/
└── shared/         # cross-refs/, groups.md
```

### Ferramentas Opcionais (fora do bundle core)
- `duckduckgo-search` — se disponível
- `browser-use` — se disponível
- MCPs — conforme BACKLOG_INTEGRATIONS.md

### Logs
- `plans/pdd_v2/logs/session_P1.log` — P5
- `MEMORY.md` — Log completo de 27 prompts

---

## Modelo de Provisioning

```
┌─────────────────────────────┐
│  Provisioner Agent          │
│  (Meta-Trainer / Externo)   │
│                             │
│  1. Lê plans/pdd_v2/       │
│  2. Executa setup.sh        │
│  3. Injeta artefatos-semente│
│  4. Executa PLAYBOOK.yaml   │
│  5. Valida com self-test    │
│                             │
│  Resultado: Nova instância  │
│  Exocórtex.IA em PRODUCTION │
└─────────────────────────────┘
        │
        ▼
┌─────────────────────────────┐
│  Hermes-Alvo                │
│  (Instância do Executivo)   │
│                             │
│  - 13 skills                │
│  - 4 camadas de acervo      │
│  - 2 profiles               │
│  - SOUL.md personalizado    │
│  - Quality gates ativos     │
│                             │
│  Configuration State:       │
│  PRODUCTION                 │
└─────────────────────────────┘
```

---

## Critérios de Saída Finais

- [ ] Configuration State = PRODUCTION
- [ ] setup.sh reproduz o estado completo em ambiente limpo
- [ ] BACKLOG_INTEGRATIONS.md atualizado
- [ ] MEMORY.md contém log completo (27 prompts)
- [ ] Todos os testes de P4 re-executados e passando
- [ ] self-test = 5/5
- [ ] Drift audit = PASS

---

> **Pós-P5:** Uso real. Integrações do BACKLOG conforme critérios de reavaliação.
