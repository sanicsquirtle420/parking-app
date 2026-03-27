from db import get_connection
from datetime import datetime

def get_available_parking(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    now = datetime.now()
    current_day = now.strftime('%a')
    current_time = now.strftime('%H:%M:%S')

    try:
        cursor.execute("""
            SELECT DISTINCT 
                pl.lot_id,
                pl.lot_name,
                pl.capacity,
                pl.current_occupancy,
                (pl.capacity - pl.current_occupancy) AS spots_left
            FROM users u
            JOIN user_permits up ON u.user_id = up.user_id
            JOIN parking_rules pr ON up.permit_id = pr.permit_id
            JOIN parking_lots pl ON pr.lot_id = pl.lot_id
            WHERE u.user_id = %s
              AND FIND_IN_SET(%s, pr.day_of_week)
              AND %s BETWEEN pr.start_time AND pr.end_time
              AND pl.current_occupancy < pl.capacity
        """, (user_id, current_day, current_time))

        return cursor.fetchall()

    except Exception as e:
        print("Error fetching parking:", e)
        return []

    finally:
        cursor.close()
        conn.close()

def get_best_parking(user_id):
    lots = get_available_parking(user_id)
    if not lots:
        return None
    
    return max(lots, key=lambda x: x['spots_left'])

def get_ranked_parking(user_id):
    lots = get_available_parking(user_id)
    # Sort lots by spots left descending
    return sorted(lots, key=lambda x: x['spots_left'], reverse=True)
