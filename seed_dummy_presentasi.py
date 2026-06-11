"""
SEED DUMMY DATA - UNTUK PRESENTASI SEMENTARA

Script ini HANYA mengisi data ke database lokal Django.
Tidak mengubah kode apapun. Aman untuk dibersihkan setelah.

CARA PAKAI:
  python seed_dummy_presentasi.py

CARA CLEAR SETELAH PRESENTASI:
  python clear_dummy_presentasi.py
"""

import os
import sys
import django

# Fix Windows terminal encoding for special characters
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
from datetime import date, timedelta, datetime
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libraryrank.settings')
django.setup()

from django.contrib.auth.models import User
from leaderboard.models import (
    Member, Faculty, Visit, BorrowRecord, Book,
    PointPolicy, LevelTier, BadgeRule, Reward, PointTransaction
)
from django.utils import timezone

# ────────────────────────────────────────────────────────────
# CONFIG
# ────────────────────────────────────────────────────────────
DUMMY_TAG = "DUMMY_PRESENTASI"  # tag di field title buku agar mudah dihapus
TODAY = date.today()

# ────────────────────────────────────────────────────────────
# 1. GAMIFICATION MASTER DATA (levels, badges, policies)
# ────────────────────────────────────────────────────────────
print("[*] Seeding gamification master data...")

# Point Policies
PointPolicy.objects.get_or_create(action_type='visit',   defaults={'points': 10})
PointPolicy.objects.get_or_create(action_type='borrow',  defaults={'points': 25})
PointPolicy.objects.get_or_create(action_type='seminar', defaults={'points': 15})

# Level Tiers
levels = [
    (0,    100,  'Pengunjung',   1, '#95a5a6'),
    (101,  300,  'Pembaca',      2, '#3498db'),
    (301,  700,  'Pelajar',      3, '#2ecc71'),
    (701,  1500, 'Peneliti',     4, '#9b59b6'),
    (1501, 3000, 'Cendekia',     5, '#e67e22'),
    (3001, None, 'Legenda Perpus', 6, '#f1c40f'),
]
for min_xp, max_xp, name, lv_num, color in levels:
    LevelTier.objects.get_or_create(level_num=lv_num, defaults={
        'name': name, 'min_xp': min_xp, 'max_xp': max_xp, 'color': color
    })

# Badge Rules
BadgeRule.objects.get_or_create(id_code='weekly_warrior', defaults={
    'name': 'Weekly Warrior', 'icon': '🥈',
    'image_url': '/static/img/badges/weekly warior.png', 'color': '#bdc3c7',
    'desc': 'Datang ke perpus 3x dalam seminggu', 'criteria_type': 'visits_week', 'min_value': 3
})
BadgeRule.objects.get_or_create(id_code='library_legend', defaults={
    'name': 'Library Legend', 'icon': '🥇',
    'image_url': '/static/img/badges/top 10 leaderboard.png', 'color': '#f1c40f',
    'desc': 'Top 10 Leaderboard bulan ini', 'criteria_type': 'visits_month_top10', 'min_value': 10
})
BadgeRule.objects.get_or_create(id_code='book_worm', defaults={
    'name': 'Book Worm', 'icon': '📚',
    'image_url': '/static/img/badges/bookworm.png', 'color': '#9b59b6',
    'desc': 'Meminjam > 5 buku dalam 1 semester', 'criteria_type': 'borrows_semester', 'min_value': 6
})

# Rewards
rewards_data = [
    ('Voucher Kantin Rp 15.000',   'Tukar poin untuk voucher makan siang di kantin kampus.', 150,  20, '🍱'),
    ('Akses E-Journal Premium',    'Akses 1 bulan e-journal internasional gratis.',           300,  15, '📰'),
    ('Bebas Denda 1x',             'Bebas denda keterlambatan satu kali peminjaman.',          200,  30, '✅'),
    ('Stiker Perpustakaan Edisi Limited', 'Stiker eksklusif edisi terbatas koleksi perpus.',   80,  50, '🎨'),
    ('Pin Library Champion',       'Pin eksklusif Library Champion untuk jaket/tas.',          500,  10, '🏅'),
]
for name, desc, cost, stock, icon in rewards_data:
    Reward.objects.get_or_create(name=name, defaults={
        'description': desc, 'points_cost': cost, 'stock': stock,
        'image_url': '', 'is_active': True
    })

print("    [OK] Gamification master data selesai.\n")

# ────────────────────────────────────────────────────────────
# 2. FAKULTAS
# ────────────────────────────────────────────────────────────
print("[*] Seeding Fakultas...")

