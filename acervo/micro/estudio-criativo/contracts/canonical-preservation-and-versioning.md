---
title: Contrato — Preservação Canônica e Versionamento Integral
created: 2026-06-01
updated: 2026-06-01
nature: contracts
kind: contract
scope_mode: micro
scope_slug: estudio-criativo
applies_to: []
authority: canonical
operational_mode: blocking
stability: stable
sources: []
derived_from: []
confidence: high
promotion_policy: none
upstream:
  source_skill: null
  assumed_version: null
  coupling: none
tags: [contract, canonical, preservation, versioning]
---

# Regra canônica

O microverso `estudio-criativo` é canônico no Acervo do Exocórtex.

## Obrigações

1. Preservar integralmente o conteúdo do microverso.
2. Registrar toda mudança em `log.md`.
3. Versionar cada alteração de arquivo no controle de versão do workspace.
4. Proibir sobrescrita destrutiva sem trilha de auditoria.
5. Tratar exclusão como exceção, com justificativa explícita e registro.
6. Manter histórico de decisões e evolução metodológica no próprio microverso.

## Política operacional

- Alterações são incrementais e rastreáveis.
- Conteúdo legado vai para `_archive/` quando houver refatoração estrutural.
- Mudanças em contratos exigem revisão cuidadosa e atualização de `index.md` quando aplicável.
