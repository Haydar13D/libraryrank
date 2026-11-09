# Design Document: Alur Poin Musiman & Klasemen (Model B1)

**Tanggal:** 2026-11-09  
**Status:** Menunggu Persetujuan  
**Target:** LibraryRank (`leaderboard` app)

---

## 1. Latar Belakang & Tujuan
Saat ini, penukaran merchandise mencatat transaksi minus (`amount = -reward.points_cost`) di tabel `PointTransaction`. Pada kode `koha_utils.py`, nilai minus ini langsung mengurangi `total_p` yang dipakai untuk merangking papan klasemen di halaman utama dan TV Display. Akibatnya, mahasiswa yang menukarkan merchandise mengalami penurunan peringkat di klasemen (*disinsentif* untuk menukar reward).

Selain itu, siklus reset semester menyetel ulang poin pada tanggal aktif (`active_reset_date`). Pemilik sistem menyetujui model **B1**, yaitu satu siklus reset semester terpadu di mana skor prestasi klasemen tidak berkurang saat mahasiswa menukarkan merchandise.

---

## 2. Pendekatan yang Dipertimbangkan

| Pendekatan | Cara Kerja | Alasan Dipilih / Ditolak |
|---|---|---|
| **Opsi A (Dipisah Penuh)** | Saldo koin belanja tidak pernah di-reset (akumulatif seumur hidup), hanya peringkat yang di-reset per semester. | Ditolak oleh pemilik sistem karena tidak cocok dengan siklus anggaran merchandise tahunan/semesteran perpustakaan. |
| **Opsi B2 (Digabung Penuh, Peringkat Ikut Turun)** | Poin tunggal, berkurang saat belanja merchandise, peringkat klasemen langsung anjlok. | Ditolak karena merugikan mahasiswa juara; mahasiswa takut menukar hadiah karena rankingnya akan disalip. |
| **Opsi B1 (Terpadu: Skor Prestasi Utuh, Saldo Belanja Berkurang)** | Poin berbasis semester berjalan. Skor klasemen dihitung dari akumulasi kotor (*Gross XP*). Saldo belanja dihitung dari sisa poin (*Net XP*). Keduanya di-reset bersamaan saat pergantian semester. | **DIPILIH**. Adil bagi pemuncak klasemen, menjaga semangat kompetisi, dan selaras dengan siklus reset semester perpustakaan. |

---

## 3. Spesifikasi Alur & Perubahan Teknis

### A. Perhitungan Poin di `koha_utils.py`
Saat mengagregasi data kunjungan, peminjaman, dan transaksi poin lokal:
1. **`gross_points` (Skor Klasemen & Peringkat):**
   $$\text{gross\_points} = \text{kunjungan} + \text{peminjaman} + \sum (\text{PointTransaction bernilai positif, misal: seminar/event})$$
   *Peringkat 1 s.d. selesai diurutkan berdasarkan `gross_points`.*
2. **`redeemed_points` (Poin yang Telah Ditukar):**
   $$\text{redeemed\_points} = \left| \sum (\text{PointTransaction dengan transaction\_type='redeem'}) \right|$$
3. **`available_points` (Saldo Poin Belanja Hadiah):**
   $$\text{available\_points} = \max(0, \text{gross\_points} - \text{redeemed\_points})$$

### B. Validasi Penukaran Reward (`views.py` & `integration_views.py`)
- Pengecekan saldo pada saat `api_request_otp`, `api_verify_otp_and_redeem`, dan `integration_redeem` menggunakan `available_points` (bukan `gross_points`).
- Mahasiswa hanya bisa menukar reward jika `available_points >= reward.points_cost`.

### C. Penyesuaian Antarmuka Pengguna (UI)
- **Tabel Leaderboard & TV Display:** Menampilkan `gross_points` sebagai **Total Poin / Skor Prestasi**.
- **Modal Profil Mahasiswa & Katalog Reward:**
  - Menampilkan badge **Skor Klasemen** (misal: 200 XP).
  - Menampilkan **Saldo Poin Belanja** (misal: Sisa 100 XP yang dapat ditukarkan).

---

## 4. Batasan & Rencana Pengujian
- **Non-Goals:** Tidak mengubah schema tabel database (tidak perlu migrasi baru karena `PointTransaction` sudah menyimpan tipe transaksi dan nilai positif/negatif).
- **Verifikasi:**
  1. Mahasiswa dengan 200 XP menukar reward 100 XP.
  2. Verifikasi posisi rank dan skor di leaderboard tetap 200 XP.
  3. Verifikasi saldo penukaran selanjutnya menjadi 100 XP.
  4. Pengujian batas kupon tidak dapat menukar melebihi saldo sisa.

