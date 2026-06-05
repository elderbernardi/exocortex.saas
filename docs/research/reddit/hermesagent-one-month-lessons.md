# Reddit Research — One month with Hermes Agent: what users reported

Source: https://www.reddit.com/r/hermesagent/comments/1t29ogw/one_month_with_hermes_agent_what_i_wish_i_knew/

Collection note: Reddit HTML/JSON returned 403 in this environment. The public Reddit RSS feed was accessible and returned 131 entries covering the post and comments.

## 1. Começar grande demais

Problema:
Usuários tendem a superestimar a prontidão do setup e tentar automatizar “metade da vida” logo no começo: inbox, pesquisa, redes sociais, organização pessoal etc.

Contexto:
O post principal relata que Hermes funciona bem out of the box, mas justamente por parecer poderoso no primeiro uso, induz o usuário a pular etapas.

Aprendizados:
O gargalo não é instalar. O gargalo é transformar workflows em rotinas confiáveis. Quando algo quebra, isso expõe instruções vagas, pressupostos errados e falta de estrutura.

Soluções:
- Começar com um workflow pequeno.
- Torná-lo boringly reliable.
- Só depois conectar novos fluxos.
- Usar quebras como feedback para refinar processo, instruções e skills.
- Evitar o perfect setup loop antes de produzir algo real.

## 2. News digest como primeiro workflow útil

Problema:
Usuários ficam presos configurando o sistema e não chegam a construir nada.

Contexto:
Um comentário sugere começar com um digest de notícias agendado. Outro usuário confirma que criou um feed matinal, mas ele repetia notícias entre categorias e dias.

Aprendizados:
Digest de notícias é simples o bastante para começar, mas já revela problemas reais: gosto editorial, duplicação, fontes, relevância e persistência entre execuções.

Soluções:
- Criar um cron simples de notícias.
- Refinar instruções com base no resultado.
- Definir categorias e critérios de deduplicação.
- Usar como laboratório inicial para aprender como o agente erra e melhora.
- Exemplo citado: digest semanal de eventos locais via email + Telegram, com top 3 eventos gerado automaticamente.

## 3. Perfis não são presets; são agentes separados

Problema:
Usuários tratam profiles como simples presets e se confundem sobre quando usar, como manter e como compartilhar contexto.

Contexto:
Vários comentários discutem profiles. Um usuário relatou que, ao pedir para Hermes criar um perfil, ele instalou uma segunda instância. Outro achava trabalhoso alternar entre perfis.

Aprendizados:
Perfis funcionam melhor quando tratados como agentes separados, com estado próprio: config, SOUL/instruções, memória, sessões, skills, cron jobs e gateway state. Mas perfis não são sandbox de filesystem.

Soluções:
- Criar perfis por papel: coding, research, automation, writing.
- Não transformar o profile default num backpack gigante.
- Clonar config existente e cortar o que não pertence.
- Usar regra: um perfil, uma função, uma memória, um conjunto limpo de tools/skills.
- Fixar cwd quando o perfil opera sobre projeto específico.
- Não instalar Hermes de novo para cada profile.

## 4. Compartilhamento de conhecimento entre perfis

Problema:
Se perfis são separados, surge dificuldade para passar conhecimento entre research, security, design, dev etc.

Contexto:
Um usuário pergunta como compartilhar conhecimento entre um security profile e um dev profile no mesmo projeto. Outro aponta que memória, wiki e arquivos do projeto podem se dispersar.

Aprendizados:
Nem todo perfil precisa saber tudo. Separação reduz ambiguidade, mas exige uma base comum explícita para informações compartilhadas.

Soluções:
- Manter uma base documental dentro do projeto acessível por todos os perfis.
- Usar wiki/llm-wiki/Obsidian como fonte compartilhada.
- Fazer handoff por documentos de decisão, README, especificações ou briefs.
- Evitar depender de memória invisível entre perfis.
- Registrar conhecimento operacional em arquivos versionados quando for conhecimento do projeto.

## 5. Configuração é parte do produto

Problema:
Muitos comportamentos “estranhos” do Hermes são, na verdade, problemas de config: settings ausentes, tools demais, instruções conflitantes, parâmetros mal entendidos.

Contexto:
O post principal enfatiza que config is not admin work; it is the product. Um comentário relata perda de tempo usando Gemini para otimizar config, quando Hermes podia explicar o próprio estado melhor: havia config de smart routing, mas não implementação no codebase.

Aprendizados:
Config molda o comportamento do agente. Não é detalhe operacional. Perguntar a outro LLM genérico pode gerar recomendações incompatíveis com a versão real do Hermes.

