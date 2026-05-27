---
name: exocortex-prompt-log
description: Registra prompts de configuração no MEMORY.md para auditoria e reprodutibilidade
version: 1.0.0
metadata:
  hermes:
    tags: [exocortex, logging, audit, configuration]
---

# Exocortex Prompt Log

## Trigger
Ativar AUTOMATICAMENTE após cada prompt de configuração que altere SOUL.md, MEMORY.md, config.yaml ou instale skills/tools.

## Procedure
1. Registrar em MEMORY.md uma entrada com:
   - Prompt ID (ex: 004)
   - Timestamp (ISO 8601)
   - Fase (P1-P6)
   - Artefatos criados ou modificados
   - Status: success | partial | failed
   - Resumo do que mudou

2. Formato de entrada:
   ```
   [PDD-{ID}] {timestamp} | Phase: P{N} | Status: {status}
   Artifacts: {lista}
   Summary: {resumo em 1 linha}
   ```

## Objective
Manter um log auditável que permite REPRODUZIR a configuração em uma nova instância Hermes. Qualquer agente deve poder ler MEMORY.md e entender o histórico completo de configuração.
