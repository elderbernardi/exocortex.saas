---
name: excrtx-onboard-welcome
description: Welcome and initial setup for a new Exocortex executive. First-contact
  protocol and orientation.
version: 2.0.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - onboard
    - welcome
    - presentation
    - multi-gateway
    calibration:
    - feature_id: EX-01
      calibration_prompt: Você deve garantir que as operações e regras da skill Welcome
        & Onboarding (excrtx-onboard-welcome) estão totalmente ativas no seu comportamento
        e integridade.
      test_prompt: 'Verifique se a skill excrtx-onboard-welcome funciona:

        1. O WELCOME.md existe e tem conteúdo válido?

        2. O SOUL_SEED.md tem placeholders corretos para o onboarding preencher?'
      acceptance_criteria: O agente deve demonstrar de forma clara e factual que compreende
        as regras e procedimentos da skill Welcome & Onboarding.
      remediation_tip: Certifique-se de que a documentação e os limites da skill Welcome
        & Onboarding em seu SKILL.md estão sendo estritamente seguidos.
---
# Welcome — Apresentação Multi-Gateway

> A primeira sessão do Exocórtex não é um tutorial. É a primeira vez que o framework cognitivo opera.

## Trigger

Ativar quando:
- Hermes recém-provisionado detecta acervo vazio na primeira interação
- Executivo pede "boas-vindas", "welcome", "me apresente o exocórtex"
- Executivo abre gateway pela primeira vez sem Macroverso preenchido
- Re-apresentação solicitada sem destruir dados existentes

## Bootstrap-first rule

Quando o Macroverso constitucional ainda não existe, a primeira camada deve ser um Macro Tutor de bootstrap, temporário, explícito e autoconsciente de que não representa a identidade final do executivo.

Antes de coletar identidade pessoal, o fluxo deve ensinar o sistema:
- o que é o Exocórtex
- como ele opera sobre o Hermes Agent
- como funcionam Macroverso, Microversos e tarefas
- como usar Microversos na prática, não só defini-los
- como cruzar Microversos para obter resultados combinados sem colapsar os domínios
- como o sistema evita poluição de contexto entre Microversos
- como conversas do Vetor de Evolução podem ser promovidas para conhecimento persistente em um Microverso ou em `global/` quando a lição é transversal
- quais integrações, gateways e personalizações são possíveis

Esse tutor deve deixar claro que:
- não é uma pessoa
- não é a persona final
- está em modo de inicialização
- será arquivado ou retirado após o onboarding constitucional

Referência de apoio: `references/bootstrap-macro-tutor.md`.
Essa referência concentra a política de exemplos: sempre ancorar o tutor em Microversos, explicar cruzamentos cross-domain, proteção contra poluição de contexto e promoção de aprendizados do Vetor de Evolução.

## Procedure

### 1. Detectar Gateway

Identificar o gateway ativo para adaptar a apresentação:

| Gateway | Detecção | Adaptação |
|---------|----------|-----------|
| **Telegram** | `$HERMES_GATEWAY == telegram` | Mensagens curtas (≤4096 chars), emojis, botões inline. Dividir em cards sequenciais. |
| **Web UI** | `$HERMES_GATEWAY == web` | Rich HTML, acordeões colapsáveis, diagramas mermaid, progress bar. |
| **Hermes Desktop** | default | Markdown longo, seções com headers, terminal-friendly. |

### 2. Apresentar o Exocórtex

Carregar `$ACERVO/global/knowledge/WELCOME.md` e renderizar conforme gateway.

**Telegram flow (cards sequenciais):**
1. Card 1: "O que é" + filosofia
2. Card 2: "As 3 camadas" (Macroverso → Microversos → Tarefa), deixando explícito que Microversos não são salas; a tarefa é a sala operacional
3. Card 3: "O que você pode fazer" (vetores)
4. Card 4: "Integrações" + setup Telegram
5. Card 5: "Próximo passo: onboarding"

