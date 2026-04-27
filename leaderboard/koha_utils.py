import datetime
from django.db import connections
from django.conf import settings
from .models import PointPolicy, BadgeRule, SystemLog, PointTransaction
import time

def _get_role_from_category(categorycode):
    cat = (categorycode or '').upper()
    # Explicit mapping or sub-string detection
    student_cats = [c.upper() for c in getattr(settings, 'KOHA_STUDENT_CATEGORIES', [])]
    lecturer_cats = [c.upper() for c in getattr(settings, 'KOHA_LECTURER_CATEGORIES', [])]
    staff_cats = [c.upper() for c in getattr(settings, 'KOHA_STAFF_CATEGORIES', [])]
    
    if cat in student_cats or 'STD' in cat or 'MHS' in cat or cat == 'S' or 'MAHASISWA' in cat:
        return 'student'
    if cat in lecturer_cats or 'TC' in cat or 'DSN' in cat or cat == 'L' or 'DOSEN' in cat:
        return 'lecturer'
    if cat in staff_cats or 'STAF' in cat or 'TDK' in cat or 'LIB' in cat or 'PT' in cat or 'TENDIK' in cat or 'PEG' in cat or 'KAR' in cat:
        return 'staff'
    return 'unknown'

def _get_faculty_name(branchcode):
    if not branchcode or branchcode.upper() == 'PUSAT':
        return ''
    branch_map = getattr(settings, 'KOHA_BRANCH_FACULTY_MAP', {})
    return branch_map.get(branchcode, branchcode)

def _get_faculty_color(branchcode):
    # Mapping for colors based on branches
    branch_map = getattr(settings, 'KOHA_BRANCH_FACULTY_MAP', {})
    if not branch_map: return '#4da6ff'
    
    keys = list(branch_map.keys())
    colors = ['#4da6ff','#3de08a','#9b72ff','#ff6eb4','#ff914d','#f5c842','#ff5c5c','#41e0d0']
    
    try:
        idx = keys.index(branchcode)
        return colors[idx % len(colors)]
    except ValueError:
        return '#8892aa'

def _format_initials(name):
    parts = (name or '').split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    if name:
        return name[:2].upper()
    return '??'

