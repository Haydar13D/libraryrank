import os
import django
import sys

sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libraryrank.settings')
django.setup()

from django.db import connections

with connections['koha'].cursor() as cursor:
    cursor.execute("""
        SELECT cardnumber, CONCAT(IFNULL(firstname,''), ' ', IFNULL(surname,'')) as name
        FROM borrowers
        WHERE categorycode IN ('STD1', 'STD2')
          AND cardnumber IS NOT NULL
          AND cardnumber != ''
        ORDER BY RAND()
        LIMIT 20
    """)
    rows = cursor.fetchall()

print("NIM (cardnumber) mahasiswa:")
for card, name in rows:
    print(f"  {card}  -> {name.strip()}")
