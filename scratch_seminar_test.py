import os
import django
import sys
sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libraryrank.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from leaderboard.models import SeminarUpload, PointTransaction, PointPolicy

# Pastikan ada PointPolicy untuk seminar
policy, created = PointPolicy.objects.get_or_create(
    action_type='seminar',
    defaults={'points': 20, 'description': 'Poin kehadiran seminar', 'is_active': True}
)
print(f"PointPolicy seminar: {policy.points} poin (created={created})")

# Hapus data seminar lama jika ada (untuk testing bersih)
old = PointTransaction.objects.filter(transaction_type='seminar').count()
if old > 0:
    print(f"Menghapus {old} transaksi seminar lama...")
    PointTransaction.objects.filter(transaction_type='seminar').delete()

# Baca file CSV
with open('seminar_dummy.csv', 'rb') as f:
    csv_content = f.read()

csv_file = SimpleUploadedFile("seminar_literasi_digital.csv", csv_content, content_type="text/csv")

# Buat SeminarUpload (ini akan otomatis proses CSV-nya)
upload = SeminarUpload.objects.create(
    title="Seminar Literasi Digital & Kecerdasan Buatan 2026",
    csv_file=csv_file
)

print(f"\nHasil Upload:")
print(f"  ID: {upload.id}")
print(f"  Judul: {upload.title}")
print(f"  Processed: {upload.processed}")

# Verifikasi transaksi
transactions = PointTransaction.objects.filter(transaction_type='seminar')
print(f"\nTotal transaksi seminar berhasil: {transactions.count()}")
for t in transactions:
    print(f"  NIM: {t.cardnumber} -> +{t.amount} poin | {t.description}")
