"""
api/routes_public.py
====================
Endpoints that don't require authentication.
- POST /api/login        → validate credentials, return JWT
- POST /api/register     → create new user (signup)
- GET  /api/lots         → load all lots for the map
- GET  /api/lots/browse  → visitor mode filter
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional

from db import get_connection
from auth import (
    hash_password,
    verify_password,
    create_token,
    lookup_user_by_email,
)

router = APIRouter()


# ============================================================
# PYDANTIC SCHEMAS
# ============================================================


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    first_name: str
    last_name: str
    role: str
    permit_name: Optional[str] = None


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    role: str  # "student" | "faculty" | "visitor"


# ============================================================
# LOGIN
# ============================================================


@router.post("/api/login", response_model=LoginResponse)
def login(body: LoginRequest):
    """
    Authenticate a user with email + password.
    On success, returns a JWT token the frontend stores for later requests.
    """
    user = lookup_user_by_email(body.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(body.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_token(user["user_id"], user["role"])
    return LoginResponse(
        access_token=token,
        user_id=user["user_id"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        role=user["role"],
        permit_name=user.get("permit_name"),
    )


# ============================================================
# REGISTER (basic — production would do email verification etc.)
# ============================================================


def _gen_userid(role: str) -> str:
    """Auto-generate next stu###/fac###/vis### ID."""
    prefix_map = {"student": "stu", "faculty": "fac", "visitor": "vis", "admin": "adm"}
    prefix = prefix_map.get(role.lower(), "usr")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT user_id FROM users
        WHERE user_id LIKE %s
        ORDER BY CAST(SUBSTRING(user_id, 4) AS UNSIGNED) DESC
        LIMIT 1
        """,
        (f"{prefix}%",),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    next_num = 1 if row is None else int(row[0][3:]) + 1
    return f"{prefix}{next_num:03d}"


@router.post("/api/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest):
    """
    Create a new user account. Hashes the password before inserting.
    """
    role = body.role.lower()
    if role not in ("student", "faculty", "visitor"):
        raise HTTPException(status_code=400, detail="Invalid role")

    # Check email isn't taken
    if lookup_user_by_email(body.email) is not None:
        raise HTTPException(status_code=409, detail="Email already registered")

    user_id = _gen_userid(role)
    pw_hash = hash_password(body.password)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO users (user_id, first_name, last_name, email, password_hash, role)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (user_id, body.first_name, body.last_name, body.email, pw_hash, role),
    )
    conn.commit()
    cursor.close()
    conn.close()

    return {"user_id": user_id, "message": "Account created. You can now log in."}


# ============================================================
# MAP DATA (public — visitors can browse without login)
# ============================================================


@router.get("/api/lots")
def get_all_lots():
    """Load all 12 lots with status for the map view."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT lot_id, lot_name, latitude, longitude,
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
        """
    )
    lots = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"lots": lots}


@router.get("/api/lots/browse")
def browse_as_visitor(permit_type: str = "V"):
    """
    Visitor mode: show lots that accept a given permit right now.
    No login required.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT pl.lot_id, pl.lot_name, pl.latitude, pl.longitude,
               pl.capacity, pl.current_occupancy,
               pl.capacity - pl.current_occupancy AS available_spaces,
               ROUND((pl.current_occupancy / pl.capacity) * 100, 1) AS occupancy_pct,
               pr.day_of_week, pr.start_time, pr.end_time
        FROM parking_rules pr
        JOIN parking_lots pl ON pr.lot_id = pl.lot_id
        WHERE pr.permit_id = %s
          AND pr.is_allowed = TRUE
          AND FIND_IN_SET(
                ELT(DAYOFWEEK(CURDATE()),
                    'Sun','Mon','Tue','Wed','Thu','Fri','Sat'),
                pr.day_of_week
              ) > 0
          AND CURTIME() BETWEEN pr.start_time AND pr.end_time
        ORDER BY occupancy_pct ASC
        """,
        (permit_type,),
    )
    lots = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"permit_type": permit_type, "available_lots": lots}
