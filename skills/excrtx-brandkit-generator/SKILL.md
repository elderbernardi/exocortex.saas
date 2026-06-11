---
name: excrtx-brandkit-generator
description: "Extrai identidade visual da logo corporativa e gera DESIGN.md com tokens WCAG-ready no cascade global→micro do Exocórtex."
version: 1.0.0
category: excrtx
platforms: [linux]
metadata:
  hermes:
    tags: [exocortex, design, brand, tokens, brandkit, wcag]
    related_skills: [excrtx-quality-designsys, excrtx-quality-taste, design-md]
    calibration:
      - feature_id: EX-18
        calibration_prompt: >
          Quando o executivo pedir para gerar identidade visual a partir de uma
          logo, ative esta skill. Consulte o Pipeline desta skill e o script
          scripts/brandkit-extract.py para o fluxo completo.
        test_prompt: Gere identidade visual para o cliente Acme Inc a partir da logo /tmp/acme-logo.png
        acceptance_criteria: >
          DESIGN.md gerado com extends:global, WCAG AA válido, lint passa,
          cores extraídas e classificadas corretamente.
---
# excrtx-brandkit-generator

Ponte entre **brandkit.md** (guia criativo de identidade visual) e
**excrtx-quality-designsys** (persistência de tokens no cascade global→micro).

> ⚠️ Esta skill **não** consome brandkit.md como entrada — a logo é a única fonte.
> brandkit.md é o guia criativo que antecede esta skill; esta skill é a
> implementação técnica. Se não houver logo asset, use brandkit.md diretamente.

## Pipeline

```
logo (PNG/JPG/SVG)
  ↓ Fase A: Extração de Paleta
Paleta bruta (5 cores)
  ↓ Fase B: Classificação + Derivação
Sistema cromático (primary, secondary, tertiary, accent, neutral, dark, on-*, danger, success)
  ↓ Fase C: Validação WCAG AA
Ajustes de contraste automáticos
  ↓ Fase D: Geração DESIGN.md
Arquivo YAML + markdown com extends: global
  ↓ Fase E: Lint + Persistência
acervo/micro/{slug}/DESIGN.md
```

## Quando Ativar

- Executivo pede "gere identidade visual para [cliente]"
- Executivo fornece caminho de logo + slug de microverso
- Tarefa que precisa criar DESIGN.md de micro a partir de asset visual

**Não usar quando:**
- Não há logo asset (apenas briefing textual) — use brandkit.md diretamente
- O trabalho é puramente conceitual sem asset visual para extrair cores
- A paleta precisa ser definida manualmente (editar DESIGN.md diretamente)

## Entrada

| Argumento | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `logo_path` | string | Sim | Caminho absoluto para PNG, JPG ou SVG |
| `micro_slug` | string | Sim | Slug do microverso destino |
| `brand_name` | string | Não | Nome da marca (default: slug capitalizado) |

**Variáveis de ambiente:**
- `ACERVO` — diretório raiz do Acervo Cognitivo (default: `../../acervo` relativo ao script).
  A saída é escrita em `$ACERVO/micro/{slug}/DESIGN.md`.

## Saída

- `acervo/micro/{slug}/DESIGN.md` — arquivo de tokens Google DESIGN.md válido
- Resumo: cores extraídas, ajustes WCAG, resultado do lint

## Dependências

```bash
pip install Pillow scikit-learn       # extração de paleta (obrigatório)
pip install cairosvg                  # fallback SVG→PNG (opcional, para SVGs sem cores explícitas)
npm install -g @google/design.md      # lint do DESIGN.md (opcional, fallback para npx)
```

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

## Scripts

- `scripts/brandkit-extract.py` — extração de paleta + geração de DESIGN.md

## Limitações (v1)

- Logo com gradientes: apenas cores sólidas são extraídas (gradientes ignorados)
- Tipografia: sempre herdada do global (a logo não carrega informação tipográfica)
- SVGs complexos (>1000 elementos): desempenho não garantido
- Imagens grandes (>10MB): redimensionadas para 256x256 antes da extração
- Geração de assets gráficos (favicon, ícones): fora do escopo (só tokens textuais)
- Interface: CLI-only (sem UI visual)

## Critérios de Aceitação

| ID | Critério | Como verificar |
|----|----------|----------------|
| EX-BRAND-01 | Extrai paleta de PNG/JPG (K-Means n=5) | 5 cores retornadas, ordenadas por frequência |
| EX-BRAND-02 | Extrai cores explícitas de SVG | Cores de fill/stroke sem rasterizar |
| EX-BRAND-03 | Gera cores derivadas (neutral, dark, on-*, danger, success) | Presentes no DESIGN.md mesmo se não na logo |
| EX-BRAND-04a | Valida WCAG AA ≥ 4.5:1 internamente | Script reporta "✅" para todos os pares |
| EX-BRAND-04b | DESIGN.md passa no lint externo | `npx @google/design.md lint` exit 0 |
| EX-BRAND-05 | Ajusta automaticamente contrastes falhos | on-primary/on-tertiary modificados se < 4.5:1 |
| EX-BRAND-06 | Gera DESIGN.md com YAML frontmatter válido | `npx @google/design.md lint` não reporta parse errors |
| EX-BRAND-07 | Inclui `extends: global` no frontmatter | YAML contém `extends: global` |
| EX-BRAND-08 | Herda tipografia e componentes do global | DESIGN.md não redefine typography/rounded/spacing/components |
| EX-BRAND-09 | Rejeita paletas com < 3 cores | Erro claro, aborta com mensagem |
| EX-BRAND-10 | Integra cascade excrtx-quality-designsys | Escrito em acervo/micro/{slug}/DESIGN.md |
