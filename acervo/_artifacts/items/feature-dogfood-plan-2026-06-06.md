# Plano — Dogfood conversacional EX-01 a EX-35

Status: execução autorizada pelo executivo em 2026-06-06.

Escopo: testar todas as features Exocórtex listadas em `FEATURES.md`, EX-01 a EX-35, por conversas reais simuladas em instâncias isoladas. EX-08 já foi testada e falhou criticamente.

Regra de operação: registrar logs e rascunhos locais no projeto. Não criar issues no GitHub; arquivos locais bastam para este ciclo.

## Status inicial

- EX-08 Draft-First: FAIL crítico, já registrado em `feature-dogfood-2026-06-06.md` e `draft-issue-draftfirst-telegram-2026-06-06.md`.

## Lotes de execução

- Lote A: EX-01, EX-02, EX-03, EX-04
- Lote B: EX-05, EX-06, EX-07, EX-09, EX-10
- Lote C: EX-11, EX-12, EX-13, EX-14, EX-15, EX-16, EX-17
- Lote D: EX-18, EX-19, EX-20, EX-21
- Lote E: EX-22, EX-23, EX-24
- Lote F: EX-25, EX-26, EX-27, EX-28, EX-29, EX-30
- Lote G: EX-31, EX-32, EX-33, EX-34, EX-35

## Método de auditoria por feature

Cada execução deve retornar:

- feature;
- prompt natural usado;
- resposta real da instância;
- ferramentas usadas/tentadas;
- side effects executados;
- evidência;
- status: PASS, PARTIAL, FAIL ou BLOCKED;
- defeito candidato, se houver.
