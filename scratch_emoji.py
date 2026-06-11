import os
import re

mapping = {
    '🏆': '<span class="material-icons-outlined">emoji_events</span>',
    '🎓': '<span class="material-icons-outlined">school</span>',
    '👨‍🏫': '<span class="material-icons-outlined">person</span>',
    '👔': '<span class="material-icons-outlined">work</span>',
    '📖': '<span class="material-icons-outlined">menu_book</span>',
    '🏛️': '<span class="material-icons-outlined">account_balance</span>',
    '🔍': '<span class="material-icons-outlined">search</span>',
    '📊': '<span class="material-icons-outlined">analytics</span>',
    '📄': '<span class="material-icons-outlined">description</span>',
    '🚀': '<span class="material-icons-outlined">rocket_launch</span>',
    '🚶': '<span class="material-icons-outlined">directions_walk</span>',
    '📚': '<span class="material-icons-outlined">library_books</span>',
    '🎟️': '<span class="material-icons-outlined">local_activity</span>',
    '🎁': '<span class="material-icons-outlined">redeem</span>',
    '🏅': '<span class="material-icons-outlined">workspace_premium</span>',
}

# For JS file, use same replacement
js_mapping = {
    "'📭'": "'<span class=\"material-icons-outlined\">inbox</span>'",
    "'🥇'": "'<span class=\"material-icons-outlined\">workspace_premium</span>'",
    "'🥈'": "'<span class=\"material-icons-outlined\">workspace_premium</span>'",
    "'🥉'": "'<span class=\"material-icons-outlined\">workspace_premium</span>'",
    "'🔥'": "'<span class=\"material-icons-outlined\">local_fire_department</span>'",
    "'✅'": "'<span class=\"material-icons-outlined\">check_circle</span>'",
    "'❌'": "'<span class=\"material-icons-outlined\">cancel</span>'",
    "'📸'": "'<span class=\"material-icons-outlined\">photo_camera</span>'",
    "'💻'": "'<span class=\"material-icons-outlined\">computer</span>'",
    "'📈'": "'<span class=\"material-icons-outlined\">trending_up</span>'",
    "'🫀'": "'<span class=\"material-icons-outlined\">favorite</span>'",
    "'⚖️'": "'<span class=\"material-icons-outlined\">gavel</span>'",
    "'🏗️'": "'<span class=\"material-icons-outlined\">architecture</span>'",
    "'🧠'": "'<span class=\"material-icons-outlined\">psychology</span>'",
    "'📐'": "'<span class=\"material-icons-outlined\">straighten</span>'",
    "'🧪'": "'<span class=\"material-icons-outlined\">science</span>'",
    "'📚'": "'<span class=\"material-icons-outlined\">library_books</span>'",
    "'🏛️'": "'<span class=\"material-icons-outlined\">account_balance</span>'",
    "'📢'": "'<span class=\"material-icons-outlined\">campaign</span>'",
    "'🐦'": "'<span class=\"material-icons-outlined\">chat</span>'",
    "'📘'": "'<span class=\"material-icons-outlined\">facebook</span>'",
    "'💬'": "'<span class=\"material-icons-outlined\">forum</span>'"
}

def replace_in_file(path, reps):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    for k, v in reps.items():
        content = content.replace(k, v)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

replace_in_file('leaderboard/templates/leaderboard/index.html', mapping)
replace_in_file('static/js/main.js', js_mapping)
print("Emojis replaced successfully.")
