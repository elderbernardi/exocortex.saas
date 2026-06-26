# Prompt — próxima sessão / Fase 5

Você está no repo `/home/elder/projetos/projetob/exocortex.saas` e deve continuar a execução da **META #97** a partir da **Fase 5**.

## Objetivo desta sessão
Executar a **Fase 5 — DocBrain Pipeline** com prioridade em:
1. **#114** — health check e reparo do DocBrain
2. **#115** — adaptador `excrtx-adapter-docbrain-acervo` (somente se #114 ficar funcional ou se der para deixar scaffold/testes/diagnóstico consistente sem inventar funcionamento)

## Contexto já resolvido
- Fase 4 foi concluída e publicada.
- Issues fechadas: **#111, #112, #113**.
- META **#97** foi atualizada e permanece **aberta**.
- Commit remoto atual de referência no repo `exocortex.saas`: `5825b61`.

## Fontes de verdade a carregar antes de agir
1. `docs/plans/2026-06-25_inteligencia-competitiva-fase4-10.md`
   - ler especialmente a seção **Fase 5**
2. `docs/plans/prompt-fase4-start.md`
   - usar como contexto operacional e convenções
3. issue **#114**
4. issue **#115**
5. se necessário, contrato mencionado no plano:
   - `.harness/contracts/exocortex-to-docbrain.md`

## Restrições obrigatórias
- **Não inventar sucesso** do DocBrain. Validar com output real.
- **Não executar `npm install`, `pip install` ou equivalente sem aprovação explícita do executivo.**
- Se faltar dependência, diagnosticar com precisão, registrar bloqueio e preparar DRAFT.
- `DocBrain` é privado/local em `/home/elder/projetos/projetob/docbrain/` — **não citar em docs públicos**.
- Toda ação externa exige DRAFT antes de publicar.
- Se editar skill, rodar `python3 scripts/skill_judge.py --skill <nome> --d1-only`.
- Não encerrar a sessão com plano genérico; entregar resultado verificável, ou bloqueio diagnosticado com evidência real.

## Sequência de execução esperada

### Etapa 1 — inspeção inicial
- verificar estado do repo `exocortex.saas`
- verificar estado do repo `docbrain`
- reler a Fase 5 do plano
- abrir #114 e #115
- identificar se existe drift de path/config ligado à issue #11

### Etapa 2 — Fase 5a / #114
Rodar primeiro o health check do DocBrain:

```bash
cd /home/elder/projetos/projetob/docbrain
npm run --silent cli -- api health --output json
```

Esperado: payload JSON de health com `ok: true`.

Se falhar, diagnosticar em ordem:
1. `node --version`
2. existência de build/artefatos esperados
3. variáveis/chaves necessárias no `.env` do DocBrain
4. Python e dependências Python exigidas pelo DocBrain
5. drift entre paths reais e paths esperados na skill/docs/contrato

**Sem instalar nada sem autorização.**

Se o health check ficar funcional, executar um smoke test mínimo real de parse em fixture/documento apropriado, se existir e for seguro.

### Etapa 3 — Fase 5b / #115
Só avançar para implementação do adaptador se houver base real suficiente.

Objetivo:
- criar ou completar `skills/excrtx-adapter-docbrain-acervo/`
- criar script de orquestração para receber arquivo, chamar DocBrain, transformar saída em markdown estruturado e preparar promoção ao Acervo
- respeitar o contrato do Acervo e provenance no frontmatter

Antes de escrever código:
- localizar o contrato `.harness/contracts/exocortex-to-docbrain.md`
- inspecionar estrutura do Acervo e convenções mínimas de escrita
- definir o menor caminho funcional e testável

Validação mínima esperada para #115, se implementado:
- teste automatizado com fixture
- prova de que o adaptador chama ou consegue chamar o DocBrain com interface correta
- output local verificável

## Entregáveis esperados no fim da sessão
1. diagnóstico real do **#114** com comandos e outputs
2. reparo aplicado **ou** bloqueio preciso com causa raiz
3. se possível, avanço real do **#115** com testes
4. atualização do plano local se houver drift entre documento e estado real
5. **DRAFTs locais** para comentário de issue:
   - #114
   - #115 (se houver avanço)
6. resumo final respondendo claramente:
   - DocBrain está funcional neste runtime?
   - O que falta exatamente para fechar #114?
   - Dá para iniciar/fechar #115 agora ou não?

## Critério de sucesso desta sessão
- sucesso principal: `#114` diagnosticada com evidência real e, idealmente, resolvida
- sucesso secundário: `#115` iniciada com base técnica correta, sem teatro

## Tom de execução
Seja cirúrgico. Corrija drift documental se encontrar. Não trate hipótese como fato. Se algo falhar, mostre o comando, o erro e a implicação.
