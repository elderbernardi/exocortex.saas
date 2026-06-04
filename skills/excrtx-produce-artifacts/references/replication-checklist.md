# Replication Checklist

Use este checklist ao portar o Personal Artifact Workspace para outro Exocórtex-Hermes.

1. Copiar ou recriar o contrato:
   `~/.hermes/acervo/global/contracts/personal-artifact-workspace.md`

2. Criar área operacional:
   `~/.hermes/acervo/_artifacts/`

3. Instalar/copiar publicador:
   `~/.hermes/acervo/global/tools/artifact_publish.py`

4. Registrar documentação operacional:
   `~/.hermes/acervo/global/tools/personal-artifact-publisher.md`

5. Configurar OAuth Google Workspace ou provider equivalente.

6. Validar autenticação:
   `python ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --check`

7. Habilitar Google Drive API no projeto OAuth quando necessário.

8. Rodar pacote de teste com fonte Markdown e export HTML.

9. Confirmar criação de:
   - `manifest.json`
   - `receipt.google_drive.json` ou `receipt.google_drive.failed.json`

10. Validar política Draft-First:
    - upload privado permitido;
    - link público/compartilhamento bloqueado sem aprovação.

11. Atualizar `global/index.md` e `global/log.md`.

12. Registrar qualquer diferença do ambiente alvo no Acervo.
