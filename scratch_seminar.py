import os
import django
from django.core.files.uploadedfile import SimpleUploadedFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libraryrank.settings')
django.setup()

from leaderboard.models import PointPolicy, SeminarUpload, PointTransaction
from django.test import Client

# 1. Create Point Policy for seminar
policy, created = PointPolicy.objects.get_or_create(action_type='seminar', defaults={'points': 20})
if not created:
    policy.points = 20
    policy.is_active = True
    policy.save()

# 2. Create test CSV
csv_content = b"NIM\nSTD1\nSTD2\nTC1\nSTAF1\nSTAF2\n"
csv_file = SimpleUploadedFile("seminar_test.csv", csv_content, content_type="text/csv")

# 3. Create SeminarUpload
upload = SeminarUpload.objects.create(
    title="Seminar Literasi Digital 2026",
    csv_file=csv_file
)

# 4. Verify Point Transactions
transactions = PointTransaction.objects.filter(transaction_type='seminar')
print("Seminar transactions count:", transactions.count())

# 5. Test API
c = Client(HTTP_HOST='localhost')
r = c.get('/api/pemustaka-teraktif/?role=student')
data = r.json()
print("Top Seminar Students:", len(data.get('top_seminar', [])))
if data.get('top_seminar'):
    print("First top seminar student:", data['top_seminar'][0]['name'], "- seminars:", data['top_seminar'][0]['visits'])

r = c.get('/api/pemustaka-teraktif/?role=staff')
data = r.json()
print("Top Seminar Staff:", len(data.get('top_seminar', [])))
if data.get('top_seminar'):
    print("First top seminar staff:", data['top_seminar'][0]['name'], "- seminars:", data['top_seminar'][0]['visits'])
