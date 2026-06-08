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
| **Entrega ao executivo** | `send_message` para o próprio usuário no home channel | Pode executar sem DRAFT quando for self-delivery operacional, com destinatário inequívoco e sem representar fala do executivo para terceiros. |
| **Comunicação para terceiros** | email, calendar, messaging, comentário, DM, post | **Draft-First obrigatório.** Jamais enviar sem aprovação pós-DRAFT. |
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

### R3: Governança de entrega e comunicação
Antes de usar uma tool de comunicação, classificar o ato:

1. **Self-delivery operacional**
   - Destinatário: o próprio executivo
   - Canal: home channel dele
   - Natureza: entrega operacional do sistema, recibo, teste técnico explícito ou envio do próprio output de volta ao operador
   - Política: pode executar sem DRAFT

2. **Comunicação para terceiros**
   - Qualquer destinatário que não seja inequivocamente o próprio executivo
   - Qualquer canal compartilhado, grupo ou superfície pública
   - Qualquer texto que represente fala do executivo para terceiros
   - Política: Draft-First obrigatório

Fluxo para casos com Draft-First:
1. Gerar rascunho localmente
2. Apresentar ao executivo
3. Executivo aprova → executar
4. Executivo rejeita → descartar ou revisar

Na dúvida sobre destinatário, canal ou efeito social, tratar como comunicação para terceiros.

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

### R6: Mudanças de configuração com efeito colateral exigem ambiente isolado de validação
Quando a tarefa altera automações que chamam CLIs de configuração (`hermes config set`, setup scripts, provisionadores, roteadores de provider/model, wrappers que escrevem estado), validar em duas camadas antes de declarar pronto:

1. **Teste isolado com binário fake no PATH**
   - Criar diretório temporário.
   - Injetar um shim executável (`hermes`, ou outro CLI-alvo) no `PATH` para registrar argumentos em arquivo.
   - Rodar o script real contra esse ambiente e verificar as chamadas exatas emitidas.
   - Objetivo: provar intenção de mutação sem tocar no runtime principal.

2. **Smoke real somente leitura, quando houver fonte externa**
   - Se a lógica depende de API pública/catálogo remoto, executar um smoke contra a fonte real.
   - Preferir modo que gere relatório/artifact sem aplicar mutação real quando isso bastar para validar ranking/seleção.

3. **Cobrir fixtures + edge cases que apareceram no smoke**
   - Se o smoke revelar bug de parsing/tempo/formato, congelar isso em teste unitário imediatamente.
   - Exemplo de classe de bug: comparação entre datetime sem timezone e datetime com timezone.

4. **Só então integrar no setup/provisionamento**
   - Depois de provar o script isoladamente, plugar no `setup.sh`/provisionador e adicionar teste textual ou estrutural que confirme a chamada no fluxo de instalação.

Esse padrão é obrigatório para evitar travar ou contaminar o agente principal durante validação de automações de configuração.

## Support files

- `references/config-mutation-isolated-validation.md` — padrão de validação isolada para scripts que aplicam configuração via CLI, com shim no PATH, smoke real sem mutação e promoção imediata de bugs encontrados para testes.

## Whitelist Padrão

Skills do bundle `exocortex-alpha` são pré-autorizadas.
Qualquer skill fora do bundle requer menção explícita do executivo.

## Blacklist

| Tool/Ação | Motivo |
|---|---|
| `rm -rf` em qualquer path | Destruição irreversível |
| Envio direto de email/mensagem para terceiros sem aprovação pós-DRAFT | Viola Draft-First |
| Instalação de packages do sistema (`apt`, `brew`) | Requer aprovação manual |
| Acesso a dados de outros tenants | Violação de isolamento |
