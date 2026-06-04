---
title: Workflow — Hindsight como Memória Operacional do Exocórtex
created: 2026-05-31
updated: 2026-06-01
nature: processos
kind: workflow
scope_mode: micro
scope_slug: hermes-setup
applies_to: [global]
authority: canonical
operational_mode: executable
stability: active
sources: [contracts/hindsight-operational-memory-contract.md, plugins/memory/hindsight/README.md]
derived_from: []
confidence: high
promotion_policy: candidate-global
upstream:
  source_skill: autonomous-ai-agents/hermes-agent
  assumed_version: null
  coupling: adapter-only
tags: [hindsight, memory, exocortex, operational-memory, setup, workflow]
---

# Workflow — Hindsight como Memória Operacional do Exocórtex

## Objetivo

Instalar e operar Hindsight como camada auxiliar de memória semântica do agente, mantendo o harness do Exocórtex como primário.

## Modelo mental

```text
Hindsight observa e recupera.
Exocórtex interpreta.
Acervo canoniza.
Skills proceduralizam.
Built-in memory (local simples) fica desativada quando Hindsight estiver ativo.
Session Search preserva histórico literal.
```

## Pré-requisitos

1. Hermes instalado e funcional.
2. Plugin Hindsight disponível no Hermes.
3. Contrato `contracts/hindsight-operational-memory-contract.md` aceito.
4. Template de configuração presente em `templates/hindsight-config.local_embedded.json`.
5. Decisão sobre backend LLM para `local_embedded`:
   - local real: Ollama, llama.cpp, vLLM ou LM Studio;
   - self-hosted: endpoint OpenAI-compatible sob controle próprio;
   - API externa: apenas para piloto, com consciência de envio de dados.

## Instalação controlada

1. Validar status atual:

```bash
hermes memory status
```

2. Rodar setup com ativação explícita:

```bash
EXOCORTEX_ENABLE_HINDSIGHT=1 bash ~/.hermes/setup.sh
```

3. O setup sincroniza `llm_model` e `llm_base_url` do `~/.hermes/config.yaml` para `~/.hermes/hindsight/config.json` quando houver `CHANGE_ME`.

4. Se ainda existir `CHANGE_ME` após sync automático, editar manualmente `~/.hermes/hindsight/config.json`. Enquanto existir `CHANGE_ME`, o setup preserva segurança operacional e não altera `memory.provider` para `hindsight`.

5. Validar provider:

```bash
hermes memory status
```

6. Reiniciar a superfície ativa:

```text
CLI: encerrar e abrir nova sessão.
Gateway: /restart ou reinício do serviço.
```

## Configuração inicial recomendada

```json
{
  "memory_mode": "hybrid",
  "auto_recall": true,
  "auto_retain": true,
  "retain_async": true,
  "retain_every_n_turns": 2,
  "recall_budget": "low",
  "recall_prefetch_method": "recall",
  "recall_types": "observation",
  "recall_max_tokens": 1200,
  "recall_max_input_chars": 800
}
```

## Uso pelo agente

Quando Hindsight trouxer contexto:

1. Tratar como observação operacional.
2. Verificar se conflita com SOUL, contratos, skills, built-in memory ou Acervo.
3. Usar apenas se melhorar a resposta atual.
4. Não expor detalhes técnicos internos ao executivo quando não forem relevantes.
5. Se a observação for estratégica, propor promoção ao Acervo.

## Promoção

Usar este funil:

```text
Hindsight observation
→ candidato
→ Acervo decision/contract/workflow/reflection
→ skill, se virar procedimento
→ built-in memory, se for invariante compacto
```

Critérios para promover:

- recorrência em mais de uma sessão;
- correção explícita do executivo;
- impacto em decisões futuras;
- regra operacional reutilizável;
- dependência para replicabilidade do setup.

## Ajuste de ruído

Se Hindsight sobrecarregar contexto:

1. Reduzir `recall_max_tokens` para 800.
2. Manter `recall_types: observation`.
3. Manter `recall_budget: low`.
4. Aumentar `retain_every_n_turns` para 3 ou 4.
5. Considerar `memory_mode: tools` para recall sob demanda.

Se Hindsight for pouco útil:

1. Aumentar `recall_budget` para `mid`.
2. Aumentar `recall_max_tokens` para 1800.
3. Ajustar `bank_retain_mission`.
4. Testar `hindsight_reflect` sob demanda em perguntas de síntese.

## Auditoria de 7 dias

Verificar:

- Houve redução de perguntas repetidas?
- O recall trouxe contexto útil?
- Houve ruído no output?
- Houve confusão entre observação e decisão?
- Houve aumento perceptível de latência?
- Alguma memória deveria virar Acervo?

## Auditoria de 14 dias

Escolher uma decisão:

1. Manter Hindsight como provider default.
2. Manter Hindsight apenas em perfis específicos.
3. Trocar `memory_mode` para `tools`.
4. Reduzir retenção automática.
5. Desativar Hindsight.
6. Comparar com Holographic como alternativa local-controlada.

## Desativação

```bash
hermes config set memory.provider none
hermes config set memory.memory_enabled true
hermes config set memory.user_profile_enabled true
```

Depois reiniciar a sessão ou gateway. O Exocórtex deve continuar operando com memória simples local, Session Search, skills e Acervo.

## Política de bank para este Hermes

- `bank_id_template` padrão: `exocortex`
- Perfis `exec` e `evol` compartilham o mesmo bank.
- Isolamento por profile não é usado neste setup.
