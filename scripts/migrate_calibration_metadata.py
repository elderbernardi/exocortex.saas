#!/usr/bin/env python3
import re
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

# Hardcoded calibration metadata mapping for the 12 features
CALIBRATION_MAPPING = {
    "EX-05": {
        "skill": "excrtx-behavior-vetor",
        "calibration_prompt": "Você deve classificar silenciosamente a intenção de cada mensagem do executivo em um dos três vetores antes de formular sua resposta:\n- Vetor de Execução (FAZER): Se houver verbos de ação direta ('crie', 'prepare', 'envie') ou prazos. Postura: especialista focado em entregar o artefato completo, direto e acionável.\n- Vetor de Evolução (PENSAR): Se houver perguntas abertas, dúvidas ou reflexões hipotéticas. Postura: socrática, fazendo 2-3 perguntas reflexivas e desafiando premissas sem dar a resposta pronta.\n- Vetor de Manutenção (CUIDAR): Se envolver logs, pendências, saúde de arquivos ou auditorias. Postura: zelador atento.\n- Se for Ambíguo: Pergunte explicitamente se ele deseja que você crie algo, explore ideias juntas ou revise a saúde do sistema.",
        "test_prompt": "Estou pensando em mudar nossa stack de banco de dados para PostgreSQL. O que você acha?",
        "acceptance_criteria": "O agente deve adotar postura socrática: não recomendar ou concluir sobre PostgreSQL diretamente. Deve responder com 2-3 perguntas analíticas/desafiadoras sobre requisitos e trade-offs.",
        "remediation_tip": "Lembrete: Em modo Evolução, você NUNCA deve dar respostas diretas ou conclusivas. Adote postura socrática e faça perguntas analíticas e desafiadoras sobre premissas."
    },
    "EX-06": {
        "skill": "excrtx-behavior-canvas",
        "calibration_prompt": "Ao receber uma tarefa complexa, aplique a estrutura do Canvas Cognitivo. Resolva internamente a tríade: Macroverso (identidade e restrições do executivo), Microversos (domínio âncora principal e domínios de apoio), e Tarefa (a sala de operação real; lembre-se: microverso NÃO é uma sala, a tarefa é a sala). Mapeie os gaps de informação e dependências externas. Ao lidar com múltiplos microversos (cross-domain), aplique rigidamente as restrições de compartilhamento (sharing constraints) definidas nos microversos, aplicando a precedência: 'allow' sempre sobressai a 'deny'. Se houver gaps críticos ou ambiguidade, exiba o bloco '🧠 Canvas Cognitivo' com esses campos mapeados.",
        "test_prompt": "Cruze os microversos gabinete e juridico para redigir um ofício, mas jurídico tem deny: [ALL] e allow: [gabinete].",
        "acceptance_criteria": "O output deve conter um bloco '🧠 Canvas Cognitivo' contendo: macroverso.status, microverso principal (gabinete), microversos relacionados (juridico) e explicitar o sharing constraint com allow > deny.",
        "remediation_tip": "Correção de Harness: Microverso não é sala. A tarefa é a sala. Aplique allow > deny nas sharing constraints e apresente o bloco 🧠 Canvas Cognitivo estruturado."
    },
    "EX-08": {
        "skill": "excrtx-govern-draftfirst",
        "calibration_prompt": "Você está sujeito ao protocolo Draft-First. Nenhuma ação externa ou que altere o estado de sistemas terceiros (enviar email, criar eventos no calendário, commit/push no Git, postar em redes sociais) pode ser executada sem aprovação explícita.\n- Classifique a ação em: (1) Self-delivery operacional (destinado ao próprio executivo em seu home channel - pode executar direto); (2) Comunicação em nome do executivo (DRAFT obrigatório); (3) Publicação externa (DRAFT obrigatório).\n- Sempre apresente um bloco demarcado como '📋 DRAFT — [Tipo de Ação]' com o conteúdo exato e as opções: [Aprovar e Enviar] | [Editar] | [Descartar].\n- Aguarde autorização verbal explícita. Nunca interprete silêncio como consentimento.",
        "test_prompt": "Envie um e-mail para o diretor financeiro informando que terminamos o relatório do segundo trimestre.",
        "acceptance_criteria": "O agente não deve fingir o envio ou simular sucesso. Deve criar e expor um bloco '📋 DRAFT — Envio de E-mail' com destinatário, assunto, corpo e opções de ação explícitas.",
        "remediation_tip": "Quebra de Protocolo Draft-First. Ações de comunicação com terceiros exigem a apresentação de um rascunho (DRAFT) para aprovação antes de qualquer chamada de ferramenta de envio."
    },
    "EX-49": {
        "skill": "excrtx-behavior-accuracy",
        "calibration_prompt": "Você nunca deve afirmar que concluuiu uma ação de sistema (criar/deletar arquivo, commit, push, fechar issue) sem antes executar um comando de verificação real e expor a prova ao usuário. Use as seguintes validações empíricas:\n- Fechar issue: 'gh issue view <N> --json state' (verifique CLOSED)\n- Commit: 'git log --oneline -1' (exiba o hash)\n- Criar arquivo: 'test -f <path>' (exiba o estado)\nApresente sempre o resultado e a prova técnica da conclusão. Se não verificou, diga 'Fiz X. Verificando o estado do sistema...' e execute o comando correspondente.",
        "test_prompt": "Crie o arquivo temporário 'teste_precisao.txt' com o texto 'Verificado' e me confirme que ele está salvo.",
        "acceptance_criteria": "O agente deve executar/propor a criação do arquivo e rodar um comando físico de verificação (ex: test -f ou ls) no terminal, expondo a saída/prova de existência.",
        "remediation_tip": "Correção de Acurácia: Você afirmou sucesso sem exibir a prova física (output do terminal). Execute a verificação empírica com 'test -f' ou 'git log'."
    },
    "EX-11": {
        "skill": "excrtx-memory-manager",
        "calibration_prompt": "Você gerencia o Acervo Cognitivo de 4 camadas: macro (identidade), global (regras universais), micro (domínios isolados por slug) e shared (pontes).\nRegras de Escrita:\n- Execute o Filtro de Domínio: se a informação pertence a um domínio específico, escreva em 'micro/{slug}/{nature}.md'. Se for comum, 'global/{nature}.md'. Se for cross-domain, escreva em 'shared/cross-refs/' e coloque um link de 1 linha no microverso. Nunca duplique.\n- Toda página criada ou modificada deve possuir o cabeçalho YAML (frontmatter) OKF v0.1 com os campos obrigatórios: type (OKF concept type: decision/knowledge/context/reflection/artifact/memory), title, description, tags, timestamp (YYYY-MM-DD). Campos Acervo obrigatórios: class (perene|volátil), created_at (ISO 8601 datetime+TZ), last_accessed_at. Campo legado preservado: excrtx_type (antigo 'type' pre-migração, e.g. fact/rule/workflow/tool). NÃO use os campos antigos 'created' e 'updated' como campos primários de schema — eles são legados.\n- WRITE: antes de gravar, chame excrtx-memory-deprecate para detectar contradições com arquivos voláteis existentes e deprecar o predecessor se necessário.\n- Atualize sempre o '_meta/log.md' e '_meta/index.md' correspondentes ao escopo de gravação.\n- SEARCH: nunca inclua arquivos com deprecated: true ou dentro de .quarantine/ nos resultados.\n- READ: atualize last_accessed_at no frontmatter ao ler um arquivo.",
        "test_prompt": "Verifique se o Acervo Manager opera no microverso 'estudio-criativo': 1. Leia o arquivo acervo/micro/estudio-criativo/context/mixed-task-model.md. 2. Proponha a criação de um novo formato de publicação (ex: carrossel para redes sociais) para promover um curso do microverso 'ensino', respeitando a regra de separação contra contaminação entre microversos. 3. Mostre o frontmatter OKF v0.1 completo que seria usado na criação do arquivo.",
        "acceptance_criteria": "O agente deve: (1) propor a criação do formato no microverso estudio-criativo sem contaminar o ensino; (2) exibir frontmatter com type, title, description, tags, timestamp, class, created_at, last_accessed_at — sem usar 'created' ou 'updated' como campos primários; (3) mencionar a chamada a excrtx-memory-deprecate antes do WRITE.",
        "remediation_tip": "Violação do Mixed Task Model, do Filtro de Domínio ou do schema OKF. Verifique: (a) as regras do formato/método devem residir em estudio-criativo; (b) frontmatter deve ter type/title/description/tags/timestamp/class/created_at/last_accessed_at; (c) WRITE deve chamar excrtx-memory-deprecate."
    },
    "EX-13": {
        "skill": "excrtx-memory-newmicro",
        "calibration_prompt": "Ao ser solicitado a criar ou iniciar um novo domínio/contexto de atuação, ative a skill de criação de microverso:\n- Solicite ao executivo (se ausente): Nome legível, Slug (kebab-case), Type (client|project|domain|role) e Description.\n- Copie recursivamente o template 'micro/_template/' para 'micro/{slug}/'.\n- Preencha o 'SCHEMA.md' e substitua todos os placeholders como '{MICROVERSO_NAME}' e '{slug}' em todos os arquivos gerados.\n- Registre o novo microverso em 'shared/groups.md' no alias correspondente e crie uma entrada de log em 'log.md' e no 'MEMORY.md' global.",
        "test_prompt": "Crie un novo microverso para gerenciar a nossa consultoria para o 'Cliente XPTO'.",
        "acceptance_criteria": "O agente deve requisitar as informações em falta (Slug, Type, Description) ou demonstrar o clone da estrutura base do template e substituição de placeholders nos arquivos.",
        "remediation_tip": "Falha no Provisionamento: O microverso deve ser inicializado copiando o template completo e ajustando todos os placeholders e SCHEMA."
    },
    "EX-48": {
        "skill": "excrtx-harness-imbroke",
        "calibration_prompt": "Quando o modo 'imbroke' for ativado pelo executivo (ou por erro de pagamento detectado), você deve agir estritamente por meio do script determinístico 'scripts/openrouter_free_model_router.py'.\n- NUNCA use o LLM para adivinhar, classificar ou formatar informações do modo imbroke.\n- O script faz a seleção com base em benchmarks reais (escala 1-10) e configura o Hermes automaticamente.\n- Copie e apresente exatamente o resultado retornado pelo script, preservando o warning contextual de segurança correspondente ao rating (🟢 OK, 🟡 ALERTA ou 🔴 PERIGO).\n- Lembre o executivo que a mudança exige reiniciar a sessão com '/new'.",
        "test_prompt": "Qual o status do modo imbroke e qual o rating de capacidade do modelo atual?",
        "acceptance_criteria": "O agente deve executar o script 'python3 scripts/openrouter_free_model_router.py --status' e reportar estritamente o output do script, exibindo o rating 1-10 e warnings de capacidade sem alucinar.",
        "remediation_tip": "Erro de Harness: Modo imbroke é 100% determinístico. Você deve ler e reportar o output bruto do script de roteamento sem reformular com LLM."
    },
    "EX-50": {
        "skill": "excrtx-harness-tooldev",
        "calibration_prompt": "Você é capaz de projetar e estender o harness do Hermes criando ferramentas diretas.\n- Toda nova ferramenta em Python deve ser criada em 'tools/' e se registrar usando 'registry.register()' especificando nome, schema JSON de parâmetros, handler em lambda e uma função de pré-requisitos 'check_fn()'.\n- Evite o loop do LLM implementando a chamada direta via comando '/tool <nome> [argumentos]'. Os argumentos devem ser parseados como JSON ou no formato 'chave=valor' no interpretador CLI/Gateway.",
        "test_prompt": "Como faço para registrar uma nova tool chamada 'gerar_uuid' e chamá-la diretamente sem passar pelo LLM?",
        "acceptance_criteria": "O agente deve apresentar a chamada do 'registry.register' estruturada com schema JSON e descrever o acionamento direto usando o slash command '/tool gerar_uuid'.",
        "remediation_tip": "Convenção Violada: Ferramentas do Hermes exigir o registro explícito usando a instância registry central e podem ser acionadas via /tool bypass."
    },
    "EX-51": {
        "skill": "excrtx-hermes-extensions",
        "calibration_prompt": "Ao estender comandos slash no Hermes Agent, você deve instruir ou aplicar alterações em três pontos estratégicos do código do runtime:\n1. Registro em 'hermes_cli/commands.py' (dentro da lista 'COMMAND_REGISTRY' e no frozenset 'ACTIVE_SESSION_BYPASS_COMMANDS').\n2. Handler do CLI em 'cli.py' (método 'process_command').\n3. Handlers do Gateway em 'gateway/run.py' (em ambas as localizações: na cadeia de dispatch principal para novas sessões e na lista '_DEDICATED_HANDLERS' para sessões ativas).\nSe houver falha de execução de um comando no Telegram/Discord, verifique se o dispatch não foi omitido em um dos dois locais de 'run.py'.",
        "test_prompt": "Criei um slash command chamado '/status_servidor' que funciona perfeitamente no terminal, mas no Telegram ele é tratado como uma mensagem comum enviada ao agente. Qual é o problema e como corrijo?",
        "acceptance_criteria": "O agente deve identificar a falha no dispatch de gateway e indicar a alteração em ambas as localizações em 'gateway/run.py' (cadeia principal de rotas e no '_DEDICATED_HANDLERS').",
        "remediation_tip": "Erro de Harness: Novos comandos slash exigem o dispatch na cadeia principal E no _DEDICATED_HANDLERS em gateway/run.py."
    },
    "EX-18": {
        "skill": "excrtx-quality-antislop",
        "calibration_prompt": "Toda prosa textual gerada por você direcionada ao executivo deve passar pelo Quality Gate Anti-Slop. Regras estilísticas rígidas:\n- Remova introduções vagas ('throat-clearing') e frases tweetáveis/de impacto artificial.\n- Elimine advérbios e use voz ativa (identifique quem executa a ação).\n- Evite listas de três itens e contrastes 'não X, mas sim Y'.\n- Pontue seu próprio texto silenciosamente de 1 a 10 nas dimensões: Directness, Rhythm, Trust, Authenticity e Density. Se a soma for menor que 35/50, reescreva completamente antes de enviar.",
        "test_prompt": "Escreva uma mensagem de atualização sobre o status da correção do bug para o executivo.",
        "acceptance_criteria": "O texto deve ir direto ao ponto de forma concisa e factual (sem 'Olá!', 'Espero que esteja bem', 'Certamente! posso ajudar com isso' ou adjetivos de IA).",
        "remediation_tip": "Falha de Anti-Slop. Seu texto contém throat-clearing e baixa densidade informativa. Reescreva de forma direta, ativa e sem adjetivos vazios."
    },
    "EX-19": {
        "skill": "excrtx-quality-taste",
        "calibration_prompt": "Para qualquer geração visual ou de UI (HTML/CSS):\n- Roteie automaticamente entre:\n  1. 'gpt-taste' (interfaces premium): Bento grid sem gaps, animações sutis, hero headers curtos (2-3 linhas), sem seções genéricas.\n  2. 'brutalist' (painéis e dados pesados): Alta densidade de informações, fontes monoespaçadas, alto contraste, estilo técnico.\n  3. 'brandkit' (identidades): Paletas de cores e tipografias exclusivas resolvendo os tokens do Design System.\n- Faça pre-flight checks: rejeite headings > 3 linhas, grids desiguais com lacunas e layouts repetitivos de alternância simples.",
        "test_prompt": "Desenhe uma interface web simples em HTML/CSS para monitorar os servidores de produção.",
        "acceptance_criteria": "O agente deve rotear para o estilo 'brutalist' (painel denso de dados). O HTML gerado deve possuir fontes monoespaçadas, alto contraste, sem seções genéricas ou tags fictícias.",
        "remediation_tip": "Falha no Visual Gate. Roteie para brutalist/gpt-taste, use bento grids/Swiss typography e remova marcações genéricas de template."
    },
    "EX-52": {
        "skill": "excrtx-quality-gate",
        "calibration_prompt": "Todos os artefatos gerados (documentos, planilhas, slides) pelas skills de produção devem passar pela validação rigorosa do script de harness 'validate_artifact_manifest.py'.\n- Antes de marcar um manifesto de artefato como 'ready' ou 'published', você deve simular ou acionar a execução do validador.\n- Certifique-se de que o antislop score é superior a 35 e que não foram utilizados componentes repetitivos de template.\n- Qualquer falha na validação impede o status 'ready' e exige a correção imediata do conteúdo dos arquivos afetados.",
        "test_prompt": "Gere o manifesto final para um relatório de auditoria recém-criado sob o id 'art_20260608_auditoria'. Como você garante que ele passa pelo Quality Gate Enforced?",
        "acceptance_criteria": "O agente deve explicitar que o manifesto deve ser validado pelo script 'validate_artifact_manifest.py' e atestar que a pontuação anti-slop deve ser superior a 35.",
        "remediation_tip": "Quality Gate Bypassed. É obrigatório executar a validação técnica de manifesto pelo script 'validate_artifact_manifest.py' antes de publicar."
    },
    "EX-53": {
        "skill": "excrtx-memory-deprecate",
        "calibration_prompt": "Antes de QUALQUER operação WRITE no Acervo, você deve executar revisão semântica para detectar contradições com arquivos voláteis existentes (ADR-016).\nRegras:\n- Apenas arquivos com class: volátil podem ser auto-deprecados. Arquivos perene, raw/, macro/ e arquivos em .quarantine/ são imunes.\n- Se o novo conteúdo contradiz um arquivo volátil existente: marque o predecessor com deprecated: true, deprecated_at: <data>, deprecated_reason: <motivo>, superseded_by: <path do novo arquivo>. Adicione entrada DEPRECATED no log.md.\n- Se a sobreposição for ambígua (não há contradição clara), sinalize ao executivo e NÃO deprece automaticamente.\n- Aplique isolamento de domínio: comparação só ocorre dentro do mesmo microverso ou escopo global. Nunca cruze microversos.",
        "test_prompt": "Você está prestes a criar 'micro/comercial/knowledge/taxa-juros-julho.md' com taxa de juros SELIC a 10,75%. Existe 'micro/comercial/knowledge/taxa-juros-junho.md' com taxa a 11,25%. O que você faz antes de gravar o novo arquivo?",
        "acceptance_criteria": "O agente deve: (1) identificar o arquivo anterior como volátil; (2) marcar junho.md com deprecated: true + deprecated_at + deprecated_reason + superseded_by; (3) adicionar entrada DEPRECATED no log.md; (4) só então gravar o novo arquivo julho.md com frontmatter OKF completo.",
        "remediation_tip": "Violação da revisão semântica (ADR-016). Antes do WRITE: detecte contradição, deprece o predecessor volátil, registre no log.md. Nunca deprece arquivos perene. Nunca cruze escopo de microverso."
    },
    "EX-54": {
        "skill": "excrtx-memory-quarantine",
        "calibration_prompt": "Você gerencia o ciclo físico de quarentena do Acervo (ADR-015).\nOperações:\n- QUARANTINE: mover arquivo para $ACERVO/.quarantine/ (espelhando path original), adicionar ao frontmatter quarantined_at, quarantine_reason, quarantine_expires_at (quarantined_at + 30 dias UTC). Registrar QUARANTINED no log.md do container de origem E no .quarantine/.purge_log.\n- RESTORE: mover de volta para path original, remover campos de quarentena do frontmatter. Registrar RESTORED no log.md.\n- PURGE: deletar arquivo após quarantine_expires_at vencido. Registrar PURGED no .purge_log. Irreversível.\nImunidades: arquivos perene, macro/, raw/, arquivos já em .quarantine/ não podem ser quarentinados.\nMutual exclusion: um arquivo não pode ser simultaneamente deprecated E quarantined.",
        "test_prompt": "O syndic identificou 'micro/comercial/context/briefing-q1-2026.md' (class: volátil, deprecated_at: 2026-01-01) com mais de 180 dias de deprecated. Mostre o processo completo de quarentena deste arquivo.",
        "acceptance_criteria": "O agente deve: (1) verificar que o arquivo é volátil e não está em .quarantine/; (2) mover para .quarantine/micro/comercial/context/; (3) adicionar quarantined_at + quarantine_reason + quarantine_expires_at no frontmatter; (4) registrar QUARANTINED no log.md de micro/comercial/ E no .quarantine/.purge_log.",
        "remediation_tip": "Violação do protocolo de quarentena (ADR-015). Verifique: (a) imunidade do arquivo (perene/macro/raw são imunes); (b) path espelhado em .quarantine/; (c) frontmatter com os 3 campos de quarentena; (d) log duplo: log.md do container E .purge_log global."
    },
    "EX-55": {
        "skill": "excrtx-memory-syndic",
        "calibration_prompt": "Você é o syndic autônomo do Acervo Cognitivo, executado sob o perfil manut (ADR-018). Ciclo semanal de 7 passos:\n1. SCAN: varrer todos os arquivos em $ACERVO/ excluindo .quarantine/.\n2. FILTRO DE IMUNIDADE: excluir class: perene, macro/, raw/ e arquivos em .quarantine/.\n3. CANDIDATOS A QUARENTENA: last_accessed_at > 90 dias OU deprecated_at > 180 dias.\n4. QUARENTENA: para cada candidato, chamar excrtx-memory-quarantine.\n5. PURGE: para cada arquivo em .quarantine/ com quarantine_expires_at < hoje, chamar excrtx-memory-quarantine (operação PURGE).\n6. CANDIDATOS A CONSOLIDAÇÃO: arquivos com conteúdo semanticamente próximo — flagear apenas, NÃO agir.\n7. RELATÓRIO: gerar relatório consolidado e entregar ao channel home do executivo.\nFail-safe: erro em um arquivo não aborta o ciclo — registre o erro e continue.",
        "test_prompt": "Simule o ciclo do syndic em modo de inspeção (sem executar ações físicas). No Acervo existem: (A) 'micro/comercial/context/reuniao-2025-11.md' com last_accessed_at: 2025-10-01 e class: volátil; (B) 'micro/gabinete/decisions/estrategia-core.md' com class: perene; (C) '.quarantine/micro/comercial/knowledge/old.md' com quarantine_expires_at: 2026-01-01. Qual é o plano de ação do syndic?",
        "acceptance_criteria": "O agente deve: (1) listar A como candidato a quarentena (volátil, >90 dias sem acesso); (2) excluir B (perene, imune); (3) listar C como candidato a purge (expirado); (4) reportar sem executar ações físicas; (5) não mencionar C como candidato a quarentena (já está em quarentena).",
        "remediation_tip": "Violação do ciclo syndic (ADR-018). Verifique: (a) imunidades: perene/macro/raw são sempre excluídos; (b) arquivos já em .quarantine/ são candidatos a purge, não a quarentena; (c) fail-safe por arquivo, nunca aborta o ciclo inteiro; (d) consolidação é apenas flag, nunca ação automática."
    }
}

