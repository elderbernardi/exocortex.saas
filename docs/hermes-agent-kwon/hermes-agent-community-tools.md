# Relatório: addons, plugins e skills recomendados para Hermes Agent

Data da pesquisa: 26 de maio de 2026

## 1. Resumo executivo

O ecossistema do Hermes Agent ainda é jovem e cresce rápido, então a melhor estratégia para projetos gerais não é instalar tudo que aparece nos diretórios. A comunidade converge para um padrão mais conservador: manter o perfil padrão pequeno, carregar skills sob demanda, criar bundles para fluxos recorrentes e validar cada integração com um smoke test visível antes de ampliar permissões.

Para o Exocórtex.IA SaaS, a seleção mais útil é uma stack enxuta:

1. **Skills oficiais e bundles** para workflows repetíveis.
2. **Curator ou curadoria equivalente** para evitar acúmulo de skills obsoletas.
3. **Web/search e browser controlados** para pesquisa e coleta.
4. **Memória explicável** para recall auditável.
5. **Observabilidade e segurança** antes de integrações com contas reais.
6. **Workspace/dashboard** apenas quando houver necessidade operacional de acompanhar agentes, memória e sessões.

## 2. Critérios de seleção

As ferramentas abaixo foram selecionadas por sinais combinados, não por popularidade isolada:

- presença em documentação oficial, diretórios curados ou listas comunitárias;
- utilidade transversal para projetos de software, pesquisa, automação e operação;
- maturidade declarada quando disponível;
- capacidade de reduzir risco operacional, contexto carregado ou trabalho repetitivo;
- feedback recorrente em discussões do Reddit sobre o que funciona e o que cria atrito.

Sinais fracos, como estrelas de GitHub ou menções soltas em diretórios, foram tratados como indicativos de descoberta, não como prova de qualidade.

## 3. Recomendações principais

### 3.1. Sistema oficial de Skills e Skill Bundles

**Recomendação:** usar como camada base em qualquer projeto Hermes.

O Hermes trata skills como memória procedural: instruções carregadas sob demanda para tarefas específicas. A documentação oficial descreve skills como arquivos Markdown que ensinam quando usar uma capacidade, como executá-la e o que evitar. A comunidade também reforça o modelo de progressive disclosure: o agente enxerga primeiro um índice compacto, depois carrega o `SKILL.md` completo e, se necessário, arquivos específicos como referências, templates ou scripts.

**Por que usar:**

- padroniza workflows que precisam ser repetíveis;
- reduz reinvenção de procedimentos entre sessões;
- evita carregar instruções longas no prompt principal;
- permite criar bundles como `/backend-dev`, `/research-sprint` ou `/incident-response`.

**Uso recomendado para projetos gerais:**

- criar bundles por tipo de trabalho, não por ferramenta;
- manter bundles pequenos, com 2 a 4 skills realmente complementares;
- incluir no bundle uma instrução curta de precedência, por exemplo: testar primeiro, aplicar mudança pequena, verificar antes de finalizar.

