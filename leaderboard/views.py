from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from datetime import date, timedelta
import datetime
import json
from .models import Member, Reward, PointTransaction, RedemptionClaim
# Ditch models entirely for leaderboard APIs
from .demo_data import DEMO_DATA
from .koha_utils import get_live_members, get_live_member_detail, get_live_faculties_stats, get_live_books_stats, get_live_daily_visits
from .exports import export_excel_response, export_pdf_response
from django.db import connections

def get_date_range(request):
    today = date.today()
    if today.month <= 6:
        first = today.replace(month=1, day=1)
    else:
        first = today.replace(month=7, day=1)
    try:
        date_from = date.fromisoformat(request.GET.get('date_from', first.isoformat()))
        date_to   = date.fromisoformat(request.GET.get('date_to',   today.isoformat()))
    except ValueError:
        date_from, date_to = first, today
    return date_from, date_to

def _use_demo():
    # If the koha connection can't be reached, fallback to demo
    try:
        koha = connections['koha']
        koha.ensure_connection()
        return False
    except Exception:
        return True

def index(request):
    date_from, date_to = get_date_range(request)
    rewards = Reward.objects.filter(is_active=True)
    return render(request, 'leaderboard/index.html', {
        'date_from': date_from.isoformat(),
        'date_to':   date_to.isoformat(),
        'search_q':  request.GET.get('q', ''),
        'rewards':   rewards,
    })

@cache_page(60 * 10)  # 10 menit
def api_overview(request):
    if _use_demo():
        overview = dict(DEMO_DATA['overview'])
        overview['daily_visits'] = [540, 610, 580, 590, 520, 240, 0]
        return JsonResponse(overview)
    
    date_from, date_to = get_date_range(request)
    q = request.GET.get('q', '').strip()
    
    # Keep global stats overall by querying all members in this range
    all_live_members = get_live_members(date_from, date_to)
    
    # Filter for leaderboard & nominations if there is a query q
    if q:
        live_members = get_live_members(date_from, date_to, search_q=q)
    else:
        live_members = all_live_members
        
    leaderboard = live_members[:15]
    
    nominations = {}
    for role in ['student', 'lecturer', 'staff']:
        top = next((m for m in live_members if m['role'] == role), None)
        if top:
            nominations[role] = top

    # Global stats (do not shrink when searching)
    total_visited = sum(m['v_cnt'] for m in all_live_members)
    total_books = sum(m['b_cnt'] for m in all_live_members)
    active_members_count = len(all_live_members)
    total_faculties = len(set(m['faculty'] for m in all_live_members if m.get('faculty')))

    # Get real daily visits for the chart
    daily_visits = get_live_daily_visits(date_from, date_to, live_members, is_filtered=bool(q))

    return JsonResponse({
        'leaderboard': leaderboard,
        'nominations': nominations,
        'daily_visits': daily_visits,
        'stats': {
            'total_visitors': total_visited,
            'total_books': total_books,
            'active_members': active_members_count,
            'total_faculties': total_faculties
        }
    })

@cache_page(60 * 10)  # 10 menit
def api_role_leaderboard(request, role):
    if _use_demo(): return JsonResponse(DEMO_DATA.get(f'role_{role}', {'leaderboard': []}))
    date_from, date_to = get_date_range(request)
    q = request.GET.get('q', '').strip()
    
    members = get_live_members(date_from, date_to, search_q=q)
    role_members = [m for m in members if m['role'] == role][:20]
    
    for i, m in enumerate(role_members):
        m['rank'] = i + 1
        
    return JsonResponse({'leaderboard': role_members})

@cache_page(60 * 10)  # 10 menit
def api_books(request):
    if _use_demo(): return JsonResponse(DEMO_DATA['books'])
    date_from, date_to = get_date_range(request)

    # Kedua fungsi ini share cache key yang sama — get_live_members tidak query ulang
    books = get_live_books_stats(date_from, date_to)
    members = get_live_members(date_from, date_to)  # dari cache jika sudah dipanggil

    borrowers = sorted(members, key=lambda x: x['b_cnt'], reverse=True)[:8]
    for i, m in enumerate(borrowers):
        m['rank'] = i + 1
        m['visits'] = m['b_cnt']

    return JsonResponse({'books': books, 'borrowers': borrowers})

