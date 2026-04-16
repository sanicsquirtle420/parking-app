-- ============================================
-- admin_queries.sql
-- Standalone admin queries for the Ole Miss
-- Campus Parking App. These map directly to
-- the admin user stories in Milestone 2.
-- ============================================


-- ============================================
-- QUERY 1: Lots over 90% capacity
-- Admin Story: Karen wants to see which lots
-- are over 90% capacity to identify lots
-- that need attention.
-- Expected: Coliseum (92.5%), Lyceum (92.5%),
-- Student Union (91.0%), Jackson Garage (91.4%)
-- ============================================
SELECT
    lot_name,
    capacity,
    current_occupancy,
    capacity - current_occupancy AS available_spaces,
    ROUND((current_occupancy / capacity) * 100, 1) AS occupancy_pct
FROM parking_lots
WHERE (current_occupancy / capacity) * 100 >= 90
ORDER BY occupancy_pct DESC;


-- ============================================
-- QUERY 2: Lots with zero EV chargers
-- Admin Story: Karen wants to see which lots
-- have zero EV chargers to prioritize where
-- to install new charging infrastructure.
-- Expected: Stockard/Martin, Residential West,
-- Lyceum Circle, Kennon Observatory,
-- Law School, Visitor Center
-- ============================================
SELECT
    lot_name,
    capacity,
    current_occupancy,
    ev_charger_count
FROM parking_lots
WHERE ev_charger_count = 0
ORDER BY lot_name;


-- ============================================
-- QUERY 3: Overloaded vs Underutilized comparison
-- Admin Story: Karen wants to compare overloaded
-- lots against underutilized lots that accept
-- the same permit types to recommend drivers
-- redistribute to less crowded options.
-- Example: Coliseum (92.5%) vs South Lot 6 (35%)
-- both accept S permits on weekdays.
-- ============================================
SELECT
    pl.lot_name,
    pl.capacity,
    pl.current_occupancy,
    ROUND((pl.current_occupancy / pl.capacity) * 100, 1) AS occupancy_pct,
    p.permit_name,
    pr.day_of_week,
    pr.start_time,
    pr.end_time,
    CASE
        WHEN (pl.current_occupancy / pl.capacity) * 100 >= 90 THEN 'OVERLOADED'
        WHEN (pl.current_occupancy / pl.capacity) * 100 <= 50 THEN 'UNDERUTILIZED'
        ELSE 'NORMAL'
    END AS load_status
FROM parking_rules pr
JOIN parking_lots pl ON pr.lot_id = pl.lot_id
JOIN permits p ON pr.permit_id = p.permit_id
WHERE p.permit_id = 'S'
  AND FIND_IN_SET('Mon', pr.day_of_week) > 0
ORDER BY occupancy_pct DESC;


-- ============================================
-- QUERY 4: Peak occupancy from the log
-- Admin Story: Karen wants to review the
-- parking_occupancy_log to find peak usage
-- hours for the Coliseum Commuter Lot.
-- Expected: Peak at 10:00 AM with 385/400 (96.3%)
-- ============================================
SELECT
    pl.lot_name,
    pol.recorded_at,
    pol.occupancy,
    pl.capacity,
    ROUND((pol.occupancy / pl.capacity) * 100, 1) AS occupancy_pct,
    pol.ev_chargers_in_use,
    pl.ev_charger_count
FROM parking_occupancy_log pol
JOIN parking_lots pl ON pol.lot_id = pl.lot_id
WHERE pl.lot_name = 'Coliseum Commuter Lot'
ORDER BY pol.recorded_at;


-- ============================================
-- QUERY 5: User permit expiration check
-- Admin Story: Faculty member James Williams
-- (fac003) wants to check his permit expiration
-- dates. His FC and ADA permits expire 2026-07-31.
-- Also useful for admin to find expired permits.
-- ============================================

-- 5a: Check a specific user's permits
SELECT
    u.user_id,
    u.first_name,
    u.last_name,
    u.role,
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
WHERE u.user_id = 'fac003';

