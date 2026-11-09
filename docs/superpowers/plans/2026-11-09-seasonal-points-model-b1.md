# Seasonal Points & Leaderboard (Model B1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Memisahkan perhitungan Skor Prestasi Klasemen (*Gross XP*) agar tidak turun saat menukar merchandise, sementara Saldo Belanja (*Available XP*) berkurang sesuai biaya reward yang ditukarkan pada semester aktif.

**Architecture:** Modifikasi agregasi transaksi di `koha_utils.py` untuk memisahkan transaksi perolehan positif (kunjungan, peminjaman, seminar/event) dengan transaksi penukaran reward (negatif `redeem`). Menggunakan `gross_points` untuk perangkingan klasemen & level, dan `available_points` untuk validasi transaksi penukaran reward di `views.py` dan `integration_views.py`.

**Tech Stack:** Django 5, MySQL 8.0, Python 3.12, Vanilla JS.

**Spec:** `docs/superpowers/specs/2026-11-09-seasonal-points-and-leaderboard-design.md`

## Global Constraints
- `LeaderboardConfig.get_active_reset_date()` tetap menjadi batas awal perhitungan musim aktif (`date_from`).
- Skema database tabel `PointTransaction` dan `RedemptionClaim` tidak diubah (zero migration).
- Transaksi `redeem` di `PointTransaction` tetap mencatat nilai minus `amount = -points_cost`.

## Review Focus
- Mahasiswa menukar reward tidak boleh mengalami penurunan peringkat di tabel Leaderboard (`gross_points` konstan).
- Mahasiswa tidak boleh bisa menukar reward jika `available_points < points_cost`.
- Nilai `available_points` tidak boleh pernah bernilai negatif (`max(0, available_points)`).
- Modal detail anggota di frontend menampilkan dua angka: Skor Klasemen (Gross) dan Saldo Belanja (Available).
- Kiosk/TV Display hanya menampilkan Skor Klasemen (Gross).

---

### Task 1: Pisahkan Gross Points dan Available Points di `koha_utils.py`

**Files:**
- Modify: `leaderboard/koha_utils.py:270-350`
- Modify: `leaderboard/koha_utils.py:420-470`

**Interfaces:**
- Produces: `member_dict['total_p']` (Gross XP), `member_dict['available_p']` (Saldo Belanja), `member_dict['redeemed_p']` (Total XP Ditukar).

- [ ] **Step 1: Modifikasi agregasi transaksi lokal di `get_live_members` (`koha_utils.py`)**
Pisahkan agregasi transaksi lokal menjadi:
- `local_earned_map`: Jumlah `amount` dari transaksi positif (event, seminar, bonus).
- `local_redeemed_map`: Jumlah absolut `amount` dari transaksi negatif (`transaction_type='redeem'`).
Hitung:
- `total_p = v_points + b_points + local_earned` (Skor Klasemen - Gross XP).
- `redeemed_p = local_redeemed`.
- `available_p = max(0, total_p - redeemed_p)` (Saldo Poin Siap Ditukar).

- [ ] **Step 2: Modifikasi agregasi transaksi di `get_live_member_detail` (`koha_utils.py`)**
Pastikan detail profil anggota juga mengembalikan `total_p` (Gross), `available_p` (Net), dan `redeemed_p`.

- [ ] **Step 3: Verifikasi via Django shell**
Jalankan tes perhitungan untuk memastikan member dengan riwayat redeem memiliki `total_p > available_p`.

---

### Task 2: Sesuaikan Validasi Saldo di `leaderboard/views.py`

**Files:**
- Modify: `leaderboard/views.py:240-350`

**Interfaces:**
- Consumes: `get_live_members` dan `get_live_member_detail` dari `koha_utils.py`.
- Modifies: `get_member_total_points(cardnumber)` mengembalikan `available_p` (saldo siap tukar).

- [ ] **Step 1: Perbarui fungsi `get_member_total_points` di `views.py`**
Pastikan fungsi mengembalikan `m.get('available_p', m['total_p'])` agar validasi penukaran reward memeriksa sisa saldo belanja, bukan gross XP.

- [ ] **Step 2: Perbarui respons JSON di `api_member_detail` (`views.py`)**
Sertakan `available_points` dan `gross_points` dalam payload JSON respons agar frontend bisa menampilkannya.

- [ ] **Step 3: Verifikasi endpoint OTP (`/api/redeem/request-otp/` & `/api/redeem/confirm/`)**
Pastikan validasi saldo pada `api_request_otp` dan `api_verify_otp_and_redeem` memvalidasi terhadap sisa saldo `available_points`.

---

### Task 3: Sesuaikan Validasi Saldo di `leaderboard/integration_views.py`

**Files:**
- Modify: `leaderboard/integration_views.py:100-154`

**Interfaces:**
- Consumes: `get_member_total_points` (mengembalikan `available_p`).

- [ ] **Step 1: Pastikan `integration_redeem` menggunakan `available_points`**
Cek saldo dengan `available_points = get_member_total_points(member_id)`. Jika `available_points < reward.points_cost`, tolak dengan status 400.

- [ ] **Step 2: Update respons JSON `integration_redeem`**
Sertakan informasi `remaining_points` yang akurat setelah dipotong.

---

### Task 4: Perbarui Tampilan Frontend (Modal Profil & Katalog)

**Files:**
- Modify: `leaderboard/templates/leaderboard/index.html`
- Modify: `static/js/main.js`

- [ ] **Step 1: Tambahkan elemen informasi Saldo di Modal Profil (`index.html`)**
Tampilkan label jelas:
- **Skor Klasemen:** `<span id="modalGrossXP">200 XP</span>` (Peringkat Klasemen)
- **Saldo Belanja:** `<span id="modalAvailableXP">100 XP</span>` (Bisa Ditukar Merchandise)

- [ ] **Step 2: Perbarui script mapping di `static/js/main.js`**
Saat modal detail anggota dibuka, isi data `total_p` ke Skor Klasemen dan `available_p` ke Saldo Belanja Hadiah.

- [ ] **Step 3: Verifikasi tampilan di browser**
Buka homepage dan klik salah satu profil pemustaka untuk memastikan kedua angka tampil presisi dan informatif.

---

### Task 5: Pengujian Otomatis End-to-End

**Files:**
- Create: `scratch/test_model_b1.py`

- [ ] **Step 1: Buat script pengujian skenario Model B1**
Simulasikan skenario:
1. Member dengan kunjungan & seminar total 200 XP (Ranking 1).
2. Member menukar reward 100 XP.
3. Assert: Ranking member tetap Ranking 1 dengan `total_p == 200`.
4. Assert: Saldo `available_p == 100`.
5. Member mencoba menukar reward 150 XP -> Assert: Ditolak (saldo tidak cukup).
6. Member menukar reward 100 XP -> Assert: Berhasil, saldo `available_p == 0`.
7. Assert: Ranking member tetap Ranking 1 dengan `total_p == 200`.

- [ ] **Step 2: Jalankan pengujian di Docker container**
Command: `docker compose exec web python scratch/test_model_b1.py`
Expected: Seluruh assertion lolos (Exit code 0).

- [ ] **Step 3: Bersihkan file scratch test**
Hapus `scratch/test_model_b1.py` setelah pengujian sukses.

