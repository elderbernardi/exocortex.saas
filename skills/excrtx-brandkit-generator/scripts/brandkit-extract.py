#!/usr/bin/env python3
"""
brandkit-extract.py — Extrai paleta de cores de uma logo e gera DESIGN.md

Uso:
  python brandkit-extract.py --logo /path/to/logo.png --slug cliente-x --name "Cliente X"

Flags:
  --logo      Caminho para PNG, JPG ou SVG
  --slug      Slug do microverso destino
  --name      Nome da marca (default: slug capitalizado)
  --outdir    Diretório de saída (default: acervo/micro/{slug})
  --dry-run   Apenas printa o DESIGN.md no stdout, não escreve
"""

import argparse
import json
import math
import os
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("ERRO: Pillow não instalado. Execute: pip install Pillow", file=sys.stderr)
    sys.exit(1)

try:
    from sklearn.cluster import KMeans
    import numpy as np
except ImportError:
    print("ERRO: scikit-learn não instalado. Execute: pip install scikit-learn", file=sys.stderr)
    sys.exit(1)

# ─── Utilitários de Cor ───────────────────────────────────────────────────

def hex_to_rgb(hex_color):
    """#RRGGBB → (R, G, B)"""
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"

def rgb_to_hsl(r, g, b):
    """(R,G,B) 0-255 → (H, S, L) 0-360, 0-100, 0-100"""
    r, g, b = r/255.0, g/255.0, b/255.0
    mx, mn = max(r, g, b), min(r, g, b)
    l = (mx + mn) / 2
    if mx == mn:
        return (0, 0, round(l * 100))
    d = mx - mn
    s = d / (1 - abs(2 * l - 1))
    if mx == r:
        h = (60 * ((g - b) / d) + 360) % 360
    elif mx == g:
        h = (60 * ((b - r) / d) + 120) % 360
    else:
        h = (60 * ((r - g) / d) + 240) % 360
    return (round(h), round(s * 100), round(l * 100))

def relative_luminance(r, g, b):
    """WCAG 2.1 relative luminance. r,g,b 0-255."""
    def linearize(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)