-- 5b: Find ALL expired or expiring-soon permits
SELECT
    u.user_id,
    u.first_name,
    u.last_name,
    u.role,
    p.permit_name,
    up.expiration_date,
    DATEDIFF(up.expiration_date, CURDATE()) AS days_remaining,
    CASE
        WHEN up.expiration_date < CURDATE() THEN 'EXPIRED'
        WHEN up.expiration_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY) THEN 'EXPIRING SOON'
        ELSE 'ACTIVE'
    END AS permit_status
FROM users u
JOIN user_permits up ON u.user_id = up.user_id
JOIN permits p ON up.permit_id = p.permit_id
HAVING permit_status IN ('EXPIRED', 'EXPIRING SOON')
ORDER BY up.expiration_date ASC;


-- ============================================
-- QUERY 6: "Can this user park here right now?"
-- The core rule engine query. Given a user_id,
-- lot_id, and the current day/time, returns
-- YES or NO.
-- Example: John Doe (stu001) checking
-- Stockard/Martin Lot (lot 1) on a weekday.
-- His RC permit is allowed Mon-Fri 00:00-23:59.
-- ============================================
SELECT
    u.first_name,
    u.last_name,
    p.permit_name,
    pl.lot_name,
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
JOIN parking_lots pl ON pl.lot_id = 1                    -- << lot to check
LEFT JOIN parking_rules pr
    ON pr.permit_id = up.permit_id
   AND pr.lot_id = pl.lot_id
   AND FIND_IN_SET(
         ELT(DAYOFWEEK(CURDATE()), 'Sun','Mon','Tue','Wed','Thu','Fri','Sat'),
         pr.day_of_week
       ) > 0
   AND CURTIME() BETWEEN pr.start_time AND pr.end_time
WHERE u.user_id = 'stu001'                               -- << user to check
ORDER BY can_park DESC
LIMIT 1;


-- ============================================
-- QUERY 7: Full availability check for a user
-- Given a user_id, shows ALL lots where they
-- can park RIGHT NOW based on their permit(s),
-- the current day of week, and current time.
-- Example: Tyler Brown (stu003) with RW permit
-- checking on a weekday — expects Residential
-- West Lot (Mon-Fri all day). Change user_id
-- to test other users, e.g. 'stu002' for
-- Maria Garcia (S permit) after 5pm to see
-- more lots open up.
-- ============================================
SELECT
    pl.lot_name,
    p.permit_name,
    pr.day_of_week,
    pr.start_time,
    pr.end_time,
    pl.current_occupancy,
    pl.capacity,
    pl.capacity - pl.current_occupancy AS available_spaces,
    ROUND((pl.current_occupancy / pl.capacity) * 100, 1) AS occupancy_pct
FROM users u
JOIN user_permits up ON u.user_id = up.user_id
JOIN permits p ON up.permit_id = p.permit_id
JOIN parking_rules pr ON pr.permit_id = up.permit_id
JOIN parking_lots pl ON pr.lot_id = pl.lot_id
WHERE u.user_id = 'stu002'                               -- << user to check
  AND up.expiration_date >= CURDATE()
  AND pr.is_allowed = TRUE
  AND FIND_IN_SET(
        ELT(DAYOFWEEK(CURDATE()), 'Sun','Mon','Tue','Wed','Thu','Fri','Sat'),
        pr.day_of_week
      ) > 0
  AND CURTIME() BETWEEN pr.start_time AND pr.end_time
ORDER BY occupancy_pct ASC;


-- ============================================
-- QUERY 8: Admin add a new parking rule
-- Admin Story: Karen wants to add a new rule
-- for Vaught-Hemingway Lot (lot 11) opening
-- it to all permit types on Saturdays for
-- football games.
-- NOTE: This is an INSERT — run only when needed.
-- ============================================
-- INSERT INTO parking_rules (lot_id, permit_id, day_of_week, start_time, end_time)
-- VALUES
-- (11, 'RC',  'Sat', '00:00:00', '23:59:59'),
-- (11, 'RW',  'Sat', '00:00:00', '23:59:59'),
-- (11, 'FC',  'Sat', '00:00:00', '23:59:59'),
-- (11, 'FW',  'Sat', '00:00:00', '23:59:59'),
-- (11, 'V',   'Sat', '00:00:00', '23:59:59'),
-- (11, 'ADA', 'Sat', '00:00:00', '23:59:59');
