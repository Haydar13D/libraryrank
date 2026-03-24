from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import date, timedelta

from .models import Member, Faculty, Book, Visit, BorrowRecord
from .exports import export_excel_response, export_pdf_response
from .demo_data import DEMO_DATA   # fallback when DB is empty


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def get_date_range(request):
    today = date.today()
    first = today.replace(day=1)
    try:
        date_from = date.fromisoformat(request.GET.get('date_from', first.isoformat()))
        date_to   = date.fromisoformat(request.GET.get('date_to',   today.isoformat()))
    except ValueError:
        date_from, date_to = first, today
    return date_from, date_to


def _use_demo():
    """Return True if no real data exists yet (fresh install / demo mode)."""
    return not Member.objects.filter(is_active=True).exists()


def _initials(name):
    parts = name.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper()


def _sub(member):
    if member.role == 'student':
        fac = member.faculty.name if member.faculty else 'Unknown'
        return f"{fac} · {member.year_enrolled or ''}"
    elif member.role == 'lecturer':
        fac = member.faculty.name if member.faculty else 'Unknown'
        return f"{fac} · {member.title}"
    return f"{member.department} · {member.title or 'Staff'}"


def _member_dict(member, visit_count, borrow_count):
    return {
        'id':       member.member_id,
        'name':     member.name,
        'role':     member.role,
        'faculty':  member.faculty.name if member.faculty else member.department,
        'faculty_color': member.faculty.color if member.faculty else '#8892aa',
        'initials': _initials(member.name),
        'visits':   visit_count,
        'books':    borrow_count,
        'streak':   member.streak_days,
        'sub':      _sub(member),
        'title':    member.title,
        'year':     member.year_enrolled,
        'dept':     member.department,
    }


# ─────────────────────────────────────────────
# PAGE VIEW
# ─────────────────────────────────────────────

def index(request):
    date_from, date_to = get_date_range(request)
    return render(request, 'leaderboard/index.html', {
        'date_from': date_from.isoformat(),
        'date_to':   date_to.isoformat(),
        'search_q':  request.GET.get('q', ''),
    })


# ─────────────────────────────────────────────
# API: OVERVIEW
# ─────────────────────────────────────────────

def api_overview(request):
    if _use_demo():
        return JsonResponse(DEMO_DATA['overview'])

    date_from, date_to = get_date_range(request)
    q = request.GET.get('q', '').strip()

    members_qs = Member.objects.filter(is_active=True)
    if q:
        members_qs = members_qs.filter(
            Q(name__icontains=q) | Q(member_id__icontains=q) |
            Q(faculty__name__icontains=q) | Q(department__icontains=q)
        )

    members = members_qs.annotate(
        visit_total=Count('visits', filter=Q(
            visits__visited_at__gte=date_from,
            visits__visited_at__lt=date_to + timedelta(days=1)
        )),
        borrow_total=Count('borrow_records', filter=Q(
            borrow_records__borrowed_at__gte=date_from,
            borrow_records__borrowed_at__lt=date_to + timedelta(days=1)
        ))
    ).filter(visit_total__gt=0).order_by('-visit_total')[:15]

    leaderboard = [
        dict(_member_dict(m, m.visit_total, m.borrow_total), rank=i+1)
        for i, m in enumerate(members)
    ]

    nominations = {}
    for role in ['student', 'lecturer', 'staff']:
        top = Member.objects.filter(role=role, is_active=True).annotate(
            visit_total=Count('visits', filter=Q(
                visits__visited_at__gte=date_from,
                visits__visited_at__lt=date_to + timedelta(days=1)
            ))
        ).order_by('-visit_total').first()
        if top:
            nominations[role] = _member_dict(top, top.visit_total, 0)

    total_visitors = Visit.objects.filter(
        visited_at__gte=date_from, visited_at__lt=date_to + timedelta(days=1)
    ).count()

    return JsonResponse({
        'leaderboard': leaderboard,
        'nominations': nominations,
        'stats': {
            'total_visitors':  total_visitors,
            'total_books':     BorrowRecord.objects.filter(borrowed_at__gte=date_from, borrowed_at__lt=date_to + timedelta(days=1)).count(),
            'active_members':  Member.objects.filter(visits__visited_at__gte=date_from, visits__visited_at__lt=date_to + timedelta(days=1), is_active=True).distinct().count(),
            'total_faculties': Faculty.objects.count(),
        }
    })


# ─────────────────────────────────────────────
# API: ROLE LEADERBOARD
# ─────────────────────────────────────────────

