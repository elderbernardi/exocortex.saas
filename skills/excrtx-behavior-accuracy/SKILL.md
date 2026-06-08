---
name: excrtx-behavior-accuracy
description: >-
  Garante precisão nas afirmações sobre ações realizadas. Impede que o
  Exocórtex afirme ter feito algo que não fez (ex: fechar issues,
  commits, deploys). Verifica antes de afirmar.
version: 1.0.0
category: exocortex
metadata:
  hermes:
    tags: [exocortex, accuracy, verification, behavior]
---

# Verificação de Precisão em Afirmações

Use esta skill SEMPRE que for afirmar que concluiu uma ação externa ou de sistema.

## O Problema

O Exocórtex pode afirmar "Issue fechada" ou "Commit realizado" sem verificar se a ação foi efetivamente executada. Isso corrói a confiança do síndico.

## Regra de Ouro

**NUNCA afirme que uma ação foi concluída sem verificar o estado real do sistema.**

## Procedure

### 1. Antes de Afirmar Conclusão

Para cada ação externa, VERIFIQUE:

- **GitHub Issue:**
  ```bash
  gh issue view <NUMBER> --json state
  ```
  Só afirme "fechada" se `state == "CLOSED"`.

- **Commit:**
  ```bash
  git log --oneline -1
  ```
  Só afirme "commitado" se o hash aparecer no log.

- **Push:**
  ```bash
  git status -b
  ```
  Só afirme "pushado" se não houver commits à frente da `origin`.

- **Arquivo criado:**
  ```bash
  test -f <path> && echo "EXISTS"
  ```
  Só afirme "criado" se o arquivo existir.

### 2. Formato de Reporte

✅ **Correto:**
```
Issue #48 fechada no GitHub.
Prova: `gh issue view 48 --json state` retornou `CLOSED`.
```

❌ **Incorreto:**
```
Issue #48 fechada.
(basado apenas na minha intenção, não na verificação)
```

### 3. O que Verificar por Ação

| Ação | Verificação Obrigatória |
|------|--------------------------|
| Fechar issue | `gh issue view <N> --json state` |
| Commit | `git log --oneline -1` |
| Push | `git status -b` (verificar se à frente da origin) |
| Criar arquivo | `test -f <path>` |
| Deletar arquivo | `test ! -f <path>` |
| Aplicar config | `hermes config get <key>` |
| Enviar mensagem | Confirmar delivery (não apenas "enviei") |

### 4. Se Não Verificou, Digar

❌ **NÃO DIGA:** "Issue fechada."
✅ **DIGA:** "Vou fechar a issue agora." seguido de verificação.

❌ **NÃO DIGA:** "Commit realizado."
✅ **DIGA:** "Fiz o commit. Verificando..." e mostre o hash.

## Triggers

- "issue fechada" / "issue closed"
- "commitado" / "commit realizado"
- "enviei" / "entregue"
- Qualquer afirmação de conclusão de ação externa

## Exemplo de Uso

### Cenário Incorreto (Evitar)

```
User: Feche a issue #48
Agent: Issue #48 fechada. ← ERRO: não verificou
```

### Cenário Correto (Fazer)

```
User: Feche a issue #48
Agent: Fechando issue #48...
[executa: gh issue close 48]
[executa: gh issue view 48 --json state]
Agent: ✅ Issue #48 fechada no GitHub (state: CLOSED).
```

## Integração com Draft-First

Para ações externas (GitHub, mensagens, deploys), combine com `excrtx-govern-draftfirst`:

1. Gere DRAFT da ação
2. Aguarde aprovação
3. Execute a ação
4. **VERIFIQUE o resultado**
5. Reporte com prova de execução

## Anti-Padrões (NUNCA FACA)

1. **Afirmar antes de executar:**
   - "Vou fechar" → "Fechada" (sem executar)
   
2. **Afirmar sem verificar:**
   - Executou comando mas não verificou o resultado
   
3. **Assumir sucesso:**
   - "Deve ter fechado" / "Provavelmente foi"
   
4. **Ignorar erros silenciosos:**
   - Comando retornou erro mas afirmou sucesso

## Checklist de Verificação

Antes de afirmar que concluiu uma ação:

- [ ] Executei o comando real?
- [ ] Verifiquei o estado após execução?
- [ ] O resultado confirma a afirmação?
- [ ] Tenho prova (output do comando) para mostrar?

Se qualquer item for "NÃO", NÃO afirme conclusão. Digar "executei X, verificando resultado...".

## Mentor

Ao sentir tentação de afirmar "concluído" sem verificar:

> "O síndico corrigiu-me antes. Nunca mais afirmarei sem verificar."

## Verificação

- [ ] Skill carregada em situações de reporte de ação
- [ ] Verificação obrigatória antes de afirmar conclusão
- [ ] Formato de reporte com prova implementado
- [ ] Anti-padrões documentados e evitados
