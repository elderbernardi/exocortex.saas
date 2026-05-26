# Fase P6: Production — Tenant Pronto

> **Status:** ⬜ Não Iniciada  
> **Prompts:** Nenhum (estado final)  
> **Depende de:** P5 score = 5/5

---

## Objetivo

Estado final da configuração PDD. O Hermes agora É o Exocórtex.IA e está pronto para uso real ou para servir como template de tenant.

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
| `exocortex-search` | Memory |
| `exocortex-new-microverso` | Memory |
| `exocortex-tool-governance` | Tools |
| `nature-contexto` | Nature |
| `nature-conhecimento` | Nature |
| `nature-instrucao` | Nature |
| `nature-persona` | Nature |
| `nature-processo` | Nature |
| `nature-ferramenta` | Nature |
| `nature-reflexao` | Nature |
| `exocortex-draft-first` | Behavior |
| `exocortex-vetor-ativo` | Behavior |
| `exocortex-canvas` | Behavior |
| `exocortex-briefing` | Behavior |
| `exocortex-onboarding` | Behavior |

### Testes Passados
- [x] Microverso CRUD
- [x] Draft-First
- [x] Vetor de Evolução (Socrático)
- [x] Morning Briefing (cross-microverso)
- [x] Self-test 5/5

---

## Uso para Multi-Tenant

Este estado P6 serve como **golden image** para provisionar novos tenants:

```bash
# Via Meta-Trainer (automático)
hermes-trainer run playbook.yaml --target tenant-new

# Via Docker (container template)
docker commit exocortex-golden exocortex-base:p6
docker run -d --name tenant-new exocortex-base:p6
```

Cada novo tenant passa pelo Prompt 023 (Onboarding) para personalizar SOUL.md, microversos e integrações.

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
