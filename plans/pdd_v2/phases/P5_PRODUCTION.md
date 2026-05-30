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
     * 14 skills core instaladas (+ `browser-use` quando disponível)
     * 4 camadas do acervo criadas
     * Área operacional `_artifacts/` documentada para publicação de artefatos finais
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

### Skills (14 core + `browser-use` externa no bundle quando disponível)

| # | Skill | Categoria | Fase |
|---|---|---|---|
| 1 | `exocortex-self-test` | Core | P1 |
| 2 | `exocortex-prompt-log` | Core | P1 |
| 3 | `stop-slop` | Quality | P1 |
| 4 | `taste-skill` (gpt-taste, brandkit, brutalist) | Quality | P1 |
| 5 | `exocortex-design-system` | Quality | P1 |
| 6 | `acervo-manager` | Memory | P2 |
| 7 | `exocortex-new-microverso` | Memory | P2 |
| 8 | `exocortex-draft-first` | Behavior | P3 |
| 9 | `exocortex-vetor-ativo` | Behavior | P3 |
| 10 | `exocortex-canvas` | Behavior | P3 |
| 11 | `exocortex-briefing` | Behavior | P3 |
| 12 | `exocortex-onboarding` | Behavior | P3 |
| 13 | `exocortex-output-quality-gate` | Behavior | P3 |
| 14 | `exocortex-tool-governance` | Behavior | P3 |
| 15 | `browser-use` | External | P3 |

### Capacidade pós-graduação

`personal-artifact-workspace` é extensão operacional pós-P5. Ela não altera o baseline histórico de 27 prompts, mas deve ser incorporada à próxima golden image/PDD v2.1 quando o provider Drive publicar com receipt válido em ambiente limpo.

### Profiles
- `exec` — Vetor de Execução (agente especialista, artefato tangível)
- `evol` — Vetor de Evolução (tutor socrático, expansão cognitiva)

### Acervo (4 camadas + área operacional de artefatos)
```
acervo/
├── macro/          # soul.md, valores.md, estilo.md
├── global/         # index.md + contratos/tools globais
├── micro/          # {slug}/ por domínio + _template/
├── shared/         # cross-refs/, groups.md
└── _artifacts/     # source/assets/exports/manifest/receipt de artefatos finais
```

`_artifacts/` é operacional. O Acervo semântico registra decisões, contratos e páginas de conhecimento que apontam para `artifact_id` quando necessário.

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
│  - 14 core skills          │
│  - browser-use se houver   │
│  - 4 camadas de acervo     │
│  - _artifacts operacional  │
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
- [ ] Addendum `ARTIFACT_WORKSPACE.md` revisado quando a instância precisar publicar artefatos finais

---

> **Pós-P5:** Uso real. Integrações do BACKLOG conforme critérios de reavaliação. Publicação de artefatos finais segue `ARTIFACT_WORKSPACE.md`: Drive como ferramenta, Acervo como fonte/manifesto/receipt, Draft-First para compartilhamento externo.
