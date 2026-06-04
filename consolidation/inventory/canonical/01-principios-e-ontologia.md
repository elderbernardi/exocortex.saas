---
title: Harness Exocórtex v0.4 — Princípios e Ontologia
created: 2026-06-02
updated: 2026-06-02
nature: conhecimento
kind: concept
scope_mode: micro
scope_slug: harness-project
applies_to: [hermes-setup, acervo-cognitivo, exocortex-saas]
authority: canonical
operational_mode: advisory
stability: experimental
sources:
  - conversa executiva 2026-06-02 sobre harness Exocórtex/Hermes
derived_from: []
confidence: high
promotion_policy: candidate-shared
upstream:
  source_skill: null
  assumed_version: null
  coupling: none
tags: ["exocortex", "harness", "architecture", "v0.4"]
---

# 1. Princípios e ontologia

## 1.1 Identidade operacional

O Exocórtex.IA roda sobre o Hermes Agent.

- Hermes é infraestrutura: loop de agente, ferramentas, perfis, gateway, memória, skills, cron, subagentes, terminal e filesystem.
- Exocórtex é contrato cognitivo: modo de pensar, classificar, executar, manter, avaliar, preservar voz e exigir qualidade.

O harness é a camada que torna esse contrato operacional e repetível.

## 1.2 Objetivo do harness

O harness deve transformar conversas em sistema:

```text
input → Canvas → Tarefa → Execução/Evolução/Manutenção → Artefato/Decisão/Rotina → Avaliação → Persistência → Publicação opcional
```

Ele deve evitar dois fracassos:

1. **Chat efêmero**: boas conversas que morrem no histórico.
2. **Automação burra**: um agente que faz coisas sem elevar a qualidade da decisão ou da entrega.

## 1.3 Princípios

### Autoria preservada

O Exocórtex amplia a capacidade do usuário, mas não substitui sua autoria. Ele pode estruturar, provocar, revisar, executar e preparar decisões; decisões sensíveis permanecem com o usuário.

### Pensamento antes da ferramenta

Ferramentas são braços, não cérebro. O harness começa por Canvas e vetor; só depois decide se usa terminal, arquivo, browser, subagente, cron ou publicação.

### Execução verificável

Quando houver pedido de ação objetiva, a entrega precisa ser real e verificável: arquivo criado, comando rodado, teste executado, hash registrado, receipt salvo ou bloqueador declarado.

### Manutenção como zeladoria

Manutenção não é apenas “operação”. É cuidado contínuo do sistema: inbox, pendências, artefatos sem receipt, decisões abertas, skills obsoletas, links quebrados, microversos degradados.

### Qualidade como evolução

O objetivo não é apenas produzir; é ajudar o usuário a entregar melhor do que entregaria sozinho. Por isso existe Avaliação por Personas além do Quality Gate.

### Metadados acima de paths

Paths ajudam humanos e ferramentas, mas as relações canônicas ficam em metadados. Um artefato não “pertence” a um microverso apenas porque está em uma pasta; ele se relaciona por manifesto.

### Separação saudável das entidades

Microverso, Tarefa e Artefato são independentes:

- Microverso preserva contexto.
- Tarefa organiza intenção.
- Artefato preserva entrega.

## 1.4 Ontologia v0.4

| Entidade | Definição | Persistência |
|---|---|---|
| Canvas | Estrutura da intenção | Em tarefa persistida (`canvas.yaml`) |
| Tarefa | Intenção do usuário persistida | `acervo/_tasks/{task_id}/` |
| Artefato | Entrega reprodutível | `acervo/_artifacts/items/{artifact_id}/` |
| Microverso | Contexto cognitivo durável | `acervo/micro/{slug}/` |
| Rotina | Procedimento de manutenção/zeladoria, programável ou acionável por gatilho | `acervo/_routines/{routine_id}/` quando recorrente/auditável |
| Automação | Gatilho/scheduler/evento que aciona rotina/persona | `acervo/_automations/{automation_id}.yaml` |
| Persona | Modo de ação/avaliação | Skill, prompt, frontmatter ou config operacional |
| Decisão | Escolha resolvida ou pendência | `micro/{slug}/decisions/` ou vinculada à tarefa |
| Skill | Procedimento reutilizável | Hermes skills e/ou Acervo `skills/` |
| Manifesto | Relação canônica do artefato | `manifest.json` |
| Receipt | Prova de publicação/entrega | `receipts/` |
| Inbox | Entrada bruta compartilhável | `acervo/_inbox/` |

### Rotina vs Automação

Rotina é o procedimento de cuidado. Automação é o mecanismo que dispara a rotina.

Exemplo: “revisar decisões pendentes” é rotina; “todo domingo às 18h” é automação.

## 1.5 Vetores de alto nível

### Evolução

Pensar, formular, tensionar, explorar possibilidades, explicitar premissas, aprender, evoluir conhecimento, gerar decisões candidatas e sugerir promoção de contexto para microversos.

### Execução

Produzir algo objetivo: documento, código, plano, arquivo, export, revisão, comando, publicação privada autorizada.

### Manutenção

Zelar pelo sistema: organizar, auditar, revisar, promover, arquivar, reabrir, limpar, validar, sincronizar, publicar redundância quando aprovado.

## 1.6 Regra de dominância

Quando uma entidade dominante for necessária, ela é a **Tarefa**.

Mas a tarefa não é qualquer ação. Ela representa a intenção do usuário abstraída pelo Canvas.

## 1.7 O que não entra neste modelo

- Não transformar toda mensagem em tarefa persistida.
- Não sincronizar o Acervo inteiro com Drive.
- Não tratar path como fonte única da verdade.
- Não permitir que personas em background tomem decisões sensíveis.
- Não publicar externamente sem aprovação explícita.
