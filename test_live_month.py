import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libraryrank.settings')
django.setup()

from leaderboard.views import _use_demo
from datetime import date
from leaderboard.koha_utils import get_live_members

print("Is Demo Mode Triggered?:", _use_demo())

try:
    today = date.today()
    first = today.replace(day=1)
    print("Testing query for:", first, "to", today)
    members = get_live_members(first, today)
    print("Total members found this month:", len(members))
    if members:
        print("Top 1:", members[0])
except Exception as e:
    import traceback
    traceback.print_exc()