faculties_data = [
    ('Teknik',                   'FT',   '#3de08a'),
    ('Ilmu Komputer',            'FILKOM','#4da6ff'),
    ('Kedokteran',               'FK',   '#9b72ff'),
    ('Ekonomi dan Bisnis',       'FEB',  '#ff6eb4'),
    ('Hukum',                    'FH',   '#ff914d'),
    ('Psikologi',                'FPSI', '#f5c842'),
    ('Pertanian',                'FP',   '#41e0d0'),
    ('Ilmu Sosial dan Ilmu Politik', 'FISIP', '#ff5c5c'),
]
fac_objs = {}
for name, code, color in faculties_data:
    obj, _ = Faculty.objects.get_or_create(code=code, defaults={'name': name, 'color': color})
    fac_objs[code] = obj

print(f"    [OK] {len(fac_objs)} fakultas berhasil dibuat.\n")

# ────────────────────────────────────────────────────────────
# 3. MEMBER DATA
# ────────────────────────────────────────────────────────────
print("[*] Seeding Members...")

# Format NIM: L + tahun + jurusan 2 digit + nomor urut 4 digit
def make_nim(year, fac_code, num):
    fac_num = {
        'FT': '01', 'FILKOM': '02', 'FK': '03', 'FEB': '04',
        'FH': '05', 'FPSI': '06', 'FP': '07', 'FISIP': '08'
    }.get(fac_code, '99')
    return f"L{year}{fac_num}{num:04d}"

students_raw = [
    # (nama, fac_code, angkatan, visit_bulan_ini, borrow_semester, visit_minggu_ini)
    ('Ahmad Fauzi Ramadhan',    'FILKOM', 2022, 28, 12, 6),
    ('Siti Nurhaliza Putri',    'FK',     2021, 25, 18, 5),
    ('Rizky Maulana Akbar',     'FT',     2022, 23, 9,  5),
    ('Dewi Ayu Lestari',        'FEB',    2023, 21, 14, 4),
    ('Muhammad Hafiz Ibrahim',  'FH',     2021, 20, 7,  4),
    ('Anisa Rahma Fitriani',    'FPSI',   2022, 18, 11, 4),
    ('Dimas Arya Kusuma',       'FT',     2020, 17, 8,  3),
    ('Fajar Nurfadillah',       'FILKOM', 2023, 16, 6,  3),
    ('Laila Nur Aini',          'FK',     2022, 15, 15, 3),
    ('Bagas Prasetyo Utomo',    'FEB',    2021, 14, 10, 3),
    ('Cindy Permata Sari',      'FPSI',   2023, 13, 8,  2),
    ('Evan Drajat Wicaksana',   'FH',     2020, 12, 5,  2),
    ('Galih Setiawan Nugroho',  'FP',     2022, 11, 7,  2),
    ('Hana Safitri Rahayu',     'FISIP',  2021, 10, 9,  2),
    ('Irfan Mauludi Santoso',   'FILKOM', 2020, 9,  4,  2),
    ('Joko Prasetyo Budi',      'FT',     2023, 8,  3,  1),
    ('Karina Astuti Wulandari', 'FK',     2021, 8,  13, 1),
    ('Luqman Hakim Salim',      'FEB',    2022, 7,  6,  1),
    ('Maya Indah Permatasari',  'FP',     2023, 7,  5,  1),
    ('Naufal Ardiansyah Putra', 'FISIP',  2022, 6,  4,  1),
]

lecturers_raw = [
    # (nama, fac_code, title, visit_bulan_ini, borrow_semester)
    ('Dr. Siti Rahayu, M.T.',         'FT',     'Associate Professor', 22, 10),
    ('Prof. Eko Supriyanto, Ph.D.',   'FK',     'Guru Besar',          19, 14),
    ('Dr. Anwar Fauzi, S.H., M.H.',   'FH',     'Dosen',               17, 8),
    ('Dr. Rina Sulistyowati, M.Sc.',  'FEB',    'Associate Professor', 15, 11),
    ('Dr. Yudha Pratama, M.Kom.',     'FILKOM', 'Dosen',               14, 5),
    ('Prof. Dewi Wulandari, Ph.D.',   'FPSI',   'Guru Besar',          12, 16),
    ('Dr. Hafiz Nugraha, M.T.',       'FT',     'Dosen',               10, 6),
]

staff_raw = [
    # (nama, dept, title, visit_bulan_ini, borrow_semester)
    ('Budi Santoso',       'Administrasi Umum',    'Staf Senior',        18, 3),
    ('Wati Rahayu',        'Pengolahan',            'Pustakawan',         16, 5),
    ('Agus Wibowo',        'IT & Sistem',           'Staf IT',            14, 2),
    ('Erna Damayanti',     'Referensi',             'Pustakawan Senior',  12, 7),
    ('Joko Wahono',        'Sirkulasi',             'Staf Pelayanan',     10, 2),
]

