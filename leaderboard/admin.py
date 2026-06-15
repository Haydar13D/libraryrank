from django.contrib import admin, messages
from django.db import transaction
from unfold.admin import ModelAdmin
from unfold.decorators import display
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import redirect
from django.utils import timezone
from .models import Member, Faculty, Book, LevelTier, BadgeRule, PointPolicy, SystemLog, Reward, PointTransaction, RedemptionClaim, Seminar, SeminarRegistration, LeaderboardConfig

# Visit and BorrowRecord models are no longer managed by Django ORM!
# The entire architecture has shifted to Live Koha Read-Only via koha_utils.py
# Therefore, registering them will show zero local data and cause confusion.

@admin.register(LeaderboardConfig)
class LeaderboardConfigAdmin(ModelAdmin):
    list_display = ['reset_mode', 'get_active_reset_date']
    
    def has_add_permission(self, request):
        return not LeaderboardConfig.objects.exists()

    @display(description='Tanggal Reset Aktif')
    def get_active_reset_date(self, obj):
        return LeaderboardConfig.get_active_reset_date()

@admin.register(LevelTier)
class LevelTierAdmin(ModelAdmin):
    list_display = ['name', 'level_num', 'min_xp', 'max_xp', 'color_badge']
    ordering = ['min_xp']
    fieldsets = (
        ('Informasi Level', {'fields': ('name', 'level_num')}),
        ('Kriteria XP', {'fields': ('min_xp', 'max_xp')}),
        ('Visual', {'fields': ('color',)}),
    )

    @display(description='Warna')
    def color_badge(self, obj):
        return format_html('<span style="background-color: {}; padding: 4px 8px; border-radius: 4px; color: #fff; font-weight: bold;">{}</span>', obj.color, obj.color)

@admin.register(BadgeRule)
class BadgeRuleAdmin(ModelAdmin):
    list_display = ['id_code', 'name', 'criteria_type', 'min_value', 'icon']

@admin.register(PointPolicy)
class PointPolicyAdmin(ModelAdmin):
    list_display = ['action_type', 'points', 'is_active']
    list_editable = ['points', 'is_active']

@admin.register(Reward)
class RewardAdmin(ModelAdmin):
    list_display = ['name', 'points_cost', 'stock', 'status_label', 'action_buttons']
    list_editable = ['stock', 'points_cost']
    search_fields = ['name']
    fieldsets = (
        ('Informasi Barang', {'fields': ('name', 'description', 'image')}),
        ('Pengaturan Stok & Harga', {'fields': ('points_cost', 'stock', 'is_active')}),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/toggle-active/', self.admin_site.admin_view(self.toggle_active_view), name='toggle_reward_active'),
        ]
        return custom_urls + urls

    def toggle_active_view(self, request, object_id):
        obj = self.get_object(request, object_id)
        if obj:
            obj.is_active = not obj.is_active
            obj.save()
            status = "Aktif" if obj.is_active else "Nonaktif"
            self.message_user(request, f"Status merchandise {obj.name} diubah menjadi {status}.")
        return redirect('admin:leaderboard_reward_changelist')

    @display(description='Aksi')
    def action_buttons(self, obj):
        url_edit = reverse('admin:leaderboard_reward_change', args=[obj.id])
        btn_edit = format_html('<a href="{}" style="background-color: #3b82f6; color: white; padding: 4px 12px; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 12px;">Edit</a>', url_edit)
        
        url_toggle = reverse('admin:toggle_reward_active', args=[obj.id])
        if obj.is_active:
            btn_toggle = format_html(
                '<a href="{}" style="display: inline-flex; align-items: center; width: 44px; height: 24px; background-color: #10b981; border-radius: 9999px; text-decoration: none; transition: background-color 0.2s;" title="Matikan">'
                '<span style="display: inline-block; width: 18px; height: 18px; background-color: white; border-radius: 50%; transform: translateX(22px); transition: transform 0.2s; box-shadow: 0 1px 3px rgba(0,0,0,0.3);"></span>'
                '</a>', url_toggle)
        else:
            btn_toggle = format_html(
                '<a href="{}" style="display: inline-flex; align-items: center; width: 44px; height: 24px; background-color: #d1d5db; border-radius: 9999px; text-decoration: none; transition: background-color 0.2s;" title="Sediakan">'
                '<span style="display: inline-block; width: 18px; height: 18px; background-color: white; border-radius: 50%; transform: translateX(4px); transition: transform 0.2s; box-shadow: 0 1px 3px rgba(0,0,0,0.3);"></span>'
                '</a>', url_toggle)
            
        return format_html('<div style="display: flex; gap: 12px; align-items: center;">{} {}</div>', btn_edit, btn_toggle)

    @display(description='Status', label=True)
    def status_label(self, obj):
        if not obj.is_active:
            return "Tidak Tersedia"
        return "Tersedia" if obj.stock > 0 else "Habis"

