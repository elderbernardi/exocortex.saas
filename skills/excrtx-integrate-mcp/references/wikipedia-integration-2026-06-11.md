# Wikipedia MCP Integration — 2026-06-11

## Escopo

Adicionar servidor MCP Wikipedia (Rudra-ravi/wikipedia-mcp) ao Hermes Agent conforme issue #2 do repositório exocortex.saas.

## Comandos Executados

### Instalação
```bash
pip install wikipedia-mcp
# wikipedia-mcp-2.0.1, wikipedia-api-0.15.0
```

### Configuração via CLI — FALHOU
```bash
hermes mcp add wikipedia --command wikipedia-mcp --args '--country,BR'
# ERRO: unrecognized arguments: --country,BR

hermes mcp add wikipedia --command wikipedia-mcp --args --country BR
# ERRO: unrecognized arguments: --country BR

hermes mcp add wikipedia --command wikipedia-mcp --args '--country' 'BR'
# ERRO: unrecognized arguments: --country BR
```

**Causa:** O CLI do Hermes (`hermes mcp add`) faz parsing via argparse e flags
como `--country` são consumidas como flags do próprio CLI, não passadas adiante.
Isso é um problema estrutural do `hermes mcp add --args`.

### Configuração via hermes config set — PARCIAL
```bash
hermes config set mcp_servers.wikipedia.command wikipedia-mcp
# OK

hermes config set mcp_servers.wikipedia.args '["--country", "BR"]'
# Gravou, mas como STRING '"["--country", "BR"]"' em vez de lista YAML
```
**Problema:** `hermes config set` serializa o valor usando yaml.dump, e uma string
JSON é tratada como string, não parseada como lista.

### Correção via Python
```python
import yaml
from pathlib import Path

config_path = Path.home() / ".hermes" / "config.yaml"
config = yaml.safe_load(config_path.read_text())
config["mcp_servers"]["wikipedia"]["args"] = ["--country", "BR"]
config_path.write_text(
    yaml.dump(config, default_flow_style=False, sort_keys=False, allow_unicode=True)
)
```

### Teste
```bash
hermes mcp test wikipedia
# ✓ Connected (671ms)
# ✓ Tools discovered: 22
```

## Ferramentas Descobertas (11 + 11 aliases wikipedia_*)
1. search_wikipedia / wikipedia_search_wikipedia
2. get_article / wikipedia_get_article
3. get_summary / wikipedia_get_summary
4. get_sections / wikipedia_get_sections
5. get_links / wikipedia_get_links
6. get_coordinates / wikipedia_get_coordinates
7. get_related_topics / wikipedia_get_related_topics
8. summarize_article_for_query / wikipedia_summarize_article_for_query
9. summarize_article_section / wikipedia_summarize_article_section
10. extract_key_facts / wikipedia_extract_key_facts
11. test_wikipedia_connectivity / wikipedia_test_wikipedia_connectivity

## Notas Operacionais

- `hermes model` requer terminal interativo — NÃO funciona via pipe/subprocess
- `hermes auth add nous --no-browser` gera URL OAuth mas não printa saída quando
  executado via background, possivelmente porque bufferiza ou usa curses
- Para login Nous Research, o caminho mais confiável é executar `hermes auth add nous`
  diretamente no terminal (não via Telegram)
