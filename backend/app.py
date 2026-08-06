"""ATLAS API — FastAPI backend serving the matching engine and the dashboard."""
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from database import get_conn, init_db, row_to_internship, row_to_student
from matching import engine

app = FastAPI(title="ATLAS", description="AI-based internship matching for SIH25033")

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"


def load_students() -> list[dict]:
    with get_conn() as conn:
        return [row_to_student(r) for r in conn.execute("SELECT * FROM students")]


def load_internships() -> list[dict]:
    with get_conn() as conn:
        return [row_to_internship(r) for r in conn.execute("SELECT * FROM internships")]


@app.on_event("startup")
def startup() -> None:
    init_db()
    with get_conn() as conn:
        if conn.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0:
            import seed
            seed.seed()


@app.get("/api/internships")
def list_internships(search: str = "", page: int = Query(1, ge=1),
                     page_size: int = Query(10, ge=1, le=50)):
    items = load_internships()
    if search:
        q = search.lower()
        items = [j for j in items
                 if q in j["title"].lower() or q in j["company"].lower()
                 or q in j["sector"].lower() or q in j["location"].lower()
                 or any(q in sk.lower() for sk in j["skills_required"])]
    total = len(items)
    start = (page - 1) * page_size
    return {"total": total, "page": page, "page_size": page_size,
            "items": items[start:start + page_size]}


@app.get("/api/students")
def list_students(page: int = Query(1, ge=1),
                  page_size: int = Query(20, ge=1, le=250)):
    items = load_students()
    start = (page - 1) * page_size
    return {"total": len(items), "page": page, "page_size": page_size,
            "items": items[start:start + page_size]}


@app.get("/api/students/{student_id}")
def get_student(student_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Student not found")
    return row_to_student(row)


@app.get("/api/students/{student_id}/recommendations")
def get_recommendations(student_id: int, top_n: int = Query(5, ge=1, le=20)):
    students = load_students()
    student = next((s for s in students if s["id"] == student_id), None)
    if not student:
        raise HTTPException(404, "Student not found")
    internships = load_internships()
    result = engine.recommend(student, students, internships, top_n=top_n)
    j_by_id = {j["id"]: j for j in internships}
    for rec in result["recommendations"]:
        rec["internship"] = j_by_id[rec["internship_id"]]
    return result


@app.post("/api/allocate")
def run_allocation():
    students = load_students()
    internships = load_internships()
    results = engine.run_allocation(students, internships)
    now = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        conn.execute("DELETE FROM allocations")
        conn.executemany(
            "INSERT INTO allocations (run_at, student_id, internship_id, total_score,"
            " skill_score, location_score, sector_score, fairness_boost, explanation)"
            " VALUES (?,?,?,?,?,?,?,?,?)",
            [(now, r["student_id"], r["internship_id"], r["total_score"],
              r["skill_score"], r["location_score"], r["sector_score"],
              r["fairness_boost"], r["explanation"]) for r in results],
        )
    return _allocation_summary(results, students, internships)


@app.get("/api/allocation")
def get_allocation():
    students = load_students()
    internships = load_internships()
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM allocations ORDER BY total_score DESC").fetchall()
    if not rows:
        return {"run_at": None, "summary": None, "matches": []}
    results = [dict(r) for r in rows]
    return _allocation_summary(results, students, internships)


def _allocation_summary(results: list[dict], students: list[dict],
                        internships: list[dict]) -> dict:
    s_by_id = {s["id"]: s for s in students}
    j_by_id = {j["id"]: j for j in internships}
    matches = []
    for r in results:
        s, j = s_by_id[r["student_id"]], j_by_id[r["internship_id"]]
        matches.append({**{k: r[k] for k in
                           ("student_id", "internship_id", "total_score", "skill_score",
                            "location_score", "sector_score", "fairness_boost",
                            "explanation")},
                        "student_name": s["name"], "student_qualification": s["qualification"],
                        "first_generation": s["first_generation"],
                        "college_tier": s["college_tier"],
                        "internship_title": j["title"], "company": j["company"],
                        "location": j["location"], "sector": j["sector"],
                        "verified": j["verified"]})
    n_students = len(students)
    placed = len(matches)
    equity = sum(1 for m in matches if m["first_generation"] or m["college_tier"] >= 2)
    avg = round(sum(m["total_score"] for m in matches) / placed, 4) if placed else 0
    return {
        "run_at": results[0].get("run_at") if results else None,
        "summary": {
            "students_total": n_students,
            "students_placed": placed,
            "placement_rate": round(placed / n_students, 4) if n_students else 0,
            "avg_match_score": avg,
            "equity_placements": equity,
        },
        "matches": matches,
    }


app.mount("/static", StaticFiles(directory=FRONTEND), name="static")


@app.get("/")
def index():
    return FileResponse(FRONTEND / "index.html")
