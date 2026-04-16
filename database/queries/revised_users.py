"""
database/queries/users.py
=========================
User-related database queries + bcrypt password hashing.

Follows the existing project pattern:
  - imports get_connection from db.py
  - try/except/finally with print-based error logging
  - procedural functions (no class wrapping)

Functions in this file:
  hash_password(plain)            → bcrypt hash string
  verify_password(plain, stored)  → bool (optional helper)
  create_user(...)                → hashes + inserts into users table
  get_user(email)                 → returns user dict for login
  get_all_users()                 → returns list of all users
  update_user_email(user_id, ...) → edit email
  delete_user(user_id)            → remove a user
  gen_userid(permit)              → auto-generate stu005/fac004/vis003-style ID

REQUIREMENTS:
  pip install bcrypt mysql-connector-python
"""

import sys, os
import bcrypt
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from db import get_connection


# ============================================================
# PASSWORD HASHING HELPERS
# ============================================================
# These are small utility functions. create_user() uses hash_password
# internally. verify_password is optional — login_screen.py already
# does bcrypt.checkpw inline, but we expose it here in case you want
# it for a "change password" feature later.

def hash_password(plain_password):
    """
    Hash a plain-text password using bcrypt.
    Returns a UTF-8 string ready to store in users.password_hash.
    """
    salt = bcrypt.gensalt()
    tmp = plain_password.encode("utf-8")
    return bcrypt.hashpw(tmp, salt).decode("utf-8")


def verify_password(plain_password, stored_hash):
    """
    Check if a plain password matches a stored bcrypt hash.
    Returns True/False. Useful for password confirmation flows.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        stored_hash.encode("utf-8"),
    )


# ============================================================
# CREATE USER (signup)
# ============================================================

def create_user(user_id, first_name, last_name, email, password, role):
    """
    Insert a new user into the users table with a properly
    bcrypt-hashed password.

    Called from create_account_screen.py after the signup form.
    `password` is plain text — we hash it here before it ever
    touches the database.
    """
    conn = get_connection()
    cursor = conn.cursor()
    passwd = hash_password(password)

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


# ============================================================
# GET USER (login)
# ============================================================

def get_user(email):
    """
    Look up a user by email. Returns a dict with the user's info
    + their permit name (joined from user_permits + permits).

    Used by login_screen.py — the returned dict needs:
      user_id, first_name, last_name, email, password_hash,
      role, user_permit_name
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT u.*, p.permit_name AS user_permit_name
            FROM users u
            LEFT JOIN user_permits up ON u.user_id = up.user_id
            LEFT JOIN permits p ON up.permit_id = p.permit_id
            WHERE u.email = %s
        """, (email,))
        return cursor.fetchone()
    except Exception as e:
        print("Error fetching user:", e)
        return None
    finally:
        cursor.close()
        conn.close()


# ============================================================
# GET ALL USERS (admin)
# ============================================================

def get_all_users():
    """
    Return every user in the database.
    Used by the admin panel users section.
    """
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


# ============================================================
# UPDATE USER EMAIL
# ============================================================

def update_user_email(user_id, new_email):
    """
    Change a user's email address.
    """
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


# ============================================================
# DELETE USER
# ============================================================

def delete_user(user_id):
    """
    Remove a user from the database.
    NOTE: If the user has rows in user_permits, you'll hit a
    foreign key error. Consider deleting their user_permits
    entries first, or use ON DELETE CASCADE on that table.
    """
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


# ============================================================
# GENERATE USER ID
# ============================================================

def gen_userid(permit):
    """
    Generate the next user_id for a given role/permit.
    Takes first 3 chars of the permit name (e.g. "Student" → "stu")
    and appends a 3-digit counter.

    Returns: 'stu005', 'fac004', 'vis003' etc.

    NOTE: Uses MAX(numeric_suffix) + 1 rather than COUNT + 1 so the
    function stays safe if any users get deleted in the middle of
    the sequence (e.g. stu002 removed → next would still be stu005,
    not stu004 which would be a silent collision).
    """
    conn = get_connection()
    cursor = conn.cursor()
    permit = permit[:3].lower()

    try:
        # Find the highest existing numeric suffix for this prefix
        cursor.execute(
            """
            SELECT user_id FROM users
            WHERE user_id LIKE %s
            ORDER BY CAST(SUBSTRING(user_id, 4) AS UNSIGNED) DESC
            LIMIT 1
            """,
            (f"{permit}%",),
        )
        row = cursor.fetchone()

        if row is None:
            next_num = 1
        else:
            # row[0] is e.g. 'stu004' — strip the 3-letter prefix, add 1
            next_num = int(row[0][3:]) + 1

        str_count = str(next_num)
        while len(str_count) != 3:
            str_count = "0" + str_count

        print(f"USER ID: {permit}{str_count}")
        return f"{permit}{str_count}"

    except Exception as e:
        print("Error creating User ID: ", e)
    finally:
        cursor.close()
        conn.close()