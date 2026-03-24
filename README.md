# 📚 LibraryRank — University Library Leaderboard

Django + MySQL/MariaDB leaderboard system built for **Koha ILS** universities.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              MySQL / MariaDB Server                  │
│                                                      │
│  ┌─────────────────┐     ┌──────────────────────┐   │
│  │   libraryrank   │     │        koha          │   │
│  │  (Django app DB)│     │   (Koha ILS — READ   │   │
│  │  Django writes  │     │    ONLY, never        │   │
│  │  here via ORM   │     │    touched by ORM)    │   │
│  └────────┬────────┘     └──────────┬───────────┘   │
│           │                         │               │
└───────────┼─────────────────────────┼───────────────┘
            │                         │
            │    sync_from_koha       │
            │◄────────────────────────┘
            │  reads Koha borrowers, issues,
            │  statistics → writes to libraryrank
            ▼
     LibraryRank Web App
     (leaderboard, rankings, exports)
```

---

## 🚀 Quick Start — Run Locally

### Step 1 — Prerequisites

Install these first:
- **Python 3.11+** → https://python.org
- **MySQL or MariaDB** → https://mariadb.org (or use your existing Koha server)
- A MySQL client tool: **MySQL Workbench**, **DBeaver**, **HeidiSQL**, or `mysql` CLI

---

### Step 2 — Create the LibraryRank database

Open MySQL Workbench (or any MySQL client) and run:

```sql
-- Create the LibraryRank app database
CREATE DATABASE libraryrank
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Create a dedicated user for the Django app
CREATE USER 'libraryrank_user'@'localhost' IDENTIFIED BY 'yourpassword';
GRANT ALL PRIVILEGES ON libraryrank.* TO 'libraryrank_user'@'localhost';

