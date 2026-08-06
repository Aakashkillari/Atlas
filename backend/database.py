"""SQLite database layer for ATLAS.

SQLite keeps the demo zero-setup. The production path is PostgreSQL +
pgvector (swap the cosine-similarity step in matching/embeddings.py for a
pgvector `<=>` query); the schema below maps 1:1 to that design.
"""
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "atlas.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    qualification TEXT NOT NULL,          -- e.g. 'BTech CSE'
    qualification_level INTEGER NOT NULL, -- 1=12th, 2=Diploma, 3=UG, 4=PG
    skills TEXT NOT NULL,                 -- JSON list
    preferred_locations TEXT NOT NULL,    -- JSON list, may contain 'Any'
    preferred_sectors TEXT NOT NULL,      -- JSON list
    home_state TEXT NOT NULL,
    first_generation INTEGER NOT NULL,    -- 0/1
    college_tier INTEGER NOT NULL,        -- 1/2/3
    available_months INTEGER NOT NULL     -- max internship duration they can commit
);

CREATE TABLE IF NOT EXISTS internships (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    sector TEXT NOT NULL,
    location TEXT NOT NULL,
    state TEXT NOT NULL,
    skills_required TEXT NOT NULL,        -- JSON list
    min_qualification_level INTEGER NOT NULL,
    duration_months INTEGER NOT NULL,
    stipend INTEGER NOT NULL,
    capacity INTEGER NOT NULL,
    verified INTEGER NOT NULL,            -- 0/1
    description TEXT NOT NULL,
    company_about TEXT NOT NULL DEFAULT '',
    assessment_stages TEXT NOT NULL DEFAULT '[]'  -- JSON list
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    student_id INTEGER NOT NULL REFERENCES students(id),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id),
    internship_id INTEGER NOT NULL REFERENCES internships(id),
    applied_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Applied',
    UNIQUE (student_id, internship_id)
);

CREATE TABLE IF NOT EXISTS allocations (
    id INTEGER PRIMARY KEY,
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


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def row_to_student(row: sqlite3.Row) -> dict:
    d = dict(row)
    for key in ("skills", "preferred_locations", "preferred_sectors"):
        d[key] = json.loads(d[key])
    d["first_generation"] = bool(d["first_generation"])
    return d


def row_to_internship(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["skills_required"] = json.loads(d["skills_required"])
    d["assessment_stages"] = json.loads(d.get("assessment_stages") or "[]")
    d["verified"] = bool(d["verified"])
    return d
