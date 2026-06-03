# Brainstorm profundo — edição humana de drafts com Hermes remoto

Contexto: Exocórtex roda em servidor remoto. O usuário precisa editar drafts em interfaces conhecidas. O sistema deve manter persistência e coerência entre a versão canônica do Exocórtex e o documento manipulado. Hoje o Drive serve como plataforma de entrega, mas sem sincronização. O ideal é sincronizar apenas artefatos, não o Acervo inteiro.

## Tese curta

O melhor caminho não é sincronizar pasta. É criar um ciclo de artefato vivo:

Exocórtex gera draft local canônico -> publica uma superfície editável conhecida -> usuário edita -> servidor recebe sinal de mudança -> Exocórtex importa somente aquele artefato -> calcula diferença -> atualiza fonte/manifesto/receipt -> mantém vínculo de versão.

A escolha mais prática para MVP é Google Docs como superfície humana e Markdown local como fonte canônica, com manifesto ligando:

- artifact_id local;
- drive_file_id / doc_id;
- revision_id ou modifiedTime;
- hash do snapshot exportado;
- estado do ciclo: draft, human_editing, review_ready, accepted, archived;
- política de merge: overwrite, patch, sections, manual_review.

## Princípios de arquitetura

1. Acervo continua canônico para memória e reprodutibilidade.
2. Drive/Docs vira superfície de edição, não fonte global do Exocórtex.
3. Sincronização é por artefato, nunca por árvore inteira.
4. O usuário edita em ferramenta conhecida: Google Docs, Drive, VS Code remoto, OnlyOffice/Collabora ou web editor próprio.
5. Toda ida para fora preserva Draft-First: criar documento privado pode ser execução; compartilhar/publicar continua exigindo aprovação.
6. Cada alteração humana gera evento de ingestão, não substituição cega.
7. Merge automático só em regiões controladas; mudanças estruturais entram em revisão.

## Modelo de dados mínimo

Criar `sync.json` dentro de cada pacote de artefato:

```json
{
  "artifact_id": "art_YYYYMMDD_HHMMSS_slug",
  "local_source": "source/source.md",
  "surface": {
    "provider": "google_docs",
    "drive_file_id": "...",
    "doc_id": "...",
    "web_view_link": "...",
    "folder_path": "exocortex/inbox"
  },
  "state": "human_editing",
  "version": {
    "local_hash": "sha256...",
    "remote_revision_id": "...",
    "remote_modified_time": "...",
    "last_imported_revision_id": "..."
  },
  "merge_policy": "manual_review",
  "sections": [
    {
      "id": "intro",
      "title": "Introdução",
      "local_anchor": "<!-- exo:section:intro -->",
      "remote_named_range": "exo_section_intro"
    }
  ]
}
```

## Opção 1 — Google Docs como editor humano, Exocórtex como sincronizador de artefato

Fluxo:

1. Exocórtex cria `source/source.md` local.
2. Converte para Google Docs ou cria Doc via Docs API.
3. Insere metadados discretos: título, artifact_id, estado, talvez um bloco final “Notas para o Exocórtex”.
4. Entrega link privado: “Aqui está o documento. Edite se necessário. Quando terminar, responda ‘importar alterações’ ou clique em botão/atalho futuro.”
5. Exocórtex monitora Drive changes/watch ou faz polling sob demanda.
6. Ao detectar mudança, exporta o Doc para texto/Markdown, calcula diff contra `source/source.md` e gera `source/source.human.md` ou patch.
7. Se o diff for limpo, atualiza fonte canônica. Se houver conflito, apresenta revisão.

Pontos fortes:

- Interface já conhecida.
- Edição mobile funciona.
- Google Docs já resolve colaboração concorrente via OT.
- Histórico de versão e comentários ficam no ecossistema do usuário.
- Não exige instalar nada no computador do usuário.

Pontos fracos:

- Conversão Markdown <-> Google Docs perde detalhes se o documento tiver layout complexo.
- Docs API edita por índices, o que exige cuidado.
- Comentários/sugestões do Google Docs podem não ser triviais de importar pelo wrapper atual.

Uso recomendado:

