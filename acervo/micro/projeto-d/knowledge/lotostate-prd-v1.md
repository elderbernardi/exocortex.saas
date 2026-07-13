---
title: "LotoState by ALEQIA — PRD v1"
type: knowledge
description: "Síntese canônica do PRD do LotoState by ALEQIA no contexto do Projeto D"
class: volátil
timestamp: "2026-07-05"
created_at: "2026-07-05T19:56:31Z"
created: "2026-07-05"
updated: "2026-07-05"
nature: knowledge
excrtx_type: fact
tags: [projeto-d, lotostate, aleqia, prd, lotofacil, mvp, produto]
confidence: high
sources:
  - /home/elder/.hermes/cache/documents/doc_c15191a2021b_PRD_LotoState_by_ALEQIA.md
---

# LotoState by ALEQIA — PRD v1

Documento curado a partir do PRD enviado em 2026-07-05. Este arquivo concentra a visão de produto. Modelagem técnica detalhada, guardrails operacionais e fluxo agentico foram separados em páginas próprias.

## Produto

- **Nome:** LotoState by ALEQIA
- **Contexto matemático:** Projeto D
- **Lançamento inicial:** Lotofácil
- **Ambição de plataforma:** multi-loteria
- **Superfície principal:** Monitor ALEQIA D
- **Promessa pública:** análise estatística, montagem, acompanhamento e gestão de apostas sem promessa de prêmio ou previsão determinística

## Tese de produto

O produto trata dezenas lotéricas como objetos analíticos observáveis e apresenta sinais proprietários encapsulados em linguagem pública. O objetivo não é prever resultado, mas organizar histórico, estados estatísticos e comportamento de aposta para apoiar decisão mais consciente e auditável.

## Compromissos centrais

1. **Rigor** — indicadores derivados de dados históricos e estados matemáticos controlados.
2. **Clareza** — sinais compreensíveis sem exposição da fórmula interna.
3. **Responsabilidade** — sem promessa de ganho, prêmio ou aumento garantido de chance.

## Escopo MVP aprovado no PRD

### Mobile
- onboarding e autenticação
- home com próximo concurso e atalhos
- monitor ALEQIA D com bloqueio por plano
- sugestão automática, montador manual e conferidor
- carteira resumida
- planos, checkout, compra de dezenas e suporte

### Web
- login/cadastro
- workspace do monitor ALEQIA D
- gerador de jogos e conferidor
- carteira
- planos e checkout
- suporte

## Navegação principal

1. Início
2. Monitor
3. Jogos
4. Carteira
5. ALEQIA+

## Personas e valor entregue

| Persona | Valor principal |
|---|---|
| Apostador casual | orientação simples para montar jogos |
| Apostador recorrente | controle de gasto, acertos e histórico |
| Apostador avançado | análise de dezenas, filtros e simulação |
| Gestor de bolão | organização de jogos e custos |
| Agente lotérico | base futura para serviço consultivo |

## Modelo de monetização

### Assinaturas por dezenas visíveis
| Plano | Dezenas visíveis |
|---|---:|
| Gratuito | 5 |
| Padrão | 15 |
| Intermediário | 20 |
| Pró | 24 |
| Ultra | 25 |

### Alavancas adicionais
- compra avulsa de dezenas ou painel completo por janela de tempo
- cursos ALEQIA pós-MVP
- suporte e produtos ALEQIA+

## Metas de produto destacadas

- conversão free → pago ≥ 3% em 90 dias
- DAU/MAU ≥ 22% no mês 3
- ≥ 80% de conclusão do onboarding
- ≥ 40% dos usuários pagos registrando apostas na Carteira

## Não objetivos do MVP

- não vender aposta oficial dentro do app sem autorização/integração própria
- não expor fórmulas internas do Projeto D
- não cobrir todas as loterias no MVP
- não lançar bolões oficiais, marketplace ou comunidade aberta nominal no MVP

## Linguagem pública dos indicadores

O PRD define encapsulamento dos indicadores internos sob nomes públicos como:

- ALEQIA Média
- ALEQIA Centro
- ALEQIA Impulso D
- ALEQIA Faixas D
- ALEQIA Tendência D
- ALEQIA Ritmo D
- ALEQIA Ciclo D

Esses nomes podem ser mostrados ao usuário; fórmulas e operadores internos não.

## Questões em aberto preservadas do PRD

1. stack final mobile: React Native/Expo ou Flutter
2. backend: FastAPI puro ou composição com BFF
3. engine real no MVP ou provider mockado/snapshots no início
4. provedor prioritário de pagamento
5. exigência de CPF/data de nascimento no cadastro ou só no checkout
6. estratégia oficial com Caixa: integração, redirecionamento ou exportação
7. entrada de WhatsApp no MVP público ou fase posterior
8. seleção fixa ou dinâmica das 5 dezenas do plano gratuito
9. importação futura por imagem/código de barras
10. estratégia de domínio de marca
