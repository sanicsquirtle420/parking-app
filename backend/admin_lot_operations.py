"""
admin_lot_operations.py
=======================
Page 2 — Lot Detail: All CRUD operations for parking lots, rules, and occupancy.

This file maps directly to crud_operations.sql Page 2 section.
Every function is named after the action the admin performs in the UI.

SITEMAP CONTEXT:
  Admin clicks a lot card on Page 1 (dashboard) → lands on Page 2 for that lot.
  Page 2 has three sections:
    1. Lot info (name, capacity, coordinates, EV chargers) — edit/delete
    2. Rules table (permit type, days, time window) — add/edit/toggle/delete
    3. Occupancy section — update current count + auto-log

USAGE:
  from admin_lot_operations import create_lot, update_lot_capacity, add_rule
  result = create_lot("New Engineering Garage", 34.3650, -89.5370, 200, 4)
"""

from db_connection import get_connection


# =============================================================
# LOT CRUD OPERATIONS
# =============================================================


def get_lot_detail(lot_id):
    """
    PAGE 2 — READ: Load all info for a specific lot.
    TRIGGER: Admin clicks a lot card on Page 1 dashboard.
    RETURNS: Lot info + all rules + recent occupancy logs.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Get lot info
    cursor.execute("""
        SELECT lot_id, lot_name, latitude, longitude, capacity,
               current_occupancy, ev_charger_count,
               capacity - current_occupancy AS available_spaces,
               ROUND((current_occupancy / capacity) * 100, 1) AS occupancy_pct
        FROM parking_lots
        WHERE lot_id = %s
    """, (lot_id,))
    lot = cursor.fetchone()

    # Get all rules for this lot
    cursor.execute("""
        SELECT pr.rule_id, p.permit_id, p.permit_name,
               pr.day_of_week, pr.start_time, pr.end_time, pr.is_allowed
        FROM parking_rules pr
        JOIN permits p ON pr.permit_id = p.permit_id
        WHERE pr.lot_id = %s
        ORDER BY p.permit_name, pr.day_of_week
    """, (lot_id,))
    rules = cursor.fetchall()

    # Get recent occupancy logs (last 20 entries)
    cursor.execute("""
        SELECT log_id, recorded_at, occupancy, ev_chargers_in_use
        FROM parking_occupancy_log
        WHERE lot_id = %s
        ORDER BY recorded_at DESC
        LIMIT 20
    """, (lot_id,))
    logs = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "lot": lot,
        "rules": rules,
        "occupancy_logs": logs
    }


def create_lot(lot_name, latitude, longitude, capacity, ev_charger_count=0):
    """
    PAGE 2 — CREATE: Add a new parking lot.
    TRIGGER: Admin clicks "Add New Lot" on Page 1, fills blank form, hits Save.
    FRONTEND FIELDS: lot_name, latitude, longitude, capacity, ev_charger_count.
    NOTE: lot_id is AUTO_INCREMENT. current_occupancy starts at 0.
    RETURNS: {"success": True, "lot_id": new_id} or {"success": False, "error": msg}
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # VALIDATION: Check lot name doesn't already exist
    cursor.execute(
        "SELECT COUNT(*) AS name_exists FROM parking_lots WHERE lot_name = %s",
        (lot_name,)
    )
    if cursor.fetchone()["name_exists"] > 0:
        cursor.close()
        conn.close()
        return {"success": False, "error": "A lot with this name already exists"}

    # INSERT the new lot
    cursor.execute("""
        INSERT INTO parking_lots (lot_name, latitude, longitude, capacity,
                                  current_occupancy, ev_charger_count)
        VALUES (%s, %s, %s, %s, 0, %s)
    """, (lot_name, latitude, longitude, capacity, ev_charger_count))

    new_lot_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()

    return {"success": True, "lot_id": new_lot_id}


