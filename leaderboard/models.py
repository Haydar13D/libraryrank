from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from datetime import timedelta


class LevelTier(models.Model):
    name = models.CharField(max_length=50)
    level_num = models.IntegerField(unique=True)
    min_xp = models.IntegerField()
    max_xp = models.IntegerField(null=True, blank=True)
    color = models.CharField(max_length=7, default='#95a5a6')

    class Meta:
        ordering = ['min_xp']

    def __str__(self):
        return f"Level {self.level_num}: {self.name}"


class BadgeRule(models.Model):
    CRITERIA_CHOICES = [
        ('visits_week', 'Visits in last 7 days'),
        ('visits_month_top10', 'Top 10 Visits this month'),
        ('borrows_semester', 'Borrows in last 6 months'),
        ('custom', 'Custom / Manual'),
    ]
    id_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=10)
    image_url = models.CharField(max_length=200)
    color = models.CharField(max_length=7)
    desc = models.CharField(max_length=200)
    criteria_type = models.CharField(max_length=50, choices=CRITERIA_CHOICES)
    min_value = models.IntegerField(default=0)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class PointPolicy(models.Model):
    action_type = models.CharField(max_length=50, unique=True, help_text="Contoh: visit, borrow, return_on_time, review_book")
    points = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Point Policies'

    def __str__(self):
        return f"{self.action_type.capitalize()} = {self.points} XP"


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
    email = models.EmailField(max_length=254, null=True, blank=True)

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
        for rule in BadgeRule.objects.all():
            earned = False
            if rule.criteria_type == 'visits_week':
                week_ago = now - timedelta(days=7)
                if self.visits.filter(visited_at__gte=week_ago).count() >= rule.min_value:
                    earned = True
            elif rule.criteria_type == 'borrows_semester':
                semester_ago = now - timedelta(days=180)
                if self.borrow_records.filter(borrowed_at__gte=semester_ago).count() >= rule.min_value:
                    earned = True
            elif rule.criteria_type == 'visits_month_top10':
                start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                my_month_visits = self.visits.filter(visited_at__gte=start_of_month).count()
                if my_month_visits > 0:
                    from django.db.models import Count, Q
                    top_10 = Member.objects.annotate(
                        m_visits=Count('visits', filter=Q(visits__visited_at__gte=start_of_month))
                    ).filter(m_visits__gt=0).order_by('-m_visits')[:max(1, rule.min_value)]
                    if self in top_10:
                        earned = True
            
            if earned:
                result.append({
                    'id': rule.id_code,
                    'name': rule.name,
                    'icon': rule.icon,
                    'image_url': rule.image_url,
                    'color': rule.color,
                    'desc': rule.desc
                })
        return result

    @property
    def total_points_all_time(self):
        v = self.visits.aggregate(total=models.Sum('earned_points'))['total'] or 0
        b = self.borrow_records.aggregate(total=models.Sum('earned_points'))['total'] or 0
        return v + b

    @property
    def level_info(self):
        xp = self.total_points_all_time
        tiers = list(LevelTier.objects.all().order_by('min_xp'))
        if not tiers:
            return {'name': 'Visitor', 'level_num': 1, 'current_xp': xp, 'min_xp': 0, 'max_xp': 100, 'progress_perc': 0, 'color': '#95a5a6'}
            
        for tier in tiers:
            if tier.max_xp is None or xp <= tier.max_xp:
                progress = 100
                if tier.max_xp is not None:
                    denom = max(1, tier.max_xp - tier.min_xp)
                    progress = int(((xp - tier.min_xp) / denom) * 100)
                return {
                    'name': tier.name,
                    'level_num': tier.level_num,
                    'current_xp': xp,
                    'min_xp': tier.min_xp,
                    'max_xp': tier.max_xp if tier.max_xp is not None else xp,
                    'progress_perc': min(100, progress),
                    'color': tier.color
                }
        highest = tiers[-1]
        return {
            'name': highest.name, 'level_num': highest.level_num, 'current_xp': xp, 
            'min_xp': highest.min_xp, 'max_xp': xp, 'progress_perc': 100, 'color': highest.color
        }


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
    earned_points = models.IntegerField(default=0)

    class Meta:
        ordering = ['-visited_at']

    def __str__(self):
        return f"{self.member.name} — {self.visited_at.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        if not self.pk and self.earned_points == 0:
            policy = PointPolicy.objects.filter(action_type='visit', is_active=True).first()
            if policy:
                self.earned_points = policy.points
        super().save(*args, **kwargs)


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
    earned_points = models.IntegerField(default=0)

    class Meta:
        ordering = ['-borrowed_at']

    def __str__(self):
        return f"{self.member.name} ← {self.book.title}"

    def save(self, *args, **kwargs):
        if not self.pk and self.earned_points == 0:
            policy = PointPolicy.objects.filter(action_type='borrow', is_active=True).first()
            if policy:
                self.earned_points = policy.points
        if not self.due_date:
            self.due_date = (timezone.now() + timezone.timedelta(days=14)).date()
        if self.returned_at and self.status == 'borrowed':
            self.status = 'returned'
        super().save(*args, **kwargs)

class SystemLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=100)
    duration_ms = models.FloatField(default=0)
    details = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'System Log'
        verbose_name_plural = 'System Logs'
        
    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {self.action} ({self.duration_ms}ms)"

