"""
admin_dashboard.py
==================
Page 1 — Admin Dashboard: READ-only queries powering the landing page.

This file maps to admin_views.sql and admin_queries.sql.
No create, update, or delete operations here — just data for display.

SITEMAP CONTEXT:
  When an admin logs in (role = 'admin'), they land on Page 1.
  The dashboard shows:
    - All 12 lots with occupancy bars and status badges
    - Summary stats (total capacity, total occupied, critical lot count)
    - Clicking any lot card navigates to Page 2 (admin_lot_operations.py)

USAGE:
  from admin_dashboard import get_dashboard, get_lots_over_90
  dashboard = get_dashboard()
"""

from db_connection import get_connection


def get_dashboard():
    """
    PAGE 1 — READ: Main dashboard data.
    TRIGGER: Admin logs in or navigates to dashboard.
    RETURNS: All 12 lots with occupancy %, status level, available spaces.
    Maps to: v_lot_utilization view in admin_views.sql
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            lot_id, lot_name, capacity, current_occupancy,
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
        ORDER BY (current_occupancy / capacity) DESC
    """)
    lots = cursor.fetchall()

    # Summary stats for the top of the dashboard
    total_capacity = sum(lot["capacity"] for lot in lots)
    total_occupied = sum(lot["current_occupancy"] for lot in lots)
    critical_count = sum(1 for lot in lots if lot["status_level"] == "CRITICAL")

    cursor.close()
    conn.close()

    return {
        "lots": lots,
        "summary": {
            "total_capacity": total_capacity,
            "total_occupied": total_occupied,
            "total_available": total_capacity - total_occupied,
            "overall_occupancy_pct": round((total_occupied / total_capacity) * 100, 1),
            "critical_lots": critical_count,
            "total_lots": len(lots)
        }
    }


def get_lots_over_90():
    """
    PAGE 1 — READ: Lots that need attention (over 90% capacity).
    TRIGGER: Dashboard loads — these get highlighted in red.
    Maps to: admin_queries.sql Query 1
    Admin Story: Karen wants to see which lots are over 90%.
    Expected: Coliseum (92.5%), Lyceum (92.5%), Jackson (91.4%), Student Union (91.0%)
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT lot_id, lot_name, capacity, current_occupancy,
               capacity - current_occupancy AS available_spaces,
               ROUND((current_occupancy / capacity) * 100, 1) AS occupancy_pct
        FROM parking_lots
        WHERE (current_occupancy / capacity) * 100 >= 90
        ORDER BY occupancy_pct DESC
    """)
    lots = cursor.fetchall()
    cursor.close()
    conn.close()
    return lots


def get_ev_charger_summary():
    """
    PAGE 1 — READ: EV charger status across all lots.
    TRIGGER: Dashboard loads — shows EV section.
    Maps to: v_ev_charger_summary view in admin_views.sql
    Admin Story: Karen wants to see which lots have zero EV chargers.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            pl.lot_id, pl.lot_name, pl.capacity, pl.ev_charger_count,
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
        ORDER BY pl.ev_charger_count ASC, pl.lot_name
    """)
    summary = cursor.fetchall()
    cursor.close()
    conn.close()
    return summary


def get_peak_occupancy(lot_id):
    """
    PAGE 1 — READ: Peak occupancy data for a specific lot.
    TRIGGER: Admin clicks to see peak hours for a lot.
    Maps to: admin_queries.sql Query 4
    Admin Story: Karen reviews occupancy log to find peak hours.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            pl.lot_name, pol.recorded_at, pol.occupancy, pl.capacity,
            ROUND((pol.occupancy / pl.capacity) * 100, 1) AS occupancy_pct,
            pol.ev_chargers_in_use, pl.ev_charger_count
        FROM parking_occupancy_log pol
        JOIN parking_lots pl ON pol.lot_id = pl.lot_id
        WHERE pl.lot_id = %s
        ORDER BY pol.recorded_at
    """, (lot_id,))
    logs = cursor.fetchall()
    cursor.close()
    conn.close()
    return logs


def get_occupancy_trends():
    """
    PAGE 1 — READ: Hourly occupancy trends for all lots with log data.
    TRIGGER: Dashboard loads analytics section.
    Maps to: v_occupancy_trends view in admin_views.sql
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            pl.lot_id, pl.lot_name, pl.capacity, pl.ev_charger_count,
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
        ORDER BY pl.lot_name, pol.recorded_at
    """)
    trends = cursor.fetchall()
    cursor.close()
    conn.close()
    return trends


def get_overloaded_vs_underutilized(permit_id="S"):
    """
    PAGE 1 — READ: Compare overloaded lots vs underutilized lots
    that accept the same permit type.
    Maps to: admin_queries.sql Query 3
    Admin Story: Karen compares Coliseum (92.5%) vs South Lot 6 (35%),
    both accept S permits — she can recommend redistribution.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            pl.lot_name, pl.capacity, pl.current_occupancy,
            ROUND((pl.current_occupancy / pl.capacity) * 100, 1) AS occupancy_pct,
            p.permit_name, pr.day_of_week, pr.start_time, pr.end_time,
            CASE
                WHEN (pl.current_occupancy / pl.capacity) * 100 >= 90 THEN 'OVERLOADED'
                WHEN (pl.current_occupancy / pl.capacity) * 100 <= 50 THEN 'UNDERUTILIZED'
                ELSE 'NORMAL'
            END AS load_status
        FROM parking_rules pr
        JOIN parking_lots pl ON pr.lot_id = pl.lot_id
        JOIN permits p ON pr.permit_id = p.permit_id
        WHERE p.permit_id = %s
          AND FIND_IN_SET('Mon', pr.day_of_week) > 0
        ORDER BY occupancy_pct DESC
    """, (permit_id,))
    comparison = cursor.fetchall()
    cursor.close()
    conn.close()
    return comparison
