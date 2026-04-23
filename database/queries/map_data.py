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
                polygon_id,
                lot_name,
                zone,
                capacity,
                current_occupancy
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


def can_user_park_in_polygon(user_id, polygon_id):
    if not user_id or not polygon_id:
        return None

    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now()
    current_day = now.strftime("%a")
    current_time = now.strftime("%H:%M:%S")

    try:
        cursor.execute("""
            SELECT 1
            FROM user_permits up
            JOIN parking_rules pr ON up.permit_id = pr.permit_id
            JOIN parking_lots pl ON pr.lot_id = pl.lot_id
            WHERE up.user_id = %s
              AND pl.polygon_id = %s
              AND pr.is_allowed = TRUE
              AND up.expiration_date >= CURDATE()
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
