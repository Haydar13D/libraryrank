# Design Spec: Librarian Exclusion Toggle & Redemption Permission

**Date:** 2026-11-10  
**Author:** Antigravity & User  
**Status:** Approved  

## 1. Problem Statement
In the Koha library system, library staff are assigned the category code `LIBRARIAN` ("Staf Perpustakaan"). Because library staff work daily in the library and frequently issue/return books for operational purposes (e.g. cataloging, barcode testing, repairs, displays), their visit and borrow metrics naturally outpace ordinary library patrons (students, lecturers, general staff/tendik).

Displaying librarians on public leaderboards and Kiosk TVs demotivates patrons and gives the perception that the leaderboard is unfair. However, library staff should still be recognized in the system, retain access to their individual profiles, and optionally be allowed to redeem merchandise or appear in rankings during special internal events.

## 2. Goals & Non-Goals
### Goals
- Provide admin-configurable toggles in `LeaderboardConfig` to:
  1. Hide librarians (`categorycode == 'LIBRARIAN'`) from public leaderboards & Kiosk TV.
  2. Toggle whether librarians can redeem merchandise using their accumulated points.
  3. Exclude specific additional cardnumbers/NIPs manually via comma/newline-separated list.
- Keep point calculation intact in the background so no historical activity data is lost if the toggle is turned off.
- Allow patrons to search for themselves (`search_q`) even if excluded from public top rankings.

### Non-Goals
- Deleting or zeroing out librarians' points in Koha or the database.
- Affecting non-librarian campus staff (`STAF1`, `STAF2`, etc.), who remain legitimate competitors in the Tendik/Staff tab.

## 3. Architecture & Data Model Changes
### 3.1 `LeaderboardConfig` Model (`leaderboard/models.py`)
Add fields:
- `exclude_librarians_from_leaderboard = models.BooleanField(default=True, verbose_name="Sembunyikan Staf Perpustakaan dari Leaderboard", help_text="Jika aktif, anggota dengan kategori LIBRARIAN tidak akan muncul di podium & tabel perangkingan publik.")`
- `allow_librarians_to_redeem = models.BooleanField(default=True, verbose_name="Izinkan Staf Perpustakaan Menukar Merchandise", help_text="Jika aktif, staf perpustakaan tetap dapat menggunakan saldo poinnya untuk menukarkan merchandise.")`
- `excluded_cardnumbers = models.TextField(blank=True, default="", verbose_name="NIM / Cardnumber Dikecualikan Tambahan", help_text="Daftar nomor kartu yang ingin disembunyikan dari leaderboard secara manual (pisahkan dengan koma atau baris baru).")`

### 3.2 Leaderboard Filtering (`leaderboard/koha_utils.py`)
In `get_live_members(date_from, date_to, search_q=None)`:
- Read active config from `LeaderboardConfig`.
- If `search_q` is None or empty (i.e. generating public leaderboard / podium):
  - If `config.exclude_librarians_from_leaderboard` is True and `cat.upper() == 'LIBRARIAN'`: `continue`
  - If patron's cardnumber is in `config.get_excluded_cardnumbers_list()`: `continue`
- If `search_q` is present: allow lookup so the patron can view their own profile and redeem points.

### 3.3 Redemption Permission Check (`leaderboard/views.py`)
In `api_redeem_request_otp`:
- Check if patron's category is `LIBRARIAN`.
- If `cat == 'LIBRARIAN'` and `config.allow_librarians_to_redeem is False`:
  - Return HTTP 403 / JsonResponse `{'error': 'Penukaran merchandise saat ini diprioritaskan untuk mahasiswa dan sivitas akademika umum.'}`

## 4. Verification
- Test toggling `exclude_librarians_from_leaderboard` ON and OFF: verify that librarian accounts disappear from and reappear on `api_role_leaderboard('staff')`.
- Test `excluded_cardnumbers`: verify that listed cardnumbers disappear from rankings.
- Test `allow_librarians_to_redeem` false: verify OTP request is rejected with explanatory message.
- Test `allow_librarians_to_redeem` true: verify OTP request proceeds normally.

