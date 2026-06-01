---
name: personal-artifact-workspace
description: "Criar, organizar, exportar e publicar artefatos finais do Exocórtex no workspace do usuário, mantendo reprodutibilidade no Acervo."
version: 1.0.1
author: Exocórtex
license: MIT
metadata:
  hermes:
    tags: [exocortex, artifacts, drive, acervo, publishing, reproducibility]
    category: exocortex
    related_skills: [acervo-manager, google-workspace, exocortex-draft-first, stop-slop]
---

# Personal Artifact Workspace

Use esta skill quando o usuário pedir criação, organização, exportação ou entrega de artefatos finais: documentos, PDFs, HTML, planilhas, imagens, slides, pacotes ZIP ou relatórios.

Também use quando o usuário pedir para desenhar, replicar ou auditar o harness de publicação de artefatos em outro Exocórtex-Hermes.

Antes de executar, carregue quando aplicável:

- `acervo-manager`, para respeitar a ontologia e o cascade do Acervo.
- `productivity/google-workspace`, para operações no Google Drive.
- `exocortex-draft-first`, se houver compartilhamento, envio, publicação externa ou mudança de permissão.
- `exocortex-design-system` e `taste-skill`, se o artefato tiver componente visual.
- `stop-slop`, se o artefato tiver prosa final.

## Princípio

O Drive é ferramenta de publicação. O Acervo é fonte cognitiva e registro reprodutível.

Não sincronize o Acervo inteiro com Drive. Publique exports finais por um pacote operacional controlado e grave receipts locais.

## Modelo operacional

```text
~/.hermes/acervo/_artifacts/{artifact_id}/
├── source/
│   ├── source.md
│   └── metadata.yaml
├── assets/
│   ├── images/
│   ├── data/
│   ├── logos/
│   ├── fonts/
│   ├── raw/
│   └── generated/
├── exports/
│   ├── *.pdf
│   ├── *.html
│   ├── *.docx
│   ├── *.xlsx
│   └── *.zip
├── manifest.json
└── receipt.google_drive.json
```

## Regra de fonte

Markdown é a fonte padrão para documentos, planos, ofícios, relatórios, roteiros e materiais didáticos.

Exceções aceitas:

- Planilhas: `.xlsx`, `.csv`, `.json` ou script gerador.
- Imagens: `.svg`, `.png`, `.html`, `.excalidraw` ou prompt visual.
- Apresentações: `.md` Marp ou `.pptx`.
- PDFs recebidos: PDF original como fonte, extração textual em `source/`.
- Documentos colaborativos vivos: Drive como fonte externa; Acervo guarda link e manifesto.

## Procedimento padrão

1. Classificar o artefato: documento, planilha, imagem, apresentação, HTML, ZIP, relatório ou código.
2. Se for código versionável, usar GitHub como destino primário. Se for consumo humano, usar Drive.
3. Resolver microverso, disciplina/projeto/contexto e pasta humana de destino.
4. Criar pacote em `~/.hermes/acervo/_artifacts/{artifact_id}/`.
5. Escrever a fonte em `source/`.
6. Copiar assets necessários para `assets/` com paths relativos.
7. Exportar formatos finais para `exports/`.
8. Validar exports antes de publicar: arquivo existe, tamanho maior que zero, MIME coerente e hash SHA-256 registrado.
9. Aplicar quality gates: stop-slop para prosa final; design/taste gate para visual.
10. Gerar ou atualizar `manifest.json` com hash, MIME, tamanho, fonte, exports e destino.
11. Publicar exports no Drive privado do usuário via provider configurado.
11.1. Resolver a pasta de destino antes do upload (`drive_target.folder_path`) e exigir parent explícito; upload na raiz é inválido para artefatos finais.
12. Gravar `receipt.{provider}.json` com IDs, links e status.
13. Entregar ao usuário o link do Drive e o caminho local do pacote.
14. Se o artefato tiver valor cognitivo, criar página semântica no microverso apontando para o artifact_id.

## Manifest e receipt

O manifesto é a fonte local de rastreabilidade. O receipt é a prova de publicação.

