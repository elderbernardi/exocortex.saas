---
name: exocortex-slides
description: "Use when creating premium HTML/PDF/ZIP presentation exports from Markdown, Marp Markdown, PPTX, or deck briefs inside Exocórtex. Keeps Markdown as canonical source, resolves Design System by microverso, and uses Google Drive as the default private export destination."
version: 1.0.0
author: Exocórtex
license: MIT
metadata:
  hermes:
    tags: [exocortex, presentations, html, markdown, marp, drive, visual, artifacts]
    category: exocortex
    related_skills: [exocortex-design-system, taste-skill, personal-artifact-workspace, google-workspace, exocortex-draft-first]
---

# Exocórtex Slides

Gera apresentações HTML premium a partir de fontes Markdown, Marp Markdown, PPTX ou brief de deck.

Esta skill é global. Não pertence ao microverso ensino. Ela se adapta ao microverso ativo via Acervo, contratos locais e Exocórtex Design System.

## Princípio

Markdown é fonte. HTML é export. PDF é distribuição. ZIP é pacote. Google Drive é o destino padrão de publicação privada. Deploy público é exceção e exige Draft-First.

Marp continua sendo linha de produção para slides rotineiros. Frontend Slides é renderer premium para apresentações que precisam de direção visual, narrativa e presença.

## Quando usar

Use quando o usuário pedir:

- apresentação visual premium;
- deck HTML a partir de `.md`;
- versão mais impactante de slides Marp;
- apresentação institucional, palestra, pitch, briefing, aula especial;
- export HTML/PDF/ZIP de um conteúdo Markdown;
- redesign de PPTX como apresentação web;
- transformar material textual em apresentação navegável no browser.

Não use como padrão para toda aula recorrente. Para produção didática seriada, prefira Marp, exceto quando o usuário pedir impacto visual ou entrega premium.

## Contrato de fonte

A fonte canônica deve ficar em Markdown sempre que possível:

```text
source/source.md       # conteúdo/narrativa canônica
source/brief.md        # intenção, público, duração, densidade, tom
source/slides.marp.md  # fonte Marp preservada, se existir
assets/                # imagens, logos, screenshots, dados
exports/deck.html      # export premium
exports/deck.pdf       # export estático
exports/deck.zip       # pacote de entrega
```

HTML gerado não substitui a fonte Markdown por padrão. Se o HTML for editado manualmente depois, registre isso no manifesto como divergência ou nova revisão.

## Dependências obrigatórias antes de executar

Carregue ou respeite:

- `exocortex-design-system` para resolver tokens visuais;
- `taste-skill` para validar visual;
- `personal-artifact-workspace` para pacote, manifesto, ZIP e Drive;
- `productivity/google-workspace` para upload privado ao Drive;
- `exocortex-draft-first` se houver compartilhamento, link público, deploy, mensagem ou documento colaborativo.

## Microverso adaptation

Antes de gerar previews ou deck final:

1. Resolver microverso ativo.
2. Ler `global/DESIGN.md`.
3. Ler `micro/{slug}/DESIGN.md` quando existir.
4. Ler contratos/persona/workflows locais quando relevantes.
5. Definir envelope visual:
   - `strict`: institucional, gabinete, documento oficial, risco reputacional.
   - `balanced`: padrão Exocórtex.
   - `expressive`: palestra, pitch, aula especial, narrativa visual.
   - `experimental`: estúdio-criativo ou exploração aprovada.
6. Gerar dentro do envelope. Criatividade amplia o sistema; não ignora o sistema.

### Heurísticas por microverso

```text
ensino:
  clareza didática, código legível, identidade IFSul contida, criatividade em aulas especiais.

gabinete:
  institucional, sóbrio, verde controlado, vermelho raro, sem motion ruidoso.

dev:
  arquitetura clara, diagramas, estética técnica quando útil, terminal/dark mode permitido.

estudio-criativo:
  direção de arte forte, tese visual explícita, maior liberdade, sem slop.
```

## Relação com Estúdio Criativo

Frontend Slides e Estúdio Criativo são pares.

- Estúdio Criativo ajuda com tese visual, linguagem, moodboard, direção de arte e exploração.
- Frontend Slides empacota a tese em apresentação navegável, HTML, PDF, ZIP e Drive.

Se a tarefa pede visual ousado, campanha, linguagem autoral, posterização, identidade ou exploração estética, consulte o contexto/skill do Estúdio Criativo antes do deck final.

Se o Estúdio Criativo precisar transformar uma direção visual em apresentação, ele deve chamar esta skill.

## Relação com Marp

Use Marp quando:

- a manutenção manual importa mais que direção visual;
- há muitos blocos de código;
- o material é aula recorrente;
- o PDF é a entrega principal;
- o usuário quer velocidade e previsibilidade.

Use Frontend Slides quando:

- a apresentação precisa causar impacto;
- a narrativa visual importa;
- o deck será usado em palestra, reunião ou evento;
- o usuário quer HTML premium;
- a estética precisa variar além do tema Marp.

