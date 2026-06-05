---
title: DRAFT — provisionar exocortex-ops no setup executável
created: 2026-06-05
updated: 2026-06-05
nature: context
kind: draft
scope_slug: exocortex-ops
authority: draft
stability: draft
lifecycle_state: drafted
tags: [draft, setup, provisionamento, patch]
---

# DRAFT — provisionar exocortex-ops no setup executável

## Status

Não aplicado. Aguardando aprovação explícita do executivo.

## Objetivo

Adicionar `exocortex-ops` ao installer como microverso base, preservando arquivos existentes no runtime.

## Arquivos afetados propostos

- `/home/elder/projetos/projetob/exocortex.saas/setup.sh`
- `/home/elder/projetos/projetob/exocortex.saas/acervo/micro/exocortex-ops/**`

## Mudança proposta

1. Copiar o seed do runtime para o source do installer.
2. Criar diretórios de `exocortex-ops` no Step 1.
3. Excluir `micro/exocortex-ops/***` do rsync genérico do Acervo.
4. Provisionar `exocortex-ops` com `rsync --ignore-existing`.
5. Validar arquivos essenciais no Step 9.

## Patch conceitual para setup.sh

```diff
@@
 mkdir -p "$ACERVO/micro/_template"/{context,knowledge,contracts,prompts,skills,workflows,tools,templates,decisions,reflections,persona,_meta,raw,_archive}
+mkdir -p "$ACERVO/micro/exocortex-ops"/{context,knowledge,contracts,prompts,skills,workflows,tools,templates,decisions,reflections,persona,_meta,raw,_archive}
+mkdir -p "$ACERVO/micro/exocortex-ops/_meta"/{snapshots,drafts,indices}
@@
-if [ -d "$ACERVO_SRC" ]; then
-  rsync -a --exclude '__pycache__' "$ACERVO_SRC/" "$ACERVO/" 2>/dev/null || cp -r "$ACERVO_SRC"/* "$ACERVO/" 2>/dev/null || true
+if [ -d "$ACERVO_SRC" ]; then
+  if command -v rsync >/dev/null 2>&1; then
+    rsync -a --exclude '__pycache__' --exclude 'micro/exocortex-ops/***' "$ACERVO_SRC/" "$ACERVO/"
+  else
+    warn "rsync não encontrado; cópia genérica do Acervo pulada para evitar overwrite acidental"
+  fi
+  OPS_SRC="$ACERVO_SRC/micro/exocortex-ops"
+  OPS_DST="$ACERVO/micro/exocortex-ops"
+  if [ -d "$OPS_SRC" ]; then
+    if command -v rsync >/dev/null 2>&1; then
+      rsync -a --ignore-existing --exclude '__pycache__' "$OPS_SRC/" "$OPS_DST/"
+      log "Microverso base exocortex-ops instalado/preservado"
+    else
+      warn "rsync não encontrado; exocortex-ops seed não copiado para evitar overwrite acidental"
+    fi
+  else
+    warn "Microverso base exocortex-ops source não encontrado: $OPS_SRC"
+  fi
   log "Acervo: $(find "$ACERVO" -type f 2>/dev/null | wc -l) arquivos"
 else
   fail "Acervo source não encontrado: $ACERVO_SRC"
 fi
```

## Idempotência

- `mkdir -p` para diretórios.
- `rsync --ignore-existing` para seed do microverso.
- Nenhum arquivo semântico existente em `$ACERVO/micro/exocortex-ops` deve ser sobrescrito.
- Atualizações futuras do seed entram por migração aprovada, não por overwrite automático.

## Validações planejadas

```bash
bash -n /home/elder/projetos/projetob/exocortex.saas/setup.sh

tmp_root="$(mktemp -d)"
HERMES_HOME="$tmp_root/hermes" EXOCORTEX_HOME="$tmp_root/exocortex" bash /home/elder/projetos/projetob/exocortex.saas/setup.sh

find "$tmp_root/exocortex/acervo/micro/exocortex-ops" -type f -print0 | sort -z | xargs -0 sha256sum > "$tmp_root/before.sha256"
HERMES_HOME="$tmp_root/hermes" EXOCORTEX_HOME="$tmp_root/exocortex" bash /home/elder/projetos/projetob/exocortex.saas/setup.sh
find "$tmp_root/exocortex/acervo/micro/exocortex-ops" -type f -print0 | sort -z | xargs -0 sha256sum > "$tmp_root/after.sha256"
diff -u "$tmp_root/before.sha256" "$tmp_root/after.sha256"
```

## Rollback

- Remover a árvore seed `acervo/micro/exocortex-ops` do source.
- Reverter o patch em `setup.sh`.
- Preservar o runtime existente, salvo instrução explícita em contrário.

## Riscos

- O fallback atual `cp -r` pode sobrescrever arquivos se mantido.
- O source seed pode ficar defasado do runtime.
- A divergência entre modelo reportado pelo profile e sessão atual exige auditoria separada.

## Aprovação necessária

Aplicar somente após comando explícito: `aplique`, `pode aplicar` ou equivalente.
