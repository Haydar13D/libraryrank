"""
Management command: python manage.py seed_demo_data
Populates the database with realistic demo data for development.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from leaderboard.models import Faculty, Member, Book, Visit, BorrowRecord


FACULTY_DATA = [
    ('Computer Science', 'CS', '#4da6ff'),
    ('Engineering', 'ENG', '#3de08a'),
    ('Medicine', 'MED', '#9b72ff'),
    ('Economics', 'ECO', '#ff6eb4'),
    ('Law', 'LAW', '#ff914d'),
    ('Psychology', 'PSY', '#f5c842'),
    ('Architecture', 'ARC', '#ff5c5c'),
    ('Biology', 'BIO', '#41e0d0'),
]

STUDENTS = [
    ('Ahmad Zulkifli', 'CS', 2021, 128, 24),
    ('Putri Maharani', 'MED', 2022, 115, 31),
    ('Rizky Pratama', 'ENG', 2020, 108, 19),
    ('Sari Dewi Kusuma', 'ECO', 2021, 97, 22),
    ('Fajar Hidayat', 'LAW', 2023, 89, 15),
    ('Nadia Anggraeni', 'PSY', 2022, 82, 28),
    ('Dimas Saputra', 'ARC', 2021, 75, 13),
    ('Lestari Wahyu', 'BIO', 2023, 68, 17),
    ('Bagus Santoso', 'CS', 2020, 61, 20),
    ('Yuni Astuti', 'ENG', 2022, 54, 11),
    ('Hendra Gunawan', 'MED', 2021, 48, 9),
    ('Mega Rahayu', 'ECO', 2023, 42, 14),
]

LECTURERS = [
    ('Dr. Siti Rahayu', 'ENG', 'Associate Prof.', 94, 18),
    ('Prof. Eko Budiman', 'MED', 'Professor', 87, 25),
    ('Dr. Anwar Hasan', 'LAW', 'Lecturer', 79, 12),
    ('Dr. Rina Sulistyo', 'ECO', 'Associate Prof.', 71, 20),
    ('Dr. Yudha Nugraha', 'CS', 'Lecturer', 65, 9),
    ('Prof. Dewi Santika', 'PSY', 'Professor', 58, 22),
    ('Dr. Hafiz Ramadhan', 'ARC', 'Lecturer', 50, 7),
]

STAFF = [
    ('Budi Hartono', 'Administration', 'Senior Staff', 76, 5),
    ('Wati Lestari', 'Cataloging', 'Librarian', 68, 8),
    ('Agus Priyono', 'IT Support', 'Staff', 59, 4),
    ('Erna Susanti', 'Reference', 'Senior Librarian', 51, 11),
    ('Joko Widodo', 'Circulation', 'Staff', 43, 3),
]

BOOKS = [
    ('978-0262033848', 'Introduction to Algorithms', 'Cormen et al.', 'Computer Science', 'CS', 47),
    ('978-1285165776', 'Principles of Economics', 'N. Gregory Mankiw', 'Economics', 'ECO', 39),
    ('978-0702077050', "Gray's Anatomy", 'Henry Gray', 'Medicine', 'MED', 35),
    ('978-0314271051', 'Blacks Law Dictionary', 'Henry Black', 'Law', 'LAW', 31),
    ('978-0134610672', 'Structural Analysis', 'R.C. Hibbeler', 'Engineering', 'ENG', 28),
    ('978-1319070670', 'Psychology', 'David Myers', 'Psychology', 'PSY', 24),
    ('978-1285741550', 'Calculus: Early Transcendentals', 'James Stewart', 'Mathematics', 'CS', 22),
    ('978-0134897714', 'Organic Chemistry', 'John McMurry', 'Chemistry', 'BIO', 19),
    ('978-0134190440', 'Computer Organization', 'Patterson & Hennessy', 'Computer Science', 'CS', 16),
    ('978-0321545619', 'The Pragmatic Programmer', 'Hunt & Thomas', 'Computer Science', 'CS', 14),
]


class Command(BaseCommand):
    help = 'Seed demo data for development'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding demo data...')

        # Faculties
        faculty_map = {}
        for name, code, color in FACULTY_DATA:
            f, _ = Faculty.objects.get_or_create(code=code, defaults={'name': name, 'color': color})
            faculty_map[code] = f
        self.stdout.write(f'  ✅ {len(FACULTY_DATA)} faculties created')

        # Books
        book_objs = []
        for isbn, title, author, cat, fac_code, _ in BOOKS:
            b, _ = Book.objects.get_or_create(isbn=isbn, defaults={
                'title': title, 'author': author, 'category': cat,
                'faculty': faculty_map.get(fac_code)
            })
            book_objs.append(b)
        self.stdout.write(f'  ✅ {len(BOOKS)} books created')

        now = timezone.now()
        today = now.date()

        # Students
        for i, (name, fac_code, year, visits, borrows) in enumerate(STUDENTS):
            m, _ = Member.objects.get_or_create(
                member_id=f'S{i+1:03d}',
                defaults={
                    'name': name, 'role': 'student',
                    'faculty': faculty_map.get(fac_code),
                    'year_enrolled': year,
                }
            )
            self._create_visits(m, visits, now)
            self._create_borrows(m, borrows, book_objs, now)

        self.stdout.write(f'  ✅ {len(STUDENTS)} students created')

        # Lecturers
        for i, (name, fac_code, title, visits, borrows) in enumerate(LECTURERS):
            m, _ = Member.objects.get_or_create(
                member_id=f'L{i+1:03d}',
                defaults={
                    'name': name, 'role': 'lecturer',
                    'faculty': faculty_map.get(fac_code),
                    'title': title,
                }
            )
            self._create_visits(m, visits, now)
            self._create_borrows(m, borrows, book_objs, now)

        self.stdout.write(f'  ✅ {len(LECTURERS)} lecturers created')

        # Staff
        for i, (name, dept, role, visits, borrows) in enumerate(STAFF):
            m, _ = Member.objects.get_or_create(
                member_id=f'ST{i+1:03d}',
                defaults={
                    'name': name, 'role': 'staff',
                    'department': dept, 'title': role,
                }
            )
            self._create_visits(m, visits, now)
            self._create_borrows(m, borrows, book_objs, now)

        self.stdout.write(f'  ✅ {len(STAFF)} staff created')
        self.stdout.write(self.style.SUCCESS('\n🎉 Demo data seeded successfully!'))
        self.stdout.write('  Run: python manage.py runserver')

    def _create_visits(self, member, count, now):
        """Create visit records spread over the last 30 days."""
        if member.visits.count() >= count:
            return
        existing = member.visits.count()
        to_create = count - existing
        visits = []
        for j in range(to_create):
            days_ago = random.randint(0, 29)
            hours_ago = random.randint(8, 18)
            dt = now - timedelta(days=days_ago, hours=hours_ago, minutes=random.randint(0, 59))
            visits.append(Visit(member=member, visited_at=dt))
        Visit.objects.bulk_create(visits)

    def _create_borrows(self, member, count, books, now):
        """Create borrow records spread over the last 30 days."""
        if member.borrow_records.count() >= count:
            return
        existing = member.borrow_records.count()
        to_create = count - existing
        for _ in range(to_create):
            book = random.choice(books)
            days_ago = random.randint(0, 25)
            dt = now - timedelta(days=days_ago)
            due = (dt + timedelta(days=14)).date()
            status = 'returned' if days_ago > 14 else 'borrowed'
            returned_at = dt + timedelta(days=random.randint(3, 13)) if status == 'returned' else None
            BorrowRecord.objects.create(
                member=member, book=book,
                borrowed_at=dt, due_date=due,
                status=status, returned_at=returned_at
            )