-- Create a READ-ONLY user for Koha (ask your Koha admin if you don't have access)
CREATE USER 'koha_reader'@'localhost' IDENTIFIED BY 'readonlypassword';
GRANT SELECT ON koha.* TO 'koha_reader'@'localhost';

FLUSH PRIVILEGES;
```

> If the Koha database is on a **different server**, change `localhost` to the server's IP address.

---

### Step 3 — Unzip and set up virtual environment

```bash
# Unzip the project
unzip libraryrank_django.zip
cd libraryrank

# Create virtual environment
python -m venv venv

# Activate it:
# Windows PowerShell:
venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat
# macOS / Linux:
source venv/bin/activate
```

---

### Step 4 — Install dependencies

```bash
pip install -r requirements.txt
```

> **Windows note:** If `mysqlclient` fails to install, try:
> ```bash
> pip install mysqlclient --only-binary :all:
> ```
> Or download the `.whl` from https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient

---

### Step 5 — Configure environment

```bash
# Copy the example env file
copy .env.example .env        # Windows
cp .env.example .env          # macOS/Linux
```

Open `.env` and fill in your values:

```env
# Django
SECRET_KEY=any-long-random-string-here
DEBUG=True

# LibraryRank app database (the one you just created)
DB_NAME=libraryrank
DB_USER=libraryrank_user
DB_PASSWORD=yourpassword
DB_HOST=127.0.0.1
DB_PORT=3306

# Koha database (read-only)
KOHA_DB_NAME=koha
KOHA_DB_USER=koha_reader
KOHA_DB_PASSWORD=readonlypassword
KOHA_DB_HOST=127.0.0.1
KOHA_DB_PORT=3306

# Skip CAS login for local development
CAS_LOCAL_DEV=True
```

---

### Step 6 — Run migrations

```bash
python manage.py migrate
```

This creates all LibraryRank tables inside the `libraryrank` MySQL database.
It **never touches** your Koha database.

---

### Step 7 — Create admin account

```bash
python manage.py createsuperuser
```

---

### Step 8 — Option A: Load demo data (no Koha needed)

```bash
python manage.py seed_demo_data
```

This fills the `libraryrank` database with realistic fake data so you can
see the full leaderboard UI immediately.

### Step 8 — Option B: Sync from real Koha data

```bash
# Sync last 30 days of data from Koha
python manage.py sync_from_koha

# Or sync everything (all history)
python manage.py sync_from_koha --full

# Preview without writing anything
python manage.py sync_from_koha --dry-run
```

---

### Step 9 — Start the server

```bash
python manage.py runserver
```

Open → **http://localhost:8000**
Admin → **http://localhost:8000/admin**

---

## 🔄 Koha Sync Details

The `sync_from_koha` command reads these Koha tables:

| Koha Table | What it reads | Where it goes |
|---|---|---|
| `borrowers` | Patron name, card number, category, branch | `Member` table |
| `categories` | Category description (Student/Lecturer/Staff) | role mapping |
| `branches` | Branch codes → faculty names | `Faculty` table |
| `biblio` + `biblioitems` | Book title, author, ISBN | `Book` table |
| `statistics` | Checkout/return events → visits | `Visit` table |
| `issues` | Active checkouts | `BorrowRecord` |
| `old_issues` | Returned checkouts | `BorrowRecord` |

### Finding your Koha patron category codes

Run this in your Koha MySQL:
```sql
SELECT categorycode, description, category_type FROM categories ORDER BY categorycode;
```

Then update your `.env`:
```env
KOHA_STUDENT_CATEGORIES=MHS,S,STUDENT
KOHA_LECTURER_CATEGORIES=DSN,L,DOSEN
KOHA_STAFF_CATEGORIES=STF,KARYAWAN,PEGAWAI
```

### Scheduling automatic sync (Linux cron)

```bash
# Sync every night at 1am
crontab -e

# Add this line:
0 1 * * * /path/to/venv/bin/python /path/to/libraryrank/manage.py sync_from_koha >> /var/log/libraryrank_sync.log 2>&1
```

---

## 🔐 CAS SSO Setup (Production)

1. Set `CAS_LOCAL_DEV=False` in `.env`
2. Set `CAS_SERVER_URL=https://sso.your-university.ac.id/cas/`
3. Ask IT to whitelist your app's callback URL:
   `https://yourdomain.com/accounts/callback/`

---

## 🌐 API Endpoints

All support `?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD&q=search`

| Endpoint | Returns |
|---|---|
| `GET /api/overview/` | Stats, nominations, combined top-15 |
| `GET /api/role/student/` | Student rankings |
| `GET /api/role/lecturer/` | Lecturer rankings |
| `GET /api/role/staff/` | Staff rankings |
| `GET /api/books/` | Most borrowed books + top borrowers |
| `GET /api/faculties/` | Faculty rankings + top student per faculty |
| `GET /api/member/<id>/` | Member profile + recent borrows |
| `GET /export/excel/` | Download `.xlsx` |
| `GET /export/pdf/` | Download PDF |

---

## 🛠️ Tech Stack

| | |
|---|---|
| Backend | Python 3.11+, Django 5.0 |
| Database | MySQL 8+ / MariaDB 10.6+ |
| Koha ILS | Read-only via raw SQL (same MySQL server) |
| SSO | CAS via `django-cas-ng` |
| Excel | `openpyxl` |
| PDF | `ReportLab` |
| Static files | `WhiteNoise` |
| Frontend | Vanilla JS + CSS |

---

## ❓ Troubleshooting

**`django.db.utils.OperationalError: Access denied for user`**
→ Wrong password in `.env`. Double-check `DB_PASSWORD`.

**`ModuleNotFoundError: No module named 'MySQLdb'`**
→ Run `pip install mysqlclient`. On Windows try `pip install mysqlclient --only-binary :all:`

**`sync_from_koha` says "Cannot connect to Koha"**
→ Check `KOHA_DB_*` values in `.env`. Make sure the `koha_reader` user has `SELECT` on `koha.*`.

**Leaderboard shows demo data instead of real data**
→ Run `python manage.py sync_from_koha` first. Demo data is shown only when the database is empty.

**`No module named 'django_cas_ng.urls'`**
→ This is a known mistake — the project uses `django_cas_ng.views` directly in `urls.py`, NOT `include('django_cas_ng.urls')`. The current code is already correct.
