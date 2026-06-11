"""
╔══════════════════════════════════════════════════════════════════╗
║         CLEAR DUMMY DATA — SETELAH PRESENTASI                   ║
║                                                                  ║
║  Hapus semua dummy data yang di-seed oleh                       ║
║  seed_dummy_presentasi.py                                        ║
║                                                                  ║
║  CARA PAKAI:                                                     ║
║    python manage.py shell < clear_dummy_presentasi.py           ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libraryrank.settings')
django.setup()

from leaderboard.models import (
    Member, Faculty, Visit, BorrowRecord, Book, Reward, PointTransaction
)

# ISBN dummy semua dimulai dengan '978-DM-'
DUMMY_ISBNS = [f'978-DM-{str(i).zfill(3)}' for i in range(1, 20)]

# Member IDs dummy: mahasiswa (L202201...), NIP dosen (NIP...), staf (STF...)
# Semua anggota dengan member_id yang dibuat oleh seed script
DUMMY_MEMBER_PREFIXES = ('L2022', 'L2021', 'L2020', 'L2023', 'NIP', 'STF')

print("🗑️  Menghapus dummy data presentasi...")

# 1. Hapus borrow records dari member dummy
dummy_members = Member.objects.filter(member_id__startswith='NIP') | \
                Member.objects.filter(member_id__startswith='STF') | \
                Member.objects.filter(member_id__regex=r'^L20[0-9]{2}')

borrow_del, _ = BorrowRecord.objects.filter(member__in=dummy_members).delete()
print(f"   ✅ Hapus {borrow_del} borrow records")

# 2. Hapus visits dari member dummy
visit_del, _ = Visit.objects.filter(member__in=dummy_members).delete()
print(f"   ✅ Hapus {visit_del} visits")

# 3. Hapus buku dummy
book_del, _ = Book.objects.filter(isbn__startswith='978-DM-').delete()
print(f"   ✅ Hapus {book_del} buku")

# 4. Hapus member dummy
member_ids = list(dummy_members.values_list('id', flat=True))
member_del, _ = dummy_members.delete()
print(f"   ✅ Hapus {member_del} members")

# 5. Hapus fakultas dummy (yang tidak punya member lagi)
fac_codes = ['FT', 'FILKOM', 'FK', 'FEB', 'FH', 'FPSI', 'FP', 'FISIP']
fac_del, _ = Faculty.objects.filter(code__in=fac_codes, members__isnull=True).delete()
print(f"   ✅ Hapus {fac_del} fakultas kosong")

# 6. Hapus point transactions seminar dummy
pt_del, _ = PointTransaction.objects.filter(
    description__icontains='Seminar Nasional Literasi Digital 2025'
).delete()
pt_del2, _ = PointTransaction.objects.filter(
    description__icontains='Workshop Penulisan Karya Ilmiah'
).delete()
pt_del3, _ = PointTransaction.objects.filter(
    description__icontains='Webinar Open Access Jurnal Internasional'
).delete()
print(f"   ✅ Hapus {pt_del + pt_del2 + pt_del3} point transactions")

# 7. Hapus rewards dummy (opsional — komen kalau mau keep)
reward_names = ['Voucher Kantin Rp 15.000', 'Akses E-Journal Premium',
                'Bebas Denda 1x', 'Stiker Perpustakaan Edisi Limited', 'Pin Library Champion']
reward_del, _ = Reward.objects.filter(name__in=reward_names).delete()
print(f"   ✅ Hapus {reward_del} rewards")

print()
print("=" * 60)
print("✅  Semua dummy data presentasi berhasil dihapus!")
print("    Database bersih dan siap menerima data real dari Koha.")
print("=" * 60)
