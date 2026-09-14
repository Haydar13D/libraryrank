# 📈 Kilas Balik & Peta Jalan (Roadmap) Peningkatan LibraryRank

Berikut ini adalah rekapitulasi dari seluruh masalah yang telah kita pecahkan bersama dan daftar perombakan yang sudah kita tambahkan ke dalam sistem *LibraryRank*, beserta ide-ide pengembangan tingkat lanjut (Improvements) untuk fase berikutnya.

---

## 🏗️ Kilas Balik Perubahan (What We Have Done)

### 1. Perbaikan Bug Kritis (Backend Server)
- **Kompatibilitas Windows & MySQL**: Memperbaiki sistem Django yang kolaps (`ImportError`) di sistem operasi Windows karena absennya *driver* C-Extension. Kita berhasil menyuntikkan *fallback* menggunakan `PyMySQL` murni sebagai cadangan di file `__init__.py`.
- **Bug Timezone Basis Data (`__date`)**: Memecahkan masalah kueri tanggal yang tidak mau memuat statistik kunjungan di OS Windows lokal. Kita mengubah logika penyaringan `visited_at__date` menjadi algoritma rentang tanggal cerdas (`__gte` dan `__lt` dengan penambahan *timedelta 1 hari*) di `views.py` dan `models.py`. 
- **Demo Mode Engine**: Menyambungkan logika data statis (`demo_data.py`) agar dapat ditampilkan dan dikalkulasi secara harmonis dengan UI saat database riil masih kosong.

### 2. Penambahan Fungsionalitas & Gamifikasi (Fitur)
- **Sistem Badge Apresiasi Bebas Migrasi**: Merancang kalkulasi penganugerahan predikat secara cerdas (Weekly Warrior 🥈, Library Legend 🥇, Book Worm 📚) langsung dari *QuerySet Properties* tanpa perlu membuat tabel baru, yang mengurangi kerumitan skema *Database*.
- **Papan Peringkat Real-time (UI/JS)**: Merombak Javascript agar Modal/Kartu Profil mampu memuat status pinjaman buku (*borrowed*, *returned*, *overdue*) secara detil untuk setiap pengguna.
- **IG Story Generator & Social Share**: Menyuntikkan fungsionalitas pembagi ke media sosial (*Twitter, FB, WA*) menggunakan *URL intent* dan membangun pembuat screenshot otomatis menggunakan `html2canvas` yang merender *CaptureCard* secara terisolasi menjadi file JPG tanpa membebani server backend.

### 3. Eksekusi Desain (*Brand Guideline*)
- **Revisi Tipografi**: Berpindah dari sistem *font* lawas ke dua tipe tipografi modern dan solid (`Poppins` untuk judul dan `Montserrat` untuk paragraf).
- **Tema Gelap (*Brand Focus*)**: Membangun *Dark Mode* elegan yang berpadu dengan tema pedoman merek Kampus (Biru Tua/Navy: `#1E1C4B`) serta warna aksen (Hijau Tosca & Emas/Kuning).
- **Animasi Visual (VFX) Kosmetik**: Menambahkan fitur titik/pola geometris (*dot pattern*) animasi lambat untuk menyejukkan mata dari layar kosong, plus menambahkan efek frame bercahaya (glowing border) dan nyala api (🔥) berkelap-kelip khusus untuk Ranking Top 3 di `main.css`.

---

## 🚀 Ide *Improvements* Selanjutnya (Roadmap)

Jika kamu ingin mengangkat proyek ini dari sekadar prototipe ke versi *Production-Ready*, berikut ini target pengembangan yang ideal:

### A. Performa & Database (*Security & Architecture*)
> [!TIP]
> **1. Optimalisasi DB Indexing & Caching**
> - **Masalah**: Saat ini badge (Weekly Warrior & Book Worm) dikalkulasi secara *on-the-fly* (berjalan serentak setiap kali profil profil dipanggil `/api/member/id`). Jika data API bertambah ratusan ribu baris, perhitungan Peringkat "*Library Legend*" dan *count* akan memeras CPU server (*loading* lambat).
> - **Solusi**: 
>   1. Tambahkan parameter `db_index=True` pada kolom `visited_at` dan `borrowed_at` di dalam file `models.py` Django.
>   2. Pasang sistem *Cache* tingkat lanjut (seperti `Redis` atau Cache memori bawaan Django) pada *endpoint* API Leaderboard sehingga server tidak perlu melakukan kalkulasi perhitungan badge setiap detik, cukup diperbarui tiap 5/10 menit.

> [!WARNING]
> **2. Rate-Limiting & Keamanan API**
> - Karena API dapat diakses oleh browser tanpa Token rahasia (`GET /api/overview`), sistem akan rentan terhadap *DDoS* atau *Scraping* otomatis (pengumpulan data identitas besar-besaran). Perlu dipasangi pelindung *rate-limiting* menggunakan Web Server Nginx atau *Django Rest Framework Throttle*.
> - Aktifkan konfigurasi **CORS** (Cross-Origin Resource Sharing) dan **CSP** (Content Security Policy) di `settings.py` untuk melindungi skrip `html2canvas` agar gambar luaran penggunaannya tidak cacat saat migrasi nama domain kampus/produksi.

### B. Fitur Tambahan Tingkat Lanjut (*Features*)
- **Pembuatan Custom Badge via Admin**: Alih-alih diprogram "mati" (*hardcoded*) di dalam `models.py`, alangkah kerennya jika Pustakawan bisa membuat "Badge Khusus Event" (contoh: *Pahlawan Literasi Agustus*) melalui panel Django Admin. Kita bisa memigrasikan logika badge ini menjadi struktur model `BadgeEvent` di database.
- **WebSocket / Auto-Refresh**: Daripada meminta skrip me-reset halaman dan *polling* API, proyek ini cocok dipasangkan `Django Channels` (WebSocket). Papan Peringkat bisa bergeser naik/turun seketika tanpa refresh layaknya Papan Data Perdagangan Saham (semua pengunjung lobi perpustakaan akan melihat layar mereka bergerak otomatis serentak)!

### C. *User Interface* (UI/UX)
- **Tombol Mode Terang (Light Mode)**: Walaupun *Dark Mode* saat ini sangat ramah di mata layar TV/Dasbor stasioner, tambahan sakelar (*toggle*) Mode Terang akan berguna ketika diakses pengguna HP di bawah terik matahari *outdoor*.
- **Halaman Profil Penuh**: Saat ini riwayat perpustakaan terkurung ringkas di *Modal Pop-up*. Akan jauh lebih keren dan bernilai estetik tinggi jika sebuah `libraryrank.com/member/UID` disediakan sebagai satu halaman utuh menampilkan **Grafik Garis/Infografis Statistik Peminjaman Tahunan**, lengkap dengan koleksi lencana penuh milik mereka layaknya Profil Steam atau Github.
