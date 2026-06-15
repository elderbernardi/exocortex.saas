#!/usr/bin/env python3
"""
Provisiona a skin EXCRTX no Hermes WebUI e define-a como padrão (light mode).
Aplica identidade visual completa: logos, textos, bot name.
Idempotente — seguro rodar múltiplas vezes.

Uso:
  python3 provision-excrtx-skin.py [--dry-run]
  python3 provision-excrtx-skin.py --remove   (remove a skin)
"""

import sys
import os
import re
import shutil
import subprocess
from pathlib import Path

HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
WEBUI_DIR = os.path.join(HERMES_HOME, "hermes-webui")
STATIC = os.path.join(WEBUI_DIR, "static")
API = os.path.join(WEBUI_DIR, "api")

SKIN_NAME = "excrtx"

# ─── Asset paths ─────────────────────────────────────────────────────────
SVG_TITLEBAR_SRC = None  # set by find_asset_sources()
PNG_LOGO_SRC = None
SVG_TITLEBAR_DST = os.path.join(STATIC, "excrtx-titlebar.svg")
PNG_LOGO_DST = os.path.join(STATIC, "excrtx-logo.png")


def find_asset_sources():
    """Localiza as logos fonte no acervo e no diretório de provisionamento."""
    global SVG_TITLEBAR_SRC, PNG_LOGO_SRC

    # O SVG do titlebar está no static/ (já copiado ou será gerado)
    candidates_svg = [
        os.path.join(STATIC, "excrtx-titlebar.svg"),
        os.path.join(WEBUI_DIR, "excrtx-titlebar.svg"),
    ]
    for c in candidates_svg:
        if os.path.isfile(c):
            SVG_TITLEBAR_SRC = c
            break

    # O PNG da logo está no acervo
    candidates_png = [
        os.path.join(os.environ.get("ACERVO", ""), "_artifacts", "items", "EXCRTX-logo-main.png"),
        os.path.join(HERMES_HOME, "..", "projetos", "projetob", "exocortex.saas",
                     "acervo", "_artifacts", "items", "EXCRTX-logo-main.png"),
        os.path.join(HERMES_HOME, "..", "..", "home", "elder", "projetos", "projetob",
                     "exocortex.saas", "acervo", "_artifacts", "items", "EXCRTX-logo-main.png"),
    ]
    # Expand ~
    candidates_png = [os.path.expanduser(c) for c in candidates_png]
    for c in candidates_png:
        if os.path.isfile(c):
            PNG_LOGO_SRC = c
            break


# ─── Helpers ──────────────────────────────────────────────────────────────

def log(msg):
    print(f"  {msg}")

def warn(msg):
    print(f"  ⚠ {msg}")

def ok(msg):
    print(f"  ✅ {msg}")


def check_installed():
    """Verifica se a WebUI está instalada e acessível."""
    if not os.path.isdir(WEBUI_DIR):
        print(f"ERRO: Hermes WebUI não encontrada em {WEBUI_DIR}")
        sys.exit(1)
    css = os.path.join(STATIC, "style.css")
    if not os.path.isfile(css):
        print(f"ERRO: style.css não encontrado em {css}")
        sys.exit(1)
    # Find asset sources
    find_asset_sources()
    return True


# ─── Branding (logos, textos, bot name) ──────────────────────────────────

def is_branding_applied():
    """Verifica se o branding já foi aplicado."""
    html_path = os.path.join(STATIC, "index.html")
    with open(html_path) as f:
        content = f.read()
    return "EXCRTX.IA" in content and "excrtx-titlebar.svg" in content