Campos mínimos do manifesto:

```json
{
  "artifact_id": "art_YYYYMMDD_HHMMSS_slug",
  "title": "Título humano",
  "microverso": "ensino",
  "status": "draft|ready|published|failed",
  "source_type": "markdown|xlsx|image|mixed|external",
  "source_path": "source/source.md",
  "assets_dir": "assets",
  "exports": [
    {
      "path": "exports/arquivo.pdf",
      "kind": "pdf",
      "mime": "application/pdf",
      "sha256": "...",
      "size": 12345
    }
  ],
  "drive_target": {
    "provider": "google_drive",
    "folder_path": "exocortex/inbox",
    "visibility": "private"
  }
}
```

Campos mínimos do receipt:

```json
{
  "provider": "google_drive",
  "published_at": "ISO-8601",
  "folder_path": "exocortex/inbox",
  "folder_id": "...",
  "files": [
    {
      "export_path": "exports/arquivo.pdf",
      "drive_file_id": "...",
      "web_view_link": "https://drive.google.com/...",
      "mime": "application/pdf",
      "visibility": "private",
      "sha256": "...",
      "size": 12345
    }
  ]
}
```

## Telegram delivery pattern

When the current surface is Telegram and the artifact is a visual board, HTML prototype, deck preview or multi-file deliverable, create a ZIP export even if the primary deliverable is a single file. Register the ZIP in `manifest.json`, deliver it with `MEDIA:/absolute/path/to/file.zip`, and include the local path to the primary export. See `references/telegram-zip-visual-artifacts.md`.

## Provider inicial: Google Drive local

Prefira OAuth local do Hermes, via skill `productivity/google-workspace`, antes de usar Composio.

Use Composio apenas quando o OAuth local não existir, quando o usuário pedir explicitamente ou quando o ambiente alvo exigir esse conector.

Pré-check:

```bash
python ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --check
```

Publicador inicial:

```bash
python ~/.hermes/acervo/global/tools/artifact_publish.py init \
  --title "Título" \
  --microverso ensino \
  --source-md /caminho/source.md \
  --drive-path "exocortex/ensino/2026/aulas"

python ~/.hermes/acervo/global/tools/artifact_publish.py publish \
  --artifact-dir ~/.hermes/acervo/_artifacts/{artifact_id}
```

## Políticas de destino

Destino padrão quando faltar contexto:

```text
exocortex/inbox
```

Padrões recomendados:

```text
exocortex/ensino/{ano}/{disciplina}/{tipo}
exocortex/gabinete/{ano}/{tipo}
exocortex/dev/{ano}/artefatos/{projeto}
```

Não pergunte a pasta se a intenção estiver clara. Use Inbox quando a ambiguidade não mudar o valor da entrega.

## Draft-First

Upload privado para o Drive do próprio usuário conta como entrega pessoal quando o usuário pediu o artefato.

Exige Draft-First:

- criar link público;
- compartilhar com turma, terceiros, domínio ou organização;
- enviar por email/mensagem;
- publicar em site, GitHub release ou documento compartilhado;
- converter para documento colaborativo quando isso muda formato/semântica do arquivo.

## GitHub vs Drive

Use GitHub quando o artefato for código versionável, PR, branch, commit ou release técnico.

Use Drive quando o artefato for consumo humano: PDF, planilha, ofício, relatório, material de aula, apresentação, imagem, HTML exportado ou ZIP final.

Para `exocortex-slides`, Drive é o destino padrão de publicação privada. Vercel ou URL pública são alvos opcionais avançados e exigem Draft-First explícito; não use criação/login Vercel como caminho padrão para usuário comum.

Caso híbrido: código no GitHub; artefatos finais no Drive; manifestos no Acervo.

## Troubleshooting durável

### OAuth válido, mas Drive API desabilitada

Sintoma: `setup.py --check` retorna autenticado, mas upload/search falha com `HttpError 403` informando que Google Drive API não foi usada ou está desabilitada no projeto.

Correção:

1. Habilitar Google Drive API no projeto Google Cloud do OAuth usado pelo Hermes.
2. Aguardar propagação.
3. Reexecutar o publish.

