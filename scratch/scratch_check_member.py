import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libraryrank.settings')
django.setup()

from leaderboard.models import Member

member = Member.objects.filter(member_id='L200230051').first()
if member:
    print(f"FOUND LOCAL: {member.member_id} | Name: {member.name} | Role: {member.role} | Active: {member.is_active} | Email: {member.email}")
else:
    print("NOT FOUND LOCAL L200230051")

# Also print total student count
print("Total local students in DB:", Member.objects.filter(role='student').count())