def apply_branding(dry_run=False):
    """Aplica a identidade visual EXCRTX na WebUI."""
    if is_branding_applied():
        ok("Branding: identidade EXCRTX já aplicada")
        return True

    print("🏷  Aplicando identidade visual...")
    changes = 0

    # 1. Nome do bot via .env
    env_path = os.path.join(WEBUI_DIR, ".env")
    env_updated = False
    env_lines = []
    if os.path.isfile(env_path):
        with open(env_path) as f:
            env_lines = f.readlines()

    bot_name_set = any("HERMES_WEBUI_BOT_NAME" in l for l in env_lines)
    if not bot_name_set:
        env_lines.append("HERMES_WEBUI_BOT_NAME=EXCRTX.IA\n")
        env_updated = True
        changes += 1
        log(".env: HERMES_WEBUI_BOT_NAME=EXCRTX.IA")

    if env_updated and not dry_run:
        with open(env_path, "w") as f:
            f.writelines(env_lines)

    # 1b. Atualizar settings.json (persistência do servidor)
    settings_path = os.path.join(WEBUI_DIR, os.environ.get("HERMES_WEBUI_STATE_DIR",
                                  os.path.join(HERMES_HOME, "webui")), "settings.json")
    if os.path.isfile(settings_path):
        with open(settings_path) as f:
            settings_content = f.read()
        if '"bot_name": "Hermes"' in settings_content:
            settings_content = settings_content.replace('"bot_name": "Hermes"', '"bot_name": "EXCRTX.IA"')
            if not dry_run:
                with open(settings_path, "w") as f:
                    f.write(settings_content)
            changes += 1
            log("settings.json: bot_name → EXCRTX.IA")

    # 2. Copiar assets
    assets_copied = 0
    if SVG_TITLEBAR_SRC and not os.path.isfile(SVG_TITLEBAR_DST):
        if not dry_run:
            shutil.copy2(SVG_TITLEBAR_SRC, SVG_TITLEBAR_DST)
        assets_copied += 1
        log("static/excrtx-titlebar.svg copiado")
    elif not SVG_TITLEBAR_SRC:
        warn("SVG titlebar fonte não encontrado — gere com o script primeiro")

    if PNG_LOGO_SRC and not os.path.isfile(PNG_LOGO_DST):
        if not dry_run:
            shutil.copy2(PNG_LOGO_SRC, PNG_LOGO_DST)
        assets_copied += 1
        log("static/excrtx-logo.png copiado")
    elif not PNG_LOGO_SRC:
        warn("PNG logo fonte não encontrado em acervo/_artifacts/items/")

    changes += assets_copied

    # 3. HTML: substituir elementos de branding
    html_path = os.path.join(STATIC, "index.html")
    with open(html_path) as f:
        html = f.read()

    # 3a. Page title
    if "<title>Hermes</title>" in html:
        html = html.replace("<title>Hermes</title>", "<title>EXCRTX.IA</title>")
        changes += 1
        log("index.html: <title> → EXCRTX.IA")

    # 3b. Titlebar: replace inline SVG with SVG file reference
    # O bloco antigo:
    # <span class="app-titlebar-icon" aria-hidden="true">
    #   <svg viewBox="0 0 64 64" width="16" height="16" aria-hidden="true">...</svg>
    # </span>
    old_titlebar_svg = (
        '<span class="app-titlebar-icon" aria-hidden="true">\n'
        '      <svg viewBox="0 0 64 64" width="16" height="16" aria-hidden="true">'
    )
    new_titlebar_svg = (
        '<span class="app-titlebar-icon" aria-hidden="true">\n'
        '      <img src="static/excrtx-titlebar.svg" width="16" height="16" alt="EXCRTX" aria-hidden="true">'
    )
    if old_titlebar_svg in html:
        # Encontrar o fechamento do SVG e substituir tudo até </span>
        start = html.index(old_titlebar_svg)
        end_svg_close = html.index("</svg>", start) + len("</svg>")
        # Verificar se o que segue é o </span>
        rest = html[end_svg_close:].lstrip()
        if rest.startswith("\n    </span>"):
            end_span = html.index("</span>", end_svg_close) + len("</span>")
            html = html[:start] + new_titlebar_svg + "\n    </span>" + html[end_span + len("</span>"):] if False else None
            # Abordagem mais simples: regex replace do bloco inteiro
            pass

    # Abordagem mais robusta: substituir o conteúdo interno do span
    pattern_titlebar = (
        r'(<span class="app-titlebar-icon" aria-hidden="true">)\s*'
        r'<svg viewBox="0 0 64 64" width="16" height="16" aria-hidden="true">.*?</svg>\s*'
        r'(</span>)'
    )
    replacement_titlebar = (
        r'\1\n      <img src="static/excrtx-titlebar.svg" width="16" height="16" '
        r'alt="EXCRTX" aria-hidden="true">\n    \2'
    )
    new_html = re.sub(pattern_titlebar, replacement_titlebar, html, flags=re.DOTALL)
    if new_html and new_html != html:
        html = new_html
        changes += 1
        log("index.html: titlebar icon → EXCRTX SVG")

    # 3c. Titlebar text "Hermes" → "EXCRTX.IA"
    # <span class="app-titlebar-title" id="appTitlebarTitle">Hermes</span>
    if '<span class="app-titlebar-title" id="appTitlebarTitle">Hermes</span>' in html:
        html = html.replace(
            '<span class="app-titlebar-title" id="appTitlebarTitle">Hermes</span>',
            '<span class="app-titlebar-title" id="appTitlebarTitle">EXCRTX.IA</span>'
        )
        changes += 1
        log("index.html: titlebar text → EXCRTX.IA")

    # 3d. Empty state: replace large inline SVG with PNG img
    pattern_empty_svg = (
        r'<div class="empty-logo"><svg xmlns="http://www.w3.org/2000/svg" '
        r'viewBox="0 0 64 64" width="80" height="80" aria-label="Hermes caduceus">'
        r'.*?</svg></div>'
    )
    replacement_empty = (
        '<div class="empty-logo">'
        '<img src="static/excrtx-logo.png" width="80" height="80" alt="EXCRTX.IA" '
        'style="border-radius:12px">'
        '</div>'
    )
    new_html = re.sub(pattern_empty_svg, replacement_empty, html, flags=re.DOTALL)
    if new_html and new_html != html:
        html = new_html
        changes += 1
        log("index.html: empty-state logo → EXCRTX PNG")

    # 3e. Empty state heading
    if '<h2 data-i18n="empty_title">What can I help with?</h2>' in html:
        html = html.replace(
            '<h2 data-i18n="empty_title">What can I help with?</h2>',
            '<h2 data-i18n="empty_title">Exocórtex.IA — cognição estendida</h2>'
        )
        changes += 1
        log("index.html: heading → EXCRTX")

    # 3f. Header Hermes → EXCRTX.IA nos banners
    if "<strong>Hermes agent is not responding</strong>" in html:
        html = html.replace(
            "<strong>Hermes agent is not responding</strong>",
            "<strong>Exocórtex.IA agent is not responding</strong>"
        )
        changes += 1

    if dry_run:
        log(f"Branding: dry-run ({changes} alterações)")
        return True

    if changes > 0:
        shutil.copy2(html_path, html_path + ".bak3")
        with open(html_path, "w") as f:
            f.write(html)
        ok(f"Branding: {changes} alterações aplicadas")
    else:
        ok("Branding: nada a alterar")

    return True


