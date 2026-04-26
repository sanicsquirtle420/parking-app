# Teammate Diff Summary

This summary compares this package against the teammate branches outside this folder:

- Diego: `/Users/jannatulferdous/Documents/teammate_progress/parking-app-test-diego-2`
- Joshua: `/Users/jannatulferdous/Documents/teammate_progress/parking-app-test-joshua`

`CHANGELOG.md` was used as context for the Diego-to-package history and was left unchanged.

## Big Picture

This package is not just one teammate branch copied over. It is a merged integration branch with:

- a new SQL/database package layered on top of the app
- several Diego flow fixes kept and extended
- some Joshua admin UI/query work retained
- a few files left identical to both teammates
- a few newer fixes added after the original changelog, especially around signup day-pass handling

## New In This Package Only

These files do not exist in either Diego's or Joshua's folder:

- `.env.example`
- `CHANGELOG.md`
- `database/queries/map_data.py`
- `sql/schema.sql`
- `sql/seed_reference.sql`
- `sql/seed_lots_and_rules.sql`
- `sql/views.sql`
- `sql/README.md`
- `sql/TEST_LOGINS.md`
- `utils/hash_password.py`

What these add:

- a compatibility-first schema and seed set
- database-backed lot lookup and parking-rule evaluation
- setup docs and demo credentials
- a password-hash helper

## Files Removed Relative To Team Branches

These older SQL files still exist in Diego's and/or Joshua's folders but are not part of this package:

- `sql/admin_queries.sql`
- `sql/admin_views.sql`
- `sql/crud_operations.sql`
- `sql/parking.sql`
- `sql/parkingData.sql`
- `sql/tables2.sql`
- `sql/tables_data.sql`
- `sql/user_engine.sql`

Diego-only files not carried into this package:

- `sql/parking_lots.sql`
- `sql/parking_rules.sql`

Joshua-only files not carried into this package:

- `backup.sql`
- `backup_filename.sql`

## Unchanged From Both Teammates

These files match both Diego's and Joshua's versions:

- `database/queries/admin_analytics.py`
- `database/queries/admin_dashboard.py`
- `database/queries/admin_lot_detail.py`
- `git.md`
- `utils/admin_lot_detail_screen.py`
- `utils/extract/extract_lots.py`
- `utils/extract/fix_json.py`
- `utils/lot_cords.json`
- `utils/tickets_screen.py`

## Files That Mostly Follow Diego

These match Diego directly, or are effectively Diego's version in substance:

- `utils/admin_analytics_screen.py`
- `utils/admin_permits_screen.py`

Note:

- `utils/admin_permits_screen.py` differs from Joshua only by file-ending formatting, not by meaningful behavior.

## Files Modified Beyond Both Teammates

These exist in both teammate branches but the package version is materially different from both:

- `.gitignore`
- `README.md`
- `database/db.py`
- `database/queries/admin_permits.py`
- `database/queries/parking.py`
- `database/queries/tickets.py`
- `database/queries/users.py`
- `main.py`
- `requirements.txt`
- `utils/admin_dashboard_screen.py`
- `utils/admin_navigation.py`
- `utils/buttons.py`
- `utils/create_account_screen.py`
- `utils/login_screen.py`
- `utils/lot_outlines.py`

## Change Areas

### 1. Database Layer Replaced The Old SQL Layout

Compared to both teammate branches, this package replaces the older fragmented SQL setup with:

- `sql/schema.sql` for the full schema
- `sql/seed_reference.sql` for permits, demo users, and permit assignments
- `sql/seed_lots_and_rules.sql` for lot/rule seed data
- `sql/views.sql` for reporting views

This is the largest structural difference from both teammate folders.

### 2. Map Access Now Uses Real Database Rules

Compared to both Diego and Joshua:

- `main.py` now loads lot metadata from the database through `database/queries/map_data.py`
- `utils/lot_outlines.py` checks actual parking eligibility by `user_id` and `polygon_id`
- the map tooltip shows when the parking rule was checked

