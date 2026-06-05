📋 **DRAFT — Issue GitHub**
━━━━━━━━━━━━━━━━━━━━━━━
**Repositório:** elderbernardi/exocortex.saas
**Título sugerido:** [P1] Harness de verificação pós-provisionamento: testar cada feature EX-01 a EX-35 na instância Hermes recém-instalada
**Labels:** `priority:high`, `feature`, `infra`, `testing`
━━━━━━━━━━━━━━━━━━━━━━━

## Descrição

Criar um harness de verificação executável que valide o funcionamento de **cada feature do Exocórtex (EX-01 a EX-35)** em uma instância Hermes recém-provisionada.

Este harness será o **último passo do setup** e deve executar automaticamente (ou sob demanda) para garantir que toda feature instalada esteja operacional — e, quando não estiver, que o agente tente consertar antes de reportar falha.

---

## Regras operacionais

### 1. Escopo

Cada feature catalogada em `FEATURES.md` (Parte 2, EX-01 a EX-35) deve ter **um ou mais testes** que verifiquem:

- A skill existe no runtime (`hermes skills list`)
- O SKILL.md tem frontmatter válido
- As dependências de skills estão presentes
- As dependências de tools estão disponíveis
- A função básica da skill pode ser invocada (smoke test)
- Para skills que alteram estado do sistema, verificar efeito colateral esperado

### 2. Ciclo de vida de cada teste

Para cada feature testada:

1. **Log início** — identificador do teste, feature ID, nome, timestamp
2. **Diagnóstico** — o que foi verificado, como, comando executado, retorno
3. **Resultado** — passou / falhou parcial / falhou total
4. **Encaminhamento para conserto** — instruções concretas para o agente, não para humano
5. **Auto-repair** — agente tenta consertar (até **3 tentativas**)
6. **Log do repair** — o que foi alterado, comando, resultado, re-verificação
7. **Verificação de regressão** — após cada conserto bem-sucedido, reexecutar testes de features que dependem desta (consultar mapa de dependências em FEATURES.md)
8. **Resultado final** — passou / falhou após N tentativas / falhou definitivo

### 3. Relatório final

O harness deve produzir um artefato final em `$ACERVO/_artifacts/items/` com:

- Resumo consolidado: quantas testadas, quantas passaram, quantas falharam, quantas foram reparadas
- Log completo de cada teste
- Estado final de cada feature
- Recomendações para features que falharam definitivamente

### 4. Mapa de dependências para regressão

Usar o grafo de dependências já documentado em `FEATURES.md` (seção Mapa de Dependências):

```
EX-05 (Vetor) → EX-06 (Canvas) → EX-07 (Briefing)
EX-11 (Acervo) → EX-12, EX-13, EX-14, EX-15, EX-16, EX-17
EX-21 (Quality Gate) → EX-18 (Anti-Slop), EX-19 (Taste)
EX-28 (NLM Route) → EX-29 (NLM Ops)
EX-32 (Codex Int) → EX-33 (Core), EX-34 (Ops)
etc.
```

Regressão = após reparar uma feature, re-testar features que dependem dela.

### 5. O que não testar

- **Não testar o Hermes runtime nativo** (H-01 a H-10) — isso é pré-requisito da instalação, não questão do Exocórtex
- **Não testar conectividade externa** que depende de API keys ausentes — pular com registro explícito como "pendente de key"
- **Não testar features do Hermes que não foram modificadas pelo Exocórtex**

---

## Arquivos envolvidos

- `FEATURES.md` — catálogo canônico com descrições, dependências e tools
- `setup.sh` — script que deve terminar chamando este harness
- `SOUL_SEED.md` — contrato comportamental que o self-test deve verificar
- `excrtx-assess-selftest` — skill de auto-diagnóstico existente (base para reuso)
- Skills em `skills/exocortex/excrtx-*` — fonte de cada SKILL.md

---

## Critérios de aceite

- [ ] Cada feature EX-01 a EX-35 tem pelo menos um teste
- [ ] O harness é executável via comando único (ex.: `./scripts/run-provisioning-tests.sh`)
- [ ] O relatório final é artefato no Acervo
- [ ] Auto-repair tenta 3x antes de declarar falha definitiva
- [ ] Regressão de dependências é verificada após cada reparo
- [ ] Logs são ricos o suficiente para debug remoto
- [ ] Features sem API key são registradas como "pendentes" sem falsa falha
- [ ] O harness falha rápido (fast-fail) em features que são gate para outras?

## Prioridade

**P1** — deve ser feito depois dos demais P1s (Firecrawl, gcloud, Hindsight, namespace, ruído na UI, Telegram+sudo, Syncthing), porque depende do ambiente estar estável.

━━━━━━━━━━━━━━━━━━━━━━━
⚡ **Ações:** `[Aprovar e Criar Issue]` | `[Editar]` | `[Descartar]`