created_members = []

# Create students
for i, (nama, fac_code, angkatan, v_this_month, b_semester, v_this_week) in enumerate(students_raw, start=1):
    nim = make_nim(angkatan, fac_code, i)
    member, created = Member.objects.get_or_create(
        member_id=nim,
        defaults={
            'name': nama,
            'role': 'student',
            'faculty': fac_objs.get(fac_code),
            'year_enrolled': angkatan,
            'is_active': True,
        }
    )
    created_members.append((member, v_this_month, b_semester, v_this_week, 'student'))

# Create lecturers
for i, (nama, fac_code, title, v_this_month, b_semester) in enumerate(lecturers_raw, start=1):
    nip = f"NIP{2000 + i:04d}{i:04d}"
    member, created = Member.objects.get_or_create(
        member_id=nip,
        defaults={
            'name': nama,
            'role': 'lecturer',
            'faculty': fac_objs.get(fac_code),
            'title': title,
            'is_active': True,
        }
    )
    created_members.append((member, v_this_month, b_semester, 0, 'lecturer'))

# Create staff
for i, (nama, dept, title, v_this_month, b_semester) in enumerate(staff_raw, start=1):
    nip = f"STF{2010 + i:04d}{i:04d}"
    member, created = Member.objects.get_or_create(
        member_id=nip,
        defaults={
            'name': nama,
            'role': 'staff',
            'department': dept,
            'title': title,
            'is_active': True,
        }
    )
    created_members.append((member, v_this_month, b_semester, 0, 'staff'))

print(f"    [OK] {len(created_members)} member berhasil dibuat.\n")

# ────────────────────────────────────────────────────────────
# 4. BUKU
# ────────────────────────────────────────────────────────────
print("[*] Seeding Koleksi Buku...")

books_raw = [
    # (isbn_dummy, judul, penulis, kategori, fac_code, stok)
    ('978-DM-001', 'Pemrograman Web Modern dengan Django',       'Arief Budiman, S.Kom.',     'Informatika',      'FILKOM', 5),
    ('978-DM-002', 'Algoritma dan Struktur Data',                'Dr. Hendra Wijaya',          'Informatika',      'FILKOM', 4),
    ('978-DM-003', 'Machine Learning: Teori dan Implementasi',   'Prof. Budi Santosa',         'Kecerdasan Buatan','FILKOM', 3),
    ('978-DM-004', 'Ilmu Bedah Dasar Edisi 5',                   'Mansjoer et al.',            'Kedokteran',       'FK',     4),
    ('978-DM-005', 'Farmakologi Klinik Terapan',                 'Dr. Suryani Lukman',         'Farmasi',          'FK',     3),
    ('978-DM-006', 'Manajemen Keuangan Perusahaan',              'Dr. Agus Salim, M.M.',       'Manajemen',        'FEB',    5),
    ('978-DM-007', 'Pengantar Ilmu Ekonomi Makro',               'Prof. Sadono Sukirno',       'Ekonomi',          'FEB',    6),
    ('978-DM-008', 'Hukum Perdata Indonesia',                    'Prof. R. Subekti, S.H.',     'Hukum',            'FH',     4),
    ('978-DM-009', 'Mekanika Tanah dan Fondasi',                 'Dr. Braja M. Das (Alih Bahasa)', 'Teknik Sipil', 'FT',     3),
    ('978-DM-010', 'Termodinamika Teknik',                       'Cengel & Boles (Alih Bahasa)', 'Teknik Mesin',   'FT',     3),
    ('978-DM-011', 'Psikologi Sosial Terapan',                   'Dr. Sarlito Wirawan',        'Psikologi',        'FPSI',   4),
    ('978-DM-012', 'Penelitian Ilmu Sosial: Metodologi',         'Prof. Burhan Bungin',        'Metodologi',       'FISIP',  5),
    ('978-DM-013', 'Agronomi Tanaman Pangan',                    'Dr. Andi Bahrun, M.Sc.',     'Pertanian',        'FP',     3),
    ('978-DM-014', 'Basis Data: Konsep dan Implementasi',        'Edhy Sutanta, S.T.',         'Informatika',      'FILKOM', 4),
    ('978-DM-015', 'Statistika untuk Penelitian',                'Prof. Sugiyono',             'Statistika',       'FEB',    6),
]

book_objs = []
for isbn, title, author, cat, fac_code, stock in books_raw:
    book, _ = Book.objects.get_or_create(
        isbn=isbn,
        defaults={
            'title': title,
            'author': author,
            'category': cat,
            'faculty': fac_objs.get(fac_code),
            'stock': stock,
        }
    )
    book_objs.append(book)

print(f"    [OK] {len(book_objs)} buku berhasil dibuat.\n")

