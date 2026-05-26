# Product Requirements Document (PRD): Exocórtex.IA SaaS

## 1. Introduction / Overview

O Exocórtex.IA SaaS é um Sistema Operacional Cognitivo desenhado para atuar como um "exoesqueleto de pensamento" para executivos de alto nível e consultores. Utilizando uma arquitetura multi-agente intrinsecamente ligada ao Hermes Agent e ao seu Harness nativo, o produto foca em fricção zero (Voice-First), contenção semântica de contexto e autonomia com segurança (Human-In-The-Loop). O sistema gerencia a rotina, integra ferramentas de trabalho e evolui de forma autônoma o patrimônio de conhecimento (Acervo Cognitivo) do usuário.

## 2. Arquitetura Multi-Tenant e Topologia Alinhada ao Hermes

A arquitetura não atua "por cima" do Hermes, mas utiliza o seu próprio Harness (motor de execução de agentes) para moldar o ambiente:

* O Orquestrador Central (O Router & Gestor de Macroverso): O Orquestrador é o primeiro a acessar o Macroverso. Ele não apenas roteia a mensagem, mas atua como o configurador da sessão. Ele gere o Macroverso e prepara o Harness para o Microverso, injetando as tools, personas (via system prompt) e skills adequadas antes de passar a bola para o Agente Especialista.
* Os Agentes Especialistas (Workers de Domínio no Harness): Instâncias do Hermes configuradas pelo Orquestrador. Operam num Microverso específico. Como a modelagem (ferramentas ativas, regras do jogo) já foi pré-configurada no seu Harness, o Agente Especialista roda de forma otimizada e com foco total na resolução da tarefa e no tool calling.
* Inferência Dinâmica de Vetores: O Orquestrador avalia a intenção do usuário e infere o Vetor Ativo (Execução ou Evolução). Com base nisso, ele instrui o Harness a modificar as capacidades do agente na sessão (ex: no Vetor de Evolução, o Harness bloqueia APIs de escrita externa e injeta a tool nativa de reflexão/crítica socrática do Hermes).

## 3. Acervo Cognitivo e Resolução de Conflitos

A persistência utiliza o paradigma de LLM OS (File System), organizado segundo a ontologia do Exocórtex, e montada como volumes diretamente no contêiner do Hermes:

* /macro/ (O Macroverso): Identidade raiz, valores inegociáveis e skills globais. O Orquestrador lê esta base para parametrizar o Harness de todos os agentes subsequentes.
* /micro/[dominio]/ (Os Microversos): O cenário e as tools específicas de um domínio.

### 3.1. As 7 Naturezas Integradas ao Harness

Os artefatos mapeiam diretamente para capacidades técnicas do Hermes:

1. 🏷️ Contexto: Injetado como contexto base no system_prompt.
2. 📚 Conhecimento: Indexado no VectorDB para RAG orgânico.
3. 📝 Instrução: Carregado como diretrizes condicionais de resposta.
4. 🎭 Persona: Altera o modificador de comportamento do agente no Harness.
5. ⚙️ Processo: Define Workflows (cadeias de tool calling forçadas).
6. 🔧 Ferramenta: Ativa/Desativa conectores MCP e scripts nativos (ex: E2B).
7. 🪞 Reflexão: Salvo via Self-Correction tools nativas do Hermes após um loop.

## 4. UX e Interfaces (Zero-Friction)

A complexidade técnica é abstraída do executivo.

1. WhatsApp / Telegram (Mobile First): Canal de input diário.
2. Hub HITL (Cockpit de Validação): Interface de aprovação assíncrona para resultados de tarefas de Execução.
3. Cognitive Studio (Web Dashboard): Gestão da árvore cognitiva, visualização do Acervo e configurações de integrações.

## 5. Functional Requirements e Modelagem Cognitiva

