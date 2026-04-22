-- Helper views for admin analytics and future frontend/reporting work.

CREATE OR REPLACE VIEW vw_lot_utilization AS
SELECT
    lot_id,
    polygon_id,
    lot_name,
    zone,
    capacity,
    current_occupancy,
    (capacity - current_occupancy) AS spots_left,
    CASE
        WHEN capacity > 0 THEN ROUND((current_occupancy / capacity) * 100, 1)
        ELSE 0
    END AS utilization_pct,
    ev_charger_count,
    is_active
FROM parking_lots;

CREATE OR REPLACE VIEW vw_active_permit_assignments AS
SELECT
    u.user_id,
    u.first_name,
    u.last_name,
    u.email,
    u.role,
    up.assignment_id,
    up.issued_date,
    up.expiration_date,
    up.status,
    p.permit_id,
    p.permit_name,
    p.duration_days,
    p.display_color_hex
FROM users u
LEFT JOIN user_permits up ON u.user_id = up.user_id
LEFT JOIN permits p ON up.permit_id = p.permit_id;

CREATE OR REPLACE VIEW vw_parking_rule_matrix AS
SELECT
    pr.rule_id,
    pl.lot_id,
    pl.polygon_id,
    pl.lot_name,
    pl.zone,
    p.permit_id,
    p.permit_name,
    pr.day_of_week,
    pr.start_time,
    pr.end_time,
    pr.is_allowed,
    pr.rule_source
FROM parking_rules pr
JOIN parking_lots pl ON pr.lot_id = pl.lot_id
JOIN permits p ON pr.permit_id = p.permit_id;

CREATE OR REPLACE VIEW vw_permit_usage_summary AS
SELECT
    p.permit_id,
    p.permit_name,
    p.duration_days,
    p.display_color_hex,
    COUNT(up.assignment_id) AS assigned_user_count
FROM permits p
LEFT JOIN user_permits up ON p.permit_id = up.permit_id
GROUP BY
    p.permit_id,
    p.permit_name,
    p.duration_days,
    p.display_color_hex;
