1|---
2|name: excrtx-govern-tools
3|description: Regras de governança para uso de tools pelo Exocórtex.IA. Define quando e como tools devem ser usadas, logging obrigatório, e classificação por tipo.
4|version: 1.0.0
5|category: excrtx
6|metadata:
7|  hermes:
8|    tags: [exocortex, governance, tools, policy]
9|---
10|
11|# Tool Governance — Exocórtex.IA
12|
13|> Controla COMO e QUANDO o agente usa ferramentas externas.
14|
15|## Classificação de Tools
16|
17|| Tipo | Exemplos | Política |
18||---|---|---|
19|| **Internos** | file_read, file_write, terminal, hermes-cli | Uso livre. Logar apenas em ações destrutivas (delete, overwrite). |
20|| **Pesquisa** | duckduckgo-search, excrtx-integrate-browser, arxiv | Uso livre. Logar query + nº de resultados. |
21|| **Entrega ao executivo** | `send_message` para o próprio usuário no home channel | Pode executar sem DRAFT quando for self-delivery operacional, com destinatário inequívoco e sem representar fala do executivo para terceiros. |
22|| **Comunicação para terceiros** | email, calendar, messaging, comentário, DM, post | **Draft-First obrigatório.** Jamais enviar sem aprovação pós-DRAFT. |
23|| **Criação externa** | Google Docs, Drive, compartilhamentos | **Draft-First obrigatório.** Criar como rascunho local primeiro. |
24|| **Configuração** | hermes skills install, pip install, mcp add | **Aprovação obrigatória.** Logar no session log. Atualizar setup.sh. |
25|
26|## Regras de Uso
27|
28|### R1: Princípio do Menor Privilégio
29|Usar a tool mais simples que resolve o problema.
30|- Precisa de dados? → `file_read` antes de `web_search`
31|- Precisa de busca? → `duckduckgo-search` antes de `excrtx-integrate-browser`
32|- Precisa de browser? → `excrtx-integrate-browser` CLI antes do modo agente
33|
34|### R2: Logging Obrigatório
35|Toda tool call que modifique estado externo DEVE ser logada:
36|```
37|[TOOL] {timestamp} | {tool_name} | {action} | {target} | {result}
38|```
39|
40|### R3: Governança de entrega e comunicação
41|Antes de usar uma tool de comunicação, classificar o ato:
42|
43|1. **Self-delivery operacional**
44|   - Destinatário: o próprio executivo
45|   - Canal: home channel dele
46|   - Natureza: entrega operacional do sistema, recibo, teste técnico explícito ou envio do próprio output de volta ao operador
47|   - Política: pode executar sem DRAFT
48|
49|2. **Comunicação para terceiros**
50|   - Qualquer destinatário que não seja inequivocamente o próprio executivo
51|   - Qualquer canal compartilhado, grupo ou superfície pública
52|   - Qualquer texto que represente fala do executivo para terceiros
53|   - Política: Draft-First obrigatório
54|
55|Fluxo para casos com Draft-First:
56|1. Gerar rascunho localmente
57|2. Apresentar ao executivo
58|3. Executivo aprova → executar
59|4. Executivo rejeita → descartar ou revisar
60|
61|Na dúvida sobre destinatário, canal ou efeito social, tratar como comunicação para terceiros.
62|
63|### R4: Sandbox por Microverso
64|Quando operando dentro de um microverso, tools devem respeitar o escopo:
65|- Buscas no acervo: restringir ao microverso ativo (a menos que cross-domain seja explícito)
66|- File writes: restringir ao path do microverso ativo
67|- Exceção: skills de meta-gestão (excrtx-memory-manager) podem operar cross-microverso
68|
69|### R5: Failsafe — Sem Mutação Silenciosa
70|Se uma tool falhar, o agente DEVE:
71|1. Reportar a falha ao executivo
72|2. Nunca tentar auto-reparar com outra tool sem informar
73|3. Sugerir alternativas
74|
75|### R6: Mudanças de configuração com efeito colateral exigem ambiente isolado de validação
76|Quando a tarefa altera automações que chamam CLIs de configuração (`hermes config set`, setup scripts, provisionadores, roteadores de provider/model, wrappers que escrevem estado), validar em duas camadas antes de declarar pronto:
77|
78|1. **Teste isolado com binário fake no PATH**
79|   - Criar diretório temporário.
80|   - Injetar um shim executável (`hermes`, ou outro CLI-alvo) no `PATH` para registrar argumentos em arquivo.
81|   - Rodar o script real contra esse ambiente e verificar as chamadas exatas emitidas.
82|   - Objetivo: provar intenção de mutação sem tocar no runtime principal.
83|
84|2. **Smoke real somente leitura, quando houver fonte externa**
85|   - Se a lógica depende de API pública/catálogo remoto, executar um smoke contra a fonte real.
86|   - Preferir modo que gere relatório/artifact sem aplicar mutação real quando isso bastar para validar ranking/seleção.
87|
88|3. **Cobrir fixtures + edge cases que apareceram no smoke**
89|   - Se o smoke revelar bug de parsing/tempo/formato, congelar isso em teste unitário imediatamente.
90|   - Exemplo de classe de bug: comparação entre datetime sem timezone e datetime com timezone.
91|
92|4. **Só então integrar no setup/provisionamento**
93|   - Depois de provar o script isoladamente, plugar no `setup.sh`/provisionador e adicionar teste textual ou estrutural que confirme a chamada no fluxo de instalação.
94|
95|Esse padrão é obrigatório para evitar travar ou contaminar o agente principal durante validação de automações de configuração.
96|
97|## Support files
98|
99|- `references/config-mutation-isolated-validation.md` — padrão de validação isolada para scripts que aplicam configuração via CLI, com shim no PATH, smoke real sem mutação e promoção imediata de bugs encontrados para testes.
100|
101|## Whitelist Padrão
102|
103|Skills do bundle `exocortex-alpha` são pré-autorizadas.
104|Qualquer skill fora do bundle requer menção explícita do executivo.
105|
106|## Blacklist
107|
108|| Tool/Ação | Motivo |
109||---|---|
110|| `rm -rf` em qualquer path | Destruição irreversível |
111|| Envio direto de email/mensagem para terceiros sem aprovação pós-DRAFT | Viola Draft-First |
112|| Instalação de packages do sistema (`apt`, `brew`) | Requer aprovação manual |
113|| Acesso a dados de outros tenants | Violação de isolamento |
114|