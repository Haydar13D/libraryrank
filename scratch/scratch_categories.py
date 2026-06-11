import os
import sys
import django

# Add root folder to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libraryrank.settings')
django.setup()

from django.db import connections

try:
    with connections['koha'].cursor() as cursor:
        cursor.execute("SELECT categorycode, COUNT(*) as count FROM borrowers GROUP BY categorycode ORDER BY count DESC")
        rows = cursor.fetchall()
        print("=== KATEGORI ANGGOTA DI KOHA ===")
        for row in rows:
            print(f"Category: {row[0]} | Jumlah: {row[1]}")
except Exception as e:
    print("Error:", e)
