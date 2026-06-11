import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libraryrank.settings')
django.setup()

from django.db import connections

try:
    with connections['koha'].cursor() as cursor:
        cursor.execute("SELECT cardnumber, firstname, surname, categorycode, email, lost FROM borrowers WHERE firstname LIKE %s OR surname LIKE %s OR cardnumber LIKE %s", ['%Haydar%', '%Haydar%', '%Haydar%'])
        rows = cursor.fetchall()
        print("=== HASIL PENCARIAN 'HAYDAR' ===")
        for r in rows:
            print(f"Card: {r[0]} | Name: {r[1]} {r[2]} | Cat: {r[3]} | Email: {r[4]} | Lost: {r[5]}")
except Exception as e:
    print("Error:", e)
