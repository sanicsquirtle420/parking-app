# Draft Changelog — Parking Session & UI Update

All changes made relative to the current integrated package branch (see `CHANGELOG.md` for prior history and `TEAMMATE_DIFF_SUMMARY.md` for cross-branch context).

---

## New Python Files

- **`database/queries/parking_sessions.py`** — Complete parking session management module. Six functions:
  - `start_parking_session(user_id, lot_id, polygon_id, lot_name)`: Inserts a row into `parking_sessions`, increments `current_occupancy` on `parking_lots`. Prevents duplicate active sessions (one session per user at a time). Returns session dict on success, `None` if the lot is full or user already has an active session elsewhere.
  - `end_parking_session(user_id)`: Sets `end_time = NOW()` on the active session and decrements `current_occupancy` using `GREATEST(... - 1, 0)` to avoid negative values. Returns `True`/`False`.
  - `get_active_session(user_id)`: Returns the user's active (un-ended) session dict or `None`. Used by the map tooltip and the sidebar session indicator.
  - `get_lot_current_occupancy(lot_id)`: Returns real-time occupancy, capacity, and spots left for a single lot.
  - `ensure_parking_sessions_table()`: `CREATE TABLE IF NOT EXISTS` for `parking_sessions` with indexes on `(user_id, end_time)` and `(lot_id)`. Called once at app startup from `main.py`.

## Modified Python Files

### `main.py`
- **New import**: `ensure_parking_sessions_table` from `database.queries.parking_sessions`.
- `MainApp.build()`: Added `self.active_parking_session = None` to track the logged-in user's current session app-wide.
- `MainApp.build()`: Added `ensure_parking_sessions_table()` call at startup (wrapped in try/except so the app still launches if the DB is unreachable).
- Lot info dict passed to `LotOutline` now includes `lot_id` and `current_occupancy` (previously only had `polygon_id`, `name`, `capacity`, `permit_required`).

### `utils/login_screen.py`
- **Removed**: `guest_btn = red_button("Continue as Visitor")` and its `on_release` binding (line 57–58 in the previous version).
- **Removed**: `root.add_widget(guest_btn)` (line 64 in the previous version).
- **Removed**: `guest(self, instance)` method (lines 116–123 in the previous version) which set `user_data` to a hardcoded Guest/Visitor dict and navigated to the main screen without authentication.
- Login screen now only shows two buttons: "Login" and "Create Account".

### `utils/lot_outlines.py`
- **New imports**: `BoxLayout`, `Button` from Kivy; `start_parking_session`, `end_parking_session`, `get_active_session` from `database.queries.parking_sessions`.
- `__init__`: Explicitly initializes `self._tooltip = None`.
- `on_mouse`: Added logic to keep the tooltip visible when the cursor moves from the lot polygon into the tooltip widget (prevents flicker when clicking buttons).
- **New method** `_on_park_here(self, instance)`: Calls `start_parking_session()` with the lot's `lot_id`, `polygon_id`, and `name`. Stores result on `app.active_parking_session`. Calls `main_screen.refresh_sidebar()` to update the sidebar. Hides the tooltip after action.
- **New method** `_on_end_session(self, instance)`: Calls `end_parking_session(user_id)`. Clears `app.active_parking_session`. Refreshes sidebar. Hides tooltip.
- `show_tooltip`: Completely reworked from a single `Label` to a `BoxLayout` containing:
  - An info label showing lot name, capacity, **spots left** (new), permit required, timestamp, and eligibility.
  - A conditional action button:
    - **"Park Here"** (green) if user can park and has no active session — this is the only way to start a parking session.
    - **"End Session"** (red) if user is currently parked in this specific lot.
    - **"Parked in: [lot name]"** info label if user is parked in a different lot.
    - No button if user cannot park or is not logged in.
- Tooltip background opacity increased from `0.75` to `0.85` for better readability over the map.

### `utils/buttons.py`
- **New imports**: `ScrollView` from Kivy; `end_parking_session`, `get_active_session` from `database.queries.parking_sessions`; `get_user_allowed_lots` from `database.queries.map_data`.
- **New constant**: `LOT_ITEM_HEIGHT = 36`.
- `__init__`: Added session indicator label (`self.session_label`) below the user info. Added "End Parking Session" button (`self.end_session_btn`) that is only visible when the user has an active session. Added "Available Lots" header label. Added `ScrollView` containing a `BoxLayout` (`self.lot_list_box`) for the lot list. Calls `_load_lot_list()` on a 0.5-second delay after init.
- Reduced `user_label` height from `150` to `100` and `clock_label` height from `50` to `40` to make room for the lot list.
- Added `size_hint_y=None, height=40` to the anchor layout wrapping the title label.
- **New method** `_load_lot_list(dt=None)`: Queries only the lots the logged-in user is allowed to park in via `get_user_allowed_lots(user_id)` (same permit/rules/day/time logic as the map tooltip). Sorts by name and builds a scrollable list of clickable buttons. Each button shows the lot name only; clicking it pans and zooms the map to that lot's coordinates. Shows "No lots available for your permit" if the user has no allowed lots. No parking actions from the sidebar — users must hover on the map lot to start a session.
- **New method** `_pan_to_lot(lat, lon)`: Centers the map on the given lat/lon and zooms to level 17 if currently zoomed out further.
- **New method** `_on_end_session(instance)`: Ends the active session, clears `app.active_parking_session`, refreshes sidebar.
- **New method** `_update_session_label()`: Shows/hides the session indicator label and the "End Parking Session" button based on whether the user has an active parking session. Displays lot name and start time.
- `update_user_info()`: Now also calls `_update_session_label()` and `_load_lot_list()` so the sidebar fully refreshes when a session starts or ends.
- `go_to_login()`: Now also clears `app.active_parking_session = None` on logout.
- `on_parent()`: Now also calls `_update_session_label()`.