- Textos, ofícios, relatórios, planos, roteiros, e-mails longos.
- Artefatos onde a substância textual importa mais que layout pixel-perfect.

MVP:

- Sem webhook inicialmente.
- Comando “importar alterações do doc X”.
- Export Doc -> text/plain ou Markdown aproximado.
- Gerar diff e pedir aceite.

Evolução:

- Drive `changes.watch` + `changes.list` para evento de alteração.
- `sync.json` por artefato.
- Named ranges por seção para merges parciais.
- Receipts com revision_id.

## Opção 2 — Google Docs com seções ancoradas e merge controlado

Fluxo:

1. O documento nasce de template com marcadores `{{section_intro}}`, `{{section_contexto}}` ou named ranges.
2. O Exocórtex só escreve dentro de regiões marcadas.
3. O usuário pode editar livremente fora dessas regiões.
4. Na importação, o Exocórtex compara seção por seção.
5. O merge automático só ocorre se a seção mantiver âncora reconhecível.

Pontos fortes:

- Evita sobrescrever observações do usuário.
- Permite “atualize só a agenda”, “regenere só conclusão”, “preserve minhas notas”.
- Bom para documentos com estrutura previsível.

Pontos fracos:

- Exige disciplina de template.
- Se o usuário apagar âncoras, o sistema cai para revisão manual.

Uso recomendado:

- Ofícios, planos de aula, atas, relatórios padronizados, documentos institucionais.

## Opção 3 — Drive como pasta de artefatos editáveis, sem Docs API profunda

Fluxo:

1. Exocórtex publica `source.md`, `source.docx` ou `draft.md` em `exocortex/{microverso}/drafts`.
2. Usuário edita o arquivo no Drive usando Google Docs, Word online ou editor local sincronizado pelo Drive Desktop.
3. Exocórtex baixa apenas aquele arquivo quando solicitado.
4. Usa hash + modifiedTime + revision para detectar mudança.

Pontos fortes:

- Mais simples que Docs API estruturada.
- Funciona com DOCX, MD, PDF anotado, CSV.
- Mantém o modelo atual de artifact workspace.

Pontos fracos:

- Sem sincronização fina.
- Conversão pode gerar ruído.
- Conflitos precisam de revisão manual.

Uso recomendado:

- MVP rápido.
- Usuários que só precisam editar e devolver.

## Opção 4 — “Inbox de revisões”: usuário devolve o arquivo editado

Fluxo:

1. Exocórtex entrega draft em Drive.
2. Usuário edita onde quiser.
3. Usuário envia o arquivo revisado por upload, Drive, Telegram ou formulário.
4. Exocórtex trata como nova entrada: `source/revisions/user_YYYYMMDD.ext`.
5. Exocórtex calcula diff e cria `source/source.accepted.md`.

Pontos fortes:

- Robusto e independente de API de edição.
- Funciona com qualquer formato.
- Bom para usuários não técnicos.

Pontos fracos:

- Não é sincronização, é ingestão de revisão.
- Mais manual.
- Menos elegante.

Uso recomendado:

- Fallback universal.
- Ambientes com OAuth instável ou política restritiva.

## Opção 5 — Editor web próprio do Exocórtex com Monaco/TipTap/ProseMirror

Fluxo:

1. Server expõe link autenticado para editar draft.
2. Editor web carrega `source/source.md` ou estrutura JSON.
3. Usuário edita no navegador.
4. Salvar grava direto no artefato local do servidor.
5. Exocórtex atualiza manifesto e versões.

Pontos fortes:

- Coerência máxima: não há conversão externa.
- Controle total de metadados, seções, versão, diff, autosave.
- Pode mostrar painel lateral: “o que o Exocórtex entendeu”, “alterações pendentes”, “aplicar estilo”.

Pontos fracos:

- Exige produto próprio.
- Menos familiar que Google Docs.
- Precisa autenticação, permissão, backups e UX.

Uso recomendado:

- Produto Exocórtex.SaaS no médio prazo.
- Quando o artefato precisa preservar estrutura interna mais que experiência Google.

Decisão técnica:

