---
title: Arquitetura do Harness Exocórtex v0.4 — Índice
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

# Arquitetura do Harness Exocórtex v0.4

Este pacote consolida a arquitetura discutida para operar o Exocórtex.IA sobre o Hermes Agent como um harness cognitivo-operacional: uma camada que transforma intenção do usuário em Canvas, Tarefas, Artefatos, Avaliações, Rotinas de manutenção, Automação e memória/acervo.

A documentação está organizada em módulos para permitir implementação progressiva no Hermes sem endurecer prematuramente a ontologia do Acervo v2.

## Leitura recomendada

1. [Princípios e ontologia](01-principios-e-ontologia.md)
2. [Protocolo cognitivo e Canvas](02-protocolo-cognitivo-canvas.md)
3. [Entidades e filesystem](03-entidades-filesystem.md)
4. [Artefatos, avaliação e publicação](04-artefatos-avaliacao-publicacao.md)
5. [Personas, vetores e automações](05-personas-vetores-automacoes.md)
6. [Templates canônicos v0.4](06-templates.md)
7. [Roadmap, pendências e critérios de aceite](07-roadmap-e-pendencias.md)

## Tese central

O Exocórtex não é apenas um assistente conversacional. É uma organização cognitiva mínima operando sobre Hermes:

- **Canvas** é a forma estruturada da intenção.
- **Tarefa** é a intenção persistida derivada do Canvas.
- **Artefato** é a entrega reprodutível.
- **Microverso** é o contexto cognitivo durável.
- **Rotina** é o cuidado programável do sistema.
- **Automação** é o gatilho/scheduler/evento que aciona rotinas/personas.
- **Persona** é o modo de ação/avaliação.
- **Avaliação** é a etapa deliberada de elevação da qualidade.
- **Quality Gate** é o piso mínimo de segurança, completude e verificabilidade.

Frase canônica:

> O Exocórtex transforma intenções em Canvas; Canvas persistentes viram Tarefas; Tarefas podem gerar Artefatos; Artefatos passam por Quality Gate e, quando relevante, por Avaliação de Personas para elevar qualidade; Rotinas mantêm o sistema saudável; Microversos preservam contexto; Automação aciona Personas e Rotinas para cuidar do que não deve depender da lembrança do usuário.

## Decisões consolidadas

1. Manter o Acervo v2 como fonte canônica semântica.
2. Usar três vetores de alto nível: Evolução, Execução e Manutenção.
3. Eleger a Tarefa como entidade dominante operacional quando uma dominância for necessária.
4. Definir Tarefa como intenção do usuário abstraída pelo Canvas, não como qualquer item operacional.
5. Definir Rotina como procedimento de manutenção/zeladoria, programável, recorrente, acionável por gatilho ou intangível.
6. Centralizar tarefas em `acervo/_tasks/`, pois tarefas podem cruzar microversos.
7. Centralizar artefatos finais em `acervo/_artifacts/items/` — Modelo 2.
8. Tratar Microverso, Tarefa e Artefato como entidades independentes ligadas por metadados.
9. Separar Inbox como zona de entrada compartilhável, não como subpasta de artefatos.
10. Manter Drive como publicação expressa por ora; adiar sync amplo até haver mais experiência.
11. Usar `friendly_name` e nomes de exportação humanos para arquivos apresentados ao usuário.
12. Incluir etapa de Avaliação por personas relacionadas aos microversos da tarefa.
13. Adicionar a persona **Professor**.
14. Adicionar a persona **Cientista** para peer review epistemológico.
15. Adicionar o **Zelador de Skills** como persona/protocolo de melhoria de skills.
16. Perguntar ao usuário se deseja publicar quando um artefato estiver pronto/aprovado.

## Arquivos irmãos relevantes

- Plano de setup Hermes: `micro/hermes-setup/workflows/exocortex-harness-v0.4-setup-plan.md`
- Microverso: `micro/harness-project/`
- Futuro registro de tarefas: `acervo/_tasks/`
- Futuro registro de artefatos: `acervo/_artifacts/items/`
