"""ATLAS API: FastAPI backend for students, companies, and admin."""
import json
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, Header, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import auth
import chatbot
import live_data
import llm
from database import (UPLOADS_DIR, get_conn, init_db, insert_returning_id,
                      notify, row_to_internship, row_to_student)
from matching import engine, scoring
from matching.embeddings import skill_similarity_matrix

app = FastAPI(title="ATLAS", description="AI-based internship allocation for SIH25033")

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"


def load_students() -> list[dict]:
    with get_conn() as conn:
        return [row_to_student(r) for r in conn.execute("SELECT * FROM students")]


def load_internships(include_suspended: bool = False) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM internships")
        items = [row_to_internship(r) for r in rows]
    if not include_suspended:
        items = [j for j in items if j.get("status") != "Suspended"]
    return items


def principal(authorization: str) -> dict | None:
    token = authorization.removeprefix("Bearer ").strip()
    return auth.principal_for_token(token) if token else None


def require_role(authorization: str, role: str) -> dict:
    p = principal(authorization)
    if not p or p["role"] != role:
        raise HTTPException(403, f"{role.capitalize()} sign-in required.")
    return p


def pair_score(student: dict, internship: dict) -> dict:
    sim = skill_similarity_matrix([student], [internship])[0][0]
    return scoring.composite(student, internship, sim)


@app.on_event("startup")
def startup() -> None:
    init_db()
    with get_conn() as conn:
        if conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0] == 0:
            import seed
            seed.seed()


# ================= auth =================
class SignupBody(BaseModel):
    name: str
    email: str
    password: str


class CompanySignupBody(BaseModel):
    company_name: str
    sector: str
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


@app.post("/api/auth/company/signup")
def auth_company_signup(item: CompanySignupBody):
    try:
        return auth.company_signup(item.company_name, item.sector, item.email, item.password)
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
    p = principal(authorization)
    if not p:
        raise HTTPException(401, "Not signed in")
    return p


@app.post("/api/auth/logout")
def auth_logout(authorization: str = Header("")):
    token = authorization.removeprefix("Bearer ").strip()
    if token:
        auth.logout(token)
    return {"ok": True}


# ================= internships (public browse) =================
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


# ================= student profile + recommendations =================
class ProfileUpdate(BaseModel):
    skills: list[str]
    qualification: str
    qualification_level: int
    preferred_locations: list[str]
    preferred_sectors: list[str]
    first_generation: bool
    college_tier: int


@app.put("/api/students/{student_id}")
def update_student(student_id: int, item: ProfileUpdate,
                   authorization: str = Header("")):
    p = principal(authorization)
    if not p or p["role"] != "student" or p["student"]["id"] != student_id:
        raise HTTPException(403, "You can only edit your own profile.")
    with get_conn() as conn:
        conn.execute(
            "UPDATE students SET skills=?, qualification=?, qualification_level=?,"
            " preferred_locations=?, preferred_sectors=?, first_generation=?,"
            " college_tier=? WHERE id=?",
            (json.dumps(item.skills), item.qualification, item.qualification_level,
             json.dumps(item.preferred_locations), json.dumps(item.preferred_sectors),
             int(item.first_generation), item.college_tier, student_id))
        row = conn.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
    return row_to_student(row)


@app.get("/api/students/{student_id}/recommendations")
def get_recommendations(student_id: int, top_n: int = Query(6, ge=1, le=20)):
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


@app.get("/api/students/{student_id}/skill-analytics")
def skill_analytics(student_id: int):
    students = load_students()
    student = next((s for s in students if s["id"] == student_id), None)
    if not student:
        raise HTTPException(404, "Student not found")
    internships = load_internships()
    demand: dict[str, int] = {}
    canonical: dict[str, str] = {}
    for j in internships:
        for sk in j["skills_required"]:
            key = sk.lower()
            canonical.setdefault(key, sk)
            demand[key] = demand.get(key, 0) + 1
    have = {s.lower() for s in student["skills"]}
    ranked = sorted(demand.items(), key=lambda kv: -kv[1])
    top_demand = [{"skill": canonical[k], "count": v, "have": k in have}
                  for k, v in ranked[:12]]
    missing = [d for d in top_demand if not d["have"]][:5]
    coverage_hits = sum(1 for j in internships
                        if any(sk.lower() in have for sk in j["skills_required"]))
    return {
        "skills": student["skills"],
        "coverage_pct": round(coverage_hits / len(internships) * 100) if internships else 0,
        "top_demand": top_demand,
        "top_missing": missing,
        "total_internships": len(internships),
    }


