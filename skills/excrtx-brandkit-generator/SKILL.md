---
name: excrtx-brandkit-generator
description: Extrai e traduz identidades visuais de logos, campanhas ou marcas técnicas para DESIGN.md e aplicações públicas WCAG-ready no escopo correto.
version: 1.2.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - design
    - brand
    - tokens
    - brandkit
    - wcag
    related_skills:
    - excrtx-quality-designsys
    - excrtx-quality-taste
    - design-md
    - excrtx-produce-artifacts
    calibration:
    - feature_id: EX-55
      calibration_prompt: 'Quando o executivo pedir para extrair ou traduzir identidade visual a partir de logo, conjunto de campanha ou marca técnica, ative esta skill. Classifique primeiro o modo: logo única, campanha multi-asset ou publicação editorial. Use o script apenas no modo logo; nos demais, carregue a referência correspondente.'
      test_prompt: Gere identidade visual para o cliente Acme Inc a partir da logo /tmp/acme-logo.png
      acceptance_criteria: DESIGN.md gerado no escopo correto, WCAG AA válido, lint aprovado e evidência visual classificada conforme o modo.
      remediation_tip: 'FALHA: modo ou escopo não resolvido. Logo única usa extração → classificação → contraste → DESIGN.md → lint/persistência. Campanha multi-asset usa evidência distribuída e DESIGN.md no root da campanha. Publicação editorial classifica os ativos como preservar, redesenhar, textura ou descartar e produz territórios completos de capa. Apresente o DRAFT antes de ação externa.'
---
# excrtx-brandkit-generator

Ponte entre **brandkit.md** (guia criativo de identidade visual) e
**excrtx-quality-designsys** (persistência de tokens no cascade global→micro).

> Esta skill opera em três modos de fonte:
> - **logo única** — identidade corporativa extraída de PNG/JPG/SVG;
> - **campanha multi-asset** — identidade distribuída entre lockup, banners, tags,
>   fotografia, templates e manual institucional.
> - **publicação editorial** — marca ASCII, CLI, diagramática ou developer-facing
>   traduzida para uma capa pública sem copiar literalmente o meio técnico.
>
> `brandkit.md` continua sendo o guia criativo. Para campanhas multi-asset, use
> `references/campaign-multi-asset-design-system.md`; não reduza a identidade ao
> arquivo de logo quando as peças fornecidas carregam a linguagem visual.

## Pipeline

### Modo logo única

```
logo PNG/JPG/SVG
  → K-Means ou cores SVG
  → classificação cromática
  → pares WCAG
  → DESIGN.md no cascade do microverso
```

### Modo campanha multi-asset

```
lockup + peças planas + fotografia + manual + restrições
  → cores sólidas exatas nas peças planas
  → tons de tratamento via K-Means nas fotografias
  → separação entre paleta expressiva, tokens funcionais e cores protegidas
  → DESIGN.md no root da campanha
  → ponteiros em AGENTS.md, índice de assets e Acervo
```

### Modo publicação editorial

```
marca técnica + conteúdo editorial + público
  → inventário semântico: preservar / redesenhar / textura / descartar
  → um sistema editorial ou, em comparação, territórios distintos de posicionamento
  → DESIGN.md local + frente / lombada / quarta capa
  → comparação em miniatura e spread completo
```

Todos os modos terminam com lint Google, contraste WCAG, validação de links e pre-flight visual adequado à superfície.

## When to Use

Activate when:
- Executive asks "gere identidade visual para [cliente]"
- Executive provides a logo path + microverso slug
- Executive provides a campaign asset set and asks for one design system across surfaces
- Publishing project must adapt ASCII, CLI, diagrammatic or developer-facing branding for a general readership
- Task requires creating a DESIGN.md from visual evidence

**Don't use for:** Textual-only briefings without visual assets (use brandkit.md directly). Purely conceptual work without visual evidence. Manual palette definition (edit DESIGN.md directly). Editing existing tokens (use `excrtx-quality-designsys`).

