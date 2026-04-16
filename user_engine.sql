-- ============================================================
-- user_engine.sql
-- Ole Miss Campus Parking App — User-Facing Queries
-- ============================================================
--
-- PURPOSE:
-- These queries power the student, faculty, and visitor
-- experience. When a user opens the app, logs in, and
-- checks parking availability, these are the queries
-- running behind the scenes.
--
-- USER TYPES & HOW THEY INTERACT:
--   Students/Faculty: Log in with their credentials.
--     The app knows their user_id and looks up their
--     permit(s) from user_permits automatically.
--   Visitors: Can browse without logging in. The app
--     prompts them to "Select Permit Type: Visitor"
--     to activate the rule engine.
--
-- APP FLOW (what the user experiences):
--   1. User logs in (or visitor selects permit type)
--   2. App shows map with all 12 lots
--   3. User taps a lot → app runs the YES/NO check
--   4. If YES → shows occupancy warning if lot is full
--   5. If NO → (smart recommendations coming later)
--
-- FRONTEND: Replace {placeholders} with actual values.
-- ============================================================


-- ============================================================
-- QUERY 1: Get User Profile + Permits After Login
-- ============================================================
-- TRIGGER: User successfully logs in. The app needs to know
--          who they are and what permits they hold so it can
--          run the rule engine on every lot they check.
--
-- FRONTEND: Call this immediately after authentication.
--           Store the results in session/state — you'll need
--           the permit_id(s) for all subsequent queries.
--
-- NOTE: A user can have MULTIPLE permits (e.g. fac003 has
--       both FC and ADA). Return ALL of them. The rule engine
--       checks each permit separately.
-- ============================================================

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
JOIN user_permits up ON u.user_id = up.user_id
JOIN permits p ON up.permit_id = p.permit_id
WHERE u.user_id = '{user_id}';

-- FRONTEND LOGIC:
-- If permit_status = 'EXPIRED' for ALL permits:
--   Show warning: "Your permit has expired. Contact Parking Services."
--   The rule engine will return NO for everything anyway.
-- If permit_status = 'EXPIRING SOON':
--   Show a banner: "Your [permit_name] expires on [expiration_date]"


-- ============================================================
-- QUERY 2: Load All Lots for the Map
-- ============================================================
-- TRIGGER: App loads the home/map page. Needs all 12 lots
--          with their coordinates (for map markers), capacity,
--          and current occupancy (for color-coded markers).
--
-- FRONTEND: Use latitude + longitude to place markers on the
--           map. Color code by occupancy:
--             GREEN  = LOW (under 50%)
--             YELLOW = MODERATE (50-69%)
--             ORANGE = HIGH (70-89%)
--             RED    = CRITICAL (90%+)
-- ============================================================

SELECT
    lot_id,
    lot_name,
    latitude,
    longitude,
    capacity,
    current_occupancy,
    ev_charger_count,
    capacity - current_occupancy AS available_spaces,
    ROUND((current_occupancy / capacity) * 100, 1) AS occupancy_pct,
    CASE
        WHEN (current_occupancy / capacity) * 100 >= 90 THEN 'CRITICAL'
        WHEN (current_occupancy / capacity) * 100 >= 70 THEN 'HIGH'
        WHEN (current_occupancy / capacity) * 100 >= 50 THEN 'MODERATE'
        ELSE 'LOW'
    END AS status_level
FROM parking_lots
ORDER BY lot_name;


-- ============================================================
-- QUERY 3: The YES/NO Decision — Can This User Park Here?
-- ============================================================
-- TRIGGER: User taps a specific lot marker on the map.
--          The app checks: does this user's permit allow
--          parking at this lot RIGHT NOW (current day + time)?
--
-- THIS IS THE CORE RULE ENGINE.
--
-- HOW IT WORKS:
--   1. Looks up the user's permit(s) from user_permits
--   2. Checks parking_rules for a matching rule at this lot
--      for this permit on today's day of week
--   3. Checks if current time falls within the rule's window
--   4. Checks if the permit hasn't expired
--   5. Returns YES or NO
--
-- FRONTEND FORM FIELDS:
--   {user_id} → from session (logged-in user)
--   {lot_id}  → from the lot marker the user tapped
--
-- DISPLAY:
--   YES → Large green checkmark + "You can park here"
--   NO  → Large red X + "Your permit is not valid here right now"
-- ============================================================

