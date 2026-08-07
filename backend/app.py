"""ATLAS API — FastAPI backend serving the matching engine and the dashboard."""
import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import auth
import chatbot
import live_data
import llm
from database import get_conn, init_db, insert_returning_id, row_to_internship, row_to_student
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


class ProfileUpdate(BaseModel):
    skills: list[str]
    qualification: str
    qualification_level: int
    preferred_locations: list[str]
    preferred_sectors: list[str]
    first_generation: bool
    college_tier: int


@app.put("/api/students/{student_id}")
def update_student(student_id: int, item: ProfileUpdate):
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE students SET skills=?, qualification=?, qualification_level=?,"
            " preferred_locations=?, preferred_sectors=?, first_generation=?,"
            " college_tier=? WHERE id=?",
            (json.dumps(item.skills), item.qualification, item.qualification_level,
             json.dumps(item.preferred_locations), json.dumps(item.preferred_sectors),
             int(item.first_generation), item.college_tier, student_id))
        if cur.rowcount == 0:
            raise HTTPException(404, "Student not found")
        row = conn.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
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


class NewInternship(BaseModel):
    title: str
    company: str
    sector: str
    location: str
    state: str = ""
    skills_required: list[str]
    min_qualification_level: int = 1
    duration_months: int = 12
    stipend: int = 5000
    capacity: int = 5
    verified: bool = False
    description: str = ""
    company_about: str = ""
    assessment_stages: list[str] = []


@app.post("/api/internships")
def add_internship(item: NewInternship):
    desc = item.description or (
        f"{item.title} at {item.company}, {item.location}. Work on "
        f"{', '.join(item.skills_required[:3])} under the PM Internship Scheme.")
    with get_conn() as conn:
        new_id = insert_returning_id(
            conn,
            "INSERT INTO internships (title, company, sector, location, state,"
            " skills_required, min_qualification_level, duration_months, stipend,"
            " capacity, verified, description, company_about, assessment_stages)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (item.title, item.company, item.sector, item.location,
             item.state or item.location, json.dumps(item.skills_required),
             item.min_qualification_level, item.duration_months, item.stipend,
             item.capacity, int(item.verified), desc,
             item.company_about, json.dumps(item.assessment_stages)),
        )
        row = conn.execute("SELECT * FROM internships WHERE id=?",
                           (new_id,)).fetchone()
    return row_to_internship(row)


class Application(BaseModel):
    student_id: int
    internship_id: int


@app.post("/api/apply")
def apply(item: Application):
    with get_conn() as conn:
        active = conn.execute(
            "SELECT COUNT(*) FROM applications WHERE student_id=?",
            (item.student_id,)).fetchone()[0]
        if active >= 3:
            raise HTTPException(400, "Application limit reached: a candidate may "
                                     "hold at most 3 active applications.")
        existing = conn.execute(
            "SELECT id FROM applications WHERE student_id=? AND internship_id=?",
            (item.student_id, item.internship_id)).fetchone()
        if existing:
            raise HTTPException(400, "Already applied to this internship.")
        conn.execute(
            "INSERT INTO applications (student_id, internship_id, applied_at, status)"
            " VALUES (?,?,?,?)",
            (item.student_id, item.internship_id,
             datetime.now(timezone.utc).isoformat(), "Applied"))
    return {"ok": True}


@app.get("/api/students/{student_id}/applications")
def list_applications(student_id: int):
    internships = {j["id"]: j for j in load_internships()}
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM applications WHERE student_id=? ORDER BY applied_at DESC",
            (student_id,)).fetchall()
    return [{**dict(r), "internship": internships.get(r["internship_id"])}
            for r in rows]


def require_admin(authorization: str = Header("")):
    token = authorization.removeprefix("Bearer ").strip()
    if not auth.is_admin_token(token):
        raise HTTPException(403, "Admin sign-in required.")


APPLICATION_FLOW = ["Applied", "Shortlisted", "Offer Sent", "Accepted", "Declined", "Rejected"]
ADMIN_STATUSES = {"Shortlisted", "Offer Sent", "Rejected"}
STUDENT_STATUSES = {"Accepted", "Declined"}


class StatusBody(BaseModel):
    status: str


@app.patch("/api/applications/{app_id}/status")
def update_application_status(app_id: int, item: StatusBody,
                              authorization: str = Header("")):
    if item.status not in ADMIN_STATUSES | STUDENT_STATUSES:
        raise HTTPException(400, f"Status must be one of {sorted(ADMIN_STATUSES | STUDENT_STATUSES)}")
    if item.status in ADMIN_STATUSES:
        require_admin(authorization)
    with get_conn() as conn:
        cur = conn.execute("UPDATE applications SET status=? WHERE id=?",
                           (item.status, app_id))
        if cur.rowcount == 0:
            raise HTTPException(404, "Application not found")
    return {"ok": True, "status": item.status}


