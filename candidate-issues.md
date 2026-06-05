# Candidate Issues — consolidação inicial

> Status: rascunho local para triagem manual posterior no GitHub.
> Origem: notas soltas desta sessão, links enviados pelo executivo e screenshot operacional.
> Objetivo: transformar o backlog bruto em issues já classificadas, com recorte inicial, contexto e critério de aceite.

## Convenção sugerida de classificação

- **Tipo:** `docs`, `bug`, `feature`, `infra`, `research`, `chore`
- **Prioridade:** `P0`, `P1`, `P2`, `P3`
- **Área:** `hermes`, `exocortex`, `memory`, `ui`, `integration`, `models`, `docbrain`, `google`, `telegram`

---

## 1) Documentar e integrar Hermes Workspace no ecossistema Exocórtex

- **Tipo:** `docs` + `research`
- **Prioridade:** `P2`
- **Área:** `integration`, `hermes`, `exocortex`
- **Fonte:** https://hermes-workspace.com/

### Título sugerido
Documentar Hermes Workspace e definir onde ele entra no fluxo do Exocórtex

### Contexto
Precisamos avaliar o papel do Hermes Workspace dentro do pacote `exocortex.saas`: o que ele resolve, onde complementa o runtime Hermes, quais dependências exige e como isso deve aparecer em docs, features e setup.

### Escopo inicial
- Ler e resumir o Hermes Workspace
- Mapear relação com Hermes Dashboard / Web UI / artifacts
- Definir se entra como integração oficial, opcional ou apenas referência
- Atualizar documentação canônica se a integração fizer sentido

### Critérios de aceite
- Há nota técnica objetiva com prós, contras e encaixe arquitetural
- Há decisão explícita: adotar, adiar ou rejeitar
- Se adotado, há ponto de entrada claro em docs/setup

---

## 2) Documentar Hermes Desktop e posicionar seu uso dentro do Exocórtex

- **Tipo:** `docs`
- **Prioridade:** `P2`
- **Área:** `hermes`, `integration`
- **Fonte:** https://hermes-agent.nousresearch.com/docs/user-guide/desktop

### Título sugerido
Adicionar suporte documental ao Hermes Desktop e clarificar seu papel no setup do Exocórtex

### Contexto
O projeto já documenta várias superfícies do Hermes, mas falta explicitar como o modo Desktop se encaixa no fluxo operacional do Exocórtex, quando preferi-lo e quais trade-offs ele traz frente ao dashboard/web/CLI.

### Escopo inicial
- Extrair capabilities e limitações do modo Desktop
- Comparar com CLI e dashboard atual
- Atualizar README/FEATURES/setup se houver lacuna
- Registrar quando usar Desktop e quando não usar

### Critérios de aceite
- A documentação cita Hermes Desktop de forma consistente
- O papel do Desktop no stack fica claro
- Não há ambiguidade entre dashboard, web UI e Desktop

---

## 3) Avaliar Syncthing como alternativa ao Drive para superfícies editáveis e sync local

- **Tipo:** `research` + `infra`
- **Prioridade:** `P1`
- **Área:** `integration`, `google`, `exocortex`
- **Fonte:** https://syncthing.net/

### Título sugerido
Avaliar Syncthing como alternativa ao Google Drive para sincronização de artefatos e drafts

### Contexto
Há interesse em uma alternativa ao Drive. O ponto não é só sync de arquivos, mas entender se Syncthing serve para drafts editáveis, transporte entre máquinas e artefatos locais sem quebrar a separação entre Acervo, superfícies externas e receipts.

### Escopo inicial
- Comparar Syncthing vs Drive no modelo do Exocórtex
- Identificar riscos de sincronizar conteúdo cognitivo indevidamente
- Definir se serve para artifacts, drafts, inbox ou apenas transporte local
- Registrar limites de segurança, conflito e versionamento

### Critérios de aceite
- Existe avaliação comparativa objetiva
- Há recomendação de uso ou rejeição por caso de uso
- Se aprovado, existe proposta de fluxo operacional compatível com `excrtx-produce-artifacts`

---

## 4) Avaliar Terrarium como componente local para o Exocórtex

- **Tipo:** `research`
- **Prioridade:** `P2`
- **Área:** `integration`, `infra`
- **Fonte:** https://github.com/terion-name/terrarium

### Título sugerido
Avaliar Terrarium e decidir se ele agrega valor real ao ambiente local do Exocórtex

