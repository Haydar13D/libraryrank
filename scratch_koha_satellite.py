import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libraryrank.settings')
django.setup()

import pymysql

try:
    conn = pymysql.connect(
        host='10.12.0.7',
        user='pilot_satellite',
        password='B1sm1r0bb1k4123',
        database='koha_satellite',
        port=3306
    )
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM visitorhistory WHERE cardnumber = 'L200230051' AND visittime >= '2026-04-01' AND visittime < '2026-05-01'")
        cnt = cursor.fetchone()[0]
        print(f"Visits in April 2026 for L200230051: {cnt}")
        
        cursor.execute("DESCRIBE visitorhistory")
        print("\nColumns in visitorhistory:")
        for r in cursor.fetchall():
            print("  ", r)
except Exception as e:
    print('Connection ERROR:', e)
