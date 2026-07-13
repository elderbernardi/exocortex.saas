---
title: "LotoState by ALEQIA — Guardrails de Produto"
type: knowledge
description: "Contratos operacionais e de exposição pública derivados do PRD do LotoState"
class: perene
timestamp: "2026-07-05"
created_at: "2026-07-05T19:56:31Z"
created: "2026-07-05"
updated: "2026-07-05"
nature: contracts
excrtx_type: rule
tags: [projeto-d, lotostate, aleqia, guardrails, monetizacao, whatsapp, monitor]
confidence: high
sources:
  - /home/elder/.hermes/cache/documents/doc_c15191a2021b_PRD_LotoState_by_ALEQIA.md
---

# LotoState by ALEQIA — Guardrails de Produto

Regras operacionais derivadas do PRD. Este arquivo captura contratos que devem orientar UX, API pública, monetização e comunicação do produto.

## Comunicação pública do modelo

### Regra 1 — sem promessa de prêmio
**QUANDO** o produto descrever sinais, scores, sugestões ou tendências  
**ENTÃO** a comunicação deve apresentar análise estatística e apoio à decisão, nunca promessa de prêmio, ganho ou previsão certeira  
**EXCETO** nenhuma exceção operacional prevista no PRD

### Regra 2 — sem exposição de fórmula
**QUANDO** o frontend, materiais públicos ou APIs de cliente exibirem indicadores ALEQIA D  
**ENTÃO** mostrar apenas nomes públicos, scores, estados e descrições interpretáveis  
**EXCETO** superfícies internas explicitamente segregadas para auditoria técnica

### Regra 3 — linguagem proibida
**QUANDO** houver copy pública, onboarding, marketing ou suporte automatizado  
**ENTÃO** bloquear expressões como “garantimos acerto”, “previsão certeira” e equivalentes  
**EXCETO** citações literais em material crítico que esteja explicitamente marcando o termo como proibido

## Bloqueio por plano e entitlement

### Regra 4 — backend é autoridade
**QUANDO** o cliente solicitar dezenas, scores ou estados do monitor  
**ENTÃO** o backend define visibilidade, plano e entitlements ativos  
**EXCETO** nenhuma regra sensível deve ser resolvida definitivamente no frontend

### Regra 5 — dezena bloqueada não vaza
**QUANDO** uma dezena estiver bloqueada por plano  
**ENTÃO** o payload não pode conter número, score, histórico, sparkline ou sinal inferível  
**EXCETO** nenhum

### Regra 6 — tile bloqueado é genérico
**QUANDO** a UI renderizar uma dezena bloqueada  
**ENTÃO** exibir apenas estado genérico, mensagem comercial e CTA de desbloqueio  
**EXCETO** nenhuma revelação parcial do conteúdo bloqueado

### Regra 7 — compra avulsa não altera assinatura
**QUANDO** o usuário comprar dezena extra ou painel temporário  
**ENTÃO** criar entitlement temporário independente do plano recorrente  
**EXCETO** promoções administrativas explícitas controladas no backend

## Operação de apostas e resultado

### Regra 8 — sem aposta oficial implícita
**QUANDO** o app gerar, salvar, compartilhar ou conferir jogos  
**ENTÃO** o produto deve deixar claro que não enviou aposta oficial à Caixa no MVP  
**EXCETO** se houver integração formal posterior e fluxo explícito confirmado

### Regra 9 — geração respeita permissão
**QUANDO** o gerador de jogos montar sugestões  
**ENTÃO** não pode usar dezenas bloqueadas sem entitlement válido  
**EXCETO** nenhuma

## Dados oficiais e rastreabilidade

### Regra 10 — fonte e status visíveis
**QUANDO** o produto exibir concurso, prêmio ou resultado  
**ENTÃO** preservar fonte lógica, timestamp e status `official`, `cached`, `pending` ou `error`  
**EXCETO** nenhuma

## WhatsApp e consentimento

### Regra 11 — opt-in obrigatório
**QUANDO** o sistema enviar WhatsApp transacional, promocional ou de suporte automatizado  
**ENTÃO** deve existir consentimento ativo com timestamp, origem e versão do texto  
**EXCETO** nenhuma

### Regra 12 — revogação respeitada
**QUANDO** o usuário revogar consentimento  
**ENTÃO** o sistema interrompe novos envios dependentes desse opt-in  
**EXCETO** obrigações legais ou operacionais que não dependam de WhatsApp

## Dados sensíveis

### Regra 13 — sem CPF puro
**QUANDO** houver necessidade de CPF por checkout, idade ou compliance  
**ENTÃO** não armazenar CPF em texto puro no domínio principal  
**EXCETO** nenhum caso previsto no PRD autoriza texto puro
