"""
api/auth.py
===========
Authentication + authorization helpers.
- bcrypt password hashing/verification
- JWT token creation/validation
- FastAPI dependencies for protected routes
"""

from datetime import datetime, timedelta
from typing import Optional
import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from db import get_connection


# ============================================================
# JWT CONFIG
# ============================================================
# In a real app this would come from env vars. For this project
# it's hardcoded — just don't commit the secret to public git.

SECRET_KEY = "ole-miss-parking-dev-secret-change-me-in-prod"
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24

# Used by FastAPI dependencies to extract the token from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


# ============================================================
# PASSWORD HELPERS
# ============================================================


def hash_password(plain: str) -> str:
    """bcrypt-hash a plain password for storing in the database."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, stored_hash: str) -> bool:
    """Compare a plain password to a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), stored_hash.encode("utf-8"))
    except (ValueError, AttributeError):
        # Stored hash is malformed (e.g. sample data has 'hashed_pw_001')
        return False


# ============================================================
# JWT TOKEN HELPERS
# ============================================================


def create_token(user_id: str, role: str) -> str:
    """Generate a JWT with the user's ID and role baked in."""
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT. Raises if expired or malformed."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired. Log in again.",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        )


# ============================================================
# FASTAPI DEPENDENCIES
# ============================================================
# These get injected into route handlers. Use them to protect endpoints:
#   @app.get("/me")
#   def me(user = Depends(get_current_user)):
#       ...


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Extract the logged-in user from the Authorization header.
    Returns: {"user_id": ..., "role": ...}
    Raises 401 if the token is missing, expired, or invalid.
    """
    payload = decode_token(token)
    return {"user_id": payload["sub"], "role": payload["role"]}


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """
    Same as get_current_user but also enforces role = 'admin'.
    Use on admin-only endpoints.
    """
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return user


# ============================================================
# USER LOOKUP (for login)
# ============================================================


def lookup_user_by_email(email: str) -> Optional[dict]:
    """Fetch a user + their primary permit by email. Used during login."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT u.user_id, u.first_name, u.last_name, u.email,
               u.password_hash, u.role,
               p.permit_id AS permit_id, p.permit_name AS permit_name
        FROM users u
        LEFT JOIN user_permits up ON u.user_id = up.user_id
        LEFT JOIN permits p       ON up.permit_id = p.permit_id
        WHERE u.email = %s
        ORDER BY up.expiration_date DESC
        LIMIT 1
        """,
        (email,),
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user