# ================= applications (no cap) =================
class Application(BaseModel):
    student_id: int
    internship_id: int


@app.post("/api/apply")
def apply(item: Application, authorization: str = Header("")):
    p = principal(authorization)
    if not p or p["role"] != "student" or p["student"]["id"] != item.student_id:
        raise HTTPException(403, "Sign in as a student to apply.")
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id FROM applications WHERE student_id=? AND internship_id=?",
            (item.student_id, item.internship_id)).fetchone()
        if existing:
            raise HTTPException(400, "Already applied to this internship.")
        j = conn.execute("SELECT * FROM internships WHERE id=?",
                         (item.internship_id,)).fetchone()
        if not j:
            raise HTTPException(404, "Internship not found")
        conn.execute(
            "INSERT INTO applications (student_id, internship_id, applied_at, status)"
            " VALUES (?,?,?,?)",
            (item.student_id, item.internship_id,
             datetime.now(timezone.utc).isoformat(), "Applied"))
        if j["company_id"]:
            notify(conn, "company", j["company_id"],
                   f"New application for {j['title']} from {p['student']['name']}.",
                   "c-applicants")
    return {"ok": True}


@app.get("/api/students/{student_id}/applications")
def list_applications(student_id: int):
    internships = {j["id"]: j for j in load_internships(include_suspended=True)}
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM applications WHERE student_id=? ORDER BY applied_at DESC",
            (student_id,)).fetchall()
    return [{**dict(r), "internship": internships.get(r["internship_id"])}
            for r in rows]


ADMIN_STATUSES = {"Shortlisted", "Offer Sent", "Rejected"}
STUDENT_STATUSES = {"Accepted", "Declined"}


class StatusBody(BaseModel):
    status: str


@app.patch("/api/applications/{app_id}/status")
def update_application_status(app_id: int, item: StatusBody,
                              authorization: str = Header("")):
    if item.status not in ADMIN_STATUSES | STUDENT_STATUSES:
        raise HTTPException(400, "Invalid status")
    p = principal(authorization)
    if not p:
        raise HTTPException(401, "Sign-in required.")
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM applications WHERE id=?", (app_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Application not found")
        j = conn.execute("SELECT * FROM internships WHERE id=?",
                         (row["internship_id"],)).fetchone()
        if item.status in ADMIN_STATUSES:
            allowed = p["role"] == "admin" or (
                p["role"] == "company" and p["company"]
                and j["company_id"] == p["company"]["id"])
            if not allowed:
                raise HTTPException(403, "Only the posting company or admin can do that.")
        else:
            if not (p["role"] == "student" and p["student"]
                    and p["student"]["id"] == row["student_id"]):
                raise HTTPException(403, "Only the applicant can respond to an offer.")
        conn.execute("UPDATE applications SET status=? WHERE id=?",
                     (item.status, app_id))
        if item.status in ADMIN_STATUSES:
            notify(conn, "student", row["student_id"],
                   f"Update on {j['title']} at {j['company']}: {item.status}."
                   + (" Respond within 14 days." if item.status == "Offer Sent" else ""),
                   "applications")
        elif j["company_id"]:
            notify(conn, "company", j["company_id"],
                   f"An applicant has {item.status.lower()} the offer for {j['title']}.",
                   "c-applicants")
    return {"ok": True, "status": item.status}


# ================= company portal =================
class CompanyInternship(BaseModel):
    title: str
    location: str
    state: str = ""
    skills_required: list[str]
    min_qualification_level: int = 1
    duration_months: int = 12
    stipend: int = 5000
    capacity: int = 5
    description: str = ""
    assessment_stages: list[str] = []


