"""
admin_permit_operations.py
==========================
Page 3 — Permits & Users: All CRUD for permit types and user-permit assignments.

This file maps directly to crud_operations.sql Page 3 section.

SITEMAP CONTEXT:
  Admin navigates here from the sidebar/nav menu.
  Page 3 has two sections:
    1. Permits section — table of all permit types (add/edit/delete)
    2. Users section — searchable table of user-permit assignments
       (assign/renew individual/bulk renew/revoke)

USAGE:
  from admin_permit_operations import create_permit, assign_permit, revoke_permit
  result = create_permit("EV", "EV Priority", "Priority at EV charger spots")
"""

from db_connection import get_connection


# =============================================================
# PERMIT TYPE CRUD OPERATIONS
# =============================================================


def get_all_permits():
    """
    PAGE 3 — READ: Load all permit types for the permits table.
    TRIGGER: Admin navigates to Page 3, permits section loads.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT permit_id, permit_name, description
        FROM permits
        ORDER BY permit_name
    """)
    permits = cursor.fetchall()
    cursor.close()
    conn.close()
    return permits


def create_permit(permit_id, permit_name, description):
    """
    PAGE 3 — CREATE: Add a new permit type.
    TRIGGER: Admin clicks "Add Permit", fills in ID/name/description, hits Save.
    NOTE: permit_id is NOT auto-increment — admin chooses it (e.g. 'EV').
          This is because permit_ids are short codes used throughout the system.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # VALIDATION: Check permit_id doesn't already exist
    cursor.execute(
        "SELECT COUNT(*) AS id_exists FROM permits WHERE permit_id = %s",
        (permit_id,)
    )
    if cursor.fetchone()["id_exists"] > 0:
        cursor.close()
        conn.close()
        return {"success": False, "error": "This permit ID already exists"}

    cursor.execute(
        "INSERT INTO permits (permit_id, permit_name, description) VALUES (%s, %s, %s)",
        (permit_id, permit_name, description)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"success": True, "permit_id": permit_id}


def update_permit(permit_id, permit_name, description):
    """
    PAGE 3 — UPDATE: Edit a permit type's name or description.
    TRIGGER: Admin clicks "Edit" on a permit row, changes fields, hits Save.
    NOTE: permit_id itself should NOT be editable — it's a primary key
          referenced by parking_rules and user_permits.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE permits SET permit_name = %s, description = %s WHERE permit_id = %s",
        (permit_name, description, permit_id)
    )
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()
    return {"success": affected > 0}


def delete_permit(permit_id):
    """
    PAGE 3 — DELETE: Remove a permit type.
    TRIGGER: Admin clicks "Delete" on a permit row, confirms in dialog.
    IMPORTANT: Can only delete if no rules or user_permits reference it.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # VALIDATION: Check for dependencies before allowing delete
    cursor.execute("""
        SELECT
            (SELECT COUNT(*) FROM parking_rules WHERE permit_id = %s) AS rules_using,
            (SELECT COUNT(*) FROM user_permits WHERE permit_id = %s) AS users_using
    """, (permit_id, permit_id))
    deps = cursor.fetchone()

    if deps["rules_using"] > 0 or deps["users_using"] > 0:
        cursor.close()
        conn.close()
        return {
            "success": False,
            "error": f"Cannot delete — {deps['rules_using']} rules and "
                     f"{deps['users_using']} users still reference this permit. "
                     f"Remove those first."
        }

    cursor.execute("DELETE FROM permits WHERE permit_id = %s", (permit_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"success": True}


# =============================================================
# USER-PERMIT ASSIGNMENT OPERATIONS
# =============================================================


def get_all_users_with_permits():
    """
    PAGE 3 — READ: Load searchable table of all users and their permits.
    TRIGGER: Admin navigates to Page 3, users section loads.
    RETURNS: List of users with permit info and expiration status.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            u.user_id, u.first_name, u.last_name, u.email, u.role,
            p.permit_id, p.permit_name,
            up.issued_date, up.expiration_date,
            CASE
                WHEN up.expiration_date < CURDATE() THEN 'EXPIRED'
                WHEN up.expiration_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY) THEN 'EXPIRING SOON'
                ELSE 'ACTIVE'
            END AS permit_status
        FROM users u
        LEFT JOIN user_permits up ON u.user_id = up.user_id
        LEFT JOIN permits p ON up.permit_id = p.permit_id
        ORDER BY u.last_name, u.first_name
    """)
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users


def search_user(search_term):
    """
    PAGE 3 — READ: Search for a user by ID, name, or email.
    TRIGGER: Admin types in the search box in the users section.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    wildcard = f"%{search_term}%"
    cursor.execute("""
        SELECT
            u.user_id, u.first_name, u.last_name, u.email, u.role,
            p.permit_id, p.permit_name,
            up.issued_date, up.expiration_date,
            CASE
                WHEN up.expiration_date < CURDATE() THEN 'EXPIRED'
                WHEN up.expiration_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY) THEN 'EXPIRING SOON'
                ELSE 'ACTIVE'
            END AS permit_status
        FROM users u
        LEFT JOIN user_permits up ON u.user_id = up.user_id
        LEFT JOIN permits p ON up.permit_id = p.permit_id
        WHERE u.user_id LIKE %s
           OR u.first_name LIKE %s
           OR u.last_name LIKE %s
           OR u.email LIKE %s
        ORDER BY u.last_name, u.first_name
    """, (wildcard, wildcard, wildcard, wildcard))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


