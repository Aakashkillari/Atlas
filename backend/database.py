"""Database layer for ATLAS: SQLite by default, PostgreSQL when DATABASE_URL is set.

SQLite keeps local development zero-setup. Setting DATABASE_URL (a Neon or
Supabase Postgres connection string) switches the same schema and queries to
Postgres for persistent cloud deployments. Queries are written with `?`
placeholders and translated for Postgres automatically.
"""
import json
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "atlas.db"
DATABASE_URL = os.environ.get("DATABASE_URL", "")
IS_PG = DATABASE_URL.startswith(("postgres://", "postgresql://"))

if IS_PG:
    import psycopg

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id {PK},
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    qualification TEXT NOT NULL,
    qualification_level INTEGER NOT NULL,
    skills TEXT NOT NULL,
    preferred_locations TEXT NOT NULL,
    preferred_sectors TEXT NOT NULL,
    home_state TEXT NOT NULL,
    first_generation INTEGER NOT NULL,
    college_tier INTEGER NOT NULL,
    available_months INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS internships (
    id {PK},
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    sector TEXT NOT NULL,
    location TEXT NOT NULL,
    state TEXT NOT NULL,
    skills_required TEXT NOT NULL,
    min_qualification_level INTEGER NOT NULL,
    duration_months INTEGER NOT NULL,
    stipend INTEGER NOT NULL,
    capacity INTEGER NOT NULL,
    verified INTEGER NOT NULL,
    description TEXT NOT NULL,
    company_about TEXT NOT NULL DEFAULT '',
    assessment_stages TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS users (
    id {PK},
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    student_id INTEGER NOT NULL REFERENCES students(id),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS applications (
    id {PK},
    student_id INTEGER NOT NULL REFERENCES students(id),
    internship_id INTEGER NOT NULL REFERENCES internships(id),
    applied_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Applied',
    UNIQUE (student_id, internship_id)
);

CREATE TABLE IF NOT EXISTS allocations (
    id {PK},
    run_at TEXT NOT NULL,
    student_id INTEGER NOT NULL REFERENCES students(id),
    internship_id INTEGER NOT NULL REFERENCES internships(id),
    total_score REAL NOT NULL,
    skill_score REAL NOT NULL,
    location_score REAL NOT NULL,
    sector_score REAL NOT NULL,
    fairness_boost REAL NOT NULL,
    explanation TEXT NOT NULL
);
"""


class _HybridRow(dict):
    """Postgres row supporting both row["col"] and row[0] like sqlite3.Row."""
    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)


def _hybrid_row_factory(cursor):
    fields = [c.name for c in cursor.description] if cursor.description else []
    def make(values):
        return _HybridRow(zip(fields, values))
    return make


class _PGConn:
    """Thin wrapper translating sqlite-style `?` placeholders to `%s`."""
    def __init__(self, conn):
        self._conn = conn

    def execute(self, sql, params=()):
        return self._conn.execute(sql.replace("?", "%s"), params)

    def executemany(self, sql, seq_of_params):
        cur = self._conn.cursor()
        cur.executemany(sql.replace("?", "%s"), list(seq_of_params))
        return cur

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self._conn.commit()
        else:
            self._conn.rollback()
        self._conn.close()
        return False


def get_conn():
    if IS_PG:
        conn = psycopg.connect(DATABASE_URL, row_factory=_hybrid_row_factory)
        return _PGConn(conn)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    pk = "SERIAL PRIMARY KEY" if IS_PG else "INTEGER PRIMARY KEY"
    schema = SCHEMA.replace("{PK}", pk)
    with get_conn() as conn:
        for statement in schema.split(";"):
            if statement.strip():
                conn.execute(statement)


def insert_returning_id(conn, sql: str, params) -> int:
    """INSERT and return the new row id on both backends."""
    if IS_PG:
        return conn.execute(sql + " RETURNING id", params).fetchone()["id"]
    return conn.execute(sql, params).lastrowid


def sync_sequences(conn) -> None:
    """After seeding explicit ids on Postgres, advance the serial sequences."""
    if not IS_PG:
        return
    for table in ("students", "internships", "applications", "allocations", "users"):
        conn.execute(
            f"SELECT setval(pg_get_serial_sequence('{table}', 'id'),"
            f" COALESCE((SELECT MAX(id) FROM {table}), 1))")


def row_to_student(row) -> dict:
    d = dict(row)
    for key in ("skills", "preferred_locations", "preferred_sectors"):
        d[key] = json.loads(d[key])
    d["first_generation"] = bool(d["first_generation"])
    return d


def row_to_internship(row) -> dict:
    d = dict(row)
    d["skills_required"] = json.loads(d["skills_required"])
    d["assessment_stages"] = json.loads(d.get("assessment_stages") or "[]")
    d["verified"] = bool(d["verified"])
    return d
