import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import get_connection

def create_user(user_id, first_name, last_name, email, password_hash, role):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (user_id, first_name, last_name, email, password_hash, role)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, first_name, last_name, email, password_hash, role))

        conn.commit()
        print("User created successfully")

    except Exception as e:
        print("Error creating user:", e)

    finally:
        cursor.close()
        conn.close()

def get_user(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT 
                u.*, 
                p.permit_name AS user_permit_name 
            FROM users u
            LEFT JOIN user_permits up ON u.user_id = up.user_id
            LEFT JOIN permits p ON up.permit_id = p.permit_id
            WHERE u.user_id = %s
        """, (user_id,))

        return cursor.fetchone()

    except Exception as e:
        print("Error fetching user:", e)
        return None

    finally:
        cursor.close()
        conn.close()

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()

    except Exception as e:
        print("Error fetching users:", e)
        return []

    finally:
        cursor.close()
        conn.close()

def update_user_email(user_id, new_email):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE users
            SET email = %s
            WHERE user_id = %s
        """, (new_email, user_id))

        conn.commit()
        print("User updated successfully")

    except Exception as e:
        print("Error updating user:", e)

    finally:
        cursor.close()
        conn.close()

def delete_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM users WHERE user_id = %s
        """, (user_id,))

        conn.commit()
        print("User deleted successfully")

    except Exception as e:
        print("Error deleting user:", e)

    finally:
        cursor.close()
        conn.close()