# ─── CSS block to inject ──────────────────────────────────────────────────

CSS_BLOCK = """
  /* ── Skin: EXCRTX (Exocórtex.IA) ──
     Deep navy surfaces with electric blue accent, derived from the EXCRTX.IA
     logo palette (#03123f primary, #1376ed accent). Light mode uses cool gray
     surfaces; dark mode uses near-black navy. Monospace font stack stays
     pragmatic, not playful. Opt-in via Settings → Skin picker. */
  :root[data-skin="excrtx"]{
    color-scheme:light;
    --bg:#f4f5f8;--sidebar:#e8ecf2;--surface:#ffffff;--surface-subtle:#f0f2f6;--surface-subtle-hover:#e4e8ef;
    --main-bg:#f4f5f8;--topbar-bg:rgba(244,245,248,.96);
    --border:#d2d6e3;--border2:#bcc1ce;--border-subtle:#e0e4ec;--border-muted:#c5cad6;
    --text:#03123f;--strong:#010a28;--muted:#8f8a91;--em:#1a3c86;
    --accent:#1376ed;--accent-hover:#0e5fd6;--accent-bg:rgba(19,118,237,.08);--accent-bg-strong:rgba(19,118,237,.16);--accent-text:#0e5fd6;
    --blue:#1376ed;--gold:#1a3c86;--focus-ring:rgba(19,118,237,.3);--focus-glow:rgba(19,118,237,.1);
    --input-bg:#ffffff;--hover-bg:#e8ecf2;--code-bg:#f0f2f6;--code-inline-bg:#e4e8ef;--code-text:#03123f;--pre-text:#03123f;
    --error:#E53E3E;--success:#38A169;--warning:#D69E2E;--info:#1376ed;
    --radius-sm:4px;--radius-md:8px;--radius-card:8px;--radius-lg:12px;
    --font-ui:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,system-ui,sans-serif;
    --user-bubble-bg:#e8ecf2;--user-bubble-border:#d2d6e3;--user-bubble-text:#03123f;--user-bubble-placeholder:#8f8a91;
    --user-selection-bg:rgba(19,118,237,.22);--user-selection-text:#03123f;
  }
  :root.dark[data-skin="excrtx"]{
    color-scheme:dark;
    --bg:#181f30;--sidebar:#1d2539;--surface:#222c42;--surface-subtle:#263148;--surface-subtle-hover:#2c3852;
    --main-bg:#181f30;--topbar-bg:rgba(24,31,48,.96);
    --border:#2a3652;--border2:#334062;--border-subtle:#232d47;--border-muted:#2a3652;
    --text:#c8d2e2;--strong:#e8ecf2;--muted:#6e7a94;--em:#99a8c2;
    --accent:#3b8af0;--accent-hover:#5c9ff4;--accent-bg:rgba(59,138,240,.12);--accent-bg-strong:rgba(59,138,240,.2);--accent-text:#6baaf6;
    --blue:#3b8af0;--gold:#6baaf6;--focus-ring:rgba(59,138,240,.28);--focus-glow:rgba(59,138,240,.08);
    --input-bg:#1d2539;--hover-bg:rgba(59,138,240,.08);--code-bg:#181f30;--code-inline-bg:rgba(59,138,240,.1);--code-text:#99a8c2;--pre-text:#c8d2e2;
    --error:#F07178;--success:#7EC98C;--warning:#E6B86E;--info:#3b8af0;
    --user-bubble-bg:#263148;--user-bubble-border:#334062;--user-bubble-text:#c8d2e2;--user-bubble-placeholder:#6e7a94;
    --user-selection-bg:rgba(59,138,240,.28);--user-selection-text:#e8ecf2;
  }
  /* EXCRTX skin: component-level overrides */
  :root[data-skin="excrtx"],:root[data-skin="excrtx"] body{background:var(--bg)!important;}
  :root[data-skin="excrtx"] .app-titlebar,
  :root[data-skin="excrtx"] .rail,
  :root[data-skin="excrtx"] .sidebar,
  :root[data-skin="excrtx"] .rightpanel,
  :root[data-skin="excrtx"] .topbar,
  :root[data-skin="excrtx"] .composer-wrap{background:var(--sidebar)!important;border-color:var(--border)!important;box-shadow:none!important;}
  :root[data-skin="excrtx"] .main,
  :root[data-skin="excrtx"] .chat,
  :root[data-skin="excrtx"] .panel-view{background:var(--bg)!important;}
  /* New chat / send buttons: electric blue solid */
  :root[data-skin="excrtx"]:not(.dark) .new-chat-btn,
  :root.dark[data-skin="excrtx"] .new-chat-btn,
  :root[data-skin="excrtx"] button.send-btn:not(:disabled),
  :root[data-skin="excrtx"] .btn.primary,
  :root[data-skin="excrtx"] .update-primary,
  :root[data-skin="excrtx"] .clarify-submit{background:var(--accent)!important;border-color:var(--accent)!important;color:#fff!important;font-weight:600!important;box-shadow:0 1px 3px rgba(19,118,237,.28)!important;}
  :root[data-skin="excrtx"]:not(.dark) .new-chat-btn:hover,
  :root.dark[data-skin="excrtx"] .new-chat-btn:hover,
  :root[data-skin="excrtx"] button.send-btn:not(:disabled):hover,
  :root[data-skin="excrtx"] .btn.primary:hover{background:var(--accent-hover)!important;border-color:var(--accent-hover)!important;box-shadow:0 2px 8px rgba(19,118,237,.45)!important;}
  /* Active session: left accent bar */
  :root[data-skin="excrtx"] .session-item.active{border-left:2px solid var(--accent);}
  :root[data-skin="excrtx"] .session-item.active .session-title,
  :root[data-skin="excrtx"] .session-item.active .session-meta{color:var(--accent-text)!important;}
  /* Tool cards */
  :root[data-skin="excrtx"] .tool-card{background:var(--surface-subtle)!important;border-color:var(--border)!important;}
  :root[data-skin="excrtx"] .tool-card:hover{border-color:var(--border2)!important;}
  :root[data-skin="excrtx"] .tool-card-running{background:var(--accent-bg)!important;border-color:var(--accent-bg-strong)!important;}
  :root[data-skin="excrtx"] .tool-arg-key,
  :root[data-skin="excrtx"] .tool-card-more{color:var(--accent-text)!important;}
  :root[data-skin="excrtx"] .tool-card-running-dot{background:var(--accent)!important;}
  /* User bubble */
  :root[data-skin="excrtx"] .msg-row[data-role="user"] .msg-body{background:var(--user-bubble-bg)!important;border:1px solid var(--user-bubble-border)!important;border-radius:12px!important;color:var(--user-bubble-text)!important;}
  /* Composer */
  :root[data-skin="excrtx"] .composer-box{border-radius:12px!important;}
  :root[data-skin="excrtx"] .composer-box:focus-within{border-color:var(--accent)!important;box-shadow:0 0 0 3px var(--focus-ring)!important;}
  /* Logo */
  :root[data-skin="excrtx"] .logo{background:linear-gradient(145deg,var(--accent-hover),var(--accent))!important;box-shadow:0 2px 10px var(--accent-bg-strong)!important;}
  /* Links */
  :root[data-skin="excrtx"] .msg-body a,
  :root[data-skin="excrtx"] .preview-md a{color:var(--accent-text)!important;}
  :root[data-skin="excrtx"] ::selection{background:var(--accent-bg-strong);}
  /* Scrollbar */
  :root[data-skin="excrtx"]::-webkit-scrollbar-thumb{background:var(--border2)!important;}
  :root[data-skin="excrtx"]::-webkit-scrollbar-thumb:hover{background:var(--accent-bg-strong)!important;}

"""

