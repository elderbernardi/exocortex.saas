# Workflow para rascunho de versão candidata de UI

Use quando o executivo já escolheu uma direção visual e pede “rascunho da candidata”, “versão candidata” ou uma composição híbrida. Neste estágio, não gere outra rodada de variantes: consolide a direção escolhida em um único artefato comparável e interativo.

## 0. Reconciliar com o baseline de produção

**Este passo é obrigatório e precede qualquer geração de mockup.** Não pule para o design antes de ler o código real.

1. Leia o arquivo fonte da tela atual no repositório do produto (`.vue`, `.tsx`, `.jsx`, `.html`). Identifique cada seção, componente, elemento de dados e interação.
2. Leia a especificação funcional (SPEC, RFC, doc de produto) que rege a remodelagem.
3. Recupere artefatos de design exploration anteriores (Stitch, Figma, mockups locais) se existirem.
4. Mapeie: o que a SPEC manda **preservar**, o que manda **remover**, e o que manda **adicionar**.
5. Classifique a operação: é **enhance** (adiciona/remove seções preservando a estrutura) ou **reconstrução** (a SPEC autoriza partir do zero)? A menos que a SPEC diga explicitamente "reconstruir", trate como enhance.
6. Liste cada elemento do baseline que será preservado, removido ou modificado. Este mapa é o contrato visual; se algo sumir na entrega, a culpa é de quem não mapeou.

## 2. Converter direção em arquitetura candidata

- Preserve o primeiro nível de leitura na visão principal.
- Mova listas extensas e evidências para áreas de profundidade.
- Para briefings e cockpits, uma divisão útil é:
  - **Resumo:** risco, KPIs, tendência, orientação e próxima ação;
  - **Comercial:** oferta, ranking, oportunidades e GAPs;
  - **Contexto:** anotações, notícias, fontes e atualização.
- Não invente dados para preencher a arquitetura. Sínteses derivadas devem ser identificáveis a partir dos dados existentes.

## 3. Produzir mockup local antes de tocar o produto

Crie um HTML autocontido fora do código de produção:

- CSS inline e tokens concentrados em `:root`;
- zero hex hardcoded fora de `:root`;
- viewport mobile de referência explícita;
- navegação entre estados ou abas;
- pelo menos uma transição significativa;
- CTA com feedback visível;
- sem alterar o repositório do produto até aprovação.

Teste todas as superfícies, não apenas o estado inicial:

1. Estado principal.
2. Cada aba ou segmento.
3. Accordions/disclosures.
4. CTA e feedback.
5. Navegação persistente.

## 4. Separar modo interativo de modo de captura

Elementos `position: fixed` ficam corretos no uso, mas podem aparecer no meio de screenshots full-page e ocultar conteúdo. Mantenha dois modos no mesmo HTML:

```css
.capture .phone { padding-bottom: 0; }
.capture .fixed-actions {
  position: static;
  transform: none;
  width: 100%;
}
.capture .bottom-nav {
  position: static;
  transform: none;
  width: 100%;
}
.capture .toast { display: none; }
```

```js
if (new URLSearchParams(location.search).has('capture')) {
  document.body.classList.add('capture');
}
```

- Uso interativo: `index.html`
- Screenshot de apresentação: `index.html?capture=1`

Antes de capturar, meça `document.documentElement.scrollHeight` no modo `capture` e renderize na largura-alvo.

## 5. Verificação

- Abra o HTML no navegador e confirme a árvore de acessibilidade.
- Clique em todas as abas e controles.
- Confirme via DOM o estado de componentes que snapshots textuais possam omitir.
- Renderize a screenshot final com navegador real.
- Rode auditoria de tokens:

```python
import re
style = html.split('<style>', 1)[1].split('</style>', 1)[0]
root = style.split(':root', 1)[1].split('}', 1)[0]
outside = style.replace(root, '', 1)
assert not re.findall(r'#[0-9a-fA-F]{3,8}\b', outside)
```

- Aplique gate visual ao PNG final: sem sobreposição, texto legível, CTA e navegação no fim no modo de captura.

## Entrega

Entregue:

1. Screenshot da candidata no estado principal.
2. HTML interativo.
3. Mapa curto do que permanece em cada aba/área.
4. Declaração explícita de que o produto não foi alterado, quando o artefato for apenas exploratório.
5. Quais decisões ainda dependem de aprovação.

## Pitfalls

- **Construir do zero quando a SPEC pede enhance.** Se a especificação diz "remodelar abaixo do ponto X" ou lista explicitamente o que preservar, a operação é enhance — não reconstrução. Construir do zero descarta elementos que o executivo espera ver (barras de faturamento, badges, datas, recomendações) e força retrabalho. Sempre execute o passo 0 (reconciliar com o baseline) antes de gerar o primeiro mockup. Se o executivo disser "faltam informações", "perdeu o legado" ou "não está de acordo", o erro é ter pulado o baseline — volte ao passo 0 e reconcilie.
- **Ignorar artefatos de design exploration anteriores.** Stitch, Figma ou mockups locais que o executivo gerou ou aprovou contêm conceitos visuais que ele espera ver incorporados. Recupere-os no passo 0.3 e referencie-os no mapa de preservação/adição.
- **Gerar novas variantes após a escolha:** dilui a decisão; consolide uma candidata.
- **Alterar o produto para apresentar um rascunho:** use mockup local descartável.
- **Screenshot full-page com rodapé fixo:** cria falsa sobreposição; use modo `capture`.
- **Validar só o Resumo:** abas secundárias podem estar vazias ou quebradas.
- **Inventar conteúdo para preencher cards:** preserve os dados da referência.
- **Confundir mockup local com estado canônico do gerador ou do produto:** declare a origem do artefato.
