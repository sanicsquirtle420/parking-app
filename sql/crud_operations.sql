-- ============================================================
-- crud_operations.sql
-- Ole Miss Campus Parking App — Admin CRUD Operations
-- ============================================================
--
-- PURPOSE:
-- This file contains every INSERT, UPDATE, and DELETE query
-- the frontend admin panel needs. Each query is organized by
-- which PAGE and BUTTON triggers it. The frontend team should
-- treat each query as a template — replace the {placeholder}
-- values with actual form inputs from the admin UI.
--
-- HOW TO USE THIS FILE:
-- 1. Find the page your component lives on (Page 1, 2, or 3)
-- 2. Find the button/action the admin clicks
-- 3. Use the query template, replacing {placeholders} with
--    the values from the admin's form fields
-- 4. Every query includes a VALIDATION query to run BEFORE
--    the actual operation to prevent bad data
--
-- PAGES OVERVIEW:
-- Page 1: Dashboard (READ only — uses admin_views.sql)
--         One button: "Add New Lot" → opens blank Page 2
-- Page 2: Lot Detail (CRUD for lots + rules + occupancy)
-- Page 3: Permits & Users (CRUD for permits + user permits)
-- Page 4: Analytics (READ only — uses admin_views.sql)
--
-- EXISTING FILES THE FRONTEND ALSO NEEDS:
-- admin_views.sql  → 5 views that power the dashboard/analytics
-- admin_queries.sql → READ queries for admin insights
-- user_engine.sql   → student/faculty/visitor facing queries
--
-- ============================================================


-- ************************************************************
-- PAGE 2: LOT DETAIL
-- Admin clicks a lot card on Page 1 dashboard, lands here.
-- This page shows: lot info, rules table, occupancy section.
-- ************************************************************


-- ============================================================
-- PAGE 2 — CREATE: Add a New Parking Lot
-- ============================================================
-- TRIGGER: Admin clicks "Add New Lot" button on Page 1.
--          A blank Page 2 form opens with empty fields.
--          Admin fills in: lot name, latitude, longitude,
--          capacity, and EV charger count. Hits "Save".
--
-- FRONTEND FORM FIELDS:
--   {lot_name}         → text input  (required, e.g. 'New Engineering Garage')
--   {latitude}         → decimal input (e.g. 34.3650)
--   {longitude}        → decimal input (e.g. -89.5370)
--   {capacity}         → number input (required, e.g. 200)
--   {ev_charger_count} → number input (default 0)
--
-- NOTE: lot_id is AUTO_INCREMENT — do NOT pass it from frontend.
--       current_occupancy starts at 0 for a new lot.
-- ============================================================

-- VALIDATION: Check lot name doesn't already exist
SELECT COUNT(*) AS name_exists
FROM parking_lots
WHERE lot_name = '{lot_name}';
-- If name_exists > 0, show error: "A lot with this name already exists"

-- OPERATION:
INSERT INTO parking_lots (lot_name, latitude, longitude, capacity, current_occupancy, ev_charger_count)
VALUES ('{lot_name}', {latitude}, {longitude}, {capacity}, 0, {ev_charger_count});

-- AFTER INSERT: Redirect admin to Page 2 for the new lot.
-- Get the new lot_id with:
SELECT LAST_INSERT_ID() AS new_lot_id;


-- ============================================================
-- PAGE 2 — UPDATE: Edit Lot Details
-- ============================================================
-- TRIGGER: Admin is on Page 2 for a specific lot.
--          Clicks "Edit" next to a field (capacity, lat/long,
--          EV chargers, or lot name). The field becomes an
--          input box. Admin changes the value. Hits "Save".
--
-- FRONTEND: You know the {lot_id} from the URL/route param.
--           Only send the fields that changed.
--
-- PATTERN: Run the specific UPDATE for whichever field changed.
--          You can combine multiple field changes into one
--          UPDATE if the admin edits several fields at once.
-- ============================================================

-- Update lot name
-- TRIGGER: Admin clicks "Edit" next to lot name, types new name, hits Save
UPDATE parking_lots
SET lot_name = '{lot_name}'
WHERE lot_id = {lot_id};

-- Update capacity
-- TRIGGER: Admin clicks "Edit" next to capacity (e.g. construction added spots)
UPDATE parking_lots
SET capacity = {capacity}
WHERE lot_id = {lot_id};