Soluções:
- Perguntar ao próprio Hermes para explicar a config.
- Verificar se uma opção existe no código, não só no arquivo.
- Reduzir tools/skills ativas por perfil.
- Evitar ajustes cegos.
- Documentar tradeoffs de cada parâmetro.

## 6. Skills são núcleo operacional, não acessório

Problema:
Usuários subestimam skills ou não estruturam quando o agente deve usá-las.

Contexto:
O post principal diz que Hermes não é chat + tools; o valor está em aprender workflows, criar skills, melhorá-las e reutilizá-las. Comentários sobre Obsidian mostram que criar uma skill sobre quando atualizar a wiki ajudou.

Aprendizados:
A skill transforma comportamento repetido em procedimento durável. Mas se a skill é vaga ou contraditória, o agente pode ignorar, interpretar errado ou usar ferramenta errada.

Soluções:
- Criar skills para workflows recorrentes.
- Incluir gatilhos claros: quando usar, quando não usar.
- Registrar paths importantes em memória quando forem estáveis.
- Criar skill específica para atualizar vault/wiki.
- Revisar skills quando o agente esquece ou usa ferramenta errada.
- Manter skills pequenas, específicas e testáveis.

## 7. Memória padrão é insuficiente para uso sério

Problema:
Vários usuários relatam que a memória explode, fica confusa ou deixa de ser consultada. Um usuário diz que ainda sofre com memória; outro diz que o agente escrevia no Obsidian e depois esquecia de consultar.

Contexto:
Comentários discutem memory.md, holographic memory, Hindsight local, Obsidian, LLM wiki e arquivos mestres.

Aprendizados:
Memória precisa de arquitetura. Um único MEMORY.md pequeno não sustenta uso pessoal complexo. Memórias automáticas podem trazer fatos obsoletos e criar conflito. Fonte de verdade humana e memória contextual automática têm papéis diferentes.

Soluções:
- Separar memória contextual de fonte de verdade.
- Usar Obsidian/wiki/documentos como fonte precisa e editável.
- Usar memória para preferências, caminhos e fatos estáveis.
- Criar cron jobs de limpeza/verificação/rewrite de memória.
- Evitar registrar tudo como memória permanente.
- Se usar memória holográfica, prever rotina para expirar ou corrigir fatos obsoletos.
- Comentário relevante: um usuário migrou de Master Memory File TXT para Obsidian Vault organizado pelo Hermes.

## 8. Obsidian/wiki funciona, mas precisa de protocolo

Problema:
Usuários relatam que Hermes escreve na wiki, mas em sessões novas não volta a consultá-la.

Contexto:
Um usuário criou Obsidian para sessões, skills, automations, README e Learning.md. Outro teve dificuldade porque o agente esquecia o vault.

Aprendizados:
A existência do vault não basta. O agente precisa saber onde está, quando consultar, quando atualizar, qual arquivo é fonte de verdade e como resolver conflitos entre memória e wiki.

Soluções:
- Salvar localização do vault na memória.
- Criar skill de atualização da wiki.
- Definir frases-gatilho, como “salve no Hermes Vault”.
- Estruturar pastas: sessions, skills, automations, README, Learning.md.
- Usar Obsidian como fonte de verdade para dados precisos, especialmente dispositivos, IPs e configs.
- Usar memória apenas para saber que deve consultar a wiki.

## 9. Modelo principal importa muito

Problema:
Usuários relatam que modelo errado destrói a experiência agentic: não usa tools bem, não recupera wiki, gera respostas ruins ou custa caro demais.

Contexto:
Comentários citam experiências com Gemma, Qwen, DeepSeek, GPT mini, GLM, Mimo, OpenRouter, Nous Central e modelos chineses.

Aprendizados:
Não basta o modelo ser bom em chat. Ele precisa ser bom em tool use, leitura, seguir instruções, raciocínio operacional, custo com contexto longo e visão quando o workflow usa screenshots.

Soluções:
- Usar modelo principal mais capaz para orquestração.
- Usar modelos menores para tarefas delegadas ou simples.
- Evitar baratear demais o main model.
- Manter chats curtos quando trocar de modelo, porque o novo modelo pode precisar reler todo o contexto.
- Avaliar custo por provider: usuários relataram OpenRouter mais caro em alguns casos e DeepSeek direto mais barato.
- Para DeepSeek 4 Flash gratuito, um usuário indica provider Nous Central.
- Se o workflow depende de imagens, escolher modelo com visão.

## 10. Custo e caching podem sair do controle

Problema:
Usuários relatam gastos inesperados: um usuário gastou US$10 no primeiro dia usando DeepSeek v4 via OpenRouter, enquanto outro falava em US$0,25/dia.

Contexto:
Discussão aponta que provider, cache e troca frequente de modelo podem afetar muito o custo.

