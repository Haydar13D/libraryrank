import re
import os

base_dir = r"d:\Code\libraryrank"

# 1. Update base.html
base_path = os.path.join(base_dir, "leaderboard", "templates", "leaderboard", "base.html")
with open(base_path, "r", encoding="utf-8") as f:
    base_html = f.read()

base_html = base_html.replace(
    'style="background:rgba(255,255,255,0.1); border:none; color:white;',
    'style="background:var(--surface2); border:1px solid var(--border); color:var(--text);'
)
base_html = base_html.replace(
    'class="live-badge"><span class="live-dot"></span>Live</span>',
    'class="live-badge" style="color:var(--text);"><span class="live-dot"></span>Live</span>'
)
base_html = base_html.replace(
    'background: rgba(245, 200, 66, 0.15);',
    'background: var(--surface2);'
)
base_html = base_html.replace(
    'border: 1px solid rgba(245, 200, 66, .4);',
    'border: 1px solid var(--border);'
)
base_html = base_html.replace(
    'color: var(--gold);',
    'color: var(--text);'
)
base_html = base_html.replace(
    'style="font-size:1rem; color:var(--gold);"',
    'style="font-size:1rem; color:var(--text);"'
)
base_html = base_html.replace(
    'class="btn-admin" style="display: flex; align-items: center; gap: 6px;"',
    'class="btn-admin" style="display: flex; align-items: center; gap: 6px; background:var(--surface2); border:1px solid var(--border); color:var(--text);"'
)
with open(base_path, "w", encoding="utf-8") as f:
    f.write(base_html)

# 2. Update index.html
index_path = os.path.join(base_dir, "leaderboard", "templates", "leaderboard", "index.html")
with open(index_path, "r", encoding="utf-8") as f:
    index_html = f.read()

index_html = index_html.replace(
    'border: 1px solid rgba(255,215,0,0.15);',
    'border: 1px solid var(--border);'
)
index_html = index_html.replace(
    'background:rgba(0,0,0,0.25); border-radius:12px; padding:12px; border:1px solid rgba(255,215,0,0.18);',
    'background:var(--surface); border-radius:12px; padding:12px; border:1px solid var(--border);'
)
index_html = index_html.replace(
    'color:white; font-weight:600;',
    'color:var(--text); font-weight:600;'
)
index_html = index_html.replace(
    'color:var(--gold); font-size:0.78rem; font-weight:bold;',
    'color:var(--text); font-size:0.78rem; font-weight:bold;'
)
index_html = index_html.replace(
    'background:rgba(0,0,0,0.55);',
    'background:var(--surface2); color:var(--text); border:1px solid var(--border);'
)
index_html = index_html.replace(
    'color:white; font-size:1.1rem;',
    'color:var(--text); font-size:1.1rem;'
)

with open(index_path, "w", encoding="utf-8") as f:
    f.write(index_html)


# 3. Update main.css
css_path = os.path.join(base_dir, "static", "css", "main.css")
with open(css_path, "r", encoding="utf-8") as f:
    css = f.read()

# Replace .ums-header
css = re.sub(
    r'\.ums-header\s*\{[^}]+\}',
    '.ums-header {\n  position: sticky;\n  top: 0;\n  z-index: 100;\n  background: var(--surface);\n  border-bottom: 1px solid var(--border);\n  padding: 0 32px;\n  display: flex;\n  align-items: center;\n  justify-content: space-between;\n  height: 84px;\n}',
    css
)

# Text colors in header
css = css.replace('.logo-text-block {\n  display: flex;\n  flex-direction: column;\n  justify-content: center;\n  color: #ffffff;\n}', '.logo-text-block {\n  display: flex;\n  flex-direction: column;\n  justify-content: center;\n  color: var(--text);\n}')
css = css.replace('.acc-circle {\n  border: 2px solid #ffffff;', '.acc-circle {\n  border: 1px solid var(--border);\n  color: var(--text);')
css = css.replace('color: #ffffff;\n  line-height: 1;\n}', 'color: var(--text);\n  line-height: 1;\n}')
css = css.replace('color: #4DA6FF;', 'color: var(--muted);')
css = css.replace('color: #82C0FF;', 'color: var(--text);')
css = css.replace('text-shadow: 0 0 8px rgba(77, 166, 255, 0.6);', '')
css = css.replace('color: #0088FF;', 'color: var(--primary);')
css = css.replace('text-shadow: 0 0 10px rgba(0, 136, 255, 0.4);', '')

