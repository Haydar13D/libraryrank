from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Member, Faculty, Book, LevelTier, BadgeRule, PointPolicy, SystemLog, Reward, PointTransaction, RedemptionClaim, Seminar, SeminarRegistration

# Visit and BorrowRecord models are no longer managed by Django ORM!
# The entire architecture has shifted to Live Koha Read-Only via koha_utils.py
# Therefore, registering them will show zero local data and cause confusion.

@admin.register(LevelTier)
class LevelTierAdmin(ModelAdmin):
    list_display = ['name', 'level_num', 'min_xp', 'max_xp', 'color']
    ordering = ['min_xp']

@admin.register(BadgeRule)
class BadgeRuleAdmin(ModelAdmin):
    list_display = ['id_code', 'name', 'criteria_type', 'min_value', 'icon']

@admin.register(PointPolicy)
class PointPolicyAdmin(ModelAdmin):
    list_display = ['action_type', 'points', 'is_active']
    list_editable = ['points', 'is_active']

@admin.register(Reward)
class RewardAdmin(ModelAdmin):
    list_display = ['name', 'points_cost', 'stock', 'is_active']
    list_editable = ['stock', 'is_active', 'points_cost']
    search_fields = ['name']

@admin.register(PointTransaction)
class PointTransactionAdmin(ModelAdmin):
    list_display = ['cardnumber', 'amount', 'transaction_type', 'description', 'created_at']
    list_filter = ['transaction_type']
    search_fields = ['cardnumber', 'description']

from .models import SeminarUpload
from django.db import models
from django.forms import Textarea
@admin.register(SeminarUpload)
class SeminarUploadAdmin(ModelAdmin):
    list_display = ['title', 'input_method', 'processed', 'created_at']
    list_filter = ['processed']
    search_fields = ['title']
    readonly_fields = ['processed']

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={
            'placeholder': 'Contoh cara input data:\nL200230051\nL200230052\nL200230053\n\n* Ketik satu NIM per baris.\n* Tekan tombol ENTER untuk NIM selanjutnya.\n* NIM bisa menggunakan huruf besar atau kecil.',
            'rows': 10
        })},
    }

    def input_method(self, obj):
        parts = []
        if obj.csv_file: parts.append("CSV File")
        if obj.manual_input: parts.append("Manual Textbox")
        return " + ".join(parts) if parts else "-"
    input_method.short_description = "Input Method"


@admin.register(SystemLog)
class SystemLogAdmin(ModelAdmin):
    list_display = ['timestamp', 'action', 'duration_ms', 'details']
    list_filter = ['action']
    search_fields = ['details']
    # Make it read-only
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Faculty)
class FacultyAdmin(ModelAdmin):
    list_display = ('code', 'name', 'color')
    search_fields = ('code', 'name')

@admin.register(Member)
class MemberAdmin(ModelAdmin):
    list_display = ('member_id', 'name', 'role', 'faculty_code', 'is_active', 'streak_days')
    list_filter = ('role', 'is_active')
    search_fields = ('member_id', 'name', 'department')
    
    def faculty_code(self, obj):
        return obj.faculty.code if obj.faculty else '-'
    faculty_code.short_description = 'Faculty'

@admin.register(Book)
class BookAdmin(ModelAdmin):
    list_display = ('isbn', 'title', 'author', 'category', 'faculty')
    list_filter = ('category', 'faculty')
    search_fields = ('isbn', 'title', 'author')


@admin.register(RedemptionClaim)
class RedemptionClaimAdmin(ModelAdmin):
    list_display = ['code', 'member', 'reward', 'status', 'created_at', 'claimed_at']
    list_filter = ['status']
    search_fields = ['code', 'member__member_id', 'member__name', 'reward__name']
    actions = ['mark_as_claimed']

    @admin.action(description="Mark selected claims as Claimed / Sudah Diambil")
    def mark_as_claimed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='claimed', claimed_at=timezone.now())
        self.message_user(request, f"{updated} kupon berhasil ditandai sebagai sudah diambil.")


@admin.register(Seminar)
class SeminarAdmin(ModelAdmin):
    list_display = ('title', 'speaker', 'date', 'points_register', 'points_attend', 'claim_code', 'claim_code_active')
    list_filter = ('claim_code_active', 'date')
    search_fields = ('title', 'speaker', 'claim_code')
    actions = ['activate_claim_code', 'deactivate_claim_code']

    @admin.action(description="Aktifkan Klaim Kode Kehadiran")
    def activate_claim_code(self, request, queryset):
        updated = queryset.update(claim_code_active=True)
        self.message_user(request, f"{updated} seminar berhasil diaktifkan klaim kodenya.")

    @admin.action(description="Nonaktifkan Klaim Kode Kehadiran")
    def deactivate_claim_code(self, request, queryset):
        updated = queryset.update(claim_code_active=False)
        self.message_user(request, f"{updated} seminar berhasil dinonaktifkan klaim kodenya.")


@admin.register(SeminarRegistration)
class SeminarRegistrationAdmin(ModelAdmin):
    list_display = ('member_id', 'get_member_name', 'seminar', 'email', 'registered_at', 'attended_at', 'status')
    list_filter = ('status', 'seminar')
    search_fields = ('member_id', 'email', 'seminar__title')
    actions = ['mark_as_attended']

    def get_member_name(self, obj):
        member = Member.objects.filter(member_id=obj.member_id).first()
        return member.name if member else 'Tidak Terdaftar'
    get_member_name.short_description = 'Nama Anggota'

    @admin.action(description="Tandai peserta terpilih sebagai Hadir")
    def mark_as_attended(self, request, queryset):
        from django.utils import timezone
        from django.db import transaction
        from leaderboard.models import PointTransaction
        
        count = 0
        for reg in queryset.filter(status='registered'):
            with transaction.atomic():
                reg.status = 'attended'
                reg.attended_at = timezone.now()
                reg.save()
                
                # Give points
                PointTransaction.objects.create(
                    cardnumber=reg.member_id,
                    amount=reg.seminar.points_attend,
                    transaction_type='seminar',
                    description=f"Kehadiran Seminar (Manual Admin): {reg.seminar.title}"
                )
                count += 1
                
        # Clear cache
        from django.core.cache import cache
        cache.clear()
        
        self.message_user(request, f"{count} peserta berhasil ditandai sebagai hadir dan poin ditambahkan.")
