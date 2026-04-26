from database.db import get_connection


def get_all_lots():
    """Return all parking lots with occupancy and EV charger info."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT
                lot_id,
                lot_name,
                capacity,
                current_occupancy,
                ev_charger_count,
                CASE
                    WHEN capacity > 0
                    THEN ROUND((current_occupancy / capacity) * 100, 1)
                    ELSE 0
                END AS utilization_pct
            FROM parking_lots
            ORDER BY lot_name
        """)
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching lots:", e)
        return []
    finally:
        cursor.close()
        conn.close()