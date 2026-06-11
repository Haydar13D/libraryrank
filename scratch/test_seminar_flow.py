import os
import django
import sys
from datetime import timedelta

# Ensure project root is in PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libraryrank.settings')
django.setup()

from django.utils import timezone
from leaderboard.models import Member, Seminar, SeminarRegistration, PointTransaction
from django.db import transaction

print("=== MEMULAI TEST SEMINAR FLOW ===")

# 1. Get or create test member
member_id = "L200230051"
member = Member.objects.filter(member_id=member_id).first()
if not member:
    print(f"Membuat test member {member_id}...")
    member = Member.objects.create(
        member_id=member_id,
        name="HAYDAR AULIA RAHMAN",
        role="student",
        is_active=True
    )
else:
    print(f"Member ditemukan: {member.name}")

# 2. Create test Seminar
seminar_title = "Test Seminar Keamanan Siber 2026"
# Delete existing test seminar if any to avoid unique constraint on claim_code
Seminar.objects.filter(claim_code="TEST-SEM-SEC").delete()

now = timezone.now()
seminar = Seminar.objects.create(
    title=seminar_title,
    speaker="Prof. Dr. Ir. Budi Rahardjo",
    description="Seminar keamanan informasi berskala nasional.",
    date=now + timedelta(days=2),
    registration_open=now - timedelta(days=1),
    registration_close=now + timedelta(days=1),
    points_register=5,
    points_attend=25,
    claim_code="TEST-SEM-SEC",
    claim_code_active=False
)
print(f"Seminar berhasil dibuat: {seminar.title}")

# 3. Simulate Registration
print("\nMensimulasikan pendaftaran...")
# Check conditions (should be open)
is_open = seminar.registration_open <= now <= seminar.registration_close
print(f"Apakah pendaftaran dibuka? {is_open}")

if is_open:
    with transaction.atomic():
        reg = SeminarRegistration.objects.create(
            seminar=seminar,
            member_id=member_id,
            email="l200230051@student.ums.ac.id",
            status='registered'
        )
        pt = PointTransaction.objects.create(
            cardnumber=member_id,
            amount=seminar.points_register,
            transaction_type='seminar',
            description=f"Pendaftaran Seminar: {seminar.title}"
        )
    print(f"Pendaftaran sukses! Poin pendaftaran ditambahkan: +{seminar.points_register} XP")

# 4. Simulate Claim (before active - should fail)
print("\nMensimulasikan klaim sebelum kode diaktifkan...")
if not seminar.claim_code_active:
    print("LOG: Klaim ditolak karena kode belum diaktifkan oleh panitia. (BENAR)")

# 5. Activate code and claim
print("\nMensimulasikan klaim setelah kode diaktifkan...")
seminar.claim_code_active = True
seminar.save()

# Refresh from db
reg = SeminarRegistration.objects.get(id=reg.id)
if reg.status == 'registered' and seminar.claim_code_active and seminar.claim_code == "TEST-SEM-SEC":
    with transaction.atomic():
        reg.status = 'attended'
        reg.attended_at = timezone.now()
        reg.save()
        
        pt_attend = PointTransaction.objects.create(
            cardnumber=member_id,
            amount=seminar.points_attend,
            transaction_type='seminar',
            description=f"Kehadiran Seminar: {seminar.title}"
        )
    print(f"Klaim sukses! Poin kehadiran ditambahkan: +{seminar.points_attend} XP")

# Check totals
from leaderboard.views import get_member_total_points
total_p = get_member_total_points(member_id)
print(f"\nTotal poin berjalan mahasiswa {member_id}: {total_p} XP")

# Clean up test seminar
SeminarRegistration.objects.filter(seminar=seminar).delete()
PointTransaction.objects.filter(description__contains=seminar.title).delete()
seminar.delete()
print("\nData test dibersihkan. TEST BERHASIL!")