class Reward(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    points_cost = models.IntegerField(default=100)
    stock = models.IntegerField(default=10)
    image_url = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['points_cost']
        
    def __str__(self):
        return f"{self.name} ({self.points_cost} XP)"

class PointTransaction(models.Model):
    TYPE_CHOICES = [
        ('event', 'Event Participation'),
        ('seminar', 'Seminar Attendance'),
        ('redeem', 'Redeem Reward'),
        ('manual', 'Manual Adjustment'),
    ]
    cardnumber = models.CharField(max_length=50, db_index=True)
    amount = models.IntegerField(help_text="Format: + for event, - for redemption")
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='manual')
    description = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.cardnumber} | {self.amount} ({self.transaction_type})"


import csv
import io
class SeminarUpload(models.Model):
    title = models.CharField(max_length=200, help_text="Nama atau Judul Seminar")
    csv_file = models.FileField(upload_to='seminars/', help_text="Upload file CSV berisi satu kolom NIM/Cardnumber", blank=True, null=True)
    manual_input = models.TextField(blank=True, help_text="Atau input NIM/Cardnumber mahasiswa di sini (satu NIM per baris)")
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Input Data Seminar'
        verbose_name_plural = 'Input Data Seminar'

    def __str__(self):
        return f"{self.title} ({self.created_at.strftime('%Y-%m-%d')})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if not self.processed and (self.csv_file or self.manual_input):
            try:
                # Get points from policy
                policy = PointPolicy.objects.filter(action_type='seminar', is_active=True).first()
                points = policy.points if policy else 15
                
                cardnumbers = []
                
                # 1. Process CSV file if uploaded
                if self.csv_file:
                    try:
                        self.csv_file.open('r')
                        file_content = self.csv_file.read()
                        
                        # Handle bytes or string
                        if isinstance(file_content, bytes):
                            file_content = file_content.decode('utf-8-sig')
                            
                        csv_reader = csv.reader(io.StringIO(file_content))
                        for row in csv_reader:
                            if row and row[0].strip():
                                cardnumber = row[0].strip()
                                if cardnumber.lower() not in ['nim', 'cardnumber', 'id']:
                                    cardnumbers.append(cardnumber.upper())
                    finally:
                        self.csv_file.close()
                        
                # 2. Process manual textbox input if provided
                if self.manual_input:
                    for line in self.manual_input.splitlines():
                        for part in line.replace(',', ' ').split():
                            cnum = part.strip()
                            if cnum and cnum.lower() not in ['nim', 'cardnumber', 'id']:
                                cardnumbers.append(cnum.upper())
                                
                # Remove duplicates preserving order
                unique_cardnumbers = list(dict.fromkeys(cardnumbers))
                
                if unique_cardnumbers:
                    transactions = []
                    for cardnumber in unique_cardnumbers:
                        transactions.append(PointTransaction(
                            cardnumber=cardnumber,
                            amount=points,
                            transaction_type='seminar',
                            description=f"Peserta: {self.title}"
                        ))
                    PointTransaction.objects.bulk_create(transactions)
                
                self.processed = True
                super().save(update_fields=['processed'])
                
                # Clear leaderboard cache automatically
                from django.core.cache import cache
                cache.clear()
            except Exception as e:
                # Log error or print
                print(f"Error processing Seminar Input: {e}")


class RedemptionClaim(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending / Belum Diambil'),
        ('claimed', 'Claimed / Sudah Diambil'),
    ]
    code = models.CharField(max_length=50, unique=True, db_index=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='redemptions')
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE, related_name='redemptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    claimed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} — {self.member.name} ({self.status})"


class Seminar(models.Model):
    title = models.CharField(max_length=200, help_text="Judul Seminar")
    speaker = models.CharField(max_length=100, help_text="Pembicara/Narasumber")
    description = models.TextField(blank=True, null=True, help_text="Deskripsi Singkat Seminar")
    date = models.DateTimeField(help_text="Tanggal & Waktu Seminar")
    registration_open = models.DateTimeField(help_text="Tanggal Dibuka Pendaftaran")
    registration_close = models.DateTimeField(help_text="Tanggal Ditutup Pendaftaran")
    points_register = models.IntegerField(default=2, help_text="Poin untuk mendaftar")
    points_attend = models.IntegerField(default=15, help_text="Poin untuk kehadiran")
    claim_code = models.CharField(max_length=50, unique=True, help_text="Kode Unik Klaim Kehadiran (misal: UMS-SEM-XYZ)")
    claim_code_active = models.BooleanField(default=False, help_text="Apakah klaim kehadiran sedang aktif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} ({self.date.strftime('%d %b %Y')})"


class SeminarRegistration(models.Model):
    STATUS_CHOICES = [
        ('registered', 'Terdaftar'),
        ('attended', 'Hadir / Diklaim'),
    ]
    seminar = models.ForeignKey(Seminar, on_delete=models.CASCADE, related_name='registrations')
    member_id = models.CharField(max_length=50, db_index=True, help_text="NIM / Cardnumber")
    email = models.EmailField(max_length=254, help_text="Email Mahasiswa saat mendaftar")
    registered_at = models.DateTimeField(auto_now_add=True)
    attended_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')

    class Meta:
        ordering = ['-registered_at']
        unique_together = ('seminar', 'member_id')

    def __str__(self):
        return f"{self.member_id} - {self.seminar.title} ({self.status})"