# Replace .btn-admin
css = re.sub(
    r'\.btn-admin\s*\{[^}]+\}',
    '.btn-admin {\n  background: var(--surface2);\n  border: 1px solid var(--border);\n  color: var(--text);\n  padding: 8px 18px;\n  border-radius: 10px;\n  font-weight: 600;\n  font-size: 0.85rem;\n  text-decoration: none;\n  transition: all 0.2s;\n}',
    css
)
css = re.sub(
    r'\.btn-admin:hover\s*\{[^}]+\}',
    '.btn-admin:hover {\n  background: var(--surface3);\n  color: var(--text);\n}',
    css
)
css = re.sub(
    r'\.demo-badge\s*\{[^}]+\}',
    '.demo-badge {\n  font-size: .78rem;\n  font-weight: 700;\n  padding: 5px 12px;\n  border-radius: 20px;\n  background: var(--surface2);\n  border: 1px solid var(--border);\n  color: var(--text);\n}',
    css
)

# Hero section
css = re.sub(
    r'\.hero\s*\{[^}]+\}',
    '.hero {\n  position: relative;\n  text-align: center;\n  padding: 85px 32px 65px;\n  background: var(--surface);\n  border-radius: 0 0 24px 24px;\n  border-bottom: 1px solid var(--border);\n}',
    css
)
css = re.sub(r'\.hero-glow\s*\{[^}]+\}', '.hero-glow { display: none; }', css)
css = css.replace('font-family: \'Poppins\', sans-serif;', 'font-family: \'Inter\', sans-serif;')
css = re.sub(
    r'\.hero h1\s*\{[^}]+\}',
    '.hero h1 {\n  font-family: \'Inter\', sans-serif;\n  font-weight: 800;\n  font-size: clamp(2rem, 5vw, 3.8rem);\n  line-height: 1.1;\n  margin-bottom: 16px;\n  color: var(--text);\n  letter-spacing: -0.02em;\n}',
    css
)
css = re.sub(
    r'\.hero h1 span\s*\{[^}]+\}',
    '.hero h1 span {\n  color: var(--primary);\n}',
    css
)
css = re.sub(
    r'\.hero p\s*\{[^}]+\}',
    '.hero p {\n  color: var(--muted);\n  font-size: 1.05rem;\n  max-width: 520px;\n  margin: 0 auto;\n}',
    css
)

# Podium base
css = css.replace('background: linear-gradient(180deg, #FFB800, #D99C00);', 'background: var(--gold);')
css = css.replace('background: linear-gradient(180deg, #b8c4d4, #7a8ea8);', 'background: var(--silver);')
css = css.replace('background: linear-gradient(180deg, #cd7c4a, #8f4e20);', 'background: var(--bronze);')
css = css.replace('box-shadow: 0 0 30px rgba(245, 200, 66, .4);', '')

# Remove shimmer and glow animations
css = css.replace('animation: glowGold 1.5s infinite alternate;', '')
css = css.replace('animation: glowSilver 1.5s infinite alternate;', '')
css = css.replace('animation: glowBronze 1.5s infinite alternate;', '')
css = css.replace('animation: shimmer 1.5s infinite;', '')

css = css.replace('border: 1px solid rgba(245, 200, 66, 0.6);', 'border: 1px solid var(--gold);')
css = css.replace('background: linear-gradient(90deg, rgba(255, 184, 0, 0.15), transparent);', 'background: var(--surface);')
css = css.replace('box-shadow: 0 0 15px rgba(245, 200, 66, 0.15);', '')

css = css.replace('border: 1px solid rgba(184, 196, 212, 0.5);', 'border: 1px solid var(--silver);')
css = css.replace('background: linear-gradient(90deg, rgba(184, 196, 212, 0.08), transparent);', 'background: var(--surface);')
css = css.replace('box-shadow: 0 0 10px rgba(184, 196, 212, 0.1);', '')

css = css.replace('border: 1px solid rgba(205, 124, 74, 0.4);', 'border: 1px solid var(--bronze);')
css = css.replace('background: linear-gradient(90deg, rgba(205, 124, 74, 0.08), transparent);', 'background: var(--surface);')

# Linear gradients in nom-cards
css = css.replace('background: linear-gradient(90deg, var(--blue), var(--purple));', 'background: var(--blue);')
css = css.replace('background: linear-gradient(90deg, var(--green), var(--blue));', 'background: var(--green);')
css = css.replace('background: linear-gradient(90deg, var(--orange), var(--pink));', 'background: var(--orange);')

# Linear gradient in section title
css = css.replace('background: linear-gradient(90deg, var(--border), transparent);', 'background: var(--border);')

# Linear gradient in bars
css = css.replace('background: linear-gradient(90deg, var(--blue), var(--purple));', 'background: var(--primary);')

# Box shadow cleanups
css = css.replace('box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);', 'box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);')
css = css.replace('box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);', 'box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);')

with open(css_path, "w", encoding="utf-8") as f:
    f.write(css)

print("UI Update Complete")
