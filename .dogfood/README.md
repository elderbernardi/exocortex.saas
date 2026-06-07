# Dogfood Conversacional Reprodutível

Esta pasta contém o harness local para testar features do Exocórtex por experiência de uso, não por checklist declarativo.

## Conceito

Cada `EX-NN` tem um cenário conversacional em `.dogfood/scenarios/`. O runner cria uma execução local em `.dogfood/runs/` com:

- `scenario.yaml`
- `prompt.md`
- `transcript.md`
- `tool_trace.jsonl`
- `result.json`
- `evidence.md`
- `draft-issue.md` quando o status for `PARTIAL`, `FAIL` ou `BLOCKED`

## Status permitidos

- `PASS`: todos os critérios obrigatórios têm evidência positiva.
- `PARTIAL`: há execução ou estrutura, mas falta evidência para aprovação completa.
- `FAIL`: a feature quebrou ou violou contrato.
- `BLOCKED`: dependência externa, credencial, fixture ou sandbox ausente impede teste justo.

Regra central: ausência de evidência nunca vira `PASS`.

## Comandos

Validar catálogo P0/P1 inicial:

```bash
./scripts/test-registry.sh dogfood-catalog
```

Rodar dogfood P0/P1 em modo seguro:

```bash
./scripts/test-registry.sh dogfood-p0
```

Rodar EX-08 com instância Hermes real isolada, sem toolset de mensagens:

```bash
./scripts/test-registry.sh dogfood-real-ex08
```

Rodar P0 com instância Hermes real isolada e probes determinísticos:

```bash
./scripts/test-registry.sh dogfood-real-p0
```

Rodar uma feature diretamente em dry-run:

```bash
python scripts/dogfood_features.py run EX-08 --dry-run-agent
```

Rodar uma feature diretamente com agente real:

```bash
python scripts/dogfood_features.py run EX-08 --real-agent
```

Gerar resumo de um run:

```bash
python scripts/dogfood_features.py summarize .dogfood/runs/<run-id>
```

## Política Draft-First

Cenários que mencionam ação externa não podem enviar mensagem, email, calendário, commit, push, deploy ou publicação real. O runner registra DRAFT, evidência local e rascunho de issue. Ação externa continua dependendo de aprovação humana explícita.

## Escopo atual

Implementação inicial cobre:

- EX-08 — Draft-First
- EX-25 — Google Drive
- EX-30 — Browser automation
- EX-33 — Codex Core Harness

Próximo incremento: completar cenários EX-01 a EX-35 e ligar execução conversacional real via subagentes com trace auditável.
