# Heredoc + Python Patch: Escaping Recipe

Objetivo: evitar `SyntaxError` ao injetar código Python com backslashes via `<<'PY'` em bash.

## O problema

Quando `setup.sh` usa `<<'PY'` (heredoc com aspas simples) para embutir um script Python,
a string Python dentro do heredoc **não** é interpretada pelo bash. Mas ao escrever a string
de substituição para um regex Python, o nível de escaping necessário é duplo:

1. O Python source code precisa de `\\` para representar um literal `\`
2. Mas como o heredoc é lido como texto puro, a string precisa conter **exatamente** os
   caracteres que o Python vai interpretar

## A regra

Para `replace('\\', '\\\\')` no código Python gerado (escapar barra + escapar aspas simples):

```python
# WRONG (triple-quote, non-raw):
replacement = '''...
        escaped = args.query.replace("\\\\", "\\\\\\\\").replace("'", "\\\\'")
...'''
# Result: SyntaxError no arquivo alvo — o Python da string interpreta os escapes ANTES
# de inserir no texto, produzindo número errado de barras.

# CORRECT (raw triple-quote):
replacement = r'''...
        escaped = args.query.replace('\\', '\\\\').replace("'", "\\'")
...'''
```

A diferença: `r'''...'''` (raw) preserva os caracteres **exatamente como escritos**,
sem interpretar `\` como escape. O texto injetado no arquivo alvo será:

```python
escaped = args.query.replace('\\', '\\\\').replace("'", "\\'")
```

Que é Python válido: `\\` → literal `\`, `\\\\` → literal `\\`.

## Checklist ao escrever patches Python em heredoc bash

1. Sempre usar `r'''...'''` (raw triple-quote) para a string de substituição
2. Dentro da raw string, escrever o código Python como ele deve aparecer no arquivo final
3. NÃO usar `"\\\\\\\\\\\\\\\\"` — isso é confuso e quase sempre errado
4. Testar: `python -m py_compile <arquivo_gerado>` após o patch

## Detecção de idempotência

NÃO usar substring solta como detector:

```python
# WRONG: falso positivo se substring aparecer fora do bloco alvo
if "trashed = false" in text:
    print("ALREADY")

# CORRECT: comparar bloco completo após re.subn
new_text, count = re.subn(pattern, replacement, text, flags=re.MULTILINE)
if new_text == text:
    # Verificar se é ALREADY (já no estado correto) ou SKIP (bloco não encontrado)
    try:
        py_compile.compile(str(path), doraise=True)
    except py_compile.PyCompileError:
        print("SKIP")  # Estado correto mas inválido por outro erro
    else:
        print("ALREADY")  # Estado correto e compilável
```

## Referência

A sessão de 2026-06-07 que corrigiu `setup.sh` do exocortex.saas passou por ~5 tentativas
de escaping antes de encontrar a combinação correta. A versão final usa `r'''` e `new_text == text`.