"""
Management command: python manage.py sync_from_koha

Reads patron, circulation, and visit data directly from the Koha MySQL/MariaDB
database and syncs it into LibraryRank's PostgreSQL database.

Koha tables used (read-only):
  borrowers       → Member (patron name, cardnumber, category, branch)
  categories      → role mapping (student/lecturer/staff)
  issues          → active checkouts (BorrowRecord)
  old_issues      → returned checkouts (BorrowRecord)
  statistics      → visit/issue events (Visit) — as fallback
  biblio          → book title
  biblioitems     → book ISBN
  items           → book copy info
  branches        → library branches → faculty mapping

Koha Satellite tables used (read-only, host: 10.12.0.7):
  visitorhistory  → visit events from gate scanner (primary visit source)

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
            self.stdout.write(self.style.WARNING('[DRY RUN] nothing will be written\n'))

        self.stdout.write('Connecting to Koha MySQL/MariaDB...')

        try:
            koha = connections['koha']
            koha.ensure_connection()
            self.stdout.write(self.style.SUCCESS('Connected to Koha database'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Cannot connect to Koha: {e}'))
            self.stdout.write('   Check KOHA_DB_* settings in your .env file.')
            return

        # Try connecting to satellite database (visitorhistory) via pymysql directly
        # (kompatibel dengan MariaDB lama versi 10.1 yang ada di server satellite)
        self.satellite_conn = None
        try:
            import pymysql
            sat_db = settings.DATABASES.get('satellite', {})
            self.satellite_conn = pymysql.connect(
                host=sat_db.get('HOST', '10.12.0.7'),
                user=sat_db.get('USER', 'pilot_satellite'),
                password=sat_db.get('PASSWORD', ''),
                database=sat_db.get('NAME', 'koha_satellite'),
                port=int(sat_db.get('PORT', 3306)),
                charset='utf8mb4',
                connect_timeout=5,
            )
            self.stdout.write(self.style.SUCCESS('Connected to Koha Satellite database (visitorhistory)\n'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Cannot connect to Satellite DB: {e} — visit sync will use Koha statistics only\n'))

        self.koha = koha
        self.since = date.today() - timedelta(days=self.days) if not self.full else date(2000, 1, 1)

        # Run sync steps in order
        faculty_map  = self._sync_faculties()
        member_map   = self._sync_members(faculty_map)
        book_map     = self._sync_books(faculty_map)
        self._sync_visits(member_map)
        self._sync_borrows(member_map, book_map)

        self.stdout.write(self.style.SUCCESS('\nKoha sync complete!'))

    # ─────────────────────────────────────────────────────
    # STEP 1: Faculties from Koha branches
    # ─────────────────────────────────────────────────────
    def _sync_faculties(self):
        self.stdout.write('Syncing faculties from Koha branches...')
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
                action = 'Created' if created else 'Updated'
            else:
                self.stdout.write(f'   [dry] Would upsert Faculty: {faculty_name} ({code})')
                action = '   [dry]'
                faculty_map[code] = None

        self.stdout.write(f'   {len(branches)} branches -> faculties')
        return faculty_map

    # ─────────────────────────────────────────────────────
    # STEP 2: Members from Koha borrowers
    # ─────────────────────────────────────────────────────
    def _sync_members(self, faculty_map):
        self.stdout.write('Syncing members from Koha borrowers...')

        student_cats  = [c.upper() for c in settings.KOHA_STUDENT_CATEGORIES]
        lecturer_cats = [c.upper() for c in settings.KOHA_LECTURER_CATEGORIES]
        staff_cats    = [c.upper() for c in settings.KOHA_STAFF_CATEGORIES]

        # Incremental filter: when not full sync, only check patrons updated or enrolled since self.since
        where_sql = "WHERE (b.lost = 0 OR b.lost IS NULL)"
        params = []
        if not self.full:
            where_sql += " AND (b.updated_on >= %s OR b.dateenrolled >= %s)"
            params = [self.since, self.since]

        with self.koha.cursor() as cursor:
            cursor.execute(f"""
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
                {where_sql}
                ORDER BY b.borrowernumber
            """, params)
            rows = cursor.fetchall()

        existing_members = {m.member_id: m for m in Member.objects.all()}
        member_map = {}  # borrowernumber → Member instance
        to_create = []
        to_update_dict = {}  # pk → Member instance
        skipped_count = 0

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
                continue

            full_name = f"{(firstname or '').strip()} {(surname or '').strip()}".strip()
            if not full_name:
                full_name = cardnumber or f'Patron-{borrowernumber}'
            full_name = full_name[:150]

            faculty = faculty_map.get(branchcode)
            year_enrolled = None
            if dateenrolled and role == 'student':
                year_enrolled = dateenrolled.year if hasattr(dateenrolled, 'year') else None

            member_id = str(cardnumber or f'KOHA-{borrowernumber}')[:20]
            member_email = email.strip() if email and email.strip() else f"{member_id.lower()}@student.ums.ac.id"
            title_val = (category_desc or '')[:100]

            if member_id in existing_members:
                m = existing_members[member_id]
                changed = False
                if m.name != full_name: m.name = full_name; changed = True
                if m.role != role: m.role = role; changed = True
                if m.faculty_id != (faculty.id if faculty else None): m.faculty = faculty; changed = True
                if m.year_enrolled != year_enrolled: m.year_enrolled = year_enrolled; changed = True
                if m.title != title_val: m.title = title_val; changed = True
                if m.email != member_email and (email and email.strip()): m.email = member_email; changed = True
                if changed and m.pk is not None:
                    to_update_dict[m.pk] = m
                member_map[borrowernumber] = m
            else:
                new_m = Member(
                    member_id=member_id,
                    name=full_name,
                    role=role,
                    faculty=faculty,
                    year_enrolled=year_enrolled,
                    title=title_val,
                    email=member_email,
                    is_active=True,
                )
                to_create.append(new_m)
                existing_members[member_id] = new_m
                member_map[borrowernumber] = new_m

        if not self.dry_run:
            if to_create:
                Member.objects.bulk_create(to_create, batch_size=1000)
            if to_update_dict:
                Member.objects.bulk_update(
                    list(to_update_dict.values()),
                    ['name', 'role', 'faculty', 'year_enrolled', 'title', 'email'],
                    batch_size=1000
                )

        self.stdout.write(
            f'   Members: {len(to_create)} created, {len(to_update_dict)} updated, {skipped_count} skipped'
        )
        return member_map

    # ─────────────────────────────────────────────────────
    # STEP 3: Books from Koha biblio + biblioitems
    # ─────────────────────────────────────────────────────
    def _sync_books(self, faculty_map):
        self.stdout.write('Syncing books from Koha biblio...')

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
        existing_books = {b.isbn: b for b in Book.objects.all()}
        to_create = []
        to_update_dict = {}  # pk → Book instance

        for row in rows:
            biblionumber, title, author, isbn, itemtype, homebranch = row
            if not title:
                continue

            isbn_clean = (isbn or '').strip()[:20] or f'KOHA-BIB-{biblionumber}'
            faculty = faculty_map.get(homebranch)
            title_val = (title or '')[:300]
            author_val = (author or 'Unknown')[:200]
            category_val = (itemtype or 'General')[:100]

            if isbn_clean in existing_books:
                b_obj = existing_books[isbn_clean]
                changed = False
                if b_obj.title != title_val: b_obj.title = title_val; changed = True
                if b_obj.author != author_val: b_obj.author = author_val; changed = True
                if b_obj.category != category_val: b_obj.category = category_val; changed = True
                if b_obj.faculty_id != (faculty.id if faculty else None): b_obj.faculty = faculty; changed = True
                if changed and b_obj.pk is not None:
                    to_update_dict[b_obj.pk] = b_obj
                book_map[biblionumber] = b_obj
            else:
                new_b = Book(
                    isbn=isbn_clean,
                    title=title_val,
                    author=author_val,
                    category=category_val,
                    faculty=faculty,
                )
                to_create.append(new_b)
                existing_books[isbn_clean] = new_b
                book_map[biblionumber] = new_b

        if not self.dry_run:
            if to_create:
                Book.objects.bulk_create(to_create, batch_size=1000)
            if to_update_dict:
                Book.objects.bulk_update(list(to_update_dict.values()), ['title', 'author', 'category', 'faculty'], batch_size=1000)

        self.stdout.write(f'   Books: {len(to_create)} created, {len(to_update_dict)} updated')
        return book_map

    # ─────────────────────────────────────────────────────
    # STEP 4: Visits from Koha Satellite & Koha Statistics
    # ─────────────────────────────────────────────────────
    def _sync_visits(self, member_map):
        card_to_member = {str(m.member_id).strip().upper(): m for m in Member.objects.all()}
        existing_visits = set(Visit.objects.filter(visited_at__gte=self.since).values_list('member_id', 'visited_at__date'))
        from datetime import time as time_cls

        # ── PRIMARY: Satellite visitorhistory ──────────────────────────────
        sat_created = sat_skipped = 0
        to_create_sat = []

        if self.satellite_conn:
            self.stdout.write(f'Syncing visits from Satellite visitorhistory (since {self.since})...')
            with self.satellite_conn.cursor() as cursor:
                cursor.execute("""
                    SELECT cardnumber, visittime, location
                    FROM visitorhistory
                    WHERE visittime >= %s
                      AND cardnumber IS NOT NULL
                      AND cardnumber != ''
                    ORDER BY visittime
                """, [self.since])
                sat_rows = cursor.fetchall()

            for cardnumber, visittime, location in sat_rows:
                card_clean = str(cardnumber).strip().upper()
                member = card_to_member.get(card_clean)
                if not member:
                    sat_skipped += 1
                    continue

                visit_dt = visittime if timezone.is_aware(visittime) else timezone.make_aware(visittime)
                v_date = visit_dt.date()
                if (member.id, v_date) not in existing_visits:
                    visit_points = 5 if visit_dt.time() < time_cls(9, 0) else 2
                    to_create_sat.append(Visit(
                        member=member,
                        visited_at=visit_dt,
                        purpose=f'Gate scan: {location or "perpus"}',
                        earned_points=visit_points
                    ))
                    existing_visits.add((member.id, v_date))
                    sat_created += 1

            if not self.dry_run and to_create_sat:
                Visit.objects.bulk_create(to_create_sat, batch_size=1000)

            self.stdout.write(f'   Visits (gate scan): {sat_created} created, {sat_skipped} skipped (patron not in system)')
        else:
            self.stdout.write(self.style.WARNING('   Satellite DB tidak tersambung — melewati sinkronisasi visitorhistory.'))

        # ── SECONDARY: Koha statistics (issue/localuse/return) ────────────
        self.stdout.write(f'Syncing visits from Koha statistics (since {self.since})...')
        with self.koha.cursor() as cursor:
            cursor.execute("""
                SELECT s.borrowernumber, b.cardnumber, s.datetime, s.branch, s.type
                FROM statistics s
                LEFT JOIN borrowers b ON s.borrowernumber = b.borrowernumber
                WHERE s.borrowernumber IS NOT NULL
                  AND s.datetime >= %s
                  AND s.type IN ('issue', 'localuse', 'return')
                ORDER BY s.datetime
            """, [self.since])
            rows = cursor.fetchall()

        koha_created = koha_skipped = 0
        to_create_koha = []

        for borrowernumber, cardnumber, dt, branch, stat_type in rows:
            card_clean = str(cardnumber or '').strip().upper()
            member = card_to_member.get(card_clean) or member_map.get(borrowernumber)
            if not member:
                koha_skipped += 1
                continue

            visit_dt = dt if timezone.is_aware(dt) else timezone.make_aware(dt)
            v_date = visit_dt.date()
            if (member.id, v_date) not in existing_visits:
                visit_points = 5 if visit_dt.time() < time_cls(9, 0) else 2
                to_create_koha.append(Visit(
                    member=member,
                    visited_at=visit_dt,
                    purpose=f'Koha: {stat_type}',
                    earned_points=visit_points
                ))
                existing_visits.add((member.id, v_date))
                koha_created += 1

        if not self.dry_run and to_create_koha:
            Visit.objects.bulk_create(to_create_koha, batch_size=1000)

        self.stdout.write(f'   Visits (Koha stats): {koha_created} created, {koha_skipped} skipped (patron not in system)')

    # ─────────────────────────────────────────────────────
    # STEP 5: Borrow records from Koha issues + old_issues
    # ─────────────────────────────────────────────────────
    def _sync_borrows(self, member_map, book_map):
        self.stdout.write(f'Syncing borrow records from Koha issues (since {self.since})...')

        with self.koha.cursor() as cursor:
            cursor.execute("""
                SELECT
                    i.borrowernumber,
                    b.cardnumber,
                    i.itemnumber,
                    it.biblionumber,
                    i.issuedate,
                    i.date_due,
                    NULL AS returndate,
                    'borrowed' AS status
                FROM issues i
                JOIN items it ON i.itemnumber = it.itemnumber
                LEFT JOIN borrowers b ON i.borrowernumber = b.borrowernumber
                WHERE i.issuedate >= %s

                UNION ALL

                SELECT
                    oi.borrowernumber,
                    b.cardnumber,
                    oi.itemnumber,
                    it.biblionumber,
                    oi.issuedate,
                    oi.date_due,
                    oi.returndate,
                    'returned' AS status
                FROM old_issues oi
                JOIN items it ON oi.itemnumber = it.itemnumber
                LEFT JOIN borrowers b ON oi.borrowernumber = b.borrowernumber
                WHERE oi.issuedate >= %s

                ORDER BY issuedate
            """, [self.since, self.since])
            rows = cursor.fetchall()

        card_to_member = {str(m.member_id).strip().upper(): m for m in Member.objects.all()}
        existing_borrows = {
            (br.member_id, br.book_id, br.borrowed_at.date()): br
            for br in BorrowRecord.objects.filter(borrowed_at__gte=self.since)
        }

        created = updated = skipped = 0
        to_create_borrows = []
        to_update_borrows_dict = {}

        for row in rows:
            borrowernumber, cardnumber, itemnumber, biblionumber, issuedate, date_due, returndate, status = row

            card_clean = str(cardnumber or '').strip().upper()
            member = card_to_member.get(card_clean) or member_map.get(borrowernumber)
            book   = book_map.get(biblionumber) or Book.objects.filter(isbn=f'KOHA-BIB-{biblionumber}').first()

            if not member or not book:
                skipped += 1
                continue

            issue_dt   = issuedate if not issuedate or timezone.is_aware(issuedate) else timezone.make_aware(issuedate)
            return_dt  = returndate if not returndate or timezone.is_aware(returndate) else timezone.make_aware(returndate)
            due_date   = date_due.date() if isinstance(date_due, datetime) else date_due

            if status == 'borrowed' and due_date and due_date < date.today():
                status = 'overdue'

            points = 5
            if status == 'returned' and return_dt and issue_dt:
                duration_hours = (return_dt - issue_dt).total_seconds() / 3600
                if duration_hours >= 24:
                    points += 10
                    if due_date and return_dt.date() > due_date:
                        days_late = (return_dt.date() - due_date).days
                        points -= days_late * 5
            elif status == 'overdue' and due_date:
                days_late = (date.today() - due_date).days
                points -= days_late * 5

            if points < -50: points = -50

            borrow_key = (member.id, book.id, issue_dt.date() if issue_dt else date.today())
            if borrow_key in existing_borrows:
                br = existing_borrows[borrow_key]
                changed = False
                if br.status != status: br.status = status; changed = True
                if br.returned_at != return_dt: br.returned_at = return_dt; changed = True
                if br.earned_points != points: br.earned_points = points; changed = True
                if changed and br.pk is not None:
                    to_update_borrows_dict[br.pk] = br
                    updated += 1
            else:
                new_br = BorrowRecord(
                    member=member,
                    book=book,
                    borrowed_at=issue_dt or timezone.now(),
                    due_date=due_date or (date.today() + timedelta(days=14)),
                    returned_at=return_dt,
                    status=status,
                    earned_points=points
                )
                to_create_borrows.append(new_br)
                existing_borrows[borrow_key] = new_br
                created += 1

        if not self.dry_run:
            if to_create_borrows:
                BorrowRecord.objects.bulk_create(to_create_borrows, batch_size=1000)
            if to_update_borrows_dict:
                BorrowRecord.objects.bulk_update(list(to_update_borrows_dict.values()), ['status', 'returned_at', 'earned_points'], batch_size=1000)

        self.stdout.write(f'   Borrow records: {created} created, {updated} updated, {skipped} skipped')
