"""
user_operations.py
==================
Student / Faculty / Visitor facing operations.

This file maps directly to user_engine.sql.
These functions power the map view, rule engine, and user profile.

SITEMAP CONTEXT:
  After login, students/faculty land on the Map View.
  They can:
    - See all 12 lots on the map (get_all_lots)
    - Tap a lot for YES/NO (check_parking)
    - Filter to see only their available lots (get_available_lots)
    - View their profile and permits (get_user_profile)
  Visitors can browse without login using visitor mode (browse_by_permit)

LOGIN FLOW:
  Same login page for everyone. After login:
    role = 'admin'   → redirect to Admin Dashboard (Page 1)
    role = 'student'  → redirect to Map View
    role = 'faculty'  → redirect to Map View
    role = 'visitor'  → redirect to Map View

USAGE:
  from user_operations import login, check_parking, get_available_lots
  user = login("jdoe@go.olemiss.edu", "hashed_pw_001")
  result = check_parking("stu001", 1)
"""

from db_connection import get_connection


# =============================================================
# AUTHENTICATION
# =============================================================


def login(email, password_hash):
    """
    LOGIN: Validate user credentials.
    TRIGGER: User enters email + password on login page, hits Sign In.
    NOTE: Password hashing (bcrypt) must happen BEFORE calling this.
          The auth layer hashes the password, then passes the hash here.
    RETURNS:
      Success → {"success": True, "user_id": ..., "role": ..., ...}
      Failure → {"success": False, "error": "Invalid email or password"}
    FRONTEND LOGIC:
      role = 'admin'   → redirect to /admin/dashboard
      role = 'student'  → redirect to /map
      role = 'faculty'  → redirect to /map
      role = 'visitor'  → redirect to /map
      Then immediately call get_user_profile() to load permits.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT user_id, first_name, last_name, role FROM users "
        "WHERE email = %s AND password_hash = %s",
        (email, password_hash)
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        return {"success": True, **user}
    else:
        return {"success": False, "error": "Invalid email or password"}


def check_active_permits(user_id):
    """
    POST-LOGIN CHECK: Does this user have any non-expired permits?
    TRIGGER: Immediately after login, before showing the map.
    RETURNS: Count of active permits.
    FRONTEND LOGIC:
      If count = 0 → show message:
        "You don't have an active parking permit.
         Contact Parking Services to get one."
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT COUNT(*) AS active_permits FROM user_permits "
        "WHERE user_id = %s AND expiration_date >= CURDATE()",
        (user_id,)
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result["active_permits"]


# =============================================================
# USER PROFILE
# =============================================================


def get_user_profile(user_id):
    """
    USER PROFILE: Load user info + all their permits with status.
    TRIGGER: After login, or when user navigates to profile page.
    NOTE: A user can have MULTIPLE permits (e.g. fac003 has FC + ADA).
    FRONTEND LOGIC:
      If permit_status = 'EXPIRED' for ALL permits:
        Show warning: "Your permit has expired. Contact Parking Services."
      If permit_status = 'EXPIRING SOON':
        Show banner: "Your [permit_name] expires on [expiration_date]"
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
        JOIN user_permits up ON u.user_id = up.user_id
        JOIN permits p ON up.permit_id = p.permit_id
        WHERE u.user_id = %s
    """, (user_id,))
    permits = cursor.fetchall()
    cursor.close()
    conn.close()

    if not permits:
        return {"user_id": user_id, "permits": [], "has_active": False}

    return {
        "user_id": permits[0]["user_id"],
        "first_name": permits[0]["first_name"],
        "last_name": permits[0]["last_name"],
        "email": permits[0]["email"],
        "role": permits[0]["role"],
        "permits": [
            {
                "permit_id": p["permit_id"],
                "permit_name": p["permit_name"],
                "issued_date": str(p["issued_date"]),
                "expiration_date": str(p["expiration_date"]),
                "status": p["permit_status"]
            }
            for p in permits
        ],
        "has_active": any(p["permit_status"] == "ACTIVE" for p in permits)
    }


# =============================================================
# MAP DATA
# =============================================================