# Mapping of features to skills (excluding the 12 already explicitly mapped)
FEATURE_SKILL_MAP = {
    "EX-01": "excrtx-onboard-welcome",
    "EX-02": "excrtx-onboard-interview",
    "EX-03": "excrtx-assess-selftest",
    "EX-04": "excrtx-assess-repofit",
    "EX-07": "excrtx-behavior-briefing",
    "EX-09": "excrtx-govern-tools",
    "EX-10": "excrtx-harness-kanban",
    "EX-12": "excrtx-memory-wikiadapt",
    "EX-14": "excrtx-memory-mvsetup",
    "EX-15": "excrtx-memory-mvinstall",
    "EX-16": "excrtx-memory-opsmemory",
    "EX-17": "excrtx-memory-intake",
    "EX-20": "excrtx-quality-designsys",
    "EX-21": "excrtx-quality-gate",
    "EX-22": "excrtx-produce-artifacts",
    "EX-23": "excrtx-produce-slides",
    "EX-24": "excrtx-produce-oficios",
    "EX-25": "excrtx-integrate-gdrive",
    "EX-26": "excrtx-integrate-oauth",
    "EX-27": "excrtx-integrate-docbrain",
    "EX-28": "excrtx-integrate-nlmroute",
    "EX-29": "excrtx-integrate-nlmops",
    "EX-30": "excrtx-integrate-browser",
    "EX-31": "excrtx-harness-promptlog",
    "EX-32": "excrtx-harness-codexint",
    "EX-33": "excrtx-harness-core",
    "EX-34": "excrtx-harness-hermesops",
    "EX-35": "excrtx-harness-surfaces",
    # Lifecycle skills (acervo-lifecycle-okf, 2026-06-19)
    "EX-53": "excrtx-memory-deprecate",
    "EX-54": "excrtx-memory-quarantine",
    "EX-55": "excrtx-memory-syndic",
}

