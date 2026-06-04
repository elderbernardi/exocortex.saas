# Drive search hardening (sem Composio)

Checklist aplicado em sessão real:

- OAuth validado com `setup.py --check`.
- Diagnóstico de falha inicial: `HttpError 403 accessNotConfigured` (Drive API desabilitada no projeto GCP).
- Após habilitar API no Console, busca voltou a responder normalmente.

Melhorias de robustez confirmadas:

1. Escape de entrada (`'` e `\\`) ao montar `fullText contains '...`.
2. Filtro padrão `trashed = false` no modo textual.
3. Paginação por `nextPageToken` até atingir `--max`.
4. Validação de `--max >= 1`.

Teste mínimo recomendado:

- termo comum: `relatório`
- termo com apóstrofo: `O'Reilly`
- `--max` acima do page size para validar paginação.