@app.get("/api/company/me")
def company_me(authorization: str = Header("")):
    p = require_role(authorization, "company")
    c = p["company"]
    with get_conn() as conn:
        listings = [row_to_internship(r) for r in conn.execute(
            "SELECT * FROM internships WHERE company_id=?", (c["id"],))]
        listing_ids = [j["id"] for j in listings]
        n_apps = 0
        if listing_ids:
            qmarks = ",".join("?" * len(listing_ids))
            n_apps = conn.execute(
                f"SELECT COUNT(*) FROM applications WHERE internship_id IN ({qmarks})",
                listing_ids).fetchone()[0]
    return {"company": c, "listings": listings, "applications": n_apps}


@app.post("/api/company/internships")
def company_post_internship(item: CompanyInternship, authorization: str = Header("")):
    p = require_role(authorization, "company")
    c = p["company"]
    desc = item.description or (
        f"{item.title} at {c['name']}, {item.location}. Work on "
        f"{', '.join(item.skills_required[:3])} under the PM Internship Scheme.")
    with get_conn() as conn:
        new_id = insert_returning_id(
            conn,
            "INSERT INTO internships (title, company, sector, location, state,"
            " skills_required, min_qualification_level, duration_months, stipend,"
            " capacity, verified, description, company_about, assessment_stages,"
            " company_id, status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (item.title, c["name"], c["sector"], item.location,
             item.state or item.location, json.dumps(item.skills_required),
             item.min_qualification_level, item.duration_months, item.stipend,
             item.capacity, 0, desc, c.get("about", ""),
             json.dumps(item.assessment_stages), c["id"], "Pending"))
        row = conn.execute("SELECT * FROM internships WHERE id=?", (new_id,)).fetchone()
    return row_to_internship(row)


@app.get("/api/company/applicants")
def company_applicants(authorization: str = Header("")):
    p = require_role(authorization, "company")
    c = p["company"]
    students = {s["id"]: s for s in load_students()}
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT a.*, i.title AS internship_title, i.id AS iid FROM applications a"
            " JOIN internships i ON i.id = a.internship_id"
            " WHERE i.company_id=? ORDER BY a.applied_at DESC", (c["id"],)).fetchall()
        docs = {}
        for d in conn.execute("SELECT * FROM documents"):
            docs.setdefault(d["student_id"], []).append(
                {"id": d["id"], "filename": d["filename"]})
        internships = {j["id"]: j for j in load_internships(include_suspended=True)}
    out = []
    for r in rows:
        s = students.get(r["student_id"])
        j = internships.get(r["iid"])
        if not s or not j:
            continue
        score = pair_score(s, j)
        out.append({
            "id": r["id"], "status": r["status"], "applied_at": r["applied_at"],
            "internship_title": r["internship_title"],
            "student": {"id": s["id"], "name": s["name"],
                        "qualification": s["qualification"], "skills": s["skills"],
                        "home_state": s["home_state"]},
            "match_pct": round(score["total_score"] * 100),
            "documents": docs.get(s["id"], []),
        })
    return out


# ================= documents / resume =================
SKILL_VOCAB_EXTRA = ["Python", "Java", "JavaScript", "React", "SQL", "Excel",
                     "Machine Learning", "Data Analysis", "AutoCAD", "Tally",
                     "Communication", "Marketing", "Sales", "Cloud Computing"]


def _parse_resume_skills(path: Path) -> list[str]:
    try:
        from pypdf import PdfReader
        text = " ".join((page.extract_text() or "")
                        for page in PdfReader(str(path)).pages).lower()
    except Exception:
        return []
    vocab: dict[str, str] = {}
    for j in load_internships(include_suspended=True):
        for sk in j["skills_required"]:
            vocab[sk.lower()] = sk
    for sk in SKILL_VOCAB_EXTRA:
        vocab.setdefault(sk.lower(), sk)
    found = [orig for low, orig in vocab.items() if low in text]
    return sorted(set(found))[:15]


