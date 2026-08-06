"""Deterministic seed data: ~200 students and ~50 internships across sectors."""
import json
import random

from database import get_conn, init_db

rng = random.Random(25033)  # SIH problem-statement number as seed

SECTORS = {
    "IT & Software": {
        "skills": ["Python", "Java", "JavaScript", "React", "SQL", "Data Analysis",
                   "Machine Learning", "Cloud Computing", "Git", "REST APIs"],
        "roles": ["Software Development Intern", "Data Analytics Intern",
                  "QA Engineering Intern", "Cloud Support Intern"],
        "companies": ["TCS", "Infosys", "Wipro", "HCLTech", "Tech Mahindra", "LTIMindtree"],
    },
    "Banking & Finance": {
        "skills": ["Accounting", "Excel", "Financial Analysis", "Tally",
                   "Data Entry", "Communication", "SQL", "Risk Analysis"],
        "roles": ["Banking Operations Intern", "Finance Analyst Intern",
                  "Audit Support Intern"],
        "companies": ["HDFC Bank", "ICICI Bank", "SBI", "Axis Bank", "Bajaj Finserv"],
    },
    "Manufacturing": {
        "skills": ["AutoCAD", "SolidWorks", "Quality Control", "Lean Manufacturing",
                   "Safety Compliance", "Maintenance", "PLC Programming"],
        "roles": ["Production Intern", "Quality Assurance Intern",
                  "Maintenance Engineering Intern"],
        "companies": ["Tata Motors", "Mahindra", "Larsen & Toubro", "Bajaj Auto", "JSW Steel"],
    },
    "Energy": {
        "skills": ["Electrical Systems", "Solar PV", "AutoCAD", "Safety Compliance",
                   "Field Operations", "Data Analysis"],
        "roles": ["Renewable Energy Intern", "Electrical Operations Intern"],
        "companies": ["NTPC", "Adani Green", "Tata Power", "ReNew Power"],
    },
    "Healthcare & Pharma": {
        "skills": ["Lab Techniques", "Quality Control", "Documentation",
                   "Biology", "Chemistry", "Data Entry", "Regulatory Compliance"],
        "roles": ["Pharma QC Intern", "Clinical Data Intern", "Lab Operations Intern"],
        "companies": ["Sun Pharma", "Cipla", "Dr. Reddy's", "Apollo Hospitals"],
    },
    "Retail & FMCG": {
        "skills": ["Sales", "Communication", "Inventory Management", "Excel",
                   "Marketing", "Customer Service", "Supply Chain"],
        "roles": ["Sales & Marketing Intern", "Supply Chain Intern",
                  "Store Operations Intern"],
        "companies": ["Hindustan Unilever", "ITC", "Reliance Retail", "Marico", "Dabur"],
    },
}

CITIES = [
    ("Mumbai", "Maharashtra"), ("Pune", "Maharashtra"), ("Bengaluru", "Karnataka"),
    ("Hyderabad", "Telangana"), ("Chennai", "Tamil Nadu"), ("Delhi", "Delhi"),
    ("Gurugram", "Haryana"), ("Kolkata", "West Bengal"), ("Ahmedabad", "Gujarat"),
    ("Jaipur", "Rajasthan"), ("Lucknow", "Uttar Pradesh"), ("Indore", "Madhya Pradesh"),
    ("Nagpur", "Maharashtra"), ("Coimbatore", "Tamil Nadu"), ("Bhubaneswar", "Odisha"),
    ("Patna", "Bihar"), ("Guwahati", "Assam"), ("Visakhapatnam", "Andhra Pradesh"),
]

FIRST_NAMES = ["Aarav", "Vivaan", "Aditya", "Arjun", "Rohan", "Karthik", "Siddharth",
               "Rahul", "Amit", "Nikhil", "Ananya", "Diya", "Priya", "Sneha", "Kavya",
               "Meera", "Pooja", "Riya", "Shreya", "Neha", "Farhan", "Imran", "Zoya",
               "Fatima", "Gurpreet", "Harleen", "Joseph", "Mary", "Tenzin", "Lalita"]
