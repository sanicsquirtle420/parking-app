import sys, os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import get_connection


def start_parking_session(user_id, lot_id, polygon_id, lot_name):
    """
    Start a parking session for a user in a given lot.
    Increments current_occupancy on the lot.
    Returns the session dict on success, or None if the lot is full or user already has an active session.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Check if user already has an active session anywhere
        cursor.execute("""
            SELECT session_id, lot_name
            FROM parking_sessions
            WHERE user_id = %s AND end_time IS NULL
            LIMIT 1
        """, (user_id,))
        existing = cursor.fetchone()
        if existing:
            print(f"User {user_id} already has active session in {existing['lot_name']}")
            return None

        # Check lot capacity
        cursor.execute("""
            SELECT lot_id, lot_name, capacity, current_occupancy
            FROM parking_lots
            WHERE lot_id = %s
            LIMIT 1
        """, (lot_id,))
        lot = cursor.fetchone()
        if not lot:
            print(f"Lot {lot_id} not found")
            return None

        if lot["current_occupancy"] >= lot["capacity"]:
            print(f"Lot {lot['lot_name']} is full ({lot['current_occupancy']}/{lot['capacity']})")
            return None

        # Insert session
        cursor.execute("""
            INSERT INTO parking_sessions (user_id, lot_id, polygon_id, lot_name, start_time, end_time)
            VALUES (%s, %s, %s, %s, NOW(), NULL)
        """, (user_id, lot_id, polygon_id, lot_name))

        # Increment occupancy
        cursor.execute("""
            UPDATE parking_lots
            SET current_occupancy = current_occupancy + 1
            WHERE lot_id = %s
        """, (lot_id,))

        conn.commit()

        session_id = cursor.lastrowid
        return {
            "session_id": session_id,
            "user_id": user_id,
            "lot_id": lot_id,
            "polygon_id": polygon_id,
            "lot_name": lot_name,
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    except Exception as e:
        conn.rollback()
        print("Error starting parking session:", e)
        return None

    finally:
        cursor.close()
        conn.close()


def end_parking_session(user_id):
    """
    End the active parking session for a user.
    Decrements current_occupancy on the lot.
    Returns True on success, False if no active session found.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Find active session
        cursor.execute("""
            SELECT session_id, lot_id, lot_name
            FROM parking_sessions
            WHERE user_id = %s AND end_time IS NULL
            LIMIT 1
        """, (user_id,))
        session = cursor.fetchone()
        if not session:
            print(f"No active session for user {user_id}")
            return False

        # End the session
        cursor.execute("""
            UPDATE parking_sessions
            SET end_time = NOW()
            WHERE session_id = %s
        """, (session["session_id"],))

        # Decrement occupancy (don't go below 0)
        cursor.execute("""
            UPDATE parking_lots
            SET current_occupancy = GREATEST(current_occupancy - 1, 0)
            WHERE lot_id = %s
        """, (session["lot_id"],))

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        print("Error ending parking session:", e)
        return False

    finally:
        cursor.close()
        conn.close()


def get_active_session(user_id):
    """
    Get the active parking session for a user, if any.
    Returns session dict or None.
    """
    if not user_id:
        return None

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT session_id, user_id, lot_id, polygon_id, lot_name, start_time
            FROM parking_sessions
            WHERE user_id = %s AND end_time IS NULL
            LIMIT 1
        """, (user_id,))
        return cursor.fetchone()

    except Exception as e:
        print("Error fetching active session:", e)
        return None

    finally:
        cursor.close()
        conn.close()


def get_lot_current_occupancy(lot_id):
    """
    Get the real-time occupancy for a lot.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT lot_id, lot_name, capacity, current_occupancy,
                   (capacity - current_occupancy) AS spots_left
            FROM parking_lots
            WHERE lot_id = %s
            LIMIT 1
        """, (lot_id,))
        return cursor.fetchone()

    except Exception as e:
        print("Error fetching lot occupancy:", e)
        return None

    finally:
        cursor.close()
        conn.close()


def ensure_parking_sessions_table():
    """
    Create the parking_sessions table if it doesn't exist.
    This is safe to call repeatedly.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parking_sessions (
                session_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(20) NOT NULL,
                lot_id INT NOT NULL,
                polygon_id VARCHAR(50),
                lot_name VARCHAR(100),
                start_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                end_time DATETIME DEFAULT NULL,
                INDEX idx_user_active (user_id, end_time),
                INDEX idx_lot (lot_id)
            )
        """)
        conn.commit()

    except Exception as e:
        conn.rollback()
        print("Error creating parking_sessions table:", e)

    finally:
        cursor.close()
        conn.close()
