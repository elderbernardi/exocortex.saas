---
type: context
title: "Microverso: Estúdio Editorial"
description: "Type: `domain`"
tags: [estudio-editorial, schema, editorial]
timestamp: 2026-07-07
class: perene
created_at: 2026-07-07T19:13:18Z
last_accessed_at: 2026-07-07T19:13:18Z
nature: context
---

# Microverso: Estúdio Editorial

Type: `domain`

Descrição: Centro canônico para editoração de trabalhos escritos e artefatos de comunicação elaborada.

## Escopo

O Estúdio Editorial é o centro canônico do Exocórtex para editoração de trabalhos escritos: livros, manuais, guias, notícias editoriais, reportagens, ensaios, séries narrativas e comunicações que exigem elaboração maior que uma peça avulsa.

Ele não substitui o Estúdio Criativo. O Estúdio Criativo governa criação, linguagem, design e produção ampla. O Estúdio Editorial governa método editorial: pauta, linha editorial, voz autoral, arquitetura de obra, revisão, canon textual, publicação e reaproveitamento de corpus escrito.

## Tipo

`domain`: capacidade funcional permanente.

## Relação com outros microversos

- Atua como microverso próprio quando a demanda é editorial.
- Atua em tarefas mistas quando outro microverso fornece o domínio do conteúdo e este fornece método editorial.
- Mantém fronteira com `estudio-criativo`: editorial cuida de obras e textos longos; criativo cuida de conceito, visual, campanha e artefatos multimodais.
- A integração `autonovel` entra como referência técnica e metodológica, não como verdade literária universal.

## Contratos locais

1. Voz autoral antes de automação.
2. Canon textual antes de expansão.
3. Estrutura editorial antes de produção em massa.
4. Revisão adversarial antes de publicação.
5. Fontes brutas ficam em `raw/`; síntese canônica fica nas natures.
6. Comunicação externa, publicação, envio ou alteração de documento compartilhado exige Draft-First.
7. Ferramentas externas e dependências só entram no runtime após aprovação explícita e teste local.

## Taxonomia inicial

- `editorial`: editoração, linha editorial, publicação.
- `book`: livros e manuscritos longos.
- `manual`: manuais, guias, apostilas e documentação autoral.
- `journalism`: notícias editoriais, reportagens e pauta.
- `canon`: fatos duros, continuidade, consistência e decisões de obra.
- `voice`: voz autoral, estilo, tom, anti-slop.
- `revision`: revisão, crítica, corte, reescrita e validação.
- `autonovel`: referência externa NousResearch/autonovel.

## Lint local

- Não confundir texto longo com texto inchado.
- Não deixar a IA apagar a voz do autor.
- Não publicar texto sem rodada de crítica adversarial.
- Não tratar output gerado como canônico antes de revisão humana.
- Não misturar conteúdo de domínio atendido dentro deste microverso; usar ponteiros e cross-refs.
