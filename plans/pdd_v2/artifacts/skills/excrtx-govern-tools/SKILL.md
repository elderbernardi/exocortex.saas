---
name: excrtx-govern-tools
description: Regras de governança para uso de tools pelo Exocórtex.IA. Define quando e como tools devem ser usadas, logging obrigatório, e classificação por tipo.
version: 1.0.0
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
| **Pesquisa** | duckduckgo-search, excrtx-integrate-browser, arxiv | Uso livre. Logar query + nº de resultados. |
| **Comunicação** | email (futuro), calendar (futuro), messaging | **Draft-First obrigatório.** Jamais enviar sem aprovação. |
| **Criação externa** | Google Docs, Drive, compartilhamentos | **Draft-First obrigatório.** Criar como rascunho local primeiro. |
| **Configuração** | hermes skills install, pip install, mcp add | **Aprovação obrigatória.** Logar no session log. Atualizar setup.sh. |

## Regras de Uso

### R1: Princípio do Menor Privilégio
Usar a tool mais simples que resolve o problema.
- Precisa de dados? → `file_read` antes de `web_search`
- Precisa de busca? → `duckduckgo-search` antes de `excrtx-integrate-browser`
- Precisa de browser? → `excrtx-integrate-browser` CLI antes do modo agente

### R2: Logging Obrigatório
Toda tool call que modifique estado externo DEVE ser logada:
```
[TOOL] {timestamp} | {tool_name} | {action} | {target} | {result}
```

### R3: Draft-First para Comunicações
Tools de comunicação (email, calendar, messaging) NUNCA executam diretamente.
Fluxo:
1. Gerar rascunho localmente
2. Apresentar ao executivo
3. Executivo aprova → executar
4. Executivo rejeita → descartar ou revisar

### R4: Sandbox por Microverso
Quando operando dentro de um microverso, tools devem respeitar o escopo:
- Buscas no acervo: restringir ao microverso ativo (a menos que cross-domain seja explícito)
- File writes: restringir ao path do microverso ativo
- Exceção: skills de meta-gestão (excrtx-memory-manager) podem operar cross-microverso

### R5: Failsafe — Sem Mutação Silenciosa
Se uma tool falhar, o agente DEVE:
1. Reportar a falha ao executivo
2. Nunca tentar auto-reparar com outra tool sem informar
3. Sugerir alternativas

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