# ─── Skin registration ────────────────────────────────────────────────────

def is_skin_registered():
    """Verifica se a skin já está registrada (CSS + index.html)."""
    css_path = os.path.join(STATIC, "style.css")
    html_path = os.path.join(STATIC, "index.html")
    with open(css_path) as f:
        css_ok = 'data-skin="excrtx"' in f.read()
    with open(html_path) as f:
        html_ok = "excrtx:1" in f.read()
    return css_ok and html_ok


def inject_css(dry_run=False):
    css_path = os.path.join(STATIC, "style.css")
    marker = '  /* ── Skin: Zeus ──'
    with open(css_path) as f:
        content = f.read()
    if 'data-skin="excrtx"' in content:
        ok("CSS: skin EXCRTX já presente")
        return True
    if marker not in content:
        warn("CSS: marker 'Skin: Zeus' não encontrado")
        return False
    new_content = content.replace(marker, CSS_BLOCK.rstrip("\n") + "\n" + marker)
    if dry_run:
        log("CSS: dry-run")
        return True
    shutil.copy2(css_path, css_path + ".bak")
    with open(css_path, "w") as f:
        f.write(new_content)
    ok("CSS: skin EXCRTX injetada")
    return True


def register_in_index(dry_run=False):
    html_path = os.path.join(STATIC, "index.html")
    with open(html_path) as f:
        content = f.read()
    if "excrtx:1" in content:
        ok("index.html: skin já registrada")
        return True
    old = "'verdigris':1}"
    new = "'verdigris':1,excrtx:1}"
    if old not in content:
        warn("index.html: padrão não encontrado")
        return False
    if dry_run:
        log("index.html: dry-run")
        return True
    shutil.copy2(html_path, html_path + ".bak")
    with open(html_path, "w") as f:
        f.write(content.replace(old, new))
    ok("index.html: skin registrada")
    return True


