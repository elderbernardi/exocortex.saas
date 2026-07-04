# .quarantine/

Diretório de quarentena do Acervo Cognitivo (ADR-015).

Arquivos aqui estão aguardando purge definitivo após janela de 30 dias
(fonte canônica dos thresholds: `global/contracts/memory-lifecycle-constants.md`).
Durante esse período, o executivo pode restaurá-los com `excrtx-memory-quarantine`.

A estrutura interna espelha a do acervo (`micro/...`, `global/...`) para facilitar restore.

Não edite arquivos aqui diretamente. Use as skills do lifecycle:
- `excrtx-memory-quarantine` — mover, restaurar, purgar
- `excrtx-memory-syndic` — ciclo autônomo de scan/purge

`.purge_log` registra todas as operações de purge (append-only).
Este diretório NÃO faz parte da memória ativa — SEARCH e context loading o ignoram.