def update_lot_name(lot_id, lot_name):
    """
    PAGE 2 — UPDATE: Edit lot name.
    TRIGGER: Admin clicks "Edit" next to lot name, types new name, hits Save.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE parking_lots SET lot_name = %s WHERE lot_id = %s",
        (lot_name, lot_id)
    )
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()
    return {"success": affected > 0}


def update_lot_capacity(lot_id, capacity):
    """
    PAGE 2 — UPDATE: Edit lot capacity.
    TRIGGER: Admin clicks "Edit" next to capacity (e.g. construction added spots).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE parking_lots SET capacity = %s WHERE lot_id = %s",
        (capacity, lot_id)
    )
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()
    return {"success": affected > 0}


def update_lot_ev_chargers(lot_id, ev_charger_count):
    """
    PAGE 2 — UPDATE: Edit EV charger count.
    TRIGGER: Admin clicks "Edit" next to EV chargers (new chargers installed).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE parking_lots SET ev_charger_count = %s WHERE lot_id = %s",
        (ev_charger_count, lot_id)
    )
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()
    return {"success": affected > 0}


def update_lot_coordinates(lot_id, latitude, longitude):
    """
    PAGE 2 — UPDATE: Edit lot map location.
    TRIGGER: Admin clicks "Edit" next to coordinates.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE parking_lots SET latitude = %s, longitude = %s WHERE lot_id = %s",
        (latitude, longitude, lot_id)
    )
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()
    return {"success": affected > 0}


def update_lot_all(lot_id, lot_name, capacity, latitude, longitude, ev_charger_count):
    """
    PAGE 2 — UPDATE: Edit multiple lot fields at once.
    TRIGGER: Admin edits several fields then hits one "Save All" button.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE parking_lots
        SET lot_name = %s, capacity = %s, latitude = %s,
            longitude = %s, ev_charger_count = %s
        WHERE lot_id = %s
    """, (lot_name, capacity, latitude, longitude, ev_charger_count, lot_id))
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()
    return {"success": affected > 0}


def decommission_lot(lot_id):
    """
    PAGE 2 — DELETE: Remove a parking lot and all its rules/logs.
    TRIGGER: Admin clicks "Decommission Lot" button, confirms in dialog.
    IMPORTANT: Deletes in order due to foreign keys:
      1. parking_occupancy_log (references lot_id)
      2. parking_rules (references lot_id)
      3. parking_lots (the lot itself)
    RETURNS: Impact info + success status.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # PRE-DELETE: Show admin what will be affected
    cursor.execute("""
        SELECT
            (SELECT COUNT(*) FROM parking_rules WHERE lot_id = %s) AS rules_to_delete,
            (SELECT COUNT(*) FROM parking_occupancy_log WHERE lot_id = %s) AS logs_to_delete
    """, (lot_id, lot_id))
    impact = cursor.fetchone()

    # CASCADE DELETE in correct order
    cursor.execute("DELETE FROM parking_occupancy_log WHERE lot_id = %s", (lot_id,))
    cursor.execute("DELETE FROM parking_rules WHERE lot_id = %s", (lot_id,))
    cursor.execute("DELETE FROM parking_lots WHERE lot_id = %s", (lot_id,))

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "success": True,
        "rules_deleted": impact["rules_to_delete"],
        "logs_deleted": impact["logs_to_delete"]
    }


# =============================================================
# RULE CRUD OPERATIONS
# =============================================================


def get_permit_dropdown():
    """
    HELPER: Populate the permit type dropdown for the "Add Rule" form.
    RETURNS: List of {permit_id, permit_name}.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT permit_id, permit_name FROM permits ORDER BY permit_name")
    permits = cursor.fetchall()
    cursor.close()
    conn.close()
    return permits


