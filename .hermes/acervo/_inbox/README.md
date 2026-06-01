
# Exocortex Inbox

Área operacional para intake de arquivos, mídias, links e lotes recebidos pelo Exocórtex.

Esta pasta não substitui o Acervo semântico. Ela preserva bruto, extrações e roteamento antes de qualquer promoção.

## Estrutura

```text
_inbox/
└── int_YYYYMMDD_HHMMSS_slug/
    ├── original/
    ├── derived/
    ├── manifest.json
    ├── routing.json
    └── log.json
```

## Regras

1. O original sempre é preservado.
2. `manifest.json` registra canal, hash, MIME, tamanho e status.
3. `routing.json` registra hipóteses de microverso, diretório funcional e próxima ação.
4. `derived/` guarda texto extraído, OCR, transcrição ou preview.
5. Promoção para o Acervo é posterior e explícita.
6. ZIPs não são promovidos automaticamente.
7. `_inbox/` é operacional; não é página de conhecimento.
