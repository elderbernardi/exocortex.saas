# F5 — Polish & GA (charter)

> **Charter, não plano.** Plano detalhado após gate F4.

## Objetivo

Elevar o Canvas de Tarefas de feature funcional a parte canônica do produto Exocórtex: acessível, calibrado, documentado, auditável.

## Entregáveis

1. **A11y**: navegação por teclado completa (fila de gaps e checkout operáveis sem mouse); contraste e foco visível no padrão Calm Console.
2. **i18n**: strings no catálogo `static/i18n.js` (PT-BR primário, chaves EN) — padrão MOD-006.
3. **Calibração EX**: skills novas com EX-ID + cenário dogfood cada (formato FEATURES.md); `calibrate-hermes.sh` cobre enquadrador (vetor correto nas 3 frases canônicas + gaps não fabricados).
4. **Docs**: FEATURES.md + README (seção WebUI) + `provision/hermes-webui/README.md` atualizados; `sources.lock.yaml` re-pinado para o SHA estável do fork; UPSTREAM-SYNC.md com a estratégia de cherry-pick dos MODs novos.
5. **Auditoria interativa** (skill interactive-audit, gates G0–G5): persona executivo não-técnico executa a jornada completa (frase → sala → execução → colheita → receita); backlog de achados triado.
6. **Fechamento COLLAB**: change record concluído no umbrella; contrato exocortex-hermes-webui com status `ativo`; meta issue #130 fechada com sumário de evidências.

## Gate de saída

Dogfood PASS nos cenários novos; auditoria interativa com veredito GO; provisionamento limpo numa máquina de teste (`EXOCORTEX_ENABLE_HERMES_WEBUI=1 bash setup.sh` → Canvas de Tarefas funcional).

## Guardrails específicos

Nenhuma feature nova nesta fase (polish only); qualquer achado da auditoria que exija design volta como issue-filha, não como scope creep da F5.
