---
name: personal-intake-workspace
description: "Receber, normalizar, extrair, triar e promover arquivos e mídias enviados ao Exocórtex por múltiplos canais, sem contaminar o Acervo semântico com bruto não curado."
version: 1.0.0
author: Exocórtex
license: MIT
metadata:
  hermes:
    tags: [exocortex, intake, inbox, ingestion, multicanal, acervo, triage, voice, files]
    category: exocortex
    related_skills: [acervo-manager, hermes-surface-architecture, personal-artifact-workspace, exocortex-draft-first]
---

# Personal Intake Workspace

Use esta skill quando o usuário pedir para desenhar, implementar, revisar ou operar o caminho de entrada de arquivos, áudios, imagens, PDFs, links ou lotes enviados ao Exocórtex.

Também use quando a discussão envolver inbox, intake multicanal, anexos, dropzone, onboarding voice-first, triagem cognitiva ou promoção de material bruto para o Acervo.

Antes de executar, carregue quando aplicável:

- `acervo-manager`, para respeitar ontologia, scope e promotion.
- `hermes-surface-architecture`, para separar canal, UI e cockpit operacional.
- `exocortex-draft-first`, se o intake acionar comunicação ou publicação externa.
- `personal-artifact-workspace`, se o material ingerido virar artefato final publicável.
- `ocr-and-documents`, `google-workspace`, STT ou visão, conforme o tipo de mídia.

## Princípio

Entrada não é memória. Entrada é matéria-prima.

O arquivo recebido não deve entrar direto no Acervo semântico. Primeiro ele cai numa área operacional de intake, onde é preservado, descrito, extraído e triado. Só depois o sistema decide se aquilo vira memória, tarefa, referência operacional ou artefato derivado.

## Modelo mental

Use a simetria abaixo:

```text
input -> _inbox -> acervo semântico -> _artifacts -> publish
```

- `_inbox/` guarda bruto, extrações e roteamento.
- `acervo/` guarda conhecimento curado.
- `_artifacts/` guarda saídas finais para consumo humano.

Não colapse essas camadas.

## Workspace operacional

Local canônico:

```text
~/.hermes/acervo/_inbox/{intake_id}/
├── original/
│   └── <arquivo ou mídia original>
├── derived/
│   ├── transcript.md
│   ├── ocr.md
│   ├── extracted.md
│   └── preview.json
├── manifest.json
├── routing.json
└── log.json
```

`_inbox/` é operacional, não semântico. Não substitui `knowledge/`, `context/`, `contracts/` nem `raw/` de um microverso.

## Regra estrutural

Não escrever uploads diretamente em `micro/{slug}/knowledge`, `context`, `contracts` ou páginas equivalentes.

Também não usar o Acervo semântico como depósito de binários, anexos ou transcrições cruas. O destino semântico só é decidido após triagem.

## IntakeEnvelope

Todo canal deve convergir para um envelope interno comum. Campos mínimos:

```json
{
  "intake_id": "int_YYYYMMDD_HHMMSS_slug",
  "channel": "telegram|whatsapp|email|webhook|api_server|dashboard",
  "received_at": "ISO-8601",
  "content_type": "document|image|audio|video|zip|link|text",
  "original_filename": "...",
  "mime_type": "...",
  "local_cached_path": "...",
  "user_caption": "...",
  "correlation_id": "...",
  "session_ref": "..."
}
```

Canal não decide workflow. Canal só entrega envelope.

## Arquitetura recomendada

Quando existir uma GUI ou integração dedicada, respeite a separação:

```text
USER -> GUI -> SERVER -> HERMES
```

- GUI/gateway recebe o gesto humano.
- SERVER normaliza upload, persiste o bruto e gera o envelope.
- HERMES classifica, extrai, triageia e propõe promoção.

Não empurre a responsabilidade de recepção de arquivos crus para dentro da lógica cognitiva se houver um servidor intermediário disponível.

### Seed orgânico para rollout

Se a GUI final ainda não existe, não espere o stack definitivo para validar a arquitetura.

Use um control plane HTTP mínimo como seed:

