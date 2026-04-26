import sys, os
from datetime import timedelta
import bcrypt

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import get_connection


ROLE_PREFIX_BY_ROLE = {
    "student": "stu",
    "faculty": "fac",
    "admin": "adm",
    "visitor": "vis",
}

ROLE_ALIASES = {
    "faculty/staff": "faculty",
    "staff": "faculty",
}

SIGNUP_DAY_PASS_PERMIT_ID = "DAY"
SIGNUP_DAY_PASS_HOURS = 24
SIGNUP_DAY_PASS_PERMIT_NAME = "Free Day Pass"
SIGNUP_DAY_PASS_DESCRIPTION = (
    "1 day - Automatic signup day pass valid for the first 24 hours until admin assigns a permit."
)
SIGNUP_DAY_PASS_COLOR = "#FFDD57"
SIGNUP_DAY_PASS_SORT_ORDER = 85
SIGNUP_DAY_PASS_SOURCE_PERMIT_ID = "VSD"
SIGNUP_DAY_PASS_SOURCE_PERMIT_NAME = "Visitor"


def normalize_role(role):
    normalized = (role or "").strip().lower()
    return ROLE_ALIASES.get(normalized, normalized)


def get_user_id_prefix(role):
    normalized_role = normalize_role(role)
    prefix = ROLE_PREFIX_BY_ROLE.get(normalized_role)
    if not prefix:
        raise ValueError(f"Unsupported role for user id generation: {role}")
    return prefix


def _get_signup_day_pass_source_permit_id(cursor):
    cursor.execute("""
        SELECT permit_id
        FROM permits
        WHERE permit_id = %s
        LIMIT 1
    """, (SIGNUP_DAY_PASS_SOURCE_PERMIT_ID,))
    row = cursor.fetchone()
    if row:
        return row[0]

    cursor.execute("""
        SELECT permit_id
        FROM permits
        WHERE LOWER(permit_name) = %s
        ORDER BY permit_id
        LIMIT 1
    """, (SIGNUP_DAY_PASS_SOURCE_PERMIT_NAME.lower(),))
    row = cursor.fetchone()
    if row:
        return row[0]

    return None


def _ensure_signup_day_pass_exists_with_cursor(cursor):
    cursor.execute("""
        INSERT INTO permits
            (
                permit_id,
                permit_name,
                description,
                duration_days,
                display_color_hex,
                is_active,
                sort_order
            )
        VALUES
            (%s, %s, %s, %s, %s, TRUE, %s)
        ON DUPLICATE KEY UPDATE
            permit_name = VALUES(permit_name),
            description = VALUES(description),
            duration_days = VALUES(duration_days),
            display_color_hex = VALUES(display_color_hex),
            is_active = VALUES(is_active),
            sort_order = VALUES(sort_order)
    """, (
        SIGNUP_DAY_PASS_PERMIT_ID,
        SIGNUP_DAY_PASS_PERMIT_NAME,
        SIGNUP_DAY_PASS_DESCRIPTION,
        1,
        SIGNUP_DAY_PASS_COLOR,
        SIGNUP_DAY_PASS_SORT_ORDER,
    ))

    source_permit_id = _get_signup_day_pass_source_permit_id(cursor)
    if not source_permit_id:
        raise RuntimeError(
            "Unable to create the signup day pass because no visitor permit exists to clone parking rules from."
        )

    cursor.execute("""
        DELETE FROM parking_rules
        WHERE permit_id = %s
    """, (SIGNUP_DAY_PASS_PERMIT_ID,))

    cursor.execute("""
        INSERT INTO parking_rules
            (lot_id, permit_id, day_of_week, start_time, end_time, is_allowed, rule_source)
        SELECT
            DISTINCT pr.lot_id,
            %s,
            'Mon,Tue,Wed,Thu,Fri,Sat,Sun',
            '00:00:00',
            '23:59:59',
            TRUE,
            'system'
        FROM parking_rules pr
        WHERE pr.permit_id = %s
          AND pr.is_allowed = TRUE
    """, (SIGNUP_DAY_PASS_PERMIT_ID, source_permit_id))

    cursor.execute("""
        SELECT COUNT(*)
        FROM parking_rules
        WHERE permit_id = %s
    """, (SIGNUP_DAY_PASS_PERMIT_ID,))
    if int(cursor.fetchone()[0] or 0) == 0:
        raise RuntimeError(
            "Unable to create the signup day pass because visitor parking rules were not available to clone."
        )


def _assign_signup_day_pass_with_cursor(cursor, user_id):
    _ensure_signup_day_pass_exists_with_cursor(cursor)

    cursor.execute("""
        DELETE FROM user_permits
        WHERE user_id = %s
    """, (user_id,))

    cursor.execute("""
        INSERT INTO user_permits
            (user_id, permit_id, issued_date, expiration_date, status, assigned_by, note)
        VALUES
            (%s, %s, NOW(), DATE_ADD(NOW(), INTERVAL %s HOUR), 'active', %s, %s)
    """, (
        user_id,
        SIGNUP_DAY_PASS_PERMIT_ID,
        SIGNUP_DAY_PASS_HOURS,
        "system",
        "Automatic 24-hour signup day pass until admin assigns a permit.",
    ))


def assign_signup_day_pass(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        _assign_signup_day_pass_with_cursor(cursor, user_id)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error assigning signup day pass:", e)
        raise
    finally:
        cursor.close()
        conn.close()


def create_user(user_id, first_name, last_name, email, password, role, assign_signup_pass=False):
    conn = get_connection()
    cursor = conn.cursor()
    salt = bcrypt.gensalt()

    first_name = (first_name or "").strip()
    last_name = (last_name or "").strip()
    email = (email or "").strip().lower()
    role = normalize_role(role)

    if role not in ROLE_PREFIX_BY_ROLE:
        raise ValueError(f"Unsupported role: {role}")

    tmp = password.encode("utf-8") # Hashing password
    passwd = bcrypt.hashpw(tmp, salt).decode("utf-8")

    try:
        cursor.execute("SELECT 1 FROM users WHERE email = %s", (email,))
        rows = cursor.fetchall()

        if len(rows) > 0:
            return False
        else:
            cursor.execute("""
                INSERT INTO users (user_id, first_name, last_name, email, password_hash, role)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, first_name, last_name, email, passwd, role))

            if assign_signup_pass:
                _assign_signup_day_pass_with_cursor(cursor, user_id)

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
    email = (email or "").strip().lower()

    try:
        cursor.execute("""
            SELECT
                u.*,
                up.permit_id AS active_permit_id,
                up.expiration_date AS active_permit_expiration,
                p.permit_name AS user_permit_name
            FROM users u
            LEFT JOIN user_permits up
                ON u.user_id = up.user_id
               AND up.status = 'active'
               AND up.expiration_date >= NOW()
            LEFT JOIN permits p ON up.permit_id = p.permit_id
            WHERE u.email = %s
            LIMIT 1
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

    try:
        prefix = get_user_id_prefix(permit)
        cursor.execute("""
            SELECT COALESCE(MAX(CAST(SUBSTRING(user_id, 4) AS UNSIGNED)), 0)
            FROM users
            WHERE user_id LIKE %s
        """, (f"{prefix}%",))
        next_sequence = int(cursor.fetchone()[0] or 0) + 1
        return f"{prefix}{next_sequence:03d}"

    except Exception as e:
        print("Error creating User ID: ", e)
        raise
    finally:
        cursor.close()
        conn.close()
