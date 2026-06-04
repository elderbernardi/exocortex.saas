# Marp e Frontend Slides — Trilhas de Artefato

## Princípio

Marp é linha de produção. Frontend Slides é renderer premium.

Ambos preservam Markdown como fonte canônica sempre que possível. A escolha do renderer depende do objetivo do artefato, não do microverso sozinho.

## Quando usar Marp

Use Marp para:

- aula recorrente;
- material técnico com muito código;
- manutenção manual frequente;
- PDF rápido;
- produção seriada por unidade/disciplina;
- decks onde consistência e velocidade valem mais que direção visual.

## Quando usar Frontend Slides

Use `exocortex-slides` para:

- apresentação premium;
- palestra;
- pitch;
- briefing executivo;
- aula especial;
- abertura/fechamento de unidade;
- artefato com narrativa visual forte;
- HTML navegável como entrega principal.

## Regra de export

Google Drive privado é o destino padrão para entrega final ao usuário comum.

Vercel ou publicação pública só entram quando o usuário pede URL pública e aprova o DRAFT.

## Pacote recomendado

```text
_artifacts/{artifact_id}/
├── source/
│   ├── source.md
│   ├── brief.md
│   └── slides.marp.md
├── assets/
├── previews/
├── exports/
│   ├── deck.html
│   ├── deck.pdf
│   └── deck.zip
└── manifest.json
```

## Relação com Estúdio Criativo

Se o deck precisa de tese visual forte, Frontend Slides consulta Estúdio Criativo. Se Estúdio Criativo precisa entregar apresentação, chama Frontend Slides para empacotar e exportar.