-- Update EV charger count
-- TRIGGER: Admin clicks "Edit" next to EV chargers (e.g. new chargers installed)
UPDATE parking_lots
SET ev_charger_count = {ev_charger_count}
WHERE lot_id = {lot_id};

-- Update coordinates
-- TRIGGER: Admin clicks "Edit" next to map location
UPDATE parking_lots
SET latitude = {latitude}, longitude = {longitude}
WHERE lot_id = {lot_id};

-- Update multiple fields at once
-- TRIGGER: Admin edits several fields then hits one "Save All" button
UPDATE parking_lots
SET lot_name = '{lot_name}',
    capacity = {capacity},
    latitude = {latitude},
    longitude = {longitude},
    ev_charger_count = {ev_charger_count}
WHERE lot_id = {lot_id};


-- ============================================================
-- PAGE 2 — DELETE: Decommission a Parking Lot
-- ============================================================
-- TRIGGER: Admin clicks "Decommission Lot" button at the
--          bottom of Page 2. A confirmation dialog appears:
--          "Are you sure? This will remove the lot and all
--          its rules and occupancy history."
--
-- IMPORTANT: Foreign keys mean you MUST delete in this order:
--   1. parking_occupancy_log (references lot_id)
--   2. parking_rules (references lot_id)
--   3. parking_lots (the lot itself)
--
-- FRONTEND: Show a confirmation modal BEFORE running these.
--           Display the lot name and how many rules/logs will
--           be deleted so the admin knows the impact.
-- ============================================================

-- PRE-DELETE INFO: Show admin what will be affected
SELECT
    (SELECT COUNT(*) FROM parking_rules WHERE lot_id = {lot_id}) AS rules_to_delete,
    (SELECT COUNT(*) FROM parking_occupancy_log WHERE lot_id = {lot_id}) AS logs_to_delete;

-- STEP 1: Delete occupancy logs for this lot
DELETE FROM parking_occupancy_log WHERE lot_id = {lot_id};

-- STEP 2: Delete all rules for this lot
DELETE FROM parking_rules WHERE lot_id = {lot_id};

-- STEP 3: Delete the lot itself
DELETE FROM parking_lots WHERE lot_id = {lot_id};

-- AFTER DELETE: Redirect admin back to Page 1 dashboard.