def register_in_config(dry_run=False):
    cfg_path = os.path.join(API, "config.py")
    with open(cfg_path) as f:
        content = f.read()
    if '"excrtx"' in content:
        ok("config.py: skin já registrada")
        return True
    old = '    "verdigris",\n}'
    new = '    "verdigris",\n    "excrtx",\n}'
    if old not in content:
        warn("config.py: padrão não encontrado")
        return False
    if dry_run:
        log("config.py: dry-run")
        return True
    shutil.copy2(cfg_path, cfg_path + ".bak")
    with open(cfg_path, "w") as f:
        f.write(content.replace(old, new))
    ok("config.py: skin registrada")
    return True


def register_in_boot(dry_run=False):
    boot_path = os.path.join(STATIC, "boot.js")
    with open(boot_path) as f:
        content = f.read()
    if "name:'EXCRTX'" in content:
        ok("boot.js: skin já registrada")
        return True
    old = "  {name:'Verdigris', value:'verdigris', colors:['#C89A5A','#0F1714','#22342C']},\n];"
    new = ("  {name:'Verdigris', value:'verdigris', colors:['#C89A5A','#0F1714','#22342C']},\n"
           "  {name:'EXCRTX', value:'excrtx', colors:['#181f30','#c8d2e2','#3b8af0']},\n];")
    if old not in content:
        warn("boot.js: padrão não encontrado")
        return False
    if dry_run:
        log("boot.js: dry-run")
        return True
    shutil.copy2(boot_path, boot_path + ".bak")
    with open(boot_path, "w") as f:
        f.write(content.replace(old, new))
    ok("boot.js: skin registrada")
    return True


