"""Orchestrates the four-stage pipeline:

  1. hard-filter gate  ->  2. semantic scoring  ->  3. fairness weighting
  ->  4. Hungarian allocation

Also provides per-student recommendations with the cold-start fallback.
"""
from . import allocate, explain, filters, scoring
from .embeddings import skill_similarity_matrix

COLD_START_MIN_SKILLS = 2


def _score_all(students: list[dict], internships: list[dict]):
    """Return score_lookup and detail_lookup for all eligible pairs."""
    eligible = filters.eligible_pairs(students, internships)
    sim = skill_similarity_matrix(students, internships)
    j_index = {j["id"]: idx for idx, j in enumerate(internships)}
    j_by_id = {j["id"]: j for j in internships}

    score_lookup: dict[tuple[int, int], float] = {}
    detail_lookup: dict[tuple[int, int], dict] = {}
    for si, s in enumerate(students):
        for j_id in eligible[s["id"]]:
            detail = scoring.composite(s, j_by_id[j_id], sim[si, j_index[j_id]])
            score_lookup[(s["id"], j_id)] = detail["total_score"]
            detail_lookup[(s["id"], j_id)] = detail
    return score_lookup, detail_lookup


def run_allocation(students: list[dict], internships: list[dict]) -> list[dict]:
    score_lookup, detail_lookup = _score_all(students, internships)
    pairs = allocate.solve(students, internships, score_lookup)
    s_by_id = {s["id"]: s for s in students}
    j_by_id = {j["id"]: j for j in internships}

    results = []
    for s_id, j_id in pairs:
        detail = detail_lookup[(s_id, j_id)]
        results.append({
            "student_id": s_id,
            "internship_id": j_id,
            **detail,
            "explanation": explain.explain(s_by_id[s_id], j_by_id[j_id], detail),
        })
    results.sort(key=lambda r: r["total_score"], reverse=True)
    return results


def recommend(student: dict, students: list[dict], internships: list[dict],
              top_n: int = 5) -> dict:
    """Top-N matches for one student; popularity fallback for thin profiles."""
    if len(student["skills"]) < COLD_START_MIN_SKILLS:
        pool = [j for j in internships if filters.is_eligible(student, j)] or internships
        pool.sort(key=lambda j: (j["sector"] in student["preferred_sectors"],
                                 j["verified"], j["capacity"]), reverse=True)
        return {
            "cold_start": True,
            "reason": "Profile has too few skills for reliable semantic matching; "
                      "showing popular, verified internships in preferred sectors instead.",
            "recommendations": [{"internship_id": j["id"]} for j in pool[:top_n]],
        }

    score_lookup, detail_lookup = _score_all([student], internships)
    j_by_id = {j["id"]: j for j in internships}
    ranked = sorted(score_lookup.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
    return {
        "cold_start": False,
        "recommendations": [
            {
                "internship_id": j_id,
                **detail_lookup[(s_id, j_id)],
                "explanation": explain.explain(student, j_by_id[j_id],
                                               detail_lookup[(s_id, j_id)]),
            }
            for (s_id, j_id), _ in ranked
        ],
    }