@cache_page(60 * 10)  # 10 menit
def api_faculties(request):
    if _use_demo(): return JsonResponse(DEMO_DATA['faculties'])
    date_from, date_to = get_date_range(request)

    faculties = get_live_faculties_stats(date_from, date_to)
    members = get_live_members(date_from, date_to)  # dari cache, tidak query ulang

    # Top students per faculty
    top_per_faculty = []
    fac_names = set(m['faculty'] for m in members if m['role'] == 'student')

    for fac in fac_names:
        top = next((m for m in members if m['faculty'] == fac and m['role'] == 'student'), None)
        if top:
            top_per_faculty.append({
                'faculty': fac, 'faculty_color': top['faculty_color'],
                'name': top['name'], 'initials': top['initials'],
                'visits': top['v_cnt'], 'role': 'student'
            })

    top_per_faculty.sort(key=lambda x: x['visits'], reverse=True)
    return JsonResponse({'faculties': faculties, 'top_per_faculty': top_per_faculty})

@cache_page(60) # lower cache for detail
def api_member_detail(request, member_id):
    if _use_demo(): 
        all_p = (DEMO_DATA['overview']['leaderboard'] + DEMO_DATA.get('role_student', {}).get('leaderboard', []))
        p = next((x for x in all_p if x['id'] == member_id), None)
        if not p: return JsonResponse({'error': 'Not found'}, status=404)
        demo_badges = [
            {'name': 'Library Legend', 'desc': 'Top 10 Klasemen!', 'image_url': '/static/img/badges/top 10 leaderboard.png', 'color': '#f1c40f'},
            {'name': 'Weekly Warrior', 'desc': 'Rajin datang ke perpus.', 'image_url': '/static/img/badges/weekly warior.png', 'color': '#4DA6FF'},
            {'name': 'Book Worm', 'desc': 'Sering pinjam buku.', 'image_url': '/static/img/badges/bookworm.png', 'color': '#1CBDB3'}
        ]
        return JsonResponse({**p, 'visits_range': p['visits'], 'visits_total': p['visits'], 'books_range': p['books'], 'books_total': p['books'], 'badges': demo_badges, 'recent_borrows': []})
        
    date_from, date_to = get_date_range(request)
    detail = get_live_member_detail(member_id, date_from, date_to)
    if not detail:
        return JsonResponse({'error': 'Not found'}, status=404)
    return JsonResponse(detail)

@cache_page(60 * 10)  # 10 menit
def api_pemustaka_teraktif(request):
    if _use_demo():
        from .demo_data import _STUDENTS, _LECTURERS, _STAFF, _ALL
        role_param = request.GET.get('role', 'all').lower()
        role_map = {
            # bahasa Indonesia
            'mahasiswa': 'student', 'dosen': 'lecturer', 'tendik': 'staff',
            # bahasa Inggris (dipakai JS frontend)
            'student': 'student', 'lecturer': 'lecturer', 'staff': 'staff',
        }
        role = role_map.get(role_param, 'all')
        if role == 'student': pool = _STUDENTS
        elif role == 'lecturer': pool = _LECTURERS
        elif role == 'staff': pool = _STAFF
        else: pool = _ALL
        top_xp_k        = sorted(pool, key=lambda x: x['visits'], reverse=True)[:10]
        top_pengunjung_k = sorted(pool, key=lambda x: x['visits'], reverse=True)[:10]
        top_peminjam_k  = sorted(pool, key=lambda x: x['books'],  reverse=True)[:10]
        # Seminar: ambil 6 teratas (sisanya 0 seminar)
        top_seminar_k   = sorted(pool[:6], key=lambda x: x['visits'], reverse=True)[:10]
        return JsonResponse({
            'top_xp':        [dict(p, rank=i+1, total_p=p['visits']) for i, p in enumerate(top_xp_k)],
            'top_pengunjung': [dict(p, rank=i+1) for i, p in enumerate(top_pengunjung_k)],
            'top_peminjam':  [dict(p, rank=i+1) for i, p in enumerate(top_peminjam_k)],
            'top_seminar':   [dict(p, rank=i+1, visits=0) for i, p in enumerate(top_seminar_k)],
        })
        
    date_from, date_to = get_date_range(request)
    if 'year' in request.GET:
        try:
            year = int(request.GET['year'])
            date_from = date(year, 1, 1)
            date_to = date(year, 12, 31)
        except ValueError:
            pass

    members = get_live_members(date_from, date_to)
    
    role_param = request.GET.get('role', 'all').lower()
    role_map = {
        'mahasiswa': 'student', 'dosen': 'lecturer', 'tendik': 'staff',
        'student': 'student', 'lecturer': 'lecturer', 'staff': 'staff'
    }
    target_role = role_map.get(role_param, 'all')
    
    if target_role != 'all':
        members = [m for m in members if m['role'] == target_role]
        
    top_xp = sorted(members, key=lambda x: x['total_p'], reverse=True)[:10]
    top_pengunjung = sorted(members, key=lambda x: x['v_cnt'], reverse=True)[:10]
    top_peminjam = sorted(members, key=lambda x: x['b_cnt'], reverse=True)[:10]
    top_seminar = sorted(members, key=lambda x: x.get('s_cnt', 0), reverse=True)[:10]
    
    for i, m in enumerate(top_xp): m['rank'] = i + 1
    
    for i, m in enumerate(top_pengunjung): 
        mp = dict(m)
        mp['rank'] = i + 1
        mp['visits'] = m['v_cnt'] # Render as visits count
        top_pengunjung[i] = mp
        
    for i, m in enumerate(top_peminjam): 
        mp = dict(m)
        mp['rank'] = i + 1
        mp['visits'] = m['b_cnt'] # Render as books count
        top_peminjam[i] = mp

    for i, m in enumerate(top_seminar): 
        mp = dict(m)
        mp['rank'] = i + 1
        mp['visits'] = m.get('s_cnt', 0) # Render as seminar count
        top_seminar[i] = mp
        
    return JsonResponse({
        'top_xp': top_xp,
        'top_pengunjung': top_pengunjung,
        'top_peminjam': top_peminjam,
        'top_seminar': top_seminar
    })