Registre a falha em `receipt.google_drive.failed.json` e marque `manifest.status = failed`. Não transforme isso em regra negativa sobre Drive ou OAuth.

## Common Pitfalls

1. Sincronizar o Acervo inteiro com Drive. Isso mistura memória cognitiva com superfície de entrega.
2. Publicar source/assets por padrão. Entregue exports finais; envie pacote completo só quando fizer sentido.
3. Criar link público automaticamente. Upload privado é entrega pessoal; compartilhamento exige aprovação.
4. Confundir OAuth válido com API habilitada. O token pode renovar e a Drive API ainda falhar com 403.
5. Usar Composio como default. Para o Exocórtex pessoal, prefira OAuth local auditável.
6. Deixar artefato sem receipt. Link sem receipt não é reprodutível.
7. Gerar PDF/HTML sem fonte. Sempre preserve a fonte ou registre por que o formato final é a fonte canônica.
8. Ignorar assets. Copie assets necessários para o pacote com paths relativos.
9. Upload final sem parent resolvido (raiz do Drive). Toda publicação final precisa de `drive_target.folder_path` e receipt com `folder_id`.
10. Tratar Vercel como caminho padrão para decks HTML premium. Para usuário comum, export final vai para Drive privado; URL pública/deploy é exceção com Draft-First.

## Verification Checklist

- [ ] Skill `personal-artifact-workspace` carregada antes de criar/publicar artefato.
- [ ] Pacote criado em `~/.hermes/acervo/_artifacts/{artifact_id}`.
- [ ] Fonte preservada em `source/` ou exceção registrada no manifesto.
- [ ] Assets necessários copiados para `assets/`.
- [ ] Exports finais gerados em `exports/`.
- [ ] Em Telegram, ZIP final criado e registrado no manifesto quando o artefato for visual, HTML, deck ou pacote multi-arquivo.
- [ ] Hash, MIME e tamanho registrados no manifesto.
- [ ] Quality gates aplicados quando houver texto ou visual.
- [ ] Upload privado feito no Drive configurado.
- [ ] Receipt gravado com `drive_file_id` e `web_view_link`.
- [ ] Falhas gravadas em `receipt.google_drive.failed.json`.
- [ ] Compartilhamento externo bloqueado até aprovação explícita.
- [ ] Se houver valor cognitivo, página semântica criada no microverso.

## Reprodutibilidade

Detalhes de apoio:

- `references/session-2026-05-30-mvp.md` — desenho e decisões do MVP inicial.
- `references/replication-checklist.md` — checklist para portar a capacidade para outro Exocórtex-Hermes.
- `references/pdd-v2-doc-alignment.md` — como alinhar PDD v2, provisioner e microverso ao evoluir esta capacidade.
- `references/drive-path-governance.md` — regra de parent explícito, fallback `exocortex/inbox` e correção de upload indevido na raiz.
- `references/telegram-zip-visual-artifacts.md` — padrão de entrega por ZIP no Telegram para artefatos visuais/HTML com manifesto.
- `references/frontend-slides-artifact-track.md` — política de pacote, Drive e Draft-First para apresentações HTML premium geradas por `exocortex-slides`.
- `references/marp-frontend-slides-artifact-tracks.md` — política para combinar Marp como linha de produção de slides e Frontend Slides como renderer premium de artefatos visuais.

Toda implementação replicável precisa conter:

- contrato em `global/contracts/personal-artifact-workspace.md`;
- ferramenta ou provider equivalente;
- área `_artifacts/`;
- manifestos e receipts;
- regra de Drive como publicação, não sincronização;
- política Draft-First para compartilhamento;
- documentação de setup do provider.

## Referências

- `references/session-2026-05-30-mvp.md` — desenho e decisões do MVP inicial.
- `references/replication-checklist.md` — checklist de portabilidade para outro Exocórtex-Hermes.
- `references/pdd-v2-doc-alignment.md` — alinhamento documental entre PDD v2, provisioner e microverso.
- `templates/manifest-template.md` — template comentado de `manifest.json`.