- TipTap/ProseMirror se o documento é rico e semântico.
- Monaco se o draft é Markdown/código/configuração.
- Yjs se quiser edição colaborativa real-time com CRDT.

## Opção 6 — VS Code remoto / code-server para usuários técnicos

Fluxo:

1. Exocórtex cria workspace por usuário/artefato.
2. Usuário abre code-server no navegador.
3. Edita Markdown, JSON, HTML, slides etc.
4. Git ou snapshots locais registram tudo.
5. Exocórtex importa direto dos arquivos.

Pontos fortes:

- Excelente para usuário técnico.
- Mantém fonte real, sem conversão.
- Bom para slides HTML, Markdown, scripts, dados.

Pontos fracos:

- Não serve para usuário leigo.
- UX menos institucional.
- Requer isolamento por usuário.

Uso recomendado:

- Elder e usuários power-user.
- Artefatos técnicos e visuais.

## Opção 7 — OnlyOffice/Collabora self-hosted como editor de DOCX/ODT

Fluxo:

1. Exocórtex gera DOCX/ODT.
2. Usuário edita em OnlyOffice/Collabora no navegador.
3. Servidor recebe callback de salvamento.
4. Exocórtex baixa versão final e converte para Markdown/HTML se necessário.

Pontos fortes:

- Interface parecida com Word.
- Self-hosted, sem depender do Google.
- Callbacks de edição já existem no modelo desses editores.

Pontos fracos:

- Operação mais pesada.
- Menos integrado ao Drive atual.
- Conversão ainda existe.

Uso recomendado:

- Instalações institucionais ou usuários que não querem Google.

## Opção 8 — Git como camada de verdade para drafts técnicos

Fluxo:

1. Cada artefato vivo vira branch ou commit local.
2. Usuário edita por web editor, VS Code, GitHub Codespaces ou GitHub web editor.
3. Exocórtex compara commits.
4. Aceite de revisão vira merge interno.

Pontos fortes:

- Versionamento forte.
- Diff excelente.
- Reversibilidade real.

Pontos fracos:

- Não serve para usuário comum.
- GitHub externo exige Draft-First para push/PR público/privado fora do ambiente local.

Uso recomendado:

- Código, templates, decks HTML, materiais versionáveis.

## Opção 9 — Comentários/comandos no próprio documento

Fluxo:

O usuário edita o Doc e escreve comandos em blocos especiais:

```text
[EXO]
Reescreva esta seção com tom mais institucional.
Preserve os três exemplos.
[/EXO]
```

Ou usa comentários do Google Docs, quando a API suportar leitura adequada.

Pontos fortes:

- UX natural: o usuário conversa com o Exocórtex dentro do draft.
- Mantém contexto local da edição.
- Reduz troca de chat.

Pontos fracos:

- Comentários têm API/permissionamento mais delicado.
- Blocos de comando podem poluir o texto se não forem removidos.

Uso recomendado:

- Segunda fase do Google Docs MVP.

## Arquitetura recomendada em camadas

### Camada 1 — Artefato local canônico

`~/.hermes/acervo/_artifacts/{artifact_id}` continua sendo a unidade operacional.

Adicionar:

- `sync.json`;
- `source/revisions/`;
- `source/source.remote.md`;
- `diffs/`;
- `locks/` ou campo `state`.

### Camada 2 — Superfície externa editável

Inicial: Google Docs privado no Drive.

Futuro:

- editor web próprio;
- code-server para técnico;
- OnlyOffice/Collabora para self-hosted.

### Camada 3 — Watcher/sync

Inicial:

- sync sob demanda: “importar alterações”.

Depois:

- Drive `changes.watch` para webhook;
- `changes.list` com `pageToken` guardado;
- renovar canais expirados;
- filtrar somente `drive_file_id` registrado em `sync.json`.

### Camada 4 — Motor de diff/merge

Políticas:

- `manual_review`: sempre gerar diff e aguardar aceite.
- `safe_overwrite`: para artefato simples onde usuário aceita que Docs vire fonte.
- `section_merge`: merge por âncoras/seções.
- `append_notes`: importar só bloco “Notas do usuário”.

