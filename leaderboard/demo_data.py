"""
Fallback demo data — ditampilkan saat koneksi ke Koha tidak tersedia.
Data ini menggunakan nama, NIM, dan fakultas Indonesia yang realistis.
"""

# visits = jumlah raw (akan dikali 15 menjadi XP oleh _add_level)
# books  = jumlah buku dipinjam semester ini

_STUDENTS = [
    {'id':'L202201001','name':'Ahmad Fauzi Ramadhan',    'faculty':'Ilmu Komputer',           'year':2022,'visits':28,'books':12,'streak':14,'initials':'AF','role':'student','sub':'Ilmu Komputer · 2022','faculty_color':'#4da6ff'},
    {'id':'L202102001','name':'Siti Nurhaliza Putri',    'faculty':'Kedokteran',               'year':2021,'visits':25,'books':18,'streak':9, 'initials':'SN','role':'student','sub':'Kedokteran · 2021','faculty_color':'#9b72ff'},
    {'id':'L202201002','name':'Rizky Maulana Akbar',     'faculty':'Teknik',                   'year':2022,'visits':23,'books':9, 'streak':7, 'initials':'RM','role':'student','sub':'Teknik · 2022','faculty_color':'#3de08a'},
    {'id':'L202304001','name':'Dewi Ayu Lestari',        'faculty':'Ekonomi dan Bisnis',       'year':2023,'visits':21,'books':14,'streak':11,'initials':'DA','role':'student','sub':'Ekonomi dan Bisnis · 2023','faculty_color':'#ff6eb4'},
    {'id':'L202105001','name':'Muhammad Hafiz Ibrahim',  'faculty':'Hukum',                    'year':2021,'visits':20,'books':7, 'streak':5, 'initials':'MH','role':'student','sub':'Hukum · 2021','faculty_color':'#ff914d'},
    {'id':'L202206001','name':'Anisa Rahma Fitriani',    'faculty':'Psikologi',                'year':2022,'visits':18,'books':11,'streak':6, 'initials':'AR','role':'student','sub':'Psikologi · 2022','faculty_color':'#f5c842'},
    {'id':'L202001001','name':'Dimas Arya Kusuma',       'faculty':'Teknik',                   'year':2020,'visits':17,'books':8, 'streak':4, 'initials':'DA','role':'student','sub':'Teknik · 2020','faculty_color':'#3de08a'},
    {'id':'L202302001','name':'Fajar Nurfadillah',       'faculty':'Ilmu Komputer',            'year':2023,'visits':16,'books':6, 'streak':3, 'initials':'FN','role':'student','sub':'Ilmu Komputer · 2023','faculty_color':'#4da6ff'},
    {'id':'L202203001','name':'Laila Nur Aini',          'faculty':'Kedokteran',               'year':2022,'visits':15,'books':15,'streak':3, 'initials':'LN','role':'student','sub':'Kedokteran · 2022','faculty_color':'#9b72ff'},
    {'id':'L202104001','name':'Bagas Prasetyo Utomo',    'faculty':'Ekonomi dan Bisnis',       'year':2021,'visits':14,'books':10,'streak':2, 'initials':'BP','role':'student','sub':'Ekonomi dan Bisnis · 2021','faculty_color':'#ff6eb4'},
    {'id':'L202306001','name':'Cindy Permata Sari',      'faculty':'Psikologi',                'year':2023,'visits':13,'books':8, 'streak':2, 'initials':'CP','role':'student','sub':'Psikologi · 2023','faculty_color':'#f5c842'},
    {'id':'L202005001','name':'Evan Drajat Wicaksana',   'faculty':'Hukum',                    'year':2020,'visits':12,'books':5, 'streak':2, 'initials':'ED','role':'student','sub':'Hukum · 2020','faculty_color':'#ff914d'},
    {'id':'L202207001','name':'Galih Setiawan Nugroho',  'faculty':'Pertanian',                'year':2022,'visits':11,'books':7, 'streak':1, 'initials':'GS','role':'student','sub':'Pertanian · 2022','faculty_color':'#41e0d0'},
    {'id':'L202108001','name':'Hana Safitri Rahayu',     'faculty':'Ilmu Sosial dan Ilmu Politik','year':2021,'visits':10,'books':9,'streak':1,'initials':'HS','role':'student','sub':'FISIP · 2021','faculty_color':'#ff5c5c'},
    {'id':'L202002001','name':'Irfan Mauludi Santoso',   'faculty':'Ilmu Komputer',            'year':2020,'visits':9, 'books':4, 'streak':1, 'initials':'IM','role':'student','sub':'Ilmu Komputer · 2020','faculty_color':'#4da6ff'},
    {'id':'L202301001','name':'Joko Prasetyo Budi',      'faculty':'Teknik',                   'year':2023,'visits':8, 'books':3, 'streak':1, 'initials':'JP','role':'student','sub':'Teknik · 2023','faculty_color':'#3de08a'},
    {'id':'L202103001','name':'Karina Astuti Wulandari', 'faculty':'Kedokteran',               'year':2021,'visits':8, 'books':13,'streak':1, 'initials':'KA','role':'student','sub':'Kedokteran · 2021','faculty_color':'#9b72ff'},
    {'id':'L202204001','name':'Luqman Hakim Salim',      'faculty':'Ekonomi dan Bisnis',       'year':2022,'visits':7, 'books':6, 'streak':0, 'initials':'LH','role':'student','sub':'Ekonomi dan Bisnis · 2022','faculty_color':'#ff6eb4'},
    {'id':'L202307001','name':'Maya Indah Permatasari',  'faculty':'Pertanian',                'year':2023,'visits':7, 'books':5, 'streak':0, 'initials':'MI','role':'student','sub':'Pertanian · 2023','faculty_color':'#41e0d0'},
    {'id':'L202208001','name':'Naufal Ardiansyah Putra', 'faculty':'Ilmu Sosial dan Ilmu Politik','year':2022,'visits':6,'books':4, 'streak':0,'initials':'NA','role':'student','sub':'FISIP · 2022','faculty_color':'#ff5c5c'},
]

