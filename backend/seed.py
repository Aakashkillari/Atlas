"""Seed data: real PMIS-participating companies + internship listings.

NO synthetic students: students register through real signup only.
Company names are genuine PM Internship Scheme participants, sourced from
PIB press releases and news coverage of the scheme (top-500-by-CSR cohort).
Each seeded company gets a demo login: hr@<slug>.example.in / company@1234
"""
import json
import random
from datetime import datetime, timezone

import auth
from database import get_conn, init_db, sync_sequences

rng = random.Random(25033)

# (name, sector, cities[(city,state)]) - real PMIS participant companies per PIB/news
REAL_COMPANIES = [
    ("Tata Consultancy Services", "IT & Software", [("Pune", "Maharashtra"), ("Chennai", "Tamil Nadu"), ("Hyderabad", "Telangana")]),
    ("Infosys", "IT & Software", [("Bengaluru", "Karnataka"), ("Pune", "Maharashtra")]),
    ("Wipro", "IT & Software", [("Bengaluru", "Karnataka"), ("Chennai", "Tamil Nadu")]),
    ("HCLTech", "IT & Software", [("Chennai", "Tamil Nadu"), ("Lucknow", "Uttar Pradesh")]),
    ("Tech Mahindra", "IT & Software", [("Pune", "Maharashtra"), ("Hyderabad", "Telangana")]),
    ("HDFC Bank", "Banking & Finance", [("Mumbai", "Maharashtra"), ("Delhi", "Delhi")]),
    ("ICICI Bank", "Banking & Finance", [("Mumbai", "Maharashtra"), ("Ahmedabad", "Gujarat")]),
    ("State Bank of India", "Banking & Finance", [("Mumbai", "Maharashtra"), ("Kolkata", "West Bengal")]),
    ("Bajaj Finserv", "Banking & Finance", [("Pune", "Maharashtra")]),
    ("Max Life Insurance", "Banking & Finance", [("Gurugram", "Haryana"), ("Delhi", "Delhi")]),
    ("Larsen & Toubro", "Manufacturing", [("Mumbai", "Maharashtra"), ("Chennai", "Tamil Nadu")]),
    ("Maruti Suzuki", "Manufacturing", [("Gurugram", "Haryana")]),
    ("Mahindra & Mahindra", "Manufacturing", [("Mumbai", "Maharashtra"), ("Nagpur", "Maharashtra")]),
    ("Eicher Motors", "Manufacturing", [("Chennai", "Tamil Nadu"), ("Indore", "Madhya Pradesh")]),
    ("Tata Motors", "Manufacturing", [("Pune", "Maharashtra"), ("Jamshedpur", "Jharkhand")]),
    ("JSW Steel", "Manufacturing", [("Mumbai", "Maharashtra"), ("Bellary", "Karnataka")]),
    ("NTPC", "Energy", [("Delhi", "Delhi"), ("Patna", "Bihar")]),
    ("ONGC", "Energy", [("Dehradun", "Uttarakhand"), ("Mumbai", "Maharashtra")]),
    ("Adani Green Energy", "Energy", [("Ahmedabad", "Gujarat"), ("Jaipur", "Rajasthan")]),
    ("Tata Power", "Energy", [("Mumbai", "Maharashtra")]),
    ("Sun Pharma", "Healthcare & Pharma", [("Mumbai", "Maharashtra"), ("Vadodara", "Gujarat")]),
    ("Cipla", "Healthcare & Pharma", [("Mumbai", "Maharashtra"), ("Goa", "Goa")]),
    ("Alembic Pharmaceuticals", "Healthcare & Pharma", [("Vadodara", "Gujarat")]),
    ("Dr. Reddy's Laboratories", "Healthcare & Pharma", [("Hyderabad", "Telangana")]),
    ("Hindustan Unilever", "Retail & FMCG", [("Mumbai", "Maharashtra"), ("Kolkata", "West Bengal")]),
    ("ITC", "Retail & FMCG", [("Kolkata", "West Bengal"), ("Bengaluru", "Karnataka")]),
    ("Jubilant FoodWorks", "Retail & FMCG", [("Noida", "Uttar Pradesh"), ("Bengaluru", "Karnataka")]),
    ("Reliance Retail", "Retail & FMCG", [("Mumbai", "Maharashtra"), ("Ahmedabad", "Gujarat")]),
    ("Marico", "Retail & FMCG", [("Mumbai", "Maharashtra")]),
    ("Dabur", "Retail & FMCG", [("Ghaziabad", "Uttar Pradesh")]),
]