* Canvas Cognitivo como Ponteiros (Pointers): O áudio do executivo não preenche um formulário engessado. O Hermes infere os pontos do Canvas (Tarefa, O que sei, Par ideal) e converte-os em ponteiros semânticos dinâmicos. Estes ponteiros instruem o Harness a focar em certas áreas da memória ou a chamar ferramentas específicas sem travar o diálogo.
* Gestão de Macro/Microversos: Suportar sub-sistemas de arquivos isolados.
* Política "Draft-First" (Vetor de Execução): Tarefas ativas guardam rascunhos em plataformas externas (ex: Gmail via Workspace MCP) e pedem aprovação no Cockpit.
* Vetor de Evolução Integrado: Instruindo o Hermes a usar seu motor de evolução e reflexão nativo para atuar socraticamente, guiando o usuário, mapeando lacunas de pensamento e gravando as conclusões na LLM Wiki.

## 6. Configuração Assistida e Meta-Alinhamento

O sistema utiliza o próprio Hermes para compreender como o cliente deseja que o seu Exocórtex funcione.

* Meta-Prompting de Adaptação: O sistema possui um modo de "Configuração Assistida" acessível via interface. O Hermes assume a Persona de "Arquiteto de Sistemas Cognitivos".
* Ajuste Fino Orgânico: O executivo dialoga com o Arquiteto: "Não gostei de como o Agente de Finanças respondeu ontem, foi muito prolixo." O Hermes compreende a queixa, escreve uma nova diretriz de estilo (Natureza 📝 Instrução) e guarda-a no Microverso correspondente.
* Self-Building Harness: O Hermes sugere a criação de novos Microversos ou alteração de Workflows com base nas necessidades que deduz das conversas. O produto é dinâmico e auto-regulável através de meta-análise.

## 7. Fluxo de Onboarding e Instanciação de Infraestrutura

A criação de um novo Tenant (Cliente) é um processo altamente orquestrado, combinando infraestrutura em nuvem isolada e o Setup Zero-Friction.

### 7.1. O Processo de Instanciação Técnica (Infra-as-Code)

Quando um novo cliente subscreve o SaaS, o Control Plane dispara os seguintes eventos em background:

1. Provisionamento do Contêiner: Um novo contêiner Docker/Kubernetes Pod exclusivo é instanciado, contendo a imagem base do Hermes Agent e o seu Harness de execução.
2. Isolamento de Volumes (EFS/EBS): Volumes de armazenamento criptografados são criados e montados no contêiner representando a árvore da LLM Wiki (/macro e /micro).
3. Isolamento de VectorDB: Um namespace isolado é criado no banco de dados vetorial (ex: Qdrant/Pinecone) com as chaves API únicas deste contêiner.
4. Bootstrapping Inicial: O Harness é iniciado com um Seed Prompt pré-carregado no /macro/ que instrui o Hermes a entrar no "Modo Entrevistador" para o Onboarding.

### 7.2. O Onboarding Cognitivo (Interface)

1. Convite e Autenticação: O executivo recebe um link no WhatsApp/Telegram e sincroniza a sua conta.
2. Entrevista Base (Voice-First): O Hermes inicia o diálogo: "Olá. A sua infraestrutura segura está pronta. Para configurarmos o seu Macroverso, conte-me em áudio: quais são os valores inegociáveis na sua comunicação e tomada de decisão?"
3. Auto-Configuração: O Hermes capta as respostas, processa os ficheiros anexos (ex: PDFs de relatórios passados) e executa tool calls locais para gravar os ficheiros .md inaugurais no /macro/ e desenhar a primeira sugestão de /micro/.
4. Pronto a Usar: O executivo acede ao Cognitive Studio apenas para conectar credenciais (ex: Login Google) dos MCP Servers e o sistema entra em produção.

## 8. Non-Functional Requirements

* Latência Otimizada: Como a modelagem é feita no Harness e o Orquestrador repassa o contexto estruturado (Pointers), a latência do Agente Especialista é reduzida.
* Isolamento Total: Sem partilha de memória RAM, ficheiros ou índices vetoriais entre clientes.