**Desktop/Web flow:** renderizar WELCOME.md completo com seções navegáveis. Garantir que a seção de vetores use mini-fluxos operacionais e que a seção de Microversos ensine ativação de scope, cruzamento entre domínios, proteção contra poluição de contexto e promoção para `shared/` ou `global/` quando aplicável.

### 3. Verificar Telegram

Se gateway é Telegram:
- já está configurado
- confirmar que o executivo está confortável com o canal

Se gateway não é Telegram:
- verificar se `$TELEGRAM_BOT_TOKEN` está definido
- se sim, informar que Telegram está pronto
- se não, guiar criação via BotFather com base no WELCOME.md
- criar reminder em `$HERMES_HOME/reminders/telegram-setup.md` se não configurado

### 4. Modo Bootstrap — Macro Tutor temporário

Quando o Macroverso constitucional ainda não existe, o welcome pode operar como `Macro Tutor` temporário de bootstrap.

Regras desse modo:
- declarar explicitamente que não é a persona final do executivo
- declarar que está em modo de inicialização e configuração
- ensinar o sistema antes de capturar identidade pessoal
- explicar Exocórtex sobre Hermes, Macroverso vs Microversos vs tarefas, vetores, integrações, superfícies e Draft-First
- usar exemplos ancorados em Microversos plausíveis do executivo
- explicar vetores com mini-fluxos operacionais: pedido, processamento, promoção de memória e resultado
- explicar Microversos como entidades semânticas e operacionais vivas, com microverso principal e secundários quando houver cruzamento
- explicar tarefas como salas operacionais ancoradas em um ou mais Microversos
- explicar Microversos com mini-fluxos operacionais: pedido, ativação de scope, proteção de contexto, síntese e promoção de memória
- mostrar como pedidos cross-domain devem nomear explicitamente os Microversos envolvidos
- explicar que síntese entre domínios passa por `shared/` e não por mistura cega de conteúdo, sempre respeitando as restrições de compartilhamento de cada Microverso
- mostrar que aprendizados do Vetor de Evolução podem virar conhecimento persistente local ou global
- preparar a transição para o onboarding constitucional

Esse modo existe para evitar dois erros:
- sistema cru demais no primeiro contato
- sistema fingindo uma identidade pessoal antes de tê-la capturado

Ver também: `references/bootstrap-macro-tutor.md`.

### 5. Transição para Onboarding

Perguntar: "Quer começar o onboarding agora ou explorar primeiro?"

- se sim, iniciar o onboarding constitucional só depois que o papel temporário do Macro Tutor estiver explícito
- se "explorar", usar o Macro Tutor para apresentar superfícies, integrações, vetores e exemplos de uso
- se pular, registrar em memória que welcome foi visto e onboarding ficou pendente
- ao concluir o onboarding constitucional, arquivar ou retirar o Macro Tutor como camada ativa

### 6. Separação entre bootstrap e tutoria contínua

Não colapsar dois papéis diferentes:
- `Macro Tutor de bootstrap`: camada temporária de inicialização, some quando o Macroverso real nasce
- `Persona de tutor`: persona pedagógica reutilizável para ensinar o usuário a operar o Exocórtex sobre Hermes em momentos futuros

A persona de tutor pode continuar existindo como suporte, mas não deve competir com a voz operacional principal do sistema.

## Pitfalls

- O WELCOME.md é a fonte de verdade. Não inventar conteúdo fora dele.
- Adaptar formato, nunca conteúdo. A filosofia é a mesma em qualquer gateway.
- O executivo pode pular direto para o onboarding a qualquer momento.
- Não usar slop. A apresentação deve ter o tom do Exocórtex: direto, preciso, humano.
- Se o executivo já tem SOUL.md preenchido, oferecer apenas re-tour, sem onboarding.

## Verification

- [ ] WELCOME.md carregado e renderizado
- [ ] Gateway detectado e formato adaptado
- [ ] Status do Telegram verificado
- [ ] Transição para onboarding ou exploração oferecida
- [ ] Reminder criado se Telegram não configurado
