"""Stage 3 — Composite scoring with fairness weighting.

total = (0.6*skill + 0.2*location + 0.2*sector) * fairness_boost

The fairness boost implements the affirmative-action requirement in the
official SIH25033 brief: first-generation applicants and tier-2/3 college
students receive a small multiplicative lift so a strong-fit student is not
buried by a thinner, less keyword-rich profile.
"""

WEIGHTS = {"skill": 0.6, "location": 0.2, "sector": 0.2}
FIRST_GEN_BOOST = 0.05
TIER_BOOST = {1: 0.0, 2: 0.03, 3: 0.05}


def location_score(student: dict, internship: dict) -> float:
    prefs = student["preferred_locations"]
    if internship["location"] in prefs:
        return 1.0
    if "Any" in prefs:
        return 0.8
    if internship["state"] == student["home_state"]:
        return 0.6
    return 0.2


def sector_score(student: dict, internship: dict) -> float:
    return 1.0 if internship["sector"] in student["preferred_sectors"] else 0.3


def fairness_boost(student: dict) -> float:
    boost = 1.0 + TIER_BOOST[student["college_tier"]]
    if student["first_generation"]:
        boost += FIRST_GEN_BOOST
    return boost


def composite(student: dict, internship: dict, skill_sim: float) -> dict:
    loc = location_score(student, internship)
    sec = sector_score(student, internship)
    boost = fairness_boost(student)
    raw = WEIGHTS["skill"] * skill_sim + WEIGHTS["location"] * loc + WEIGHTS["sector"] * sec
    return {
        "skill_score": round(float(skill_sim), 4),
        "location_score": round(loc, 4),
        "sector_score": round(sec, 4),
        "fairness_boost": round(boost, 4),
        "total_score": round(min(raw * boost, 1.0), 4),
    }
