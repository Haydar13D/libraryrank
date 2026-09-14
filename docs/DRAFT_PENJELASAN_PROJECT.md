# 📚 Draft Lengkap Penjelasan & Panduan Proyek: LibraryRank

Draft ini disusun khusus untuk membantu memahami seluruh arsitektur, teknologi, alur kode, dan fungsi dari tiap file di **LibraryRank**, terutama jika kamu belum familiar dengan Python dan Django.

---

## 1. 🏗️ Gambaran Umum Arsitektur Proyek

**LibraryRank** adalah aplikasi papan peringkat (leaderboard) dan dasbor analitik perpustakaan. Aplikasi ini dirancang untuk berjalan berdampingan dengan sistem perpustakaan **Koha ILS** tanpa merusak data Koha itu sendiri.

### **Alur Kerja (Workflow) Sistem:**
```text
[Pengguna / Browser] 
        │
   (Meminta Halaman / Filter Periode)
        ▼
[Django URLs] (Mengatur rute URL ke Fungsi yang tepat)
        │
        ▼
[Django Views] (Menerima request, memanggil Koha Utils)
        │
        ▼
[Koha Utils (koha_utils.py)] ──────────────────────────────┐
        │                                                  │
   (Query SQL Langsung)                              (Query Database)
        ▼                                                  ▼
[Database 'koha'] (Read-Only)                    [Database 'libraryrank']
- Baca tabel borrowers                           - Baca tabel PointPolicy
- Baca tabel statistics (kunjungan)              - Baca tabel BadgeRule
- Baca tabel issues (peminjaman)                 - (Aturan Gamifikasi)
        │                                                  │
        └──────────────────────────────────────────────────┘
        ▼
[Kalkulasi di Views/Utils] (Menghitung XP, Badge, Level, dan Mengurutkan Peringkat)
        │
        ▼
[Frontend (HTML/JS/CSS)] (Menerima data JSON dari Views dan merendernya dalam bentuk Leaderboard dengan efek animasi)
```

**Kunci Utama Arsitektur:** Aplikasi melakukan kalkulasi poin (*XP*) secara **Live (Real-time)** langsung dengan mengambil data *log* dari Koha, lalu menggabungkannya dengan sistem *Badge* dan *Point* yang diatur melalui Admin Panel Django milik LibraryRank.

---

## 2. 🛠️ Penjelasan Teknologi yang Digunakan