**Fontes:** documentação oficial de [Skills System](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills), visão geral de [Features](https://hermes-ai.net/docs/features/) e discussão ["How Skills Work in Hermes Agent"](https://www.reddit.com/r/hermesagent/comments/1smlqdt/how_skills_work_in_hermes_agent/).

### 3.2. Curator e manutenção de skills

**Recomendação:** habilitar ou replicar a prática de curadoria desde cedo.

O Curator oficial monitora skills criadas pelo agente, acompanha uso e arquiva skills pouco utilizadas ou redundantes. A documentação oficial afirma que ele não altera skills bundled ou instaladas do hub; seu alvo são skills geradas pelo próprio loop de autoaprendizado.

Há também uma proposta comunitária relevante, `hermes-curator-evolver`, que tenta evoluir skills a partir de evidência local de sessão, com dry-run, backups e rollback. Ainda deve ser tratado como beta, mas o desenho é alinhado com uma necessidade real: manutenção baseada em evidência, não reescrita automática cega.

**Por que usar:**

- reduz duplicação e bloat de skills;
- preserva a utilidade do catálogo;
- cria uma trilha mais auditável para melhorias em workflows;
- combina bem com ambientes multiagente, onde cada agente pode gerar skills demais.

**Uso recomendado para projetos gerais:**

- manter skills oficiais/hub como base imutável ou quase imutável;
- permitir autoevolução apenas em skills locais, com backup;
- exigir revisão humana para mudanças que alterem comandos, permissões ou integrações externas.

**Fontes:** [Curator oficial](https://hermes-agent.nousresearch.com/docs/user-guide/features/curator) e post sobre [`hermes-curator-evolver`](https://www.reddit.com/r/hermesagent/comments/1t7wzy6/i_built_a_localfirst_hermes_plugin_that_evolves/).

### 3.3. Hermes Atlas e Awesome Hermes Agent

**Recomendação:** usar como diretórios de descoberta, não como lista de instalação automática.

O [Hermes Atlas](https://hermesatlas.com/) se apresenta como um mapa comunitário com mais de 100 ferramentas, skills, plugins, workspaces e integrações em 12 categorias. A lista [Awesome Hermes Agent](https://github.com/0xNyk/awesome-hermes-agent) também organiza skills, MCPs, memória, plugins e integrações.

**Por que usar:**

- acelera pesquisa de ferramentas por categoria;
- ajuda a encontrar alternativas para memória, web search, browser automation, orquestração e workspace;
- traz status como production, beta ou experimental em alguns itens.

**Cuidados:**

- diretórios comunitários podem incluir projetos com suporte superficial a Hermes;
- a própria comunidade no Reddit pediu camadas de review, ranking e validação;
- cada item deve passar por leitura de README, inspeção de permissões e smoke test local.

**Fonte:** [Hermes Atlas](https://hermesatlas.com/), [Awesome Hermes Agent](https://github.com/0xNyk/awesome-hermes-agent) e discussão sobre o [diretório comunitário no Reddit](https://www.reddit.com/r/hermesagent/comments/1t7c15v/the_hermes_agent_subreddit_community_tool/).

## 4. Ferramentas selecionadas por categoria

### 4.1. Pesquisa, browser e coleta de informação

| Ferramenta | Status prático | Uso recomendado |
| --- | --- | --- |
| `hermes-web-search-plus` | Promissor | Multi-provider search para pesquisa geral com Serper, Tavily, Exa, Querit e Perplexity. |
| `hermes-cloudflare` | Promissor | Scraping e extração via Cloudflare Browser Rendering. Útil para coleta controlada de páginas. |
| `agent-browser-mcp` | Promissor, com atenção a permissões | Controle de Chrome real via MCP, screenshots, CDP e input físico. Bom para QA visual e automação, mas deve ser isolado. |
| Skills oficiais de research/OCR/docs | Recomendado | Preferir skills oficiais para PDFs, OCR, documentos e workflows de pesquisa quando atenderem ao caso. |

**Recomendação para projetos gerais:** começar com um search provider e uma skill de documentos. Só adicionar browser real quando a tarefa exigir interação com páginas dinâmicas ou QA visual.

### 4.2. Memória e recall

| Ferramenta | Status prático | Uso recomendado |
| --- | --- | --- |
| `hindsight` | Recomendado para avaliação | Camada de memória de longo prazo com workflows de retain, recall e reflect, disponível via plugin ou MCP. |
| `yantrikdb-hermes-plugin` | Promissor | Memória Hermes-native com canonicalização, tracking de contradições e `why_retrieved`. |
| `hermes-memory-plugin` | Promissor | Banco local/embedded com BM25-first retrieval e scoring de importância. |
| `hermes-agentmemory` | Nichado | Foco em deleção real e auditoria de operações de memória. |

**Recomendação para projetos gerais:** privilegiar memória explicável. Para Exocórtex, recursos como contradições, ranking por recência e `why_retrieved` são mais importantes do que apenas armazenar mais contexto.

### 4.3. Segurança, governança e observabilidade

| Ferramenta | Status prático | Uso recomendado |
| --- | --- | --- |
| `clawshell` | Recomendado para avaliação | Camada de segurança runtime com proteção de PII e credenciais sensíveis. |
| `hermes-otel` | Promissor | Plugin de OpenTelemetry para rastrear execução, custos, latência e falhas. |
| `hermes-plugins` | Promissor | Conjunto de plugins para goal management, ponte interagente, seleção de modelo e controle de custo. |
| Curator oficial | Recomendado | Governança de skills geradas pelo agente. |

**Recomendação para projetos gerais:** instalar segurança e observabilidade antes de conectar e-mail, calendário, browser real ou contas corporativas.

### 4.4. Produtividade e workspace

| Ferramenta | Status prático | Uso recomendado |
| --- | --- | --- |
| `microsoft-workspace-skill` | Recomendado quando o cliente usa Microsoft 365 | Outlook, calendário, contatos, perfil e free/busy via Microsoft Graph, com OAuth2. |
| Skills oficiais de Google Workspace | Recomendado quando o cliente usa Google | Gmail, Calendar, Drive, Docs e Sheets via CLI ou Python, conforme catálogo oficial. |
| `hermes-workspace` | Recomendado para operação interna | GUI comunitária para chat, terminal, gerenciador de skills e visualização de memória. |
| `mission-control` | Promissor para escala | Orquestração self-hosted de tarefas, workflows multiagente e monitoramento de gasto. |

**Recomendação para projetos gerais:** usar workspace/dashboard para operadores e desenvolvedores, não necessariamente para o usuário final. No Exocórtex, o executivo deve continuar em canais de baixa fricção; dashboards servem ao time técnico e ao cockpit de aprovação.

### 4.5. Criação e melhoria de skills

| Ferramenta | Status prático | Uso recomendado |
| --- | --- | --- |
| `hermes-skill-factory` | Promissor | Converter workflows demonstrados em skills formatadas e reutilizáveis. |
| `bmad-module-skill-forge` | Promissor | Transformar repositórios e docs em skills compatíveis com agentskills.io. |
| `Agentic-MCP-Skill` | Promissor | Ponte entre MCP tool servers e o padrão de skills. |
| `hermes-agent-idea-workflow` | Beta comunitário | Pipeline de ideia para design doc, spec e handoff de implementação. |
| `hermes-agent-supwerpowers-chatgpt` | Beta comunitário | Adaptação de workflow estilo Superpowers para Hermes/ChatGPT. |

**Recomendação para projetos gerais:** usar essas ferramentas para acelerar produção de skills, mas revisar manualmente gatilhos, comandos, permissões e critérios de verificação antes de adotá-las em projetos reais.

### 4.6. Multiagente e orquestração

| Ferramenta | Status prático | Uso recomendado |
| --- | --- | --- |
| `hermes-agent-acp-skill` | Promissor | Delegação multiagente para Hermes, Codex ou Claude Code. |
| `opencode-hermes-multiagent` | Promissor | Pacote com agentes especializados para pesquisa, planejamento, implementação e qualidade. |
| `mission-control` | Promissor | Supervisão de workflows multiagente e custos. |
| `swarmclaw` | Nichado | Swarms autônomos com skills e múltiplos provedores de modelo. |

**Recomendação para projetos gerais:** só adicionar orquestração multiagente depois que o workflow single-agent estiver estável. A comunidade reporta que bloat de ferramentas e skills prejudica a tomada de decisão do agente.

## 5. Insights relevantes do Reddit

### 5.1. Bloat é o maior risco operacional

Uma discussão forte em `r/hermesagent` aponta que carregar muitas tools, MCPs e skills cria custo de contexto e confusão semântica. A sugestão recorrente é separar perfis finos:

- `default`: arquivo, busca e shell básico;
- `comms`: Slack, e-mail e mensagens;
- `scheduling`: cron, calendário e lembretes;
- `research`: browser, search e sessões;
- `admin`: configuração, logs e manutenção.

**Aplicação prática:** para projetos gerais, não montar um "perfil universal". Usar perfis ou bundles por intenção.

Fonte: ["Hermes Agent Tool and Skills Bloat"](https://www.reddit.com/r/hermesagent/comments/1t34qee/hermes_agent_tool_and_skills_bloat/).

### 5.2. Skills boas precisam de verificação, não apenas instrução

A discussão sobre como skills funcionam destaca que uma skill forte não é um prompt genérico. Ela deve conter:

- gatilhos claros;
- procedimento exato;
- exemplos de comando;
- armadilhas comuns;
- verificação antes de declarar sucesso.

**Aplicação prática:** qualquer skill criada para Exocórtex deve incluir smoke test ou critério observável de sucesso.

Fonte: ["How Skills Work in Hermes Agent"](https://www.reddit.com/r/hermesagent/comments/1smlqdt/how_skills_work_in_hermes_agent/).

### 5.3. Diretórios comunitários precisam de camada de confiança

No post sobre o diretório comunitário, usuários pediram ranking, reviews e validação real, observando que alguns itens alegam suporte a Hermes sem evidência clara no repositório.

**Aplicação prática:** antes de recomendar uma ferramenta para produção, exigir:

- README com instalação Hermes explícita;
- permissões e variáveis de ambiente documentadas;
- último commit ou release recente;
- teste local mínimo;
- rollback ou desinstalação clara.

Fonte: ["The Hermes Agent subreddit community tool directory is now live"](https://www.reddit.com/r/hermesagent/comments/1t7c15v/the_hermes_agent_subreddit_community_tool/).

### 5.4. Compartilhamento multiagente ainda é artesanal

Uma thread recente descreve uso de diretórios compartilhados e symlinks para skills/plugins entre perfis. Isso indica demanda real por reuso entre agentes, mas também mostra que a arquitetura ainda tem arestas.

**Aplicação prática:** em ambientes multi-tenant ou multiagente, não depender de symlink manual como arquitetura principal. Definir um mecanismo próprio de distribuição, versionamento e aprovação de skills.

Fonte: ["Shared skills and plugins for multi agent setup"](https://www.reddit.com/r/hermesagent/comments/1tmc525/shared_skills_and_plugins_for_multi_agent_setup/).

## 6. Stack inicial recomendada para projetos gerais

### Perfil mínimo

- Skills oficiais necessárias ao domínio.
- 1 bundle de planejamento e execução.
- 1 bundle de pesquisa.
- Curator oficial ou rotina de auditoria de skills.
- Search provider único.
- Observabilidade básica.

### Perfil de desenvolvimento de software

- Bundle `/dev-workflow` com planejamento, teste, code review e PR.
- `hermes-web-search-plus` para pesquisa técnica.
- `Agentic-MCP-Skill` apenas quando o projeto realmente precisar expor MCPs ao agente.
- `hermes-otel` para rastrear loops longos e falhas.
- Curadoria periódica de skills criadas pelo agente.

### Perfil Exocórtex.IA SaaS

- Skills oficiais de Google Workspace ou Microsoft Workspace conforme tenant.
- Política de "draft-first" codificada como skill ou bundle.
- Memória explicável, preferindo plugins com auditoria e `why_retrieved`.
- Segurança runtime antes de qualquer integração de e-mail/calendário.
- Perfis separados por microverso: execução, pesquisa, evolução socrática e administração.
- Dashboard/workspace apenas para operadores, suporte e auditoria interna.

## 7. Riscos e recomendações de adoção

1. **Não instalar todos os MCPs disponíveis.** Cada tool adicionada compete por atenção do agente.
2. **Tratar plugins de browser como alto privilégio.** Eles podem operar páginas reais e devem rodar em ambiente isolado.
3. **Não permitir autoedição irrestrita de skills.** Usar dry-run, backup e revisão para mudanças que alterem comportamento.
4. **Separar skills de produto e skills experimentais.** O que afeta clientes precisa de versionamento e aprovação.
5. **Preferir integrações oficiais ou bem documentadas para e-mail/calendário.** Draft-first deve ser uma regra técnica, não apenas uma instrução textual.
6. **Medir custo e latência.** Plugins de memória, browser e multiagente podem melhorar qualidade, mas também aumentam tempo de execução.

## 8. Fontes consultadas

- Hermes Agent Docs: [Skills System](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)
- Hermes Agent Docs: [Curator](https://hermes-agent.nousresearch.com/docs/user-guide/features/curator)
- Hermes Agent Docs: [Bundled Skills Catalog](https://hermes-agent.nousresearch.com/docs/reference/skills-catalog)
- Hermes Agent Docs: [Features](https://hermes-ai.net/docs/features/)
- Hermes Atlas: [community map](https://hermesatlas.com/)
- GitHub: [Awesome Hermes Agent](https://github.com/0xNyk/awesome-hermes-agent)
- DeepWiki: [Skills, Tools & Plugins overview](https://deepwiki.com/nousresearch-hermes-agent/hermes-agent/5-skills-tools-and-plugins)
- Reddit: [How Skills Work in Hermes Agent](https://www.reddit.com/r/hermesagent/comments/1smlqdt/how_skills_work_in_hermes_agent/)
- Reddit: [Hermes Agent Tool and Skills Bloat](https://www.reddit.com/r/hermesagent/comments/1t34qee/hermes_agent_tool_and_skills_bloat/)
- Reddit: [hermes-curator-evolver](https://www.reddit.com/r/hermesagent/comments/1t7wzy6/i_built_a_localfirst_hermes_plugin_that_evolves/)
- Reddit: [community tool directory](https://www.reddit.com/r/hermesagent/comments/1t7c15v/the_hermes_agent_subreddit_community_tool/)
- Reddit: [Shared skills and plugins for multi agent setup](https://www.reddit.com/r/hermesagent/comments/1tmc525/shared_skills_and_plugins_for_multi_agent_setup/)
- Reddit: [Idea Workflow skill set](https://www.reddit.com/r/hermesagent/comments/1t1ohf5/i_made_an_idea_workflow_skill_set_for_hermes_agent/)
- Reddit: [Superpowers workflow adaptation](https://www.reddit.com/r/hermesagent/comments/1t154dz/i_adapted_the_superpowers_workflow_into/)
