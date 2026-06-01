---
name: exocortex-tool-governance
description: Regras de governança para uso de tools pelo Exocórtex.IA. Define quando e como tools devem ser usadas, logging obrigatório, e classificação por tipo.
version: 1.1.0
category: exocortex
metadata:
  hermes:
    tags: [exocortex, governance, tools, policy]
---

# Tool Governance — Exocórtex.IA

> Controla COMO e QUANDO o agente usa ferramentas externas.

## Classificação de Tools

| Tipo | Exemplos | Política |
|---|---|---|
| **Internos** | file_read, file_write, terminal, hermes-cli | Uso livre. Logar apenas em ações destrutivas (delete, overwrite). |
| **Pesquisa** | duckduckgo-search, browser-use, arxiv | Uso livre. Logar query + nº de resultados. |
| **Comunicação** | email, messaging | **Draft-First obrigatório.** Jamais enviar sem aprovação. |
| **Agenda (calendar)** | consultar, criar, alterar, remover eventos | Execução permitida quando houver gatilho explícito do executivo (ex.: "atualizar compromisso") ou comando direto de agenda; registrar ação e resultado. |
| **Criação externa** | Google Docs, Drive, compartilhamentos | **Draft-First obrigatório.** Criar como rascunho local primeiro. Upload final de artefato exige path de destino resolvido (nunca raiz). |
| **Configuração** | hermes skills install, pip install, mcp add | **Aprovação obrigatória.** Logar no session log. Atualizar setup.sh. |

## Regras de Uso

### R1: Princípio do Menor Privilégio
Usar a tool mais simples que resolve o problema.
- Precisa de dados? → `file_read` antes de `web_search`
- Precisa de busca? → `duckduckgo-search` antes de `browser-use`
- Precisa de browser? → `browser-use` CLI antes do modo agente

### R2: Logging Obrigatório
Toda tool call que modifique estado externo DEVE ser logada:
```
[TOOL] {timestamp} | {tool_name} | {action} | {target} | {result}
```

### R3: Draft-First para Comunicações
Tools de comunicação (email, messaging) NUNCA executam diretamente.
Fluxo:
1. Gerar rascunho localmente
2. Apresentar ao executivo
3. Executivo aprova → executar
4. Executivo rejeita → descartar ou revisar

**Exceção governada — Agenda (calendar):**
- Alterações de eventos podem executar direto quando houver gatilho explícito do executivo (ex.: "atualizar compromisso") ou instrução inequívoca de agenda.
- Antes de mutar: localizar o evento correto e validar data/horário alvo.
- Depois de mutar: confirmar resultado com ID, horário final e status.

### R4: Sandbox por Microverso
Quando operando dentro de um microverso, tools devem respeitar o escopo:
- Buscas no acervo: restringir ao microverso ativo (a menos que cross-domain seja explícito)
- File writes: restringir ao path do microverso ativo
- Exceção: skills de meta-gestão (acervo-manager) podem operar cross-microverso

### R5: Failsafe — Sem Mutação Silenciosa
Se uma tool falhar, o agente DEVE:
1. Reportar a falha ao executivo
2. Nunca tentar auto-reparar com outra tool sem informar
3. Sugerir alternativas

### R6: Publicação no Drive com parent obrigatório
Para artefato final do Exocórtex:
1. Resolver `drive_target.folder_path` antes do upload
2. Publicar com parent explícito (pasta final)
3. Gravar receipt com `folder_id` e `web_view_link`
4. Upload na raiz do Drive é falha de governança e deve ser corrigido (mover/republicar + registrar)

### R7: Knowledge Intake via NotebookLM (CLI-first)
Quando a tarefa for de aprendizado/síntese de conhecimento:
1. Sugerir NotebookLM como rota padrão
2. Priorizar `nlm` CLI; usar MCP (`notebooklm-mcp`) como fallback
3. Sem fontes fornecidas: buscar e adicionar as 10 melhores fontes
4. Se não for resolvível por fonte documental: adicionar fonte via deep research; fallback web search
5. Sempre registrar fontes usadas na entrega

### R8: Operações básicas de agenda para automação
Operações suportadas por padrão no Exocórtex:
1. **Listar agenda** em janela de tempo (hoje, semana, intervalo ISO)
2. **Buscar compromisso** por título aproximado + faixa de horário
3. **Criar compromisso** com timezone explícito e duração definida
4. **Atualizar compromisso** (horário, título, local, descrição)
5. **Remover compromisso** com confirmação explícita do executivo

Regras de robustez:
- Resolver conflitos por heurística: mesmo título + mesma data + menor distância de horário.
- Em ambiguidade (2+ candidatos fortes), pedir desambiguação curta.
- Registrar sempre: `event_id`, operação, antes/depois, status final.

## Whitelist Padrão

Skills do bundle `exocortex-alpha` são pré-autorizadas.
Qualquer skill fora do bundle requer menção explícita do executivo.

## Blacklist

| Tool/Ação | Motivo |
|---|---|
| `rm -rf` em qualquer path | Destruição irreversível |
| Envio direto de email/mensagem | Viola Draft-First |
| Instalação de packages do sistema (`apt`, `brew`) | Requer aprovação manual |
| Acesso a dados de outros tenants | Violação de isolamento |