SELECT
    u.first_name,
    u.last_name,
    p.permit_name,
    pl.lot_name,
    pl.capacity,
    pl.current_occupancy,
    pl.capacity - pl.current_occupancy AS available_spaces,
    ROUND((pl.current_occupancy / pl.capacity) * 100, 1) AS occupancy_pct,
    pl.ev_charger_count,
    pr.day_of_week,
    pr.start_time,
    pr.end_time,
    CASE
        WHEN pr.rule_id IS NOT NULL
         AND pr.is_allowed = TRUE
         AND up.expiration_date >= CURDATE()
        THEN 'YES'
        ELSE 'NO'
    END AS can_park
FROM users u
JOIN user_permits up ON u.user_id = up.user_id
JOIN permits p ON up.permit_id = p.permit_id
JOIN parking_lots pl ON pl.lot_id = {lot_id}
LEFT JOIN parking_rules pr
    ON pr.permit_id = up.permit_id
   AND pr.lot_id = pl.lot_id
   AND FIND_IN_SET(
         ELT(DAYOFWEEK(CURDATE()), 'Sun','Mon','Tue','Wed','Thu','Fri','Sat'),
         pr.day_of_week
       ) > 0
   AND CURTIME() BETWEEN pr.start_time AND pr.end_time
WHERE u.user_id = '{user_id}'
ORDER BY can_park DESC
LIMIT 1;

-- FRONTEND LOGIC AFTER RESULT:
-- If can_park = 'YES':
--   Show green YES
--   Then check occupancy_pct:
--     >= 90%: Warning — "You can park here, but the lot is nearly full
--             ({available_spaces} spots left)"
--     >= 70%: Notice — "Lot is filling up ({available_spaces} spots left)"
--     < 70%:  All good — "{available_spaces} spots available"
--   If ev_charger_count > 0:
--     Show EV info: "{ev_charger_count} EV chargers at this lot"
--
-- If can_park = 'NO':
--   Show red NO
--   Show the rule window if one exists for another time:
--     "Your permit is valid here [day_of_week] from [start_time] to [end_time]"
--   (Smart lot recommendation coming in future update)


-- ============================================================
-- QUERY 4: All Available Lots for This User Right Now
-- ============================================================
-- TRIGGER: User clicks "Show All My Lots" or a filter button
--          to see everywhere they can park at this moment.
--          This is the filtered map view — only shows lots
--          where the rule engine returns YES.
--
-- FRONTEND: Highlight these lots on the map in green.
--           Gray out all other lots.
--           Sort by occupancy (least full first) so user
--           picks the lot with most available spaces.
--
-- FRONTEND FORM FIELDS:
--   {user_id} → from session (logged-in user)
-- ============================================================

SELECT
    pl.lot_id,
    pl.lot_name,
    pl.latitude,
    pl.longitude,
    p.permit_name,
    pr.day_of_week,
    pr.start_time,
    pr.end_time,
    pl.current_occupancy,
    pl.capacity,
    pl.capacity - pl.current_occupancy AS available_spaces,
    ROUND((pl.current_occupancy / pl.capacity) * 100, 1) AS occupancy_pct,
    pl.ev_charger_count,
    CASE
        WHEN (pl.current_occupancy / pl.capacity) * 100 >= 90 THEN 'CRITICAL'
        WHEN (pl.current_occupancy / pl.capacity) * 100 >= 70 THEN 'HIGH'
        WHEN (pl.current_occupancy / pl.capacity) * 100 >= 50 THEN 'MODERATE'
        ELSE 'LOW'
    END AS status_level
FROM users u
JOIN user_permits up ON u.user_id = up.user_id
JOIN permits p ON up.permit_id = p.permit_id
JOIN parking_rules pr ON pr.permit_id = up.permit_id
JOIN parking_lots pl ON pr.lot_id = pl.lot_id
WHERE u.user_id = '{user_id}'
  AND up.expiration_date >= CURDATE()
  AND pr.is_allowed = TRUE
  AND FIND_IN_SET(
        ELT(DAYOFWEEK(CURDATE()), 'Sun','Mon','Tue','Wed','Thu','Fri','Sat'),
        pr.day_of_week
      ) > 0
  AND CURTIME() BETWEEN pr.start_time AND pr.end_time
ORDER BY occupancy_pct ASC;