def get_live_members(date_from, date_to, search_q=None):
    """
    Executes a direct query to Koha using memory aggregations.
    """
    start_time = time.time()
    date_to_plus_1 = date_to + datetime.timedelta(days=1)
    
    with connections['koha'].cursor() as cursor:
        params = [date_from, date_to_plus_1, date_from, date_to_plus_1, date_from, date_to_plus_1]
        
        # We group first internally, then join to borrowers. This is standard fast SQL.
        sql = """
        SELECT
            b.borrowernumber, b.cardnumber, b.firstname, b.surname, b.categorycode, b.branchcode, b.dateenrolled,
            IFNULL(v.visit_count, 0) as visit_count,
            IFNULL(i.issue_count, 0) + IFNULL(oi.old_issue_count, 0) as borrow_count
        FROM borrowers b
        LEFT JOIN (
            SELECT borrowernumber, COUNT(*) as visit_count 
            FROM statistics 
            WHERE datetime >= %s AND datetime < %s AND type IN ('issue', 'localuse', 'return') 
            GROUP BY borrowernumber
        ) v ON b.borrowernumber = v.borrowernumber
        LEFT JOIN (
            SELECT borrowernumber, COUNT(*) as issue_count 
            FROM issues 
            WHERE issuedate >= %s AND issuedate < %s 
            GROUP BY borrowernumber
        ) i ON b.borrowernumber = i.borrowernumber
        LEFT JOIN (
            SELECT borrowernumber, COUNT(*) as old_issue_count 
            FROM old_issues 
            WHERE issuedate >= %s AND issuedate < %s 
            GROUP BY borrowernumber
        ) oi ON b.borrowernumber = oi.borrowernumber
        """
        
        if search_q:
            sql += " WHERE b.firstname LIKE %s OR b.surname LIKE %s OR b.cardnumber LIKE %s"
            qs = f"%{search_q}%"
            params.extend([qs, qs, qs])
            
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
    duration = round((time.time() - start_time) * 1000, 2)
    
    # Try logging DB fetch
    try:
        SystemLog.objects.create(
            action="Koha Live Query (Members)",
            duration_ms=duration,
            details=f"Fetched {len(rows)} raw rows from Koha. Date range: {date_from} to {date_to}"
        )
    except Exception:
        pass

    members = []
    
    # Dynamic Point Policies
    try:
        vp_policy = PointPolicy.objects.filter(action_type='visit', is_active=True).first()
        bp_policy = PointPolicy.objects.filter(action_type='borrow', is_active=True).first()
        v_mult = vp_policy.points if vp_policy else 2
        b_mult = bp_policy.points if bp_policy else 5
    except Exception:
        v_mult, b_mult = 2, 5
        
    # Dynamic Badge Rules
    try:
        all_badges = list(BadgeRule.objects.all())
    except Exception:
        all_badges = []
        
    # Manual Points from Transactions
    try:
        from django.db.models import Sum
        pt_qs = PointTransaction.objects.values('cardnumber').annotate(total=Sum('amount'))
        local_points = {item['cardnumber']: item['total'] or 0 for item in pt_qs if item['cardnumber']}
    except Exception:
        local_points = {}
    
    for row in rows:
        borrowernumber, card, fname, sname, cat, branch, enrolled, v_cnt, b_cnt = row
        v_cnt = v_cnt or 0
        b_cnt = b_cnt or 0
        
        full_name = f"{(fname or '').strip()} {(sname or '').strip()}".strip() or str(card)
        role = _get_role_from_category(cat)
        
        if role == 'unknown':
            continue
            
        # Pengecualian (Exclude) untuk akun Statistical / Admin
        name_upper = full_name.upper()
        cat_upper = (cat or '').upper()
        if 'STATISTICAL' in name_upper or 'ADMIN' in name_upper or 'STAT' in cat_upper:
            continue
            
        # Only include active people, BUT always include staff and lecturer so they don't appear empty!
        if v_cnt == 0 and b_cnt == 0 and not search_q:
            if role == 'student':
                continue
        
        faculty = _get_faculty_name(branch)
        year_enrolled = enrolled.year if hasattr(enrolled, 'year') else ''
        
        visit_points = v_cnt * v_mult
        borrow_points = b_cnt * b_mult
        local_pt = local_points.get(str(card), 0)
        total_p = visit_points + borrow_points + local_pt

        # Calculate live badges dynamically!
        badges = []
        for br in all_badges:
            if br.criteria_type == 'visits_week' and v_cnt >= br.min_value:
                badges.append({'id': br.id_code, 'name': br.name, 'icon': br.icon, 'color': br.color, 'desc': br.desc})
            elif br.criteria_type == 'borrows_semester' and b_cnt >= br.min_value:
                badges.append({'id': br.id_code, 'name': br.name, 'icon': br.icon, 'color': br.color, 'desc': br.desc})

        if faculty:
            sub = f"{card} · {faculty}"
        else:
            sub = f"{card}"

        members.append({
            'id': str(card),
            'borrowernumber': borrowernumber,
            'name': full_name,
            'role': role,
            'faculty': faculty,
            'faculty_color': _get_faculty_color(branch),
            'initials': _format_initials(full_name),
            'visits': total_p, # used as total points rendering in JS
            'books': b_cnt,
            'streak': 0, # Cannot calculate streak reliably without querying specific dates
            'sub': sub,
            'badges': badges,
            'total_p': total_p,
            'v_cnt': v_cnt,
            'b_cnt': b_cnt
        })
        
    # Sort members by total points descending
    members.sort(key=lambda x: x['total_p'], reverse=True)
    
    # Assign Library Legend to top 10
    for i, m in enumerate(members[:10]):
        if m['total_p'] > 0:
            m['badges'].insert(0, {'id': 'library_legend', 'name': 'Library Legend', 'icon': '🥇', 'color': '#f1c40f', 'desc': 'Top 10 Klasemen!'})
            m['rank'] = i + 1
            
    return members

