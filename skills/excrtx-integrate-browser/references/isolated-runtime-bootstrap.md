# Bootstrap de runtime isolado para Browser Automation

## Quando aplicar
- Quando a skill precisar funcionar em ambientes sem `uv` global
- Quando o setup precisar ser portátil e autocontido no diretório da própria skill
- Quando o browser (Playwright/Chromium) não deve depender de caches globais do sistema

## Padrão adotado
Provisionar um runtime local em `skills/excrtx-integrate-browser/.runtime/` com subpaths explícitos:

- `uv/` — instalação local do `uv`
- `bin/` — executáveis expostos pela tool install (`browser-use`)
- `python/` — runtime Python gerenciado
- `tools/` — artefatos de tools do `uv`
- `cache/uv/` — cache isolado do `uv`
- `ms-playwright/` — browsers baixados pelo Playwright

## Regras operacionais
1. O wrapper deve preferir o runtime local da skill antes de depender do PATH global.
2. O instalador deve fazer auto-bootstrap quando `uv` estiver ausente.
3. O wrapper deve injetar temporariamente no PATH tanto o diretório de binários da tool quanto o diretório do `uv` local.
4. Variáveis de isolamento devem apontar para `.runtime/`, em especial:
   - `UV_PYTHON_INSTALL_DIR`
   - `UV_TOOL_DIR`
   - `UV_CACHE_DIR`
   - `PLAYWRIGHT_BROWSERS_PATH`
5. O setup preventivo (`setup.sh`) e o reparo sob demanda (primeiro uso do wrapper) devem convergir para o mesmo layout de runtime.

## Pitfall confirmado
Se apenas `bin/` entra no PATH e o diretório do binário do `uv` não entra, comandos subsequentes que dependem de `uvx`/`uv tool` podem falhar mesmo com a instalação local presente.

## Workaround estável
Para provisionar o Chromium, preferir:

```bash
uv tool run --from playwright playwright install chromium
```

Em vez de depender de fluxos indiretos do `browser-use install`, que podem tentar `sudo`, assumir PATH global ou falhar em shells mais restritos.

## Verificação mínima
Validar a presença de:
- `.runtime/uv/uv`
- `.runtime/bin/browser-use`
- `.runtime/ms-playwright/`

E executar um smoke real:

```bash
skills/excrtx-integrate-browser/scripts/browser-use.sh --help
```

Critério de aceite: bootstrap completo + help do CLI com exit 0.