_LECTURERS = [
    {'id':'NIP20010001','name':'Dr. Siti Rahayu, M.T.',        'faculty':'Teknik',              'title':'Lektor Kepala','visits':22,'books':10,'streak':21,'initials':'SR','role':'lecturer','sub':'Teknik · Lektor Kepala','faculty_color':'#3de08a'},
    {'id':'NIP20020001','name':'Prof. Eko Supriyanto, Ph.D.',  'faculty':'Kedokteran',          'title':'Guru Besar',   'visits':19,'books':14,'streak':18,'initials':'ES','role':'lecturer','sub':'Kedokteran · Guru Besar','faculty_color':'#9b72ff'},
    {'id':'NIP20030001','name':'Dr. Anwar Fauzi, S.H., M.H.', 'faculty':'Hukum',               'title':'Dosen',        'visits':17,'books':8, 'streak':15,'initials':'AF','role':'lecturer','sub':'Hukum · Dosen','faculty_color':'#ff914d'},
    {'id':'NIP20040001','name':'Dr. Rina Sulistyowati, M.Sc.','faculty':'Ekonomi dan Bisnis',  'title':'Lektor Kepala','visits':15,'books':11,'streak':10,'initials':'RS','role':'lecturer','sub':'Ekonomi dan Bisnis · Lektor Kepala','faculty_color':'#ff6eb4'},
    {'id':'NIP20050001','name':'Dr. Yudha Pratama, M.Kom.',   'faculty':'Ilmu Komputer',       'title':'Dosen',        'visits':14,'books':5, 'streak':8, 'initials':'YP','role':'lecturer','sub':'Ilmu Komputer · Dosen','faculty_color':'#4da6ff'},
    {'id':'NIP20060001','name':'Prof. Dewi Wulandari, Ph.D.', 'faculty':'Psikologi',           'title':'Guru Besar',   'visits':12,'books':16,'streak':12,'initials':'DW','role':'lecturer','sub':'Psikologi · Guru Besar','faculty_color':'#f5c842'},
    {'id':'NIP20070001','name':'Dr. Hafiz Nugraha, M.T.',     'faculty':'Teknik',              'title':'Dosen',        'visits':10,'books':6, 'streak':5, 'initials':'HN','role':'lecturer','sub':'Teknik · Dosen','faculty_color':'#3de08a'},
]

_STAFF = [
    {'id':'STF20110001','name':'Budi Santoso',    'faculty':'Administrasi Umum','dept':'Administrasi Umum', 'title':'Staf Senior',      'visits':18,'books':3,'streak':30,'initials':'BS','role':'staff','sub':'Administrasi · Staf Senior','faculty_color':'#8892aa'},
    {'id':'STF20120001','name':'Wati Rahayu',     'faculty':'Pengolahan',        'dept':'Pengolahan',        'title':'Pustakawan',       'visits':16,'books':5,'streak':25,'initials':'WR','role':'staff','sub':'Pengolahan · Pustakawan','faculty_color':'#8892aa'},
    {'id':'STF20130001','name':'Agus Wibowo',     'faculty':'IT & Sistem',       'dept':'IT & Sistem',       'title':'Staf IT',          'visits':14,'books':2,'streak':18,'initials':'AW','role':'staff','sub':'IT & Sistem · Staf IT','faculty_color':'#8892aa'},
    {'id':'STF20140001','name':'Erna Damayanti',  'faculty':'Referensi',         'dept':'Referensi',         'title':'Pustakawan Senior','visits':12,'books':7,'streak':22,'initials':'ED','role':'staff','sub':'Referensi · Pustakawan Senior','faculty_color':'#8892aa'},
    {'id':'STF20150001','name':'Joko Wahono',     'faculty':'Sirkulasi',         'dept':'Sirkulasi',         'title':'Staf Pelayanan',   'visits':10,'books':2,'streak':14,'initials':'JW','role':'staff','sub':'Sirkulasi · Staf Pelayanan','faculty_color':'#8892aa'},
]