Modo híbrido recomendado:

```text
source.md ou slides.marp.md
  -> brief.md
  -> previews/style-a.html, style-b.html, style-c.html
  -> exports/deck.html
  -> exports/deck.pdf
  -> exports/deck.zip
  -> upload privado no Google Drive, quando solicitado ou como export final padrão
```

## Workflow

### 1. Intake

Coletar ou inferir:

- microverso;
- propósito;
- público;
- duração ou número aproximado de slides;
- densidade: `speaker-led` ou `reading-first`;
- tom: institucional, didático, técnico, provocativo, criativo etc.;
- assets disponíveis;
- se a fonte é Markdown, Marp, PPTX ou brief livre.

Se a intenção estiver clara, não faça entrevista longa. Use defaults e assuma `balanced`.

### 2. Criar pacote de artefato

Usar `personal-artifact-workspace` como base:

```text
~/.hermes/acervo/_artifacts/{artifact_id}/
├── source/
├── assets/
├── previews/
├── exports/
└── manifest.json
```

Preservar fonte Markdown em `source/`.

### 3. Resolver Design System

Aplicar `exocortex-design-system`:

- global primeiro;
- override do microverso depois;
- validar/lint quando tokens forem criados ou alterados;
- nunca hardcodear estética IFSul fora dos tokens quando existir token canônico.

### 4. Gerar 3 previews

Usar a referência upstream em:

```text
references/upstream-frontend-slides/
```

Ler nesta ordem:

1. `STYLE_PRESETS.md`;
2. `bold-template-pack/selection-index.json`;
3. apenas os `preview.md` dos candidatos;
4. nunca ler todos os `design.md` antes da escolha.

Cada preview deve parecer um slide real do deck, não uma ficha diagnóstica. Não renderizar “Option A”, “template”, “preview”, nomes de arquivo ou metadados internos no slide.

### 5. Escolha de direção

Apresentar as três opções com nomes no texto da resposta, não dentro do slide.

Se o usuário escolher “misturar”, pedir só o ajuste necessário. Não reiniciar o processo.

### 6. Gerar deck final

Antes de gerar, ler:

```text
references/upstream-frontend-slides/html-template.md
references/upstream-frontend-slides/viewport-base.css
references/upstream-frontend-slides/animation-patterns.md
```

Se usuário escolheu um bold template, ler exatamente o `design.md` escolhido.

Requisitos:

- HTML autocontido;
- palco fixo 1920x1080;
- `.deck-stage` escalado para viewport;
- slides com classe `.slide`;
- navegação por teclado/toque;
- `prefers-reduced-motion`;
- sem overflow;
- sem texto pequeno demais;
- sem reflow mobile que destrói o 16:9;
- sem meta-labels visíveis.

### 7. Exportar PDF e ZIP

PDF:

```bash
bash scripts/export-pdf.sh exports/deck.html exports/deck.pdf
```

ZIP:

```bash
bash scripts/package-deck.sh \
  --source source/source.md \
  --html exports/deck.html \
  --pdf exports/deck.pdf \
  --out exports/deck.zip \
  --assets assets \
  --manifest manifest.json
```

### 8. Oferecer upload privado no Drive

Ao entregar um deck local (HTML/PDF/ZIP), pergunte ao usuário se quer subir os slides para o Google Drive privado dele, salvo quando ele já pediu upload explicitamente.

Formato recomendado da pergunta:

```text
Quer que eu suba estes slides para o seu Drive?
Destino sugerido: exocortex/{microverso}/{ano}/apresentacoes
Arquivos: HTML, PDF e ZIP completo.
```

Se o usuário responder positivamente (`sim`, `suba`, `pode subir`, `ok`, etc.), execute o upload privado via `personal-artifact-workspace` e `productivity/google-workspace`.

Se o usuário já pediu upload ou usou verbo de ação claro (`suba para o Drive`, `publique no meu Drive`, `manda para o Drive`), não pergunte de novo. Execute direto, pois upload privado para o Drive do próprio usuário conta como entrega pessoal do artefato solicitado.

#### Regras de path no Drive

Use sempre a estrutura padrão do Exocórtex. Nunca envie para a raiz do Drive.

Destino padrão quando faltar contexto:

```text
exocortex/inbox
```

Destinos recomendados para apresentações:

```text
exocortex/{microverso}/{ano}/apresentacoes
exocortex/ensino/{ano}/{disciplina}/slides-premium
exocortex/gabinete/{ano}/apresentacoes
exocortex/dev/{ano}/apresentacoes
exocortex/estudio-criativo/{ano}/decks
```

Regras:

- Resolver ou criar cada segmento da pasta (`exocortex` → microverso → ano → tipo) antes do upload.
- Registrar `drive_target.folder_path` e `folder_id` no `manifest.json`.
- Gravar `receipt.google_drive.json` com IDs, links, MIME, hash, tamanho e visibilidade.
- Subir preferencialmente HTML, PDF e ZIP; se houver restrição, subir ao menos PDF e ZIP.
- Manter os arquivos privados por padrão.
- Compartilhar, tornar público, enviar por email/mensagem ou criar link público exige Draft-First.

