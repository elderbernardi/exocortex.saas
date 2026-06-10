# Heredoc + Python Patch: Escaping Recipe

Goal: avoid `SyntaxError` when injecting Python code with backslashes via `<<'PY'` in bash.

## The Problem

When `setup.sh` uses `<<'PY'` (single-quoted heredoc) to embed a Python script,
the Python string inside the heredoc **is not** interpreted by bash. But when writing the
replacement string for a Python regex, the required escaping level is double:

1. The Python source code needs `\\` to represent a literal `\`
2. But since the heredoc is read as raw text, the string needs to contain **exactly** the
   characters that Python will interpret

## The Rule

For `replace('\\', '\\\\')` in generated Python code (escape backslash + escape single quotes):

```python
# WRONG (triple-quote, non-raw):
replacement = '''...
        escaped = args.query.replace("\\\\", "\\\\\\\\").replace("'", "\\\\'")
...'''
# Result: SyntaxError in target file — the string's Python interprets escapes BEFORE
# inserting into text, producing the wrong number of backslashes.

# CORRECT (raw triple-quote):
replacement = r'''...
        escaped = args.query.replace('\\', '\\\\').replace("'", "\\'")
...'''
```

The difference: `r'''...'''` (raw) preserves characters **exactly as written**,
without interpreting `\` as escape. The text injected into the target file will be:

```python
escaped = args.query.replace('\\', '\\\\').replace("'", "\\'")
```

Which is valid Python: `\\` → literal `\`, `\\\\` → literal `\\`.

## Checklist When Writing Python Patches in Bash Heredoc

1. Always use `r'''...'''` (raw triple-quote) for the replacement string
2. Inside the raw string, write Python code as it should appear in the final file
3. DO NOT use `"\\\\\\\\\\\\\\\\\\"` — this is confusing and almost always wrong
4. Test: `python -m py_compile <generated_file>` after the patch

## Idempotency Detection

DO NOT use a loose substring as detector:

```python
# WRONG: false positive if substring appears outside target block
if "trashed = false" in text:
    print("ALREADY")

# CORRECT: compare full block after re.subn
new_text, count = re.subn(pattern, replacement, text, flags=re.MULTILINE)
if new_text == text:
    # Check if ALREADY (already correct) or SKIP (block not found)
    try:
        py_compile.compile(str(path), doraise=True)
    except py_compile.PyCompileError:
        print("SKIP")  # Correct state but invalid from other error
    else:
        print("ALREADY")  # Correct state and compilable
```

## Reference

The 2026-06-07 session that fixed `setup.sh` in exocortex.saas went through ~5 escaping
attempts before finding the correct combination. The final version uses `r'''` and `new_text == text`.