- `POST /v1/intake/upload` para arquivo;
- `POST /v1/intake/text` para texto curto;
- `POST /v1/intake/link` para links;
- `GET /v1/intake/{id}` para inspeção;
- `POST /v1/intake/{id}/promote` para promoção explícita.

Esse server não decide semântica. Ele só recebe, normaliza metadata e invoca a tool de intake.

Regra importante: GUI, bot, webhook ou gateway não devem chamar `intake_ingest.py` diretamente. O canal fala HTTP com o control plane; o control plane fala com a tool cognitiva.

Para MVP, uma implementação stdlib/local sem dependência nova obrigatória é aceitável. Se o projeto evoluir para FastAPI ou outro framework, preserve o contrato externo do `IntakeEnvelope` e dos endpoints.

## Canais prioritários

Para adoção com menor atrito:

1. Telegram como superfície espontânea do executivo.
2. GUI web com dropzone para upload formal, desktop e lote.

Depois expandir para WhatsApp, email forward, webhook e API.

## Fluxo padrão

### 1. Recepção

Receber o arquivo, áudio, imagem, ZIP, link ou lote via canal disponível.

Persistir imediatamente em `_inbox/{intake_id}/original/`.

### 2. Manifesto inicial

Criar `manifest.json` com:

- metadados do envelope;
- hash SHA-256 do original quando aplicável;
- tamanho;
- MIME;
- status inicial `received`.

### 3. Extração por tipo

Aplicar o trilho certo:

- áudio/voz -> transcrição + resumo curto;
- PDF/doc -> extração para Markdown; OCR se escaneado;
- imagem -> OCR + descrição visual quando necessário;
- ZIP -> inventário do conteúdo, sem promoção automática;
- link -> metadados, snapshot textual e resolução com conector quando fizer sentido.

Sempre preservar o original.

### 4. Triagem cognitiva

Gerar uma hipótese útil, não uma taxonomia burocrática.

Responder em linguagem simples:

- o que chegou;
- o que foi extraído;
- o que parece ser;
- qual microverso/diretório/ação faz mais sentido.

Exemplo:

```text
Recebi 1 PDF. Parece ser um plano de ensino.
Extraí 12 páginas.
Sugestão:
- microverso: ensino
- destino provável: knowledge/ ou contracts/
- próxima ação: resumir, arquivar bruto, ou promover para página semântica
```

### 5. Promoção

Escolher um destes destinos:

1. ficar apenas em `_inbox/` como referência operacional;
2. virar página semântica no Acervo;
3. virar tarefa acionável;
4. virar artefato derivado no `personal-artifact-workspace`.

Não presuma que todo intake vira conhecimento.

## Heurística de UX

Evite pedir taxonomia antes do upload.

A UX correta é:

1. gesto natural do usuário — mandar arquivo, áudio, foto, link;
2. confirmação curta — recebi, extraí, isso parece X;
3. proposta de destino — quer que eu promova para Y ou deixe na inbox?

Primeiro curadoria assistida. Depois automação.

## Voice-first

Áudio não é exceção; é canal de primeira classe.

O intake deve acomodar:

- mensagem de voz curta;
- áudio longo com transcrição;
- áudio acompanhado de arquivo ou foto;
- fala que explica o contexto do anexo.

Quando houver áudio + anexo, trate os dois como partes do mesmo intake quando a correlação for clara.

## Doc-first extraction

Para documentos, prefira uma rota de extração para Markdown limpo. O objetivo é tornar o conteúdo legível e promotável, não apenas armazenar o binário.

Se houver stack local como markitdown, liteparse, OCR ou pipeline similar, encaixe-a aqui. A lição durável é a etapa de extração; não a ferramenta específica.

### Engine documental vs wiki própria

Quando o intake usar um projeto legado que também gera wiki própria, não assuma que a wiki desse projeto deve virar o centro arquitetural. No Exocórtex, a wiki/acervo semântico já existe. Prefira primeiro um modo de somente processamento, mantendo a projeção wiki como opcional, se o atrito for baixo.

Regra prática:

