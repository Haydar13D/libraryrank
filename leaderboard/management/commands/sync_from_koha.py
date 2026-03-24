"""
Management command: python manage.py sync_from_koha

Reads patron, circulation, and visit data directly from the Koha MySQL/MariaDB
database and syncs it into LibraryRank's PostgreSQL database.

Koha tables used (read-only):
  borrowers       → Member (patron name, cardnumber, category, branch)
  categories      → role mapping (student/lecturer/staff)
  issues          → active checkouts (BorrowRecord)
  old_issues      → returned checkouts (BorrowRecord)
  statistics      → visit/issue events (Visit)
  biblio          → book title
  biblioitems     → book ISBN
  items           → book copy info
  branches        → library branches → faculty mapping

Run this on a schedule (e.g. every night via cron):
  0 1 * * * /path/to/venv/bin/python manage.py sync_from_koha >> /var/log/libraryrank_sync.log 2>&1
"""

from django.core.management.base import BaseCommand
from django.db import connections, transaction
from django.conf import settings
from django.utils import timezone
from datetime import datetime, date, timedelta

from leaderboard.models import Member, Faculty, Book, Visit, BorrowRecord


class Command(BaseCommand):
    help = 'Sync patron, circulation, and visit data from Koha MySQL into LibraryRank PostgreSQL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days', type=int, default=30,
            help='How many days back to sync visits and borrows (default: 30)'
        )
        parser.add_argument(
            '--full', action='store_true',
            help='Full sync — re-sync all records, not just recent ones'
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Print what would be synced without writing to the database'
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.days = options['days']
        self.full = options['full']

        if self.dry_run:
            self.stdout.write(self.style.WARNING('⚠️  DRY RUN — nothing will be written\n'))

        self.stdout.write('🔗 Connecting to Koha MySQL/MariaDB...')

        try:
            koha = connections['koha']
            koha.ensure_connection()
            self.stdout.write(self.style.SUCCESS('✅ Connected to Koha database\n'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Cannot connect to Koha: {e}'))
            self.stdout.write('   Check KOHA_DB_* settings in your .env file.')
            return

        self.koha = koha
        self.since = date.today() - timedelta(days=self.days) if not self.full else date(2000, 1, 1)

        # Run sync steps in order
        faculty_map  = self._sync_faculties()
        member_map   = self._sync_members(faculty_map)
        book_map     = self._sync_books(faculty_map)
        self._sync_visits(member_map)
        self._sync_borrows(member_map, book_map)

        self.stdout.write(self.style.SUCCESS('\n🎉 Koha sync complete!'))

    # ─────────────────────────────────────────────────────
    # STEP 1: Faculties from Koha branches
    # ─────────────────────────────────────────────────────
    def _sync_faculties(self):
        self.stdout.write('📍 Syncing faculties from Koha branches...')
        branch_map = getattr(settings, 'KOHA_BRANCH_FACULTY_MAP', {})
        faculty_colors = [
            '#4da6ff','#3de08a','#9b72ff','#ff6eb4',
            '#ff914d','#f5c842','#ff5c5c','#41e0d0',
        ]

        with self.koha.cursor() as cursor:
            cursor.execute("SELECT branchcode, branchname FROM branches ORDER BY branchname")
            branches = cursor.fetchall()

        faculty_map = {}  # branchcode → Faculty instance
        for i, (code, name) in enumerate(branches):
            faculty_name = branch_map.get(code, name)
            color = faculty_colors[i % len(faculty_colors)]

            if not self.dry_run:
                faculty, created = Faculty.objects.update_or_create(
                    code=code,
                    defaults={'name': faculty_name, 'color': color}
                )
                faculty_map[code] = faculty
                action = '✨ Created' if created else '🔄 Updated'
            else:
                self.stdout.write(f'   [dry] Would upsert Faculty: {faculty_name} ({code})')
                action = '   [dry]'
                faculty_map[code] = None

        self.stdout.write(f'   ✅ {len(branches)} branches → faculties')
        return faculty_map

    # ─────────────────────────────────────────────────────
    # STEP 2: Members from Koha borrowers
    # ─────────────────────────────────────────────────────
    def _sync_members(self, faculty_map):
        self.stdout.write('👥 Syncing members from Koha borrowers...')

        student_cats  = [c.upper() for c in settings.KOHA_STUDENT_CATEGORIES]
        lecturer_cats = [c.upper() for c in settings.KOHA_LECTURER_CATEGORIES]
        staff_cats    = [c.upper() for c in settings.KOHA_STAFF_CATEGORIES]

        with self.koha.cursor() as cursor:
            cursor.execute("""
                SELECT
                    b.borrowernumber,
                    b.cardnumber,
                    b.surname,
                    b.firstname,
                    b.categorycode,
                    b.branchcode,
                    b.dateenrolled,
                    b.email,
                    c.description AS category_description
                FROM borrowers b
                LEFT JOIN categories c ON b.categorycode = c.categorycode
                WHERE b.lost = 0 OR b.lost IS NULL
                ORDER BY b.borrowernumber
            """)
            rows = cursor.fetchall()

        member_map = {}  # borrowernumber → Member instance
        created_count = updated_count = skipped_count = 0

        for row in rows:
            (borrowernumber, cardnumber, surname, firstname,
             categorycode, branchcode, dateenrolled, email,
             category_desc) = row

            cat_upper = (categorycode or '').upper()
            if cat_upper in student_cats:
                role = 'student'
            elif cat_upper in lecturer_cats:
                role = 'lecturer'
            elif cat_upper in staff_cats:
                role = 'staff'
            else:
                skipped_count += 1
                continue  # skip unknown categories

            full_name = f"{(firstname or '').strip()} {(surname or '').strip()}".strip()
            if not full_name:
                full_name = cardnumber or f'Patron-{borrowernumber}'

            faculty = faculty_map.get(branchcode)
            year_enrolled = None
            if dateenrolled and role == 'student':
                year_enrolled = dateenrolled.year if hasattr(dateenrolled, 'year') else None

            member_id = cardnumber or f'KOHA-{borrowernumber}'

            if not self.dry_run:
                member, created = Member.objects.update_or_create(
                    member_id=member_id,
                    defaults={
                        'name': full_name,
                        'role': role,
                        'faculty': faculty,
                        'year_enrolled': year_enrolled,
                        'title': category_desc or '',
                        'is_active': True,
                    }
                )
                member_map[borrowernumber] = member
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            else:
                self.stdout.write(f'   [dry] {role}: {full_name} ({member_id})')

        self.stdout.write(
            f'   ✅ Members: {created_count} created, {updated_count} updated, {skipped_count} skipped (unknown category)'
        )
        return member_map

    # ─────────────────────────────────────────────────────
    # STEP 3: Books from Koha biblio + biblioitems
    # ─────────────────────────────────────────────────────
    def _sync_books(self, faculty_map):
        self.stdout.write('📚 Syncing books from Koha biblio...')

        with self.koha.cursor() as cursor:
            cursor.execute("""
                SELECT
                    b.biblionumber,
                    b.title,
                    b.author,
                    bi.isbn,
                    bi.itemtype,
                    i.homebranch
                FROM biblio b
                LEFT JOIN biblioitems bi ON b.biblionumber = bi.biblionumber
                LEFT JOIN items i ON b.biblionumber = i.biblionumber
                GROUP BY b.biblionumber, b.title, b.author, bi.isbn, bi.itemtype, i.homebranch
                ORDER BY b.biblionumber
                LIMIT 5000
            """)
            rows = cursor.fetchall()

        book_map = {}  # biblionumber → Book instance
        created_count = updated_count = 0

        for row in rows:
            biblionumber, title, author, isbn, itemtype, homebranch = row
            if not title:
                continue

            isbn_clean = (isbn or '').strip()[:20] or f'KOHA-BIB-{biblionumber}'
            faculty = faculty_map.get(homebranch)

            if not self.dry_run:
                book, created = Book.objects.update_or_create(
                    isbn=isbn_clean,
                    defaults={
                        'title': (title or '')[:300],
                        'author': (author or 'Unknown')[:200],
                        'category': (itemtype or 'General')[:100],
                        'faculty': faculty,
                    }
                )
                book_map[biblionumber] = book
                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.stdout.write(f'   ✅ Books: {created_count} created, {updated_count} updated')
        return book_map

    # ─────────────────────────────────────────────────────
    # STEP 4: Visits from Koha statistics table
    # Koha logs every checkout, renewal, return in `statistics`.
    # We treat any 'issue' (checkout) event as a library visit.
    # ─────────────────────────────────────────────────────
    def _sync_visits(self, member_map):
        self.stdout.write(f'🚪 Syncing visits from Koha statistics (since {self.since})...')

        with self.koha.cursor() as cursor:
            cursor.execute("""
                SELECT
                    borrowernumber,
                    datetime,
                    branch,
                    type
                FROM statistics
                WHERE
                    borrowernumber IS NOT NULL
                    AND datetime >= %s
                    AND type IN ('issue', 'localuse', 'return')
                ORDER BY datetime
            """, [self.since])
            rows = cursor.fetchall()

        created = skipped = 0
        visits_to_create = []

        for borrowernumber, dt, branch, stat_type in rows:
            member = member_map.get(borrowernumber)
            if not member:
                skipped += 1
                continue

            if not self.dry_run:
                # Use get_or_create to avoid duplicate visits per member per hour
                visit_dt = dt if hasattr(dt, 'tzinfo') else timezone.make_aware(dt)
                # Round to hour to deduplicate same-session events
                visit_hour = visit_dt.replace(minute=0, second=0, microsecond=0)
                _, created_flag = Visit.objects.get_or_create(
                    member=member,
                    visited_at__date=visit_hour.date(),
                    defaults={'visited_at': visit_dt, 'purpose': f'Koha: {stat_type}'}
                )
                if created_flag:
                    created += 1

        self.stdout.write(f'   ✅ Visits: {created} created, {skipped} skipped (patron not in system)')

    # ─────────────────────────────────────────────────────
    # STEP 5: Borrow records from Koha issues + old_issues
    # ─────────────────────────────────────────────────────
    def _sync_borrows(self, member_map, book_map):
        self.stdout.write(f'📖 Syncing borrow records from Koha issues (since {self.since})...')

        # Active checkouts
        with self.koha.cursor() as cursor:
            cursor.execute("""
                SELECT
                    i.borrowernumber,
                    i.itemnumber,
                    it.biblionumber,
                    i.issuedate,
                    i.date_due,
                    NULL AS returndate,
                    'borrowed' AS status
                FROM issues i
                JOIN items it ON i.itemnumber = it.itemnumber
                WHERE i.issuedate >= %s

                UNION ALL

                SELECT
                    oi.borrowernumber,
                    oi.itemnumber,
                    it.biblionumber,
                    oi.issuedate,
                    oi.date_due,
                    oi.returndate,
                    'returned' AS status
                FROM old_issues oi
                JOIN items it ON oi.itemnumber = it.itemnumber
                WHERE oi.issuedate >= %s

                ORDER BY issuedate
            """, [self.since, self.since])
            rows = cursor.fetchall()

        created = skipped = 0

        for row in rows:
            borrowernumber, itemnumber, biblionumber, issuedate, date_due, returndate, status = row

            member = member_map.get(borrowernumber)
            book   = book_map.get(biblionumber)

            if not member or not book:
                skipped += 1
                continue

            if not self.dry_run:
                issue_dt   = timezone.make_aware(issuedate) if issuedate and not hasattr(issuedate, 'tzinfo') else issuedate
                return_dt  = timezone.make_aware(returndate) if returndate and not hasattr(returndate, 'tzinfo') else returndate
                due_date   = date_due if isinstance(date_due, date) else (date_due.date() if date_due else None)

                # Determine overdue status
                if status == 'borrowed' and due_date and due_date < date.today():
                    status = 'overdue'

                _, flag = BorrowRecord.objects.get_or_create(
                    member=member,
                    book=book,
                    borrowed_at__date=issue_dt.date() if issue_dt else date.today(),
                    defaults={
                        'borrowed_at': issue_dt or timezone.now(),
                        'due_date': due_date or (date.today() + timedelta(days=14)),
                        'returned_at': return_dt,
                        'status': status,
                    }
                )
                if flag:
                    created += 1

        self.stdout.write(f'   ✅ Borrow records: {created} created, {skipped} skipped')
