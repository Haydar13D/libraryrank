import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libraryrank.settings')
django.setup()

from django.db import connections
from leaderboard.models import Member

def remove_alumni():
    print("Mencari data alumni (kode XALMN) di Koha...")
    with connections['koha'].cursor() as cursor:
        cursor.execute("SELECT cardnumber, borrowernumber FROM borrowers WHERE categorycode LIKE 'XA%'")
        rows = cursor.fetchall()
        
    alumni_ids = []
    for row in rows:
        cardnumber, borrowernumber = row
        member_id = str(cardnumber or f'KOHA-{borrowernumber}')[:20]
        alumni_ids.append(member_id)
        
    print(f"Ditemukan {len(alumni_ids)} alumni di Koha.")
    
    # Menghapus dari database lokal in chunks
    chunk_size = 500
    total_deleted = 0
    for i in range(0, len(alumni_ids), chunk_size):
        chunk = alumni_ids[i:i+chunk_size]
        members_to_delete = Member.objects.filter(member_id__in=chunk)
        count = members_to_delete.count()
        if count > 0:
            members_to_delete.delete()
            total_deleted += count
    
    print(f"Berhasil MENGHAPUS {total_deleted} alumni dari sistem LibraryRank lokal.")

if __name__ == "__main__":
    remove_alumni()