### Contexto
O link foi marcado como candidato a documentação/integração. Falta definir se o Terrarium resolve um problema real do `exocortex.saas` ou se é apenas ferramenta interessante sem encaixe imediato.

### Escopo inicial
- Entender o produto e seu modelo operacional
- Mapear ganhos potenciais para isolamento, ambiente local ou workflow
- Comparar com o que já existe no setup atual
- Registrar decisão de adoção ou descarte

### Critérios de aceite
- Existe análise curta e verificável
- Há decisão explícita com justificativa
- Se adotado, há plano mínimo de integração documental/técnica

---

## 5) Fazer setup local do Firecrawl e documentar o fluxo de uso

- **Tipo:** `infra` + `feature`
- **Prioridade:** `P1`
- **Área:** `integration`, `hermes`

### Título sugerido
Instalar/configurar Firecrawl localmente e documentar o fluxo operacional no Exocórtex

### Contexto
O setup do Firecrawl está pendente. Isso precisa sair do estado implícito e virar procedimento reproduzível: dependências, autenticação, forma de chamada e onde ele entra no stack de coleta/pesquisa.

### Escopo inicial
- Instalar ou preparar setup local do Firecrawl
- Validar funcionamento mínimo
- Registrar pré-requisitos e pitfalls
- Atualizar docs/skills relevantes

### Critérios de aceite
- O setup pode ser reproduzido em outra máquina
- Há smoke test mínimo documentado
- O papel do Firecrawl no ecossistema fica claro

---

## 6) Fechar setup de Google login: instalar `gcloud` e alinhar fluxo com Google Workspace

- **Tipo:** `infra`
- **Prioridade:** `P1`
- **Área:** `google`, `integration`

### Título sugerido
Instalar `gcloud` e fechar o fluxo de autenticação Google usado pelo Exocórtex

### Contexto
Foi identificado que `gcloud` não está instalado, bloqueando ou degradando o login Google. Isso impacta especialmente Google Workspace e qualquer fluxo que dependa de credenciais locais coerentes.

### Escopo inicial
- Instalar `gcloud`
- Validar login/autenticação local
- Verificar compatibilidade com as skills de Google Workspace
- Atualizar docs de setup para evitar drift futuro

### Critérios de aceite
- `gcloud` está disponível e funcional
- O fluxo de login Google está documentado
- O caminho recomendado no projeto bate com o runtime real

---

## 7) Configurar Hindsight como provider de memória e registrar credenciais necessárias

- **Tipo:** `infra` + `docs`
- **Prioridade:** `P1`
- **Área:** `memory`, `hermes`

### Título sugerido
Configurar Hindsight como memory provider padrão e documentar credenciais no setup

### Contexto
Foi anotado que Hindsight não está configurado e que o projeto deveria usar `hermes config set memory.provider hindsight`, seguido de configuração em `.hermes/.env`.

### Escopo inicial
- Validar suporte a Hindsight no ambiente atual
- Configurar provider de memória
- Registrar variáveis/credenciais exigidas
- Atualizar setup e documentação operacional

### Critérios de aceite
- O provider ativo pode ser verificado no runtime
- O caminho de configuração está documentado
- Não há instruções contraditórias entre docs e ambiente real

---

## 8) Consolidar suporte a multiagentes e registrar o impacto da `multiagents skill`

- **Tipo:** `docs` + `feature`
- **Prioridade:** `P2`
- **Área:** `hermes`, `exocortex`

### Título sugerido
Documentar a habilitação de multiagentes e definir seu papel no harness do Exocórtex

### Contexto
Foi anotado que a `multiagents skill` já foi habilitada. Falta verificar o que isso altera no comportamento esperado, quais workflows passam a existir e como evitar sobreposição com mecanismos nativos de delegação.

### Escopo inicial
- Auditar o que foi habilitado de fato
- Mapear diferenças entre skill, tool de delegação e profiles
- Documentar casos de uso válidos e armadilhas
- Atualizar README/FEATURES/skills, se necessário

### Critérios de aceite
- Está claro o que foi habilitado e por quê
- Há recomendação de uso e não uso
- Não sobra ambiguidade entre multiagent skill e delegação nativa

---

## 9) Corrigir drift de namespace de skills entre `exocortex` e `excrtx`

- **Tipo:** `bug` + `docs`
- **Prioridade:** `P1`
- **Área:** `exocortex`, `hermes`

### Título sugerido
Corrigir inconsistência entre `Skills list exocortex` e o namespace canônico `excrtx`

