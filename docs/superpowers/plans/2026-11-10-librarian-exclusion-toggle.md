# Librarian Exclusion Toggle & Redemption Permission Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement admin-configurable toggles to exclude library staff (LIBRARIAN) and custom cardnumbers from public leaderboards, while controlling merchandise redemption access.

**Architecture:** Extend `LeaderboardConfig` model with boolean and text fields; integrate filtering in `leaderboard/koha_utils.py` for public ranking queries; enforce redemption permissions in `leaderboard/views.py`.

**Tech Stack:** Django 5, MySQL (Docker), Koha Database, Django Admin.

**Spec:** `docs/superpowers/specs/2026-11-10-librarian-exclusion-toggle-design.md`

## Global Constraints
- Do not lose or delete any Koha activity or point records for librarians.
- Backward compatibility: when `search_q` is used to look up a patron profile, librarians can still be found.
- Non-librarian university staff (`STAF1`, `STAF2`) must remain visible in the Tendik/Staff tab.

## Review Focus
1. `config.exclude_librarians_from_leaderboard` is True: no patrons with `categorycode == 'LIBRARIAN'` appear in `api_role_leaderboard('staff')` or overview.
2. `config.exclude_librarians_from_leaderboard` is False: librarians reappear in staff rankings.
3. `config.excluded_cardnumbers`: specific cardnumbers listed are excluded even if they are students or non-librarians.
4. Patron search `api_member_detail(cardnumber)`: librarians can still view their details regardless of the exclusion toggle.
5. Redemption: when `allow_librarians_to_redeem` is False, OTP request is blocked for librarians; when True, OTP request is allowed.

---

### Task 1: Update LeaderboardConfig Model and Migrations
**Files:**
- Modify: `leaderboard/models.py:749-790`
- Modify: `leaderboard/admin.py`

- [ ] **Step 1: Add new fields to LeaderboardConfig in `leaderboard/models.py`**
  Add:
  - `exclude_librarians_from_leaderboard` (BooleanField, default=True)
  - `allow_librarians_to_redeem` (BooleanField, default=True)
  - `excluded_cardnumbers` (TextField, blank=True, default='')
  - Helper method `get_excluded_cardnumbers_set()` returning a set of uppercase stripped cardnumbers.
  - Helper classmethod `get_config()` returning the active or default config instance.

- [ ] **Step 2: Generate and apply Django migrations**
  Run `docker-compose exec -T web python manage.py makemigrations` and `migrate`.

- [ ] **Step 3: Update `LeaderboardConfigAdmin` in `leaderboard/admin.py`**
  Ensure the new fields are neatly organized into fieldsets in the Django admin interface.

---

### Task 2: Implement Leaderboard Filtering in Koha Utils
**Files:**
- Modify: `leaderboard/koha_utils.py:270-340`

- [ ] **Step 1: Update `get_live_members()` to respect exclusion rules**
  - Fetch active config via `LeaderboardConfig.get_config()`.
  - When `not search_q`:
    - If `config.exclude_librarians_from_leaderboard` and `cat_upper == 'LIBRARIAN'`: `continue`.
    - If `card_clean in excluded_cards_set`: `continue`.
  - When `search_q` is present: do not filter by exclusion so patron search & detail still work.

- [ ] **Step 2: Include `categorycode` in the member dictionary return**
  Ensure `'categorycode': cat_upper` is included in each member dictionary so views/APIs can access it directly.

---

### Task 3: Enforce Redemption Permission in Views
**Files:**
- Modify: `leaderboard/views.py: api_redeem_request_otp`

- [ ] **Step 1: Check `allow_librarians_to_redeem` before sending OTP**
  In `api_redeem_request_otp`:
  - Retrieve the patron's category code via Koha or `get_live_member_detail`.
  - If category is `LIBRARIAN` and `config.allow_librarians_to_redeem is False`:
    - Return `JsonResponse({'error': 'Penukaran merchandise saat ini diprioritaskan untuk mahasiswa dan sivitas akademika umum.'}, status=403)`

---

### Task 4: End-to-End Automated Verification
**Files:**
- Create: `scratch/test_librarian_exclusion.py`

- [ ] **Step 1: Write automated test script**
  Verify:
  1. Toggle ON: librarians absent from public leaderboard list.
  2. Toggle OFF: librarians present in public leaderboard list.
  3. Custom cardnumber exclusion works.
  4. Redemption toggle ON vs OFF works as expected.
  5. Search/profile detail continues to work for librarians.
- [ ] **Step 2: Run test in container and confirm all assertions pass**
- [ ] **Step 3: Clean up scratch test file and commit changes**

