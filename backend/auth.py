"""Email/password authentication with PBKDF2 hashing and DB-backed sessions.

Roles: student (self signup), company (self signup, one account per company),
admin (single fixed credential). Works unchanged on PostgreSQL.
"""
import hashlib
import secrets
from datetime import datetime, timezone

from database import get_conn, insert_returning_id, row_to_student

PBKDF2_ITERATIONS = 200_000

# Single fixed admin account (per product decision for the prototype)
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "admin@1234"
ADMIN_USER_ID = 0


def _hash(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), PBKDF2_ITERATIONS
    ).hex()


def _create_user(conn, email: str, password: str, role: str,
                 student_id: int | None = None,
                 company_id: int | None = None) -> int:
    salt = secrets.token_hex(16)
    return insert_returning_id(
        conn,
        "INSERT INTO users (email, password_hash, salt, student_id, company_id,"
        " role, created_at) VALUES (?,?,?,?,?,?,?)",
        (email, _hash(password, salt), salt, student_id, company_id, role,
         datetime.now(timezone.utc).isoformat()))


def _email_taken(conn, email: str) -> bool:
    return bool(conn.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone())


import re as _re

MOBILE_RE = r"(\+91)?[6-9]\d{9}"


def clean_mobile(mobile: str) -> str:
    """Normalise and validate a mandatory Indian mobile number."""
    digits = _re.sub(r"[^\d+]", "", mobile or "")
    if not _re.fullmatch(MOBILE_RE, digits):
        raise ValueError("Please enter a valid 10-digit Indian mobile number.")
    return digits


def signup(name: str, email: str, password: str, mobile: str) -> dict:
    email = email.strip().lower()
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters.")
    if email == ADMIN_EMAIL:
        raise ValueError("This email is reserved.")
    mobile = clean_mobile(mobile)
    with get_conn() as conn:
        if _email_taken(conn, email):
            raise ValueError("An account with this email already exists.")
        student_id = insert_returning_id(
            conn,
            "INSERT INTO students (name, email, qualification, qualification_level,"
            " skills, preferred_locations, preferred_sectors, home_state,"
            " first_generation, college_tier, available_months, mobile)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (name.strip(), email, "12th Pass", 1, "[]", '["Any"]', "[]",
             "", 0, 3, 12, mobile))
        _create_user(conn, email, password, "student", student_id=student_id)
    return login(email, password)


def company_signup(company_name: str, sector: str, email: str, password: str) -> dict:
    email = email.strip().lower()
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters.")
    if email == ADMIN_EMAIL:
        raise ValueError("This email is reserved.")
    now = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        if _email_taken(conn, email):
            raise ValueError("An account with this email already exists.")
        existing = conn.execute("SELECT id FROM companies WHERE name=?",
                                (company_name.strip(),)).fetchone()
        if existing:
            company_id = existing["id"]
        else:
            # new companies await admin approval before they can post
            company_id = insert_returning_id(
                conn,
                "INSERT INTO companies (name, sector, about, status, created_at)"
                " VALUES (?,?,?,?,?)",
                (company_name.strip(), sector, "", "Pending", now))
        _create_user(conn, email, password, "company", company_id=company_id)
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
        return {"token": token, "role": "admin", "student": None, "company": None}
    with get_conn() as conn:
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if not user or not secrets.compare_digest(
                user["password_hash"], _hash(password, user["salt"])):
            raise ValueError("Invalid email or password.")
        token = secrets.token_hex(32)
        conn.execute(
            "INSERT INTO sessions (token, user_id, created_at) VALUES (?,?,?)",
            (token, user["id"], datetime.now(timezone.utc).isoformat()))
        student = company = None
        if user["student_id"]:
            row = conn.execute("SELECT * FROM students WHERE id=?",
                               (user["student_id"],)).fetchone()
            student = row_to_student(row) if row else None
        if user["company_id"]:
            row = conn.execute("SELECT * FROM companies WHERE id=?",
                               (user["company_id"],)).fetchone()
            company = dict(row) if row else None
    return {"token": token, "role": user["role"], "student": student, "company": company}


def principal_for_token(token: str) -> dict | None:
    """Resolve a session token to {'role', 'student', 'company'}."""
    if not token:
        return None
    with get_conn() as conn:
        sess = conn.execute("SELECT * FROM sessions WHERE token=?", (token,)).fetchone()
        if not sess:
            return None
        if sess["user_id"] == ADMIN_USER_ID:
            return {"role": "admin", "student": None, "company": None}
        user = conn.execute("SELECT * FROM users WHERE id=?",
                            (sess["user_id"],)).fetchone()
        if not user:
            return None
        student = company = None
        if user["student_id"]:
            row = conn.execute("SELECT * FROM students WHERE id=?",
                               (user["student_id"],)).fetchone()
            student = row_to_student(row) if row else None
        if user["company_id"]:
            row = conn.execute("SELECT * FROM companies WHERE id=?",
                               (user["company_id"],)).fetchone()
            company = dict(row) if row else None
        return {"role": user["role"], "student": student, "company": company}


def student_for_token(token: str) -> dict | None:
    p = principal_for_token(token)
    return p["student"] if p else None


def is_admin_token(token: str) -> bool:
    p = principal_for_token(token)
    return bool(p and p["role"] == "admin")


def logout(token: str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM sessions WHERE token=?", (token,))
