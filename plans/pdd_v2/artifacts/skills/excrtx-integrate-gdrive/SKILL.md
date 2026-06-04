---
name: excrtx-integrate-gdrive
description: Configurar e operar Google Drive via API direta (sem Composio), com foco em robustez de busca e validação.
version: 1.0.0
author: Exocortex
license: MIT
---

# Google Drive Direct API (sem Composio)

## Quando usar
Use esta skill quando o executivo pedir integração direta com Google Drive (OAuth + Drive API) sem camada Composio.

## Objetivo
Garantir operação estável para leitura/escrita no Drive, com atenção para falhas comuns de query, paginação e higiene de resultados.

## Referências
- `references/drive-search-hardening.md` — checklist curto de diagnóstico e hardening validado em sessão real.
- `references/setup-propagation-checklist.md` — como propagar o hardening para todos os setups (projeto, Hermes e seed) e validar pós-provisionamento.

## Workflow padrão
1. Validar autenticação OAuth local (`setup.py --check`).
2. Validar ativação da Drive API no projeto GCP (erro 403 `accessNotConfigured` indica API desabilitada).
3. Validar leitura real com `drive search`.
4. Se necessário, endurecer a implementação de busca no wrapper local.
5. Propagar o hardening para os scripts de setup do Exocórtex (projeto + `~/.hermes/setup.sh` + seed de artifacts), para evitar regressão em reprovisionamento.
6. Para publicação de artefato final, encaminhar para `excrtx-produce-artifacts` e usar `artifact_publish.py` (manifest + receipt + resolução de pasta). Não publicar final com `google_api.py drive upload` direto.

## Hardening obrigatório para `drive search`
Ao implementar/ajustar busca em Drive API direta, aplicar este baseline:

1) Escapar input textual de query
- Em query construída com `fullText contains '...`', escapar aspas simples (`'`) e barra (`\\`) no texto do usuário.
- Evita quebra de sintaxe em termos como `O'Reilly`.

2) Excluir lixeira por padrão
- Em modo não-raw, anexar `and trashed = false`.
- Mantém resultado útil por default e reduz ruído operacional.

3) Paginar até cumprir `--max`
- Solicitar `nextPageToken` nos fields.
- Repetir chamadas até alcançar `--max` ou esgotar páginas.
- Não assumir que uma chamada retorna tudo.

4) Validar limites de entrada
- Rejeitar `--max < 1` com erro explícito.

## Snippet de referência (lógica)
- `fields`: `nextPageToken, files(id,name,mimeType,modifiedTime,webViewLink)`
- Loop: acumular `files`, atualizar `pageToken`, encerrar sem token.
- Retorno final: truncar para `files[:max]`.

## Verificação rápida
- Busca comum: termo com acento (ex.: `relatório`).
- Busca com apóstrofo (ex.: `O'Reilly`).
- Busca com `--max` maior que page size para confirmar paginação.

## Pitfalls
- `403 accessNotConfigured` não é bug de código: é API desabilitada no projeto GCP.
- Query textual sem escape quebra silenciosamente ou retorna erro de sintaxe.
- Sem filtro de `trashed`, resultados podem confundir decisões do usuário.

## Regras de execução
- Ações destrutivas/externas (delete/share/write em contexto de comunicação) seguem Draft-First quando envolverem decisão de negócio do executivo.
- Para diagnóstico técnico local, pode executar validações diretas sem etapa de rascunho.
- `google_api.py drive upload` direto é permitido para teste técnico pontual; é proibido para publicação final de artefato do Exocórtex.
