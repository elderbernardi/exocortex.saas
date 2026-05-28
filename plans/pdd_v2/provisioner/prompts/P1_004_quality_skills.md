---
phase: P1
sequence: 4
name: prompt_log_quality_skills
depends_on: P1_003
exit_criteria:
  - "hermes skills list mostra 5 skills"
  - "SOUL.md contém Values #6 e #7"
  - "Smoke test stop-slop: scoring >= 35/50"
  - "Smoke test taste-skill: pre-flight check funcional"
verify_command: "hermes skills list | grep -cE 'prompt-log|stop-slop|taste-skill|design-system'"
---

Instale quatro skills nesta ordem:

1. exocortex-prompt-log — Skill que registra cada prompt significativo
   no MEMORY.md com: timestamp, intent, artifacts gerados, learnings.

2. stop-slop — Skill anti-padrões de escrita de IA.
   Adicione ao SOUL.md o Value #6 ("Estética Funcional"):
   "Toda prosa gerada por mim passa pelo crivo do stop-slop.
    Pontuação mínima: 35/50. Abaixo disso, reescrevo."

3. taste-skill — Skills anti-defaults visuais (gpt-taste, brandkit, brutalist).
   Adicione ao SOUL.md o Value #7 ("Anti-Slop Visual"):
   "Todo output visual é filtrado pelo taste-skill antes de entrega.
    Nenhuma geração visual sai sem pre-flight check."

4. exocortex-design-system — Skill de tokens visuais (DESIGN.md cascade).
   Gerencia o cascade global/DESIGN.md → micro/{slug}/DESIGN.md.
   Integra com taste-skill (validação) e brandkit (criação).

Execute smoke test para cada skill instalada.
