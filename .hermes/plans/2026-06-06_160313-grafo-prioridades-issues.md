# Grafo de prioridades e dependências das issues abertas

Goal: transformar o backlog atual em sequência operacional para iniciar desenvolvimento com menor risco e maior efeito sistêmico.

Contexto:
- Baseado nas issues abertas do repositório elderbernardi/exocortex.saas em 2026-06-06.
- Leitura feita a partir de títulos, labels e corpos disponíveis via `gh issue list --json`.
- O grafo abaixo representa dependência prática de desenvolvimento, não dependência formal do GitHub.

## Snapshot por prioridade

P0
- #35 Draft-First não bloqueia envio externo em conversa real via subinstância
- #36 Google Drive quebra por SyntaxError em google_api.py
- #29 Criar roteador determinístico de modelos free do OpenRouter com fallback por competência

P1
- #41 Production skills têm lacunas entre promessa e execução nominal
- #40 Kanban não preserva blocked
- #39 NotebookLM bloqueado por auth HTTP 400 e ausência de uv
- #38 Browser Automation bloqueada por ausência de uv e path divergente
- #37 Harness infra passa em checks determinísticos sem provar comportamento central
- #28 Mapear comportamento do gateway Telegram com sudo e múltiplas instâncias Hermes
- #27 Corrigir inconsistência de namespace de skills entre exocortex e excrtx
- #25 Configurar Hindsight como memory provider padrão e documentar credenciais no setup
- #24 Instalar gcloud e fechar fluxo de autenticação Google usado pelo Exocórtex
- #22 Avaliar Syncthing como alternativa ao Google Drive para sincronização de artefatos e drafts
- #21 Harness de verificação pós-provisionamento: testar cada feature EX-01 a EX-35
- #13 Implementar Macro Tutor de bootstrap autoconsciente para o modo de inicialização
- #12 Corrigir a modelagem do exocortex-ops: estrutura canônica vs. snapshot operacional
- #11 Corrigir drift de paths do DocBrain entre skill, documentação e runtime
- #10 Unificar a fonte de verdade de modelo/profile nos registros operacionais
- #5 Slash commands /xc não estão funcionando
- #4 Setup de segurança da VPS
- #3 Configurar e automatizar o uso de UI web e desktop

P2
- #43 Artifact ID preserva acento no slug
- #42 Design System tem mismatch entre contrato, path real e operações
- #33 Considerar perfil Hermes convencional
- #31 Converter aprendizados de usuários do Hermes em documentação e ações
- #30 Avaliar inclusionai/ring-2.6-1t:free
- #26 Documentar habilitação de multiagentes e definir papel no harness
- #23 Avaliar Terrarium
- #20 Forçar respostas e mensagens do agente Hermes em PT-BR
- #19 Documentar conceito de Microverso
- #18 Skill para gerar identidade visual automaticamente
- #17 Criar identidade visual para o Exocórtex
- #16 Inicializar um MEMORY.md auditável
- #15 Criar uma persona tutora para ensinar o uso do Exocórtex sobre o Hermes
- #14 Implementar onboarding constitucional que arquiva o Macro Tutor e promove o Macroverso do executivo
- #9 Avaliar Firecrawl local
- #8 Manual do Acervo via Obsidian
- #7 Verificar permissões entre Microversos
- #6 Orquestração dinâmica de vetores usando /personality
- #2 Adicionar servidor MCP da Wikipedia

## Grafo executivo

Legenda:
- `->` depende operacionalmente de
- `[merge?]` indica provável sobreposição/need de consolidação
- `(track)` indica trilha paralela possível

```text
Fundação de segurança e verdade operacional
#35 Draft-First ──┐
#40 Kanban blocked ├─> #37 Harness comportamental ─> #21 Harness pós-provisionamento ─> #41 Production skills
#10 Fonte de verdade ┘
#27 Namespace skills ────────────────────────────────┘

Trilha Google / integrações
#36 Google Drive SyntaxError ─> #24 gcloud/auth Google ─┬─> #39 NotebookLM
                                                         ├─> #22 Syncthing vs Drive
                                                         └─> #25 Hindsight setup docs (parcialmente paralelo)

Trilha toolchain/browser
#27 Namespace skills ─┬─> #38 Browser Automation
                      └─> #11 DocBrain path drift
#38 Browser Automation ─> #9 Firecrawl local (opcional)

Trilha onboarding e identidade
#13 Macro Tutor ─┬─> #14 Onboarding constitucional
#15 Persona tutora [merge?] ┘
#14 Onboarding constitucional ─> #20 PT-BR
#16 MEMORY auditável ──────────┘
#12 exocortex-ops modelagem ───┘

Trilha superfície / operação
#5 Slash commands /xc ─> #6 Vetores via /personality
#3 UI web/desktop ─────> #6 Vetores via /personality (opcional)
#4 VPS hardening ──────> implantação segura das superfícies
#28 Gateway Telegram multi-instância ─> consolidação operacional de comunicação externa

Trilha modelos e pesquisa
#29 Roteador OpenRouter free ─> #30 Avaliar ring-2.6-1t
#31 Lições do Reddit ─────────> docs/setup/skills transversais
#2 MCP Wikipedia, #23 Terrarium, #26 multiagentes = extensões não-críticas

Trilha acabamento / consistência
#42 Design System mismatch ─> #17 Identidade visual ─> #18 Brandkit
#43 Slug ASCII-safe = fix isolado, pode entrar cedo como quick win
#8 Obsidian, #19 Microverso = documentação estrutural
#7 Permissões = governança estrutural
```

