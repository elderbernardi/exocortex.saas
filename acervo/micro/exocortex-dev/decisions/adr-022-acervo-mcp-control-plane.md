---
type: decision
title: ADR-022 — Acervo MCP Control Plane
description: Filesystem é verdade física; core semântico local governa mutações agentic do Acervo via CLI e MCP.
tags:
- acervo
- mcp
- cli
- control-plane
- architecture
- microversos
timestamp: '2026-06-28'
class: perene
created_at: '2026-06-28T18:13:31Z'
nature: decisions
excrtx_type: decision
confidence: high
status: accepted
scope_slug: exocortex-dev
---

# ADR-022 — Acervo MCP Control Plane

## Status

Accepted.

## Contexto

O Acervo já possui uma semântica forte de memória: quatro camadas (`macro`, `global`, `micro`, `shared`), filtragem por domínio, frontmatter canônico, validação e logging. O problema atual não é ausência de estrutura documental. O problema é ausência de uma **autoridade operacional única** para mutações semânticas.

Hoje, a escrita agentic do Acervo pode surgir de múltiplos lugares:

- scripts ad hoc
- skills que descrevem a política
- convenções em README/planos
- validações executadas depois da escrita

Esse desenho cria drift entre intenção e execução: a regra existe, mas não está consolidada num plano de controle reutilizável.

Ao mesmo tempo, o estado da arte em memória para agentes resolve outro pedaço do problema. Trabalhos como **MemGPT** e **MemoryOS** tratam hierarquia, troca entre camadas de memória e retenção de contexto pessoal. O **MCP**, por sua vez, padroniza transporte e descoberta de capacidades entre hosts, clientes e servidores. Nenhum desses componentes, isoladamente, resolve a governança semântica do Acervo.

A tese operacional passa a ser esta:

> o valor do MCP do Acervo não é dar acesso a arquivos; é expor operações semânticas estáveis sobre memória canônica já estruturada por macroverso e microversos.

## Decisão

Adotar um **Acervo MCP Control Plane** com quatro camadas distintas:

| Camada | Papel | Autoridade |
|---|---|---|
| Filesystem | Persistência final dos arquivos do Acervo | Verdade física |
| Core semântico local | Resolve escopo, valida, prepara, comita, indexa e loga | Verdade operacional |
| CLI local (`acervoctl`) | Superfície oficial para humano, testes e scripts | Interface local |
| Servidor MCP (`acervo-mcp`) | Superfície oficial para agentes Hermes | Interface agentic |

### Regra-mãe

**Agentes escrevem conhecimento canônico do Acervo via plano de controle semântico.**

### Exceções permitidas

Escrita direta em arquivo continua permitida para:

- humano
- scripts de infraestrutura
- manutenção corretiva
- refactors estruturais do repositório
- operações fora do escopo semântico do Acervo

### Invariantes

1. O filesystem continua sendo a fonte de verdade física.
2. O core semântico local é a única fonte de regra para mutações semânticas.
3. CLI e MCP chamam o mesmo core; não duplicam regra de negócio.
4. O servidor MCP não é editor genérico de arquivos.
5. Escritas semânticas relevantes usam duas fases: `prepare` e `commit`.
6. Escritas cross-microverso não duplicam conteúdo; usam referência, promoção controlada ou ponte em `shared/`.

## Arquitetura operacional

### Fluxo de escrita

```text
Agent/Humano/Script
  -> acervoctl ou acervo-mcp
  -> semantic core
  -> scope guard + validators + index/log
  -> filesystem
```

### Contrato mínimo do core

O core deve concentrar, no mínimo:

- `resolve_acervo_root()`
- `resolve_active_microverso()`
- `guard_write_scope()`
- `prepare_write()`
- `commit_write()`
- `validate_entry()`
- `update_index()`
- `append_log()`
- `build_receipt()`

### Modelo de mutação

**Prepare**
- resolve destino
- valida escopo
- monta frontmatter
- calcula diff/receipt
- acusa conflito antes da gravação

**Commit**
- grava no path final
- revalida frontmatter e contrato
- atualiza `_meta/index.md`
- atualiza `_meta/log.md`
- retorna receipt verificável

### Superfície mínima do MCP

No primeiro corte, o servidor deve expor apenas intenções semânticas:

- `acervo_list_microversos`
- `acervo_search`
- `acervo_read_page`
- `acervo_prepare_write`
- `acervo_commit_write`
- `acervo_create_entry`
- `acervo_update_entry`
- `acervo_validate_scope`
- `acervo_validate_frontmatter`
- `acervo_export_microverso`

Tudo o que for edição arbitrária de arquivo (`write_file`, `patch_file`, `rm`, `mv`) permanece fora do escopo do servidor.

## Consequências

### Positivas

- Consolida a autoridade operacional numa library local verificável.
- Permite governança semântica sem matar o acesso humano ao filesystem.
- Desacopla semântica de transporte: o core vive sem MCP; o MCP apenas o expõe.
- Reduz drift entre skill, documentação e implementação real.
- Cria uma trilha auditável para mutações agentic (`prepare`, `commit`, `receipt`, `log`).

### Custos

- Introduz atrito saudável na escrita agentic: nem toda mutação vira `write_file` direto.
- Exige manutenção de contratos, validadores e testes de paridade entre core, CLI e MCP.
- Obriga migração gradual de clientes reais para o novo caminho oficial.

### Riscos

1. **MCP virar editor genérico de arquivos**  
   Contramedida: restringir o servidor a operações semânticas.

2. **Duplicação de regra entre core, CLI e MCP**  
   Contramedida: qualquer lógica relevante deve viver no core.

3. **Fragmentação entre microversos**  
   Contramedida: formalizar quando referenciar, quando promover e quando manter isolamento.

4. **Governança só no papel**  
   Contramedida: migrar ao menos um cliente real (`docbrain_to_acervo.py`) no primeiro ciclo.

## Relação com o estado da arte

Esta ADR não propõe um novo algoritmo de memória. Ela propõe uma disciplina de sistema.

- **MemGPT** oferece um modelo forte de hierarquia operacional de memória.
- **MemoryOS** reforça a ideia de camadas, atualização e memória pessoal persistente.
- **MCP** padroniza o protocolo entre aplicação e ferramentas.

A contribuição específica do Exocórtex está em outro ponto:

> combinar separação estrutural por macroverso/microversos, governança de escrita, auditabilidade em filesystem e exposição protocolar fina via CLI/MCP.

## Critérios de aceite

- [ ] Existe um core local que executa mutação semântica sem depender de MCP.
- [ ] Existe uma CLI local com saída estável para `prepare` e `commit`.
- [ ] Existe um servidor MCP fino, com paridade funcional com a CLI para o mesmo input.
- [ ] A política de uso fica explícita: humano e infra podem editar arquivo; agente semântico deve preferir CLI/MCP.
- [ ] Pelo menos um cliente real do repositório migra para o novo caminho oficial.
- [ ] Há testes de sucesso e falha cobrindo `scope`, `frontmatter`, `index`, `log` e `cross-microverso write`.

## Referências

### Internas

- `.hermes/plans/2026-06-28_174717-acervo-mcp-control-plane.md`
- `acervo/micro/exocortex-dev/decisions/skill-vs-mcp-selection.md`
- `acervo/micro/exocortex-ops/knowledge/mcp-registry.md`
- `FEATURES.md` (EX-06, EX-11)

### Externas

- Packer et al., *MemGPT: Towards LLMs as Operating Systems* — arXiv:2310.08560
- Kang et al., *Memory OS of AI Agent* — arXiv:2506.06326
- Model Context Protocol — Architecture overview and Specification