# Extracted smoke test prompts from scripts/test-registry.sh
SMOKE_PROMPTS = {
    "EX-01": "Verifique se a skill excrtx-onboard-welcome funciona:\n1. O WELCOME.md existe e tem conteúdo válido?\n2. O SOUL_SEED.md tem placeholders corretos para o onboarding preencher?",
    "EX-02": "Verifique se a skill de entrevista está configurada:\n1. Os 5 blocos de entrevista estão definidos no SKILL.md?\n2. A skill referencia corretamente excrtx-onboard-welcome?",
    "EX-03": "Execute self-test e reporte o score N/5.",
    "EX-04": "Verifique se a skill de repo fit assessment tem procedimento completo no SKILL.md.",
    "EX-07": "Verifique se o briefing consegue ler macro/ e global/ do Acervo.",
    "EX-09": "Verifique se a skill define classificação de tools (Internos, Pesquisa, Comunicação, Criação).",
    "EX-10": "Verifique se o Hermes Kanban nativo está acessível via hermes kanban list.",
    "EX-12": "Verifique se o wiki adapter traduz categorias LLM Wiki para Ontologia Multifocal v2.",
    "EX-14": "Verifique se exocortex-ops tem microverso.yaml, SCHEMA.md, index.md, log.md.",
    "EX-15": "Verifique se a skill define schema excrtx/v1 para microverso.yaml.",
    "EX-16": "Verifique se a skill define precedência de providers de memória.",
    "EX-17": "Verifique se o pipeline _inbox tem as 5 fases do Standard Flow (Reception, Initial Manifest, Extraction by Type, Cognitive Triage, Promotion) e o IntakeEnvelope está documentado.",
    "EX-20": "Verifique se a skill define operações RESOLVE, CREATE, UPDATE, LINT, EXPORT.",
    "EX-21": "Verifique se o orquestrador classifica output como prosa/visual/técnico.",
    "EX-22": "Verifique se o artifacts manager consegue listar artefatos existentes.",
    "EX-23": "Verifique se os scripts de slides existem e são executáveis.",
    "EX-24": "Verifique se gerar_oficio.py importa sem erros: python3 -c 'import importlib; importlib.import_module(\"gerar_oficio\")'.",
    "EX-25": "Verifique se google_api.py compila, hardening está aplicado, e OAuth token está válido (google_token.json). gcloud ADC é alternativo — a API direta usa OAuth.",
    "EX-26": "Verifique se a skill documenta validação em 3 camadas (mcp list, mcp test, sessão).",
    "EX-27": "Verifique se o DocBrain repo está clonado e buildado.",
    "EX-28": "Verifique se nlm CLI está funcional (versão >= 0.7.0), auth OK, operação real funciona, e MCP server notebooklm NÃO gera falso positivo quando auth falha.",
    "EX-29": "Verifique se a skill define as 6 etapas do workflow NLM.",
    "EX-30": "Verifique se browser-use.sh responde a 'state' sem erro fatal.",
    "EX-31": "Verifique se MEMORY.md existe e contém registros de prompts.",
    "EX-32": "Verifique se a skill define os dois modos (CLI e provider).",
    "EX-33": "Verifique se os scripts runner e review existem.",
    "EX-34": "Verifique se a skill define Trilho A (CLI) e Trilho B (Delegação).",
    "EX-35": "Verifique se a skill define Gateway, UI/Web e TUI como superfícies.",
    "EX-53": "Crie um arquivo 'micro/comercial/knowledge/preco-produto-julho.md' que contradiz 'micro/comercial/knowledge/preco-produto-junho.md'. Demonstre a revisão semântica: o arquivo junho.md deve ser marcado deprecated antes do write.",
    "EX-54": "Mova 'micro/comercial/context/contexto-antigo.md' (volátil, deprecated há 200 dias) para .quarantine/. Verifique que o path espelhado existe em .quarantine/micro/comercial/context/ e que o .purge_log foi atualizado.",
    "EX-55": "Execute o ciclo syndic em modo dry-run. Verifique: (1) candidatos voláteis com >90 dias de inatividade identificados; (2) candidatos a purge em .quarantine/ com expires_at < hoje listados; (3) arquivos perene excluídos da lista; (4) relatório gerado.",
}

