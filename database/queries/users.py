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
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        rows = cursor.fetchall()

        if len(rows) > 0:
            return False
        else:
            cursor.execute("""
                INSERT INTO users (user_id, first_name, last_name, email, password_hash, role)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, first_name, last_name, email, passwd, role))

            conn.commit()
            print("User created successfully")
            return True

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
    print(f"DEBUG: Looking for prefix '{permit}'")
    new_id: str = ""
    try:
        cursor.execute(
            "SELECT COUNT(*) FROM users WHERE user_id = %s",
            (f"{permit}001",)
        )
        result = cursor.fetchone()
        print(f"DEBUG: 001 check result: {result}")

        if result[0] == 0:
            new_id = f"{permit}001"
        else:
            cursor.execute("""
                SELECT CONCAT(%s, LPAD(t.seq + 1, 3, '0')) AS next_id
                FROM (
                    SELECT CAST(SUBSTRING(user_id, 4) AS UNSIGNED) AS seq
                    FROM users
                    WHERE user_id LIKE %s
                ) AS t
                WHERE NOT EXISTS (
                    SELECT 1 FROM users
                    WHERE user_id = CONCAT(%s, LPAD(t.seq + 1, 3, '0'))
                )
                ORDER BY t.seq ASC
                LIMIT 1
            """, (permit, f"{permit}%", permit))

            row = cursor.fetchone()
            print(f"DEBUG: Gap query result: {row}")

            if row is None:
                cursor.execute("""
                    SELECT CAST(SUBSTRING(user_id, 4) AS UNSIGNED) AS seq
                    FROM users WHERE user_id LIKE %s
                    ORDER BY seq DESC LIMIT 1
                """, (f"{permit}%",))
                max_row = cursor.fetchone()
                print(f"DEBUG: Max row result: {max_row}")
                new_id = f"{permit}{str(max_row[0] + 1).zfill(3)}"
            else:
                new_id = row[0]

        print(f"USER ID: {new_id}")
        return new_id

    except Exception as e:
        print("Error creating User ID: ", e)
    finally:
        cursor.close()
        conn.close()

def get_permit_types():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT permit_name FROM permits")
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results

def add_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
        
    query = """
            INSERT INTO user_permits (user_id, permit_id, issued_date, expiration_date)
            VALUES (%s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 1 YEAR))
        """
    cursor.execute(query, (user_id, "VSD")) # Auto assigns Visitor Daily for new users
    conn.commit()

    conn.close()

def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT u.*, p.permit_name 
        FROM users u
        LEFT JOIN user_permits up ON u.user_id = up.user_id
        LEFT JOIN permits p ON up.permit_id = p.permit_id
        WHERE u.email = %s AND u.password_hash = %s
    """
    
    cursor.execute(query, (email, password))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user(email):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT u.*, p.permit_name AS user_permit_name
        FROM users u
        LEFT JOIN user_permits up ON u.user_id = up.user_id
        LEFT JOIN permits p on up.permit_id = p.permit_id
        WHERE u.email = %s
    """, (email,))

    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user