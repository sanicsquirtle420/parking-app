from datetime import datetime

from database.db import get_connection


def _result(ok, message):
    return {"ok": ok, "message": message}


def _normalize_time(value):
    raw = (value or "").strip()
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            parsed = datetime.strptime(raw, fmt)
            return parsed.strftime("%H:%M:%S")
        except ValueError:
            continue
    raise ValueError("Invalid time format")


def get_admin_lot_detail_snapshot(lot_id):
    conn = get_connection()
    lot_cursor = conn.cursor(dictionary=True)
    permit_cursor = conn.cursor(dictionary=True)
    rule_cursor = conn.cursor(dictionary=True)

    try:
        lot_cursor.execute("""
            SELECT
                lot_id,
                lot_name,
                capacity,
                current_occupancy,
                ev_charger_count
            FROM parking_lots
            WHERE lot_id = %s
        """, (lot_id,))
        lot = lot_cursor.fetchone()

        permit_cursor.execute("""
            SELECT permit_id, permit_name
            FROM permits
            ORDER BY permit_name
        """)
        permits = permit_cursor.fetchall()

        rule_cursor.execute("""
            SELECT
                pr.rule_id,
                pr.permit_id,
                p.permit_name,
                pr.day_of_week,
                pr.start_time,
                pr.end_time,
                pr.is_allowed
            FROM parking_rules pr
            JOIN permits p ON pr.permit_id = p.permit_id
            WHERE pr.lot_id = %s
            ORDER BY pr.day_of_week, pr.start_time, p.permit_name
        """, (lot_id,))
        rules = rule_cursor.fetchall()

        return {"lot": lot, "permits": permits, "rules": rules}
    except Exception as e:
        print("Error fetching lot detail snapshot:", e)
        return None
    finally:
        lot_cursor.close()
        permit_cursor.close()
        rule_cursor.close()
        conn.close()


def update_lot_capacity(lot_id, capacity):
    if capacity < 0:
        return _result(False, "Capacity must be zero or greater.")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT current_occupancy
            FROM parking_lots
            WHERE lot_id = %s
        """, (lot_id,))
        row = cursor.fetchone()
        if not row:
            return _result(False, "Lot not found.")

        current_occupancy = row[0]
        if capacity < current_occupancy:
            return _result(False, "Capacity cannot be below current occupancy.")

        cursor.execute("""
            UPDATE parking_lots
            SET capacity = %s
            WHERE lot_id = %s
        """, (capacity, lot_id))
        conn.commit()
        return _result(True, "Capacity updated.")
    except Exception as e:
        conn.rollback()
        print("Error updating lot capacity:", e)
        return _result(False, "Unable to update capacity.")
    finally:
        cursor.close()
        conn.close()

def update_lot_occupancy(lot_id, occupancy):
    if occupancy < 0:
        return _result(False, "Occupancy must be zero or greater.")

    conn = get_connection()
    lot_cursor = conn.cursor()
    log_cursor = conn.cursor()

    try:
        lot_cursor.execute("""
            SELECT capacity
            FROM parking_lots
            WHERE lot_id = %s
        """, (lot_id,))
        row = lot_cursor.fetchone()
        if not row:
            return _result(False, "Lot not found.")

        capacity = row[0]
        if occupancy > capacity:
            return _result(False, "Occupancy cannot exceed capacity.")

        lot_cursor.execute("""
            UPDATE parking_lots
            SET current_occupancy = %s
            WHERE lot_id = %s
        """, (occupancy, lot_id))

        log_cursor.execute("""
            INSERT INTO parking_occupancy_log (lot_id, recorded_at, occupancy, ev_chargers_in_use)
            VALUES (%s, NOW(), %s, %s)
        """, (lot_id, occupancy, 0))

        conn.commit()
        return _result(True, "Occupancy updated.")
    except Exception as e:
        conn.rollback()
        print("Error updating lot occupancy:", e)
        return _result(False, "Unable to update occupancy.")
    finally:
        lot_cursor.close()
        log_cursor.close()
        conn.close()


def update_ev_chargers(lot_id, ev_charger_count):
    if ev_charger_count < 0:
        return _result(False, "EV charger count must be zero or greater.")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE parking_lots
            SET ev_charger_count = %s
            WHERE lot_id = %s
        """, (ev_charger_count, lot_id))
        conn.commit()
        if cursor.rowcount == 0:
            return _result(False, "Lot not found.")
        return _result(True, "EV charger count updated.")
    except Exception as e:
        conn.rollback()
        print("Error updating EV chargers:", e)
        return _result(False, "Unable to update EV chargers.")
    finally:
        cursor.close()
        conn.close()


def add_rule(lot_id, permit_id, day_of_week, start_time, end_time):
    try:
        normalized_start = _normalize_time(start_time)
        normalized_end = _normalize_time(end_time)
    except ValueError:
        return _result(False, "Times must use HH:MM or HH:MM:SS.")

    day_of_week = (day_of_week or "").strip()
    if not day_of_week:
        return _result(False, "Select at least one day.")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COUNT(*)
            FROM parking_rules
            WHERE lot_id = %s
              AND permit_id = %s
              AND day_of_week = %s
              AND start_time = %s
              AND end_time = %s
        """, (lot_id, permit_id, day_of_week, normalized_start, normalized_end))
        if cursor.fetchone()[0]:
            return _result(False, "That rule already exists.")

        cursor.execute("""
            INSERT INTO parking_rules (lot_id, permit_id, day_of_week, start_time, end_time)
            VALUES (%s, %s, %s, %s, %s)
        """, (lot_id, permit_id, day_of_week, normalized_start, normalized_end))
        conn.commit()
        return _result(True, "Rule added.")
    except Exception as e:
        conn.rollback()
        print("Error adding parking rule:", e)
        return _result(False, "Unable to add rule.")
    finally:
        cursor.close()
        conn.close()


def toggle_rule(rule_id, is_allowed):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE parking_rules
            SET is_allowed = %s
            WHERE rule_id = %s
        """, (not bool(is_allowed), rule_id))
        conn.commit()
        if cursor.rowcount == 0:
            return _result(False, "Rule not found.")
        return _result(True, "Rule updated.")
    except Exception as e:
        conn.rollback()
        print("Error toggling parking rule:", e)
        return _result(False, "Unable to update rule.")
    finally:
        cursor.close()
        conn.close()


def delete_rule(rule_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            DELETE FROM parking_rules
            WHERE rule_id = %s
        """, (rule_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return _result(False, "Rule not found.")
        return _result(True, "Rule deleted.")
    except Exception as e:
        conn.rollback()
        print("Error deleting parking rule:", e)
        return _result(False, "Unable to delete rule.")
    finally:
        cursor.close()
        conn.close()