Aprendizados:
O mesmo modelo pode ter custo operacional muito diferente dependendo do provider. Caching importa. Contexto longo e reprocessamento de chat elevam custo.

Soluções:
- Monitorar spend desde o primeiro dia.
- Testar provider direto vs OpenRouter.
- Usar provider com cache eficiente.
- Evitar alternância frequente de modelo dentro da mesma conversa longa.
- Criar novas sessões quando trocar de modelo.
- Usar modelos menores para setup e tarefas simples; modelo maior para trabalho complexo.

## 11. UI customizada pode virar solução sem problema

Problema:
Usuários gastam tempo criando UI personalizada antes de resolver integrações básicas.

Contexto:
Um comentário relata construir uma UI customizada com LLM, vector DB e várias ideias, para depois perceber que faltavam coisas básicas: calendário, email, lembretes.

Aprendizados:
A parte útil pode estar no plumbing chato, não no brilho da interface. Uma UI bonita não compensa ausência de workflows confiáveis.

Soluções:
- Priorizar integrações essenciais antes de UI avançada.
- Começar com interface simples de chat.
- Perguntar: “o que eu realmente preciso além do que já tenho?”
- Criar UI local/minimalista só depois que os fluxos base funcionarem.
- Evitar construir “porque posso” em vez de “porque preciso”.

## 12. Gateway, Telegram e tópicos têm limites de roteamento

Problema:
Usuários querem usar Telegram como única interface com múltiplos perfis/tópicos, mas enfrentam confusão: profile muda no gateway, não necessariamente por tópico.

Contexto:
Um usuário usa Telegram para dieta, água e treinos, com tópicos Nutrition e Fitness. Ele tentou fazer channel prompts rotearem para agents específicos. Relatou que o orquestrador às vezes tenta fazer tudo sozinho e erra timezone apesar de MEMORY.md.

Aprendizados:
Channel prompt pode orientar roteamento, mas não é o mesmo que switching real de profile por tópico. Subagents precisam receber contexto explicitamente. Há discussão divergente nos comentários sobre delegate_task entre profiles, mas um usuário leu o código e apontou que model/toolsets/instructions podem vir do target profile, enquanto credenciais/provider config herdam do parent; memória/skills não são herdadas automaticamente.

Soluções:
- Tratar roteamento por tópico como prompt-based routing, não como isolamento real.
- Passar contexto explícito para subagents.
- Para isolamento forte, considerar bots separados por perfil ou gateway separado.
- Se usar um gateway único, criar channel prompts muito objetivos.
- Não depender só de MEMORY.md para timezone; validar timezone em cada cron/log sensível.
- Testar delegação entre perfis com tarefas simples antes de workflows críticos.

## 13. Automação via browser/desktop em VPS dedicada

Problema:
Usuários querem controlar browser, desktop e credenciais de forma mais prática para tarefas web.

Contexto:
Um comentário relata solução com host Linux mínimo em VPS pública usando X, xrdp, Chrome, chrome-tools MCP, Hermes, Docker e firewall rules. O usuário loga via RDP no browser para inserir credenciais e deixa Hermes controlar Docker/browser.

Aprendizados:
Automação web/desktop pode exigir ambiente gráfico persistente e controlado. Separar host por categoria de tarefa reduz interferência. Mas há alerta de segurança: VPS pública com browser logado, RDP e credenciais exige hardening forte.

Soluções:
- Criar host Linux dedicado mínimo por categoria de tarefa.
- Usar Docker para isolar workloads.
- Configurar firewall rigoroso.
- Usar RDP apenas por canal seguro/VPN/IP allowlist.
- Não expor browser/RDP publicamente sem proteção.
- Registrar skills e tasks para manter comportamento consistente.
- Isso conecta diretamente com as issues de UI web/desktop e segurança de VPS.

## 14. Segurança, privacidade e região do provider

Problema:
Usuários discutem risco de dados indo para provedores chineses ou modelos que podem ser banidos.

Contexto:
Comentários sobre DeepSeek/Qwen levantam preocupação com dados em servidores chineses e possíveis bloqueios regulatórios. Outro usuário europeu relativiza com proxies/leis europeias.

Aprendizados:
Provider de LLM é decisão de segurança, não só custo/performance. Workflows pessoais podem conter dados sensíveis: finanças, screenshots, emails, calendário, negócios.

Soluções:
- Classificar dados por sensibilidade.
- Definir quais providers podem receber quais tipos de dados.
- Evitar mandar screenshots financeiros/documentos sensíveis para modelo sem política clara.
- Preferir provider/região compatível com privacidade desejada.
- Documentar tradeoff custo vs privacidade.
- Para automações críticas, criar política de roteamento por tipo de dado.

## 15. Instruções e guardrails podem ser ignorados