SECTOR_SKILLS = {
    "IT & Software": ["Python", "Java", "JavaScript", "React", "SQL", "Data Analysis",
                      "Machine Learning", "Cloud Computing", "Git", "REST APIs"],
    "Banking & Finance": ["Accounting", "Excel", "Financial Analysis", "Tally",
                          "Data Entry", "Communication", "SQL", "Risk Analysis"],
    "Manufacturing": ["AutoCAD", "SolidWorks", "Quality Control", "Lean Manufacturing",
                      "Safety Compliance", "Maintenance", "PLC Programming"],
    "Energy": ["Electrical Systems", "Solar PV", "AutoCAD", "Safety Compliance",
               "Field Operations", "Data Analysis"],
    "Healthcare & Pharma": ["Lab Techniques", "Quality Control", "Documentation",
                            "Biology", "Chemistry", "Data Entry", "Regulatory Compliance"],
    "Retail & FMCG": ["Sales", "Communication", "Inventory Management", "Excel",
                      "Marketing", "Customer Service", "Supply Chain"],
}

SECTOR_ROLES = {
    "IT & Software": ["Software Development Intern", "Data Analytics Intern",
                      "QA Engineering Intern", "Cloud Support Intern"],
    "Banking & Finance": ["Banking Operations Intern", "Finance Analyst Intern",
                          "Audit Support Intern"],
    "Manufacturing": ["Production Intern", "Quality Assurance Intern",
                      "Maintenance Engineering Intern"],
    "Energy": ["Renewable Energy Intern", "Electrical Operations Intern"],
    "Healthcare & Pharma": ["Pharma QC Intern", "Clinical Data Intern",
                            "Lab Operations Intern"],
    "Retail & FMCG": ["Sales & Marketing Intern", "Supply Chain Intern",
                      "Store Operations Intern"],
}

ASSESSMENT_STAGES = [
    ["Online Aptitude Test", "HR Interview"],
    ["Resume Shortlist", "Technical Test", "Panel Interview"],
    ["Profile Screening", "Group Discussion", "Final Interview"],
    ["Online Test", "Technical Interview", "HR Round"],
]

ABOUT = ("{company} is a partner company under the PM Internship Scheme, offering "
         "structured 12-month internships with mentorship, on-the-job training and "
         "a monthly assistance of Rs 5,000.")


def slug(name: str) -> str:
    return "".join(c for c in name.lower().replace("&", "and") if c.isalnum())[:20]


def seed() -> None:
    init_db()
    now = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        for table in ("allocations", "applications", "sessions", "users",
                      "documents", "notifications", "complaints",
                      "students", "internships", "companies"):
            conn.execute(f"DELETE FROM {table}")

        company_ids = {}
        for name, sector, _cities in REAL_COMPANIES:
            conn.execute(
                "INSERT INTO companies (name, sector, about, status, created_at)"
                " VALUES (?,?,?,?,?)",
                (name, sector, ABOUT.format(company=name), "Active", now))
        for row in conn.execute("SELECT id, name FROM companies"):
            company_ids[row["name"]] = row["id"]

        n_internships = 0
        for name, sector, cities in REAL_COMPANIES:
            for _ in range(rng.randint(3, 5)):
                city, state = rng.choice(cities)
                role = rng.choice(SECTOR_ROLES[sector])
                skills = rng.sample(SECTOR_SKILLS[sector], k=rng.randint(3, 5))
                verified = 1 if rng.random() < 0.8 else 0
                conn.execute(
                    "INSERT INTO internships (title, company, sector, location,"
                    " state, skills_required, min_qualification_level,"
                    " duration_months, stipend, capacity, verified, description,"
                    " company_about, assessment_stages, company_id, status)"
                    " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (role, name, sector, city, state, json.dumps(skills),
                     rng.choices([1, 2, 3], weights=[2, 3, 5])[0], 12, 5000,
                     rng.randint(2, 8), verified,
                     f"{role} at {name}, {city}. Work on {', '.join(skills[:3])} "
                     f"under the PM Internship Scheme. 12-month engagement with "
                     f"monthly assistance of Rs 5,000.",
                     ABOUT.format(company=name), json.dumps(rng.choice(ASSESSMENT_STAGES)),
                     company_ids[name], "Verified" if verified else "Pending"))
                n_internships += 1
        sync_sequences(conn)

    # demo company logins (created via normal auth so hashes are real)
    for name, _sector, _cities in REAL_COMPANIES:
        email = f"hr@{slug(name)}.example.in"
        try:
            auth.company_signup(name, _sector, email, "company@1234")
        except ValueError:
            pass

    print(f"Seeded {len(REAL_COMPANIES)} real PMIS companies, {n_internships} "
          f"internships, 0 students (students register themselves).")
    print("Company demo logins: hr@<companyslug>.example.in / company@1234 "
          "(e.g. hr@tataconsultancyserv.example.in)")


if __name__ == "__main__":
    seed()