_BOOKS = [
    {'title':'Pemrograman Web Modern dengan Django',        'author':'Arief Budiman, S.Kom.',          'category':'Informatika',        'borrows':47},
    {'title':'Algoritma dan Struktur Data',                 'author':'Dr. Hendra Wijaya',              'category':'Informatika',        'borrows':41},
    {'title':'Pengantar Ilmu Ekonomi Makro',                'author':'Prof. Sadono Sukirno',           'category':'Ekonomi',            'borrows':38},
    {'title':'Ilmu Bedah Dasar Edisi 5',                    'author':'Mansjoer, Arif et al.',          'category':'Kedokteran',         'borrows':35},
    {'title':'Hukum Perdata Indonesia',                     'author':'Prof. R. Subekti, S.H.',         'category':'Hukum',              'borrows':31},
    {'title':'Statistika untuk Penelitian',                 'author':'Prof. Sugiyono',                 'category':'Metodologi',         'borrows':29},
    {'title':'Manajemen Keuangan Perusahaan',               'author':'Dr. Agus Salim, M.M.',           'category':'Manajemen',          'borrows':26},
    {'title':'Machine Learning: Teori dan Implementasi',    'author':'Prof. Budi Santosa, Ph.D.',      'category':'Kecerdasan Buatan',  'borrows':23},
    {'title':'Psikologi Sosial Terapan',                    'author':'Dr. Sarlito Wirawan',            'category':'Psikologi',          'borrows':20},
    {'title':'Mekanika Tanah dan Fondasi',                  'author':'Braja M. Das (Alih Bahasa)',     'category':'Teknik Sipil',       'borrows':17},
]

_FACULTIES = [
    {'name':'Ilmu Komputer',             'code':'FILKOM', 'color':'#4da6ff','visitors':312,'books':178},
    {'name':'Teknik',                    'code':'FT',     'color':'#3de08a','visitors':287,'books':143},
    {'name':'Kedokteran',                'code':'FK',     'color':'#9b72ff','visitors':261,'books':201},
    {'name':'Ekonomi dan Bisnis',        'code':'FEB',    'color':'#ff6eb4','visitors':219,'books':112},
    {'name':'Hukum',                     'code':'FH',     'color':'#ff914d','visitors':184,'books':79},
    {'name':'Psikologi',                 'code':'FPSI',   'color':'#f5c842','visitors':156,'books':94},
    {'name':'Pertanian',                 'code':'FP',     'color':'#41e0d0','visitors':121,'books':68},
    {'name':'Ilmu Sosial dan Ilmu Politik','code':'FISIP','color':'#ff5c5c','visitors':108,'books':57},
]

def _add_level(item):
    item['visits'] = item['visits'] * 15  # scale up to look like XP points
    xp = item['visits']
    levels = [
        (0,    100,  'Pengunjung',     1,     '#95a5a6'),
        (101,  300,  'Pembaca',        2,     '#3498db'),
        (301,  700,  'Pelajar',        3,     '#2ecc71'),
        (701,  1500, 'Peneliti',       4,     '#9b59b6'),
        (1501, 3000, 'Cendekia',       5,     '#e67e22'),
        (3001, float('inf'), 'Legenda Perpus', 'MAX', '#f1c40f')
    ]
    for min_xp, max_xp, name, lv_num, color in levels:
        if xp <= max_xp:
            progress = 100
            if max_xp != float('inf'):
                progress = int(((xp - min_xp) / max(1, (max_xp - min_xp))) * 100)
            item['level'] = {
                'name': name, 'level_num': lv_num, 'current_xp': xp,
                'min_xp': min_xp, 'max_xp': max_xp if max_xp != float('inf') else xp,
                'progress_perc': min(100, progress), 'color': color
            }
            break

for s in _STUDENTS + _LECTURERS + _STAFF:
    _add_level(s)

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
            'total_visitors': 3847,
            'total_books':    743,
            'active_members': 247,
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