@app.post("/api/documents")
async def upload_document(file: UploadFile = File(...), authorization: str = Header("")):
    p = require_role(authorization, "student")
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Please upload a PDF file.")
    data = await file.read()
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 5 MB).")
    stored = f"{p['student']['id']}_{secrets.token_hex(6)}.pdf"
    path = UPLOADS_DIR / stored
    path.write_bytes(data)
    skills = _parse_resume_skills(path)
    with get_conn() as conn:
        doc_id = insert_returning_id(
            conn,
            "INSERT INTO documents (student_id, filename, stored_path, uploaded_at,"
            " parsed_skills) VALUES (?,?,?,?,?)",
            (p["student"]["id"], file.filename, stored,
             datetime.now(timezone.utc).isoformat(), json.dumps(skills)))
    return {"id": doc_id, "filename": file.filename, "parsed_skills": skills}


@app.get("/api/documents")
def my_documents(authorization: str = Header("")):
    p = require_role(authorization, "student")
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, filename, uploaded_at, parsed_skills FROM documents"
            " WHERE student_id=? ORDER BY uploaded_at DESC",
            (p["student"]["id"],)).fetchall()
    return [{**dict(r), "parsed_skills": json.loads(r["parsed_skills"])} for r in rows]


@app.get("/api/documents/{doc_id}/download")
def download_document(doc_id: int, authorization: str = Header(""),
                      token: str = Query("")):
    p = principal(authorization) or auth.principal_for_token(token)
    if not p:
        raise HTTPException(401, "Sign-in required.")
    with get_conn() as conn:
        d = conn.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
    if not d:
        raise HTTPException(404, "Document not found")
    is_owner = p["role"] == "student" and p["student"] and p["student"]["id"] == d["student_id"]
    if not (is_owner or p["role"] in ("admin", "company")):
        raise HTTPException(403, "Not allowed.")
    return FileResponse(UPLOADS_DIR / d["stored_path"], filename=d["filename"],
                        media_type="application/pdf")


# ================= notifications =================
@app.get("/api/notifications")
def get_notifications(authorization: str = Header("")):
    p = principal(authorization)
    if not p or p["role"] == "admin":
        return {"unread": 0, "items": []}
    rid = p["student"]["id"] if p["role"] == "student" else p["company"]["id"]
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM notifications WHERE role=? AND recipient_id=?"
            " ORDER BY created_at DESC LIMIT 50", (p["role"], rid)).fetchall()
    items = [dict(r) for r in rows]
    return {"unread": sum(1 for i in items if not i["read"]), "items": items}


@app.post("/api/notifications/read")
def mark_notifications_read(authorization: str = Header("")):
    p = principal(authorization)
    if not p or p["role"] == "admin":
        return {"ok": True}
    rid = p["student"]["id"] if p["role"] == "student" else p["company"]["id"]
    with get_conn() as conn:
        conn.execute("UPDATE notifications SET read=1 WHERE role=? AND recipient_id=?",
                     (p["role"], rid))
    return {"ok": True}


# ================= complaints =================
class ComplaintBody(BaseModel):
    subject: str
    details: str


@app.post("/api/complaints")
def submit_complaint(item: ComplaintBody, authorization: str = Header("")):
    p = require_role(authorization, "student")
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO complaints (student_id, subject, details, status, created_at)"
            " VALUES (?,?,?,?,?)",
            (p["student"]["id"], item.subject.strip(), item.details.strip(),
             "Open", datetime.now(timezone.utc).isoformat()))
    return {"ok": True}


@app.get("/api/admin/complaints")
def admin_complaints(authorization: str = Header("")):
    require_role(authorization, "admin")
    students = {s["id"]: s for s in load_students()}
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM complaints ORDER BY created_at DESC").fetchall()
    return [{**dict(r), "student_name": students.get(r["student_id"], {}).get("name", "?")}
            for r in rows]


@app.patch("/api/admin/complaints/{cid}")
def resolve_complaint(cid: int, item: StatusBody, authorization: str = Header("")):
    require_role(authorization, "admin")
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM complaints WHERE id=?", (cid,)).fetchone()
        if not row:
            raise HTTPException(404, "Not found")
        conn.execute("UPDATE complaints SET status=? WHERE id=?", (item.status, cid))
        notify(conn, "student", row["student_id"],
               f"Your grievance '{row['subject']}' is now: {item.status}.", "help")
    return {"ok": True}