LAST_NAMES = ["Sharma", "Verma", "Patel", "Reddy", "Nair", "Iyer", "Das", "Ghosh",
              "Kumar", "Singh", "Yadav", "Khan", "Sheikh", "Kaur", "Gill", "Fernandes",
              "D'Souza", "Meena", "Murmu", "Rao", "Naidu", "Pillai", "Joshi", "Kulkarni"]

QUALIFICATIONS = [
    ("12th Pass", 1), ("Diploma", 2), ("BA", 3), ("BCom", 3), ("BSc", 3),
    ("BTech CSE", 3), ("BTech Mechanical", 3), ("BTech Electrical", 3),
    ("BBA", 3), ("BPharm", 3), ("MBA", 4), ("MTech", 4), ("MSc", 4),
]


def make_students(n: int = 200) -> list[dict]:
    students = []
    for i in range(1, n + 1):
        sector = rng.choice(list(SECTORS))
        pool = SECTORS[sector]["skills"]
        # ~15% thin profiles to exercise the cold-start fallback
        thin = rng.random() < 0.15
        skills = rng.sample(pool, k=1 if thin else rng.randint(3, 6))
        qual, level = rng.choice(QUALIFICATIONS)
        home_city, home_state = rng.choice(CITIES)
        prefs = [home_city]
        if rng.random() < 0.5:
            prefs.append(rng.choice([c for c, _ in CITIES if c != home_city]))
        if rng.random() < 0.25:
            prefs = ["Any"]
        students.append({
            "id": i,
            "name": f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
            "email": f"student{i}@example.in",
            "qualification": qual,
            "qualification_level": level,
            "skills": skills,
            "preferred_locations": prefs,
            "preferred_sectors": [sector] + ([rng.choice(list(SECTORS))] if rng.random() < 0.3 else []),
            "home_state": home_state,
            "first_generation": int(rng.random() < 0.35),
            "college_tier": rng.choices([1, 2, 3], weights=[2, 4, 4])[0],
            "available_months": rng.choice([6, 12, 12, 12]),
        })
    return students


def make_internships(n: int = 50) -> list[dict]:
    internships = []
    for i in range(1, n + 1):
        sector = rng.choice(list(SECTORS))
        cfg = SECTORS[sector]
        role = rng.choice(cfg["roles"])
        company = rng.choice(cfg["companies"])
        city, state = rng.choice(CITIES)
        skills = rng.sample(cfg["skills"], k=rng.randint(3, 5))
        internships.append({
            "id": i,
            "title": role,
            "company": company,
            "sector": sector,
            "location": city,
            "state": state,
            "skills_required": skills,
            "min_qualification_level": rng.choices([1, 2, 3], weights=[2, 3, 5])[0],
            "duration_months": 12,
            "stipend": 5000,
            "capacity": rng.randint(2, 8),
            "verified": int(rng.random() < 0.7),
            "description": f"{role} at {company}, {city}. Work on {', '.join(skills[:3])} "
                           f"under the PM Internship Scheme. 12-month engagement with "
                           f"monthly assistance of Rs 5,000.",
        })
    return internships


def seed() -> None:
    init_db()
    with get_conn() as conn:
        conn.execute("DELETE FROM allocations")
        conn.execute("DELETE FROM students")
        conn.execute("DELETE FROM internships")
        for s in make_students():
            conn.execute(
                "INSERT INTO students VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (s["id"], s["name"], s["email"], s["qualification"],
                 s["qualification_level"], json.dumps(s["skills"]),
                 json.dumps(s["preferred_locations"]), json.dumps(s["preferred_sectors"]),
                 s["home_state"], s["first_generation"], s["college_tier"],
                 s["available_months"]),
            )
        for j in make_internships():
            conn.execute(
                "INSERT INTO internships VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (j["id"], j["title"], j["company"], j["sector"], j["location"],
                 j["state"], json.dumps(j["skills_required"]),
                 j["min_qualification_level"], j["duration_months"], j["stipend"],
                 j["capacity"], j["verified"], j["description"]),
            )
    print("Seeded 200 students and 50 internships.")


if __name__ == "__main__":
    seed()