## Dependências práticas mais fortes

1. #35 -> #37 -> #21
   Motivo: não faz sentido ampliar harness antes de corrigir o bug de segurança mais grave e a metodologia de teste que hoje dá falso positivo.

2. #36 -> #24 -> #39
   Motivo: Drive está quebrado por sintaxe; depois vem auth Google; só então NotebookLM pode ser tratado com diagnóstico menos ambíguo.

3. #27 -> #38 e #11
   Motivo: namespace/path drift contamina skill loading, wrappers e documentação. Vale atacar inconsistências de contrato antes de integrar browser/docbrain.

4. #13/#15 -> #14
   Motivo: bootstrap tutor e persona tutora parecem sobrepostos. Definir e consolidar isso antes do onboarding constitucional evita retrabalho.

5. #37 -> #41
   Motivo: production skills precisam de validação nominal real. Primeiro arruma o harness que detecta a falha; depois corrige cada skill com confiança.

6. #5 -> #6
   Motivo: não vale sofisticar orquestração com `/personality` se a superfície de slash commands ainda falha.

7. #42 -> #17 -> #18
   Motivo: design contract primeiro; identidade aplicada depois; automação de brandkit por último.

## Caminho recomendado para iniciar desenvolvimento

### Fase 0 — sanear o que invalida confiança do sistema
1. #35 Draft-First
2. #37 Harness comportamental falso-positivo
3. #21 Harness EX-01..EX-35
4. #40 Kanban blocked
5. #10 Fonte de verdade modelo/profile
6. #27 Namespace de skills

Saída esperada:
- o sistema para de executar side effects indevidos
- o harness passa a provar comportamento, não só presença
- o backlog restante fica mensurável

### Fase 1 — destravar integrações que hoje quebram nominalmente
7. #36 Google Drive SyntaxError
8. #24 gcloud/auth Google
9. #39 NotebookLM auth + uv
10. #38 Browser Automation + uv + path
11. #11 DocBrain path drift
12. #41 Production skills nominal flow

Saída esperada:
- integrações principais deixam de falhar por setup/path/syntax
- produção de artefatos e automações viram trilha executável

### Fase 2 — consolidar superfície operacional
13. #5 Slash commands /xc
14. #3 UI web/desktop
15. #4 Segurança da VPS
16. #28 Gateway Telegram multi-instância

Saída esperada:
- canais de operação estáveis
- hardening mínimo para rodar com menos risco

### Fase 3 — fechar identidade/onboarding do produto
17. Resolver overlap entre #13 e #15
18. #13 Macro Tutor
19. #14 Onboarding constitucional
20. #16 MEMORY auditável
21. #20 PT-BR
22. #12 Modelagem exocortex-ops

Saída esperada:
- narrativa de produto e onboarding coerentes
- memória e ops modeladas de forma auditável

### Fase 4 — research e extensões
23. #29 Roteador OpenRouter free
24. #30 Avaliação ring-2.6-1t
25. #22 Syncthing vs Drive
26. #31 lições do Reddit promovidas para docs/setup
27. #26 multiagentes
28. #23 Terrarium
29. #9 Firecrawl
30. #2 MCP Wikipedia

### Fase 5 — acabamento e consistência de produto
31. #42 Design System
32. #17 Identidade visual
33. #18 Brandkit
34. #43 slug ASCII-safe
35. #8 manual Obsidian
36. #7 permissões entre microversos
37. #19 documentação do conceito de microverso
38. #33 perfil Hermes convencional

## Recomendações de execução imediata

Escolha A — menor risco, maior efeito sistêmico
- começar por #35, #37, #21
- razão: corrige guardrail crítico e cria radar confiável para o resto

Escolha B — destravar integrações principais
- começar por #36, #24, #39, #38
- razão: reduz a quantidade de features “instaladas mas não operacionais”

Escolha C — fechar narrativa do produto
- começar por consolidar #13 + #15, depois #14 e #16
- razão: bom para onboarding e posicionamento, mas não remove os maiores riscos técnicos

## Minha recomendação

Opção A primeiro, com esta ordem exata:
1. #35
2. #37
3. #21
4. #40
5. #10
6. #27
7. #36
8. #24
9. #39
10. #38

Isso cria uma espinha dorsal: segurança -> prova real -> observabilidade -> integrações.
