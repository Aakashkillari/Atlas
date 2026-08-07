"""Email/password authentication with PBKDF2 hashing and DB-backed sessions.

The same schema works unchanged on PostgreSQL when the demo moves off SQLite.
"""
import hashlib
import secrets
from datetime import datetime, timezone

from database import get_conn, insert_returning_id, row_to_student

PBKDF2_ITERATIONS = 200_000

# Prototype admin account (Phase 2 moves this to full RBAC with company roles)
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "admin@1234"
ADMIN_USER_ID = 0


def _hash(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), PBKDF2_ITERATIONS
    ).hex()


def signup(name: str, email: str, password: str) -> dict:
    email = email.strip().lower()
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters.")
    now = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        if conn.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
            raise ValueError("An account with this email already exists.")
        student_id = insert_returning_id(
            conn,
            "INSERT INTO students (name, email, qualification, qualification_level,"
            " skills, preferred_locations, preferred_sectors, home_state,"
            " first_generation, college_tier, available_months)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (name.strip(), email, "12th Pass", 1, "[]", '["Any"]', "[]",
             "", 0, 3, 12))
        salt = secrets.token_hex(16)
        conn.execute(
            "INSERT INTO users (email, password_hash, salt, student_id, created_at)"
            " VALUES (?,?,?,?,?)",
            (email, _hash(password, salt), salt, student_id, now))
    return login(email, password)


def login(email: str, password: str) -> dict:
    email = email.strip().lower()
    if email == ADMIN_EMAIL:
        if not secrets.compare_digest(password, ADMIN_PASSWORD):
            raise ValueError("Invalid email or password.")
        token = secrets.token_hex(32)
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO sessions (token, user_id, created_at) VALUES (?,?,?)",
                (token, ADMIN_USER_ID, datetime.now(timezone.utc).isoformat()))
        return {"token": token, "admin": True, "student": None}
    with get_conn() as conn:
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if not user or not secrets.compare_digest(
                user["password_hash"], _hash(password, user["salt"])):
            raise ValueError("Invalid email or password.")
        token = secrets.token_hex(32)
        conn.execute(
            "INSERT INTO sessions (token, user_id, created_at) VALUES (?,?,?)",
            (token, user["id"], datetime.now(timezone.utc).isoformat()))
        student = conn.execute(
            "SELECT * FROM students WHERE id=?", (user["student_id"],)).fetchone()
    return {"token": token, "student": row_to_student(student)}


def student_for_token(token: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT s.* FROM sessions x"
            " JOIN users u ON u.id = x.user_id"
            " JOIN students s ON s.id = u.student_id"
            " WHERE x.token=?", (token,)).fetchone()
    return row_to_student(row) if row else None


def is_admin_token(token: str) -> bool:
    if not token:
        return False
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM sessions WHERE token=? AND user_id=?",
            (token, ADMIN_USER_ID)).fetchone()
    return bool(row)


def logout(token: str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM sessions WHERE token=?", (token,))