def api_role_leaderboard(request, role):
    if _use_demo():
        return JsonResponse(DEMO_DATA.get(f'role_{role}', {'leaderboard': []}))

    date_from, date_to = get_date_range(request)
    q = request.GET.get('q', '').strip()

    qs = Member.objects.filter(role=role, is_active=True)
    if q:
        qs = qs.filter(
            Q(name__icontains=q) | Q(member_id__icontains=q) |
            Q(faculty__name__icontains=q) | Q(department__icontains=q)
        )

    members = qs.annotate(
        visit_total=Count('visits', filter=Q(
            visits__visited_at__gte=date_from,
            visits__visited_at__lt=date_to + timedelta(days=1)
        )),
        borrow_total=Count('borrow_records', filter=Q(
            borrow_records__borrowed_at__gte=date_from,
            borrow_records__borrowed_at__lt=date_to + timedelta(days=1)
        ))
    ).order_by('-visit_total')[:20]

    leaderboard = [
        dict(_member_dict(m, m.visit_total, m.borrow_total), rank=i+1)
        for i, m in enumerate(members)
    ]
    return JsonResponse({'leaderboard': leaderboard})


# ─────────────────────────────────────────────
# API: BOOKS
# ─────────────────────────────────────────────

def api_books(request):
    if _use_demo():
        return JsonResponse(DEMO_DATA['books'])

    date_from, date_to = get_date_range(request)
    q = request.GET.get('q', '').strip()

    books_qs = Book.objects.annotate(
        borrow_total=Count('borrow_records', filter=Q(
            borrow_records__borrowed_at__gte=date_from,
            borrow_records__borrowed_at__lt=date_to + timedelta(days=1)
        ))
    ).filter(borrow_total__gt=0).order_by('-borrow_total')[:10]
    if q:
        books_qs = books_qs.filter(Q(title__icontains=q) | Q(author__icontains=q))

    books = [{'rank': i+1, 'title': b.title, 'author': b.author,
               'category': b.category, 'faculty': b.faculty.name if b.faculty else '',
               'borrows': b.borrow_total} for i, b in enumerate(books_qs)]

    borrowers_qs = Member.objects.filter(is_active=True).annotate(
        borrow_total=Count('borrow_records', filter=Q(
            borrow_records__borrowed_at__gte=date_from,
            borrow_records__borrowed_at__lt=date_to + timedelta(days=1)
        ))
    ).filter(borrow_total__gt=0).order_by('-borrow_total')[:8]

    borrowers = [
        dict(_member_dict(m, m.borrow_total, m.borrow_total), rank=i+1, visits=m.borrow_total)
        for i, m in enumerate(borrowers_qs)
    ]
    return JsonResponse({'books': books, 'borrowers': borrowers})


# ─────────────────────────────────────────────
# API: FACULTIES
# ─────────────────────────────────────────────

def api_faculties(request):
    if _use_demo():
        return JsonResponse(DEMO_DATA['faculties'])

    date_from, date_to = get_date_range(request)

    faculties = Faculty.objects.annotate(
        visitor_count=Count('members__visits', filter=Q(
            members__visits__visited_at__gte=date_from,
            members__visits__visited_at__lt=date_to + timedelta(days=1)
        )),
        book_count=Count('members__borrow_records', filter=Q(
            members__borrow_records__borrowed_at__gte=date_from,
            members__borrow_records__borrowed_at__lt=date_to + timedelta(days=1)
        ))
    ).order_by('-visitor_count')

    fac_data = [{'name': f.name, 'code': f.code, 'color': f.color,
                  'visitors': f.visitor_count, 'books': f.book_count}
                for f in faculties]

    top_per_faculty = []
    for fac in Faculty.objects.all():
        top = Member.objects.filter(faculty=fac, role='student', is_active=True).annotate(
            visit_total=Count('visits', filter=Q(
                visits__visited_at__gte=date_from,
                visits__visited_at__lt=date_to + timedelta(days=1)
            ))
        ).order_by('-visit_total').first()
        if top and top.visit_total > 0:
            top_per_faculty.append({
                'faculty': fac.name, 'faculty_color': fac.color,
                'name': top.name, 'initials': _initials(top.name),
                'visits': top.visit_total, 'role': 'student',
            })

    top_per_faculty.sort(key=lambda x: x['visits'], reverse=True)
    return JsonResponse({'faculties': fac_data, 'top_per_faculty': top_per_faculty})


# ─────────────────────────────────────────────
# API: MEMBER DETAIL
# ─────────────────────────────────────────────