def get_all_lots():
    """
    MAP VIEW: Load all 12 lots with coordinates and status for map markers.
    TRIGGER: Map page loads (for any user type).
    FRONTEND LOGIC: Use latitude + longitude to place markers.
      Color code by status_level:
        GREEN  = LOW (under 50%)
        YELLOW = MODERATE (50-69%)
        ORANGE = HIGH (70-89%)
        RED    = CRITICAL (90%+)
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            lot_id, lot_name, latitude, longitude,
            capacity, current_occupancy, ev_charger_count,
            capacity - current_occupancy AS available_spaces,
            ROUND((current_occupancy / capacity) * 100, 1) AS occupancy_pct,
            CASE
                WHEN (current_occupancy / capacity) * 100 >= 90 THEN 'CRITICAL'
                WHEN (current_occupancy / capacity) * 100 >= 70 THEN 'HIGH'
                WHEN (current_occupancy / capacity) * 100 >= 50 THEN 'MODERATE'
                ELSE 'LOW'
            END AS status_level
        FROM parking_lots
        ORDER BY lot_name
    """)
    lots = cursor.fetchall()
    cursor.close()
    conn.close()
    return lots


# =============================================================
# RULE ENGINE — THE CORE LOGIC
# =============================================================


def check_parking(user_id, lot_id):
    """
    THE YES/NO DECISION: Can this user park at this lot right now?
    TRIGGER: User taps a specific lot marker on the map.

    HOW IT WORKS:
      1. Looks up user's permit(s) from user_permits
      2. Checks parking_rules for a matching rule at this lot
         for this permit on today's day of week
      3. Checks if current time falls within the rule's window
      4. Checks if the permit hasn't expired
      5. Returns YES or NO + occupancy info

    FRONTEND DISPLAY:
      YES → Green checkmark + "You can park here"
        Then check occupancy_pct:
          >= 90%: Warning — "Lot is nearly full ({available_spaces} spots left)"
          >= 70%: Notice — "Lot is filling up ({available_spaces} spots left)"
          < 70%:  "plenty of space ({available_spaces} spots available)"
        If ev_charger_count > 0:
          Show: "{ev_charger_count} EV chargers at this lot"
      NO → Red X + "Your permit is not valid here right now"
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            u.first_name, u.last_name,
            p.permit_name,
            pl.lot_name, pl.capacity, pl.current_occupancy,
            pl.capacity - pl.current_occupancy AS available_spaces,
            ROUND((pl.current_occupancy / pl.capacity) * 100, 1) AS occupancy_pct,
            pl.ev_charger_count,
            pr.day_of_week, pr.start_time, pr.end_time,
            CASE
                WHEN pr.rule_id IS NOT NULL
                 AND pr.is_allowed = TRUE
                 AND up.expiration_date >= CURDATE()
                THEN 'YES'
                ELSE 'NO'
            END AS can_park
        FROM users u
        JOIN user_permits up ON u.user_id = up.user_id
        JOIN permits p ON up.permit_id = p.permit_id
        JOIN parking_lots pl ON pl.lot_id = %s
        LEFT JOIN parking_rules pr
            ON pr.permit_id = up.permit_id
           AND pr.lot_id = pl.lot_id
           AND FIND_IN_SET(
                 ELT(DAYOFWEEK(CURDATE()), 'Sun','Mon','Tue','Wed','Thu','Fri','Sat'),
                 pr.day_of_week
               ) > 0
           AND CURTIME() BETWEEN pr.start_time AND pr.end_time
        WHERE u.user_id = %s
        ORDER BY can_park DESC
        LIMIT 1
    """, (lot_id, user_id))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result is None:
        return {"can_park": "NO", "error": "User or lot not found"}

    return result


