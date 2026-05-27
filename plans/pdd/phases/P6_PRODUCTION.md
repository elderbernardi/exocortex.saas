# Fase P6: Production — Tenant Pronto

> **Status:** ✅ Ready (2026-05-27) — Golden image pronta  
> **Prompts:** Nenhum (estado final)  
> **Depende de:** P5 score = 5/5

---

## Objetivo

Estado final da configuração PDD. O Hermes agora É o Exocórtex.IA e está pronto para uso real ou para servir como **golden image** consumida pelo Provisioner Agent.

---

## Estado Esperado

### Artefatos
- `SOUL.md` — Identidade completa com Configuration State = P6
- `MEMORY.md` — Log completo de 28 prompts + histórico
- `acervo/` — Estrutura macro/micro/shared completa
- `config.yaml` — MCPs configurados e governance aplicada

### Skills Instaladas
| Skill | Categoria |
|---|---|
| `exocortex-self-test` | Core |
| `exocortex-prompt-log` | Core |
| `acervo-manager` | Memory (consolida 7 Natures — ADR-005) |
| `exocortex-new-microverso` | Memory |
| `exocortex-tool-governance` | Tools |
| `stop-slop` | Quality (textual) |
| `taste-skill` | Quality (visual — gpt-taste, brandkit, brutalist) |
| `exocortex-draft-first` | Behavior |
| `exocortex-vetor-ativo` | Behavior |
| `exocortex-canvas` | Behavior |
| `exocortex-briefing` | Behavior |
| `exocortex-onboarding` | Behavior |
| `exocortex-output-quality-gate` | Behavior (Executor Gate) |

### Bundle
- `exocortex-alpha` — carrega skills Core + Memory + Quality via `/exocortex-alpha`

### Profiles
- `exec` — Vetor de Execução
- `evol` — Vetor de Evolução

### Testes Passados
- [x] Microverso CRUD
- [x] Draft-First
- [x] Vetor de Evolução (Socrático)
- [x] Morning Briefing (cross-microverso)
- [x] Quality Gate — Prosa (stop-slop ≥ 35/50)
- [x] Quality Gate — Visual (taste-skill pre-flight)
- [x] Self-test 5/5

### MCPs (Backlog)
Ver `BACKLOG_INTEGRATIONS.md` — integrações externas a ativar pós-P6.

---

## Uso para Multi-Tenant

Este estado P6 serve como **golden image** consumida pelo **Provisioner Agent** — um agente dedicado e separado, que NÃO é uma instância do Exocórtex do executivo.

### Modelo de Provisionamento

```
[Provisioner Agent]  →  cria container + HERMES_HOME isolado
                     →  instala golden image (P6)
                     →  configura secrets/API keys
                     →  ativa instância
                             ↓
[Hermes do Executivo] →  inicializa com bundle exocortex-alpha
                      →  detecta acervo vazio
                      →  executa Onboarding (Prompt 023)
                      →  personaliza SOUL.md + microversos
```

### Responsabilidades

| Agente | Responsabilidade |
|---|---|
| **Provisioner Agent** | Criar container, instalar golden image, configurar infra, ativar instância |
| **Hermes do Executivo** | Executar onboarding, personalizar identidade, operar no dia-a-dia |

> ⚠️ O Hermes do executivo **nunca** provisiona outros tenants. Um Exocórtex não se auto-replica. O Provisioner pode ser outro Hermes dedicado a essa função, ou um serviço na Code Branch (E4).

---

## Transição para Code Branch

Quando o PDD atinge seus limites (features que Hermes vanilla não suporta), a Code Branch assume:

| Necessidade | Solução (Code Branch) |
|---|---|
| Multi-tenant control plane | `control-plane/` service |
| HITL Cockpit web | `web/` Next.js app |
| Custom MCP servers | `mcp-servers/` Python |
| Container orchestration | Docker Compose → K8s |

Ver `../code/PLAN.md` para detalhes.