-- ============================================================
-- QUERY 5: Visitor Mode — Check by Permit Type (No Login)
-- ============================================================
-- TRIGGER: A visitor (or anyone browsing without login)
--          selects "Visitor" from a permit type dropdown.
--          The app shows which lots accept Visitor permits
--          right now.
--
-- HOW THIS DIFFERS FROM QUERY 4:
--   Query 4 looks up the user's permits from user_permits.
--   This query takes a raw permit_id and checks directly —
--   no user account needed.
--
-- FRONTEND: Show a dropdown on the map page: "Browse as:"
--           with options for each permit type. When visitor
--           selects one, run this query.
--
-- FRONTEND FORM FIELDS:
--   {permit_id} → from dropdown (e.g. 'V' for Visitor)
-- ============================================================

SELECT
    pl.lot_id,
    pl.lot_name,
    pl.latitude,
    pl.longitude,
    p.permit_name,
    pr.day_of_week,
    pr.start_time,
    pr.end_time,
    pl.current_occupancy,
    pl.capacity,
    pl.capacity - pl.current_occupancy AS available_spaces,
    ROUND((pl.current_occupancy / pl.capacity) * 100, 1) AS occupancy_pct,
    pl.ev_charger_count,
    CASE
        WHEN (pl.current_occupancy / pl.capacity) * 100 >= 90 THEN 'CRITICAL'
        WHEN (pl.current_occupancy / pl.capacity) * 100 >= 70 THEN 'HIGH'
        WHEN (pl.current_occupancy / pl.capacity) * 100 >= 50 THEN 'MODERATE'
        ELSE 'LOW'
    END AS status_level
FROM parking_rules pr
JOIN parking_lots pl ON pr.lot_id = pl.lot_id
JOIN permits p ON pr.permit_id = p.permit_id
WHERE pr.permit_id = '{permit_id}'
  AND pr.is_allowed = TRUE
  AND FIND_IN_SET(
        ELT(DAYOFWEEK(CURDATE()), 'Sun','Mon','Tue','Wed','Thu','Fri','Sat'),
        pr.day_of_week
      ) > 0
  AND CURTIME() BETWEEN pr.start_time AND pr.end_time
ORDER BY occupancy_pct ASC;


-- ============================================================
-- QUERY 6: Get All Rules for a Specific Lot
-- ============================================================
-- TRIGGER: User taps a lot and wants to see the full
--          schedule — not just whether they can park NOW,
--          but all time windows and permit types for the lot.
--
-- FRONTEND: Display this as a table or schedule grid on the
--           lot detail panel. Helps users plan ahead.
--           E.g. "I can't park here now, but I can after 5pm"
-- ============================================================

SELECT
    p.permit_name,
    pr.day_of_week,
    pr.start_time,
    pr.end_time,
    pr.is_allowed
FROM parking_rules pr
JOIN permits p ON pr.permit_id = p.permit_id
WHERE pr.lot_id = {lot_id}
ORDER BY p.permit_name, pr.day_of_week;


-- ============================================================
-- QUERY 7: Login Validation
-- ============================================================
-- TRIGGER: User enters email and password on the login page.
--          Frontend hashes the password and sends it here.
--
-- NOTE: Password hashing must happen on the frontend/backend
--       API layer BEFORE this query runs. This query just
--       compares the stored hash with the submitted hash.
--
-- FRONTEND: The auth team handles the hashing logic.
--           This query is what they call after hashing.
--
-- RETURNS: user_id and role if credentials match.
--          Empty result = invalid login.
-- ============================================================

SELECT user_id, first_name, last_name, role
FROM users
WHERE email = '{email}'
  AND password_hash = '{password_hash}';

-- FRONTEND LOGIC AFTER LOGIN:
-- If result is empty → "Invalid email or password"
-- If role = 'admin' → redirect to Admin Dashboard (Page 1)
-- If role = 'student' or 'faculty' → redirect to Map View
-- If role = 'visitor' → redirect to Map View
-- Then immediately run Query 1 to load their permits


-- ============================================================
-- QUERY 8: Check If User Has Any Valid Permits
-- ============================================================
-- TRIGGER: After login, before showing the map, the app
--          checks if the user has at least one non-expired
--          permit. If not, the rule engine can't help them.
--
-- FRONTEND: If count = 0, show message:
--           "You don't have an active parking permit.
--            Contact Parking Services to get one."
-- ============================================================

SELECT COUNT(*) AS active_permits
FROM user_permits
WHERE user_id = '{user_id}'
  AND expiration_date >= CURDATE();