def get_available_lots(user_id):
    """
    FILTERED MAP: Show ALL lots where this user can park RIGHT NOW.
    TRIGGER: User clicks "Show All My Lots" or a filter button.
    FRONTEND: Highlight these lots in green on the map.
              Gray out all other lots.
              Sort by occupancy (least full first).
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            pl.lot_id, pl.lot_name, pl.latitude, pl.longitude,
            p.permit_name,
            pr.day_of_week, pr.start_time, pr.end_time,
            pl.current_occupancy, pl.capacity,
            pl.capacity - pl.current_occupancy AS available_spaces,
            ROUND((pl.current_occupancy / pl.capacity) * 100, 1) AS occupancy_pct,
            pl.ev_charger_count,
            CASE
                WHEN (pl.current_occupancy / pl.capacity) * 100 >= 90 THEN 'CRITICAL'
                WHEN (pl.current_occupancy / pl.capacity) * 100 >= 70 THEN 'HIGH'
                WHEN (pl.current_occupancy / pl.capacity) * 100 >= 50 THEN 'MODERATE'
                ELSE 'LOW'
            END AS status_level
        FROM users u
        JOIN user_permits up ON u.user_id = up.user_id
        JOIN permits p ON up.permit_id = p.permit_id
        JOIN parking_rules pr ON pr.permit_id = up.permit_id
        JOIN parking_lots pl ON pr.lot_id = pl.lot_id
        WHERE u.user_id = %s
          AND up.expiration_date >= CURDATE()
          AND pr.is_allowed = TRUE
          AND FIND_IN_SET(
                ELT(DAYOFWEEK(CURDATE()), 'Sun','Mon','Tue','Wed','Thu','Fri','Sat'),
                pr.day_of_week
              ) > 0
          AND CURTIME() BETWEEN pr.start_time AND pr.end_time
        ORDER BY occupancy_pct ASC
    """, (user_id,))
    lots = cursor.fetchall()
    cursor.close()
    conn.close()
    return lots


# =============================================================
# VISITOR MODE (NO LOGIN REQUIRED)
# =============================================================


def browse_by_permit(permit_id):
    """
    VISITOR MODE: Check which lots accept a permit type right now.
    TRIGGER: Visitor (or anyone browsing without login) selects a
             permit type from a dropdown on the map page.
    HOW THIS DIFFERS FROM get_available_lots:
      get_available_lots looks up the user's permits from user_permits.
      This takes a raw permit_id directly — no account needed.
    FRONTEND: Show dropdown on map page: "Browse as: [Visitor ▼]"
              When selected, run this and highlight matching lots.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            pl.lot_id, pl.lot_name, pl.latitude, pl.longitude,
            p.permit_name,
            pr.day_of_week, pr.start_time, pr.end_time,
            pl.current_occupancy, pl.capacity,
            pl.capacity - pl.current_occupancy AS available_spaces,
            ROUND((pl.current_occupancy / pl.capacity) * 100, 1) AS occupancy_pct,
            pl.ev_charger_count,
            CASE
                WHEN (pl.current_occupancy / pl.capacity) * 100 >= 90 THEN 'CRITICAL'
                WHEN (pl.current_occupancy / pl.capacity) * 100 >= 70 THEN 'HIGH'
                WHEN (pl.current_occupancy / pl.capacity) * 100 >= 50 THEN 'MODERATE'
                ELSE 'LOW'
            END AS status_level
        FROM parking_rules pr
        JOIN parking_lots pl ON pr.lot_id = pl.lot_id
        JOIN permits p ON pr.permit_id = p.permit_id
        WHERE pr.permit_id = %s
          AND pr.is_allowed = TRUE
          AND FIND_IN_SET(
                ELT(DAYOFWEEK(CURDATE()), 'Sun','Mon','Tue','Wed','Thu','Fri','Sat'),
                pr.day_of_week
              ) > 0
          AND CURTIME() BETWEEN pr.start_time AND pr.end_time
        ORDER BY occupancy_pct ASC
    """, (permit_id,))
    lots = cursor.fetchall()
    cursor.close()
    conn.close()
    return lots


def get_lot_rules(lot_id):
    """
    LOT SCHEDULE: Full rule table for a specific lot.
    TRIGGER: User taps a lot and wants to see all time windows,
             not just whether they can park NOW.
    USE CASE: "I can't park here now, but I can after 5pm"
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            p.permit_name, pr.day_of_week,
            pr.start_time, pr.end_time, pr.is_allowed
        FROM parking_rules pr
        JOIN permits p ON pr.permit_id = p.permit_id
        WHERE pr.lot_id = %s
        ORDER BY p.permit_name, pr.day_of_week
    """, (lot_id,))
    rules = cursor.fetchall()
    cursor.close()
    conn.close()
    return rules
