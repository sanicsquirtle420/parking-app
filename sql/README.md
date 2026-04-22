# Teammate Parking Database Package

This package is a compatibility-first MariaDB handoff for the teammate parking app branches in:

- `/Users/jannatulferdous/Documents/teammate_progress/parking-app-main`
- `/Users/jannatulferdous/Documents/teammate_progress/parking-app-test-diego-2`
- `/Users/jannatulferdous/Documents/teammate_progress/parking-app-test-joshua`

Nothing in those project folders was modified to create this package.

## What this package optimizes for

- Keeps the table names and key column names their current Python queries already use.
- Keeps `parking_rules.rule_id` for the admin lot detail CRUD screens.
- Keeps `tickets.issue_date` for the ticket screen.
- Adds `parking_lots.polygon_id` so Diego's campus map ids can be joined to database rows later.
- Uses `users.role` as `VARCHAR(20)` instead of a strict enum so both the Diego and Joshua account flows can write role values without schema errors.
- Seeds permit names that match Diego's map labels exactly, so logins can map cleanly to the existing permit-to-polygon comparison.
- Preserves `permits.description` while also adding `duration_days`, because the current admin permit code still parses the first number from `description`.

## Files

- `schema.sql`: core schema
- `seed_reference.sql`: permits, demo users, active permit assignments
- `seed_lots_and_rules.sql`: 277 campus lot polygons transformed into database rows, plus rules, occupancy history, and sample tickets
- `views.sql`: helper views for analytics/reporting
- `TEST_LOGINS.md`: plaintext demo credentials for team testing
- `hash_password.py`: tiny bcrypt helper for creating more hashes later

## Load order

Run these files in order inside the MariaDB database the app is already configured to use:

1. `01_schema.sql`
2. `02_seed_reference.sql`
3. `03_seed_lots_and_rules.sql`
4. `04_views.sql`

## Notes

- `TEST_LOGINS.md` is for private team testing only because it contains plaintext demo passwords.
- The database stores only bcrypt hashes in `users.password_hash`.
- Lot names repeat across campus, so `polygon_id` is the stable bridge field for Diego's map data.
- The seeded permit catalog intentionally stays small and frontend-friendly. If the team later wants richer permit subtypes, they can layer that in after the UI stops relying on raw `permit_name` string matching.
