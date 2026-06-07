# DRAFT — atualização da issue #35

Issue: #35 — Draft-First não bloqueia envio externo em conversa real via subinstância

## Atualização proposta

A investigação mostrou que o problema principal não está no dogfood. O dogfood apenas expôs a lacuna. A correção correta está no harness do Exocórtex.

### Novo enquadramento

O harness precisava distinguir três categorias que antes estavam colapsadas:

1. **Self-delivery operacional**
   - entrega ao próprio executivo
   - no home channel dele
   - como resposta do sistema, recibo operacional ou teste técnico explícito

2. **Comunicação em nome do executivo**
   - mensagem, email, comentário, post ou posicionamento para terceiros

3. **Publicação/compartilhamento externo**
   - grupo, canal compartilhado, rede social, calendário, documento compartilhado, push, deploy ou equivalente

### Decisão aplicada no harness

- self-delivery operacional pode executar sem DRAFT quando o destinatário é inequivocamente o próprio executivo, o canal é o home channel dele e o conteúdo não representa fala do executivo para terceiros
- comunicação para terceiros continua em Draft-First obrigatório
- publicação/compartilhamento externo continua em Draft-First obrigatório
- destinatário ambíguo ou canal compartilhado deve ser tratado como comunicação externa

### Arquivos alterados

- `SOUL_SEED.md`
- `skills/excrtx-govern-draftfirst/SKILL.md`
- `skills/excrtx-govern-tools/SKILL.md`

### Testes adicionados

- `tests/test_harness_draftfirst_policy.py`

### Critérios de aceite revisados

- [ ] O harness distingue self-delivery operacional de comunicação para terceiros
- [ ] Self-delivery ao próprio executivo no home channel pode ocorrer sem DRAFT
- [ ] Comunicação para terceiros continua exigindo DRAFT e aprovação pós-DRAFT
- [ ] Canal compartilhado ou destinatário ambíguo continua caindo em Draft-First
- [ ] A política está refletida na Constituição (`SOUL_SEED.md`) e nas skills de governança
- [ ] Há teste automatizado cobrindo a taxonomia nova

## Comentário sugerido na issue

> Atualização de escopo: a correção correta está no harness do Exocórtex, não no dogfood. O problema era de modelagem da política de comunicação. O harness agora distingue self-delivery operacional, comunicação em nome do executivo e publicação/compartilhamento externo. Self-delivery ao próprio executivo no home channel pode executar sem DRAFT; comunicação para terceiros continua exigindo Draft-First com aprovação pós-DRAFT; destino ambíguo ou canal compartilhado continua tratado como comunicação externa. Também adicionei teste automatizado cobrindo essa taxonomia.
