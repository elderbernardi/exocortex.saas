# Exocórtex.IA — Prompt para Codex CLI

> Cole este prompt no Codex ou use o one-liner abaixo.

## One-liner

```bash
# Download + execução direta
bash <(curl -fsSL https://raw.githubusercontent.com/elderbernardi/exocortex.saas/main/install-exocortex.sh)
```

## Para Codex CLI com repo já clonado

```bash
cd ~/.exocortex-provisioner  # ou onde o install-exocortex.sh extraiu
codex --cd . --approval-mode on-request "$(cat CODEX_BOOTSTRAP.md)"
```

## Para Codex CLI sem repo (download direto)

```bash
# 1. Baixar provisioner
TMPDIR=$(mktemp -d)
curl -fsSL https://github.com/elderbernardi/exocortex.saas/archive/refs/heads/main.tar.gz | tar xz -C "$TMPDIR"
PROV="$TMPDIR/exocortex.saas-main/plans/pdd_v2/provisioner"

# 2. Lançar codex com o bootstrap prompt
codex --cd "$PROV" "$(cat "$PROV/CODEX_BOOTSTRAP.md")"
```
