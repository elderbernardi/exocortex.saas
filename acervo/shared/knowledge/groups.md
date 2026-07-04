---
type: knowledge
title: Shared Access Groups
description: Define aliases para controle de acesso (firewall) entre Microversos.
tags: []
timestamp: 2026-05-27
class: volátil
created_at: 2026-05-27T04:03:03Z
last_accessed_at: 2026-05-27T04:03:03Z
deprecated: true
deprecated_at: "2026-07-04T00:00:00Z"
deprecated_reason: "Superseded por shared/groups.md, registro canônico único de grupos de microversos. Taxonomia ALL/CLIENTS/PROJECTS obsoleta; membro cliente-alfa não existe em acervo/micro/."
---

# Shared Access Groups

> **Superseded by:** [`shared/groups.md`](../groups.md) — registro canônico único de grupos (2026-07-04).

> Define aliases para controle de acesso (firewall) entre Microversos.
> Usado em tarefas com scope restrito via deny/allow.
> Regra de ouro: allow SEMPRE sobrescreve deny.

## Built-in Aliases

### ALL
Todos os Microversos existentes. Atualizado automaticamente.
```yaml
members: auto  # Populated dynamically from micro/ directory listing
```

### CLIENTS
Microversos do tipo `client`.
```yaml
members: [cliente-alfa]  # Auto-populated: all micro/ where SCHEMA.md type: client
```

### PROJECTS
Microversos do tipo `project`.
```yaml
members: []  # Auto-populated: all micro/ where SCHEMA.md type: project
```

## Custom Groups

<!-- Adicionar grupos customizados aqui. Exemplo:
### CONFIDENTIAL
Microversos com dados sensíveis que requerem isolamento extra.
```yaml
members: [cliente-alfa, cliente-beta]
```
-->

## Usage

Nas tarefas, restringir acesso com:
```yaml
scope:
  deny: [ALL]           # Bloqueia todos os Microversos
  allow: [cliente-acme] # Exceto ACME — allow sobrescreve deny
```

Ou usar aliases de grupo:
```yaml
scope:
  deny: [CLIENTS]       # Bloqueia clientes
  allow: [PROJECTS]     # Permite projetos
```

**Default:** Se nenhum scope é definido, acesso é ABERTO a todos os Microversos.
