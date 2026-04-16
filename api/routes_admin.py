"""
api/routes_admin.py
===================
Admin-only endpoints. All routes require a valid JWT with role='admin'.

PAGE 1 (Dashboard):
  GET  /api/admin/dashboard

PAGE 2 (Lot Detail):
  GET    /api/admin/lots/{lot_id}
  POST   /api/admin/lots
  PUT    /api/admin/lots/{lot_id}
  DELETE /api/admin/lots/{lot_id}
  POST   /api/admin/rules
  PUT    /api/admin/rules/{rule_id}
  PATCH  /api/admin/rules/{rule_id}/toggle
  DELETE /api/admin/rules/{rule_id}
  PUT    /api/admin/lots/{lot_id}/occupancy

PAGE 3 (Permits & Users):
  GET    /api/admin/permits
  POST   /api/admin/permits
  PUT    /api/admin/permits/{permit_id}
  DELETE /api/admin/permits/{permit_id}
  GET    /api/admin/users
  POST   /api/admin/user-permits
  PUT    /api/admin/user-permits/{user_id}/{permit_id}
  DELETE /api/admin/user-permits/{user_id}/{permit_id}
  PUT    /api/admin/bulk-renew/{permit_id}
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from db import get_connection
from auth import require_admin

router = APIRouter()


# ============================================================
# PYDANTIC SCHEMAS
# ============================================================


class LotCreate(BaseModel):
    lot_name: str
    latitude: float
    longitude: float
    capacity: int
    ev_charger_count: int = 0


class LotUpdate(BaseModel):
    lot_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    capacity: Optional[int] = None
    ev_charger_count: Optional[int] = None


class RuleCreate(BaseModel):
    lot_id: int
    permit_id: str
    day_of_week: str  # e.g. "Mon,Tue,Wed,Thu,Fri"
    start_time: str   # e.g. "07:00:00"
    end_time: str


class RuleUpdate(BaseModel):
    permit_id: str
    day_of_week: str
    start_time: str
    end_time: str


class OccupancyUpdate(BaseModel):
    occupancy: int
    ev_chargers_in_use: int = 0


class PermitCreate(BaseModel):
    permit_id: str
    permit_name: str
    description: str = ""


class PermitUpdate(BaseModel):
    permit_name: str
    description: str = ""


class UserPermitCreate(BaseModel):
    user_id: str
    permit_id: str
    issued_date: str
    expiration_date: str


class UserPermitRenew(BaseModel):
    issued_date: str
    expiration_date: str


class BulkRenew(BaseModel):
    new_expiration_date: str


# ============================================================
# PAGE 1: DASHBOARD
# ============================================================


@router.get("/api/admin/dashboard")
def dashboard(_: dict = Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT lot_id, lot_name, capacity, current_occupancy,
               ev_charger_count,
               ROUND((current_occupancy / capacity) * 100, 1) AS occupancy_pct,
               CASE
                   WHEN (current_occupancy / capacity) * 100 >= 90 THEN 'CRITICAL'
                   WHEN (current_occupancy / capacity) * 100 >= 70 THEN 'HIGH'
                   WHEN (current_occupancy / capacity) * 100 >= 50 THEN 'MODERATE'
                   ELSE 'LOW'
               END AS status_level,
               capacity - current_occupancy AS available_spaces
        FROM parking_lots
        ORDER BY (current_occupancy / capacity) DESC
        """
    )
    lots = cursor.fetchall()
    cursor.close()
    conn.close()

    total_cap = sum(l["capacity"] for l in lots) or 1
    total_occ = sum(l["current_occupancy"] for l in lots)
    critical = sum(1 for l in lots if l["status_level"] == "CRITICAL")

    return {
        "lots": lots,
        "summary": {
            "total_capacity": total_cap,
            "total_occupied": total_occ,
            "total_available": total_cap - total_occ,
            "overall_occupancy_pct": round(total_occ / total_cap * 100, 1),
            "critical_lots": critical,
            "total_lots": len(lots),
        },
    }