-- ============================================================
-- PAGE 2 — CREATE: Add a New Parking Rule
-- ============================================================
-- TRIGGER: Admin is on Page 2 for a specific lot.
--          Clicks "Add Rule" button above the rules table.
--          A form appears with dropdowns and pickers:
--            - Permit type (dropdown from permits table)
--            - Days of week (checkboxes)
--            - Start time (time picker)
--            - End time (time picker)
--          Admin fills it in and hits "Save".
--
-- FRONTEND FORM FIELDS:
--   {lot_id}      → hidden field (from current page's lot)
--   {permit_id}   → dropdown (populated by: SELECT permit_id, permit_name FROM permits)
--   {day_of_week} → checkboxes joined as comma string (e.g. 'Mon,Tue,Wed,Thu,Fri')
--   {start_time}  → time picker (e.g. '07:00:00')
--   {end_time}    → time picker (e.g. '17:00:00')
--
-- NOTE: rule_id is AUTO_INCREMENT — do NOT pass it.
--       is_allowed defaults to TRUE.
-- ============================================================

-- POPULATE DROPDOWN: Get all permit types for the dropdown
SELECT permit_id, permit_name FROM permits ORDER BY permit_name;

-- VALIDATION: Check this exact rule doesn't already exist
SELECT COUNT(*) AS rule_exists
FROM parking_rules
WHERE lot_id = {lot_id}
  AND permit_id = '{permit_id}'
  AND day_of_week = '{day_of_week}'
  AND start_time = '{start_time}'
  AND end_time = '{end_time}';
-- If rule_exists > 0, show error: "This rule already exists for this lot"

-- OPERATION:
INSERT INTO parking_rules (lot_id, permit_id, day_of_week, start_time, end_time)
VALUES ({lot_id}, '{permit_id}', '{day_of_week}', '{start_time}', '{end_time}');


-- ============================================================
-- PAGE 2 — UPDATE: Edit an Existing Parking Rule
-- ============================================================
-- TRIGGER: Admin sees the rules table on Page 2, clicks
--          "Edit" on a specific rule row. The row becomes
--          editable — dropdowns for permit and days,
--          time pickers for start/end. Hits "Save".
--
-- FRONTEND: You know the {rule_id} from the row data.
-- ============================================================

-- OPERATION:
UPDATE parking_rules
SET permit_id = '{permit_id}',
    day_of_week = '{day_of_week}',
    start_time = '{start_time}',
    end_time = '{end_time}'
WHERE rule_id = {rule_id};


-- ============================================================
-- PAGE 2 — UPDATE: Disable/Enable a Rule (without deleting)
-- ============================================================
-- TRIGGER: Admin clicks a toggle switch on a rule row to
--          temporarily disable it (e.g. construction closure).
--          The rule stays in the database but is_allowed = FALSE.
--          The rule engine (Query 6/7) checks is_allowed,
--          so disabled rules won't return YES for users.
--
-- WHY THIS IS USEFUL: Instead of deleting a rule for a
--          temporary closure and recreating it later, admin
--          just flips a switch. E.g. lot closed for football
--          game setup — disable rules for 2 days, re-enable.
-- ============================================================

-- Disable a rule
UPDATE parking_rules SET is_allowed = FALSE WHERE rule_id = {rule_id};

-- Re-enable a rule
UPDATE parking_rules SET is_allowed = TRUE WHERE rule_id = {rule_id};


-- ============================================================
-- PAGE 2 — DELETE: Remove a Parking Rule
-- ============================================================
-- TRIGGER: Admin clicks "Delete" on a specific rule row.
--          Confirmation dialog: "Remove this rule? [permit_name]
--          permits will no longer have access during this window."
--
-- FRONTEND: Show the rule details in the confirmation dialog
--           so admin knows exactly what they're removing.
-- ============================================================

-- PRE-DELETE INFO: Get rule details for the confirmation dialog
SELECT
    p.permit_name,
    pr.day_of_week,
    pr.start_time,
    pr.end_time
FROM parking_rules pr
JOIN permits p ON pr.permit_id = p.permit_id
WHERE pr.rule_id = {rule_id};

-- OPERATION:
DELETE FROM parking_rules WHERE rule_id = {rule_id};


-- ============================================================
-- PAGE 2 — UPDATE + CREATE: Update Current Occupancy
-- ============================================================
-- TRIGGER: Admin is on Page 2, sees the occupancy section.
--          Enters a new occupancy number and optionally
--          updates EV chargers in use. Hits "Update".
--
-- THIS DOES TWO THINGS:
--   1. Updates current_occupancy in parking_lots (UPDATE)
--   2. Logs the reading in parking_occupancy_log (CREATE)
--      so we have historical data for trends/analytics
--
-- FRONTEND FORM FIELDS:
--   {lot_id}              → hidden (from current page)
--   {occupancy}           → number input
--   {ev_chargers_in_use}  → number input (default 0)
-- ============================================================

-- VALIDATION: Occupancy can't exceed capacity
SELECT capacity FROM parking_lots WHERE lot_id = {lot_id};
-- If {occupancy} > capacity, show error: "Occupancy cannot exceed lot capacity"

-- STEP 1: Update the live occupancy number
UPDATE parking_lots
SET current_occupancy = {occupancy}
WHERE lot_id = {lot_id};

-- STEP 2: Log this reading for historical tracking
INSERT INTO parking_occupancy_log (lot_id, recorded_at, occupancy, ev_chargers_in_use)
VALUES ({lot_id}, NOW(), {occupancy}, {ev_chargers_in_use});


-- ************************************************************
-- PAGE 3: PERMITS & USERS
-- Admin navigates here from the sidebar/nav menu.
-- Top section: permit types. Bottom section: user permits.
-- ************************************************************


-- ============================================================
-- PAGE 3 — CREATE: Add a New Permit Type
-- ============================================================
-- TRIGGER: Admin clicks "Add Permit" button in the permits
--          section. A form appears with fields for permit ID,
--          name, and description. Hits "Save".
--
-- FRONTEND FORM FIELDS:
--   {permit_id}   → text input, max 5 chars (e.g. 'EV')
--   {permit_name} → text input (e.g. 'EV Priority')
--   {description} → text input (e.g. 'Priority at EV charger spots')
--
-- NOTE: permit_id is NOT auto-increment — admin chooses it.
--       This is because permit_ids are used as short codes
--       throughout the system (RC, S, FC, etc.)
-- ============================================================

-- VALIDATION: Check permit_id doesn't already exist
SELECT COUNT(*) AS id_exists
FROM permits
WHERE permit_id = '{permit_id}';
-- If id_exists > 0, show error: "This permit ID already exists"

-- OPERATION:
INSERT INTO permits (permit_id, permit_name, description)
VALUES ('{permit_id}', '{permit_name}', '{description}');


-- ============================================================
-- PAGE 3 — UPDATE: Edit a Permit Type
-- ============================================================
-- TRIGGER: Admin clicks "Edit" on a permit row in the permits
--          table. The name and description become editable.
--          Hits "Save".
--
-- NOTE: permit_id should NOT be editable since it's a primary
--       key referenced by parking_rules and user_permits.
--       Changing it would break foreign key relationships.
--       If admin needs a different ID, they should create a
--       new permit and migrate users over.
-- ============================================================

-- OPERATION:
UPDATE permits
SET permit_name = '{permit_name}',
    description = '{description}'
WHERE permit_id = '{permit_id}';


-- ============================================================
-- PAGE 3 — DELETE: Remove a Permit Type
-- ============================================================
-- TRIGGER: Admin clicks "Delete" on a permit row.
--          Confirmation dialog shows impact.
--
-- IMPORTANT: Can only delete if no rules or user_permits
--            reference this permit. Otherwise foreign keys fail.
--
-- FRONTEND: Check the validation query first. If references
--           exist, show: "Cannot delete — X rules and Y users
--           still use this permit. Remove those first."
-- ============================================================

-- VALIDATION: Check for dependencies before allowing delete
SELECT
    (SELECT COUNT(*) FROM parking_rules WHERE permit_id = '{permit_id}') AS rules_using,
    (SELECT COUNT(*) FROM user_permits WHERE permit_id = '{permit_id}') AS users_using;
-- If rules_using > 0 OR users_using > 0, BLOCK the delete and show the counts

-- OPERATION (only if validation passes):
DELETE FROM permits WHERE permit_id = '{permit_id}';


-- ============================================================
-- PAGE 3 — CREATE: Assign a Permit to a User
-- ============================================================
-- TRIGGER: Admin clicks "Assign Permit" button in the users
--          section. A form appears with:
--            - User dropdown (or search box)
--            - Permit type dropdown
--            - Issued date picker
--            - Expiration date picker
--          Hits "Save".
--
-- FRONTEND FORM FIELDS:
--   {user_id}         → dropdown/search (populated by: SELECT user_id, first_name, last_name FROM users)
--   {permit_id}       → dropdown (populated by: SELECT permit_id, permit_name FROM permits)
--   {issued_date}     → date picker (e.g. '2026-03-25')
--   {expiration_date} → date picker (e.g. '2026-05-15')
-- ============================================================

-- POPULATE DROPDOWNS:
SELECT user_id, first_name, last_name, role FROM users ORDER BY last_name;
SELECT permit_id, permit_name FROM permits ORDER BY permit_name;

-- VALIDATION: Check user doesn't already have this permit
SELECT COUNT(*) AS already_assigned
FROM user_permits
WHERE user_id = '{user_id}' AND permit_id = '{permit_id}';
-- If already_assigned > 0, show error: "This user already has this permit type"

-- VALIDATION: Check expiration is after issued date
-- (Handle this on frontend — {expiration_date} must be >= {issued_date})

-- OPERATION:
INSERT INTO user_permits (user_id, permit_id, issued_date, expiration_date)
VALUES ('{user_id}', '{permit_id}', '{issued_date}', '{expiration_date}');


-- ============================================================
-- PAGE 3 — UPDATE: Individual Permit Renewal
-- ============================================================
-- TRIGGER: Admin searches for a specific user (e.g. "fac003"),
--          sees their permit(s) listed, clicks "Renew" on a
--          specific permit row. A form shows the current dates
--          and lets the admin set a new expiration date.
--          Hits "Save".
--
-- USE CASE: A single student needs their permit extended
--           (e.g. they enrolled in summer classes), or admin
--           corrects a wrong date for one user.
--
-- FRONTEND: user_id + permit_id together form the primary key
--           of user_permits, so you need BOTH to target the row.
--           Show the current issued_date and expiration_date
--           in the form as reference.
--
-- FRONTEND FORM FIELDS:
--   {user_id}         → hidden (from the user row)
--   {permit_id}       → hidden (from the permit row)
--   {issued_date}     → date picker (pre-filled with current value)
--   {expiration_date} → date picker (admin sets new date)
-- ============================================================

-- PRE-FILL: Get current dates to show in the form
SELECT
    u.first_name,
    u.last_name,
    p.permit_name,
    up.issued_date,
    up.expiration_date
FROM user_permits up
JOIN users u ON up.user_id = u.user_id
JOIN permits p ON up.permit_id = p.permit_id
WHERE up.user_id = '{user_id}' AND up.permit_id = '{permit_id}';

-- OPERATION: Update this specific user's specific permit
UPDATE user_permits
SET issued_date = '{issued_date}',
    expiration_date = '{expiration_date}'
WHERE user_id = '{user_id}' AND permit_id = '{permit_id}';


-- ============================================================
-- PAGE 3 — UPDATE: Bulk Permit Renewal
-- ============================================================
-- TRIGGER: Admin clicks "Bulk Extend" button at the top of
--          the users section. A form appears with:
--            - Permit type dropdown (e.g. "Student Commuter")
--            - New expiration date picker
--          Hits "Apply to All". Every user with that permit
--          type gets the new expiration date.
--
-- USE CASE: End of semester, all Student Commuter (S) permits
--           need extending to the next semester. Admin does it
--           in one click instead of updating each user.
--
-- FRONTEND: Show a confirmation with the count of affected
--           users before running the update.
--
-- FRONTEND FORM FIELDS:
--   {permit_id}           → dropdown (populated by: SELECT permit_id, permit_name FROM permits)
--   {new_expiration_date} → date picker (e.g. '2027-05-15')
-- ============================================================

-- PRE-UPDATE: Show admin how many users will be affected
SELECT COUNT(*) AS users_affected
FROM user_permits
WHERE permit_id = '{permit_id}';

-- OPERATION: Extend all permits of this type
UPDATE user_permits
SET expiration_date = '{new_expiration_date}'
WHERE permit_id = '{permit_id}';


-- ============================================================
-- PAGE 3 — DELETE: Revoke a User's Permit
-- ============================================================
-- TRIGGER: Admin searches for a user, clicks "Revoke" on
--          one of their permits. Confirmation dialog:
--          "Revoke [permit_name] from [first_name last_name]?"
--
-- NOTE: This only removes the permit assignment, NOT the user
--       account. The user stays in the users table but without
--       this permit, the rule engine returns NO for lots that
--       required it.
-- ============================================================

-- PRE-DELETE INFO: Show admin what they're revoking
SELECT
    u.first_name,
    u.last_name,
    p.permit_name,
    up.expiration_date
FROM user_permits up
JOIN users u ON up.user_id = u.user_id
JOIN permits p ON up.permit_id = p.permit_id
WHERE up.user_id = '{user_id}' AND up.permit_id = '{permit_id}';

-- OPERATION:
DELETE FROM user_permits
WHERE user_id = '{user_id}' AND permit_id = '{permit_id}';


-- ============================================================
-- DROPDOWN / SEARCH HELPERS
-- These queries populate the form dropdowns and search boxes
-- across the admin panel. The frontend should call these
-- when loading a form.
-- ============================================================

-- All lots (for any lot-related dropdown)
SELECT lot_id, lot_name FROM parking_lots ORDER BY lot_name;

-- All permits (for any permit-related dropdown)
SELECT permit_id, permit_name FROM permits ORDER BY permit_name;

-- All users (for user search/dropdown on Page 3)
SELECT user_id, first_name, last_name, email, role
FROM users
ORDER BY last_name, first_name;

-- All users with their permits (for the Page 3 user table)
SELECT
    u.user_id,
    u.first_name,
    u.last_name,
    u.email,
    u.role,
    p.permit_id,
    p.permit_name,
    up.issued_date,
    up.expiration_date,
    CASE
        WHEN up.expiration_date < CURDATE() THEN 'EXPIRED'
        WHEN up.expiration_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY) THEN 'EXPIRING SOON'
        ELSE 'ACTIVE'
    END AS permit_status
FROM users u
LEFT JOIN user_permits up ON u.user_id = up.user_id
LEFT JOIN permits p ON up.permit_id = p.permit_id
ORDER BY u.last_name, u.first_name;
