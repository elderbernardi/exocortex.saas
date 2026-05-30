# Personal Artifact Workspace — Addendum PDD v2

> **Data:** 2026-05-30T15:03-03:00
> **Status:** Addendum pós-graduação
> **Escopo:** publicação de artefatos finais do Exocórtex em workspace do usuário
> **Microverso canônico:** `hermes-setup`

## Decisão

O PDD v2 passa a reconhecer o Personal Artifact Workspace como capacidade de produção pós-P5.

Essa capacidade não altera a sequência base de 27 prompts do PDD v2. Ela documenta uma extensão replicável para Exocórtex-Hermes em produção: criar artefatos finais em pacotes locais do Acervo, publicar exports no Drive privado do usuário e manter fonte, assets, manifestos e receipts sob controle local.

## Princípios

1. Drive é ferramenta de publicação, não sincronização.
2. O Acervo guarda fonte, assets, manifesto, receipt e sentido cognitivo.
3. O Drive recebe exports finais para uso humano.
4. Markdown é fonte padrão para documentos, não dogma.
5. Planilhas, imagens, apresentações complexas e PDFs recebidos podem ter outras fontes canônicas.
6. Upload privado para o Drive do próprio usuário é entrega pessoal.
7. Compartilhamento externo, link público, envio ou mudança de permissão seguem Draft-First.
8. Composio é fallback ou conector opcional. O provider inicial usa OAuth local do Hermes.

## Estrutura operacional

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

## Arquivos canônicos no runtime

```text
~/.hermes/acervo/global/contracts/personal-artifact-workspace.md
~/.hermes/acervo/global/tools/personal-artifact-publisher.md
~/.hermes/acervo/global/tools/artifact_publish.py
~/.hermes/acervo/_artifacts/README.md
~/.hermes/skills/exocortex/personal-artifact-workspace/SKILL.md
```

## Skill operacional

A skill `personal-artifact-workspace` deve ser carregada quando o usuário pedir criação, organização, exportação ou entrega de documentos, PDFs, HTML, planilhas, imagens, slides, ZIPs ou relatórios.

Skills associadas:

- `acervo-manager`, para respeitar a ontologia do Acervo.
- `productivity/google-workspace`, para publicar no Drive via OAuth local.
- `exocortex-draft-first`, quando houver compartilhamento, envio ou permissão externa.
- `exocortex-design-system` e `taste-skill`, quando houver componente visual.
- `stop-slop`, quando houver prosa final.

## Fluxo padrão

1. Classificar o artefato: documento, planilha, imagem, apresentação, HTML, ZIP, relatório ou código.
2. Se for código versionável, usar GitHub como destino primário.
3. Se for consumo humano, usar Drive como destino primário.
4. Criar pacote em `~/.hermes/acervo/_artifacts/{artifact_id}/`.
5. Preservar fonte em `source/`.
6. Copiar assets necessários para `assets/`.
7. Gerar exports finais em `exports/`.
8. Validar export: existência, tamanho maior que zero, MIME coerente e SHA-256.
9. Aplicar quality gates quando houver texto ou visual.
10. Publicar exports no Drive privado do usuário.
11. Gravar receipt com `drive_file_id`, `web_view_link`, hash, MIME, tamanho e status.
12. Entregar link do Drive e caminho local do pacote.
13. Se houver valor cognitivo, criar página semântica no microverso apontando para o `artifact_id`.

## Configuração do provider inicial

Pré-check de OAuth:

```bash
python ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --check
```

Criar pacote:

```bash
python ~/.hermes/acervo/global/tools/artifact_publish.py init \
  --title "Título" \
  --microverso ensino \
  --source-md /caminho/source.md \
  --drive-path "Exocortex/Ensino/2026/Aulas"
```

Publicar exports:

```bash
python ~/.hermes/acervo/global/tools/artifact_publish.py publish \
  --artifact-dir ~/.hermes/acervo/_artifacts/{artifact_id}
```

## Troubleshooting registrado

`setup.py --check` valida o token OAuth. Ele não garante que a Google Drive API esteja habilitada no projeto Google Cloud.

Se o upload falhar com `HttpError 403` e mensagem de API desabilitada:

1. Habilitar Google Drive API no projeto OAuth usado pelo Hermes.
2. Aguardar propagação.
3. Reexecutar `publish`.
4. Preservar `receipt.google_drive.failed.json` como auditoria.

## Relação com PDD v2

Esta capacidade nasce depois da graduação P5_PRODUCTION. Ela não muda os gates históricos do PDD v2, mas deve entrar em qualquer próxima golden image ou PDD v2.1 como capacidade de entrega final.

A documentação canônica fica em dois lugares:

- Plano PDD v2: este addendum explica como replicar a capacidade no harness.
- Microverso `hermes-setup`: contratos, decisões e workflows registram o sentido operacional dentro do Acervo.

## Critério para promoção futura

Promover para golden image padrão quando:

- Google Drive API estiver habilitada e testada;
- `artifact_publish.py` publicar com receipt válido em ambiente limpo;
- a skill `personal-artifact-workspace` estiver no bundle oficial;
- o provisioner instalar contrato, ferramenta, README e skill;
- o smoke test de artefato final passar em gateway local e remoto.