1. Preservar o projeto único quando `process-only` puder ser adicionado sem fork.
2. Separar o contrato de engine (`DocumentParseResult`, job status, artifacts, lineage) da projeção wiki (`WikiPageDraft`, markdown, index local).
3. Manter a wiki do processador como consumer downstream, não como output primário do intake server.
4. Só considerar fork quando a wiki estiver tão acoplada que bloquear contrato, idempotência ou observabilidade.

Para páginas web, trate `browser-use` como trilho semântico para páginas dinâmicas, consent banners, navegação interativa e extração que exige raciocínio. Use Playwright vanilla para renderização determinística sem tokens, e urllib/fetch para páginas simples. O modo `auto` deve ser uma política de escalada explícita, não um fallback opaco.

## Relação com o Acervo

Use `acervo-manager` para promoção semântica.

A promoção deve responder explicitamente:

- isso tem valor cognitivo durável?
- qual escopo: micro, global ou shared?
- qual diretório funcional: knowledge, contracts, context, decisions, reflections, tools, workflows?
- qual Nature e `kind`?

Sem essa resposta, o material fica em `_inbox/`.

## Relação com publicação

Drive, Docs, OneDrive ou equivalentes não são a inbox primária do Exocórtex.

Eles são melhores como workspace do usuário e superfície de publicação. Quando o material ingerido virar saída final, encaminhe para `personal-artifact-workspace`.

## Pitfalls

1. Jogar arquivo bruto direto no Acervo semântico.
2. Obrigar o usuário a escolher microverso, pasta e natureza no momento do upload.
3. Acoplar workflow ao canal. Telegram e GUI devem convergir para o mesmo envelope.
4. Tratar Drive como inbox cognitiva principal.
5. Promover ZIP automaticamente sem inventário e triagem.
6. Perder o original após OCR/transcrição.
7. Tratar toda ingestão como conhecimento, em vez de considerar tarefa, referência operacional ou artefato derivado.
8. Colocar responsabilidade de recepção binária complexa dentro do Hermes quando a arquitetura já prevê SERVER intermediário.
9. Deixar GUI ou bot chamar a tool cognitiva diretamente, pulando a camada de server/control plane.
10. Quebrar o contrato HTTP no momento de migrar de MVP local para framework web; trocar a implementação é aceitável, trocar o contrato sem necessidade é regressão.

## Checklist de verificação

- [ ] Existe `_inbox/` autocontida e separada do Acervo semântico.
- [ ] Cada intake tem manifesto, hash, MIME, tamanho e status.
- [ ] O original foi preservado.
- [ ] A extração gerou texto utilizável quando aplicável.
- [ ] A resposta ao usuário foi curta e orientada a decisão.
- [ ] A sugestão de destino não exigiu taxonomia antecipada do usuário.
- [ ] A promoção para o Acervo só ocorreu após triagem.
- [ ] O material que virou saída final foi encaminhado para `personal-artifact-workspace`.

## Reprodutibilidade

Toda implementação replicável deve conter:

- contrato do `_inbox/`;
- schema do `IntakeEnvelope`;
- manifesto mínimo;
- trilhos de extração por tipo;
- regra de triagem antes de promoção;
- separação explícita entre canal, server e Hermes.

## Support files

- `references/session-2026-05-30-intake-path.md` — desenho consolidado do caminho de ingestão amigável e multicanal, com a simetria `_inbox` vs `_artifacts`, prioridades de canal e trade-offs arquiteturais.
- `references/replication-checklist.md` — checklist mínimo para portar a capability de intake para outro Exocórtex-Hermes.
- `references/multichannel-intake-contract-and-rollout.md` — contrato canônico do `IntakeEnvelope`, shape do `_inbox`, ordem de rollout e baseline da implementação v1.
- `references/intake-control-plane-seed.md` — seed prático de control plane HTTP entre GUI/gateway e `intake_ingest.py`, com endpoints mínimos e ordem de rollout.
- `references/docbrain-processing-engine-mode.md` — padrão para adaptar processadores documentais legados com wiki própria: preferir modo `process-only`, contrato `DocumentParseResult`, projeções downstream, idempotência por hash como próximo endurecimento e política web incluindo `browser-use`.
