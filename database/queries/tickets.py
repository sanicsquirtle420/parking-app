import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import get_connection

def get_user_tickets(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT ticket_id, issue_date, amount, status, description FROM tickets WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchall()
    conn.close()
    return result

def pay_all_user_tickets(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    query = "UPDATE tickets SET status = 'Paid' WHERE user_id = %s AND status = 'Unpaid'"
    cursor.execute(query, (user_id,))
    conn.commit()
    conn.close()