# ============================================================
# PAGE 2: LOT DETAIL + LOT CRUD
# ============================================================


@router.get("/api/admin/lots/{lot_id}")
def get_lot_detail(lot_id: int, _: dict = Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT lot_id, lot_name, latitude, longitude, capacity,
               current_occupancy, ev_charger_count,
               capacity - current_occupancy AS available_spaces,
               ROUND((current_occupancy / capacity) * 100, 1) AS occupancy_pct
        FROM parking_lots WHERE lot_id = %s
        """,
        (lot_id,),
    )
    lot = cursor.fetchone()
    if lot is None:
        cursor.close(); conn.close()
        raise HTTPException(status_code=404, detail="Lot not found")

    cursor.execute(
        """
        SELECT pr.rule_id, p.permit_id, p.permit_name,
               pr.day_of_week, pr.start_time, pr.end_time, pr.is_allowed
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

    cursor.execute(
        """
        SELECT log_id, recorded_at, occupancy, ev_chargers_in_use
        FROM parking_occupancy_log WHERE lot_id = %s
        ORDER BY recorded_at DESC LIMIT 20
        """,
        (lot_id,),
    )
    logs = cursor.fetchall()
    for l in logs:
        l["recorded_at"] = str(l["recorded_at"])

    cursor.close()
    conn.close()
    return {"lot": lot, "rules": rules, "occupancy_logs": logs}


@router.post("/api/admin/lots", status_code=201)
def create_lot(body: LotCreate, _: dict = Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS n FROM parking_lots WHERE lot_name = %s",
                   (body.lot_name,))
    if cursor.fetchone()["n"] > 0:
        cursor.close(); conn.close()
        raise HTTPException(status_code=409, detail="Lot name already exists")

    cursor.execute(
        """
        INSERT INTO parking_lots
            (lot_name, latitude, longitude, capacity, current_occupancy, ev_charger_count)
        VALUES (%s, %s, %s, %s, 0, %s)
        """,
        (body.lot_name, body.latitude, body.longitude, body.capacity, body.ev_charger_count),
    )
    new_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return {"lot_id": new_id, "message": "Lot created"}


@router.put("/api/admin/lots/{lot_id}")
def update_lot(lot_id: int, body: LotUpdate, _: dict = Depends(require_admin)):
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    set_clause = ", ".join(f"{col} = %s" for col in updates)
    values = list(updates.values()) + [lot_id]

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE parking_lots SET {set_clause} WHERE lot_id = %s", values)
    affected = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()

    if affected == 0:
        raise HTTPException(status_code=404, detail="Lot not found")
    return {"lot_id": lot_id, "updated_fields": list(updates.keys())}


@router.delete("/api/admin/lots/{lot_id}")
def decommission_lot(lot_id: int, _: dict = Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT (SELECT COUNT(*) FROM parking_rules WHERE lot_id = %s) AS r,
               (SELECT COUNT(*) FROM parking_occupancy_log WHERE lot_id = %s) AS l
    """, (lot_id, lot_id))
    counts = cursor.fetchone()

    cursor.execute("DELETE FROM parking_occupancy_log WHERE lot_id = %s", (lot_id,))
    cursor.execute("DELETE FROM parking_rules WHERE lot_id = %s", (lot_id,))
    cursor.execute("DELETE FROM parking_lots WHERE lot_id = %s", (lot_id,))
    affected = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()

    if affected == 0:
        raise HTTPException(status_code=404, detail="Lot not found")
    return {
        "message": "Lot decommissioned",
        "rules_deleted": counts["r"],
        "logs_deleted": counts["l"],
    }


# ============================================================
# PAGE 2: RULE CRUD
# ============================================================


@router.post("/api/admin/rules", status_code=201)
def add_rule(body: RuleCreate, _: dict = Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT COUNT(*) AS n FROM parking_rules
        WHERE lot_id = %s AND permit_id = %s AND day_of_week = %s
          AND start_time = %s AND end_time = %s
        """,
        (body.lot_id, body.permit_id, body.day_of_week, body.start_time, body.end_time),
    )
    if cursor.fetchone()["n"] > 0:
        cursor.close(); conn.close()
        raise HTTPException(status_code=409, detail="This exact rule already exists")

    cursor.execute(
        """
        INSERT INTO parking_rules (lot_id, permit_id, day_of_week, start_time, end_time)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (body.lot_id, body.permit_id, body.day_of_week, body.start_time, body.end_time),
    )
    rule_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return {"rule_id": rule_id, "message": "Rule added"}


@router.put("/api/admin/rules/{rule_id}")
def update_rule(rule_id: int, body: RuleUpdate, _: dict = Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE parking_rules
        SET permit_id = %s, day_of_week = %s, start_time = %s, end_time = %s
        WHERE rule_id = %s
        """,
        (body.permit_id, body.day_of_week, body.start_time, body.end_time, rule_id),
    )
    affected = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()

    if affected == 0:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"rule_id": rule_id, "message": "Rule updated"}


