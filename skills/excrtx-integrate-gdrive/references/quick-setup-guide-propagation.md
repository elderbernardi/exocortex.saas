# Quick-setup guide propagation (Google Cloud OAuth)

Objetivo: garantir que o script `gcloud_quick_setup.py` seja deployado junto com a skill `google-workspace` em reprovisionamento.

## Escopo

O script gera links pré-configurados do Google Cloud Console com o project ID auto-detectado,
eliminando a necessidade de navegação manual no console. Reduz o setup de ~9 passos para ~3.

## Onde vive

- **Seed/repo:** `scripts/gcloud_quick_setup.py` (exocortex.saas)
- **Runtime Hermes:** `$HERMES_HOME/skills/productivity/google-workspace/scripts/gcloud_quick_setup.py`
- **Integração:** `$HERMES_HOME/skills/productivity/google-workspace/scripts/setup.py --setup-guide`

## Requisitos de propagação

1. Copiar `gcloud_quick_setup.py` para `$HERMES_HOME/skills/productivity/google-workspace/scripts/` no provisioning.
2. Garantir que `setup.py` tenha o comando `--setup-guide` funcional.
3. Script deve ser standalone (funciona com `python gcloud_quick_setup.py` direto).

## Detecção de projeto

Ordem de precedência para auto-detecção do project ID:
1. `client_secret.json` existente em `~/.hermes/` (extrai prefixo numérico do client_id)
2. `gcloud config get-value project` (se gcloud CLI disponível)
3. `gcloud projects list --limit=1` (fallback)
4. Se nada encontrado → instruir usuário a fornecer `--project ID`

## Smoke test pós-deploy

```bash
# Detecção automática (deve encontrar projeto)
python $HERMES_HOME/skills/productivity/google-workspace/scripts/gcloud_quick_setup.py --format json

# Via setup.py
python $HERMES_HOME/skills/productivity/google-workspace/scripts/setup.py --setup-guide text

# Formato texto
python $HERMES_HOME/skills/productivity/google-workspace/scripts/gcloud_quick_setup.py --format text
```

## Pitfall

O script `gcloud_quick_setup.py` depende de `_hermes_home.py` (módulo sibling).
Se copiado para outro diretório sem `_hermes_home.py`, falha na importação.
Sempre manter junto com os outros scripts da skill `google-workspace`.