# ────────────────────────────────────────────────────────────
# 5. KUNJUNGAN & PEMINJAMAN
# ────────────────────────────────────────────────────────────
print("[*] Seeding Kunjungan & Peminjaman...")

purposes = [
    'Belajar mandiri', 'Mengerjakan tugas', 'Mencari referensi',
    'Diskusi kelompok', 'Membaca jurnal', 'Akses internet',
    'Membaca buku', 'Penelitian skripsi',
]

visit_count = 0
borrow_count = 0

random.seed(42)

for member, v_month, b_semester, v_week, role in created_members:
    # Skip kalau sudah ada visits untuk member ini (hindari duplikat)
    if member.visits.exists():
        continue

    # ── KUNJUNGAN (bulan ini) ────────────────────────────────
    # Sebar v_month kunjungan dalam 30 hari terakhir
    visit_dates = sorted(random.sample(range(1, 31), min(v_month, 30)), reverse=True)
    for days_ago in visit_dates:
        dt = timezone.now() - timedelta(days=days_ago)
        # Tambah variasi jam (08:00–16:00)
        dt = dt.replace(hour=random.randint(8, 16), minute=random.randint(0, 59), second=0, microsecond=0)
        Visit.objects.create(
            member=member,
            visited_at=dt,
            purpose=random.choice(purposes),
        )
        visit_count += 1

    # Tambah kunjungan minggu ini sesuai v_week
    for days_ago in range(min(v_week, 7)):
        dt = timezone.now() - timedelta(days=days_ago)
        dt = dt.replace(hour=random.randint(8, 16), minute=random.randint(0, 59), second=0, microsecond=0)
        Visit.objects.create(
            member=member,
            visited_at=dt,
            purpose=random.choice(purposes),
        )
        visit_count += 1

    # ── PEMINJAMAN (semester ini / 6 bulan) ─────────────────
    if member.borrow_records.exists():
        continue

    b_semester = min(b_semester, len(book_objs))
    chosen_books = random.sample(book_objs, b_semester)
    for idx, book in enumerate(chosen_books):
        days_ago = random.randint(1, 170)
        borrow_dt = timezone.now() - timedelta(days=days_ago)
        due_date = (borrow_dt + timedelta(days=14)).date()

        # 70% sudah dikembalikan, 30% masih dipinjam
        if random.random() < 0.7:
            returned_at = borrow_dt + timedelta(days=random.randint(1, 13))
            status = 'returned'
        else:
            returned_at = None
            status = 'borrowed' if due_date >= TODAY else 'overdue'

        BorrowRecord.objects.create(
            member=member,
            book=book,
            borrowed_at=borrow_dt,
            due_date=due_date,
            returned_at=returned_at,
            status=status,
        )
        borrow_count += 1

print(f"    [OK] {visit_count} kunjungan + {borrow_count} peminjaman berhasil dibuat.\n")

# ────────────────────────────────────────────────────────────
# 6. POINT TRANSACTIONS SEMINAR (opsional)
# ────────────────────────────────────────────────────────────
print("[*] Seeding Seminar Point Transactions...")

seminar_participants = [
    (created_members[0][0].member_id, "Seminar Nasional Literasi Digital 2025"),
    (created_members[1][0].member_id, "Seminar Nasional Literasi Digital 2025"),
    (created_members[2][0].member_id, "Seminar Nasional Literasi Digital 2025"),
    (created_members[3][0].member_id, "Workshop Penulisan Karya Ilmiah"),
    (created_members[4][0].member_id, "Workshop Penulisan Karya Ilmiah"),
    (created_members[5][0].member_id, "Webinar Open Access Jurnal Internasional"),
]
for cardnumber, title in seminar_participants:
    PointTransaction.objects.get_or_create(
        cardnumber=cardnumber,
        description=f"Peserta: {title}",
        defaults={'amount': 15, 'transaction_type': 'seminar'}
    )

print("    [OK] Seminar transactions selesai.\n")

# ────────────────────────────────────────────────────────────
# SUMMARY
# ────────────────────────────────────────────────────────────
print("=" * 60)
print("DUMMY DATA PRESENTASI BERHASIL DI-SEED!")
print("=" * 60)
print(f"  Members   : {Member.objects.count()} total")
print(f"  Visits    : {Visit.objects.count()} total")
print(f"  Borrows   : {BorrowRecord.objects.count()} total")
print(f"  Books     : {Book.objects.count()} total")
print(f"  Faculties : {Faculty.objects.count()} total")
print(f"  Rewards   : {Reward.objects.count()} total")
print()
print("Untuk HAPUS semua dummy data setelah presentasi:")
print("  python clear_dummy_presentasi.py")
print("=" * 60)
