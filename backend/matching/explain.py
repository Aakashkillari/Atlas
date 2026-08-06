"""Template-based plain-language explanations (deterministic, offline-safe).

An LLM-generated variant can be dropped in later behind the same function
signature — templates stay the default so the demo never depends on a
network call.
"""


def _band(score: float, high: str, mid: str, low: str) -> str:
    if score >= 0.7:
        return high
    if score >= 0.4:
        return mid
    return low


def explain(student: dict, internship: dict, scores: dict) -> str:
    parts = [_band(
        scores["skill_score"],
        f"Strong skill alignment with the {internship['title']} role",
        f"Moderate skill overlap with the {internship['title']} role",
        f"Limited direct skill overlap, but eligibility criteria are met",
    )]

    matched = sorted(set(map(str.lower, student["skills"]))
                     & set(map(str.lower, internship["skills_required"])))
    if matched:
        parts.append(f"directly matching on {', '.join(matched[:3])}")

    parts.append(_band(
        scores["location_score"],
        f"{internship['location']} is a preferred location",
        f"{internship['location']} is within reach of their home state",
        f"location ({internship['location']}) is outside stated preferences",
    ))

    if scores["sector_score"] >= 1.0:
        parts.append(f"and {internship['sector']} is their preferred sector")

    if scores["fairness_boost"] > 1.0:
        parts.append("(equity uplift applied per the scheme's affirmative-action mandate)")

    return ". ".join(p[0].upper() + p[1:] for p in parts) + "."