def export_excel(request):
    date_from, date_to = get_date_range(request)
    if _use_demo(): return JsonResponse({'error': 'Export not supported in demo mode'})
    return export_excel_response(date_from, date_to)

def export_pdf(request):
    date_from, date_to = get_date_range(request)
    if _use_demo(): return JsonResponse({'error': 'Export not supported in demo mode'})
    return export_pdf_response(date_from, date_to)


from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import random
from django.db import models

def get_member_total_points(cardnumber):
    today = date.today()
    if today.month <= 6:
        first = today.replace(month=1, day=1)
    else:
        first = today.replace(month=7, day=1)
    
    if _use_demo():
        from .demo_data import _ALL
        p = next((x for x in _ALL if x['id'] == cardnumber), None)
        if p:
            from django.db.models import Sum
            local_pt = PointTransaction.objects.filter(cardnumber=cardnumber).aggregate(total=Sum('amount'))['total'] or 0
            return p['visits'] + local_pt
        return 0
        
    from .koha_utils import get_live_members
    members = get_live_members(first, today, search_q=cardnumber)
    if members:
        for m in members:
            if m['id'] == cardnumber:
                return m['total_p']
    return 0


@csrf_exempt
def api_request_otp(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body) if request.body else request.POST
    except Exception:
        data = request.POST
        
    member_id = data.get('member_id', '').strip().upper()
    reward_id = data.get('reward_id')
    
    if not member_id or not reward_id:
        return JsonResponse({'success': False, 'error': 'NIM dan ID Hadiah harus diisi.'}, status=400)
        
    member = Member.objects.filter(member_id=member_id).first()
    if not member:
        return JsonResponse({'success': False, 'error': 'NIM/ID Anggota tidak terdaftar.'}, status=404)
        
    reward = Reward.objects.filter(id=reward_id, is_active=True).first()
    if not reward:
        return JsonResponse({'success': False, 'error': 'Hadiah tidak ditemukan atau tidak aktif.'}, status=404)
        
    if reward.stock <= 0:
        return JsonResponse({'success': False, 'error': 'Stok hadiah sudah habis.'}, status=400)
        
    points = get_member_total_points(member_id)
    if points < reward.points_cost:
        return JsonResponse({
            'success': False, 
            'error': f'Poin Anda tidak cukup. Poin Anda: {points} XP, Butuh: {reward.points_cost} XP.'
        }, status=400)
        
    otp = str(random.randint(100000, 999999))
    cache.set(f"otp_{member_id}", {'otp': otp, 'reward_id': reward_id}, 180)
    
    email = member.email
    if not email:
        email = f"{member_id.lower()}@student.ums.ac.id"
        
    subject = "[UMSLibrary] Kode OTP Verifikasi Penukaran Poin"
    message = f"""Halo {member.name},

Anda sedang mengajukan penukaran poin LibraryRank untuk reward:
🎁 {reward.name} ({reward.points_cost} XP)

Berikut adalah kode verifikasi OTP Anda:
👉 [ {otp} ]

Kode ini berlaku selama 3 menit. Demi keamanan poin Anda, jangan berikan kode ini kepada siapa pun.

Salam Hangat,
Team UMSLibrary
"""
    
    email_parts = email.split('@')
    name_part = email_parts[0]
    domain_part = email_parts[1]
    if len(name_part) > 2:
        masked_name = name_part[0] + '***' + name_part[-1]
    else:
        masked_name = '***'
    masked_email = f"{masked_name}@{domain_part}"

    email_sent = False
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL or 'noreply@ums.ac.id',
            [email],
            fail_silently=False,
        )
        email_sent = True
    except Exception as e:
        print(f"=== EMAIL OTP SENT TO {email} (SMTP error fallback) ===")
        print(f"SMTP Error Details: {e}")
        print(message)
        print("=========================================================")
        
    return JsonResponse({
        'success': True,
        'email_masked': masked_email,
        'email_sent': email_sent,
        'message': 'OTP berhasil dikirim ke email kampus.'
    })


