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

def create_ticket(user_id, amount, description, status):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO tickets (user_id, amount, description, status)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, amount, description, status))
        conn.commit()
        return {"ok": True, "message": "Ticket created."}
    except Exception as e:
        if conn:
            conn.rollback()
        print("Error creating ticket:", e)
        return {"ok": False, "message": "Unable to create ticket."}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def delete_ticket(ticket_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM tickets WHERE ticket_id = %s", (ticket_id,))
        conn.commit()
        return {"ok": True}
    except Exception as e:
        conn.rollback()
        print("Error deleting ticket:", e)
        return {"ok": False}
    finally:
        cursor.close()
        conn.close()

def toggle_ticket_status(ticket_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE tickets SET status = %s WHERE ticket_id = %s", (new_status, ticket_id))
        conn.commit()
        return {"ok": True}
    except Exception as e:
        conn.rollback()
        print("Error toggling ticket status:", e)
        return {"ok": False}
    finally:
        cursor.close()
        conn.close()

def pay_all_user_tickets(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    query = "UPDATE tickets SET status = 'Paid' WHERE user_id = %s AND status = 'Unpaid'"
    cursor.execute(query, (user_id,))
    conn.commit()
    conn.close()
