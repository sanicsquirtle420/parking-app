-- ============================================
-- admin_views.sql
-- Power BI-ready views for the Ole Miss Campus Parking App
-- These views sit on top of the existing 6 tables
-- and provide clean datasets for admin dashboards.
-- ============================================


-- ============================================
-- VIEW 1: v_lot_utilization
-- Purpose: Shows each lot's current occupancy
-- percentage and flags critical lots (>90%).
-- Supports Admin Story: "Which lots are over 90%?"
-- ============================================
CREATE OR REPLACE VIEW v_lot_utilization AS
SELECT
    lot_id,
    lot_name,
    capacity,
    current_occupancy,
    ev_charger_count,
    ROUND((current_occupancy / capacity) * 100, 1) AS occupancy_pct,
    CASE
        WHEN (current_occupancy / capacity) * 100 >= 90 THEN 'CRITICAL'
        WHEN (current_occupancy / capacity) * 100 >= 70 THEN 'HIGH'
        WHEN (current_occupancy / capacity) * 100 >= 50 THEN 'MODERATE'
        ELSE 'LOW'
    END AS status_level,
    capacity - current_occupancy AS available_spaces
FROM parking_lots
ORDER BY occupancy_pct DESC;


-- ============================================
-- VIEW 2: v_peak_occupancy
-- Purpose: For each lot in the log, shows the
-- time it hit peak occupancy and peak EV usage.
-- Supports Admin Story: "Find peak usage hours
-- for Coliseum Commuter Lot"
-- ============================================
CREATE OR REPLACE VIEW v_peak_occupancy AS
SELECT
    pl.lot_id,
    pl.lot_name,
    pl.capacity,
    pol.recorded_at AS peak_time,
    pol.occupancy AS peak_occupancy,
    ROUND((pol.occupancy / pl.capacity) * 100, 1) AS peak_occupancy_pct,
    pol.ev_chargers_in_use AS peak_ev_usage,
    pl.ev_charger_count AS total_ev_chargers
FROM parking_occupancy_log pol
JOIN parking_lots pl ON pol.lot_id = pl.lot_id
WHERE pol.occupancy = (
    SELECT MAX(pol2.occupancy)
    FROM parking_occupancy_log pol2
    WHERE pol2.lot_id = pol.lot_id
)
ORDER BY peak_occupancy_pct DESC;


-- ============================================
-- VIEW 3: v_ev_charger_summary
-- Purpose: Shows EV charger infrastructure per
-- lot and max recorded usage from the log.
-- Supports Admin Story: "Which lots have zero
-- EV chargers?"
-- ============================================
CREATE OR REPLACE VIEW v_ev_charger_summary AS
SELECT
    pl.lot_id,
    pl.lot_name,
    pl.capacity,
    pl.ev_charger_count,
    COALESCE(ev_log.max_ev_in_use, 0) AS max_ev_chargers_used,
    CASE
        WHEN pl.ev_charger_count = 0 THEN 'NO CHARGERS'
        WHEN COALESCE(ev_log.max_ev_in_use, 0) = pl.ev_charger_count THEN 'FULLY UTILIZED'
        ELSE 'AVAILABLE'
    END AS ev_status
FROM parking_lots pl
LEFT JOIN (
    SELECT lot_id, MAX(ev_chargers_in_use) AS max_ev_in_use
    FROM parking_occupancy_log
    GROUP BY lot_id
) ev_log ON pl.lot_id = ev_log.lot_id
ORDER BY pl.ev_charger_count ASC, pl.lot_name;


-- ============================================
-- VIEW 4: v_permit_rule_matrix
-- Purpose: Flattened view of which permit is
-- allowed at which lot and when. Joins
-- parking_rules with lot names and permit names.
-- Useful for both the app rule engine and
-- Power BI filtering/slicing.
-- ============================================
CREATE OR REPLACE VIEW v_permit_rule_matrix AS
SELECT
    pr.rule_id,
    pl.lot_id,
    pl.lot_name,
    p.permit_id,
    p.permit_name,
    pr.day_of_week,
    pr.start_time,
    pr.end_time,
    pr.is_allowed,
    pl.capacity,
    pl.current_occupancy
FROM parking_rules pr
JOIN parking_lots pl ON pr.lot_id = pl.lot_id
JOIN permits p ON pr.permit_id = p.permit_id
ORDER BY pl.lot_name, p.permit_name, pr.day_of_week;


-- ============================================
-- VIEW 5: v_occupancy_trends
-- Purpose: Hourly occupancy data joined with
-- lot names and capacity for Power BI line
-- charts. Includes occupancy percentage and
-- EV charger utilization rate.
-- ============================================
CREATE OR REPLACE VIEW v_occupancy_trends AS
SELECT
    pol.log_id,
    pl.lot_id,
    pl.lot_name,
    pl.capacity,
    pl.ev_charger_count,
    pol.recorded_at,
    DATE(pol.recorded_at) AS record_date,
    HOUR(pol.recorded_at) AS record_hour,
    pol.occupancy,
    ROUND((pol.occupancy / pl.capacity) * 100, 1) AS occupancy_pct,
    pol.ev_chargers_in_use,
    CASE
        WHEN pl.ev_charger_count > 0
        THEN ROUND((pol.ev_chargers_in_use / pl.ev_charger_count) * 100, 1)
        ELSE 0
    END AS ev_utilization_pct
FROM parking_occupancy_log pol
JOIN parking_lots pl ON pol.lot_id = pl.lot_id
ORDER BY pl.lot_name, pol.recorded_at;
