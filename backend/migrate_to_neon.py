"""One-shot migration: copy every row from the local SQLite database to
the Postgres database in DATABASE_URL (Neon).

Usage:
  1. Put the connection string in Atlas/.env as:  DATABASE_URL=postgresql://...
     (the .env file is gitignored and never leaves this machine)
  2. python backend/migrate_to_neon.py

Safe to re-run: it wipes the Postgres tables and copies fresh.
"""
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SQLITE_PATH = ROOT / "atlas.db"

# load .env if present (no dependency needed)
env_file = ROOT / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL.startswith(("postgres://", "postgresql://")):
    sys.exit("DATABASE_URL is not set. Put it in Atlas/.env as "
             "DATABASE_URL=postgresql://... and run again.")
if not SQLITE_PATH.exists():
    sys.exit(f"No local database found at {SQLITE_PATH}")

# initialise the Postgres schema using the app's own code
os.environ["DATABASE_URL"] = DATABASE_URL
sys.path.insert(0, str(ROOT / "backend"))
import database  # noqa: E402

database.init_db()

# FK-safe order
TABLES = ["companies", "students", "users", "sessions", "internships",
          "applications", "allocations", "documents", "notifications",
          "complaints"]

src = sqlite3.connect(SQLITE_PATH)
src.row_factory = sqlite3.Row

with database.get_conn() as dst:
    for table in reversed(TABLES):
        dst.execute(f"DELETE FROM {table}")
    for table in TABLES:
        rows = src.execute(f"SELECT * FROM {table}").fetchall()
        if not rows:
            print(f"{table}: 0 rows")
            continue
        cols = rows[0].keys()
        placeholders = ",".join("?" * len(cols))
        sql = f"INSERT INTO {table} ({','.join(cols)}) VALUES ({placeholders})"
        dst.executemany(sql, [tuple(r[c] for c in cols) for r in rows])
        print(f"{table}: {len(rows)} rows copied")
    database.sync_sequences(dst)

print("\nDone. Neon now has an exact copy of your local data.")
print("Point the app at it with DATABASE_URL (locally and on Render).")