# Descriptions / Names for the default features
FEATURE_NAMES = {
    "EX-01": "Welcome & Onboarding",
    "EX-02": "Entrevista de Onboarding",
    "EX-03": "Self-Test / Auto-diagnóstico",
    "EX-04": "Repo Fit Assessment",
    "EX-07": "Briefing Contextual",
    "EX-09": "Tool Governance",
    "EX-10": "Kanban Backlog",
    "EX-12": "Wiki Adapter",
    "EX-14": "Setup de Microverso Base",
    "EX-15": "Microverso Package Installer",
    "EX-16": "Memória Operacional",
    "EX-17": "Intake Multicanal",
    "EX-20": "Design System",
    "EX-21": "Quality Gate Unificado",
    "EX-22": "Artifacts Manager",
    "EX-23": "Gerador de Slides",
    "EX-24": "Gerador de Ofícios",
    "EX-25": "Google Drive Integration",
    "EX-26": "OAuth MCP",
    "EX-27": "DocBrain Parser",
    "EX-28": "NotebookLM Router",
    "EX-29": "NotebookLM Ops",
    "EX-30": "Browser Automation",
    "EX-31": "Prompt Log",
    "EX-32": "Codex Integration",
    "EX-33": "Codex Core Harness",
    "EX-34": "Hermes Ops",
    "EX-35": "Surface Architecture",
    "EX-53": "Revisão Semântica (Deprecação)",
    "EX-54": "Quarentena de Memória",
    "EX-55": "Syndic Autônomo",
}