Problema:
Um usuário relata que o agente ignorou skill/instruções e escolheu ferramenta errada para Calendar, além de pular heartbeats. Isso gerou desconfiança sobre workflows reais.

Contexto:
Ele pediu evento de calendário; o agente leu google-workspace e gogcli, mas escolheu gogcli mesmo com instrução declarada para usar Composio. Ao ser questionado, justificou escolha interpretando mal a skill.

Aprendizados:
Skills não são garantias formais. LLM pode interpretar mal, especialmente se a skill tiver ambiguidade ou múltiplos caminhos. Guardrails em linguagem natural precisam de verificação operacional.

Soluções:
- Reduzir tools disponíveis por perfil.
- Escrever skills com MUST/NEVER claros.
- Criar checks antes de ações externas.
- Exigir draft/approval para ações com side effect.
- Adicionar testes ou dry-run para workflows críticos.
- Preferir wrappers/scripts determinísticos para operações sensíveis.
- Logar e auditar decisões de tool use.
- Remover ferramentas alternativas quando não devem ser usadas.

## 16. Atualizações rápidas quebram tooling

Problema:
Usuários relatam que Hermes e WebUI evoluem rápido; isso empolga, mas também quebra tooling e scaffold.

Contexto:
Comentários citam updates contínuos, Hermes WebUI, Curator, self-improvement loop, novos providers/plugins/gateway. Um usuário reclama que updates quebram ferramentas.

Aprendizados:
Ecossistema em movimento exige controle de versão e estratégia de upgrade. Quem customiza muito sente mais dor em updates.

Soluções:
- Pinagem por versão/tag.
- Testar update em ambiente separado antes de produção.
- Manter changelog interno.
- Versionar configs, skills e scripts.
- Evitar depender de comportamento não documentado.
- Para WebUI/desktop, usar apenas versões oficiais e tagueadas.

## 17. Hermes para coding divide opiniões

Problema:
Alguns usuários dizem que Hermes não funcionou bem para coding; outros preferem ferramentas mais leves.

Contexto:
O autor do post diz que usa Hermes para tudo que não é código; para coding prefere ambiente leve e removeria muitas memórias/skills/tools, então não vê vantagem.

Aprendizados:
Hermes é forte como ambiente operacional/memória/automação, mas pode ser pesado para coding puro se o usuário quer fluxo minimalista.

Soluções:
- Criar perfil coding enxuto, se for usar Hermes para código.
- Remover tools, skills e memória que não servem ao repo.
- Fixar cwd do projeto.
- Usar Codex/Claude/OpenCode para coding direto quando fizer mais sentido.
- Usar Hermes como orquestrador/documentador/backlog, não necessariamente executor principal de código.

## 18. Expectativa de assistente total causa overload

Problema:
Usuários querem que Hermes gerencie casamento, finanças, negócio, bookkeeping, screenshots, notícias, stocks e decisões pessoais ao mesmo tempo. A memória e o contexto estouram.

Contexto:
Um usuário relata ter ficado dependente em 10 dias, mas depois travou por limite de memória e troca de modelo sem visão.

Aprendizados:
A experiência boa gera confiança rápida, mas isso incentiva escopo excessivo. Assistente verdadeiro exige arquitetura de memória, fontes de verdade, segurança e segmentação.

Soluções:
- Separar domínios pessoais em perfis/microversos.
- Criar fontes de verdade por domínio: finanças, casamento, negócio.
- Evitar despejar tudo na memória global.
- Criar rotinas de resumo e promoção de conhecimento.
- Escolher modelo com visão quando screenshots são parte do workflow.
- Trabalhar por domínios prioritários, não tudo ao mesmo tempo.

## Conclusão operacional para o projeto

Backlog prático derivado:

1. Profiles por função:
   - exec/orquestrador;
   - research;
   - infra/security;
   - coding;
   - automation;
   - UI/browser-desktop.

2. Memória em camadas:
   - memória curta para preferências estáveis;
   - wiki/Obsidian/Acervo como fonte de verdade;
   - skills para procedimentos;
   - cron de limpeza/verificação.

3. VPS segura antes de desktop/browser:
   - firewall;
   - SSH hardening;
   - RDP protegido;
   - Docker;
   - backups;
   - pinagem de versões.

4. UI web/desktop:
   - somente versões oficiais Nous Research;
   - update por tag;
   - avaliar forks controlados;
   - ambiente gráfico isolado por tarefa quando necessário.

5. Providers/modelos:
   - main model forte;
   - modelos menores para subtask;
   - política de dados sensíveis;
   - monitoramento de custo/cache.

6. Guardrails:
   - Draft-first para ações externas;
   - remover tools alternativas quando não devem ser usadas;
   - skills com instruções obrigatórias;
   - verificação real antes de declarar sucesso.
