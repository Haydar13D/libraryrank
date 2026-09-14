# 🌟 Dokumentasi Fitur LibraryRank

LibraryRank adalah aplikasi dasbor dan papan peringkat harian yang dirancang untuk Perpustakaan Universitas yang menggunakan Koha ILS. Berikut adalah rincian fitur dan apa saja yang ditampilkan oleh aplikasi saat ini:

---

## 1. Papan Peringkat (Leaderboard) Multi-Kategori
Menampilkan daftar pengunjung dan peminjam teraktif yang dibagi ke dalam beberapa Tab:
- **Overview**: Menampilkan statistik umum (Total Visits, Total Books) dan Nominasi Teratas dari semua role.
- **Mahasiswa, Dosen, dan Tendik (Staff)**: Menampilkan ranking pemustaka di masing-masing kategori.
- Fitur Visual Khusus: Pemustaka yang menduduki urutan **Top 1, Top 2, dan Top 3** () akan mendapatkan animasi efek bersinar (*Glowing Gold/Silver/Bronze*) secara real-time dan animasi *fire flicker* (🔥) di sebelah angka peringkatnya.

## 2. Profil Prestasi & Kartu Digital (User Modal)
Jika kamu mengklik nama salah satu pemustaka di Papan Peringkat, sebuah **Pop-up Kartu Profil (Modal)** akan muncul menampilkan:
- **Data Diri**: Inisial Avatar, Nama Lengkap, Nomor Anggota, Fakultas, dan Angkatan.
- **Statistik Total**: Jumlah Kunjungan (All-time & Periodik), Jumlah Buku Dipinjam, dan *Day Streak* (jumlah hari berturut-turut datang ke perpustakaan).
- **Recent Borrows**: Daftar lengkap riwayat peminjaman buku terakhir mereka beserta status pengembalian.

## 3. Sistem Apresiasi (Badges & Rewards)
Aplikasi memiliki mesin kalkulasi pintar yang otomatis memberikan **Badge Pencapaian** kepada pemustaka yang memenuhi kriteria tanpa membebani database:
1. **Weekly Warrior 🥈**: Diberikan jika pemustaka datang minimal 3 kali dalam seminggu terakhir.
2. **Library Legend 🥇**: Diberikan jika pemustaka masuk dalam Peringkat Top 10 kunjungan di bulan berjalan.
3. **Book Worm 📚**: Diberikan jika pemustaka meminjam lebih dari 5 buku dalam satu semester terakhir (6 bulan).
> *Kustomisasi*: Gambar ikon badge-badge ini bisa diganti menggunakan file `.png` milik sendiri melalui pengaturan `image_url` pada kode sistem.

## 4. Berbagi ke Media Sosial (Social Sharing & IG Story)
Di bagian bawah Kartu Profil, terdapat fitur *Gamification* yang memungkinkan pemustaka untuk bersombong atau mempromosikan prestasinya:
- **URL Intent (Web Share)**: Tombol instan untuk berbagi ke **Twitter (X), Facebook, dan WhatsApp** yang sudah dimuat teks otomatis (contoh: *"Saya baru saja meraih prestasi di LibraryRank Universitas..."*).
- **📸 IG Story Generator**: Fitur eksklusif yang menggunakan skrip internal (`html2canvas`) untuk men-screenshot atau mem-foto Kartu Profil secara bersih. Saat diklik, sistem akan mengekspor kartu tersebut menjadi sebuah file foto `LibraryRank_Achievement.jpg` yang langsung terunduh, membuatnya sangat mudah di-upload mahasiswa langsung ke Instagram/WhatsApp Story.

## 5. Filter Analitik & Ekspor Data
- **Filter Rentang Waktu (Date Picker)**: Memungkinkan pustakawan melihat ranking berdasarkan *minggu ini*, *bulan lalu*, atau rentang tanggal spesifik.
- **Top Books & Faculties**: Tab khusus yang menampilkan Fakultas paling aktif dalam peminjaman, serta Buku-buku mana saja yang populer dan dipinjam belakangan ini.
- **Ekspor Laporan**: Terdapat tombol hijau dan merah (di bilah atas) untuk mengekspor daftar papan peringkat saat ini ke dalam **Excel (.xlsx)** maupun **PDF**, berguna untuk laporan bulanan.

## 6. Sinkronisasi Modifikasi Nol (Zero-Touch Sync)
Meskipun aplikasi berjalan paralel dengan **Koha ILS**, LibraryRank **tidak pernah memodifikasi, menambah, atau merusak data di database utama Koha**.
- Autentikasi dilakukan via **CAS SSO** (jika kampus menggunakan Single Sign-On).
- Integrasi data hanya menggunakan mode **Read-only**. Script `python manage.py sync_from_koha` didesain untuk menyalin log pengunjung dan log sirkulasi di Koha secara pasif ke dalam database internal LibraryRank.
- Tersedia **Demo Mode** (`seed_demo_data`) untuk mengetes semua UI UI leaderboard di atas tanpa perlu dihubungkan ke Koha sama sekali.

---

*(Dokumentasi ini mencerminkan fitur frontend dan backend yang aktif pada iterasi versi saat ini).*