# ================= admin =================
@app.get("/api/admin/companies")
def admin_companies(authorization: str = Header("")):
    require_role(authorization, "admin")
    with get_conn() as conn:
        companies = [dict(r) for r in conn.execute("SELECT * FROM companies ORDER BY name")]
        counts = {r["company_id"]: r["n"] for r in conn.execute(
            "SELECT company_id, COUNT(*) AS n FROM internships"
            " WHERE company_id IS NOT NULL GROUP BY company_id")}
    for c in companies:
        c["listings"] = counts.get(c["id"], 0)
    return companies


@app.patch("/api/admin/companies/{cid}/status")
def set_company_status(cid: int, item: StatusBody, authorization: str = Header("")):
    require_role(authorization, "admin")
    if item.status not in ("Active", "Suspended"):
        raise HTTPException(400, "Status must be Active or Suspended")
    with get_conn() as conn:
        conn.execute("UPDATE companies SET status=? WHERE id=?", (item.status, cid))
        notify(conn, "company", cid, f"Your company account is now {item.status}.", "")
    return {"ok": True}


@app.patch("/api/admin/internships/{iid}/status")
def set_internship_status(iid: int, item: StatusBody, authorization: str = Header("")):
    require_role(authorization, "admin")
    if item.status not in ("Verified", "Pending", "Suspended"):
        raise HTTPException(400, "Invalid status")
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM internships WHERE id=?", (iid,)).fetchone()
        if not row:
            raise HTTPException(404, "Not found")
        conn.execute("UPDATE internships SET status=?, verified=? WHERE id=?",
                     (item.status, 1 if item.status == "Verified" else 0, iid))
        if row["company_id"]:
            notify(conn, "company", row["company_id"],
                   f"Your listing '{row['title']}' is now {item.status}.", "c-listings")
    return {"ok": True}


@app.get("/api/admin/students")
def admin_students(search: str = "", page: int = Query(1, ge=1),
                   page_size: int = Query(20, ge=1, le=250)):
    students = load_students()
    internships = {j["id"]: j for j in load_internships(include_suspended=True)}
    with get_conn() as conn:
        alloc = {r["student_id"]: dict(r) for r in conn.execute("SELECT * FROM allocations")}
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
            "match_score": a["total_score"] if a else None,
        })
    if search:
        q = search.lower()
        rows = [r for r in rows if q in r["name"].lower()
                or (r["allocated_company"] or "").lower().find(q) >= 0]
    total = len(rows)
    start = (page - 1) * page_size
    return {"total": total, "page": page, "page_size": page_size,
            "items": rows[start:start + page_size]}


@app.get("/api/admin/stats")
def admin_stats():
    with get_conn() as conn:
        return {
            "students": conn.execute("SELECT COUNT(*) FROM students").fetchone()[0],
            "companies": conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0],
            "internships": conn.execute("SELECT COUNT(*) FROM internships").fetchone()[0],
            "capacity": conn.execute("SELECT COALESCE(SUM(capacity),0) FROM internships").fetchone()[0],
            "applications": conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0],
            "allocated": conn.execute("SELECT COUNT(*) FROM allocations").fetchone()[0],
        }


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


@app.post("/api/internships")
def add_internship(item: NewInternship, authorization: str = Header("")):
    require_role(authorization, "admin")
    desc = item.description or (
        f"{item.title} at {item.company}, {item.location}.")
    with get_conn() as conn:
        crow = conn.execute("SELECT id FROM companies WHERE name=?",
                            (item.company,)).fetchone()
        new_id = insert_returning_id(
            conn,
            "INSERT INTO internships (title, company, sector, location, state,"
            " skills_required, min_qualification_level, duration_months, stipend,"
            " capacity, verified, description, company_about, assessment_stages,"
            " company_id, status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (item.title, item.company, item.sector, item.location,
             item.state or item.location, json.dumps(item.skills_required),
             item.min_qualification_level, item.duration_months, item.stipend,
             item.capacity, int(item.verified), desc, "", "[]",
             crow["id"] if crow else None,
             "Verified" if item.verified else "Pending"))
        row = conn.execute("SELECT * FROM internships WHERE id=?", (new_id,)).fetchone()
    return row_to_internship(row)


