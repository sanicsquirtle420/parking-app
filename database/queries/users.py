import sys, os
import bcrypt

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import get_connection

def create_user(user_id, first_name, last_name, email, password, role):
    conn = get_connection()
    cursor = conn.cursor()
    salt = bcrypt.gensalt() 

    tmp = password.encode("utf-8") # Hashing password
    passwd = bcrypt.hashpw(tmp, salt).decode("utf-8")

    try:
        cursor.execute("""
            INSERT INTO users (user_id, first_name, last_name, email, password_hash, role)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, first_name, last_name, email, passwd, role))

        conn.commit()
        print("User created successfully")

    except Exception as e:
        conn.rollback()
        print("Error creating user:", e)
        raise

    finally:
        cursor.close()
        conn.close()

def get_user(email):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT u.*, p.permit_name AS user_permit_name
            FROM users u
            LEFT JOIN user_permits up ON u.user_id = up.user_id
            LEFT JOIN permits p on up.permit_id = p.permit_id
            WHERE u.email = %s
        """, (email,))
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

def gen_userid(permit):
    conn = get_connection()
    cursor = conn.cursor()
    permit = permit[:3].lower()

    try:
        cursor.execute(f"SELECT user_id FROM users WHERE user_id LIKE \"{permit}%\"")
        rows = cursor.fetchall()
        count = len(rows) + 1
        str_count = str(count) 
        while len(str_count) != 3 :
            str_count = "0" + str_count
        print(f"USER ID: {permit}{str_count}")
        return f"{permit}{str_count}"

    except Exception as e:
        print("Error creating User ID: ", e)
    finally:
        cursor.close()
        conn.close()