def api_member_detail(request, member_id):
    if _use_demo():
        all_p = (DEMO_DATA['overview']['leaderboard'] +
                 DEMO_DATA.get('role_student', {}).get('leaderboard', []))
        p = next((x for x in all_p if x['id'] == member_id), None)
        if not p:
            return JsonResponse({'error': 'Not found'}, status=404)
        
        # Add a dummy badge for demo purposes
        dummy_badge = [{'id': 'weekly_warrior', 'name': 'Weekly Warrior', 'icon': '🥈', 'color': '#bdc3c7', 'desc': 'Datang ke perpus 3x dalam seminggu'}]
        
        return JsonResponse({**p, 'visits_range': p['visits'], 'visits_total': p['visits'],
                              'books_range': p['books'], 'books_total': p['books'],
                              'badges': dummy_badge if p.get('visits', 0) > 80 else [],
                              'recent_borrows': []})

    date_from, date_to = get_date_range(request)
    m = get_object_or_404(Member, member_id=member_id)

    recent = m.borrow_records.select_related('book').order_by('-borrowed_at')[:5]
    return JsonResponse({
        'id':           m.member_id,
        'name':         m.name,
        'role':         m.role,
        'faculty':      m.faculty.name if m.faculty else '',
        'department':   m.department,
        'title':        m.title,
        'year':         m.year_enrolled,
        'initials':     _initials(m.name),
        'faculty_color': m.faculty.color if m.faculty else '#8892aa',
        'visits_range': m.visit_count_in_range(date_from, date_to),
        'visits_total': m.visit_count,
        'books_range':  m.borrow_count_in_range(date_from, date_to),
        'books_total':  m.borrow_count,
        'streak':       m.streak_days,
        'sub':          _sub(m),
        'badges':       m.badges,
        'recent_borrows': [
            {'title': r.book.title, 'date': r.borrowed_at.strftime('%d %b %Y'), 'status': r.status}
            for r in recent
        ],
    })


# ─────────────────────────────────────────────
# API: PEMUSTAKA TERAKTIF (DUAL LIST)
# ─────────────────────────────────────────────

def api_pemustaka_teraktif(request):
    if _use_demo():
        from .demo_data import _STUDENTS, _LECTURERS, _STAFF, _ALL
        role_param = request.GET.get('role', 'all').lower()
        role_map = {
            'mahasiswa': 'student', 'dosen': 'lecturer', 'tendik': 'staff',
            'student': 'student', 'lecturer': 'lecturer', 'staff': 'staff'
        }
        role = role_map.get(role_param, 'all')
        if role == 'student':
            pool = _STUDENTS
        elif role == 'lecturer':
            pool = _LECTURERS
        elif role == 'staff':
            pool = _STAFF
        else:
            pool = _ALL
            
        top_pengunjung = sorted(pool, key=lambda x: x['visits'], reverse=True)[:10]
        top_peminjam = sorted(pool, key=lambda x: x['books'], reverse=True)[:10]
        
        return JsonResponse({
            'top_pengunjung': [dict(p, rank=i+1) for i, p in enumerate(top_pengunjung)],
            'top_peminjam': [dict(p, rank=i+1) for i, p in enumerate(top_peminjam)]
        })

    year_str = request.GET.get('year', str(timezone.now().year))
    try:
        year = int(year_str)
        date_from = date(year, 1, 1)
        date_to = date(year, 12, 31)
    except ValueError:
        date_from, date_to = get_date_range(request)

    role_param = request.GET.get('role', 'all').lower()
    
    role_map = {
        'mahasiswa': 'student',
        'dosen': 'lecturer',
        'tendik': 'staff',
        'student': 'student',
        'lecturer': 'lecturer',
        'staff': 'staff'
    }

    base_qs = Member.objects.filter(is_active=True)
    if role_param in role_map:
        base_qs = base_qs.filter(role=role_map[role_param])

    visitors_qs = base_qs.annotate(
        visit_total=Count('visits', filter=Q(
            visits__visited_at__gte=date_from,
            visits__visited_at__lt=date_to + timedelta(days=1)
        ))
    ).filter(visit_total__gt=0).order_by('-visit_total')[:10]

    borrowers_qs = base_qs.annotate(
        borrow_total=Count('borrow_records', filter=Q(
            borrow_records__borrowed_at__gte=date_from,
            borrow_records__borrowed_at__lt=date_to + timedelta(days=1)
        ))
    ).filter(borrow_total__gt=0).order_by('-borrow_total')[:10]

    top_pengunjung = [
        dict(_member_dict(m, m.visit_total, m.borrow_count), rank=i+1)
        for i, m in enumerate(visitors_qs)
    ]
    
    top_peminjam = [
        dict(_member_dict(m, m.visit_count, m.borrow_total), rank=i+1)
        for i, m in enumerate(borrowers_qs)
    ]

    return JsonResponse({
        'top_pengunjung': top_pengunjung,
        'top_peminjam': top_peminjam
    })


# ─────────────────────────────────────────────
# EXPORTS
# ─────────────────────────────────────────────

def export_excel(request):
    date_from, date_to = get_date_range(request)
    if _use_demo():
        from .exports import export_demo_excel
        return export_demo_excel()
    return export_excel_response(date_from, date_to)


def export_pdf(request):
    date_from, date_to = get_date_range(request)
    if _use_demo():
        from .exports import export_demo_pdf
        return export_demo_pdf()
    return export_pdf_response(date_from, date_to)
