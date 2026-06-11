#!/usr/bin/env python3
"""Refina paleta monocromática para Sales AI — v3.

A logo é #223874 (azul escuro). Precisamos de um sistema com
cores distintas entre si. O problema anterior: tertiary (púrpura)
era indistinguível da primary em luminosidade.

Nova estratégia:
- primary: #223874 (âncora da logo)
- secondary: cinza-azulado claro (variação de tom, não só luminosidade)
- tertiary: teal/verde-azulado claro (#3b82a4 → ajustar)
- accent: dourado/âmbar (contraste máximo)
- neutral: fundo frio
- dark: quase preto
"""

import json

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    return f"#{max(0,min(255,round(r))):02x}{max(0,min(255,round(g))):02x}{max(0,min(255,round(b))):02x}"

def relative_luminance(r, g, b):
    def lin(c):
        c = c/255.0
        return c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    return 0.2126*lin(r) + 0.7152*lin(g) + 0.0722*lin(b)

def contrast_ratio(hex1, hex2):
    r1,g1,b1 = hex_to_rgb(hex1); r2,g2,b2 = hex_to_rgb(hex2)
    l1 = relative_luminance(r1,g1,b1); l2 = relative_luminance(r2,g2,b2)
    return round((max(l1,l2)+0.05)/(min(l1,l2)+0.05), 2)

def adjust_for_contrast(text_hex, bg_hex, target=4.5):
    if contrast_ratio(text_hex, bg_hex) >= target:
        return text_hex
    r,g,b = hex_to_rgb(text_hex)
    bg_lum = relative_luminance(*hex_to_rgb(bg_hex))
    if bg_lum < 0.18:
        for t in range(1, 11):
            nr = int(r + (255-r)*(t/10)); ng = int(g + (255-g)*(t/10)); nb = int(b + (255-b)*(t/10))
            if contrast_ratio(rgb_to_hex(nr,ng,nb), bg_hex) >= target:
                return rgb_to_hex(nr,ng,nb)
        return "#FFFFFF"
    else:
        for t in range(1, 11):
            nr = int(r*(1-t/10)); ng = int(g*(1-t/10)); nb = int(b*(1-t/10))
            if contrast_ratio(rgb_to_hex(nr,ng,nb), bg_hex) >= target:
                return rgb_to_hex(nr,ng,nb)
        return "#111111"

primary = "#223874"
neutral = "#f4f4f6"
dark = "#101218"

# ── Paleta manual pensada para o Sistema Sales AI ──
# Uma empresa de vendas/CRM: azul confiança + quente âmbar ação
# Sistema: monocromático azul + accent quente

# Secondary: azul mais claro, lavado — bom para backgrounds secundários, hover states
# #5a6e9a → azul médio, visivelmente diferente da primary
secondary = "#5a6e9a"

# Tertiary: verde-teal escuro — complementa o azul, diferente em matiz e lum
# #1f6e5a → verde escuro, lum ~25%, visivelmente distinto
tertiary = "#1f6e5a"

# Accent: laranja-dourado — ação, CTA, badges
accent = "#e88d25"

print("=" * 60)
print("  PALETA REFINADA — SALES AI")
print("=" * 60)
print(f"primary      {primary}  (logo oficial)")
print(f"secondary    {secondary}  (azul médio)")
print(f"tertiary     {tertiary}  (verde-teal)")
print(f"accent       {accent}  (laranja ação)")
print(f"neutral      {neutral}  (fundo frio)")
print(f"dark         {dark}  (texto)")
print()

# Validar contrastes entre cores
pairs = [
    ("primary ↔ secondary", primary, secondary),
    ("primary ↔ tertiary", primary, tertiary),
    ("primary ↔ accent", primary, accent),
    ("secondary ↔ tertiary", secondary, tertiary),
    ("secondary ↔ accent", secondary, accent),
]
print("--- Contrastes entre cores do sistema ---")
for label, c1, c2 in pairs:
    cr = contrast_ratio(c1, c2)
    print(f"  {label:30s} {cr:4.1f}:1 (mín 3.0 → {'✅' if cr >= 3.0 else '⚠ mesma faixa'})")

print()

# on-* cores
on_primary = adjust_for_contrast("#FFFFFF", primary)
on_secondary = adjust_for_contrast("#101218", secondary)
on_tertiary = adjust_for_contrast("#FFFFFF", tertiary)
on_accent = adjust_for_contrast("#101218", accent)

fgpairs = [
    ("on-primary / primary", on_primary, primary),
    ("on-secondary / secondary", on_secondary, secondary),
    ("on-tertiary / tertiary", on_tertiary, tertiary),
    ("on-accent / accent", on_accent, accent),
    ("dark / neutral", dark, neutral),
]
print("--- WCAG AA (4.5:1) ---")
all_ok = True
for label, fg, bg in fgpairs:
    cr = contrast_ratio(fg, bg)
    ok = cr >= 4.5
    if not ok: all_ok = False
    print(f"  {label:35s} {cr:5.1f}:1  {'✅ AA' if ok else '❌ FALHA'}")

print()

system = {
    "primary": primary,
    "secondary": secondary,
    "tertiary": tertiary,
    "accent": accent,
    "neutral": neutral,
    "dark": dark,
    "on-primary": on_primary,
    "on-secondary": on_secondary,
    "on-tertiary": on_tertiary,
    "on-accent": on_accent,
    "danger": "#E53E3E",
    "success": "#38A169",
    "warning": "#D69E2E",
}

print("=" * 60)
print("  SISTEMA CROMÁTICO")
print("=" * 60)
print(json.dumps(system, indent=2))
