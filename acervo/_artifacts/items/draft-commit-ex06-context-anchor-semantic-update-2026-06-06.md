# DRAFT — commit local para EX-06

Status: não executado
Escopo: somente mudanças da correção semântica e de harness do EX-06

## Objetivo
Consolidar a correção da tríade obrigatória do contexto:
- Macroverso = quem fala
- Microversos = entidades semânticas autocontidas
- Tarefa = sala operacional

E unificar a regra de compartilhamento:
- `allow` tem precedência sobre `deny`

## Arquivos incluídos
- README.md
- FEATURES.md
- acervo/global/knowledge/WELCOME.md
- scripts/test-registry.sh
- skills/excrtx-behavior-canvas/SKILL.md
- skills/excrtx-onboard-welcome/SKILL.md
- skills/excrtx-onboard-welcome/references/bootstrap-macro-tutor.md
- docs/harness/ex-06-context-anchor-semantic-update.md

## Arquivos explicitamente fora deste commit
- candidate-issues.md
- HARNESS.md
- docs/branding/exocortex-ascii-logo.txt
- docs/branding/exocortex-ascii-logo-v2.txt
- acervo/_artifacts/items/draft-issue-ex06-canvas-microverso-semantics-and-sharing-2026-06-06.md

## Branch sugerida
`fix/ex06-context-anchor-semantics`

## Comandos sugeridos
```bash
git checkout -b fix/ex06-context-anchor-semantics

git add \
  README.md \
  FEATURES.md \
  acervo/global/knowledge/WELCOME.md \
  scripts/test-registry.sh \
  skills/excrtx-behavior-canvas/SKILL.md \
  skills/excrtx-onboard-welcome/SKILL.md \
  skills/excrtx-onboard-welcome/references/bootstrap-macro-tutor.md \
  docs/harness/ex-06-context-anchor-semantic-update.md

git commit -m "fix: alinhar EX-06 à tríade macroverso→microversos→tarefa

- redefine tarefa como sala operacional
- explicita microverso como entidade semântica autocontida
- adiciona sharing constraints com precedência allow > deny
- atualiza onboarding, documentação e testes de regressão"
```

## Critério de revisão antes do commit real
- conferir se não entrou arquivo de branding por acidente
- conferir se `candidate-issues.md` e `HARNESS.md` ficam fora
- validar que `scripts/test-registry.sh` continua com sintaxe ok (`bash -n`)
- validar que a issue de referência é a #32

## Referência externa já criada
- Issue: https://github.com/elderbernardi/exocortex.saas/issues/32
