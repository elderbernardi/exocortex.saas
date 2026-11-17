> **Escopo operacional vigente:** consultar `databrain_execution_status` e o runbook DataBrain `ops/EXECUTION_CONTROL.md` antes de usar estados/versões históricos deste documento. Gates são locais via `pb heavy`; o perfil factual atual é `semantic-v1`. Instruções de segurança, publicação ampla e autorização deste documento continuam aplicáveis.

# Ingestão de arquivos externos no DataBrain (inbox de produção)

Use ao receber arquivos externos (planilhas de fornecedores, CSVs, exports) para ingerir no DataBrain. Caso validado em campo: `base_scanntech_08.08.2026.xlsx` (painel de sell-out por PDV) em 2026-08-16/17.

## Passo a passo

1. **Localize o arquivo recebido.** Documentos enviados pelo executivo ficam em `~/.hermes/cache/documents/<id>_<nome>` — o nome na inbox deve ser limpo (sem o prefixo de cache).
2. **Entenda o conteúdo antes de prometer mapeamento.** Use `read_file` no XLSX (auto-extrai texto) para ver abas/colunas. Para metadados rápidos de uma planilha grande, extraia apenas abas e ranges do XML interno do XLSX com `zipfile` da biblioteca padrão; isso evita carregar milhares de linhas sem depender de bibliotecas extras.

   **Formato Scanntech APP reconhecido:** a combinação de abas `Dados Geral`, `Dados Guimaraes` e `Share Guimaraes` é aceita pelo parser dedicado Scanntech. Ele gera um Parquet Bronze por aba (`geral`, `guimaraes`, `share`). Ainda assim, confira o cabeçalho e o período: em `Dados Geral`, o padrão é PDV × estado × meses.
3. **Copie para a inbox com sudo.** O diretório é `drwxr-x--- databrain:databrain`; o usuário não tem acesso direto:

   ```bash
   SRC=/home/ubuntu/.hermes/cache/documents/<id>_<nome>
   DEST=/srv/databrain/data/inbox/<nome>
   sudo -n cp "$SRC" "$DEST"
   sudo -n ls -l "$DEST"
   sudo -n sha256sum "$SRC" "$DEST" | awk '{print $1}' | uniq -c   # esperado: 2 (hashes idênticos)
   ```

   Sem `set -e` cego: comandos `stat`/`ls` sem sudo falham com Permission denied mesmo quando o `cp` via sudo funcionou — verifique sempre por sudo.
4. **Confirme pela superfície MCP:** `databrain_list_inbox` deve listar o arquivo com `count: 1` e tamanho correto.
5. **`dry_run` (opcional, read-only):** valida a orquestração do pipeline. NO LOG esperado: `"Dry-run only: full pipeline plan validated"` com `stages: []` e counts zerados — isso é NORMAL e NÃO prova que o arquivo será aceito.
6. **`ingest_inbox`** (Bronze local, sem DRAFT): é o único teste real de mapeamento. Se o schema Bronze não reconhecer o formato, o pipeline rejeita e a inbox não é consumida.
7. Só então avalie `cold`/`hot`/`judge`/`publish` — publicações sempre com DRAFT + `approval_ref`.

## Limite estrutural

A ingestão Scanntech APP hoje cobre a entrada em Bronze, não a transformação automática para clientes, pedidos, briefings ou insights do modelo Sankhya. Para o formato reconhecido, espere logs com `Scanntech Ingestion`, três saídas Parquet, `errors: 0` e a movimentação do arquivo para `processed`. Arquivos de mercado transversais com abas ou schema diferentes continuam sujeitos a rejeição ou podem exigir um novo tipo de origem/dataset no repositório do Projeto B (via Issue/Discussion). Nunca inferir que a ingestão Bronze já atualizou Gold, IA ou Sales-AI.

## Integridade verificada nesta sessão

- SHA-256 do destino idêntico ao do cache (uniq -c = 2).
- `list_inbox` via MCP retornou o arquivo com `size_bytes` correto.
- `dry_run` (dbop_...) → `succeeded`, `ExecMainCode=0`, log com 2 linhas (plan validated + execution completed).
