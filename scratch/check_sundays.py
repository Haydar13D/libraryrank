import os
import django
import sys

# Ensure project root is in PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ensure stdout uses UTF-8 to prevent encoding errors on Windows
sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libraryrank.settings')
django.setup()

from django.db import connections
import pymysql
from django.conf import settings

# 1. Koha database Sunday statistics
print("=== Kueri Basis Data Koha (statistics) ===")
try:
    with connections['koha'].cursor() as cursor:
        cursor.execute("""
            SELECT DAYOFWEEK(datetime) as dow, COUNT(*) 
            FROM statistics 
            WHERE datetime >= '2026-01-01' 
            GROUP BY dow
            ORDER BY dow
        """)
        rows = cursor.fetchall()
        days = {1: 'Minggu', 2: 'Senin', 3: 'Selasa', 4: 'Rabu', 5: 'Kamis', 6: 'Jumat', 7: 'Sabtu'}
        for dow, cnt in rows:
            print(f"  {days.get(dow, dow)} (Day {dow}): {cnt} record")
            
        print("\nDetail data hari Minggu di Koha statistics:")
        cursor.execute("""
            SELECT datetime, type, borrowernumber, itemnumber 
            FROM statistics 
            WHERE datetime >= '2026-01-01' AND DAYOFWEEK(datetime) = 1
            LIMIT 20
        """)
        for dt, type_, bnum, itnum in cursor.fetchall():
            print(f"  Datetime: {dt}, Type: {type_}, Borrower: {bnum}, Item: {itnum}")
except Exception as e:
    print("Error querying Koha database:", e)

# 2. Satellite database Sunday statistics
print("\n=== Kueri Basis Data Satellite (visitorhistory) ===")
db = settings.DATABASES.get('satellite', {})
try:
    conn = pymysql.connect(
        host=db.get('HOST', '10.12.0.7'),
        user=db.get('USER', 'pilot_satellite'),
        password=db.get('PASSWORD', ''),
        database=db.get('NAME', 'koha_satellite'),
        port=int(db.get('PORT', 3306)),
        charset='utf8mb4'
    )
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT DAYOFWEEK(visittime) as dow, COUNT(*) 
            FROM visitorhistory 
            WHERE visittime >= '2026-01-01' 
            GROUP BY dow
            ORDER BY dow
        """)
        rows = cursor.fetchall()
        days = {1: 'Minggu', 2: 'Senin', 3: 'Selasa', 4: 'Rabu', 5: 'Kamis', 6: 'Jumat', 7: 'Sabtu'}
        for dow, cnt in rows:
            print(f"  {days.get(dow, dow)} (Day {dow}): {cnt} record")
    conn.close()
except Exception as e:
    print("Error querying Satellite database:", e)
