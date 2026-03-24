"""
Fallback demo data — shown when the database is empty.
Once you run `python manage.py sync_from_koha` or `seed_demo_data`,
real data from MySQL takes over automatically.
"""

_STUDENTS = [
    {'id':'S001','name':'Ahmad Zulkifli','faculty':'Computer Science','year':2021,'visits':128,'books':24,'streak':14,'initials':'AZ','role':'student','sub':'Computer Science · 2021','faculty_color':'#4da6ff'},
    {'id':'S002','name':'Putri Maharani','faculty':'Medicine','year':2022,'visits':115,'books':31,'streak':9,'initials':'PM','role':'student','sub':'Medicine · 2022','faculty_color':'#9b72ff'},
    {'id':'S003','name':'Rizky Pratama','faculty':'Engineering','year':2020,'visits':108,'books':19,'streak':7,'initials':'RP','role':'student','sub':'Engineering · 2020','faculty_color':'#3de08a'},
    {'id':'S004','name':'Sari Dewi Kusuma','faculty':'Economics','year':2021,'visits':97,'books':22,'streak':11,'initials':'SD','role':'student','sub':'Economics · 2021','faculty_color':'#ff6eb4'},
    {'id':'S005','name':'Fajar Hidayat','faculty':'Law','year':2023,'visits':89,'books':15,'streak':5,'initials':'FH','role':'student','sub':'Law · 2023','faculty_color':'#ff914d'},
    {'id':'S006','name':'Nadia Anggraeni','faculty':'Psychology','year':2022,'visits':82,'books':28,'streak':6,'initials':'NA','role':'student','sub':'Psychology · 2022','faculty_color':'#f5c842'},
    {'id':'S007','name':'Dimas Saputra','faculty':'Architecture','year':2021,'visits':75,'books':13,'streak':4,'initials':'DS','role':'student','sub':'Architecture · 2021','faculty_color':'#ff5c5c'},
    {'id':'S008','name':'Lestari Wahyu','faculty':'Biology','year':2023,'visits':68,'books':17,'streak':8,'initials':'LW','role':'student','sub':'Biology · 2023','faculty_color':'#41e0d0'},
    {'id':'S009','name':'Bagus Santoso','faculty':'Computer Science','year':2020,'visits':61,'books':20,'streak':3,'initials':'BS','role':'student','sub':'Computer Science · 2020','faculty_color':'#4da6ff'},
    {'id':'S010','name':'Yuni Astuti','faculty':'Engineering','year':2022,'visits':54,'books':11,'streak':2,'initials':'YA','role':'student','sub':'Engineering · 2022','faculty_color':'#3de08a'},
]

_LECTURERS = [
    {'id':'L001','name':'Dr. Siti Rahayu','faculty':'Engineering','title':'Associate Prof.','visits':94,'books':18,'streak':21,'initials':'SR','role':'lecturer','sub':'Engineering · Associate Prof.','faculty_color':'#3de08a'},
    {'id':'L002','name':'Prof. Eko Budiman','faculty':'Medicine','title':'Professor','visits':87,'books':25,'streak':18,'initials':'EB','role':'lecturer','sub':'Medicine · Professor','faculty_color':'#9b72ff'},
    {'id':'L003','name':'Dr. Anwar Hasan','faculty':'Law','title':'Lecturer','visits':79,'books':12,'streak':15,'initials':'AH','role':'lecturer','sub':'Law · Lecturer','faculty_color':'#ff914d'},
    {'id':'L004','name':'Dr. Rina Sulistyo','faculty':'Economics','title':'Associate Prof.','visits':71,'books':20,'streak':10,'initials':'RS','role':'lecturer','sub':'Economics · Associate Prof.','faculty_color':'#ff6eb4'},
    {'id':'L005','name':'Dr. Yudha Nugraha','faculty':'Computer Science','title':'Lecturer','visits':65,'books':9,'streak':8,'initials':'YN','role':'lecturer','sub':'Computer Science · Lecturer','faculty_color':'#4da6ff'},
    {'id':'L006','name':'Prof. Dewi Santika','faculty':'Psychology','title':'Professor','visits':58,'books':22,'streak':12,'initials':'DS','role':'lecturer','sub':'Psychology · Professor','faculty_color':'#f5c842'},
    {'id':'L007','name':'Dr. Hafiz Ramadhan','faculty':'Architecture','title':'Lecturer','visits':50,'books':7,'streak':5,'initials':'HR','role':'lecturer','sub':'Architecture · Lecturer','faculty_color':'#ff5c5c'},
]

