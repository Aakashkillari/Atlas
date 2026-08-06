"""Stage 4 — Optimal allocation via the Hungarian algorithm.

Each internship is expanded into `capacity` slots; the assignment problem is
solved globally so the overall allocation quality is maximised across the
entire pool — no "first come, best match wins" bias.
"""
import numpy as np
from scipy.optimize import linear_sum_assignment

INELIGIBLE = -1e6  # blocks a pairing that failed the hard gate


def solve(students: list[dict], internships: list[dict],
          score_lookup: dict[tuple[int, int], float]) -> list[tuple[int, int]]:
    """score_lookup: (student_id, internship_id) -> total score.
    Pairs absent from the lookup are ineligible. Returns (student_id, internship_id).
    """
    slots: list[int] = []  # slot index -> internship id
    for j in internships:
        slots.extend([j["id"]] * j["capacity"])

    cost = np.full((len(students), len(slots)), -INELIGIBLE)
    for si, s in enumerate(students):
        for ji, j_id in enumerate(slots):
            score = score_lookup.get((s["id"], j_id))
            if score is not None:
                cost[si, ji] = -score  # maximise score == minimise negative

    rows, cols = linear_sum_assignment(cost)
    return [
        (students[r]["id"], slots[c])
        for r, c in zip(rows, cols)
        if (students[r]["id"], slots[c]) in score_lookup
    ]
