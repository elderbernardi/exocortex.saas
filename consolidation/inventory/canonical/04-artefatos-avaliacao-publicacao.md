---
title: Harness Exocórtex v0.4 — Artefatos, Avaliação e Publicação
created: 2026-06-02
updated: 2026-06-02
nature: conhecimento
kind: concept
scope_mode: micro
scope_slug: harness-project
applies_to: [hermes-setup, acervo-cognitivo, exocortex-saas]
authority: canonical
operational_mode: advisory
stability: experimental
sources:
  - conversa executiva 2026-06-02 sobre harness Exocórtex/Hermes
derived_from: []
confidence: high
promotion_policy: candidate-shared
upstream:
  source_skill: null
  assumed_version: null
  coupling: none
tags: ["exocortex", "harness", "architecture", "v0.4"]
---

# 4. Artefatos, avaliação e publicação

## 4.1 Ciclo de vida do artefato

```text
draft → ready → approved → ask-publication → published → archived
                     ↘ failed
```

- **draft**: em construção.
- **ready**: completo e passou por Quality Gate.
- **approved**: usuário aprovou conteúdo.
- **ask-publication**: Exocórtex pergunta se o usuário deseja publicar.
- **published**: export entregue/publicado e receipt salvo.
- **failed**: export/publicação falhou, com receipt de falha.
- **archived**: preservado sem ação ativa.

## 4.2 Quality Gate vs Avaliação

### Quality Gate

Verifica piso mínimo:

- requisitos atendidos;
- formato correto;
- fontes/execução verificáveis;
- links e paths válidos;
- hash/tamanho/MIME para exports;
- segurança e Draft-First respeitados;
- ausência de slop grosseiro;
- metadados essenciais presentes.


Skills existentes a aplicar conforme o tipo de artefato:

- `exocortex-output-quality-gate`: gate geral de completude e aderência.
- `exocortex-draft-first`: bloqueio/aprovação para ação externa.
- `stop-slop`: prosa final sem vícios de escrita artificial.
- `personal-artifact-workspace`: pacote, manifesto, exports, receipts e publicação.
- `exocortex-canvas`: Canvas, vetor, tarefa dominante e avaliação requerida.
- `acervo-manager`: persistência correta no Acervo.
- `google-workspace`: publicação privada Drive/Gmail quando aprovada.
- `taste-skill` / `exocortex-design-system`: artefatos visuais quando aplicável.
- `powerpoint`, `exocortex-slides`, `ocr-and-documents` e skills de mídia/domínio conforme o artefato.

O Quality Gate deve carregar/aplicar skills existentes antes de inventar procedimento novo.

### Avaliação por Personas

Eleva qualidade:

- clareza;
- estrutura;
- didática;
- força estratégica;
- aderência ao microverso;
- riscos e lacunas;
- voz do usuário;
- recomendações de melhoria.

A Avaliação é parte da concepção de evolução: o usuário deve sair com entregas melhores do que produziria sozinho.

## 4.3 Quando avaliar

Avaliação deve ocorrer quando:

- o Canvas marcar `evaluation.required: true`;
- houver artefato final;
- entrega for pública/institucional;
- material for didático;
- tarefa envolver decisão arquitetural;
- houver múltiplos microversos;
- usuário pedir revisão ou melhoria;
- risco de qualidade for alto.

Pode ser pulada quando:

- rascunho rápido;
- execução técnica pequena;
- resposta simples;
- usuário pedir velocidade explicitamente;
- artefato for descartável.

## 4.4 Personas avaliadoras

- **Crítico**: falhas, premissas frágeis, riscos e inconsistências.
- **Professor**: clareza didática, progressão conceitual, exemplos, aprendizado.
- **Auditor**: consistência operacional, receipts, hashes, requisitos, rastreabilidade e aderência a contratos.
- **Cientista**: peer review epistemológico; verifica fatos, alucinações, consistência metodológica, evidência, vieses cognitivos e saltos argumentativos.
- **Editor**: linguagem, voz, acabamento e legibilidade.
- **Arquiteto**: coerência sistêmica, modularidade e encaixe no harness.
- **Estrategista**: impacto, trade-offs e direção de longo prazo.
- **Persona local do microverso**: aderência ao domínio específico.

## 4.5 Estrutura de avaliação no pacote

```text
_artifacts/items/{artifact_id}/
├── evaluations/
│   ├── critico.md
│   ├── professor.md
│   ├── auditor.md
│   ├── cientista.md
│   └── editor.md
```

Cada parecer deve conter:

```md
# Parecer — {Persona}

## Síntese

## Pontos fortes

## Fragilidades

## Recomendações prioritárias

## Sugestões opcionais

## Veredito
- aprovar
- aprovar com ajustes
- revisar antes de aprovar
```

