"""Deterministic seed data: ~200 students and ~50 internships across sectors."""
import json
import random

from database import get_conn, init_db, sync_sequences

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


# 25 hand-crafted realistic profiles (synthetic people, coherent stories).
# Format: name, qualification, level, skills, pref locations, pref sectors,
#         home_state, first_gen, tier, months
CURATED_STUDENTS = [
    ("Priya Deshmukh", "BTech CSE", 3, ["Python", "SQL", "Machine Learning", "Git"],
     ["Pune", "Mumbai"], ["IT & Software"], "Maharashtra", 0, 2, 12),
    ("Arjun Nair", "BTech CSE", 3, ["Java", "REST APIs", "SQL", "Cloud Computing"],
     ["Bengaluru"], ["IT & Software"], "Karnataka", 0, 1, 12),
    ("Kavitha Subramaniam", "BSc", 3, ["Data Analysis", "Excel", "SQL"],
     ["Chennai", "Coimbatore"], ["IT & Software", "Banking & Finance"], "Tamil Nadu", 1, 3, 12),
    ("Rohit Meena", "Diploma", 2, ["AutoCAD", "Maintenance", "Safety Compliance"],
     ["Jaipur"], ["Manufacturing"], "Rajasthan", 1, 3, 12),
    ("Sana Sheikh", "BCom", 3, ["Accounting", "Tally", "Excel", "Data Entry"],
     ["Hyderabad"], ["Banking & Finance"], "Telangana", 1, 2, 12),
    ("Vikram Choudhary", "BTech Mechanical", 3, ["SolidWorks", "Lean Manufacturing", "Quality Control"],
     ["Pune", "Nagpur"], ["Manufacturing"], "Maharashtra", 0, 2, 12),
    ("Ananya Banerjee", "MBA", 4, ["Marketing", "Communication", "Excel", "Sales"],
     ["Kolkata", "Any"], ["Retail & FMCG"], "West Bengal", 0, 1, 12),
    ("Deepak Yadav", "12th Pass", 1, ["Data Entry", "Communication"],
     ["Lucknow"], ["Retail & FMCG", "Banking & Finance"], "Uttar Pradesh", 1, 3, 12),
    ("Meghana Reddy", "BPharm", 3, ["Lab Techniques", "Documentation", "Quality Control"],
     ["Hyderabad", "Visakhapatnam"], ["Healthcare & Pharma"], "Andhra Pradesh", 0, 2, 12),
    ("Harpreet Singh Gill", "BTech Electrical", 3, ["Electrical Systems", "Solar PV", "AutoCAD"],
     ["Any"], ["Energy"], "Haryana", 0, 2, 12),
    ("Ritika Agarwal", "BBA", 3, ["Sales", "Customer Service", "Inventory Management"],
     ["Indore"], ["Retail & FMCG"], "Madhya Pradesh", 1, 3, 12),
    ("Mohammed Faisal", "Diploma", 2, ["PLC Programming", "Maintenance", "Quality Control"],
     ["Chennai"], ["Manufacturing"], "Tamil Nadu", 1, 3, 12),
    ("Shruti Kulkarni", "MSc", 4, ["Chemistry", "Lab Techniques", "Regulatory Compliance"],
     ["Mumbai", "Pune"], ["Healthcare & Pharma"], "Maharashtra", 0, 1, 12),
    ("Aniket Patil", "BTech CSE", 3, ["JavaScript", "React", "REST APIs"],
     ["Pune"], ["IT & Software"], "Maharashtra", 1, 2, 12),
    ("Divya Krishnan", "BCom", 3, ["Financial Analysis", "Excel", "Risk Analysis"],
     ["Bengaluru", "Chennai"], ["Banking & Finance"], "Karnataka", 0, 2, 12),
    ("Sunil Murmu", "12th Pass", 1, ["Field Operations", "Safety Compliance"],
     ["Bhubaneswar"], ["Energy", "Manufacturing"], "Odisha", 1, 3, 12),
    ("Ishita Malhotra", "MBA", 4, ["Marketing", "Supply Chain", "Data Analysis"],
     ["Delhi", "Gurugram"], ["Retail & FMCG"], "Delhi", 0, 1, 12),
    ("Karthik Iyer", "MTech", 4, ["Machine Learning", "Python", "Data Analysis", "Cloud Computing"],
     ["Bengaluru", "Hyderabad"], ["IT & Software"], "Karnataka", 0, 1, 12),
    ("Pooja Bhatt", "BSc", 3, ["Biology", "Lab Techniques", "Data Entry"],
     ["Ahmedabad"], ["Healthcare & Pharma"], "Gujarat", 1, 3, 12),
    ("Ramesh Kumar Das", "Diploma", 2, ["Electrical Systems", "Maintenance"],
     ["Patna", "Any"], ["Energy"], "Bihar", 1, 3, 12),
    ("Neelam Verma", "BA", 3, ["Communication", "Customer Service", "Data Entry"],
     ["Lucknow", "Delhi"], ["Retail & FMCG", "Banking & Finance"], "Uttar Pradesh", 1, 3, 12),
    ("Tenzin Dorjee", "BSc", 3, ["Data Analysis", "Excel", "Communication"],
     ["Guwahati", "Any"], ["IT & Software", "Banking & Finance"], "Assam", 1, 2, 12),
    ("Farhana Begum", "BPharm", 3, ["Documentation", "Regulatory Compliance", "Quality Control"],
     ["Kolkata"], ["Healthcare & Pharma"], "West Bengal", 1, 2, 12),
    ("Gaurav Saini", "BTech Mechanical", 3, ["AutoCAD", "SolidWorks", "Safety Compliance"],
     ["Jaipur", "Gurugram"], ["Manufacturing", "Energy"], "Rajasthan", 0, 3, 12),
    ("Lakshmi Pillai", "BBA", 3, ["Sales", "Marketing", "Excel", "Communication"],
     ["Chennai", "Coimbatore"], ["Retail & FMCG"], "Tamil Nadu", 0, 2, 12),
]


