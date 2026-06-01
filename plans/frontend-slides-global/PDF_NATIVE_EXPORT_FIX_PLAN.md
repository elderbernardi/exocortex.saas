# Correção do PDF nativo dos Frontend Slides

> Para Hermes: implementar com disciplina de debug sistemático. Não aplicar correção cosmética antes de trocar o pipeline de exportação.

## Objetivo

Gerar PDF de apresentação em formato slide deck real: uma página 16:9 por slide, sem cabeçalho/rodapé de impressão, sem página carta/A4, sem screenshot raster como fonte principal, pronto para abrir em modo apresentação.

## Diagnóstico

O PDF atual em `~/.hermes/acervo/_artifacts/art_20260601_101653_exocortex_saas_slides/exports/exocortex-saas-deck.pdf` está errado por dois motivos distintos.

1. Export usado no artefato atual caiu no fallback errado.

O arquivo foi gerado por Chrome headless como impressão de página comum. Evidência:

```text
Page size: 612 x 792 pts (letter)
Pages: 12
Creator: HeadlessChrome
```

O render visual confirma:

- página em orientação retrato;
- slide 16:9 encaixado no topo;
- área branca sobrando embaixo;
- cabeçalho com data/título;
- rodapé com URL e número de página.

Isso não é PDF de slides. É impressão de página web.

2. O script atual da skill também não resolve o requisito de PDF nativo.

`export-pdf.sh` captura cada slide como PNG 1920x1080 e depois monta um PDF com imagens. Mesmo quando a proporção sai correta, o resultado continua sendo uma fotografia dos slides:

- texto não fica vetorial/selectable;
- qualidade depende de DPI;
- arquivo perde semântica;
- zoom revela rasterização;
- não é o equivalente a um deck PDF nativo.

A raiz arquitetural é tratar PDF como composição de screenshots. O correto é tratar PDF como renderização paginada do próprio DOM/CSS.

## Hipótese de correção

Substituir o pipeline principal por exportação nativa via Playwright/Chromium PDF:

1. abrir o HTML em servidor local;
2. forçar modo `print`;
3. injetar/validar CSS de print com `@page` 16:9;
4. deixar todos os `.slide` visíveis, um por página;
5. chamar `page.pdf()` com tamanho 16:9, margens zero e `printBackground: true`;
6. validar o PDF gerado com `pdfinfo` e inspeção visual.

Screenshot deve virar fallback explícito, nunca default.

## Critérios de aceite

Um PDF válido precisa passar por estes checks:

```text
pdfinfo deck.pdf
```

Esperado:

- `Pages` = número de slides;
- `Page size` compatível com 16:9, por exemplo `960 x 540 pts`, `1280 x 720 pts` ou equivalente;
- sem `letter`, `A4` ou retrato;
- sem headers/footers de browser;
- render de página ocupa o frame inteiro;
- texto continua vetorial/selectable quando possível.

Validação visual mínima:

```bash
pdftoppm -f 1 -l 3 -png -r 96 deck.pdf /tmp/deck-page
```

Cada PNG deve ter proporção 16:9 e não pode conter bordas brancas, URL, data ou número de página externo.

## Arquivos a modificar

- `~/.hermes/skills/exocortex/exocortex-frontend-slides/scripts/export-pdf.sh`
- `/home/elder/projetos/pessoal/exocortex.saas/.hermes/skills/exocortex/exocortex-frontend-slides/scripts/export-pdf.sh`
- `/home/elder/projetos/pessoal/exocortex.saas/plans/pdd_v2/artifacts/skills/exocortex-frontend-slides/scripts/export-pdf.sh`
- `~/.hermes/skills/exocortex/exocortex-frontend-slides/SKILL.md`
- `/home/elder/projetos/pessoal/exocortex.saas/.hermes/skills/exocortex/exocortex-frontend-slides/SKILL.md`
- `/home/elder/projetos/pessoal/exocortex.saas/plans/pdd_v2/artifacts/skills/exocortex-frontend-slides/SKILL.md`
- `plans/frontend-slides-global/PLAN.md`

## Plano de implementação

### Tarefa 1 — Criar fixture mínima de deck

Objetivo: reproduzir o bug com um HTML pequeno e determinístico.

Criar:

```text
tests/fixtures/frontend-slides/minimal-deck.html
```

Conteúdo esperado:

- 3 slides `.slide`;
- palco 1920x1080;
- texto grande;
- fundo escuro;
- CSS de tela parecido com o deck real;
- CSS de print com uma página por slide.

### Tarefa 2 — Criar teste de regressão do export PDF

Objetivo: impedir retorno para Letter/A4/retrato/screenshot acidental.

Criar:

```text
tests/frontend-slides/test_pdf_export.sh
```

O teste deve:

1. rodar `export-pdf.sh` sobre a fixture;
2. chamar `pdfinfo`;
3. falhar se `Page size` contiver `letter` ou `A4`;
4. falhar se largura <= altura;
5. falhar se `Pages` != 3;
6. renderizar primeira página com `pdftoppm` e validar proporção aproximada 16:9.

### Tarefa 3 — Reescrever `export-pdf.sh` para modo nativo

Objetivo: tornar PDF nativo o comportamento padrão.

Mudanças:

- manter servidor local para fontes/assets;
- remover montagem de PNGs do caminho principal;
- criar flag explícita `--raster-fallback` para o comportamento antigo;
- adicionar flags:
  - `--size 16:9` default;
  - `--width 13.333in --height 7.5in` ou equivalente;
  - `--wait-ms 1000` para fontes/animações;
- no script Playwright:
  - `await page.emulateMedia({ media: 'print' })`;
  - `await page.addStyleTag({ content: '...' })` com CSS de print defensivo;
  - `await page.pdf({ path, width: '13.333in', height: '7.5in', printBackground: true, preferCSSPageSize: true, margin: {top:0,right:0,bottom:0,left:0}, displayHeaderFooter: false })`.

CSS defensivo mínimo a injetar:

```css
@page { size: 13.333in 7.5in; margin: 0; }
html, body {
  margin: 0 !important;
  padding: 0 !important;
  width: 1920px !important;
  background: #000 !important;
  -webkit-print-color-adjust: exact !important;
  print-color-adjust: exact !important;
}
.deck-viewport,
.deck-stage {
  position: static !important;
  width: 1920px !important;
  height: auto !important;
  transform: none !important;
  overflow: visible !important;
  background: transparent !important;
}
.slide {
  position: relative !important;
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
  width: 1920px !important;
  height: 1080px !important;
  overflow: hidden !important;
  break-after: page !important;
  page-break-after: always !important;
  -webkit-print-color-adjust: exact !important;
  print-color-adjust: exact !important;
}
.slide:last-child {
  break-after: auto !important;
  page-break-after: auto !important;
}
.deck-controls,
.edit-hotzone,
.edit-toggle {
  display: none !important;
}
```

### Tarefa 4 — Adicionar verificador pós-exportação

Objetivo: falhar rápido quando o PDF sair como impressão de página.

No final de `export-pdf.sh`, rodar `pdfinfo` quando disponível e validar:

- número de páginas > 0;
- largura > altura;
- proporção entre 1.70 e 1.82;
- página não é `letter`/`A4`;
- arquivo existe e não está vazio.

Se `pdfinfo` não existir, emitir warning, não falhar.

### Tarefa 5 — Atualizar documentação da skill

Objetivo: corrigir o contrato operacional.

Trocar a definição atual de PDF:

- antes: screenshot de cada slide + montagem em PDF;
- depois: PDF nativo via print CSS/Playwright;
- raster somente fallback explícito.

Adicionar pitfall:

> PDF de slides não pode ser impressão de página web. Qualquer header/footer, página Letter/A4 ou margem branca invalida a entrega.

### Tarefa 6 — Regenerar o deck Exocórtex.SaaS

Objetivo: reparar o artefato já entregue.

Rodar novo export sobre:

```text
/home/elder/.hermes/acervo/_artifacts/art_20260601_101653_exocortex_saas_slides/exports/exocortex-saas-deck.html
```

Substituir:

```text
/home/elder/.hermes/acervo/_artifacts/art_20260601_101653_exocortex_saas_slides/exports/exocortex-saas-deck.pdf
```

Depois:

- atualizar hashes no `manifest.json`;
- recriar ZIP;
- se o usuário aprovar, atualizar os arquivos no Drive.

### Tarefa 7 — QA visual final

Objetivo: confirmar que o deck está pronto para apresentação.

Executar:

```bash
pdfinfo exports/exocortex-saas-deck.pdf
pdftoppm -f 1 -l 3 -png -r 96 exports/exocortex-saas-deck.pdf /tmp/exocortex-fixed/page
```

Validar com visão:

- capa ocupa a página toda;
- não há cabeçalho/rodapé;
- não há página branca;
- slides densos continuam legíveis;
- proporção 16:9 preservada.

## Ordem de execução recomendada

1. teste reproduzindo falha;
2. novo exportador nativo;
3. teste passando;
4. documentação/skill;
5. regeneração do artefato atual;
6. QA visual;
7. atualização opcional no Drive mediante aprovação.

## Não fazer

- Não resolver com `--landscape` apenas. Isso troca a orientação, mas não corrige rasterização nem garante página 16:9.
- Não aumentar DPI de screenshots. Isso melhora a fotografia, mas continua fotografia.
- Não usar `google-chrome --print-to-pdf` direto sem `@page`, sem `displayHeaderFooter:false` e sem validação.
- Não aceitar PDF Letter/A4 para deck de apresentação.
