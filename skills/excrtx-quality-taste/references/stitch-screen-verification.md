# Verificação de telas geradas por Stitch

Use este procedimento para brainstorms e propostas de UI geradas em serviços externos como Stitch.

## Regra central

Nunca trate a resposta textual do gerador como prova de que a tela final mudou. Verifique três superfícies separadamente:

1. **Estado canônico do projeto** — busque novamente a tela pelo ID.
2. **Export HTML** — baixe o HTML mais recente e inspecione os elementos críticos.
3. **Renderização real** — abra ou renderize o HTML na viewport-alvo e faça screenshot.

Thumbnails e URLs de screenshot podem continuar apontando para uma imagem anterior após uma edição de DOM. O evento de edição prova a operação solicitada, mas não prova que o thumbnail ou export refletiu a mudança.

## Fluxo recomendado

1. Crie ou aplique o design system antes de gerar as telas.
2. Gere conceitos independentes em paralelo, cada um com arquitetura funcional distinta.
3. Faça gate visual dos screenshots iniciais:
   - hierarquia e legibilidade;
   - conteúdo obrigatório;
   - navegação e CTA;
   - ausência de áreas vazias;
   - aderência a tokens e identidade;
   - distinções semânticas exigidas pelo domínio.
4. Se uma tela vier vazia ou incompleta, edite a tela com uma instrução de correção explícita. Não aceite o resumo textual do gerador como validação.
5. Busque a tela novamente e baixe o HTML exportado.
6. Inspecione strings e estrutura críticas no HTML: itens da navegação, labels de métricas, classes do CTA, nomes das seções e quantidade de blocos.
7. Renderize o HTML em navegador real na viewport-alvo. Quando não houver driver disponível, Chromium headless é suficiente:

```bash
chromium --headless=new --no-sandbox --disable-gpu --hide-scrollbars \
  --allow-file-access-from-files --virtual-time-budget=8000 \
  --window-size=390,1650 --screenshot=/tmp/screen.png \
  file:///caminho/tela.html
```

8. Aplique o gate visual novamente ao PNG renderizado.
9. Entregue o screenshot verificado e identifique claramente se o arquivo é:
   - thumbnail original do gerador;
   - export renderizado sem alteração;
   - export normalizado localmente para comparação.

## Pitfalls

- **Confirmar pela mensagem do Stitch:** “ajustes concluídos” não substitui inspeção do HTML ou screenshot.
- **Entregar thumbnail antigo:** após edição de DOM, o screenshot associado ao screen ID pode permanecer inalterado.
- **Aceitar copy drift:** geradores podem trocar produtos, números, labels ou exemplos mesmo quando a estrutura está correta. Compare os termos críticos com a especificação.
- **Confundir aparência com cobertura funcional:** uma tela visualmente boa pode omitir etapas, fontes, labels ou navegação.
- **Modificar silenciosamente o export:** se houver normalização local para facilitar comparação, declare isso na entrega; não apresente o PNG como screenshot canônico do serviço.

## Gate mínimo

- [ ] Design system aplicado antes da geração
- [ ] Screenshots iniciais auditados visualmente
- [ ] Estado da tela consultado novamente após edits
- [ ] HTML exportado inspecionado
- [ ] Screenshot renderizado na viewport-alvo
- [ ] Navegação, CTA e labels críticos conferidos
- [ ] Copy drift corrigido ou explicitado
- [ ] Origem do screenshot final declarada
