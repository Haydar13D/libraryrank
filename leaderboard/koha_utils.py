import datetime
import hashlib
from django.db import connections
from django.conf import settings
from django.core.cache import cache
from .models import PointPolicy, BadgeRule, SystemLog, PointTransaction, LevelTier
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

def _get_satellite_visits(date_from, date_to_plus_1):
    """
    Ambil data kunjungan dari koha_satellite.visitorhistory menggunakan pymysql
    (kompatibel dengan MariaDB lama versi 10.1+).
    Returns: dict {cardnumber: visit_count}
    Hasil dicache 5 menit karena koneksi ke server eksternal paling lambat.
    """
    import pymysql

    # Cache key berdasarkan tanggal range
    cache_key = f"sat_visits_{date_from}_{date_to_plus_1}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        db = settings.DATABASES.get('satellite', {})
        conn = pymysql.connect(
            host=db.get('HOST', '10.12.0.7'),
            user=db.get('USER', 'pilot_satellite'),
            password=db.get('PASSWORD', ''),
            database=db.get('NAME', 'koha_satellite'),
            port=int(db.get('PORT', 3306)),
            charset='utf8mb4',
            connect_timeout=5,
        )
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT cardnumber, COUNT(*) as visit_count
                FROM visitorhistory
                WHERE visittime >= %s AND visittime < %s
                  AND cardnumber IS NOT NULL AND cardnumber != ''
                GROUP BY cardnumber
            """, [date_from, date_to_plus_1])
            result = {str(card).strip(): cnt for card, cnt in cursor.fetchall()}
        conn.close()
        cache.set(cache_key, result, 300)  # cache 5 menit
        return result
    except Exception:
        return {}


def get_live_members(date_from, date_to, search_q=None):
    """
    Executes a direct query to Koha using memory aggregations.
    Visit data is pulled from BOTH:
      1. koha_satellite.visitorhistory  (gate scanner — primary)
      2. koha.statistics                (circulation — secondary/fallback)
    Hasil di-cache 5 menit agar semua endpoint yang memanggil fungsi ini
    dalam satu periode tidak membebani database berulang kali.
    """
    # ── Cache layer ──────────────────────────────────────────────────────────
    cache_key = "lm_" + hashlib.md5(
        f"{date_from}|{date_to}|{search_q or ''}".encode()
    ).hexdigest()
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    # ─────────────────────────────────────────────────────────────────────────

    start_time = time.time()
    date_to_plus_1 = date_to + datetime.timedelta(days=1)

    # ── Step 1: Ambil data kunjungan dari Satellite (visitorhistory) ───────
    satellite_visits = _get_satellite_visits(date_from, date_to_plus_1)

    # ── Step 2: Ambil data dari Koha ──────────────────────────────────────
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
        
    # Dynamic Level Tiers
    try:
        tiers = list(LevelTier.objects.all().order_by('min_xp'))
    except Exception:
        tiers = []
        
    # Manual Points from Transactions
    try:
        from django.db.models import Sum, Count
        pt_qs = PointTransaction.objects.values('cardnumber', 'transaction_type').annotate(total=Sum('amount'), cnt=Count('id'))
        local_points = {}
        seminar_counts = {}
        for item in pt_qs:
            cnum = item['cardnumber']
            if not cnum: continue
            
            if cnum not in local_points:
                local_points[cnum] = 0
            local_points[cnum] += item['total'] or 0
            
            if item['transaction_type'] == 'seminar':
                seminar_counts[cnum] = item['cnt']
    except Exception:
        local_points = {}
        seminar_counts = {}
    
    for row in rows:
        borrowernumber, card, fname, sname, cat, branch, enrolled, v_cnt, b_cnt = row
        v_cnt = v_cnt or 0
        b_cnt = b_cnt or 0

        # Gabungkan kunjungan dari satellite (gate scan) + Koha statistics
        # Ambil mana yang lebih besar (gate scan biasanya lebih banyak)
        card_str = str(card).strip() if card else ''
        sat_v_cnt = satellite_visits.get(card_str, 0)
        v_cnt = max(v_cnt, sat_v_cnt)

        full_name = f"{(fname or '').strip()} {(sname or '').strip()}".strip() or str(card)
        role = _get_role_from_category(cat)
        
        if role == 'unknown':
            continue
            
        # Pengecualian (Exclude) untuk akun Statistical / Admin
        name_upper = full_name.upper()
        cat_upper = (cat or '').upper()
        if 'STATISTICAL' in name_upper or 'ADMIN' in name_upper or 'STAT' in cat_upper:
            continue
            
        faculty = _get_faculty_name(branch)
        year_enrolled = enrolled.year if hasattr(enrolled, 'year') else ''
        
        visit_points = v_cnt * v_mult
        borrow_points = b_cnt * b_mult
        local_pt = local_points.get(str(card), 0)
        total_p = visit_points + borrow_points + local_pt

        # Only include active people (with any library activity or local points), BUT always include staff and lecturer!
        if v_cnt == 0 and b_cnt == 0 and sat_v_cnt == 0 and local_pt == 0 and not search_q:
            if role == 'student':
                continue

        # Calculate live badges dynamically!
        badges = []
        for br in all_badges:
            if br.criteria_type == 'visits_week' and v_cnt >= br.min_value:
                badges.append({'id': br.id_code, 'name': br.name, 'icon': br.icon, 'color': br.color, 'desc': br.desc, 'image_url': br.image_url})
            elif br.criteria_type == 'borrows_semester' and b_cnt >= br.min_value:
                badges.append({'id': br.id_code, 'name': br.name, 'icon': br.icon, 'color': br.color, 'desc': br.desc, 'image_url': br.image_url})

        if faculty:
            sub = f"{card} · {faculty}"
        else:
            sub = f"{card}"

        s_cnt = seminar_counts.get(str(card), 0)

        # Calculate level dynamically based on total_p
        member_level = {'name': 'Visitor', 'level_num': 1, 'current_xp': total_p, 'min_xp': 0, 'max_xp': 100, 'progress_perc': 0, 'color': '#95a5a6'}
        if tiers:
            found = False
            for tier in tiers:
                if tier.max_xp is None or total_p <= tier.max_xp:
                    progress = 100
                    if tier.max_xp is not None:
                        denom = max(1, tier.max_xp - tier.min_xp)
                        progress = int(((total_p - tier.min_xp) / denom) * 100)
                    member_level = {
                        'name': tier.name,
                        'level_num': tier.level_num,
                        'current_xp': total_p,
                        'min_xp': tier.min_xp,
                        'max_xp': tier.max_xp if tier.max_xp is not None else total_p,
                        'progress_perc': min(100, progress),
                        'color': tier.color
                    }
                    found = True
                    break
            if not found:
                highest = tiers[-1]
                member_level = {
                    'name': highest.name, 'level_num': highest.level_num, 'current_xp': total_p, 
                    'min_xp': highest.min_xp, 'max_xp': total_p, 'progress_perc': 100, 'color': highest.color
                }

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
            'level': member_level,
            'total_p': total_p,
            'v_cnt': v_cnt,
            'b_cnt': b_cnt,
            's_cnt': s_cnt
        })
        
    # Sort members by total points descending
    members.sort(key=lambda x: x['total_p'], reverse=True)
    
    # Assign Library Legend to top 10
    for i, m in enumerate(members[:10]):
        if m['total_p'] > 0:
            m['badges'].insert(0, {'id': 'library_legend', 'name': 'Library Legend', 'icon': '🥇', 'color': '#f1c40f', 'desc': 'Top 10 Klasemen!', 'image_url': '/static/img/badges/top 10 leaderboard.png'})
            m['rank'] = i + 1

    # Simpan ke cache 5 menit
    cache.set(cache_key, members, 300)
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


def get_live_daily_visits(date_from, date_to, live_members, is_filtered=False):
    """
    Calculate daily visits (Monday to Sunday) using real data from:
      1. koha_satellite.visitorhistory (primary gate scan logs)
      2. koha.statistics (fallback circulation logs)
    Returns a list of 7 integers representing visits from Senin (Index 0) to Minggu (Index 6).
    """
    import pymysql
    date_to_plus_1 = date_to + datetime.timedelta(days=1)
    
    daily_counts = [0] * 7 # Index 0=Senin, ..., 6=Minggu
    
    if not live_members and is_filtered:
        return daily_counts
        
    # Koha statistics query
    koha_sql = """
        SELECT DAYOFWEEK(datetime) as dow, COUNT(*) as cnt
        FROM statistics
        WHERE datetime >= %s AND datetime < %s
          AND type IN ('issue', 'localuse', 'return')
    """
    koha_params = [date_from, date_to_plus_1]
    
    # Satellite visitorhistory query
    sat_sql = """
        SELECT DAYOFWEEK(visittime) as dow, COUNT(*) as cnt
        FROM visitorhistory
        WHERE visittime >= %s AND visittime < %s
    """
    sat_params = [date_from, date_to_plus_1]
    
    # If filtered by search query and the list is not too large
    if is_filtered and len(live_members) < 2000:
        bnums = [m['borrowernumber'] for m in live_members if m.get('borrowernumber')]
        cards = [m['id'] for m in live_members if m.get('id')]
        
        if bnums:
            koha_sql += " AND borrowernumber IN ({})".format(",".join(["%s"] * len(bnums)))
            koha_params.extend(bnums)
        else:
            koha_sql += " AND 1=0"
            
        if cards:
            sat_sql += " AND cardnumber IN ({})".format(",".join(["%s"] * len(cards)))
            sat_params.extend(cards)
        else:
            sat_sql += " AND 1=0"
            
    koha_sql += " GROUP BY dow"
    sat_sql += " GROUP BY dow"
    
    # Run Koha query
    koha_result = {}
    try:
        with connections['koha'].cursor() as cursor:
            cursor.execute(koha_sql, koha_params)
            koha_result = {row[0]: row[1] for row in cursor.fetchall()}
    except Exception:
        pass
        
    # Run Satellite query
    sat_result = {}
    try:
        db = settings.DATABASES.get('satellite', {})
        conn = pymysql.connect(
            host=db.get('HOST', '10.12.0.7'),
            user=db.get('USER', 'pilot_satellite'),
            password=db.get('PASSWORD', ''),
            database=db.get('NAME', 'koha_satellite'),
            port=int(db.get('PORT', 3306)),
            charset='utf8mb4',
            connect_timeout=5,
        )
        with conn.cursor() as cursor:
            cursor.execute(sat_sql, sat_params)
            sat_result = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
    except Exception:
        pass
        
    # Combine results: take the max of gate scans or statistics for each day of the week
    for dow in range(1, 8):
        k_val = koha_result.get(dow, 0)
        s_val = sat_result.get(dow, 0)
        max_val = max(k_val, s_val)
        
        idx = (dow - 2) % 7
        daily_counts[idx] = max_val
        
    return daily_counts