@csrf_exempt
def api_verify_otp_and_redeem(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        
    try:
        data = json.loads(request.body) if request.body else request.POST
    except Exception:
        data = request.POST
        
    member_id = data.get('member_id', '').strip().upper()
    otp_input = data.get('otp', '').strip()
    
    if not member_id or not otp_input:
        return JsonResponse({'success': False, 'error': 'NIM dan OTP harus diisi.'}, status=400)
        
    cached_data = cache.get(f"otp_{member_id}")
    if not cached_data:
        return JsonResponse({'success': False, 'error': 'Kode OTP sudah kadaluarsa atau belum diajukan.'}, status=400)
        
    if cached_data['otp'] != otp_input:
        return JsonResponse({'success': False, 'error': 'Kode OTP salah.'}, status=400)
        
    reward_id = cached_data['reward_id']
    member = Member.objects.filter(member_id=member_id).first()
    reward = Reward.objects.filter(id=reward_id, is_active=True).first()
    
    if not member or not reward:
        return JsonResponse({'success': False, 'error': 'Data anggota atau hadiah tidak valid.'}, status=400)
        
    if reward.stock <= 0:
        return JsonResponse({'success': False, 'error': 'Stok hadiah sudah habis.'}, status=400)
        
    points = get_member_total_points(member_id)
    if points < reward.points_cost:
        return JsonResponse({'success': False, 'error': 'Poin Anda tidak cukup.'}, status=400)
        
    cache.delete(f"otp_{member_id}")
    
    from django.db import transaction
    import uuid
    
    claim_code = f"UMS-REDEEM-{uuid.uuid4().hex[:6].upper()}"
    
    try:
        with transaction.atomic():
            PointTransaction.objects.create(
                cardnumber=member_id,
                amount=-reward.points_cost,
                transaction_type='redeem',
                description=f"Redeem Poin: {reward.name}"
            )
            
            reward.stock = models.F('stock') - 1
            reward.save()
            reward.refresh_from_db()
            
            claim = RedemptionClaim.objects.create(
                code=claim_code,
                member=member,
                reward=reward,
                status='pending'
            )
            
        email = member.email or f"{member_id.lower()}@student.ums.ac.id"
        subject = f"[UMSLibrary] Konfirmasi Penukaran Poin Berhasil - {claim_code}"
        message = f"""Halo {member.name},

Selamat! Penukaran poin Anda telah berhasil diproses.

Detail Penukaran:
-----------------------------------------------
• NIM/ID           : {member_id}
• Merchandise      : {reward.name}
• Poin Terpotong   : {reward.points_cost} XP
• Kode Unik Kupon  : {claim_code}
• Tanggal Penukaran: {timezone.now().strftime('%d %B %Y %H:%M')}
-----------------------------------------------

Silakan tunjukkan email ini atau tunjukkan Kode Unik di atas kepada petugas di Meja Sirkulasi Perpustakaan untuk mengambil merchandise fisik Anda.

Terima kasih telah aktif mengunjungi dan membaca di UMSLibrary!

Salam Hangat,
Team UMSLibrary
"""
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL or 'noreply@ums.ac.id',
                [email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"=== EMAIL CONFIRMATION SENT TO {email} (SMTP error fallback) ===")
            print(f"SMTP Error Details: {e}")
            print(message)
            print("==========================================================================")
            
        cache.clear()
        
        return JsonResponse({
            'success': True,
            'message': 'Penukaran poin berhasil!',
            'code': claim_code,
            'reward_name': reward.name,
            'points_cost': reward.points_cost,
            'remaining_points': points - reward.points_cost
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Terjadi kesalahan saat memproses penukaran: {str(e)}'}, status=500)
