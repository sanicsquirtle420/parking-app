from database.db import get_connection

def get_analytics_data():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                COUNT(*) AS total_lots,
                SUM(CASE WHEN current_occupancy >= capacity * 0.9 THEN 1 ELSE 0 END) AS critical_lots,
                ROUND(AVG((current_occupancy / capacity) * 100), 1) AS avg_utilization,
                SUM(CASE WHEN ev_charger_count = 0 THEN 1 ELSE 0 END) AS no_ev
            FROM parking_lots
        """)
        overview = cursor.fetchone()

        cursor.execute("""
            SELECT parking_lots.lot_name, MAX(occupancy) as peak_occupancy
            FROM parking_occupancy_log
            LEFT JOIN parking_lots ON parking_occupancy_log.lot_id = parking_lots.lot_id
            GROUP BY parking_lots.lot_id
        """)
        peak = cursor.fetchall()

        cursor.execute("""
            SELECT
                lot_name,
                ev_charger_count,
                current_occupancy
            FROM parking_lots
            WHERE ev_charger_count > 0
        """)
        ev = cursor.fetchall()

        cursor.execute("""
            SELECT
                lot_name,
                capacity,
                current_occupancy,
                ROUND((current_occupancy / capacity) * 100, 1) AS utilization
            FROM parking_lots
        """)
        lots = cursor.fetchall()

        overloaded = [l for l in lots if l["utilization"] >= 90]
        underutilized = [l for l in lots if l["utilization"] <= 40]

        return {
            "overview": overview,
            "peak": peak,
            "ev": ev,
            "overloaded": overloaded,
            "underutilized": underutilized
        }

    except Exception as e:
        print("Analytics DB error:", e)
        return None

    finally:
        cursor.close()
        conn.close()