def get_user_dropdown():
    """
    HELPER: Populate the user dropdown for "Assign Permit" form.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT user_id, first_name, last_name, role FROM users ORDER BY last_name"
    )
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users


def assign_permit(user_id, permit_id, issued_date, expiration_date):
    """
    PAGE 3 — CREATE: Assign a permit to a user.
    TRIGGER: Admin clicks "Assign New Permit", picks user + permit from
             dropdowns, sets dates, hits Save.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # VALIDATION: Check user doesn't already have this permit
    cursor.execute(
        "SELECT COUNT(*) AS already_assigned FROM user_permits "
        "WHERE user_id = %s AND permit_id = %s",
        (user_id, permit_id)
    )
    if cursor.fetchone()["already_assigned"] > 0:
        cursor.close()
        conn.close()
        return {"success": False, "error": "This user already has this permit type"}

    cursor.execute("""
        INSERT INTO user_permits (user_id, permit_id, issued_date, expiration_date)
        VALUES (%s, %s, %s, %s)
    """, (user_id, permit_id, issued_date, expiration_date))
    conn.commit()
    cursor.close()
    conn.close()
    return {"success": True}


def renew_permit_individual(user_id, permit_id, issued_date, expiration_date):
    """
    PAGE 3 — UPDATE: Renew a single user's specific permit.
    TRIGGER: Admin searches for a user, clicks "Renew" on one of their
             permit rows. A form shows current dates, admin sets new dates, hits Save.
    USE CASE: One student enrolled in summer classes and needs their
              permit extended. Or admin corrects a wrong date.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # PRE-FILL: Get current dates to display in the form
    cursor.execute("""
        SELECT u.first_name, u.last_name, p.permit_name,
               up.issued_date, up.expiration_date
        FROM user_permits up
        JOIN users u ON up.user_id = u.user_id
        JOIN permits p ON up.permit_id = p.permit_id
        WHERE up.user_id = %s AND up.permit_id = %s
    """, (user_id, permit_id))
    current = cursor.fetchone()

    if current is None:
        cursor.close()
        conn.close()
        return {"success": False, "error": "Permit assignment not found"}

    # UPDATE the dates
    cursor.execute("""
        UPDATE user_permits
        SET issued_date = %s, expiration_date = %s
        WHERE user_id = %s AND permit_id = %s
    """, (issued_date, expiration_date, user_id, permit_id))
    conn.commit()
    cursor.close()
    conn.close()

    return {
        "success": True,
        "user": f"{current['first_name']} {current['last_name']}",
        "permit": current["permit_name"],
        "old_expiration": str(current["expiration_date"]),
        "new_expiration": expiration_date
    }


def renew_permit_bulk(permit_id, new_expiration_date):
    """
    PAGE 3 — UPDATE: Bulk extend all permits of a certain type.
    TRIGGER: Admin clicks "Bulk Extend", picks a permit type from dropdown,
             sets new expiration date, hits "Apply to All".
    USE CASE: End of semester, all Student Commuter (S) permits need
              extending to next semester in one click.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # PRE-UPDATE: Show admin how many users will be affected
    cursor.execute(
        "SELECT COUNT(*) AS users_affected FROM user_permits WHERE permit_id = %s",
        (permit_id,)
    )
    count = cursor.fetchone()["users_affected"]

    # BULK UPDATE
    cursor.execute(
        "UPDATE user_permits SET expiration_date = %s WHERE permit_id = %s",
        (new_expiration_date, permit_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return {"success": True, "users_affected": count, "new_expiration": new_expiration_date}


def revoke_permit(user_id, permit_id):
    """
    PAGE 3 — DELETE: Revoke a user's permit.
    TRIGGER: Admin searches for a user, clicks "Revoke" on one of their permits.
             Confirmation dialog: "Revoke [permit_name] from [name]?"
    NOTE: This only removes the permit assignment, NOT the user account.
          Without a permit, the rule engine returns NO for everything.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # PRE-DELETE: Get info for confirmation dialog
    cursor.execute("""
        SELECT u.first_name, u.last_name, p.permit_name, up.expiration_date
        FROM user_permits up
        JOIN users u ON up.user_id = u.user_id
        JOIN permits p ON up.permit_id = p.permit_id
        WHERE up.user_id = %s AND up.permit_id = %s
    """, (user_id, permit_id))
    info = cursor.fetchone()

    if info is None:
        cursor.close()
        conn.close()
        return {"success": False, "error": "Permit assignment not found"}

    cursor.execute(
        "DELETE FROM user_permits WHERE user_id = %s AND permit_id = %s",
        (user_id, permit_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return {
        "success": True,
        "revoked": f"{info['permit_name']} from {info['first_name']} {info['last_name']}"
    }