def add_rule(lot_id, permit_id, day_of_week, start_time, end_time):
    """
    PAGE 2 — CREATE: Add a new parking rule to this lot.
    TRIGGER: Admin clicks "Add Rule" above the rules table, fills form, hits Save.
    FRONTEND FIELDS:
      lot_id     → hidden (from current page's lot)
      permit_id  → dropdown (from get_permit_dropdown())
      day_of_week → checkboxes joined as comma string (e.g. 'Mon,Tue,Wed,Thu,Fri')
      start_time → time picker (e.g. '07:00:00')
      end_time   → time picker (e.g. '17:00:00')
    NOTE: rule_id is AUTO_INCREMENT. is_allowed defaults to TRUE.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # VALIDATION: Check this exact rule doesn't already exist
    cursor.execute("""
        SELECT COUNT(*) AS rule_exists FROM parking_rules
        WHERE lot_id = %s AND permit_id = %s AND day_of_week = %s
              AND start_time = %s AND end_time = %s
    """, (lot_id, permit_id, day_of_week, start_time, end_time))

    if cursor.fetchone()["rule_exists"] > 0:
        cursor.close()
        conn.close()
        return {"success": False, "error": "This rule already exists for this lot"}

    cursor.execute("""
        INSERT INTO parking_rules (lot_id, permit_id, day_of_week, start_time, end_time)
        VALUES (%s, %s, %s, %s, %s)
    """, (lot_id, permit_id, day_of_week, start_time, end_time))

    conn.commit()
    new_rule_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return {"success": True, "rule_id": new_rule_id}


def update_rule(rule_id, permit_id, day_of_week, start_time, end_time):
    """
    PAGE 2 — UPDATE: Edit an existing parking rule.
    TRIGGER: Admin clicks "Edit" on a rule row, changes fields, hits Save.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE parking_rules
        SET permit_id = %s, day_of_week = %s, start_time = %s, end_time = %s
        WHERE rule_id = %s
    """, (permit_id, day_of_week, start_time, end_time, rule_id))
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()
    return {"success": affected > 0}


def toggle_rule(rule_id, enable):
    """
    PAGE 2 — UPDATE: Enable or disable a rule without deleting it.
    TRIGGER: Admin clicks a toggle switch on a rule row.
    USE CASE: Temporarily close a lot for construction — disable rules
              for a few days, re-enable later without recreating them.
    PARAMS: enable = True to enable, False to disable.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE parking_rules SET is_allowed = %s WHERE rule_id = %s",
        (enable, rule_id)
    )
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()
    return {"success": affected > 0}


def delete_rule(rule_id):
    """
    PAGE 2 — DELETE: Remove a parking rule.
    TRIGGER: Admin clicks "Delete" on a rule row, confirms in dialog.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # PRE-DELETE: Get rule details for the confirmation dialog
    cursor.execute("""
        SELECT p.permit_name, pr.day_of_week, pr.start_time, pr.end_time
        FROM parking_rules pr
        JOIN permits p ON pr.permit_id = p.permit_id
        WHERE pr.rule_id = %s
    """, (rule_id,))
    rule_info = cursor.fetchone()

    cursor.execute("DELETE FROM parking_rules WHERE rule_id = %s", (rule_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return {"success": True, "deleted_rule": rule_info}


# =============================================================
# OCCUPANCY OPERATIONS
# =============================================================


def update_occupancy(lot_id, occupancy, ev_chargers_in_use=0):
    """
    PAGE 2 — UPDATE + CREATE: Update current occupancy and log it.
    TRIGGER: Admin enters new occupancy number in the occupancy section, hits Save.
    THIS DOES TWO THINGS:
      1. Updates current_occupancy in parking_lots (UPDATE)
      2. Logs the reading in parking_occupancy_log (CREATE)
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # VALIDATION: Occupancy can't exceed capacity
    cursor.execute("SELECT capacity FROM parking_lots WHERE lot_id = %s", (lot_id,))
    lot = cursor.fetchone()

    if lot is None:
        cursor.close()
        conn.close()
        return {"success": False, "error": "Lot not found"}

    if occupancy > lot["capacity"]:
        cursor.close()
        conn.close()
        return {"success": False, "error": f"Occupancy cannot exceed lot capacity ({lot['capacity']})"}

    # STEP 1: Update the live occupancy number
    cursor.execute(
        "UPDATE parking_lots SET current_occupancy = %s WHERE lot_id = %s",
        (occupancy, lot_id)
    )

    # STEP 2: Log this reading for historical tracking
    cursor.execute("""
        INSERT INTO parking_occupancy_log (lot_id, recorded_at, occupancy, ev_chargers_in_use)
        VALUES (%s, NOW(), %s, %s)
    """, (lot_id, occupancy, ev_chargers_in_use))

    conn.commit()
    cursor.close()
    conn.close()

    return {"success": True, "lot_id": lot_id, "new_occupancy": occupancy}
