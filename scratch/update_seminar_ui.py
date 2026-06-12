import os

base_dir = r"d:\Code\libraryrank"
seminar_path = os.path.join(base_dir, "leaderboard", "templates", "leaderboard", "seminar.html")

with open(seminar_path, "r", encoding="utf-8") as f:
    html = f.read()

# Hero Section
html = html.replace(
    'style="padding: 85px 32px 65px; text-align: center; background: linear-gradient(rgba(15, 23, 42, 0.75), rgba(15, 23, 42, 0.9)), url(\'/static/img/library_bg.png\') no-repeat center center; background-size: cover; border-radius: 0 0 24px 24px; box-shadow: 0 4px 30px rgba(0, 0, 0, 0.25); border-bottom: 1px solid rgba(255, 215, 0, 0.15);"',
    'style="padding: 85px 32px 65px; text-align: center; background: var(--surface); border-radius: 0 0 24px 24px; border-bottom: 1px solid var(--border);"'
)
html = html.replace(
    'style="font-size: 2.5rem; font-weight: 800; color: white; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1.5px; line-height: 1.2;"',
    'style="font-family: \'Inter\', sans-serif; font-size: clamp(2rem, 5vw, 3.8rem); font-weight: 800; color: var(--text); margin-bottom: 16px; letter-spacing: -0.02em; line-height: 1.1;"'
)
html = html.replace(
    '<span style="color: var(--gold); text-shadow: 0 0 15px rgba(255,215,0,0.4);">',
    '<span style="color: var(--primary);">'
)
html = html.replace(
    'style="font-size: 1rem; color: #cbd5e1; max-width: 600px; margin: 0 auto 24px; line-height: 1.6;"',
    'style="font-size: 1.05rem; color: var(--muted); max-width: 600px; margin: 0 auto 24px;"'
)
html = html.replace(
    'style="max-width: 450px; margin: 0 auto; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); padding: 16px; border-radius: 12px; backdrop-filter: blur(10px); display: flex; gap: 8px; flex-wrap: wrap; justify-content: center;"',
    'style="max-width: 450px; margin: 0 auto; background: var(--surface2); border: 1px solid var(--border); padding: 16px; border-radius: 12px; display: flex; gap: 8px; flex-wrap: wrap; justify-content: center;"'
)
html = html.replace(
    'style="padding: 10px 20px; border-radius: 8px; border: none; background: var(--gold); color: #1c1d3f; font-weight: 700; cursor: pointer; transition: transform 0.2s, background 0.2s; font-size: 0.9rem;"',
    'style="padding: 10px 20px; border-radius: 8px; border: 1px solid var(--border); background: var(--surface); color: var(--text); font-weight: 700; cursor: pointer; transition: transform 0.2s, background 0.2s; font-size: 0.9rem;"'
)

# Panels
html = html.replace('var(--bg-card)', 'var(--surface)')
html = html.replace('border: 1px solid rgba(255,215,0,0.15)', 'border: 1px solid var(--border)')
html = html.replace('border: 1px solid rgba(255,215,0,0.18)', 'border: 1px solid var(--border)')
html = html.replace('box-shadow: 0 8px 32px rgba(0,0,0,0.15)', 'box-shadow: 0 4px 12px rgba(0,0,0,0.03)')
html = html.replace('box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3)', 'box-shadow: 0 4px 12px rgba(0,0,0,0.05)')

# Gradient Button
html = html.replace(
    'background: linear-gradient(90deg, #FFB800 0%, #FFA800 100%); color: #1c1d3f;',
    'background: var(--blue); color: #fff;'
)
html = html.replace(
    'background: var(--gold); color: #1c1d3f;',
    'background: var(--blue); color: #fff;'
)

# Modal overlay
html = html.replace(
    'background: rgba(15, 23, 42, 0.75);',
    'background: rgba(0, 0, 0, 0.4);'
)

# Text colors
html = html.replace('color: white;', 'color: var(--text);')

with open(seminar_path, "w", encoding="utf-8") as f:
    f.write(html)

print("Seminar UI Update Complete")