## 9. Épicos e Histórias de Utilizador (MVP Alpha/Beta)

* EP 1 - Fundação e Instanciação Autônoma: Scripts de orquestração Kubernetes para deploy isolado do Hermes por cliente e montagem do File System.
* EP 2 - Interface WhatsApp e Orquestrador (Pointers): Conversão de áudio para Canvas Pointers e injeção do contexto do Macroverso no Harness.
* EP 3 - Meta-Alinhamento e Onboarding: Construção do modo "Arquiteto" onde o Hermes parametriza a própria base do executivo.
* EP 4 - Vetores e Autonomia Segura: Cockpit de aprovação (Draft-first) e modo Vetor de Evolução.

## 10. Ecossistema de Integrações, Skills e MCP

Maximiza o Harness nativo do Hermes para manter a estabilidade.

### Tier 1: Harness Orgânico (Nativo)

* Local File System I/O: Para gerir a LLM Wiki (read_file, write_file).
* Docbrain (Ingestor Semântico CLI): Utiliza markitdown / llama liteparse chamado via shell nativo para converter PDFs em Markdown limpo para o Acervo.
* E2B Code Interpreter: Sandbox orgânica para dados complexos (Python).
* Tavily / Brave API:Deep Research sem servidores extras.
* Browser-Use (Playwright): Navegação dinâmica em sites.

### Tier 2: Skills Transversais (Cognitive Prompts)

Skills carregadas organicamente do Acervo.

* Self-Critique & Refine: Usa o motor nativo do Hermes para autorreflexão.
* Executive Summarizer: Padrão "Chain of Density".
* Draft Generator: Boas práticas corporativas para vetor de execução.

### Tier 3: Model Context Protocol (MCP Servers)

* Google Workspace / Slack MCP: Integração Draft-First.
* Supabase MCP: Acesso seguro via RLS a bases PostgreSQL e BaaS.
* Corporate Insights & Reports MCP: Geração de relatórios avançados sobre os dados do Docbrain.

## 11. Estrutura de Dados do LLM Wiki (File System Paradigm)

A topologia baseia-se em /macro para leitura global e /micro/[dominio] para escrita/leitura isolada, montados como volumes seguros no contêiner do Harness.

## 12. Modelagem de Dados e Contratos de API (JSON Schemas)

### 12.1. Configuração de Harness / Session Payload (Orquestrador ➔ Especialista)

O Orquestrador define a "mesa de trabalho" do Agente Especialista. Note os canvas_pointers flexíveis e a inferência de vector_mode.

{
  "session_id": "sess_8f92a1b",
  "active_microverses": ["/micro/financas/"],
  "vector_mode": "execution",
  "canvas_pointers": {
    "intent_focus": "Rever orçamento baseando-se no histórico de corte de custos",
    "identified_gaps": ["Dados do Q3 ausentes"],
    "suggested_persona_uri": "/macro/personas/cfo_analitico.md"
  },
  "harness_configuration": {
    "injected_system_prompt_uris": [
      "/macro/valores_inviolaveis.md",
      "/micro/financas/contexto_atual.md"
    ],
    "enabled_tools": ["local_fs_io", "e2b_interpreter", "corporate_insights_mcp"],
    "disabled_tools": ["slack_mcp", "workspace_mcp"]
  }
}

### 12.2. HITL Approval Request (Especialista ➔ Cockpit UI)

Gerado ao terminar o "Vetor de Execução" com dependências externas.

{
  "approval_id": "app_99x12",
  "task_id": "tsk_8f92a1b",
  "source_agent": "Microverso: Finanças",
  "artifact_type": "report_draft",
  "status": "pending_approval",
  "content": {
    "summary": "Cortes propostos no Q4",
    "uri": "/micro/financas/drafts/corte_q4.md"
  },
  "action_metadata": {
    "mcp_server": "google_workspace",
    "execute_function": "send_draft",
    "draft_id": "msg_a938fn3"
  }
}

**