## Exocórtex Governance

- **Execution vector:** use when the executive requests a concrete identity, DESIGN.md, campaign system or editorial application. Produce and verify the local artifact directly.
- **Evolution vector:** if the executive is studying positioning without asking for an artifact, explore assumptions and alternatives before converging; do not write canonical files prematurely.
- **Internal vs external:** reads, dry-runs, local renders, Acervo writes and local artifact packaging are internal actions. Publishing, sharing, uploading to a shared surface, or sending material to third parties remains Draft-First.
- **Scope promotion:** a campaign or editorial DRAFT stays in its project/artifact scope. Promote it to a broader micro/global design system only after the executive chooses that scope.

## Entrada

| Argumento | Modo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `logo_path` | logo única | Sim | Caminho absoluto para PNG, JPG ou SVG |
| `asset_paths` | campanha multi-asset | Sim | Dois ou mais ativos visuais representativos |
| `manual_paths` | campanha multi-asset | Recomendado | Manuais de marca e governança que limitam a aplicação |
| `source_asset_paths` | publicação editorial | Sim | Ativos técnicos, ASCII, CLI, diagramáticos ou developer-facing |
| `publication_brief` | publicação editorial | Sim | Título, público, conteúdo, formato, copy e restrições editoriais |
| `artifact_root` | publicação editorial | Sim | Pacote local que preservará fonte, ativos, exports e avaliações |
| `micro_slug` | todos | Recomendado | Microverso para ponteiro, log e recuperação semântica |
| `project_root` | campanha multi-asset | Sim | Root onde o DESIGN.md operacional será gravado |
| `brand_name` | todos | Não | Nome da marca, campanha ou método editorial |

**Variáveis de ambiente:**
- `ACERVO` — diretório raiz do Acervo Cognitivo para operações canônicas e ponteiros.

## Saída

- modo logo: `acervo/micro/{slug}/DESIGN.md` como override do cascade;
- modo campanha: `{project_root}/DESIGN.md` como contrato operacional autocontido;
- modo publicação editorial: DESIGN.md local, classificação semântica dos ativos e sistema completo de capa no pacote do artefato;
- em todos: ponteiro canônico quando houver valor cognitivo e resumo de paleta, contraste, lint e pre-flight adequado à superfície.

## Dependências

- Pillow e scikit-learn para extração raster e K-Means;
- cairosvg apenas quando um SVG não expõe cores e precisa de rasterização;
- `@google/design.md` para lint e export.

Não instalar dependências silenciosamente. Verifique primeiro o ambiente e prefira a CLI já disponível:

```bash
npx --no-install @google/design.md lint DESIGN.md
npx --no-install @google/design.md export --format dtcg DESIGN.md
```

Se faltar uma dependência, peça aprovação antes de instalar.

## Exemplo de Uso

```bash
# Dry-run (apenas visualiza, não escreve)
python3 scripts/brandkit-extract.py --logo /tmp/acme-logo.png --slug acme --name "ACME Corp" --dry-run

# Execução real (escreve em $ACERVO/micro/acme/DESIGN.md + executa lint)
python3 scripts/brandkit-extract.py --logo /tmp/acme-logo.png --slug acme --name "ACME Corp"

# Saída esperada:
# 🎨 brandkit-generator — ACME Corp
# 📦 Fase A: Extraindo paleta...
#    Cores extraídas (5): ■ #1a365d (25%) ■ #2b6cb0 (25%) ■ #c53030 (25%) ■ #d69e2e (25%) ■ #cc9930 (0%)
# 📦 Fase B: Classificando e derivando sistema...
# 📦 Fase C: Validando WCAG AA... ✅
# 📦 Fase D: Gerando DESIGN.md...
# ✅ Escrito: /acervo/micro/acme/DESIGN.md
# 📦 Lint: exit 0 ✅
```

## Procedure