_STAFF = [
    {'id':'ST001','name':'Budi Hartono','faculty':'Administration','dept':'Administration','title':'Senior Staff','visits':76,'books':5,'streak':30,'initials':'BH','role':'staff','sub':'Administration · Senior Staff','faculty_color':'#8892aa'},
    {'id':'ST002','name':'Wati Lestari','faculty':'Cataloging','dept':'Cataloging','title':'Librarian','visits':68,'books':8,'streak':25,'initials':'WL','role':'staff','sub':'Cataloging · Librarian','faculty_color':'#8892aa'},
    {'id':'ST003','name':'Agus Priyono','faculty':'IT Support','dept':'IT Support','title':'Staff','visits':59,'books':4,'streak':18,'initials':'AP','role':'staff','sub':'IT Support · Staff','faculty_color':'#8892aa'},
    {'id':'ST004','name':'Erna Susanti','faculty':'Reference','dept':'Reference','title':'Senior Librarian','visits':51,'books':11,'streak':22,'initials':'ES','role':'staff','sub':'Reference · Senior Librarian','faculty_color':'#8892aa'},
    {'id':'ST005','name':'Joko Widodo','faculty':'Circulation','dept':'Circulation','title':'Staff','visits':43,'books':3,'streak':14,'initials':'JW','role':'staff','sub':'Circulation · Staff','faculty_color':'#8892aa'},
]

_BOOKS = [
    {'title':'Introduction to Algorithms','author':'Cormen et al.','category':'Computer Science','borrows':47},
    {'title':'Principles of Economics','author':'N. Gregory Mankiw','category':'Economics','borrows':39},
    {"title":"Gray's Anatomy",'author':'Henry Gray','category':'Medicine','borrows':35},
    {'title':"Black's Law Dictionary",'author':'Henry Black','category':'Law','borrows':31},
    {'title':'Structural Analysis','author':'R.C. Hibbeler','category':'Engineering','borrows':28},
    {'title':'Psychology','author':'David Myers','category':'Psychology','borrows':24},
    {'title':'Calculus: Early Transcendentals','author':'James Stewart','category':'Mathematics','borrows':22},
    {'title':'Organic Chemistry','author':'John McMurry','category':'Chemistry','borrows':19},
]

_FACULTIES = [
    {'name':'Computer Science','code':'CS','color':'#4da6ff','visitors':284,'books':156},
    {'name':'Engineering','code':'ENG','color':'#3de08a','visitors':241,'books':129},
    {'name':'Medicine','code':'MED','color':'#9b72ff','visitors':228,'books':187},
    {'name':'Economics','code':'ECO','color':'#ff6eb4','visitors':195,'books':98},
    {'name':'Law','code':'LAW','color':'#ff914d','visitors':167,'books':71},
    {'name':'Psychology','code':'PSY','color':'#f5c842','visitors':143,'books':88},
    {'name':'Architecture','code':'ARC','color':'#ff5c5c','visitors':118,'books':54},
    {'name':'Biology','code':'BIO','color':'#41e0d0','visitors':101,'books':67},
]

_ALL = sorted(_STUDENTS + _LECTURERS + _STAFF, key=lambda x: x['visits'], reverse=True)

_TOP_PER_FAC = []
for _fac in _FACULTIES:
    _studs = [s for s in _STUDENTS if s['faculty'] == _fac['name']]
    if _studs:
        _top = max(_studs, key=lambda x: x['visits'])
        _TOP_PER_FAC.append({
            'faculty': _fac['name'], 'faculty_color': _fac['color'],
            'name': _top['name'], 'initials': _top['initials'],
            'visits': _top['visits'], 'role': 'student',
        })

_BORROWERS = sorted(_STUDENTS + _LECTURERS, key=lambda x: x['books'], reverse=True)[:8]

DEMO_DATA = {
    'overview': {
        'leaderboard': [dict(p, rank=i+1) for i, p in enumerate(_ALL[:15])],
        'nominations': {
            'student':  _STUDENTS[0],
            'lecturer': _LECTURERS[0],
            'staff':    _STAFF[0],
        },
        'stats': {
            'total_visitors': 2847,
            'total_books':    512,
            'active_members': 189,
            'total_faculties': 8,
        },
    },
    'role_student':  {'leaderboard': [dict(p, rank=i+1) for i, p in enumerate(_STUDENTS)]},
    'role_lecturer': {'leaderboard': [dict(p, rank=i+1) for i, p in enumerate(_LECTURERS)]},
    'role_staff':    {'leaderboard': [dict(p, rank=i+1) for i, p in enumerate(_STAFF)]},
    'books': {
        'books':     [dict(b, rank=i+1) for i, b in enumerate(_BOOKS)],
        'borrowers': [dict(p, rank=i+1, visits=p['books']) for i, p in enumerate(_BORROWERS)],
    },
    'faculties': {
        'faculties':       _FACULTIES,
        'top_per_faculty': _TOP_PER_FAC,
    },
}
