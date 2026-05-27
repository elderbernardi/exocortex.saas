# P0: Foundation — Pré-requisitos e Protocolo

> **Tipo:** Manual (Operador ou Provisioner Agent)
> **Prompts:** Nenhum
> **Gate:** Todos os artefatos-semente existem + setup.sh funcional

---

## Propósito

P0 é a preparação do terreno. Nenhuma interação com o Hermes-alvo acontece aqui.
O operador (humano ou Provisioner Agent) prepara os artefatos que os agentes
de P1+ precisam encontrar.

### Por que P0 existe em v2 (não existia em v1)?

No v1, a preparação era implícita e desorganizada. O agent_protocol foi
inventado durante a execução. As quality skills foram empurradas para P4.
O resultado: drift nas fases iniciais, setup.sh desatualizado, e prosa
de baixa qualidade nos artefatos de P2/P3.

P0 resolve isso codificando a preparação como fase formal.

---

## Artefatos-Semente

### 1. `PLAYBOOK.yaml` (este playbook)
- **Path:** `plans/pdd_v2/PLAYBOOK.yaml`
- **Conteúdo:** Protocolo de execução + agent_protocol v2 + drift_audit spec
- **O agente de P1 lê este arquivo PRIMEIRO.**

### 2. `artifacts/setup.sh` (semente)
- **Path:** `plans/pdd_v2/artifacts/setup.sh`
- **Conteúdo inicial:** Header + variáveis + estrutura de diretórios
- **Regra:** Cresce com cada fase. Ao final de P5, reproduz o estado completo.

### 3. `artifacts/SELF_TEST_SKILL.md`
- **Origem:** `.hermes/skills/exocortex/exocortex-self-test/SKILL.md` (v1)
- **Conteúdo:** Skill de auto-diagnóstico com scoring progressivo
- **Ajuste v2:** Nenhum (funcional como está)

### 4. `artifacts/SOUL_SEED.md`
- **Origem:** `plans/pdd/artifacts/SOUL_SEED.md` (v1)
- **Conteúdo:** Template de identidade com seções a serem preenchidas por P1
- **Ajuste v2:** Adicionar placeholders para Values #6 (stop-slop) e #7 (taste-skill)

### 5. `artifacts/STOP_SLOP_SKILL.md`
- **Origem:** `.hermes/skills/exocortex/stop-slop/SKILL.md` (v1)
- **Conteúdo:** Regras de escrita anti-slop + scoring 1-10
- **Ajuste v2:** Nenhum (funcional como está)

### 6. `artifacts/TASTE_SKILL/`
- **Origem:** `.hermes/skills/exocortex/taste-skill/` (v1)
- **Conteúdo:** gpt-taste, brandkit, brutalist sub-skills
- **Ajuste v2:** Nenhum (funcional como está)

### 7. `artifacts/ACERVO_MANAGER.md`
- **Origem:** `.hermes/skills/exocortex/acervo-manager/SKILL.md` (v1)
- **Conteúdo:** Skill unificada do acervo (4 camadas, 5 operações, wiki architecture)
- **Ajuste v2:** Verificar que schema YAML e 4 camadas estão documentados

### 8. `artifacts/BACKLOG_TEMPLATE.md`
- **Conteúdo:** Template para integrações futuras (MCPs, APIs)
- **Formato:** Tabela com: ID, Integração, Status, Motivo do Diferimento, Critérios de Reavaliação, Dependências

---

## Procedimento

```bash
# 1. Criar estrutura de diretórios
mkdir -p plans/pdd_v2/{phases,artifacts,logs}

# 2. Copiar artefatos-semente do v1
cp .hermes/skills/exocortex/exocortex-self-test/SKILL.md plans/pdd_v2/artifacts/SELF_TEST_SKILL.md
cp plans/pdd/artifacts/SOUL_SEED.md plans/pdd_v2/artifacts/SOUL_SEED.md
cp .hermes/skills/exocortex/stop-slop/SKILL.md plans/pdd_v2/artifacts/STOP_SLOP_SKILL.md
cp -r .hermes/skills/exocortex/taste-skill/ plans/pdd_v2/artifacts/TASTE_SKILL/
cp .hermes/skills/exocortex/acervo-manager/SKILL.md plans/pdd_v2/artifacts/ACERVO_MANAGER.md

# 3. Criar setup.sh semente
cat > plans/pdd_v2/artifacts/setup.sh << 'EOF'
#!/bin/bash
# Exocórtex.IA — PDD v2 Setup Script
# This script grows with each phase. At P5 it reproduces the full state.
# Version: 2.0.0-seed
# Phase: P0 (Foundation)
set -euo pipefail

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
EXOCORTEX_SKILLS="$HERMES_HOME/skills/exocortex"

echo "=== Exocórtex.IA PDD v2 Setup ==="
echo "Phase: P0 (Foundation)"
echo "Target: $HERMES_HOME"

# Phase P0: Create directories
mkdir -p "$EXOCORTEX_SKILLS"
mkdir -p "$HERMES_HOME/acervo"/{macro,global,micro/_template,shared/cross-refs}

echo "=== P0 Complete ==="
EOF
chmod +x plans/pdd_v2/artifacts/setup.sh

# 4. Criar BACKLOG_TEMPLATE.md
cat > plans/pdd_v2/artifacts/BACKLOG_TEMPLATE.md << 'EOF'
# Backlog de Integrações

| ID | Integração | Status | Motivo | Critério de Reavaliação | Dependências |
|---|---|---|---|---|---|
| BKL-001 | Google Workspace (OAuth) | Diferido | API keys não disponíveis | Quando OAuth estiver configurado | Google Cloud Project |
| BKL-002 | Observability MCP | Diferido | Sem infra de métricas | Quando Prometheus/Grafana disponível | Monitoring stack |
EOF

# 5. Verificar
echo "=== P0 Verification ==="
ls -la plans/pdd_v2/artifacts/
echo "✅ P0 Foundation complete"
```

---

## Critérios de Saída

- [ ] `plans/pdd_v2/artifacts/` contém todos os 8 artefatos
- [ ] `setup.sh` executa sem erros
- [ ] `PLAYBOOK.yaml` contém `agent_protocol` com 6 regras (5 originais + DRIFT_AUDIT)
- [ ] `logs/` existe e está vazio
- [ ] `RETROSPECTIVE.md` existe (base factual)
- [ ] `PLAN.md` existe (plano v2)

---

> **Próxima fase:** P1 (Identity)
