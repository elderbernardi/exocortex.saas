# Shared Access Groups

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
