from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from datetime import date, timedelta
import datetime
import json
from .models import Reward, PointTransaction
# Ditch models entirely for leaderboard APIs
from .demo_data import DEMO_DATA
from .koha_utils import get_live_members, get_live_member_detail, get_live_faculties_stats, get_live_books_stats
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

@cache_page(60 * 5)
def api_overview(request):
    if _use_demo(): return JsonResponse(DEMO_DATA['overview'])
    
    date_from, date_to = get_date_range(request)
    q = request.GET.get('q', '').strip()
    
    live_members = get_live_members(date_from, date_to, search_q=q)
    
    leaderboard = live_members[:15]
    
    nominations = {}
    for role in ['student', 'lecturer', 'staff']:
        top = next((m for m in live_members if m['role'] == role), None)
        if top:
            nominations[role] = top

    # Fake global stats based on active aggregated counts
    total_visited = sum(m['v_cnt'] for m in live_members)
    total_books = sum(m['b_cnt'] for m in live_members)

    return JsonResponse({
        'leaderboard': leaderboard,
        'nominations': nominations,
        'stats': {
            'total_visitors': total_visited,
            'total_books': total_books,
            'active_members': len(live_members),
            'total_faculties': len(set(m['faculty'] for m in live_members))
        }
    })

@cache_page(60 * 5)
def api_role_leaderboard(request, role):
    if _use_demo(): return JsonResponse(DEMO_DATA.get(f'role_{role}', {'leaderboard': []}))
    date_from, date_to = get_date_range(request)
    q = request.GET.get('q', '').strip()
    
    members = get_live_members(date_from, date_to, search_q=q)
    role_members = [m for m in members if m['role'] == role][:20]
    
    for i, m in enumerate(role_members):
        m['rank'] = i + 1
        
    return JsonResponse({'leaderboard': role_members})

@cache_page(60 * 5)
def api_books(request):
    if _use_demo(): return JsonResponse(DEMO_DATA['books'])
    date_from, date_to = get_date_range(request)
    
    books = get_live_books_stats(date_from, date_to)
    members = get_live_members(date_from, date_to)
    
    borrowers = sorted(members, key=lambda x: x['b_cnt'], reverse=True)[:8]
    for i, m in enumerate(borrowers):
        m['rank'] = i + 1
        m['visits'] = m['b_cnt'] # Render borrow count in UI
        
    return JsonResponse({'books': books, 'borrowers': borrowers})

@cache_page(60 * 5)
def api_faculties(request):
    if _use_demo(): return JsonResponse(DEMO_DATA['faculties'])
    date_from, date_to = get_date_range(request)
    
    faculties = get_live_faculties_stats(date_from, date_to)
    members = get_live_members(date_from, date_to)
    
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
        return JsonResponse({**p, 'visits_range': p['visits'], 'visits_total': p['visits'], 'books_range': p['books'], 'books_total': p['books'], 'badges': [], 'recent_borrows': []})
        
    date_from, date_to = get_date_range(request)
    detail = get_live_member_detail(member_id, date_from, date_to)
    if not detail:
        return JsonResponse({'error': 'Not found'}, status=404)
    return JsonResponse(detail)

@cache_page(60 * 5)
def api_pemustaka_teraktif(request):
    if _use_demo():
        from .demo_data import _STUDENTS, _LECTURERS, _STAFF, _ALL
        role_param = request.GET.get('role', 'all').lower()
        role_map = {'mahasiswa': 'student', 'dosen': 'lecturer', 'tendik': 'staff'}
        role = role_map.get(role_param, 'all')
        if role == 'student': pool = _STUDENTS
        elif role == 'lecturer': pool = _LECTURERS
        elif role == 'staff': pool = _STAFF
        else: pool = _ALL
        top_pengunjung_k = sorted(pool, key=lambda x: x['visits'], reverse=True)[:10]
        top_peminjam_k = sorted(pool, key=lambda x: x['books'], reverse=True)[:10]
        return JsonResponse({
            'top_pengunjung': [dict(p, rank=i+1) for i, p in enumerate(top_pengunjung_k)],
            'top_peminjam': [dict(p, rank=i+1) for i, p in enumerate(top_peminjam_k)]
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
        
    top_pengunjung = sorted(members, key=lambda x: x['total_p'], reverse=True)[:10]
    top_peminjam = sorted(members, key=lambda x: x['b_cnt'], reverse=True)[:10]
    
    for i, m in enumerate(top_pengunjung): m['rank'] = i + 1
    for i, m in enumerate(top_peminjam): 
        mp = dict(m)
        mp['rank'] = i + 1
        mp['visits'] = m['b_cnt'] # Render as books
        top_peminjam[i] = mp
        
    return JsonResponse({
        'top_pengunjung': top_pengunjung,
        'top_peminjam': top_peminjam
    })

def export_excel(request):
    date_from, date_to = get_date_range(request)
    if _use_demo(): return JsonResponse({'error': 'Export not supported in demo mode'})
    return export_excel_response(date_from, date_to)

def export_pdf(request):
    date_from, date_to = get_date_range(request)
    if _use_demo(): return JsonResponse({'error': 'Export not supported in demo mode'})
    return export_pdf_response(date_from, date_to)