# ================= allocation =================
@app.post("/api/allocate")
def run_allocation(authorization: str = Header("")):
    require_role(authorization, "admin")
    students = load_students()
    internships = load_internships()
    results = engine.run_allocation(students, internships) if students else []
    now = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        conn.execute("DELETE FROM allocations")
        conn.executemany(
            "INSERT INTO allocations (run_at, student_id, internship_id, total_score,"
            " skill_score, location_score, sector_score, fairness_boost, explanation)"
            " VALUES (?,?,?,?,?,?,?,?,?)",
            [(now, r["student_id"], r["internship_id"], r["total_score"],
              r["skill_score"], r["location_score"], r["sector_score"],
              r["fairness_boost"], r["explanation"]) for r in results])
        for r in results:
            j = next(x for x in internships if x["id"] == r["internship_id"])
            notify(conn, "student", r["student_id"],
                   f"Allocation result: you were matched to {j['title']} at "
                   f"{j['company']} ({round(r['total_score'] * 100)}% match).",
                   "dashboard")
    return _allocation_summary(results, students, internships)


@app.get("/api/allocation")
def get_allocation():
    students = load_students()
    internships = load_internships(include_suspended=True)
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM allocations ORDER BY total_score DESC").fetchall()
    if not rows:
        return {"run_at": None, "summary": None, "matches": []}
    return _allocation_summary([dict(r) for r in rows], students, internships)


def _allocation_summary(results, students, internships) -> dict:
    s_by_id = {s["id"]: s for s in students}
    j_by_id = {j["id"]: j for j in internships}
    matches = []
    for r in results:
        s, j = s_by_id.get(r["student_id"]), j_by_id.get(r["internship_id"])
        if not s or not j:
            continue
        matches.append({**{k: r[k] for k in
                           ("student_id", "internship_id", "total_score", "skill_score",
                            "location_score", "sector_score", "fairness_boost",
                            "explanation")},
                        "student_name": s["name"],
                        "first_generation": s["first_generation"],
                        "college_tier": s["college_tier"],
                        "internship_title": j["title"], "company": j["company"],
                        "location": j["location"], "verified": j["verified"]})
    n = len(students)
    placed = len(matches)
    return {
        "run_at": results[0].get("run_at") if results else None,
        "summary": {
            "students_total": n, "students_placed": placed,
            "placement_rate": round(placed / n, 4) if n else 0,
            "avg_match_score": round(sum(m["total_score"] for m in matches) / placed, 4) if placed else 0,
            "equity_placements": sum(1 for m in matches
                                     if m["first_generation"] or m["college_tier"] >= 2),
        },
        "matches": matches,
    }


# ================= chat =================
class ChatQuery(BaseModel):
    message: str
    student_id: int | None = None


@app.post("/api/chat")
def chat(item: ChatQuery, authorization: str = Header("")):
    internships = load_internships()
    students = load_students()
    p = principal(authorization)
    student = p["student"] if p and p["role"] == "student" else None
    applications = list_applications(student["id"]) if student else None

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


# ================= live government data =================
@app.get("/api/live/pmis")
def live_pmis():
    data = live_data.fetch_pmis_stats()
    if data is None:
        raise HTTPException(503, "Live government data is temporarily unavailable.")
    return data


@app.get("/api/live/insights")
def live_insights():
    data = live_data.fetch_insights()
    if data is None:
        raise HTTPException(503, "Live government data is temporarily unavailable.")
    return data


app.mount("/static", StaticFiles(directory=FRONTEND), name="static")


@app.get("/")
def index():
    return RedirectResponse("/student")


@app.get("/student")
@app.get("/company")
@app.get("/admin")
def portal():
    return FileResponse(FRONTEND / "index.html")
