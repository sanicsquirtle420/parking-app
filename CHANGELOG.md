# Changelog — Database Integration Branch

All changes made relative to Diego's branch (`parking-app-test-diego-2`).

---

## Database Schema (New Files)

- **`sql/schema.sql`** — Complete schema with 7 tables. Key additions over old `tables2.sql`: `polygon_id` and `zone` columns on `parking_lots` (bridges Diego's JSON map IDs to database rows), `VARCHAR(20)` for `users.role` instead of restrictive ENUM, `is_active`/`created_at` on users, `duration_days`/`display_color_hex` on permits, `assignment_id` auto-increment PK on `user_permits` with UNIQUE on `user_id` (one permit per user), `rule_source` on `parking_rules`, `offense_type`/`resolved_date`/`permit_id` on tickets.
- **`sql/seed_reference.sql`** — 9 permits with names matching Diego's JSON labels exactly (Faculty, Commuter Blue, Commuter Red, etc.), 10 demo users with bcrypt hashes, 9 user-permit assignments.
- **`sql/seed_lots_and_rules.sql`** — 277 parking lots from Diego's `lot_cords.json` transformed into database rows with computed centroids, capacities, and occupancy. Parking rules for all 9 zones. Sample occupancy log and tickets.
- **`sql/views.sql`** — 4 views: `vw_lot_utilization`, `vw_active_permit_assignments`, `vw_parking_rule_matrix`, `vw_permit_usage_summary`.
- **`sql/README.md`** — Documentation for load order and design decisions.
- **`sql/TEST_LOGINS.md`** — Plaintext demo credentials for team testing.

## Deleted Files

- **10 old SQL files removed** from `sql/`: `tables2.sql`, `tables_data.sql`, `parkingData.sql`, `parking_lots.sql`, `parking_rules.sql`, `admin_queries.sql`, `admin_views.sql`, `crud_operations.sql`, `parking.sql`, `user_engine.sql`. These used the old schema and would conflict with the new one.

## New Python Files

- **`database/queries/map_data.py`** — Two functions:
  - `get_map_lot_lookup()`: Queries `parking_lots` by `polygon_id` to provide real capacity/zone data to the map instead of hardcoded values.
  - `can_user_park_in_polygon(user_id, polygon_id)`: Rules-engine query that checks `user_permits` + `parking_rules` + `parking_lots` using current day/time, permit expiration, and `is_allowed` flag. Replaces Diego's string-equality permission check.
- **`utils/hash_password.py`** — CLI utility for generating bcrypt hashes.

## Modified Python Files

### `main.py`
- Imports `get_map_lot_lookup` from `map_data.py`.
- Uses `os.path.join` for JSON path (prevents file-not-found errors if working directory changes).
- Map now reads real `capacity`, `lot_name`, and `zone` from the database via `polygon_id` lookup. Falls back to JSON values if a lot isn't in the DB.

### `utils/lot_outlines.py`
- Imports `can_user_park_in_polygon` and `datetime`.
- Tooltip now calls `can_user_park_in_polygon(user_id, polygon_id)` which checks the `parking_rules` table using real-time day/time. Falls back to string comparison only for guest users (no `user_id`).
- Tooltip displays the timestamp of when the rule was checked (e.g., "Checked: Wed 02:35:17 PM").

### `utils/create_account_screen.py`
- **Bug fix**: Diego's version set `role=self.permit_type.text.strip().lower()` which stored values like `"faculty/staff"` — not a valid role. Fixed with `ROLE_BY_SELECTION` dictionary mapping selections to correct DB roles (`"student"`, `"faculty"`, `"visitor"`, `"admin"`).
- Added `PERMIT_LABEL_BY_SELECTION` dictionary so `user_data["permit"]` gets the correct permit label for map display.
- `user_data` now includes `user_id`, full name, and email (Diego's version only had email as username).
- Admin users route to `admin_dashboard` instead of the map.
- Skips `add_user()` for admin accounts (admins don't need parking permits).

### `utils/login_screen.py`
- Minor text fix: "Enter email and password" instead of "Enter User ID and Password".

### `utils/buttons.py`
- Added live clock in the sidebar showing current day and time, updating every second.

### `database/queries/parking.py`
- `get_available_parking()`: Added `up.expiration_date >= CURDATE()` and `pr.is_allowed = TRUE` checks (Diego's version didn't verify permit expiration or rule status).
- `add_user()`: Dynamically reads `duration_days` from the permits table for expiration calculation instead of hardcoding `"2026-07-31"`. Handles admin accounts by returning early.
- Removed bare `conn.close()` at module level that existed in the main branch (would crash on import).

### `database/queries/users.py`
- `gen_userid()`: Removed 5 DEBUG print statements. Uses parameterized queries (no SQL injection).
- `get_user()`: Joins to `user_permits` and `permits` to return `user_permit_name` in a single query.

### `database/queries/tickets.py`
- Added proper `try/except/finally` block with `cursor.close()` (was leaking cursor).

### `database/db.py`
- Added `USE_SSH_TUNNEL` environment variable support so the SSH tunnel can be explicitly enabled/disabled.
- Added `_wants_tunnel()` function for auto-detection when `USE_SSH_TUNNEL` is not set.
- Connection can now work both on Turing (no tunnel needed) and from a laptop (tunnel enabled).
- Switched from `mariadb` to `mysql.connector` (`import mysql.connector as mariadb`) since `mariadb` requires system C libraries that aren't available on Turing.

### `utils/admin_dashboard_screen.py`
- **Bug fix**: `self.details.shorten` and `self.details.max_lines` were set before `self.details` was created — crashed with `AttributeError` every time admin dashboard loaded.
- **Bug fix**: `selected_admin_lot` was stored on `self.manager` but read from `app` in `admin_lot_detail_screen.py` — crashed when clicking "Manage Lot".
- Replaced broken `RecycleView` with `ScrollView` + `BoxLayout` that reliably renders all 277 lot cards.
- Shows lot count in status label (e.g., "277 lots loaded").

### `requirements.txt`
- Removed `mariadb==1.1.14` (requires system C libraries).
- Removed `dotenv==0.9.9` (different package from `python-dotenv`, would shadow correct import).

### `.gitignore`
- Added `venv/` to ignored paths.

## Setup Notes

- Create a `.env` file (not tracked by git) with SSH and database credentials.
- Set `USE_SSH_TUNNEL=true` when running from laptop, `USE_SSH_TUNNEL=false` when running on Turing.
- Load SQL files in order: `schema.sql` -> `seed_reference.sql` -> `seed_lots_and_rules.sql` -> `views.sql`.