def contrast_ratio(hex1, hex2):
    """WCAG 2.1 contrast ratio entre duas cores hex."""
    r1, g1, b1 = hex_to_rgb(hex1)
    r2, g2, b2 = hex_to_rgb(hex2)
    l1 = relative_luminance(r1, g1, b1)
    l2 = relative_luminance(r2, g2, b2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

def adjust_for_contrast(text_hex, bg_hex, target=4.5):
    """
    Ajusta text_hex para atingir target contrast contra bg_hex.
    Tenta clarear (r,g,b → 255) se bg é escura, escurecer se bg é clara.
    Retorna hex ajustado.
    """
    cr = contrast_ratio(text_hex, bg_hex)
    if cr >= target:
        return text_hex

    r, g, b = hex_to_rgb(text_hex)
    bg_lum = relative_luminance(*hex_to_rgb(bg_hex))

    # Se bg é escura (< 0.18), clarear o text; se clara, escurecer
    if bg_lum < 0.18:
        # Clarear gradualmente
        for step in range(1, 11):
            t = step / 10
            nr = int(r + (255 - r) * t)
            ng = int(g + (255 - g) * t)
            nb = int(b + (255 - b) * t)
            candidate = rgb_to_hex(nr, ng, nb)
            if contrast_ratio(candidate, bg_hex) >= target:
                return candidate
        return "#FFFFFF"
    else:
        # Escurecer gradualmente
        for step in range(1, 11):
            t = step / 10
            nr = int(r * (1 - t))
            ng = int(g * (1 - t))
            nb = int(b * (1 - t))
            candidate = rgb_to_hex(nr, ng, nb)
            if contrast_ratio(candidate, bg_hex) >= target:
                return candidate
        return "#111111"


# ─── Extração de Paleta ─────────────────────────────────────────────────

def extract_from_raster(image_path, n_colors=5):
    """
    Extrai n_colors dominantes de uma imagem raster via K-Means.
    Retorna lista de (hex, frequency, cluster_center_rgb).
    """
    img = Image.open(image_path).convert("RGB")
    # Redimensionar para performance
    img.thumbnail((256, 256))
    pixels = np.array(img).reshape(-1, 3)

    # Filtrar pixels quase-branco (fundo) e quase-preto (sem informação)
    mask = ~(
        (np.all(pixels > 240, axis=1)) |  # quase branco
        (np.all(pixels < 15, axis=1))     # quase preto
    )
    filtered = pixels[mask]
    if len(filtered) < 100:
        filtered = pixels  # fallback

    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
    kmeans.fit(filtered)
    labels = kmeans.labels_

    # Contar frequência de cada cluster
    counter = Counter(labels)
    total = len(labels)

    # Ordenar clusters por frequência (decrescente)
    sorted_clusters = sorted(counter.items(), key=lambda x: -x[1])
    results = []
    for cluster_id, count in sorted_clusters:
        center = kmeans.cluster_centers_[cluster_id]
        r, g, b = int(round(center[0])), int(round(center[1])), int(round(center[2]))
        hex_color = rgb_to_hex(r, g, b)
        freq = count / total
        results.append((hex_color, freq, (r, g, b)))

    return results


def extract_from_svg(svg_path):
    """
    Extrai cores explícitas de fill e stroke em elementos SVG.
    Retorna lista de (hex, weight) — weight = contagem de ocorrências.
    """
    ns = {"svg": "http://www.w3.org/2000/svg"}
    tree = ET.parse(svg_path)
    root = tree.getroot()

    color_counter = Counter()

    for elem in root.iter():
        for attr in ("fill", "stroke"):
            val = elem.get(attr)
            if val and val.startswith("#"):
                # Normalizar shorthand #fff → #ffffff
                if len(val) == 4:
                    val = f"#{val[1]*2}{val[2]*2}{val[3]*2}"
                color_counter[val.lower()] += 1
            elif val and val.startswith("url("):
                pass  # gradiente — ignorar na v1

    if not color_counter:
        return []

    total = sum(color_counter.values())
    # Ordenar por frequência
    sorted_colors = sorted(color_counter.items(), key=lambda x: -x[1])
    results = []
    for hex_color, count in sorted_colors:
        freq = count / total
        results.append((hex_color, freq, hex_to_rgb(hex_color)))

    return results


def is_svg(filepath):
    """Detecta SVG por extensão ou conteúdo."""
    ext = Path(filepath).suffix.lower()
    if ext == ".svg":
        return True
    # Tentar detectar pela primeira linha
    try:
        with open(filepath, "r") as f:
            first = f.read(200)
            return "<svg" in first
    except Exception:
        return False


# ─── Classificação de Paleta → Sistema ─────────────────────────────────

def classify_palette(palette):
    """
    Classifica cores extraídas em papéis de design system.
    palette: lista de (hex, frequency, rgb)
    Retorna dict com cores classificadas.
    """
    if not palette:
        return None

    colors = {}
    n = len(palette)

    # Primary = cor mais frequente
    primary_hex, _, primary_rgb = palette[0]
    colors["primary"] = primary_hex

    # Calcular chroma (saturação aproximada) para cada cor
    with_chroma = []
    for hex_c, freq, rgb in palette:
        h, s, l = rgb_to_hsl(*rgb)
        chroma = s  # saturação como proxy
        with_chroma.append((hex_c, freq, rgb, chroma, s, l))
        if hex_c == primary_hex:
            primary_h, primary_s, primary_l = h, s, l

    # Ordenar por chroma (maior = mais vibrante) para encontrar accent
    by_chroma = sorted(with_chroma, key=lambda x: -x[3])

    # Secondary = segunda cor mais frequente, ou derivada da primary
    if n >= 2:
        colors["secondary"] = palette[1][0]
    else:
        # Derivar: primary com -40% saturação
        r, g, b = primary_rgb
        h, s, l = rgb_to_hsl(r, g, b)
        ns = max(0, s - 40)
        # Recalcular não é trivial sem HSL→RGB aqui; usar cinza escuro como fallback
        colors["secondary"] = "#4A5568"

    # Tertiary = cor mais distinta da primary (terceira mais frequente)
    if n >= 3:
        colors["tertiary"] = palette[2][0]
    else:
        # Derivar da primary com hue shift
        colors["tertiary"] = colors["primary"]

    # Accent = cor com maior chroma que NÃO é primary nem tertiary
    accent_found = False
    for hex_c, freq, rgb, chroma, s, l in by_chroma:
        if hex_c != colors["primary"] and hex_c != colors.get("tertiary", ""):
            colors["accent"] = hex_c
            accent_found = True
            break
    if not accent_found:
        # Derivar accent da primary: hue + 30°
        colors["accent"] = colors["primary"]

    # Neutral = fundo claro (se houver branco/quase-branco na paleta)
    neutral_found = False
    for hex_c, freq, rgb in palette:
        r, g, b = rgb
        if r > 220 and g > 220 and b > 220:
            colors["neutral"] = hex_c
            neutral_found = True
            break
    if not neutral_found:
        colors["neutral"] = "#F7FAFC"  # fallback

    # Dark = texto principal (preto/quase-preto da paleta ou fallback)
    dark_found = False
    for hex_c, freq, rgb in palette:
        r, g, b = rgb
        if r < 50 and g < 50 and b < 50:
            colors["dark"] = hex_c
            dark_found = True
            break
    if not dark_found:
        colors["dark"] = "#1A202C"

    return colors


def derive_system_colors(classified):
    """
    Deriva cores que a logo não fornece: on-primary, on-tertiary, danger, success, warning.
    Retorna dict completo com todas as cores do sistema.
    """
    system = dict(classified)

    # on-* cores com contraste garantido
    primary = system["primary"]
    tertiary = system.get("tertiary", primary)
    dark = system["dark"]
    neutral = system["neutral"]

    system["on-primary"] = adjust_for_contrast("#FFFFFF", primary)
    system["on-tertiary"] = adjust_for_contrast("#FFFFFF", tertiary)

    # Cores semânticas (sempre incluídas)
    system["danger"] = "#E53E3E"
    system["success"] = "#38A169"
    system["warning"] = "#D69E2E"

    return system


# ─── Geração de DESIGN.md ─────────────────────────────────────────────

def generate_design_md(system_colors, brand_name, slug):
    """
    Gera conteúdo do DESIGN.md completo.
    """

    colors_yaml = "\n".join(
        f"  {k}: \"{v}\""
        for k, v in sorted(system_colors.items())
    )

    content = f"""---
version: alpha
name: {brand_name}
description: Identidade visual derivada da logo corporativa via brandkit-generator
extends: global
colors:
{colors_yaml}
---
## Overview

Identidade visual gerada automaticamente a partir da logo da {brand_name}.
Cores primárias extraídas via análise de clustering (K-Means). Cores derivadas
(neutral, dark, on-*) calculadas para garantir contraste WCAG AA (≥ 4.5:1).
Cores semânticas (danger, success, warning) são defaults do sistema.

Typography, spacing, rounded, e components são herdados do global via
`extends: global`.

## Colors

- **Primary ({system_colors['primary']}):** Cor dominante extraída da logo.
- **Secondary ({system_colors['secondary']}):** Cor de suporte, segunda mais frequente na paleta.
- **Tertiary ({system_colors.get('tertiary', system_colors['primary'])}):** Cor de destaque.
- **Accent ({system_colors.get('accent', system_colors['primary'])}):** Cor de maior saturação — ações, badges.
- **Neutral ({system_colors['neutral']}):** Fundos e superfícies.
- **Dark ({system_colors['dark']}):** Texto principal.
- **on-primary ({system_colors['on-primary']}):** Texto sobre primary (contraste ajustado).
- **on-tertiary ({system_colors['on-tertiary']}):** Texto sobre tertiary (contraste ajustado).
- **Danger ({system_colors['danger']}):** Erros e ações destrutivas.
- **Success ({system_colors['success']}):** Confirmações e métricas positivas.
- **Warning ({system_colors['warning']}):** Alertas e atenção.

## Typography

Herdado de global.

## Layout & Spacing

Herdado de global.

## Components

Herdado de global.

## Do's and Don'ts

- **Do:** Usar token references (`{{colors.primary}}`) em novos componentes.
- **Do:** Manter contraste WCAG AA (4.5:1) em texto sobre fundo.
- **Don't:** Adicionar cores ad-hoc fora da paleta sem justificativa.
- **Don't:** Substituir cores semânticas (danger, success, warning) sem razão.
"""

    return content


# ─── Validação WCAG ────────────────────────────────────────────────────

def validate_wcag(system_colors):
    """
    Valida todos os pares foreground/background do sistema.
    Retorna lista de problemas encontrados.
    """
    issues = []
    pairs = [
        ("on-primary", "primary", "Texto sobre primary"),
        ("on-tertiary", "tertiary", "Texto sobre tertiary"),
        ("dark", "neutral", "Texto principal sobre fundo"),
    ]

    for text_key, bg_key, label in pairs:
        if text_key not in system_colors or bg_key not in system_colors:
            continue
        text_hex = system_colors[text_key]
        bg_hex = system_colors[bg_key]
        cr = contrast_ratio(text_hex, bg_hex)
        if cr < 4.5:
            issues.append({
                "pair": f"{text_key}/{bg_key}",
                "label": label,
                "ratio": round(cr, 2),
                "text_hex": text_hex,
                "bg_hex": bg_hex,
            })

    return issues


# ─── Main ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Extrai paleta de logo e gera DESIGN.md")
    parser.add_argument("--logo", required=True, help="Caminho para PNG, JPG ou SVG")
    parser.add_argument("--slug", required=True, help="Slug do microverso destino")
    parser.add_argument("--name", help="Nome da marca (default: slug capitalizado)")
    parser.add_argument("--outdir", help="Diretório de saída (default: acervo/micro/{slug})")
    parser.add_argument("--dry-run", action="store_true", help="Apenas printa output, não escreve")
    args = parser.parse_args()

    logo_path = args.logo
    slug = args.slug
    brand_name = args.name or slug.replace("-", " ").title()
    acervo_base = os.environ.get("ACERVO", os.path.join(os.path.dirname(__file__), "..", "..", "..", "acervo"))
    outdir = args.outdir or os.path.join(acervo_base, "micro", slug)

    if not os.path.exists(logo_path):
        print(f"ERRO: Arquivo não encontrado: {logo_path}", file=sys.stderr)
        sys.exit(1)

    print(f"🎨 brandkit-generator — {brand_name}")
    print(f"   Logo: {logo_path}")
    print(f"   Slug: {slug}")
    print()

    # ── Fase A: Extração ──
    print("📦 Fase A: Extraindo paleta...")
    if is_svg(logo_path):
        print("   Formato: SVG (parser direto)")
        palette = extract_from_svg(logo_path)
        if not palette:
            print("   ⚠ SVG sem cores explícitas. Tentando rasterizar...", file=sys.stderr)
            # Fallback: rasterizar SVG via Pillow
            from PIL import ImageDraw
            try:
                from cairosvg import svg2png
            except ImportError:
                print("   ERRO: cairosvg não instalado. SVG sem cores explícitas precisa de cairosvg.",
                      file=sys.stderr)
                sys.exit(1)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                svg2png(url=logo_path, write_to=f.name)
                palette = extract_from_raster(f.name)
            os.unlink(f.name)
    else:
        print("   Formato: Raster (Pillow + K-Means)")
        palette = extract_from_raster(logo_path)

    if not palette:
        print("ERRO: Não foi possível extrair cores da logo.", file=sys.stderr)
        sys.exit(1)

    if len(palette) < 3:
        print(f"ERRO: Paleta com apenas {len(palette)} cores detectadas (mínimo: 3). "
              "A logo pode ser muito simples ou monocromática.", file=sys.stderr)
        print("Cores encontradas:", [c[0] for c in palette], file=sys.stderr)
        sys.exit(1)

    print(f"   Cores extraídas ({len(palette)}):")
    for hex_c, freq, _ in palette:
        print(f"     ■ {hex_c}  ({freq*100:.0f}%)")

    # ── Fase B: Classificação + Derivação ──
    print()
    print("📦 Fase B: Classificando e derivando sistema...")
    classified = classify_palette(palette)
    system = derive_system_colors(classified)
    print("   Sistema cromático:")
    for key in ["primary", "secondary", "tertiary", "accent", "neutral", "dark"]:
        print(f"     {key:12s} → {system.get(key, '—')}")
    print(f"     {'on-primary':12s} → {system.get('on-primary', '—')}")
    print(f"     {'on-tertiary':12s} → {system.get('on-tertiary', '—')}")
    print(f"     {'danger':12s} → {system.get('danger', '—')}  (semântica, herdada)")
    print(f"     {'success':12s} → {system.get('success', '—')}  (semântica, herdada)")
    print(f"     {'warning':12s} → {system.get('warning', '—')}  (semântica, herdada)")

    # ── Fase C: Validação WCAG ──
    print()
    print("📦 Fase C: Validando WCAG AA...")
    issues = validate_wcag(system)
    adjustments = []
    if issues:
        print(f"   ⚠ {len(issues)} par(es) abaixo de 4.5:1")
        for iss in issues:
            print(f"     {iss['pair']}: {iss['ratio']}:1 — ajustando...")
            new_text = adjust_for_contrast(iss["text_hex"], iss["bg_hex"])
            if new_text != iss["text_hex"]:
                adjustments.append((iss["pair"], iss["text_hex"], new_text))
                # Aplicar ajuste ao system
                text_key = iss["pair"].split("/")[0]
                system[text_key] = new_text
                print(f"       → {iss['text_hex']} → {new_text} (agora {contrast_ratio(new_text, iss['bg_hex']):.1f}:1)")
    else:
        print("   ✅ Todos os pares atendem WCAG AA (≥ 4.5:1)")

    if adjustments:
        print(f"   Ajustes feitos: {len(adjustments)}")
        for pair, old, new in adjustments:
            print(f"     {pair}: {old} → {new}")

    # ── Fase D: Geração ──
    print()
    print("📦 Fase D: Gerando DESIGN.md...")
    design_md = generate_design_md(system, brand_name, slug)

    # ── Fase E: Persistência ──
    if args.dry_run:
        print()
        print("=" * 60)
        print("📄 DESIGN.md (dry-run — stdout):")
        print("=" * 60)
        print(design_md)
        print(f"\n✅ Dry-run completo. {len(palette)} cores extraídas, "
              f"{len(adjustments)} ajustes WCAG.")
        return

    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, "DESIGN.md")
    with open(outpath, "w") as f:
        f.write(design_md)
    print(f"   ✅ Escrito: {outpath}")

    # Rodar lint se disponível
    print()
    print("📦 Lint: verificando DESIGN.md...")
    import subprocess
    try:
        result = subprocess.run(
            ["npx", "-y", "@google/design.md", "lint", outpath],
            capture_output=True, text=True, timeout=30
        )
        print(f"   → exit code: {result.returncode}")
        if result.stdout:
            for line in result.stdout.strip().split("\n"):
                print(f"     {line}")
        if result.stderr:
            for line in result.stderr.strip().split("\n"):
                print(f"     ⚠ {line}")
        if result.returncode == 0:
            print("   ✅ Lint passou!")
        else:
            print("   ⚠ Lint reportou problemas (acima).")
    except FileNotFoundError:
        print("   ⚠ npx não encontrado no PATH. Lint pulado (instale Node.js).")
    except subprocess.TimeoutExpired:
        print("   ⚠ Lint timeout (30s). Pulado.")
    except Exception as e:
        print(f"   ⚠ Lint falhou: {e}")

    print()
    print(f"✅ brandkit-generator concluído para {brand_name}.")
    print(f"   DESIGN.md: {outpath}")
    print(f"   Cores extraídas: {len(palette)}")
    print(f"   Ajustes WCAG: {len(adjustments)}")
    print(f"   extends: global ✓")


if __name__ == "__main__":
    main()