from unfold.decorators import display, action

@admin.register(PointTransaction)
class PointTransactionAdmin(ModelAdmin):
    list_display = ['cardnumber', 'amount', 'transaction_type', 'description', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['cardnumber', 'description']
    actions_list = ['export_filtered_csv']

    @action(description="Export Data CSV")
    def export_filtered_csv(self, request):
        import csv
        from django.http import HttpResponse
        
        # Ambil data yang sudah difilter di halaman admin saat ini
        cl = self.get_changelist_instance(request)
        queryset = cl.get_queryset(request)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="riwayat_transaksi.csv"'
        response.write(b'\xef\xbb\xbf')
        
        writer = csv.writer(response, delimiter=';')
        writer.writerow(['Cardnumber/NIM', 'Jumlah Poin', 'Tipe Transaksi', 'Deskripsi', 'Tanggal'])
        
        for obj in queryset:
            tipe = getattr(obj, 'get_transaction_type_display', lambda: obj.transaction_type)()
            tanggal = obj.created_at.strftime('%Y-%m-%d %H:%M:%S') if obj.created_at else ''
            writer.writerow([obj.cardnumber, obj.amount, tipe, obj.description, tanggal])
            
        return response

from .models import SeminarUpload
from django.db import models
from django.forms import Textarea
@admin.register(SeminarUpload)
class SeminarUploadAdmin(ModelAdmin):
    list_display = ['title', 'points', 'input_method', 'processed', 'created_at']
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
    list_display = ('code', 'name', 'color_badge')
    search_fields = ('code', 'name')

    @display(description='Warna Tema')
    def color_badge(self, obj):
        if not obj.color: return '-'
        return format_html('<span style="background-color: {}; padding: 4px 8px; border-radius: 4px; color: #fff; font-weight: bold;">{}</span>', obj.color, obj.color)

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
    list_display = ['code', 'member', 'reward', 'status_badge', 'created_at', 'action_button']
    list_filter = ['status']
    search_fields = ['code', 'member__member_id', 'member__name', 'reward__name']
    actions = ['mark_as_claimed']
    fieldsets = (
        ('Informasi Penukaran', {'fields': ('code', 'member', 'reward')}),
        ('Status', {'fields': ('status', 'claimed_at')}),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/process-claim/', self.admin_site.admin_view(self.process_claim_view), name='process_redemption_claim'),
            path('<path:object_id>/reject-claim/', self.admin_site.admin_view(self.reject_claim_view), name='reject_redemption_claim'),
        ]
        return custom_urls + urls

    def process_claim_view(self, request, object_id):
        obj = self.get_object(request, object_id)
        if obj and obj.status == 'pending':
            with transaction.atomic():
                obj.status = 'claimed'
                obj.claimed_at = timezone.now()
                obj.save()
                
                # Potong poin permanen karena sudah disetujui
                PointTransaction.objects.create(
                    cardnumber=obj.member.member_id,
                    amount=-obj.reward.points_cost,
                    transaction_type='redeem',
                    description=f"Admin Approved Redeem: {obj.reward.name}"
                )
                
            self.message_user(request, f"Klaim {obj.code} berhasil diselesaikan. Poin telah dipotong permanen.")
        return redirect('admin:leaderboard_redemptionclaim_changelist')

    def reject_claim_view(self, request, object_id):
        obj = self.get_object(request, object_id)
        if obj and obj.status == 'pending':
            with transaction.atomic():
                obj.status = 'rejected'
                obj.save()
                
                # Kembalikan stok barang
                obj.reward.stock = models.F('stock') + 1
                obj.reward.save()
                
            self.message_user(request, f"Klaim {obj.code} berhasil ditolak. Stok dan poin mahasiswa telah dikembalikan.", level=messages.WARNING)
        return redirect('admin:leaderboard_redemptionclaim_changelist')

    @display(description='Aksi')
    def action_button(self, obj):
        url_edit = reverse('admin:leaderboard_redemptionclaim_change', args=[obj.id])
        created_str = obj.created_at.strftime('%d %b %Y, %H:%M') if obj.created_at else '-'
        
        btn_detail = format_html(
            '<button type="button" class="show-detail-modal-btn" '
            'data-code="{}" data-member="{}" data-reward="{}" data-date="{}" data-edit-url="{}" '
            'style="background-color: #3b82f6; color: white; padding: 4px 12px; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 12px; border: none; cursor: pointer; white-space: nowrap;">Detail</button>',
            obj.code, obj.member.name if obj.member else '-', obj.reward.name if obj.reward else '-', created_str, url_edit
        )
        
        if obj.status == 'pending':
            url_process = reverse('admin:process_redemption_claim', args=[obj.id])
            btn_process = format_html('<a href="{}" style="background-color: #1cbdb3; color: white; padding: 4px 12px; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 12px; white-space: nowrap;">Tandai Selesai</a>', url_process)
            
            url_reject = reverse('admin:reject_redemption_claim', args=[obj.id])
            btn_reject = format_html('<a href="{}" style="background-color: #ef4444; color: white; padding: 4px 12px; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 12px; white-space: nowrap;" onclick="return confirm(\'Tolak klaim ini? Stok barang akan dikembalikan ke sistem.\');">Tolak</a>', url_reject)
            
            return format_html('<div style="display: flex; gap: 8px; align-items: center;">{} {} {}</div>', btn_detail, btn_process, btn_reject)
            
        elif obj.status == 'claimed':
            btn_process = format_html('<span style="color: #9ca3af; font-weight: bold; font-size: 12px; white-space: nowrap;">Selesai ?</span>')
        else:
            btn_process = format_html('<span style="color: #ef4444; font-weight: bold; font-size: 12px; white-space: nowrap;">Ditolak ❌</span>')
            
        return format_html('<div style="display: flex; gap: 8px; align-items: center;">{} {}</div>', btn_detail, btn_process)

    @display(description='Status', label=True)
    def status_badge(self, obj):
        if obj.status == 'claimed':
            return "Claimed"
        elif obj.status == 'rejected':
            return "Rejected"
        return "Pending"

    @admin.action(description="Mark selected claims as Claimed / Sudah Diambil")
    def mark_as_claimed(self, request, queryset):
        updated = queryset.update(status='claimed', claimed_at=timezone.now())
        self.message_user(request, f"{updated} kupon berhasil ditandai sebagai sudah diambil.")


@admin.register(Seminar)
class SeminarAdmin(ModelAdmin):
    list_display = ('title', 'speaker', 'date', 'points_register', 'points_attend', 'claim_code', 'code_status')
    list_filter = ('claim_code_active', 'date')
    search_fields = ('title', 'speaker', 'claim_code')
    actions = ['activate_claim_code', 'deactivate_claim_code']
    fieldsets = (
        ('Informasi Umum', {'fields': ('title', 'description', 'speaker', 'date')}),
        ('Pendaftaran', {'fields': ('registration_open', 'registration_close')}),
        ('Pengaturan Poin', {'fields': ('points_register', 'points_attend')}),
        ('Kode Klaim Kehadiran', {'fields': ('claim_code', 'claim_code_active')}),
    )

    @display(description='Status Kode', boolean=True)
    def code_status(self, obj):
        return obj.claim_code_active

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
    list_display = ('member_id', 'get_member_name', 'seminar', 'email', 'registered_at', 'attended_at', 'status_badge')
    list_filter = ('status', 'seminar')
    search_fields = ('member_id', 'email', 'seminar__title')
    actions = ['mark_as_attended']

    @display(description='Status', label=True)
    def status_badge(self, obj):
        return "Attended" if obj.status == 'attended' else "Registered"

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

from .models import APIKey

@admin.register(APIKey)
class APIKeyAdmin(ModelAdmin):
    list_display = ['name', 'key', 'is_active', 'created_at', 'last_used']
    list_filter = ['is_active']
    search_fields = ['name', 'key']
