# Frontend Slides Artifact Track

## Decisão operacional

Para apresentações HTML premium geradas por `exocortex-slides`, o destino padrão de entrega é Google Drive privado via Personal Artifact Workspace.

Vercel não é padrão. Criar conta externa ou autenticar CLI de deploy é atrito alto para usuário comum. Use Vercel apenas quando o usuário pedir URL pública e aprovar explicitamente um DRAFT.

## Pacote mínimo

```text
_artifacts/{artifact_id}/
├── source/
│   ├── source.md
│   ├── brief.md
│   └── slides.marp.md        # se houver fonte Marp
├── assets/
├── previews/
│   ├── style-a.html
│   ├── style-b.html
│   └── style-c.html
├── exports/
│   ├── deck.html
│   ├── deck.pdf
│   └── deck.zip
├── manifest.json
└── receipt.google_drive.json
```

## Regra de fonte

Markdown permanece fonte canônica. HTML é export. Se o HTML for editado manualmente e virar fonte real, registrar no manifesto como nova revisão ou divergência.

## Fluxo padrão

1. Preservar fonte Markdown em `source/`.
2. Gerar previews em `previews/`.
3. Gerar `exports/deck.html`.
4. Exportar `exports/deck.pdf` quando for entrega final.
5. Criar `exports/deck.zip` incluindo fonte, HTML, PDF, assets e manifesto.
6. Publicar ZIP/PDF/HTML no Drive privado, com `drive_target.folder_path` explícito.
7. Gravar receipt com IDs e links.

## Draft-First

Exige aprovação explícita antes de executar:

- link público;
- compartilhamento com terceiros/turma/domínio;
- envio por email/mensagem;
- deploy Vercel;
- conversão para documento colaborativo compartilhado.

Upload privado ao Drive do próprio usuário é export pessoal quando o usuário pediu a entrega final.
