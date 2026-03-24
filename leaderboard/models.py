from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Faculty(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    color = models.CharField(max_length=7, default='#4da6ff')  # hex color

    class Meta:
        verbose_name_plural = 'Faculties'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_visitors(self):
        return Visit.objects.filter(member__faculty=self).count()

    @property
    def total_books_borrowed(self):
        return BorrowRecord.objects.filter(member__faculty=self).count()


class Member(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('lecturer', 'Lecturer'),
        ('staff', 'Staff'),
    ]

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='member')
    member_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')

    # Student specific
    year_enrolled = models.IntegerField(null=True, blank=True)

    # Lecturer/Staff specific
    title = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)

    photo = models.ImageField(upload_to='members/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.member_id} — {self.name}"

    @property
    def initials(self):
        parts = self.name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return self.name[:2].upper()

    @property
    def visit_count(self):
        return self.visits.count()

    @property
    def borrow_count(self):
        return self.borrow_records.count()

    @property
    def streak_days(self):
        """Calculate consecutive visit days up to today."""
        visits = self.visits.order_by('-visited_at').values_list('visited_at__date', flat=True)
        unique_days = sorted(set(visits), reverse=True)
        if not unique_days:
            return 0
        streak = 0
        today = timezone.now().date()
        for i, day in enumerate(unique_days):
            expected = today - timezone.timedelta(days=i)
            if day == expected:
                streak += 1
            else:
                break
        return streak

    def visit_count_in_range(self, date_from, date_to):
        return self.visits.filter(visited_at__gte=date_from, visited_at__lt=date_to + timedelta(days=1)).count()

    def borrow_count_in_range(self, date_from, date_to):
        return self.borrow_records.filter(borrowed_at__gte=date_from, borrowed_at__lt=date_to + timedelta(days=1)).count()

    @property
    def badges(self):
        """Dynamic badge calculation based on visits and borrows."""
        result = []
        now = timezone.now()

        # 1. Weekly Warrior 🥈 (3 visits in the last 7 days)
        week_ago = now - timedelta(days=7)
        if self.visits.filter(visited_at__gte=week_ago).count() >= 3:
            result.append({
                'id': 'weekly_warrior',
                'name': 'Weekly Warrior',
                'icon': '🥈',
                'image_url': '/static/img/badges/weekly warior.png', # Gunakan garis miring (/) dan tambah / di awal
                'color': '#bdc3c7', # silver
                'desc': 'Datang ke perpus 3x dalam seminggu'
            })

        # 2. Library Legend 🥇 (Top 10 visitors this month)
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        my_month_visits = self.visits.filter(visited_at__gte=start_of_month).count()
        if my_month_visits > 0:
            from django.db.models import Count, Q
            # Get the 10th highest visit count this month
            top_10 = Member.objects.annotate(
                m_visits=Count('visits', filter=Q(visits__visited_at__gte=start_of_month))
            ).filter(m_visits__gt=0).order_by('-m_visits')[:10]
            
            if self in top_10:
                result.append({
                    'id': 'library_legend',
                    'name': 'Library Legend',
                    'icon': '🥇',
                    'image_url': '/static/img/badges/top 10 leaderboard.png', # Gunakan garis miring (/) dan tambah / di awal
                    'color': '#f1c40f', # gold
                    'desc': 'Top 10 Leaderboard bulan ini'
                })

        # 3. Book Worm 📚 (> 5 books borrowed in the last 6 months / 1 semester)
        semester_ago = now - timedelta(days=180)
        if self.borrow_records.filter(borrowed_at__gte=semester_ago).count() > 5:
            result.append({
                'id': 'book_worm',
                'name': 'Book Worm',
                'icon': '📚',
                'image_url': '/static/img/badges/bookworm.png', # Gunakan garis miring (/) dan tambah / di awal
                'color': '#9b59b6', # purple
                'desc': 'Meminjam > 5 buku dalam 1 semester'
            })

        return result


class Book(models.Model):
    isbn = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True, related_name='books')
    stock = models.IntegerField(default=1)
    cover = models.ImageField(upload_to='books/', null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    @property
    def borrow_count(self):
        return self.borrow_records.count()


class Visit(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='visits')
    visited_at = models.DateTimeField(default=timezone.now)
    purpose = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-visited_at']

    def __str__(self):
        return f"{self.member.name} — {self.visited_at.strftime('%Y-%m-%d %H:%M')}"


class BorrowRecord(models.Model):
    STATUS_CHOICES = [
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='borrow_records')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records')
    borrowed_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateField()
    returned_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='borrowed')

    class Meta:
        ordering = ['-borrowed_at']

    def __str__(self):
        return f"{self.member.name} ← {self.book.title}"

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = (timezone.now() + timezone.timedelta(days=14)).date()
        if self.returned_at and self.status == 'borrowed':
            self.status = 'returned'
        super().save(*args, **kwargs)