def get_live_member_detail(cardnumber, date_from, date_to):
    """
    Get full detail + recent checkout history for a specific patron
    """
    members = get_live_members(date_from, date_to, search_q=cardnumber)
    if not members:
        return None
        
    member = members[0]
    borrowernumber = member['borrowernumber']
    
    # Get recent borrowing history
    sql = """
        SELECT it.title, i.issuedate, i.date_due, 'borrowed' as status
        FROM issues i
        JOIN items im ON i.itemnumber = im.itemnumber JOIN biblio it ON im.biblionumber = it.biblionumber
        WHERE i.borrowernumber = %s
        UNION ALL
        SELECT it.title, oi.issuedate, oi.date_due, 'returned' as status
        FROM old_issues oi
        JOIN items im ON oi.itemnumber = im.itemnumber JOIN biblio it ON im.biblionumber = it.biblionumber
        WHERE oi.borrowernumber = %s
        ORDER BY issuedate DESC
        LIMIT 5
    """
    
    with connections['koha'].cursor() as cursor:
        cursor.execute(sql, [borrowernumber, borrowernumber])
        history_rows = cursor.fetchall()
        
    recent_borrows = []
    for title, issuedate, date_due, status in history_rows:
        dt = issuedate.strftime('%d %b %Y') if hasattr(issuedate, 'strftime') else str(issuedate)
        
        # Check overdue live
        if status == 'borrowed' and date_due:
            date_due_obj = date_due.date() if hasattr(date_due, 'date') else date_due
            if date_due_obj < datetime.date.today():
                status = 'overdue'
                
        recent_borrows.append({
            'title': (title or 'Unknown Book')[:40],
            'date': dt,
            'status': status
        })
        
    member['recent_borrows'] = recent_borrows
    member['visits_range'] = member['v_cnt']
    member['visits_total'] = member['v_cnt']
    member['books_range'] = member['b_cnt']
    member['books_total'] = member['b_cnt']
    
    return member

def get_live_faculties_stats(date_from, date_to):
    date_to_plus_1 = date_to + datetime.timedelta(days=1)
    
    # Dynamically find branches that have activity
    sql_visitors = """
        SELECT b.branchcode, COUNT(*) as visitors
        FROM statistics s JOIN borrowers b ON s.borrowernumber = b.borrowernumber 
        WHERE s.datetime >= %s AND s.datetime < %s AND s.type IN ('issue', 'localuse', 'return')
        GROUP BY b.branchcode
    """
    sql_books = """
        SELECT b.branchcode, COUNT(*) as books
        FROM issues i JOIN borrowers b ON i.borrowernumber = b.borrowernumber 
        WHERE i.issuedate >= %s AND i.issuedate < %s
        GROUP BY b.branchcode
    """
    
    with connections['koha'].cursor() as cursor:
        cursor.execute(sql_visitors, [date_from, date_to_plus_1])
        visit_rows = cursor.fetchall()
        
        cursor.execute(sql_books, [date_from, date_to_plus_1])
        book_rows = cursor.fetchall()

    branch_stats = {}
    for bcode, v in visit_rows:
        branch_stats[bcode] = {'visitors': v, 'books': 0}
    for bcode, b_cnt in book_rows:
        if bcode not in branch_stats: branch_stats[bcode] = {'visitors': 0, 'books': 0}
        branch_stats[bcode]['books'] += b_cnt
        
    stats = []
    # Try fetching real branch names from branches table
    branch_names = getattr(settings, 'KOHA_BRANCH_FACULTY_MAP', {})
    if not branch_names:
        try:
            with connections['koha'].cursor() as cursor:
                cursor.execute("SELECT branchcode, branchname FROM branches")
                branch_names = dict(cursor.fetchall())
        except Exception:
            pass
            
    for bcode, data in branch_stats.items():
        name = branch_names.get(bcode, bcode)
        
        # User requested to omit 'Pusat' (meaning main library general staff/students) as a faculty rank
        if not bcode or name.upper() == 'PUSAT':
            continue
            
        stats.append({
            'name': name,
            'code': bcode,
            'color': _get_faculty_color(bcode),
            'visitors': data['visitors'],
            'books': data['books']
        })
        
    stats.sort(key=lambda x: x['visitors'], reverse=True)
    return stats

def get_live_books_stats(date_from, date_to):
    date_to_plus_1 = date_to + datetime.timedelta(days=1)
    sql = """
    SELECT it.title, it.author, IFNULL(bi.itemtype, 'General'), 
           COUNT(*) as borrow_count 
    FROM issues i 
    JOIN items im ON i.itemnumber = im.itemnumber 
    JOIN biblio it ON im.biblionumber = it.biblionumber 
    LEFT JOIN biblioitems bi ON it.biblionumber = bi.biblionumber
    WHERE i.issuedate >= %s AND i.issuedate < %s
    GROUP BY it.biblionumber, it.title, it.author, bi.itemtype
    ORDER BY borrow_count DESC
    LIMIT 10
    """
    
    with connections['koha'].cursor() as cursor:
        cursor.execute(sql, [date_from, date_to_plus_1])
        rows = cursor.fetchall()
        
    books = []
    for i, (title, author, category, count) in enumerate(rows):
        books.append({
            'rank': i + 1,
            'title': (title or 'Unknown')[:100],
            'author': (author or 'Unknown')[:100],
            'category': category,
            'faculty': 'All Facilities',
            'borrows': count
        })
        
    return books