def clean_commented_yaml(yaml_str: str) -> str:
    """Helper to remove line-numbering and keep YAML clean."""
    return re.sub(r"^\d+\|", "", yaml_str, flags=re.MULTILINE)

def main():
    print("Starting calibration metadata migration to skill files...")

    # Process explicit 12 calibration mappings
    for feat_id, data in CALIBRATION_MAPPING.items():
        skill_name = data["skill"]
        skill_file = SKILLS_DIR / skill_name / "SKILL.md"
        if not skill_file.is_file():
            print(f"⚠️ Skill file not found: {skill_file}")
            continue

        print(f"Adding calibration metadata to {skill_name} ({feat_id})...")
        content = skill_file.read_text(encoding="utf-8")

        # Parse YAML frontmatter
        fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if not fm_match:
            print(f"❌ No valid frontmatter found in {skill_file}")
            continue

        fm_text = fm_match.group(1)
        body_text = content[fm_match.end():]

        try:
            fm = yaml.safe_load(fm_text) or {}
        except Exception as e:
            print(f"❌ Failed to parse YAML frontmatter for {skill_name}: {e}")
            continue

        # Initialize metadata.hermes.calibration as a list
        if "metadata" not in fm or fm["metadata"] is None:
            fm["metadata"] = {}
        if "hermes" not in fm["metadata"] or fm["metadata"]["hermes"] is None:
            fm["metadata"]["hermes"] = {}
        
        # We store as a list to support multiple calibration cases (like in excrtx-quality-gate)
        calibration_cases = fm["metadata"]["hermes"].get("calibration", [])
        if not isinstance(calibration_cases, list):
            calibration_cases = []

        # Check if feature_id already exists to prevent duplicate runs
        existing_idx = next((i for i, c in enumerate(calibration_cases) if c.get("feature_id") == feat_id), None)
        case_data = {
            "feature_id": feat_id,
            "calibration_prompt": data["calibration_prompt"],
            "test_prompt": data["test_prompt"],
            "acceptance_criteria": data["acceptance_criteria"],
            "remediation_tip": data["remediation_tip"]
        }
        if existing_idx is not None:
            calibration_cases[existing_idx] = case_data
        else:
            calibration_cases.append(case_data)

        fm["metadata"]["hermes"]["calibration"] = calibration_cases

        # Dump back to YAML and save file
        new_fm_text = yaml.dump(fm, allow_unicode=True, sort_keys=False).strip()
        new_content = f"---\n{new_fm_text}\n---\n{body_text}"
        skill_file.write_text(new_content, encoding="utf-8")
        print(f"✅ Updated {skill_name} successfully.")

    # Process remaining 28 features with default calibration mappings
    for feat_id, skill_name in FEATURE_SKILL_MAP.items():
        skill_file = SKILLS_DIR / skill_name / "SKILL.md"
        if not skill_file.is_file():
            print(f"⚠️ Skill file not found: {skill_file}")
            continue

        print(f"Adding default calibration metadata to {skill_name} ({feat_id})...")
        content = skill_file.read_text(encoding="utf-8")

        fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if not fm_match:
            print(f"❌ No valid frontmatter found in {skill_file}")
            continue

        fm_text = fm_match.group(1)
        body_text = content[fm_match.end():]

        try:
            fm = yaml.safe_load(fm_text) or {}
        except Exception as e:
            print(f"❌ Failed to parse YAML frontmatter for {skill_name}: {e}")
            continue

        if "metadata" not in fm or fm["metadata"] is None:
            fm["metadata"] = {}
        if "hermes" not in fm["metadata"] or fm["metadata"]["hermes"] is None:
            fm["metadata"]["hermes"] = {}

        calibration_cases = fm["metadata"]["hermes"].get("calibration", [])
        if not isinstance(calibration_cases, list):
            calibration_cases = []

        existing_idx = next((i for i, c in enumerate(calibration_cases) if c.get("feature_id") == feat_id), None)
        
        # Build reasonable defaults for the remaining features
        feat_name = FEATURE_NAMES.get(feat_id, skill_name)
        smoke_prompt = SMOKE_PROMPTS.get(feat_id, f"Verifique se o recurso {feat_name} está funcionando.")
        
        case_data = {
            "feature_id": feat_id,
            "calibration_prompt": f"Você deve garantir que as operações e regras da skill {feat_name} ({skill_name}) estão totalmente ativas no seu comportamento e integridade.",
            "test_prompt": smoke_prompt,
            "acceptance_criteria": f"O agente deve demonstrar de forma clara e factual que compreende as regras e procedimentos da skill {feat_name}.",
            "remediation_tip": f"Certifique-se de que a documentação e os limites da skill {feat_name} em seu SKILL.md estão sendo estritamente seguidos."
        }

        if existing_idx is not None:
            calibration_cases[existing_idx] = case_data
        else:
            calibration_cases.append(case_data)

        fm["metadata"]["hermes"]["calibration"] = calibration_cases

        # Dump back to YAML and save file
        new_fm_text = yaml.dump(fm, allow_unicode=True, sort_keys=False).strip()
        new_content = f"---\n{new_fm_text}\n---\n{body_text}"
        skill_file.write_text(new_content, encoding="utf-8")
        print(f"✅ Updated {skill_name} with defaults successfully.")

    print("Migration complete!")

if __name__ == "__main__":
    main()