### 9. Deploy público

Vercel não é padrão. Criar conta Vercel é atrito para usuário comum.

Use Vercel só quando:

- o usuário pedir explicitamente URL pública;
- Drive privado não atender;
- houver aprovação inequívoca após DRAFT;
- o usuário aceitar dependência de conta externa.

## Scripts incluídos

Referência operacional adicional: `references/drive-first-export-policy.md` fixa Drive privado como caminho padrão e Vercel como exceção Draft-First.

```text
scripts/setup-frontend-slides.sh   # checa/instala dependências locais
scripts/extract-pptx.py            # extrai conteúdo de PPTX
scripts/export-pdf.sh              # exporta HTML para PDF via Playwright
scripts/package-deck.sh            # empacota fonte + exports + assets
```

Setup:

```bash
bash scripts/setup-frontend-slides.sh --check
bash scripts/setup-frontend-slides.sh --install-local
```

`--check` nunca instala nada.

## Upstream

A base upstream vendorizada é `zarazhangrui/frontend-slides`, licença MIT, versão analisada no commit `24e420e`.

Use os arquivos em `references/upstream-frontend-slides/` como referência operacional. Esta skill é o adapter Exocórtex; o upstream é insumo, não contrato final.

## Quality Gate

Antes de entregar:

- aplicar `taste-skill`;
- verificar contraste e hierarquia visual;
- verificar stage 16:9 em desktop e viewport estreita;
- verificar ausência de overflow e sobreposição;
- quando o público for leigo ou usuário potencial, trocar jargões internos/inglês por linguagem de produto compreensível; exemplo: skills → habilidades, tools → ferramentas, profiles → modos de trabalho, Draft-First → rascunho primeiro, Quality Gate → controle de qualidade;
- verificar que fonte Markdown foi preservada;
- revisar visualmente pelo menos a capa e um slide denso no browser, porque checks de DOM não capturam sensação de card grid genérico, hierarquia fraca ou controle de navegação poluindo a apresentação;
- deixar controles de navegação discretos no HTML e ocultos no print/PDF (`@media print`), para que a versão final não mostre chrome de edição;
- registrar hashes no manifesto quando publicar como artefato.

Referência prática: `references/session-2026-06-01-exocortex-saas-deck.md` documenta QA visual, fallback de PDF via Chrome headless e sequência de manifesto/ZIP usada num deck Exocórtex.SaaS.

## Pitfalls

1. Usar Frontend Slides como substituto universal de Marp. Não é.
2. Deixar HTML virar fonte canônica sem registrar decisão.
3. Publicar no Vercel por conveniência. Drive é padrão; deploy público é exceção.
4. Ignorar microverso e criar visual genérico.
5. Copiar todo `bold-template-pack` para o prompt. Leia índice, depois previews, depois um design escolhido.
6. Renderizar nomes internos no slide: “Option A”, “template”, “preview.md”, paths.
7. Usar verde IFSul saturado como fundo constante. Verde sustenta hierarquia; não precisa ocupar tudo.
8. Gerar PDF sem ZIP. Para artefato visual, ZIP preserva fonte e assets.
9. Deixar controles de navegação/editor muito visíveis no deck HTML. Eles ajudam a revisar, mas devem ficar discretos no browser e sumir no print/PDF.
10. Confiar apenas em `scrollWidth/scrollHeight`. Use esse check para overflow, mas faça inspeção visual em slides densos; matrizes de cards podem estar tecnicamente corretas e ainda parecer genéricas.
11. Trocar o renderer sem autorização e cair em `claude-design` por hábito. Para apresentações no Exocórtex, a rota padrão é `exocortex-slides` + Estúdio Criativo quando o pedido exigir direção visual forte.
12. Entregar versão antiga do deck por reutilizar arquivo local sem reconciliação de contexto. Sempre reidratar conteúdo com os dados mais atuais do evento antes da renderização final.

## Verification Checklist

- [ ] Fonte Markdown preservada em `source/`.
- [ ] Microverso resolvido.
- [ ] Design System global + override avaliados.
- [ ] 3 previews gerados antes do deck final, salvo se usuário dispensar explicitamente.
- [ ] HTML usa palco 1920x1080 e `.slide`.
- [ ] PDF exportado via Playwright quando solicitado ou como entrega final.
- [ ] ZIP criado para entrega de deck.
- [ ] Usuário recebeu a opção de subir HTML/PDF/ZIP para o Drive privado, salvo quando já pediu upload explicitamente.
- [ ] Se houver upload, path do Drive segue `exocortex/{microverso}/{ano}/apresentacoes` ou fallback `exocortex/inbox`, nunca raiz.
- [ ] Se houver upload, `manifest.json` e `receipt.google_drive.json` registram folder_id, links, hashes, MIME, tamanho e visibilidade privada.
- [ ] Nenhum deploy público sem aprovação.
- [ ] Estúdio Criativo consultado quando o pedido exigir direção visual forte.
