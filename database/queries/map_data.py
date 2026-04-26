import sys, os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import get_connection


def get_map_lot_lookup():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                lot_id,
                polygon_id,
                lot_name,
                zone,
                capacity,
                current_occupancy,
                latitude,
                longitude
            FROM parking_lots
            WHERE polygon_id IS NOT NULL
        """)
        rows = cursor.fetchall()
        return {
            row["polygon_id"]: row
            for row in rows
            if row.get("polygon_id")
        }
    except Exception as e:
        print("Error fetching map lot lookup:", e)
        return {}
    finally:
        cursor.close()
        conn.close()


def get_user_allowed_lots(user_id):
    """
    Return all lots a user is allowed to park in right now, based on
    user_permits + parking_rules + day/time checks — same logic as
    can_user_park_in_polygon but in one bulk query.
    Admins get all lots.
    Returns a dict keyed by polygon_id (same shape as get_map_lot_lookup).
    """
    if not user_id:
        return {}

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    now = datetime.now()
    current_day = now.strftime("%a")
    current_time = now.strftime("%H:%M:%S")

    try:
        # Admin bypass — return every lot
        cursor.execute("""
            SELECT role FROM users WHERE user_id = %s LIMIT 1
        """, (user_id,))
        user_row = cursor.fetchone()
        if user_row and user_row.get("role") == "admin":
            cursor.execute("""
                SELECT lot_id, polygon_id, lot_name, zone,
                       capacity, current_occupancy, latitude, longitude
                FROM parking_lots
                WHERE polygon_id IS NOT NULL
            """)
            rows = cursor.fetchall()
            return {
                row["polygon_id"]: row
                for row in rows
                if row.get("polygon_id")
            }

        # Regular users — filter through parking_rules
        cursor.execute("""
            SELECT DISTINCT
                pl.lot_id,
                pl.polygon_id,
                pl.lot_name,
                pl.zone,
                pl.capacity,
                pl.current_occupancy,
                pl.latitude,
                pl.longitude
            FROM user_permits up
            JOIN parking_rules pr ON up.permit_id = pr.permit_id
            JOIN parking_lots pl ON pr.lot_id = pl.lot_id
            WHERE up.user_id = %s
              AND pr.is_allowed = TRUE
              AND up.status = 'active'
              AND up.expiration_date >= NOW()
              AND FIND_IN_SET(%s, pr.day_of_week)
              AND %s BETWEEN pr.start_time AND pr.end_time
              AND pl.polygon_id IS NOT NULL
        """, (user_id, current_day, current_time))
        rows = cursor.fetchall()
        return {
            row["polygon_id"]: row
            for row in rows
            if row.get("polygon_id")
        }

    except Exception as e:
        print("Error fetching user-allowed lots:", e)
        return {}
    finally:
        cursor.close()
        conn.close()


def can_user_park_in_polygon(user_id, polygon_id):
    if not user_id or not polygon_id:
        return None

    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now()
    current_day = now.strftime("%a")
    current_time = now.strftime("%H:%M:%S")

    try:
        # Admin users can park in any lot — they have no user_permits/parking_rules rows
        cursor.execute("""
            SELECT role FROM users WHERE user_id = %s LIMIT 1
        """, (user_id,))
        user_row = cursor.fetchone()
        if user_row and user_row[0] == "admin":
            return True

        cursor.execute("""
            SELECT 1
            FROM user_permits up
            JOIN parking_rules pr ON up.permit_id = pr.permit_id
            JOIN parking_lots pl ON pr.lot_id = pl.lot_id
            WHERE up.user_id = %s
              AND pl.polygon_id = %s
              AND pr.is_allowed = TRUE
              AND up.status = 'active'
              AND up.expiration_date >= NOW()
              AND FIND_IN_SET(%s, pr.day_of_week)
              AND %s BETWEEN pr.start_time AND pr.end_time
            LIMIT 1
        """, (user_id, polygon_id, current_day, current_time))
        return cursor.fetchone() is not None
    except Exception as e:
        print("Error checking parking rule eligibility:", e)
        return None
    finally:
        cursor.close()
        conn.close()