### Camada 5 — Atualização do Acervo

Somente após aceite:

- atualizar `source/source.md`;
- recalcular hash;
- registrar revisão no manifesto;
- gravar decisão se houver valor cognitivo;
- atualizar página semântica do microverso se o artefato tiver valor permanente.

## Fluxo ideal para o usuário

Exocórtex:

“Aqui está o documento: [link privado do Google Docs]. Edite se necessário. Quando terminar, diga: importar alterações.”

Usuário edita.

Usuário:

“importar alterações”

Exocórtex:

1. baixa versão atual;
2. mostra resumo das mudanças;
3. apresenta diff ou seções alteradas;
4. pergunta: “aceitar como nova fonte canônica?”;
5. após aprovação, atualiza o pacote local.

## Estados do artefato

- `draft_local`: gerado, ainda não entregue.
- `sent_for_editing`: documento externo criado.
- `human_editing`: aguardando edição.
- `remote_changed`: mudança detectada.
- `imported_pending_review`: mudanças importadas, aguardando aceite.
- `accepted_canonical`: fonte local atualizada.
- `published`: export final publicado/entregue.
- `archived`: ciclo fechado.

## Regras de conflito

1. Se local mudou depois da última exportação e remoto também mudou: conflito.
2. Se remoto mudou só em seções não controladas: importar como revisão humana.
3. Se remoto removeu âncoras: revisão manual.
4. Se Exocórtex precisa regenerar conteúdo enquanto humano edita: criar sugestão em seção separada, não sobrescrever.
5. Se usuário edita documento publicado: abrir novo ciclo, não alterar publicação antiga sem receipt novo.

## Melhor combinação prática

### MVP de 2 a 4 dias

- Google Docs privado como editor.
- `sync.json` por artefato.
- export/import sob demanda.
- diff textual.
- aceite manual para atualizar fonte canônica.
- receipt com doc_id, modifiedTime e hash.

### Versão 1

- Drive `changes.watch` + `changes.list`.
- estado `remote_changed` automático.
- seção “Notas para o Exocórtex”.
- snapshots em `source/revisions/`.

### Versão 2

- named ranges ou âncoras por seção.
- merge parcial.
- comandos `[EXO]...[/EXO]` no documento.
- resumo automático das mudanças humanas.

### Versão 3

- editor web próprio para artefatos ricos.
- Yjs/CRDT se precisar colaboração real-time fora do Google Docs.
- painel de coerência: “Doc externo x fonte canônica x última publicação”.

## Recomendação final

Começar com Google Docs, mas tratar Docs como superfície de edição, não como fonte absoluta. O Exocórtex deve manter o artifact package como unidade de verdade e aceitar mudanças humanas por importação versionada.

Implementar primeiro:

1. `sync.json` no Personal Artifact Workspace.
2. `artifact_edit publish-doc` para criar Google Doc privado.
3. `artifact_edit import-doc` para exportar, diffar e criar revisão pendente.
4. `artifact_edit accept` para promover revisão humana a fonte canônica.
5. `manifest.json` com estado de sincronização.

A sincronização por webhook entra depois. Ela melhora UX, mas não é pré-requisito para coerência. O pré-requisito é vínculo de versão entre `artifact_id`, `doc_id`, `revision/modifiedTime` e `local_hash`.

## Fontes consultadas

- NotebookLM: notebook “O Exocórtex.IA: Um Exoesqueleto para o Pensamento” — princípios de autoria, persistência, acervo, validação humana e separação rascunho/publicação.
- NotebookLM research notebook “Exocortex Remote Draft Editing Sync Options”.
- Google Drive API: Retrieve changes.
- Google Drive API: Push notifications for resource changes.
- Google Drive API: Manage file revisions.
- Google Docs API: Overview, named ranges, indexes.
- Google Docs API: Merge text into a document.
- Operational Transformation: consistência em edição colaborativa.
- CRDT: convergência eventual para estruturas replicadas.

Observação: Context7 não está exposto como ferramenta neste runtime. Usei NotebookLM, skills internas, busca no Acervo e fontes oficiais via NotebookLM.
