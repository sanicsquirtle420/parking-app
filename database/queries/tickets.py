import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import get_connection

def get_user_tickets(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT ticket_id, issue_date, amount, status, description FROM tickets WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching tickets:", e)
        return []
    finally:
        cursor.close()
        conn.close()