1. **Classify source mode:**
   - one logo → use `scripts/brandkit-extract.py`;
   - campaign asset set → use `references/campaign-multi-asset-design-system.md`.
   - technical brand for a public book → use `references/editorial-book-cover-from-technical-brand.md`.
2. **Resolve scope before writing:** corporate/micro identity may live in the Acervo cascade; campaign-specific identity belongs at the campaign root; editorial-cover identity belongs in the artifact package until the executive approves promotion. Add discovery pointers without contaminating broader scopes.
3. **Extract evidence:** in logo mode, run the script dry-run. In multi-asset mode, extract exact solid colors from flat pieces and use K-Means only for photographic treatment tones. In editorial mode, inventory technical assets and classify each as preserve, redesign, texture, or discard.
4. **Derive functional tokens:** separate expressive source colors from accessible action/text pairs; require WCAG AA for every text-bearing component.
5. **Write and connect:** generate the Google DESIGN.md in the resolved scope, connect it to the project harness, and record a canonical pointer only when the system has durable cognitive value.
6. **Verify:** lint with the locally available Google CLI, validate references and contrast, export DTCG when applicable, and run the surface-specific visual gate. Editorial covers require front-only and complete-spread contact sheets.
7. **Log:** when `micro_slug` exists or the system has durable cognitive value, register the canonical operation via `excrtx-memory-manager` and refresh semantic indexing; otherwise keep traceability in the artifact manifest.

## Falhas e Tratamento de Erros

| Fase | Condição de Erro | Comportamento |
|------|------------------|---------------|
| A | Arquivo não encontrado | `sys.exit(1)` com mensagem clara |
| A | Pillow/scikit-learn não instalados | `sys.exit(1)` com comando de instalação |
| A | SVG sem cores explícitas + cairosvg ausente | `sys.exit(1)` instruindo instalar cairosvg |
| B | Paleta com < 3 cores | `sys.exit(1)` listando as cores encontradas |
| C | Contraste < 4.5:1 | Ajuste automático de on-primary/on-tertiary (relatado no output) |
| E | Lint tool (npx) ausente | Aviso no output, lint pulado (não é fatal) |
| E | Lint timeout (>30s) | Aviso, lint pulado |
| E | Qualquer exceção no lint | Aviso, lint pulado |

**Cores de fallback (quando a logo não fornece cor clara/escura):**
- `neutral`: `#F7FAFC` (fundo claro genérico)
- `dark`: `#1A202C` (texto escuro genérico)
- `secondary` (se < 2 cores na paleta): `#4A5568`
- Cores semânticas (danger, success, warning): sempre defaults do sistema

## References and Scripts

- `references/editorial-book-cover-from-technical-brand.md` — adaptação de marcas ASCII, CLI, diagramáticas ou developer-facing para três sistemas completos de capa destinados ao público geral.
- `references/campaign-multi-asset-design-system.md` — extração e governança de identidade distribuída em campanhas com vários ativos.
- `scripts/brandkit-extract.py` — extração de paleta + geração de DESIGN.md.

## Limitações (v1)

- Logo com gradientes: apenas cores sólidas são extraídas no modo logo.
- Tipografia: logo raster não prova uma família tipográfica; use manual ou arquivo-fonte quando disponível.
- Campanhas sem peças planas podem não oferecer cores canônicas exatas; sinalize a inferência.
- SVGs complexos (>1000 elementos): desempenho não garantido.
- Imagens grandes (>10MB): redimensione apenas para K-Means fotográfico; não use a miniatura para provar cores sólidas.
- Geração de assets gráficos (favicon, ícones): fora do escopo.
- Interface: CLI-only.

## Pitfalls