def register_in_i18n(dry_run=False):
    i18n_path = os.path.join(STATIC, "i18n.js")
    with open(i18n_path) as f:
        content = f.read()
    if "/excrtx)" in content:
        ok("i18n.js: skin já registrada")
        return True
    new_content = content.replace("/verdigris)", "/verdigris/excrtx)")
    if new_content == content:
        warn("i18n.js: padrão não encontrado")
        return False
    if dry_run:
        log(f"i18n.js: dry-run ({new_content.count('/excrtx)')} idiomas)")
        return True
    shutil.copy2(i18n_path, i18n_path + ".bak")
    with open(i18n_path, "w") as f:
        f.write(new_content)
    ok(f"i18n.js: skin registrada em {new_content.count('/excrtx)')} idiomas")
    return True


def set_defaults(dry_run=False):
    html_path = os.path.join(STATIC, "index.html")
    cfg_path = os.path.join(API, "config.py")
    with open(html_path) as f:
        content = f.read()
    changes = 0
    if "||'dark'" in content:
        content = content.replace("||'dark'", "||'light'")
        changes += 1
        log("index.html: tema default → light")
    if "m?m[1]:'default'" in content:
        content = content.replace("m?m[1]:'default'", "m?m[1]:'excrtx'")
        changes += 1
        log("index.html: skin default → excrtx")
    with open(cfg_path) as f:
        cfg_content = f.read()
    if '"skin": "default"' in cfg_content:
        cfg_content = cfg_content.replace('"skin": "default"', '"skin": "excrtx"')
        changes += 1
        log("config.py: skin default → excrtx")
    if dry_run:
        log(f"defaults: dry-run ({changes} alterações)")
        return True
    if changes > 0:
        shutil.copy2(html_path, html_path + ".bak2")
        with open(html_path, "w") as f:
            f.write(content)
        shutil.copy2(cfg_path, cfg_path + ".bak2")
        with open(cfg_path, "w") as f:
            f.write(cfg_content)
        ok(f"defaults: light + excrtx definidos ({changes} alterações)")
    else:
        ok("defaults: já configurados")
    return True


