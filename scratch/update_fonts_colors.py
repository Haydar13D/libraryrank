import os

base_dir = r"d:\Code\libraryrank"
css_path = os.path.join(base_dir, "static", "css", "main.css")

with open(css_path, "r", encoding="utf-8") as f:
    css = f.read()

# Replace all alternative fonts with Inter
css = css.replace("font-family: 'Poppins', sans-serif;", "font-family: 'Inter', sans-serif;")
css = css.replace("font-family: 'Montserrat', sans-serif;", "font-family: 'Inter', sans-serif;")
css = css.replace("font-family: 'Poppins', sans-serif", "font-family: 'Inter', sans-serif")
css = css.replace("font-family: 'Montserrat', sans-serif", "font-family: 'Inter', sans-serif")

# Adjust colors to be more modern and cohesive
css = css.replace("--gold: #FFB800;", "--gold: #F59E0B;")
css = css.replace("--silver: #94A3B8;", "--silver: #94A3B8;")
css = css.replace("--bronze: #CD7C4A;", "--bronze: #B45309;")
css = css.replace("--green: #1CBDB3;", "--green: #10B981;")
css = css.replace("--orange: #FFB800;", "--orange: #F59E0B;")
css = css.replace("--pink: #EC4899;", "--pink: #F43F5E;")
css = css.replace("--purple: #8B5CF6;", "--purple: #6366F1;")

# Fix any hardcoded hex values that should match
css = css.replace("#FFB800", "#F59E0B")
css = css.replace("#CD7C4A", "#B45309")
css = css.replace("#1CBDB3", "#10B981")

with open(css_path, "w", encoding="utf-8") as f:
    f.write(css)

# Also check base.html to update ?v=10 to ?v=11 to bust cache
base_path = os.path.join(base_dir, "leaderboard", "templates", "leaderboard", "base.html")
with open(base_path, "r", encoding="utf-8") as f:
    base_html = f.read()
    
base_html = base_html.replace("?v=10", "?v=11")

with open(base_path, "w", encoding="utf-8") as f:
    f.write(base_html)

print("Font and Colors updated")