- **Logo with gradients:** Only solid colors are extracted; gradients are ignored. Warn the executive if palette looks sparse.
- **SVGs with <3 explicit colors:** If cairosvg is missing and SVG has no fill/stroke, extraction fails. Install cairosvg as fallback.
- **Large images (>10MB):** Resized to 256x256 before extraction — may lose subtle color details.
- **WCAG auto-adjustment surprises:** on-primary/on-tertiary may be auto-modified to pass contrast. Always show the executive the final palette.
- **Typography evidence:** A raster logo does not prove a font family. Inherit from global only in logo-only micro overrides; campaign asset sets may use an institutional manual as authority.
- **Flat art vs photography:** K-Means is useful for photographic treatment tones but can blur canonical flat fills through antialiasing. Prefer exact repeated pixels for solid campaign colors.
- **Scope leakage:** Never put campaign-specific colors in a workspace/global DESIGN.md when future campaigns share that scope. Keep the operational file at the campaign root and add discovery pointers.
- **Protected brand colors:** Institutional mark colors can remain intentionally unused by components. Document the lint warning instead of turning protected colors into decoration.
- **Lint timeout:** npx lint can hang on complex files. 30s timeout applied; lint skip is non-fatal.

## Acceptance Criteria

| ID | Critério | Como verificar |
|----|----------|----------------|
| EX-BRAND-01 | Extrai paleta de PNG/JPG (K-Means n=5) | 5 cores retornadas, ordenadas por frequência |
| EX-BRAND-02 | Extrai cores explícitas de SVG | Cores de fill/stroke sem rasterizar |
| EX-BRAND-03 | Gera cores derivadas (neutral, dark, on-*, danger, success) | Presentes no DESIGN.md mesmo se não na logo |
| EX-BRAND-04a | Valida WCAG AA ≥ 4.5:1 internamente | Script reporta "✅" para todos os pares |
| EX-BRAND-04b | DESIGN.md passa no lint externo | `npx @google/design.md lint` exit 0 |
| EX-BRAND-05 | Ajusta automaticamente contrastes falhos | on-primary/on-tertiary modificados se < 4.5:1 |
| EX-BRAND-06 | Gera DESIGN.md com YAML frontmatter válido | `npx @google/design.md lint` não reporta parse errors |
| EX-BRAND-07 | Escopo de persistência correto | `extends: global` em micro override; arquivo autocontido no root de campanha |
| EX-BRAND-08 | Herança ou completude conforme o modo | Logo/micro herda global; campanha declara tokens necessários ao sistema inteiro |
| EX-BRAND-09 | Rejeita paletas com < 3 cores | Erro claro, aborta com mensagem |
| EX-BRAND-10 | Integra descoberta do harness | Ponteiros no Acervo e AGENTS.md, com índice semântico atualizado |
| EX-BRAND-11 | Campanha multi-asset preserva escopo e evidência | DESIGN.md no projeto, cores sólidas exatas, tons fotográficos separados e ponteiros no harness/Acervo |

## Verification

- [ ] Source mode classified: logo única or campanha multi-asset
- [ ] Script imports without error: `python3 -c "import importlib; importlib.import_module('scripts.brandkit-extract')"` or `python3 scripts/brandkit-extract.py --help`
- [ ] Logo mode dry-run produces 5 extracted colors from a test PNG
- [ ] Multi-asset mode proves source colors against flat authority assets and separates photographic tones
- [ ] Generated DESIGN.md has valid YAML frontmatter; `extends: global` is required only for Acervo micro overrides
- [ ] WCAG AA contrast ≥ 4.5:1 for all text-bearing components
- [ ] `npx --no-install @google/design.md lint` exits 0; intentional warnings are documented
- [ ] DTCG export parses, token references resolve, and local source links exist
- [ ] Campaign-specific identity does not leak into workspace/global tokens
- [ ] Technical publishing mode classifies each source element as preserve, redesign, texture, or discard
- [ ] Multiple cover concepts, when requested, differ by positioning and keep technical/runtime details out of the public promise
- [ ] Visual pre-flight confirms coherence with source assets
- [ ] Canonical pointer and semantic index are updated