def restart_webui():
    ctl = os.path.join(WEBUI_DIR, "ctl.sh")
    if not os.path.isfile(ctl):
        warn("ctl.sh não encontrado — reinicie manualmente")
        return
    result = subprocess.run([ctl, "restart"], capture_output=True, text=True, timeout=15)
    if result.returncode == 0:
        ok("WebUI reiniciada")
    else:
        warn(f"WebUI restart falhou: {result.stderr.strip()}")


def remove_skin(dry_run=False):
    files_to_restore = [
        os.path.join(STATIC, "style.css"),
        os.path.join(STATIC, "index.html"),
        os.path.join(API, "config.py"),
        os.path.join(STATIC, "boot.js"),
        os.path.join(STATIC, "i18n.js"),
    ]
    restored = 0
    for fpath in files_to_restore:
        for suffix in [".bak3", ".bak2", ".bak"]:
            bak = fpath + suffix
            if os.path.isfile(bak):
                if not dry_run:
                    shutil.copy2(bak, fpath)
                log(f"Restaurado: {os.path.basename(fpath)} ({suffix})")
                restored += 1
                break
    if restored == 0:
        warn("Nenhum backup encontrado para restaurar")
    else:
        ok(f"{restored} arquivos restaurados")
    if not dry_run:
        restart_webui()


# ─── Main ─────────────────────────────────────────────────────────────────

def main():
    dry_run = "--dry-run" in sys.argv
    remove = "--remove" in sys.argv

    print(f"🎨 EXCRTX Skin + Branding Provisioner")
    print(f"   WebUI: {WEBUI_DIR}")
    print()

    check_installed()

    if remove:
        print("🗑  Removendo skin EXCRTX...")
        remove_skin(dry_run=dry_run)
        return

    # ── Skin registration ──
    if not is_skin_registered():
        print("📦 Instalando skin EXCRTX...")
        print()
        inject_css(dry_run=dry_run)
        register_in_index(dry_run=dry_run)
        register_in_config(dry_run=dry_run)
        register_in_boot(dry_run=dry_run)
        register_in_i18n(dry_run=dry_run)
        print()
    else:
        ok("Skin EXCRTX já registrada nos arquivos")
        print()

    # ── Branding (logos + textos + bot name) ──
    apply_branding(dry_run=dry_run)
    print()

    # ── Defaults ──
    set_defaults(dry_run=dry_run)

    if dry_run:
        print("\n✅ Dry-run completo. Nenhum arquivo modificado.")
        return

    restart_webui()
    print()
    print("✅ Skin + Branding EXCRTX provisionados.")
    print("   Tema padrão: light. Skin padrão: excrtx.")
    print("   Acesse a WebUI para confirmar.")


if __name__ == "__main__":
    main()