*   **Python (3.11+)**: Bahasa pemrograman utama yang menjadi otak aplikasi (backend).
*   **Django (5.0)**: *Framework* web berbasis Python. Django sangat kuat karena memiliki mekanisme routing (URL), keamanan bawaan, arsitektur MVT (Model-View-Template), dan Admin Panel otomatis yang sangat memudahkan pengelolaan data.
*   **MySQL / MariaDB**: Sistem manajemen database yang digunakan. Proyek ini terhubung ke **dua database sekaligus**:
    1.  `libraryrank`: Menyimpan data khusus gamifikasi (badge, poin, level).
    2.  `koha`: Database utama sistem perpustakaan (hanya diakses untuk numpang baca/*read-only*).
*   **HTML, CSS, JavaScript (Vanilla)**: Digunakan di sisi Frontend (Tampilan antar muka) untuk membuat desain *Leaderboard* yang interaktif tanpa memerlukan framework rumit seperti React.

---

## 3. 🧩 Penjelasan Fungsi & Fitur Utama

Berdasarkan `FEATURES.md`, ini adalah apa yang dilakukan kode-kode tersebut:
1.  **Papan Peringkat Real-time**: Menampilkan ranking Mahasiswa, Dosen, dan Staff berdasarkan jumlah peminjaman buku dan kunjungan.
2.  **Sistem Apresiasi (Badges)**: Secara otomatis mendeteksi apakah pemustaka berhak mendapat *Weekly Warrior*, *Library Legend*, dsb.
3.  **Social Sharing & IG Story**: Meng-ekspor (screenshot otomatis menggunakan JS `html2canvas`) ID Card prestasi menjadi foto untuk diunggah ke Instagram.
4.  **Ekspor Data**: Fitur pembuatan file laporan rekap Excel dan PDF.

---

## 4. 📂 Bedah Detail Setiap File di Proyek (Tanpa Terkecuali)

Berikut adalah peran dari setiap *file* penting pada folder proyek:

### A. Folder Root (`f:\libraryrank\`)
*   **`manage.py`**: Skrip manajer bawaan Django. File ini yang kamu gunakan di terminal untuk menjalankan server (`python manage.py runserver`), menjalankan sinkronisasi, dll.
*   **`requirements.txt`**: Daftar semua *package* atau pustaka eksternal yang dibutuhkan oleh proyek (seperti modul koneksi mysql, djanggo, openpyxl untuk excel).
*   **`.env`** (dan `.env.example`): File pengaturan rahasia. Di sinilah password database, host, dan mode kunci rahasia (*SECRET_KEY*) disimpan.
*   **`README.md`, `FEATURES.md`, `review_and_roadmap.md`**: File dokumentasi berbasis teks (markdown) yang berisi panduan setup, daftar fitur, dan roadmap sejarah pengembangan.
*   **`seed_master.py` / `test_koha.py` / `test_live_month.py`**: File skrip tester yang sesekali dijalankan dari terminal untuk mengetes koneksi lokal atau injeksi data kecil ke database.

### B. Folder Konfigurasi Utama (`libraryrank/`)
*   **`settings.py`**: Urat nadi sistem Django. Di sini aplikasi diatur: mulai dari koneksi ke 2 database (default & koha), mengatur modul SSO (Single Sign-On), direktori file statis, dan mendaftarkan aplikasi bernama `leaderboard`.
*   **`urls.py`**: Pengatur "Rambu Lalu Lintas" web. File ini menentukan jika user mengakses URL tertentu (seperti `/admin`), akan diarahkan ke kode yang mana.
*   **`db_routers.py`**: File cerdas yang mengatur *routing* database. Mengatur Django agar *tidak sengaja* menulis (*write*) data ke database `koha`.
*   **`wsgi.py` / `asgi.py`**: File standar Django yang digunakan nanti jika aplikasi akan di-online-kan di server asli (production node).

### C. Folder Aplikasi Utama (`leaderboard/`)
Ini adalah jantung fungsionalitas dari LibraryRank.

*   **`models.py`**: Penjabaran tabel-tabel di Database dalam bentuk kode Python (Disebut ORM - Object Relational Mapping).
    *   Tabel Gamifikasi: `LevelTier`, `BadgeRule`, `PointPolicy` (yang bisa diedit pustakawan di admin).
    *   Tabel Logistik: `Faculty`, `SystemLog`.
    *   *(Tabel lawas/legacy untuk sinkronisasi juga ada di sini seperti `Member`, `Visit`, `BorrowRecord` namun di arsitektur Live sekarang perannya sudah digantikan oleh query langsung).*
*   **`admin.py`**: Mengontrol apa saja tabel dari `models.py` yang akan ditampilkan dan bisa dimodifikasi di dasbor Admin Django (`/admin`).
*   **`urls.py`**: Daftar URL khusus halaman leaderboard dan API (seperti `/api/overview`, `/api/role/student`, `/export/excel`).
*   **`views.py`**: Otak pengendali halaman. Saat pengunjung membuka web, `views.py` akan:
    1. Melihat apa yang diminta (tanggal berapa?).
    2. Memeriksa apakah `koha` menyala (jika mati, ia akan mengambil data pura-pura dari `demo_data.py`).
    3. Jika hidup, ia akan memangil `koha_utils.py`, meminta data, menyusun *JSON* (*JavaScript Object Notation*), lalu melemparkannya ke Frontend.
*   **`koha_utils.py`**: Jembatan murni (Script Raw SQL) antara Django dan Database Koha. Di sinilah terjadi "penarikan data berat" (*query LEFT JOIN* tabel Koha) menggunakan kalkulasi SQL yang sangat cepat, mencocokkan total buku dipinjam, hitung *points*, dan menghitung *Badge*.
*   **`demo_data.py`**: Berisi tumpukan data palsu/tiruan (Mahasiswa A, Dosen B) berguna untuk mendesain UI tanpa perlu menyalakan database Koha.
*   **`exports.py`**: Logika khusus yang mengandung kode untuk men-generate file `.xlsx` menggunakan library `openpyxl` dan file PDF menggunakan `ReportLab`.
*   **`context_processors.py`**: Skrip kecil yang menyuntikkan variabel tertentu ke semua halaman HTML secara global.

### D. Folder Skrip Perintah Latar Belakang (`leaderboard/management/commands/`)
*   **`sync_from_koha.py`**: Komando manual/script batch (dijalankan pakai `python manage.py sync_from_koha`). Secara historis, script ini digunakan untuk menyedot jutaan data dari database Koha dan disimpan satu per satu ke database internal `libraryrank`. (Catatan: Pada iterasi terbaru, ini sudah jarang digunakan karena kita sudah pakai metode Live Load via `koha_utils.py`).
*   **`seed_demo_data.py`**: Sama seperti di atas, tapi menyuntikkan data fiktif ke tabel `Member` / `Visit` ORM jika kamu mau melakukan testing full di localhost tanpa Koha.

### E. Folder Tampilan/Antar Muka
*   **`templates/leaderboard/`**: Kumpulan file HTML yang memberikan kerangka dasar web.
    *   `base.html`: Templat induk (membawa header, navigasi sidebar, layout dasar).
    *   `index.html`: File anak yang mewarisi layout dasar, dan berisi *struktur kosong* dari Leaderboard. Nantinya struktur kosong ini akan diisi menggunakan aksi dari JavaScript.
*   **`static/`**: Tempat menyimpan file *Front-End* statis:
    *   `css/`: Berisi styling (warna warni efek *glow gold*, animasi *fire flicker*).
    *   `js/`: Kumpulan kode interaktif yang mengambil data JSON dari `views.py` dan membuat HTML Leaderboard secara dinamis (seperti logika Filter tombol, klik kartu Modal/Popup).
    *   `images/`: Tempat logo dan avatar diletakkan.

---

## 5. 🔄 Workflow: Bagaimana Data dari Klik User Menjadi Tampilan?

Agar lebih terbayang, begini perjalanannya jika Pustakawan memfilter: "Tampilkan Ranking Mahasiswa Bulan Ini":

1. **User (Browser)**: Pustakawan menekan tombol Bulan Ini di Dropdown. Javascript di `static/js/` merespons, "Minta data JSON dong ke rentang tanggal ini".
2. **Javascript Fetch**: Mengirim permintaan (Request) ke `/api/role/student/?date_from=XXX&date_to=YYY`.
3. **Django URL (`urls.py`)**: Mengenali jalan URL `/api/role...` dan mengarahkannya ke fungsi `api_role_leaderboard` di file `views.py`.
4. **Django View (`views.py`)**: Menerima request, membaca parameter tanggal (Bulan ini). Ia kemudian melimpahkan tugas: "Hei `koha_utils.py`, tolong ambilkan data Mahasiswa di periode ini".
5. **Koha Utils (`koha_utils.py`)**: 
   - Melakukan koneksi murni ke Database `koha`.
   - Mengirim perintah *SQL raksasa*: "SELECT * dari borrowers, LEFT JOIN dengan statistics dan issues berdasarkan rentang tanggal".
   - Mendapatkan hasil dari database, kemudian dilooping (diulang) menggunakan Python untuk dihitung skor XP-nya (merujuk ke PointPolicy dari database `libraryrank`), dan diputuskan dia dapat *Badge* apa hari ini.
   - Mengurutkan hasilnya dari tertinggi ke terendah.
   - Mengembalikan data bentuk bersih (List Dictionary) kembali ke `views.py`.
6. **Django View (`views.py`)**: Membungkus paket menjadi respons JSON dan mengirim kembali ke Browser.
7. **Javascript (Frontend)**: Menerima JSON (Berisi Nomor 1 Si Budi Poin 500, dst). Javascript lalu membuat elemen HTML (div, span) secara real-time dan menampilkannya di layar dengan efek CSS yang meriah.

---

Draft ini bisa kamu pelajari perlahan. Django itu pada dasarnya memisahkan antara **Database (Models) - Logika Web (Views) - dan Tampilan (Templates)**. Arsitektur aplikasi LibraryRank menggunakan gaya yang semi-modern yaitu: Django tidak merender datanya langsung di HTML, melainkan berfungsi sebagai pembuat API (Penyedia Data JSON), dan Frontend JavaScript yang bertugas mempercantik dan menampilkan datanya.