This replaces the earlier map-side permit-name comparison with database-backed rule checks.

### 3. Signup And Login Flow Changed From Both Teammates

Compared to Diego:

- `utils/create_account_screen.py` no longer writes invalid roles like `faculty/staff`
- account type is mapped cleanly to database roles
- non-admin signup now assigns a temporary day pass instead of calling the older direct permit insert path
- admin signup routes to the admin dashboard

Compared to Joshua:

- Joshua's role + permit selection flow was simplified into one account-type selector
- dynamic permit dropdown behavior was removed
- signup now uses a fixed temporary `Free Day Pass` for new non-admin users

Also added after the original changelog:

- `database/queries/users.py` now auto-repairs the `DAY` permit and its rules if the configured database is missing them
- expired permits are no longer treated as active during login
- the signup pass is enforced as a real 24-hour window instead of a date-only check

### 4. Permit Validity Checks Are Stricter Now

Compared to both teammate branches:

- `database/queries/parking.py` now checks `status = 'active'`
- `database/queries/parking.py` now checks `expiration_date >= NOW()`
- `database/queries/map_data.py` uses the same active/non-expired logic
- `database/queries/users.py` only joins active, non-expired permits for login hydration

This is especially important for the new-user 24-hour pass flow.

### 5. User ID Logic Changed

Compared to Diego and Joshua:

- `database/queries/users.py` rewrites `gen_userid()`
- IDs now use role-based prefixes: `stu`, `fac`, `adm`, `vis`
- the function uses the max existing numeric suffix instead of the older gap-filling logic

Note:

- this is functionally different from some of the existing seeded IDs in the live database, which still include values like `cb001`, `cr001`, and `admin001`

### 6. Admin Permit Query Logic Was Extended

Compared to Joshua's admin permit work:

- `database/queries/admin_permits.py` now reads `duration_days` first instead of depending only on parsing `description`
- admin assignments write `status`, `assigned_by`, and `note`
- renewals use the same normalized duration lookup

The screen file `utils/admin_permits_screen.py` stayed effectively the same, but the backing query logic became more database-aware.

### 7. Admin Dashboard / Navigation Changed

Compared to both teammates:

- `utils/admin_dashboard_screen.py` was reworked around a plain `ScrollView` + `BoxLayout`
- lot cards are built more defensively
- the status label now reports lot loading state and loaded count
- `utils/admin_navigation.py` now handles scheduled refresh cancellation and token-based refresh delivery more safely

This area is partly aligned with Joshua's refresh work, but the final package version is not identical to either teammate.

### 8. Analytics Screen Stayed Closer To Diego

Compared to Joshua:

- `utils/admin_analytics_screen.py` does not preserve Joshua's final background-loading/threading structure as-is
- the current package version matches Diego's version instead

### 9. Environment And Dependency Setup Changed

Compared to both teammate branches:

- `database/db.py` now loads `.env` from the project root or `database/`
- config validation errors are more explicit
- `mysql.connector` is used instead of the standalone `mariadb` import
- `README.md` now documents the new env file shape and SQL load order
- `.env.example` was added
- `requirements.txt` drops `dotenv==0.9.9`
- `requirements.txt` drops `mariadb==1.1.14`
- `.gitignore` adds `venv/`

## Practical Read Of The Merge

If you want the shortest interpretation of what happened:

- the SQL/database architecture is new and package-specific
- the map access logic moved away from frontend string matching into database rule checks
- signup/login were refit around the new schema
- Joshua's admin permits UI was largely retained
- Diego's analytics screen was retained
- several core query files were rewritten beyond both teammates
- the newest post-changelog fixes mainly target the first-signup `Free Day Pass` flow

## Important Post-Changelog Update

The current package now includes one important fix that is newer than the existing `CHANGELOG.md`:

- if the live database is missing the `DAY` permit, signup no longer fails; the package now recreates that permit and its visitor-lot rules automatically before assigning the 24-hour pass

That behavior is present in:

- `database/queries/users.py`
- `database/queries/map_data.py`
- `database/queries/parking.py`
