import os
import django
import sys
from datetime import datetime
from django.utils import timezone

# Ensure project root is in PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libraryrank.settings')
django.setup()

from leaderboard.models import Seminar

print("=== SEEDING DEMO SEMINARS ===")

# Delete any existing test/demo seminars to avoid duplicate codes
Seminar.objects.filter(claim_code__in=["SEMINAR-SCOPUS", "SEMINAR-AI-ETHICS"]).delete()

# Seminar 1: Registration Open
s1 = Seminar.objects.create(
    title="Strategi Efektif Menulis Jurnal Bereputasi Internasional Scopus",
    speaker="Prof. Dr. Anton Setiawan, M.Sc.",
    description="Pelajari tips dan trik mematangkan manuskrip ilmiah, metodologi riset yang disukai reviewer, dan cara membalas komentar reviewer dengan persuasif.",
    date=timezone.make_aware(datetime(2026, 6, 15, 9, 0)),
    registration_open=timezone.make_aware(datetime(2026, 6, 10, 8, 0)), # already open
    registration_close=timezone.make_aware(datetime(2026, 6, 15, 8, 30)),
    points_register=2,
    points_attend=15,
    claim_code="SEMINAR-SCOPUS",
    claim_code_active=False
)
print(f"Created Seminar 1: {s1.title}")

# Seminar 2: Registration Upcoming (H-3 starts on June 17, so currently closed)
s2 = Seminar.objects.create(
    title="Literasi Digital & Etika Pemanfaatan AI Generatif dalam Riset Akademik",
    speaker="Dr. Rina Wulandari, M.T.",
    description="Panduan etis penggunaan AI generatif seperti ChatGPT, Gemini, dan Claude untuk sintesis pustaka, pencarian referensi, serta mitigasi plagiasi AI.",
    date=timezone.make_aware(datetime(2026, 6, 20, 10, 0)),
    registration_open=timezone.make_aware(datetime(2026, 6, 17, 8, 0)), # opens in future
    registration_close=timezone.make_aware(datetime(2026, 6, 20, 9, 30)),
    points_register=2,
    points_attend=15,
    claim_code="SEMINAR-AI-ETHICS",
    claim_code_active=False
)
print(f"Created Seminar 2: {s2.title}")

print("\nSeeding selesai! Silakan buka halaman /seminar/ untuk melihat seminar baru.")
