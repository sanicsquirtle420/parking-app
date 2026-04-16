from datetime import datetime, timedelta

from database.db import get_connection


DEFAULT_USER_LIMIT = 100


def _result(ok, message):
    return {"ok": ok, "message": message}


def get_admin_permits_snapshot(search_text=None, limit=DEFAULT_USER_LIMIT):
    conn = get_connection()
    permit_cursor = conn.cursor(dictionary=True)
    user_cursor = conn.cursor(dictionary=True)
    assignment_cursor = conn.cursor(dictionary=True)

    try:
        permit_cursor.execute("""
            SELECT
                p.permit_id,
                p.permit_name,
                p.description,
                (
                    SELECT COUNT(*)
                    FROM user_permits up
                    WHERE up.permit_id = p.permit_id
                ) AS usage_count
            FROM permits p
            ORDER BY permit_name
        """)
        permits = permit_cursor.fetchall()
        for permit in permits:
            permit["description"] = f"{get_permit_duration_days(permit.get('description'))} days"
            permit["usage_count"] = permit.get("usage_count", 0) or 0
        permit_name_by_id = {
            permit["permit_id"]: permit["permit_name"]
            for permit in permits
        }

        params = []
        query = """
            SELECT
                u.user_id,
                u.first_name,
                u.last_name,
                u.email,
                u.role
            FROM users u
        """

        if search_text:
            like_term = f"%{search_text.strip()}%"
            query += """
                WHERE (
                    u.user_id LIKE %s OR
                    u.first_name LIKE %s OR
                    u.last_name LIKE %s OR
                    COALESCE(u.email, '') LIKE %s
                )
            """
            params.extend([like_term, like_term, like_term, like_term])

        query += """
            ORDER BY u.last_name, u.first_name, u.user_id
        """

        if limit:
            query += " LIMIT %s"
            params.append(int(limit))

        user_cursor.execute(query, params)
        users = user_cursor.fetchall()

        if not users:
            return {"permits": permits, "users": []}

        user_ids = [user["user_id"] for user in users]
        placeholders = ", ".join(["%s"] * len(user_ids))
        assignment_cursor.execute(f"""
            SELECT
                user_id,
                permit_id,
                issued_date,
                expiration_date
            FROM user_permits
            WHERE user_id IN ({placeholders})
            ORDER BY user_id, permit_id
        """, user_ids)
        assignments = assignment_cursor.fetchall()

        assignments_by_user = {}
        for assignment in assignments:
            assignments_by_user.setdefault(assignment["user_id"], []).append(assignment)

        user_rows = []
        for user in users:
            user_assignments = assignments_by_user.get(user["user_id"])
            if not user_assignments:
                user_rows.append({
                    **user,
                    "permit_id": None,
                    "permit_name": None,
                    "issued_date": None,
                    "expiration_date": None,
                })
                continue

            for assignment in user_assignments:
                user_rows.append({
                    **user,
                    **assignment,
                    "permit_name": permit_name_by_id.get(assignment["permit_id"]),
                })

        return {"permits": permits, "users": user_rows}
    except Exception as e:
        print("Error fetching admin permits snapshot:", e)
        return None
    finally:
        permit_cursor.close()
        user_cursor.close()
        assignment_cursor.close()
        conn.close()


def create_permit_type(permit_id, permit_name, description=""):
    permit_id = (permit_id or "").strip().upper()[:5]
    permit_name = (permit_name or "").strip()
    description = (description or "").strip()

    if not permit_id or not permit_name:
        return _result(False, "Permit ID and permit name are required.")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT COUNT(*) FROM permits WHERE permit_id = %s",
            (permit_id,),
        )
        if cursor.fetchone()[0]:
            return _result(False, "That permit ID already exists.")

        cursor.execute("""
            INSERT INTO permits (permit_id, permit_name, description)
            VALUES (%s, %s, %s)
        """, (permit_id, permit_name, description))
        conn.commit()
        return _result(True, "Permit created.")
    except Exception as e:
        conn.rollback()
        print("Error creating permit:", e)
        return _result(False, "Unable to create permit.")
    finally:
        cursor.close()
        conn.close()


def assign_permit_to_user(user_id, permit_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT description FROM permits WHERE permit_id = %s",
            (permit_id,)
        )
        row = cursor.fetchone()
        desc = row[0] if row else ""

        try:
            days = int(str(desc).split()[0])
        except:
            days = 365

        issued = datetime.now()
        expiration = issued + timedelta(days=days)

        cursor.execute("""
            DELETE FROM user_permits WHERE user_id = %s
        """, (user_id,))

        cursor.execute("""
            INSERT INTO user_permits (user_id, permit_id, issued_date, expiration_date)
            VALUES (%s, %s, %s, %s)
        """, (user_id, permit_id, issued, expiration))

        conn.commit()
    except Exception as e:
        print("Assign error:", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def revoke_user_permit(user_id, permit_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            DELETE FROM user_permits
            WHERE user_id = %s AND permit_id = %s
        """, (user_id, permit_id))
        conn.commit()
        if cursor.rowcount == 0:
            return _result(False, "No permit assignment was found.")
        return _result(True, "Permit revoked.")
    except Exception as e:
        conn.rollback()
        print("Error revoking permit:", e)
        return _result(False, "Unable to revoke permit.")
    finally:
        cursor.close()
        conn.close()


def renew_user_permit(user_id, permit_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT description FROM permits WHERE permit_id = %s",
            (permit_id,)
        )
        row = cursor.fetchone()
        desc = row[0] if row else ""

        try:
            days = int(str(desc).split()[0])
        except:
            days = 365

        cursor.execute("""
            UPDATE user_permits
            SET expiration_date =
                CASE
                    WHEN expiration_date > NOW()
                        THEN expiration_date + INTERVAL %s DAY
                    ELSE NOW() + INTERVAL %s DAY
                END
            WHERE user_id = %s AND permit_id = %s
        """, (days, days, user_id, permit_id))

        conn.commit()
    except Exception as e:
        print("Renew error:", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def get_permit_usage_count(cursor, permit_id):
    cursor.execute(
        "SELECT COUNT(*) FROM user_permits WHERE permit_id = %s",
        (permit_id,)
    )
    return cursor.fetchone()[0]


def get_permit_duration_days(description):
    try:
        return int(str(description).split()[0])
    except:
        return 365


def delete_permit(permit_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        usage = get_permit_usage_count(cursor, permit_id)

        if usage > 0:
            return {"success": False, "message": "Permit is assigned to users."}

        cursor.execute(
            "DELETE FROM permits WHERE permit_id = %s",
            (permit_id,)
        )

        conn.commit()
        return {"success": True, "message": "Permit deleted."}

    except Exception as e:
        conn.rollback()
        print("Delete permit error:", e)
        return {"success": False, "message": "Delete failed."}

    finally:
        cursor.close()
        conn.close()
