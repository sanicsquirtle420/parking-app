"""
api/routes_user.py
==================
Endpoints for logged-in students, faculty, and visitors.
All routes require a valid JWT token in Authorization header.

- GET /api/me                        → user profile + permits
- GET /api/me/check-parking/{lot_id} → YES/NO rule engine for one lot
- GET /api/me/available-lots         → all lots where I can park now
- GET /api/lots/{lot_id}/rules       → full schedule for any lot
"""

from fastapi import APIRouter, Depends, HTTPException

from db import get_connection
from auth import get_current_user

router = APIRouter()


# ============================================================
# USER PROFILE
# ============================================================


@router.get("/api/me")
def get_my_profile(user: dict = Depends(get_current_user)):
    """Return the logged-in user's profile + all their permits with status."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT u.user_id, u.first_name, u.last_name, u.email, u.role,
               p.permit_id, p.permit_name,
               up.issued_date, up.expiration_date,
               CASE
                   WHEN up.expiration_date < CURDATE() THEN 'EXPIRED'
                   WHEN up.expiration_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)
                        THEN 'EXPIRING_SOON'
                   ELSE 'ACTIVE'
               END AS permit_status
        FROM users u
        LEFT JOIN user_permits up ON u.user_id = up.user_id
        LEFT JOIN permits p       ON up.permit_id = p.permit_id
        WHERE u.user_id = %s
        """,
        (user["user_id"],),
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="User not found")

    first = rows[0]
    permits = [
        {
            "permit_id": r["permit_id"],
            "permit_name": r["permit_name"],
            "issued_date": str(r["issued_date"]) if r["issued_date"] else None,
            "expiration_date": str(r["expiration_date"]) if r["expiration_date"] else None,
            "status": r["permit_status"],
        }
        for r in rows
        if r["permit_id"] is not None
    ]

    return {
        "user_id": first["user_id"],
        "first_name": first["first_name"],
        "last_name": first["last_name"],
        "email": first["email"],
        "role": first["role"],
        "permits": permits,
        "has_active_permit": any(p["status"] == "ACTIVE" for p in permits),
    }


# ============================================================
# THE RULE ENGINE — YES/NO decision
# ============================================================


@router.get("/api/me/check-parking/{lot_id}")
def check_parking(lot_id: int, user: dict = Depends(get_current_user)):
    """
    Can this user park at this lot RIGHT NOW?
    Checks permit + day + time + expiration.
    Returns YES/NO + occupancy info.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT u.first_name, u.last_name,
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
        JOIN user_permits up  ON u.user_id = up.user_id
        JOIN permits p        ON up.permit_id = p.permit_id
        JOIN parking_lots pl  ON pl.lot_id = %s
        LEFT JOIN parking_rules pr
               ON pr.permit_id = up.permit_id
              AND pr.lot_id    = pl.lot_id
              AND FIND_IN_SET(
                    ELT(DAYOFWEEK(CURDATE()),
                        'Sun','Mon','Tue','Wed','Thu','Fri','Sat'),
                    pr.day_of_week
                  ) > 0
              AND CURTIME() BETWEEN pr.start_time AND pr.end_time
        WHERE u.user_id = %s
        ORDER BY can_park DESC
        LIMIT 1
        """,
        (lot_id, user["user_id"]),
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result is None:
        raise HTTPException(status_code=404, detail="User or lot not found")

    # Convert time/date objects to strings for JSON
    for field in ("start_time", "end_time"):
        if result.get(field) is not None:
            result[field] = str(result[field])

    return result


# ============================================================
# ALL LOTS AVAILABLE RIGHT NOW
# ============================================================


@router.get("/api/me/available-lots")
def get_my_available_lots(user: dict = Depends(get_current_user)):
    """Every lot where this user can park this moment, sorted by least full."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT pl.lot_id, pl.lot_name, pl.latitude, pl.longitude,
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
        JOIN user_permits up  ON u.user_id = up.user_id
        JOIN permits p        ON up.permit_id = p.permit_id
        JOIN parking_rules pr ON pr.permit_id = up.permit_id
        JOIN parking_lots pl  ON pr.lot_id = pl.lot_id
        WHERE u.user_id = %s
          AND up.expiration_date >= CURDATE()
          AND pr.is_allowed = TRUE
          AND FIND_IN_SET(
                ELT(DAYOFWEEK(CURDATE()),
                    'Sun','Mon','Tue','Wed','Thu','Fri','Sat'),
                pr.day_of_week
              ) > 0
          AND CURTIME() BETWEEN pr.start_time AND pr.end_time
        ORDER BY occupancy_pct ASC
        """,
        (user["user_id"],),
    )
    lots = cursor.fetchall()
    # stringify time fields for JSON
    for row in lots:
        for f in ("start_time", "end_time"):
            if row.get(f) is not None:
                row[f] = str(row[f])
    cursor.close()
    conn.close()
    return {"lots": lots}


# ============================================================
# LOT SCHEDULE (public rule schedule for any lot)
# ============================================================


@router.get("/api/lots/{lot_id}/rules")
def get_lot_rules(lot_id: int, user: dict = Depends(get_current_user)):
    """Full rule table for a specific lot so users can plan ahead."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT p.permit_name, pr.day_of_week,
               pr.start_time, pr.end_time, pr.is_allowed
        FROM parking_rules pr
        JOIN permits p ON pr.permit_id = p.permit_id
        WHERE pr.lot_id = %s
        ORDER BY p.permit_name, pr.day_of_week
        """,
        (lot_id,),
    )
    rules = cursor.fetchall()
    for r in rules:
        r["start_time"] = str(r["start_time"])
        r["end_time"] = str(r["end_time"])
    cursor.close()
    conn.close()
    return {"lot_id": lot_id, "rules": rules}