## 4.6 Incorporação de melhorias

Modos:

- `suggest`: apenas apresenta sugestões ao usuário.
- `ask-user`: pergunta quais recomendações incorporar.
- `auto-incorporate`: incorpora melhorias não sensíveis e registra no manifesto.

Para artefatos finais, o padrão recomendado é `ask-user`, exceto para correções pequenas de clareza, typos e consistência.

## 4.7 Manifesto v0.4

```json
{
  "artifact_id": "art_YYYYMMDD_HHMMSS_slug",
  "canonical_slug": "exocortex-harness-v1",
  "friendly_name": "Harness v1 do Exocórtex",
  "publication_names": {
    "pdf": "Harness v1 do Exocórtex.pdf",
    "html": "Harness v1 do Exocórtex.html",
    "zip": "Harness v1 do Exocórtex.zip"
  },
  "title": "Harness v1 do Exocórtex",
  "status": "draft|ready|approved|published|archived|failed",
  "artifact_type": "document|report|deck|html|pdf|image|zip|code|mixed",
  "source_type": "markdown|html|pptx|xlsx|external|mixed",
  "task_id": "task_YYYYMMDD_slug",
  "primary_microverso": "harness-project",
  "related_microversos": ["hermes-setup"],
  "scope": "micro|shared|global",
  "owner": {
    "type": "task|microverso|shared",
    "id": "task_YYYYMMDD_slug"
  },
  "personas_involved": ["arquiteto", "critico", "professor", "cientista", "editor"],
  "semantic_links": [],
  "source_path": "source/source.md",
  "exports": [
    {
      "path": "exports/Harness v1 do Exocórtex.pdf",
      "kind": "pdf",
      "mime": "application/pdf",
      "sha256": "...",
      "size": 12345,
      "friendly_filename": "Harness v1 do Exocórtex.pdf"
    }
  ],
  "evaluation": {
    "status": "pending|completed|skipped",
    "personas": ["critico", "professor", "cientista", "editor"],
    "reports": ["evaluations/critico.md"],
    "incorporated_suggestions": [],
    "pending_suggestions": []
  },
  "publication": {
    "drive": {
      "status": "not_published|published|failed",
      "receipt_path": "receipts/receipt.google_drive.json"
    }
  },
  "provenance": {
    "created_by": "exocortex",
    "created_at": "ISO-8601",
    "origin": "conversation|cron|manual|import|task"
  }
}
```


## 4.8 Operações determinísticas sem LLM

Sempre que possível, tarefas de consolidação do harness devem ser movidas para scripts de skill ou ferramentas locais:

- validar JSON/YAML/frontmatter;
- calcular hashes e tamanhos;
- gerar views por microverso/tarefa/status;
- detectar artefatos sem receipt;
- detectar tarefas sem próximo passo;
- comparar hash de Canvas/tarefa para evitar retrabalho;
- listar decisões pendentes;
- montar ZIP/export.

O LLM deve ser reservado para interpretação, avaliação, síntese, decisão e redação.

## 4.9 Publicação

Quando o artefato estiver pronto/aprovado, o Exocórtex deve perguntar:

> Quer que eu publique ou entregue este artefato? Posso publicar no Drive privado, gerar ZIP local, preparar email com links/anexos, manter apenas local ou arquivar.

Regras:

- upload privado para Drive do próprio usuário pode ser execução após confirmação;
- compartilhamento externo exige Draft-First;
- link público exige aprovação explícita;
- email é opção de entrega, mas sempre comunicação externa;
- email/mensagem exige draft aprovado;
- padrão preferido: publicar no Drive privado, verificar links e preparar email com links;
- anexos diretos podem ser usados quando suportados pelo backend e aprovados pelo usuário;
- todo publish precisa de receipt, incluindo Drive file IDs e, quando enviado, Gmail message/thread ID.

## 4.10 Drive e sync

Estado v0.4:

- manter Drive como publicação expressa;
- não sincronizar `_artifacts` inteiro;
- `_inbox` pode ser pasta compartilhada/sincronizada por natureza;
- automação futura pode publicar redundância no Drive quando artefato atingir status aprovado/publicado;
- sync amplo fica pendente até haver experiência operacional suficiente.

## 4.11 Friendly names

`friendly_name` é o nome humano apresentado ao usuário. Não precisa ser slug nem path canônico.

Exemplo:

```json
{
  "artifact_id": "art_20260602_193000_exocortex-harness-v04",
  "canonical_slug": "exocortex-harness-v04",
  "friendly_name": "Arquitetura do Harness Exocórtex v0.4",
  "publication_names": {
    "md": "Arquitetura do Harness Exocórtex v0.4.md",
    "pdf": "Arquitetura do Harness Exocórtex v0.4.pdf"
  }
}
```