### Contexto
Foi anotado que o Hermes está usando “Skills list exocortex” e que talvez o namespace correto devesse aparecer como `excrtx`. Isso sugere drift de nomenclatura, packaging ou documentação.

### Escopo inicial
- Auditar nomes de skill no repositório, setup e runtime
- Verificar aliases, paths de instalação e listagem final
- Corrigir docs/scripts que induzem nomenclatura errada
- Garantir consistência entre catálogo, install e uso real

### Critérios de aceite
- A listagem final de skills usa a convenção decidida
- Docs, scripts e runtime convergem
- O usuário não encontra dois nomes concorrentes para a mesma família

---

## 10) Reduzir saída ruidosa no setup final e na UI web

- **Tipo:** `bug` + `ux`
- **Prioridade:** `P1`
- **Área:** `ui`, `hermes`, `exocortex`

### Título sugerido
Limpar a saída do setup final e reduzir ruído operacional exposto na UI web

### Contexto
Foi registrado que o setup final deveria omitir mais “saída suja” na UI web. Isso aponta problema de acabamento: logs, mensagens intermediárias ou detalhes internos vazando para a superfície de uso.

### Escopo inicial
- Identificar exatamente quais saídas poluem a UI
- Separar log operacional de output voltado ao usuário
- Ajustar scripts/templates/superfícies para reduzir ruído
- Preservar depuração sem degradar a experiência principal

### Critérios de aceite
- A UI web fica mais limpa em fluxos comuns
- Logs úteis continuam disponíveis fora da superfície principal
- O setup final não expõe barulho desnecessário ao operador

---

## 11) Investigar execução via Telegram com `sudo` e cenários com múltiplos Hermes na mesma máquina

- **Tipo:** `research` + `infra`
- **Prioridade:** `P1`
- **Área:** `telegram`, `hermes`, `infra`

### Título sugerido
Mapear comportamento do gateway Telegram com `sudo` e com múltiplas instâncias Hermes na mesma máquina

### Contexto
Há uma dúvida operacional crítica: como fica o Telegram quando o processo roda com `sudo` e quando existem múltiplos Hermes/perfis/instâncias no mesmo host. Isso pode afetar isolamento, roteamento, credenciais e estado do gateway.

### Escopo inicial
- Testar ou documentar impacto de `sudo`
- Entender onde o estado do gateway fica armazenado
- Mapear riscos de conflito entre instâncias/perfis
- Propor recomendação operacional segura

### Critérios de aceite
- Há resposta clara para o cenário com `sudo`
- Há orientação explícita para múltiplos Hermes na mesma máquina
- Os riscos de colisão de estado ficam documentados

---

## 12) Construir rankeador determinístico de modelos free do OpenRouter com fallback por competência

- **Tipo:** `feature`
- **Prioridade:** `P0`
- **Área:** `models`, `integration`

### Título sugerido
Criar roteador determinístico de modelos free do OpenRouter usando ranking externo e fallback por competência

### Contexto
Foi pedido um software/skill que use apenas modelos free do OpenRouter, com fallback por ordem de competência, usando o ranking já pronto do “fox in the box” no GitHub. A implementação deve fazer parsing sem LLM e setar o modelo automaticamente.

### Escopo inicial
- Encontrar e fixar a fonte canônica do ranking
- Definir parser determinístico, sem LLM
- Mapear estratégia de fallback por competência/capacidade
- Aplicar configuração automática do modelo no Hermes/Exocórtex
- Documentar atualização e critérios de refresh do ranking

### Critérios de aceite
- O ranking é obtido/parsiado sem LLM
- O sistema decide ordem de fallback de forma reprodutível
- O modelo ativo pode ser configurado automaticamente
- A solução é auditável e não depende de leitura manual a cada uso

---

## 13) Avaliar `inclusionai/ring-2.6-1t:free` e decidir onde ele entra no roteamento

- **Tipo:** `research`
- **Prioridade:** `P2`
- **Área:** `models`
- **Fonte:** https://openrouter.ai/inclusionai/ring-2.6-1t:free

### Título sugerido
Avaliar `inclusionai/ring-2.6-1t:free` para uso no stack de modelos gratuitos

### Contexto
O modelo foi indicado como candidato. Antes de entrar no roteamento automático, precisamos classificá-lo: chat, tool use, custo/limites, contexto, qualidade e posição relativa frente às outras opções free.

### Escopo inicial
- Levantar capacidades declaradas
- Testar encaixe no papel de modelo principal ou fallback
- Registrar limitações relevantes
- Indicar posição no ranking local

