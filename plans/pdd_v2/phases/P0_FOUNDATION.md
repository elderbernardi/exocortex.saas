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

O diretório `artifacts/` é a **golden image autocontida**. Tudo que o Hermes
precisa para se tornar um Exocórtex está aqui. `setup.sh` copia tudo para `~/.hermes/`.

### 1. `PLAYBOOK.yaml` (protocolo de execução)
- **Path:** `plans/pdd_v2/PLAYBOOK.yaml`
- **Conteúdo:** Protocolo de execução + agent_protocol v2 + drift_audit spec
- **O agente de P1 lê este arquivo PRIMEIRO.**

### 2. `artifacts/setup.sh`
- Script de provisionamento: copia skills, acervo, profiles e bundle para `HERMES_HOME`.
- **Uso:** `HERMES_HOME=/path/to/hermes bash artifacts/setup.sh`
- **Idempotente:** pode ser re-executado sem efeitos colaterais.

### 3. `artifacts/skills/` (15 skills)
Espelho de `~/.hermes/skills/exocortex/`. Cada subdiretório contém `SKILL.md` + recursos.

| Categoria | Skills |
|---|---|
| Core | `exocortex-self-test`, `exocortex-prompt-log` |
| Quality | `stop-slop`, `taste-skill`, `exocortex-design-system` |
| Memory | `acervo-manager`, `exocortex-new-microverso` |
| Behavior | `exocortex-draft-first`, `exocortex-vetor-ativo`, `exocortex-canvas`, `exocortex-briefing`, `exocortex-onboarding`, `exocortex-output-quality-gate`, `exocortex-tool-governance` |
| External | `browser-use` (requer tooling no host) |

### 4. `artifacts/acervo/` (4 camadas)
Espelho de `~/.hermes/acervo/`. Estrutura wiki com 4 camadas:
- `macro/` — soul.md, valores.md, estilo.md, assets/
- `global/` — index.md, DESIGN.md (tokens visuais), 7 Natures
- `micro/_template/` — Template de microverso com suporte a DESIGN.md override
- `shared/` — cross-refs/, groups.md, glossario.md

### 5. `artifacts/profiles/` (2 profiles)
- `exec/` — Vetor de Execução (foco em resultado tangível)
- `evol/` — Vetor de Evolução (foco em compreensão)

### 6. `artifacts/skill-bundles/exocortex-alpha.yaml`
Bundle principal com 14 skills core + `browser-use` como skill externa incluída quando disponível.

### 7. `artifacts/SOUL_SEED.md`
Template de identidade. Base para o SOUL.md que será construído em P1.

### 8. `artifacts/BACKLOG_TEMPLATE.md`
Template para integrações futuras (MCPs, APIs externas) com critérios de reavaliação.

---

## Procedimento

```bash
# Em uma instância Docker limpa do Hermes:
HERMES_HOME=~/.hermes bash plans/pdd_v2/artifacts/setup.sh

# Verificação:
ls ~/.hermes/skills/exocortex/     # 15 skills
ls ~/.hermes/acervo/               # macro/ global/ micro/ shared/
cat ~/.hermes/skill-bundles/exocortex-alpha.yaml  # bundle com 14 core + browser-use externo quando disponível
cat ~/.hermes/SOUL.md              # SOUL_SEED.md copiado
```

---

## Critérios de Saída

- [ ] `setup.sh` executa sem erros em instância limpa
- [ ] 15 skills copiadas para `~/.hermes/skills/exocortex/`
- [ ] Acervo com 4 camadas populadas
- [ ] Bundle `exocortex-alpha.yaml` instalado
- [ ] SOUL.md instalado (de SOUL_SEED.md)
- [ ] Profiles `exec` e `evol` instalados
- [ ] `PLAYBOOK.yaml` existe com `agent_protocol` + `drift_audit`
- [ ] `logs/` existe (para session logs de P1+)

---

> **Próxima fase:** P1 (Identity)