@app.get("/api/admin/applications")
def admin_applications(authorization: str = Header("")):
    require_admin(authorization)
    students = {s["id"]: s for s in load_students()}
    internships = {j["id"]: j for j in load_internships()}
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM applications ORDER BY applied_at DESC").fetchall()
    out = []
    for r in rows:
        s, j = students.get(r["student_id"]), internships.get(r["internship_id"])
        if not s or not j:
            continue
        out.append({"id": r["id"], "status": r["status"], "applied_at": r["applied_at"],
                    "student_name": s["name"], "student_qualification": s["qualification"],
                    "internship_title": j["title"], "company": j["company"],
                    "location": j["location"]})
    return out


@app.get("/api/admin/students")
def admin_students(search: str = "", page: int = Query(1, ge=1),
                   page_size: int = Query(20, ge=1, le=250)):
    """Students with their allocation result (which company they were matched to)."""
    students = load_students()
    internships = {j["id"]: j for j in load_internships()}
    with get_conn() as conn:
        alloc = {r["student_id"]: dict(r) for r in
                 conn.execute("SELECT * FROM allocations")}
        app_counts = {r["student_id"]: r["n"] for r in conn.execute(
            "SELECT student_id, COUNT(*) AS n FROM applications GROUP BY student_id")}
    rows = []
    for s in students:
        a = alloc.get(s["id"])
        j = internships.get(a["internship_id"]) if a else None
        rows.append({
            "id": s["id"], "name": s["name"], "qualification": s["qualification"],
            "skills": s["skills"], "home_state": s["home_state"],
            "first_generation": s["first_generation"],
            "college_tier": s["college_tier"],
            "applications": app_counts.get(s["id"], 0),
            "allocated": bool(a),
            "allocated_company": j["company"] if j else None,
            "allocated_role": j["title"] if j else None,
            "allocated_location": j["location"] if j else None,
            "match_score": a["total_score"] if a else None,
        })
    if search:
        q = search.lower()
        rows = [r for r in rows if q in r["name"].lower()
                or (r["allocated_company"] or "").lower().find(q) >= 0
                or (r["allocated_role"] or "").lower().find(q) >= 0]
    total = len(rows)
    start = (page - 1) * page_size
    return {"total": total, "page": page, "page_size": page_size,
            "items": rows[start:start + page_size]}


@app.get("/api/admin/stats")
def admin_stats():
    with get_conn() as conn:
        n_students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        n_internships = conn.execute("SELECT COUNT(*) FROM internships").fetchone()[0]
        n_capacity = conn.execute(
            "SELECT COALESCE(SUM(capacity),0) FROM internships").fetchone()[0]
        n_applications = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
        n_allocated = conn.execute("SELECT COUNT(*) FROM allocations").fetchone()[0]
        n_verified = conn.execute(
            "SELECT COUNT(*) FROM internships WHERE verified=1").fetchone()[0]
    return {"students": n_students, "internships": n_internships,
            "capacity": n_capacity, "applications": n_applications,
            "allocated": n_allocated, "verified_internships": n_verified}


class SignupBody(BaseModel):
    name: str
    email: str
    password: str


class LoginBody(BaseModel):
    email: str
    password: str


@app.post("/api/auth/signup")
def auth_signup(item: SignupBody):
    try:
        return auth.signup(item.name, item.email, item.password)
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.post("/api/auth/login")
def auth_login(item: LoginBody):
    try:
        return auth.login(item.email, item.password)
    except ValueError as e:
        raise HTTPException(401, str(e))


@app.get("/api/auth/me")
def auth_me(authorization: str = Header("")):
    token = authorization.removeprefix("Bearer ").strip()
    student = auth.student_for_token(token) if token else None
    if not student:
        raise HTTPException(401, "Not signed in")
    return student


@app.post("/api/auth/logout")
def auth_logout(authorization: str = Header("")):
    token = authorization.removeprefix("Bearer ").strip()
    if token:
        auth.logout(token)
    return {"ok": True}


class ChatQuery(BaseModel):
    message: str
    student_id: int | None = None


@app.post("/api/chat")
def chat(item: ChatQuery, authorization: str = Header("")):
    internships = load_internships()
    students = load_students()

    # resolve the student: signed-in session wins, else explicit demo id
    token = authorization.removeprefix("Bearer ").strip()
    student = auth.student_for_token(token) if token else None
    if student is None and item.student_id is not None:
        student = next((s for s in students if s["id"] == item.student_id), None)

    applications = None
    if student:
        applications = list_applications(student["id"])

    def recommender(s):
        rec = engine.recommend(s, students, internships, top_n=3)
        j_by_id = {j["id"]: j for j in internships}
        for r in rec["recommendations"]:
            r["internship"] = j_by_id[r["internship_id"]]
        return rec

    result = chatbot.answer(item.message, internships, student=student,
                            applications=applications, recommender=recommender)
    if llm.enabled():
        context = [j for j in internships if j["id"] in result["internships"]]
        result["reply"] = llm.chat_answer(item.message, context, result["reply"])
        result["llm"] = True
    return result


@app.get("/api/live/pmis")
def live_pmis():
    data = live_data.fetch_pmis_stats()
    if data is None:
        raise HTTPException(503, "Live government data is temporarily unavailable.")
    return data


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
