# ADR-002: Isolamento de Contexto entre Microversos

> **Status:** Aceita
> **Data:** 2026-05-26
> **Decisor:** @elder
> **Contexto:** Sessão PDD P2_MEMORY — proteção contra poluição de contexto

---

## Contexto

Microversos representam **workspaces isolados**: clientes, projetos, domínios ou papéis. Quando uma tarefa cruza múltiplos Microversos (ex: preparar budget que envolve Financeiro + Produto), há risco de poluição de contexto — informações de um domínio vazando para outro.

O cenário mais grave: informações confidenciais de um cliente (Cliente A) vazam para outro (Cliente B) porque uma tarefa anterior manipulou ambos os contextos.

## Decisão

### Regra 1: Filtro de Domínio na Escrita

Antes de escrever em qualquer Microverso, o agente aplica:

```
1. Conteúdo é específico deste domínio? → micro/{slug}/{nature}
2. É cross-domain? → shared/cross-refs/ + ponteiro
3. Pertence a outro micro? → micro/{outro}/{nature}
4. É universal? → global/{nature}
5. Nenhum dos acima? → descartar
```

### Regra 2: Referências, Não Duplicações

- NUNCA copiar conteúdo entre Microversos
- Criar cross-ref em `shared/` + ponteiro (1 linha) em cada Microverso
- Cross-ref é nota curta (5-15 linhas), não documento formal

### Regra 3: Firewall de Acesso (Deny-list com Aliases)

Tarefas têm acesso aberto por padrão, mas podem restringir via scope:

```yaml
scope:
  deny: [ALL]              # Bloqueia tudo
  allow: [cliente-acme]    # Exceto ACME
```

**Aliases dinâmicos:**
- `ALL` — todos os Microversos
- `CLIENTS` — type: client
- `PROJECTS` — type: project
- Grupos custom em `shared/groups.md`

**Regra de precedência:** Allow SEMPRE sobrescreve Deny.

## Alternativas Rejeitadas

1. **Allow-list pura** — Rejeitada porque exige listar todos os Microversos permitidos, quebrando com cada novo Microverso criado.
2. **Sem firewall** — Rejeitada porque confidencialidade entre clientes é requisito inegociável.
3. **Isolamento total (sem cross-ref)** — Rejeitada porque há cenários legítimos de cruzamento (ex: benchmark de pricing sem nomear clientes).

## Consequências

- Cada Microverso tem `SCHEMA.md` com regras de isolamento e neighbors declarados
- `shared/groups.md` define grupos para aliases custom
- Nature skills incluem checklist de Filtro de Domínio antes de qualquer escrita
- Logs são isolados por Microverso (cada um tem seu `log.md`)

## Referências

- Plano: `artifacts/plan_wiki_alignment.md` v3
- PRD: `docs/PRD/PRD_dev_v1.md` §3 (Isolamento de Volumes)
