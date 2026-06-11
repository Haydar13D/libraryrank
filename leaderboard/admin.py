from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Member, Faculty, Book, LevelTier, BadgeRule, PointPolicy, SystemLog, Reward, PointTransaction, RedemptionClaim

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