### Critérios de aceite
- Há ficha objetiva do modelo
- Existe recomendação clara de uso, fallback ou descarte
- O modelo não entra no stack por impressão informal

---

## 14) Absorver aprendizados de Reddit sobre Hermes Agent e converter em documentação/ações do projeto

- **Tipo:** `docs` + `research`
- **Prioridade:** `P2`
- **Área:** `hermes`, `exocortex`
- **Fontes:**
  - https://www.reddit.com/r/hermesagent/s/7GUcRwXHH1
  - https://www.reddit.com/r/hermesagent/s/WSVpdIy8LV
  - `docs/research/reddit/hermesagent-one-month-lessons.md`

### Título sugerido
Converter aprendizados de usuários do Hermes em decisões e documentação acionável no Exocórtex

### Contexto
Já existe material consolidado no repositório com lições de uso real do Hermes. O próximo passo é decidir o que deve virar documentação oficial, backlog, guardrail de setup ou anti-pattern explícito.

### Escopo inicial
- Ler os links e confrontar com a pesquisa já salva
- Extrair aprendizados aplicáveis ao Exocórtex
- Promover o que for estrutural para docs, setup ou skills
- Registrar o que fica só como observação de pesquisa

### Critérios de aceite
- Os achados relevantes viram ação ou documentação concreta
- Anti-patterns importantes ficam explicitados
- O material não fica perdido apenas em pesquisa bruta

---

## 15) Corrigir drift operacional do DocBrain: path canônico, instância duplicada e reminder stale

- **Tipo:** `bug` + `infra`
- **Prioridade:** `P0`
- **Área:** `docbrain`, `integration`
- **Fonte operacional:** screenshot desta sessão

### Título sugerido
Resolver drift do DocBrain entre skill, documentação, reminder e runtime

### Contexto
O screenshot indica um problema real de governança operacional: a skill/documentação aponta para um path canônico desatualizado, existe uma cópia alternativa em `/home/elder/projetos/projetob/docbrain` com comando `api` fora do contrato esperado e o reminder de credenciais/chave está stale.

### Escopo inicial
- Definir qual instância do DocBrain é a canônica
- Auditar paths, scripts e comandos aceitos
- Corrigir reminder/credenciais/documentação
- Alinhar runtime real com o contrato documentado

### Critérios de aceite
- Existe uma única referência canônica para DocBrain
- Skill, docs e runtime convergem
- O reminder deixa de apontar para estado obsoleto
- O usuário não encontra duas narrativas operacionais concorrentes

---

## 16) Clarificar o item “Imagem: codex” e transformá-lo em decisão acionável

- **Tipo:** `research`
- **Prioridade:** `P3`
- **Área:** `models`, `ui`

### Título sugerido
Esclarecer o significado operacional de “Imagem: codex” no backlog desta sessão

### Contexto
A anotação “Imagem: codex” foi registrada, mas ainda não está semanticamente clara o suficiente para implementação direta. Pode ser referência a visual, branding, screenshot, modelo ou fluxo envolvendo Codex.

### Escopo inicial
- Recuperar o contexto exato do item
- Definir se é tema visual, integração, branding ou modelo
- Reescrever em formato implementável

### Critérios de aceite
- O item deixa de ser ambíguo
- Vira issue concreta ou é descartado com justificativa

---

## Ordem sugerida de ataque

### P0
1. Corrigir drift operacional do DocBrain
2. Construir roteador determinístico de modelos free do OpenRouter

### P1
3. Setup local do Firecrawl
4. Instalar `gcloud` e fechar login Google
5. Configurar Hindsight como memory provider
6. Corrigir drift de namespace `exocortex` vs `excrtx`
7. Reduzir ruído na UI web
8. Investigar Telegram com `sudo` e múltiplos Hermes
9. Avaliar Syncthing como alternativa ao Drive

### P2
10. Documentar Hermes Workspace
11. Documentar Hermes Desktop
12. Avaliar Terrarium
13. Consolidar multiagentes
14. Absorver aprendizados do Reddit
15. Avaliar `inclusionai/ring-2.6-1t:free`

### P3
16. Clarificar “Imagem: codex”

---

## Observações

- Este arquivo já está consolidado para facilitar triagem manual no seu PC.
- Ainda não houve criação de issues no GitHub.
- Onde o escopo estava ambíguo, mantive o item como candidato com explicitação da incerteza, em vez de inventar um recorte falso.
