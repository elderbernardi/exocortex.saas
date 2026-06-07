# DRAFT — comentários de dependência para issues do GitHub

Objetivo: publicar comentários curtos nas issues-chave, explicitando dependências operacionais e o que cada uma desbloqueia.

## #35
Dependências operacionais
- Depende de: nenhuma
- Desbloqueia: #37, #21, #28
- Trilha: confiança sistêmica / segurança operacional

Critério para iniciar
- reproduzir o envio indevido sem aprovação pós-DRAFT
- corrigir a regra em fluxo principal e subinstância
- provar por trace que `send_message` não roda antes de aprovação explícita

## #37
Dependências operacionais
- Depende de: #35, #40
- Desbloqueia: #21, #41
- Trilha: confiança sistêmica / harness comportamental

Critério para iniciar
- incorporar teste de segurança conversacional do Draft-First
- diferenciar presença de feature vs comportamento real
- fazer o harness falhar quando wrappers/artefatos prometidos não existem

## #21
Dependências operacionais
- Depende de: #35, #37, #40, #10, #27
- Desbloqueia: #41, #39, #38 e validação transversal do restante do backlog
- Trilha: confiança sistêmica / verificação pós-provisionamento

Critério para iniciar
- ter cenários mínimos reais por feature crítica
- registrar PASS/PARTIAL/BLOCKED com evidência
- evitar falso positivo por discovery/transporte sem operação nominal

## #41
Dependências operacionais
- Depende de: #21, #37
- Desbloqueia: estabilização nominal de EX-23 e EX-24
- Trilha: production skills / validação nominal

Critério para iniciar
- usar harness já corrigido para reproduzir falhas reais
- separar falta de runner, falta de template e falta de dependência de ambiente
- fechar cada lacuna com evidência executável

## #40
Dependências operacionais
- Depende de: nenhuma
- Desbloqueia: #37, #21 e governança confiável do backlog
- Trilha: confiança sistêmica / kanban

Critério para iniciar
- reproduzir create blocked -> ready
- determinar se o bug é do Hermes upstream ou do uso atual
- documentar workaround só se o bug não puder ser corrigido localmente

## #10
Dependências operacionais
- Depende de: nenhuma
- Desbloqueia: #21 e troubleshooting confiável do runtime
- Trilha: observabilidade / verdade operacional

Critério para iniciar
- identificar a fonte única de verdade de modelo/profile
- alinhar self-check e registros operacionais
- provar ausência de drift após reexecução

## #27
Dependências operacionais
- Depende de: nenhuma
- Desbloqueia: #21, #38, #11
- Trilha: consistência de skills / packaging / docs

Critério para iniciar
- mapear namespace real no runtime, no setup e no repositório
- corrigir alias/path/documentação divergentes
- garantir que a nomenclatura final seja consistente na listagem e no uso real

## #36
Dependências operacionais
- Depende de: nenhuma
- Desbloqueia: #24, #39
- Trilha: Google / integrações críticas

Critério para iniciar
- corrigir o SyntaxError antes de qualquer diagnóstico de auth
- validar py_compile e um caso real de query com apóstrofo
- separar erro de código de erro de credencial ausente

## #24
Dependências operacionais
- Depende de: #36
- Desbloqueia: #39 e trilha Google Workspace/Drive
- Trilha: Google / autenticação local

Critério para iniciar
- instalar `gcloud`
- validar login local coerente com as skills Google
- documentar setup para evitar regressão em nova instalação

## #39
Dependências operacionais
- Depende de: #36, #24
- Desbloqueia: uso real de EX-28 e EX-29
- Trilha: NotebookLM / operação nominal

Critério para iniciar
- tratar `uv` como pré-requisito explícito ou instalar no setup
- validar `nlm login --check` e uma operação mínima real
- parar de considerar discovery MCP como prova suficiente de funcionamento

## #38
Dependências operacionais
- Depende de: #27
- Desbloqueia: smoke real de browser automation e avaliação opcional de #9
- Trilha: browser automation / toolchain

Critério para iniciar
- alinhar wrapper real e path documentado
- garantir `uv` disponível ou explicitar bootstrap automático
- provar smoke mínimo: abrir página, ler título, encerrar sessão

## #11
Dependências operacionais
- Depende de: #27
- Desbloqueia: manutenção e integração confiável do DocBrain
- Trilha: paths canônicos / documentação operacional

Critério para iniciar
- localizar todas as referências ativas ao DocBrain
- definir um path canônico
- revalidar a integração sem workaround manual

## Comentário-resumo sugerido para #21
Esta issue faz parte da espinha dorsal de confiança do projeto.

Trilha principal:
- #35 -> #37 -> #21 -> #41

Dependências de apoio:
- #40 para estado correto de backlog
- #10 para verdade operacional de modelo/profile
- #27 para consistência de namespace/path de skills

Objetivo desta trilha:
- fazer o harness provar comportamento real
- eliminar falso positivo operacional
- transformar o backlog restante em fila executável com evidência