@router.patch("/api/admin/rules/{rule_id}/toggle")
def toggle_rule(rule_id: int, _: dict = Depends(require_admin)):
    """Flip is_allowed between TRUE/FALSE."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT is_allowed FROM parking_rules WHERE rule_id = %s", (rule_id,))
    row = cursor.fetchone()
    if row is None:
        cursor.close(); conn.close()
        raise HTTPException(status_code=404, detail="Rule not found")

    new_val = not row["is_allowed"]
    cursor.execute("UPDATE parking_rules SET is_allowed = %s WHERE rule_id = %s",
                   (new_val, rule_id))
    conn.commit()
    cursor.close()
    conn.close()
    return {"rule_id": rule_id, "is_allowed": bool(new_val)}


@router.delete("/api/admin/rules/{rule_id}")
def delete_rule(rule_id: int, _: dict = Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM parking_rules WHERE rule_id = %s", (rule_id,))
    affected = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()

    if affected == 0:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"message": "Rule deleted"}


# ============================================================
# PAGE 2: OCCUPANCY UPDATE + AUTO-LOG
# ============================================================


@router.put("/api/admin/lots/{lot_id}/occupancy")
def update_occupancy(lot_id: int, body: OccupancyUpdate,
                     _: dict = Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT capacity FROM parking_lots WHERE lot_id = %s", (lot_id,))
    lot = cursor.fetchone()
    if lot is None:
        cursor.close(); conn.close()
        raise HTTPException(status_code=404, detail="Lot not found")
    if body.occupancy > lot["capacity"]:
        cursor.close(); conn.close()
        raise HTTPException(status_code=400,
                            detail=f"Occupancy exceeds capacity ({lot['capacity']})")

    cursor.execute("UPDATE parking_lots SET current_occupancy = %s WHERE lot_id = %s",
                   (body.occupancy, lot_id))
    cursor.execute(
        """
        INSERT INTO parking_occupancy_log (lot_id, recorded_at, occupancy, ev_chargers_in_use)
        VALUES (%s, NOW(), %s, %s)
        """,
        (lot_id, body.occupancy, body.ev_chargers_in_use),
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"lot_id": lot_id, "occupancy": body.occupancy, "logged": True}


# ============================================================
# PAGE 3: PERMITS
# ============================================================


@router.get("/api/admin/permits")
def list_permits(_: dict = Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT permit_id, permit_name, description FROM permits ORDER BY permit_name")
    permits = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"permits": permits}


@router.post("/api/admin/permits", status_code=201)
def create_permit(body: PermitCreate, _: dict = Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS n FROM permits WHERE permit_id = %s",
                   (body.permit_id,))
    if cursor.fetchone()["n"] > 0:
        cursor.close(); conn.close()
        raise HTTPException(status_code=409, detail="Permit ID already exists")

    cursor.execute(
        "INSERT INTO permits (permit_id, permit_name, description) VALUES (%s, %s, %s)",
        (body.permit_id, body.permit_name, body.description),
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"permit_id": body.permit_id, "message": "Permit created"}


@router.put("/api/admin/permits/{permit_id}")
def update_permit(permit_id: str, body: PermitUpdate,
                  _: dict = Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE permits SET permit_name = %s, description = %s WHERE permit_id = %s",
        (body.permit_name, body.description, permit_id),
    )
    affected = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Permit not found")
    return {"permit_id": permit_id, "message": "Permit updated"}


@router.delete("/api/admin/permits/{permit_id}")
def delete_permit(permit_id: str, _: dict = Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT
            (SELECT COUNT(*) FROM parking_rules  WHERE permit_id = %s) AS rules_using,
            (SELECT COUNT(*) FROM user_permits   WHERE permit_id = %s) AS users_using
        """,
        (permit_id, permit_id),
    )
    deps = cursor.fetchone()
    if deps["rules_using"] or deps["users_using"]:
        cursor.close(); conn.close()
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete: {deps['rules_using']} rules and "
                   f"{deps['users_using']} users still use this permit",
        )

    cursor.execute("DELETE FROM permits WHERE permit_id = %s", (permit_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Permit deleted"}


# ============================================================
# PAGE 3: USERS + USER-PERMITS
# ============================================================


@router.get("/api/admin/users")
def list_users(search: Optional[str] = None, _: dict = Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if search:
        wc = f"%{search}%"
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
            WHERE u.user_id LIKE %s OR u.first_name LIKE %s
               OR u.last_name LIKE %s OR u.email LIKE %s
            ORDER BY u.last_name, u.first_name
            """,
            (wc, wc, wc, wc),
        )
    else:
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
            ORDER BY u.last_name, u.first_name
            """
        )

    rows = cursor.fetchall()
    for r in rows:
        if r.get("issued_date"):
            r["issued_date"] = str(r["issued_date"])
        if r.get("expiration_date"):
            r["expiration_date"] = str(r["expiration_date"])
    cursor.close()
    conn.close()
    return {"users": rows}


@router.post("/api/admin/user-permits", status_code=201)
def assign_permit(body: UserPermitCreate, _: dict = Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT COUNT(*) AS n FROM user_permits WHERE user_id = %s AND permit_id = %s",
        (body.user_id, body.permit_id),
    )
    if cursor.fetchone()["n"] > 0:
        cursor.close(); conn.close()
        raise HTTPException(status_code=409, detail="User already has this permit")

    cursor.execute(
        """
        INSERT INTO user_permits (user_id, permit_id, issued_date, expiration_date)
        VALUES (%s, %s, %s, %s)
        """,
        (body.user_id, body.permit_id, body.issued_date, body.expiration_date),
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Permit assigned"}


@router.put("/api/admin/user-permits/{user_id}/{permit_id}")
def renew_permit_individual(user_id: str, permit_id: str, body: UserPermitRenew,
                            _: dict = Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE user_permits
        SET issued_date = %s, expiration_date = %s
        WHERE user_id = %s AND permit_id = %s
        """,
        (body.issued_date, body.expiration_date, user_id, permit_id),
    )
    affected = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Permit assignment not found")
    return {"message": "Permit renewed"}


@router.delete("/api/admin/user-permits/{user_id}/{permit_id}")
def revoke_permit(user_id: str, permit_id: str,
                  _: dict = Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM user_permits WHERE user_id = %s AND permit_id = %s",
        (user_id, permit_id),
    )
    affected = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Permit assignment not found")
    return {"message": "Permit revoked"}


@router.put("/api/admin/bulk-renew/{permit_id}")
def bulk_renew(permit_id: str, body: BulkRenew,
               _: dict = Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS n FROM user_permits WHERE permit_id = %s",
                   (permit_id,))
    count = cursor.fetchone()["n"]

    cursor.execute(
        "UPDATE user_permits SET expiration_date = %s WHERE permit_id = %s",
        (body.new_expiration_date, permit_id),
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"users_affected": count, "new_expiration": body.new_expiration_date}