def make_students(n: int = 200) -> list[dict]:
    students = []
    for name, qual, level, skills, locs, sectors, state, fg, tier, months in CURATED_STUDENTS:
        i = len(students) + 1
        email = name.lower().replace(" ", ".").replace("'", "") + "@example.in"
        students.append({
            "id": i, "name": name, "email": email,
            "qualification": qual, "qualification_level": level,
            "skills": skills, "preferred_locations": locs,
            "preferred_sectors": sectors, "home_state": state,
            "first_generation": fg, "college_tier": tier,
            "available_months": months,
        })
    for i in range(len(students) + 1, n + 1):
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


ASSESSMENT_STAGES = [
    ["Online Aptitude Test", "HR Interview"],
    ["Resume Shortlist", "Technical Test", "Panel Interview"],
    ["Profile Screening", "Group Discussion", "Final Interview"],
    ["Online Test", "Technical Interview", "HR Round"],
]

COMPANY_ABOUT = {
    "default": "{company} is a registered partner company under the PM Internship "
               "Scheme, offering structured 12-month internships with mentorship, "
               "on-the-job training and a monthly assistance of Rs 5,000.",
}


# Curated internships that pair naturally with the curated student profiles.
# Format: title, company, sector, city, state, skills, min_qual, capacity, verified
CURATED_INTERNSHIPS = [
    ("Software Development Intern", "TCS", "IT & Software", "Pune", "Maharashtra",
     ["Python", "SQL", "Git", "REST APIs"], 3, 6, 1),
    ("Data Analytics Intern", "Infosys", "IT & Software", "Bengaluru", "Karnataka",
     ["Python", "Data Analysis", "SQL", "Machine Learning"], 3, 5, 1),
    ("Cloud Support Intern", "Wipro", "IT & Software", "Chennai", "Tamil Nadu",
     ["Cloud Computing", "REST APIs", "Data Analysis"], 3, 4, 1),
    ("Banking Operations Intern", "HDFC Bank", "Banking & Finance", "Hyderabad", "Telangana",
     ["Accounting", "Tally", "Excel", "Data Entry"], 3, 6, 1),
    ("Finance Analyst Intern", "ICICI Bank", "Banking & Finance", "Bengaluru", "Karnataka",
     ["Financial Analysis", "Excel", "Risk Analysis"], 3, 4, 1),
    ("Quality Assurance Intern", "Tata Motors", "Manufacturing", "Pune", "Maharashtra",
     ["Quality Control", "Lean Manufacturing", "SolidWorks"], 2, 5, 1),
    ("Maintenance Engineering Intern", "Larsen & Toubro", "Manufacturing", "Jaipur", "Rajasthan",
     ["AutoCAD", "Maintenance", "Safety Compliance"], 2, 4, 1),
    ("Renewable Energy Intern", "Adani Green", "Energy", "Ahmedabad", "Gujarat",
     ["Solar PV", "Electrical Systems", "Field Operations"], 2, 5, 1),
    ("Pharma QC Intern", "Sun Pharma", "Healthcare & Pharma", "Hyderabad", "Telangana",
     ["Lab Techniques", "Quality Control", "Documentation"], 3, 5, 1),
    ("Sales & Marketing Intern", "Hindustan Unilever", "Retail & FMCG", "Kolkata", "West Bengal",
     ["Sales", "Marketing", "Communication", "Excel"], 3, 6, 1),
]


def make_internships(n: int = 120) -> list[dict]:
    internships = []
    for title, company, sector, city, state, skills, minq, cap, ver in CURATED_INTERNSHIPS:
        i = len(internships) + 1
        internships.append({
            "id": i, "title": title, "company": company, "sector": sector,
            "location": city, "state": state, "skills_required": skills,
            "min_qualification_level": minq, "duration_months": 12,
            "stipend": 5000, "capacity": cap, "verified": ver,
            "description": f"{title} at {company}, {city}. Work on {', '.join(skills[:3])} "
                           f"under the PM Internship Scheme. 12-month engagement with "
                           f"monthly assistance of Rs 5,000.",
            "company_about": COMPANY_ABOUT["default"].format(company=company),
            "assessment_stages": rng.choice(ASSESSMENT_STAGES),
        })
    for i in range(len(internships) + 1, n + 1):
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
            "company_about": COMPANY_ABOUT["default"].format(company=company),
            "assessment_stages": rng.choice(ASSESSMENT_STAGES),
        })
    return internships


def seed() -> None:
    init_db()
    with get_conn() as conn:
        conn.execute("DELETE FROM allocations")
        conn.execute("DELETE FROM applications")
        conn.execute("DELETE FROM sessions")
        conn.execute("DELETE FROM users")
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
                "INSERT INTO internships VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (j["id"], j["title"], j["company"], j["sector"], j["location"],
                 j["state"], json.dumps(j["skills_required"]),
                 j["min_qualification_level"], j["duration_months"], j["stipend"],
                 j["capacity"], j["verified"], j["description"],
                 j["company_about"], json.dumps(j["assessment_stages"])),
            )
        sync_sequences(conn)
    print("Seeded 200 students (25 curated + 175 generated) and 120 internships.")


if __name__ == "__main__":
    seed()
