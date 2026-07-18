# Revisão de landing de campanha pública

Use este roteiro para protótipos de vestibular, seleção pública, edital, campanha institucional ou serviço sujeito a aprovação.

## 1. Preflight de conteúdo

- Identifique a fonte canônica de cada data, curso, contato e CTA.
- Separe fatos publicáveis de campos dependentes de edital ou aprovação.
- Não consuma uma base marcada como `REVIEW`, `review_required` ou equivalente sem autorização explícita.
- Use apenas informação aprovada para destravar o protótipo; documente o que ficou de fora.
- Não transforme slogan de trabalho, tema criativo ou placeholder em texto público.

## 2. Assets e responsividade

- Registre origem, dimensão e hash dos assets copiados para o artefato.
- Preserve os originais como fonte de verdade.
- Desktop: exiba a peça oficial em sua proporção, sem `object-fit: cover` quando isso cortar lockup, assinatura ou pessoas.
- Mobile: prefira uma variante oficial mais vertical. Use `<picture>` para trocar o asset por breakpoint.
- Se nenhuma variante oficial funcionar, mantenha a arte inteira com `contain`; não redesenhe o lockup.

## 3. Estado DRAFT

Enquanto houver dados ou aprovações pendentes:

- inclua aviso visível de revisão interna;
- adicione `<meta name="robots" content="noindex, nofollow">`;
- não exponha placeholders como `[LINK_EDITAL]`;
- aponte para o portal oficial geral quando o link direto ainda não existir;
- mantenha no README a lista de bloqueios para publicação.

## 4. Motion resiliente

Reveal por viewport não pode tornar conteúdo dependente da animação.

Padrão seguro:

1. conteúdo aparece normalmente sem JavaScript;
2. a classe de JS ativa o estado inicial do reveal;
3. `IntersectionObserver` revela na rolagem;
4. um timeout curto revela todos os itens e desconecta o observer;
5. `prefers-reduced-motion` mantém tudo visível.

Isso evita páginas vazias em screenshots full-page, automações, navegadores degradados ou exceções posteriores no script.

## 5. Matriz mínima de teste

### Desktop

- viewport explícito, por exemplo 1440 × 1000;
- título em até duas linhas;
- CTA primário, prazo e fonte oficial na primeira dobra;
- asset sem recorte;
- navegação completa e foco visível.

### Mobile

- viewport explícito, por exemplo 390 × 844;
- título em até três linhas;
- aviso DRAFT legível sem dominar a página;
- menu com alvo mínimo de 44 px;
- CTAs empilhados sem overflow;
- asset mobile inteiro;
- textos regulatórios sem truncamento.

### Interações

- abrir e fechar menu;
- aplicar todos os filtros;
- acionar o caminho principal e conferir scroll/foco;
- abrir FAQ;
- navegar por teclado;
- confirmar `aria-pressed`, `aria-expanded` e região `aria-live`;
- revisar console e erros JavaScript.

## 6. Evidência e interpretação

Capture:

- primeira dobra desktop;
- primeira dobra mobile;
- cada seção após rolagem real;
- estados filtrados ou expandidos relevantes.

Não use screenshot full-page isolado como prova de composição: elementos `sticky` podem aparecer deslocados ou repetidos, e reveals ainda não acionados podem produzir áreas vazias. A prova principal deve ser o viewport no estado que o usuário realmente vê.

## 7. Gate final

A landing só pode sair de DRAFT quando:

- fatos e links foram revistos;
- edital e retificações foram incorporados;
- marca, neutralidade, direitos e acessibilidade passaram;
- jornada completa foi testada;
- aviso de protótipo e `noindex` foram removidos por decisão explícita;
- a versão publicada foi aberta e verificada, não apenas o arquivo local.
