# 🎤 Persiapan Wawancara: Bedah Proyek LibraryRank

Kamu akan diwawancarai sebagai **Full-Stack Engineer** yang membangun proyek ini. Panduan ini dirangkum menggunakan bahasa profesional yang siap kamu gunakan saat ditanya oleh dosen penguji, manajer IT, atau perekrut (*interviewer*).

---

## 1. Apa Latar Belakang & Kebutuhan Proyek Ini? (The "Why")

**Masalah (Problem):**
Mayoritas perpustakaan universitas menggunakan sistem **Koha ILS** untuk manajemen sirkulasi dan katalog buku. Sayangnya, Koha tidak memiliki modul *Leaderboard* (Papan Peringkat) publik yang interaktif dan menarik. Hal ini menyebabkan minat baca mahasiswa stagnan karena tidak ada rasa kompetisi atau apresiasi (gamifikasi) secara terbuka.

**Solusi Kita (The Solution):**
Kita membangun **LibraryRank**, sebuah *Dashboard Leaderboard* cerdas dan interaktif. Tujuannya adalah memacu semangat (*gamification*) mahasiswa, dosen, dan staf untuk rajin berkunjung dan meminjam buku, dengan memamerkan peringkat mereka layaknya kompetisi di dalam *game*.

---

## 2. Pilihan Teknologi (Tech Stack) & Alasannya

Jika ditanya, *"Mengapa memakai bahasa/framework ini?"*, inilah jawabanmu:

- **Backend: Python & Django 5.0**
  *Alasan:* Django sangat aman, sangat cepat untuk memodelkan database (menggunakan Django ORM), dan sudah memiliki *Admin Panel* bawaan, sehingga pustakawan bisa memantau data tanpa kita perlu membuat halaman admin dari nol.
- **Database: MySQL / MariaDB**
  *Alasan:* Karena sistem perpustakaan "Koha" asli berjalan di atas MySQL. Menggunakan MySQL untuk LibraryRank memudahkan integrasi dan penyatuan *server*.
- **Integrasi SSO (Single Sign-On)**
  *Alasan:* Aplikasi kita dikonfigurasikan menggunakan `django-cas-ng` untuk menyambung ke CAS SSO Universitas, sehingga mahasiswa tidak perlu mendaftar ulang; cukup login dengan akun akademik mereka.
- **Frontend: Vanilla HTML, CSS, dan Javascript**
  *Alasan:* Untuk efisiensi *resource*. Karena ini adalah aplikasi dasbor layar informasi (*kiosk*) yang berjalan 24 jam di LED TV lobi perpustakaan, kita menghindari framework berat seperti React atau Vue. Vanilla JS menjamin *loading* yang asinkron secepat kilat.

---

## 3. Arsitektur & Keamanan Data (How it Works)

Ini adalah bagian terpenting untuk dipahami oleh seorang *Engineer*. Bagaimana LibraryRank mengambil data pengunjung tanpa merusak sistem asli perpustakaan?

**Arsitektur "Zero-Touch Sync" (Sinkronisasi Pasif):**
1. Sistem LibraryRank **tidak pernah** mengubah isi database Koha (Koha hanya berstatus *Read-Only*).
2. Kita membuat *script* sinkronisasi khusus (Custom Django Command: `python manage.py sync_from_koha`) yang akan menarik log dari tabel `borrowers`, `issues`, dan `statistics` milik Koha.
3. Log mentah tersebut kemudian ditarik, diolah, dan disimpan ke dalam database internal milik LibraryRank itu sendiri (`Member`, `Visit`, `BorrowRecord`).
4. Dengan pemisahan database ini, seandainya web LibraryRank diretas atau *error*, sistem Koha utama universitas tempat peminjaman buku akan tetap aman 100%.

---

## 4. Bedah Fitur & Kosmetik UI (Features Breakdown)

Saat mendeskripsikan fitur, bagi ke dalam 3 poin kebanggaanmu:

### A. Dynamic Appreciation Engine (Sistem Lencana/Badge)
*"Saya mendesain sistem penghargaan dinamis di layer Model Backend tanpa membebani database dengan tabel-tabel perantara baru yang rumit."*
- **Algoritmanya:** Di file `models.py`, lencana dikalkulasi secara *real-time* saat API dipanggil. 
  - 🥈 **Weekly Warrior**: Dicari dari log `visits` berumur $\le$ 7 hari $\ge$ 3 kali.
  - 🥇 **Library Legend**: Menghitung *Subquery Rank* secara agregat dalam sebulan.
  - 📚 **Book Worm**: Menghitung `borrow_records` lebih dari 5 judul dalam batas 6 bulan.

### B. IG Story & Social Share Generator
*"Papan Peringkat tidak akan viral jika tidak bisa dibagikan."*
- Kita menanamkan *Web Intent URL* untuk membagikan pencapaian ke Twitter/WA.
- Puncak inovasinya adalah tombol **📸 IG Story**, di mana kita mengimplementasikan library **`html2canvas`**. Skrip front-end ini menangkap kode HTML dari elemen Kartu Profil, me-render-nya di dalam *memory browser*, lalu memuntahkannya sebagai sebuah *Image* (JPG) yang siap diunggah ke Instagram, semua tanpa menyita kapasitas CPU/RAM Server Backend sedikit pun!

### C. Tema Modern & Animasi Kosmetik CSS
*"Saya mendesain UI tidak kaku seperti sistem akademik konvensional, tapi lebih mirip dashboard E-Sports."*
- Tipografi *bold* (Poppins/Montserrat).
- **Dark Mode eksklusif** (Navy: `#1E1C4B`) untuk mencegah kelelahan mata karena layar TV akan selalu menyala 24/7.
- Modifikasi tingkat tinggi di file `main.css`: Saya menanamkan *Animated Grid Background* dan menyematkan efek *glowing border* secara dinamis, beserta emoji api (🔥) yang diberikan animasi CSS `@keyframes fireFlicker`, khusus untuk juara 1, 2, dan 3.

---

## 5. Ringkasan Tanya-Jawab (QnA)

**Q: Bagaimana jika terjadi mati lampu dan API Koha database terputus?**
A: Leaderboard kita memiliki databasenya sendiri. Dia akan tetap bisa melayani web secara lancar menggunakan data sinkronisasi terakhir, tidak akan *error* atau nge-*blank*.

**Q: Mengapa pada lokal saat ini menggunakan Demo Data (`_use_demo()`)?**
A: Fitur ini saya bangun (di `views.py` & `demo_data.py`) agar aplikasi tetap merender antarmuka yang sempurna sekalipun sedang dideploy dan sistem belum terhubung ke database. Sangat berguna untuk kepentingan uji klinis UI dan presentasi (*Showcase*).

**Q: Fitur teknis tambahan apa yang menarik di aplikasi ini?**
A: Saya juga menyediakan API Ekspor ke Excel (.xlsx) lewat `openpyxl` dan ekspor laporan ke format `.pdf` lewat `ReportLab`, yang sangat berguna bagi admin/pustakawan untuk melakukan *reporting* bulanan secara cepat.