### `database/queries/map_data.py`
- `get_map_lot_lookup()`: Added `lot_id`, `latitude`, and `longitude` to the SELECT query. Previously only returned `polygon_id`, `lot_name`, `zone`, `capacity`, `current_occupancy`. The returned dict values now include `lot_id` (for parking sessions) and `latitude`/`longitude` (for sidebar map-pan).
- **New function** `get_user_allowed_lots(user_id)`: Bulk version of `can_user_park_in_polygon` — returns all lots a user can park in right now in a single query. Uses the same `user_permits → parking_rules → parking_lots` join with `is_allowed`, `status = 'active'`, `expiration_date >= NOW()`, `FIND_IN_SET(day)`, and `BETWEEN start_time AND end_time` checks. Admin users bypass the rules and get all lots. Returns a dict keyed by `polygon_id` (same shape as `get_map_lot_lookup`). Used by the sidebar to show only permitted lots instead of all 277.
- `can_user_park_in_polygon()`: **Bug fix** — added admin role bypass. The function now queries the `users` table first; if `role = 'admin'`, it returns `True` immediately, granting admins parking access to **all lots at all times**. This is a code-side override only — no rows were added to `user_permits` or `parking_rules` for admin users (they still have none). The admin bypass is intentional: the database schema does not define an admin-specific permit or parking rules, so without this check admins would always be denied. Non-admin users still go through the full `user_permits → parking_rules → parking_lots` join with day/time checks as before.

## Database Changes

### New Table: `parking_sessions`
- Now defined in `sql/schema.sql` alongside the other tables. `DROP TABLE IF EXISTS parking_sessions` added at the top of the drop order (before `tickets`), and the `CREATE TABLE` statement added at the bottom (after `tickets`) so the table can be reset the same way as everything else.
- The schema in `schema.sql` includes proper foreign key constraints: `fk_parking_sessions_user` references `users(user_id)` and `fk_parking_sessions_lot` references `parking_lots(lot_id)`, both with `ON DELETE CASCADE ON UPDATE CASCADE`.
- The Python function `ensure_parking_sessions_table()` in `database/queries/parking_sessions.py` still exists as a fallback — it runs `CREATE TABLE IF NOT EXISTS` at app startup so the table gets created even if someone forgets to run the SQL. The Python version does not include foreign keys to stay self-contained; the `schema.sql` version is the canonical definition with full constraints.
- Schema:
  - `session_id INT AUTO_INCREMENT PRIMARY KEY`
  - `user_id VARCHAR(20) NOT NULL`
  - `lot_id INT NOT NULL`
  - `polygon_id VARCHAR(50)` — links to the map polygon
  - `lot_name VARCHAR(100)` — denormalized for display convenience
  - `start_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP`
  - `end_time DATETIME DEFAULT NULL` — NULL means session is active
  - Indexes: `idx_parking_sessions_user_active (user_id, end_time)`, `idx_parking_sessions_lot (lot_id)`
  - Foreign keys: `user_id → users(user_id)`, `lot_id → parking_lots(lot_id)`
- Active sessions are identified by `end_time IS NULL`.
- Starting a session increments `parking_lots.current_occupancy`; ending decrements it.

### Modified SQL File: `sql/schema.sql`
- Added `DROP TABLE IF EXISTS parking_sessions` at line 1 of the drop order (before all other drops, since it references `users` and `parking_lots`).
- Added `CREATE TABLE parking_sessions` after the `tickets` table definition, with full foreign key constraints to `users` and `parking_lots`.

## Behavioral Summary

- Users must log in or create an account to use the app (no more guest/visitor bypass).
- Logged-in users start a parking session by hovering over a lot on the map and clicking "Park Here" in the tooltip.
- The sidebar shows a scrollable list of only the lots the user is permitted to park in (filtered by permit type, day of week, and time of day — same rules as the map tooltip). Clicking a lot name pans and zooms the map to that lot so the user can then hover and start a session.
- Only one active session per user at a time.
- Sessions persist across logout — the user must manually end the session.
- Ending a session can be done from the map tooltip (hover over the lot where parked) or from the sidebar's "End Parking Session" button.
- The sidebar shows a session indicator (lot name + start time) when the user is actively parked.
- Admin users can park in **all lots at all times**. This is a code-side role check in `can_user_park_in_polygon()` — the database has no admin permit or parking rules for admins, so the function bypasses the `user_permits → parking_rules` join entirely when `users.role = 'admin'`.
- Occupancy changes are reflected in real time via `parking_lots.current_occupancy`.

## Files Not Modified

- `CHANGELOG.md` — not modified per instructions.
- `TEAMMATE_DIFF_SUMMARY.md` — not modified per instructions.
- All admin screens (`admin_dashboard_screen.py`, `admin_analytics_screen.py`, `admin_lot_detail_screen.py`, `admin_permits_screen.py`, `admin_navigation.py`) — not modified per instructions.
- `database/db.py` — unchanged.
- `database/queries/users.py` — unchanged.
- `database/queries/parking.py` — unchanged.
- `database/queries/tickets.py` — unchanged.
- `utils/create_account_screen.py` — unchanged.
- `utils/tickets_screen.py` — unchanged.
- `utils/hash_password.py` — unchanged.
