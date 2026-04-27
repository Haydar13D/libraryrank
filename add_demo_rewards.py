import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libraryrank.settings')
django.setup()

from leaderboard.models import Reward

count = Reward.objects.count()
if count == 0:
    print("Creating demo rewards...")
    Reward.objects.create(name="Kaos LibraryRank", description="Merchandise Eksklusif", points_cost=500, stock=5)
    Reward.objects.create(name="Mug Unik", description="Teman Minum Kopi", points_cost=150, stock=10)
    Reward.objects.create(name="Voucher Kantin", description="Makan Siang Gratis", points_cost=100, stock=20)
    print("Created 3 demo rewards.")
else:
    print(f"There are {count} rewards already.")
