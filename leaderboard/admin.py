from django.contrib import admin, messages
from django.db import transaction
from unfold.admin import ModelAdmin
from unfold.decorators import display
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.urls import path, reverse
from django.shortcuts import redirect
from django.utils import timezone
from .models import Member, Faculty, LevelTier, BadgeRule, PointPolicy, SystemLog, Reward, PointTransaction, RedemptionClaim, Seminar, SeminarRegistration, LeaderboardConfig

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
    list_display = ['get_seminar_title', 'get_points_display', 'input_method', 'processed', 'created_at']
    list_filter = ['processed', 'seminar']
    search_fields = ['seminar__title', 'title']
    readonly_fields = ['processed']
    fields = ['seminar', 'points', 'csv_file', 'manual_input', 'processed']

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={
            'placeholder': 'Contoh cara input data:\nL200230051\nL200230052\nL200230053\n\n* Ketik satu NIM per baris.\n* Tekan tombol ENTER untuk NIM selanjutnya.\n* NIM bisa menggunakan huruf besar atau kecil.',
            'rows': 8
        })},
    }

    @display(description='Event / Seminar')
    def get_seminar_title(self, obj):
        if obj.seminar:
            return obj.seminar.title
        return obj.title or '-'

    @display(description='Poin XP')
    def get_points_display(self, obj):
        if obj.points:
            return f"{obj.points} XP"
        policy = PointPolicy.objects.filter(action_type='seminar', is_active=True).first()
        val = policy.points if policy else (obj.seminar.points_attend if obj.seminar else 15)
        return f"{val} XP (Auto Kebijakan)"

    def input_method(self, obj):
        parts = []
        if obj.csv_file: parts.append("CSV File")
        if obj.manual_input: parts.append("Manual Textbox")
        return " + ".join(parts) if parts else "-"
    input_method.short_description = "Metode Input"


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
    list_display = ('title', 'category_badge', 'mode_badge', 'speaker', 'date', 'points_register', 'points_attend', 'claim_code', 'code_status', 'image_thumbnail', 'cert_status')
    list_filter = ('category', 'event_mode', 'claim_code_active', 'date')
    search_fields = ('title', 'speaker', 'claim_code', 'location')
    actions = ['activate_claim_code', 'deactivate_claim_code']
    readonly_fields = ('image_preview', 'cert_template_preview')
    fieldsets = (
        ('Informasi Acara & Kategori', {
            'fields': ('title', 'category', 'event_mode', 'description', 'speaker', 'date', 'location', 'meeting_url'),
            'description': 'Pilih jenis kegiatan dan format pelaksanaan (Tatap Muka, Daring/Zoom, atau Hybrid). Jika Daring/Hybrid, pastikan menyertakan Link Virtual Meeting.'
        }),
        ('Poster / Banner Acara', {'fields': ('image', 'image_preview'), 'description': 'Disarankan mengunggah gambar dengan rasio 16:9 (misal 1200x675px) atau 4:3 agar tampilan di TV Kiosk dan Portal optimal.'}),
        ('Pengaturan E-Sertifikat & Template', {
            'fields': (
                'cert_template',
                'cert_template_preview',
                'cert_font_family',
                'cert_name_pos_y',
                'cert_name_font_size',
                'cert_name_color',
                'cert_show_nim',
                'cert_nim_pos_y',
                'cert_number_template',
                'cert_number_pos_y',
            ),
            'description': 'Unggah file gambar background sertifikat kosong (PNG/JPG, disarankan A4 Landscape). Teks nama peserta akan otomatis dicetak simetris di tengah horizontal sesuai koordinat vertikal (Y).'
        }),
        ('Pendaftaran', {'fields': ('registration_open', 'registration_close')}),
        ('Pengaturan Poin', {'fields': ('points_register', 'points_attend')}),
        ('Kode Klaim Kehadiran', {'fields': ('claim_code', 'claim_code_active')}),
    )

    @display(description='Kategori', label=True)
    def category_badge(self, obj):
        colors = {
            'seminar': '#3b82f6',
            'workshop': '#8b5cf6',
            'training': '#f59e0b',
            'webinar': '#06b6d4',
            'book_review': '#ec4899',
            'other': '#6b7280',
        }
        color = colors.get(obj.category, '#3b82f6')
        return format_html('<span style="background:{}; color:#fff; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:700;">{}</span>', color, obj.get_category_display())

    @display(description='Format', label=True)
    def mode_badge(self, obj):
        mode_configs = {
            'offline': {'color': '#10b981', 'label': 'Offline'},
            'online': {'color': '#06b6d4', 'label': 'Online'},
            'hybrid': {'color': '#8b5cf6', 'label': 'Hybrid'},
        }
        cfg = mode_configs.get(obj.event_mode, {'color': '#6b7280', 'label': obj.get_event_mode_display()})
        return format_html('<span style="background:{}; color:#fff; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:700;">{}</span>', cfg['color'], cfg['label'])

    @display(description='Poster')
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 30px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />', obj.image.url)
        return "-"

    @display(description='Preview Poster Saat Ini')
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 320px; max-height: 180px; object-fit: cover; border-radius: 8px; border: 1px solid #ccc; box-shadow: 0 2px 6px rgba(0,0,0,0.1);" />', obj.image.url)
        return "Belum ada poster diunggah."

    @display(description='Visual Designer & Live Preview Template')
    def cert_template_preview(self, obj):
        img_url = obj.cert_template.url if (obj and obj.cert_template) else ''
        html = render_to_string('leaderboard/admin/cert_designer.html', {
            'obj': obj,
            'img_url': img_url
        })
        return mark_safe(html)

    @display(description='E-Sertifikat', boolean=True)
    def cert_status(self, obj):
        return bool(obj.cert_template)

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
    list_display = ('member_id', 'get_member_name', 'seminar', 'email', 'registered_at', 'attended_at', 'status_badge', 'certificate_download')
    list_filter = ('status', 'seminar')
    search_fields = ('member_id', 'email', 'seminar__title', 'certificate_number')
    actions = ['mark_as_attended', 'generate_certificates_action']

    @display(description='Status', label=True)
    def status_badge(self, obj):
        return "Attended" if obj.status == 'attended' else "Registered"

    @display(description='Sertifikat PDF')
    def certificate_download(self, obj):
        if obj.certificate_pdf:
            return format_html(
                '<a href="{}" target="_blank" style="display:inline-flex; align-items:center; gap:5px; background:#10b981; color:#fff; padding:3px 8px; border-radius:4px; text-decoration:none; font-size:11px; font-weight:700;">'
                '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>Unduh PDF</a>',
                obj.certificate_pdf.url
            )
        if obj.status == 'attended' and obj.seminar.cert_template:
            return format_html('<span style="color:#f59e0b; font-size:11px;">Belum Di-generate</span>')
        return "-"

    def get_member_name(self, obj):
        member = Member.objects.filter(member_id=obj.member_id).first()
        return member.name if member else 'Tidak Terdaftar'
    get_member_name.short_description = 'Nama Anggota'

    @admin.action(description="Tandai peserta terpilih sebagai Hadir & Kirim Sertifikat")
    def mark_as_attended(self, request, queryset):
        from django.utils import timezone
        from django.db import transaction
        from leaderboard.models import PointTransaction
        from leaderboard.cert_utils import generate_certificate_pdf, send_certificate_email
        
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
                    description=f"Kehadiran Seminar (Admin): {reg.seminar.title}"
                )

            # Generate cert & send email
            if reg.seminar.cert_template:
                generate_certificate_pdf(reg)
                send_certificate_email(reg)

            count += 1
            
        self.message_user(request, f"{count} peserta berhasil ditandai Hadir dan sertifikat diproses.")

    @admin.action(description="Generate / Regenerate Ulang Sertifikat PDF Peserta")
    def generate_certificates_action(self, request, queryset):
        from leaderboard.cert_utils import generate_certificate_pdf
        generated = 0
        for reg in queryset.filter(status='attended'):
            if reg.seminar.cert_template:
                generate_certificate_pdf(reg)
                generated += 1
        self.message_user(request, f"{generated} sertifikat PDF berhasil di-generate ulang.")

from .models import APIKey

@admin.register(APIKey)
class APIKeyAdmin(ModelAdmin):
    list_display = ['name', 'key', 'is_active', 'created_at', 'last_used']
    list_filter = ['is_active']
    search_fields = ['name', 'key']
