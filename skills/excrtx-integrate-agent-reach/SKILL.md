---
name: excrtx-integrate-agent-reach
description: Adapter skill for Agent-Reach CLI to produce normalized research items for Exocórtex research pipeline.
version: 0.1.0
category: excrtx
platforms: [linux]
metadata:
  hermes:
    tags: [exocortex, integrate, agent-reach, research]
    related_skills: [last30days, excrtx-crawler-brasil, excrtx-research-cpg-brasil]
compiled_rules: |
  # This skill does not inject runtime rules; it is a tool-only skill.
---
# excrtx-integrate-agent-reach — Adapter for Agent-Reach

## When to Use

- Você precisa de resultados de busca/web/social do Agent-Reach para usar em skills de pesquisa como `excrtx-research-cpg-brasil`.
- O executivo pediu "buscar no Agent-Reach sobre X" ou quer integrar essa fonte como opcional em um wrapper de pesquisa.
- Você quer padronizar a saída do Agent-Reach para o formato JSON esperado pelo pipeline de síntese (`[{title, url, date, source, channel, snippet, score, raw_provider, retrieved_at}]`).

**Don't use for:** Substituir o `last30days` ou o crawler setorial; esta skill é apenas uma camada de alcance opcional.

## Procedure

1. **Verifique se o Agent-Reach está disponível**  
   Execute `agent-reach --version` ou `which agent-reach`. Se não estiver instalado, siga as instruções do repositório oficial:  
   ```bash
   # Exemplo de instalação via pip (ajuste conforme o repo)
   pip install git+https://github.com/Panniantong/Agent-Reach.git
   ```
   O skill assume que o comando `agent-reach` está no `$PATH`.

2. **Defina a consulta e os canais desejados**  
   O Agent-Reach aceita flags como `--web`, `--youtube`, `--rss`, `--gitHub`, `--twitter`, `--reddit`, etc. Consulte `agent-reach help` para a lista completa.

3. **Execute a busca e capture a saída JSON**  
   O Agent-Reach já pode emitir JSON via flag `--format json`. Use isso para facilitar a transformação. Exemplo:
   ```bash
   agent-reach "Microsoft earnings" --web --youtube --format json --limit 20
   ```

4. **Transforme para o schema normalizado do Exocórtex**  
   Cada item retornado pelo Agent-Reach deve ser mapeado para:
   - `title`      → título do resultado
   - `url`        → link direto
   - `date`       → data de publicação (ISO 8601 quando disponível)
   - `source`     → nome da plataforma (web, youtube, rss, gitHub, twitter, reddit, ...)
   - `channel`    → subcategoria ou nome do canal (ex.: nome do YouTube channel, subreddit)
   - `snippet`    → trecho ou resumo do conteúdo
   - `score`      → relevância (0-100) se fornecida, ou calcular com base em engajamento
   - `raw_provider` → "agent-reach"
   - `retrieved_at` → timestamp UTC da coleta

5. **Retorne a lista JSON**  
   A skill deve imprimir a lista JSON no stdout (compact ou pretty) para que a skill consumidora possa fazer `json_parse`.

## Exemplo de chamada via Hermes

```bash
# Dentro de uma skill ou no terminal do agente:
hermes run "agent-reach search 'Microsoft earnings' --web --youtube --limit 10" --emit=compact
```

A saída deverá ser algo como:
```json
[
  {
    "title": "Microsoft Q4 Earnings Beat Estimates",
    "url": "https://www.reuters.com/technology/microsoft-q4-earnings-...",
    "date": "2026-06-20",
    "source": "web",
    "channel": "Reuters",
    "snippet": "Microsoft reported revenue of $65.6B, surpassing expectations...",
    "score": 88,
    "raw_provider": "agent-reach",
    "retrieved_at": "2026-06-22T04:10:00Z"
  },
  ...
]
```

## Pitfalls

- **Agent-Reach não instalado** → a skill falhará com "command not found". Verifique a instalação antes de usar.
- **Formatos de saída diferentes** → se o Agent-Reach mudar seu schema JSON, ajuste o mapeamento aqui.
- **Limites de taxa** → algumas plataformas (Twitter, Reddit) podem exigir autenticação; consulte a documentação do Agent-Reach para configurar credenciais.
- **Resultados vazios** → retorne uma lista vazia `[]` em vez de nenhum output, para não quebrar consumidores que esperam JSON.

## Verification

- [ ] `agent-reach --version` retorna uma versão válida.
- [ ] Executar uma busca simples com `--format json` produz JSON válido.
- [ ] A transformation produz objetos com todos os campos obrigatórios (`title`, `url`, `date`, `source`, `channel`, `snippet`, `score`, `raw_provider`, `retrieved_at`).
- [ ] A skill integrada em um wrapper de pesquisa (ex.: `excrtx-research-cpg-brasil`) consegue consumir o output sem erros de json parsing.

---