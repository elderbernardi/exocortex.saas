# Verificação de card bloqueado no Hermes Kanban

Use este padrão quando a pendência depende de decisão humana e não deve cair em execução automática.

## Sequência segura

1. Criar o card com título orientado a decisão.
2. Inserir referências obrigatórias no corpo.
3. Verificar o resultado com `kanban list` e `kanban show`.
4. Se o card não estiver em `blocked`, aplicar bloqueio explícito.
5. Verificar de novo.

## Sinal de boa qualidade

O `show` final deve deixar claro:
- status `blocked`
- resumo mais recente explicando a dependência da decisão humana
- referências suficientes para retomada sem reconstrução da sessão

## Comentário de bloqueio recomendado

```text
Aguardando decisão explícita do executivo sobre arquitetura, storage, escopo da v1 e staging privado.
```

Adapte a frase ao caso, mas mantenha o motivo concreto.

## Quando usar

- ADR proposta sem martelo final
- decisão de arquitetura
- escolha de escopo da v1
- política operacional ainda indefinida
- qualquer retomada que dependa de aprovação ou direção do executivo
