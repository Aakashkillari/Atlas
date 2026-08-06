"""Stage 1 — Hard-filter eligibility gate.

Rules run BEFORE any AI scoring. A pair that fails here never reaches the
ranking stage, mirroring how a real government allocation system must work:
policy rules first, AI second.
"""


def is_eligible(student: dict, internship: dict) -> bool:
    if student["qualification_level"] < internship["min_qualification_level"]:
        return False
    if student["available_months"] < internship["duration_months"]:
        return False
    prefs = student["preferred_locations"]
    if "Any" not in prefs:
        # willing if the city is preferred, or it is in their home state
        if internship["location"] not in prefs and internship["state"] != student["home_state"]:
            return False
    return True


def eligible_pairs(students: list[dict], internships: list[dict]) -> dict[int, list[int]]:
    """Map student id -> list of internship ids that pass the hard gate."""
    return {
        s["id"]: [j["id"] for j in internships if is_eligible(s, j)]
        for s in students
    }
