"""Retrieval-based chatbot (trial version, no LLM).

RAG-style: retrieve matching internships / FAQ entries from the database as
context, then answer from templates. The LLM upgrade later swaps only the
answer-composition step; retrieval stays identical.
"""
import re

FAQ = [
    (r"\b(stipend|salary|pay|money|amount)\b",
     "Interns under the PM Internship Scheme receive Rs 5,000 per month as "
     "assistance, plus a one-time grant of Rs 6,000 on joining."),
    (r"\b(eligib|who can|criteria|age)\b",
     "Youth aged 21-24 who are not in full-time employment or full-time "
     "education are eligible. Qualification requirements vary per internship "
     "and are checked automatically by ATLAS before matching."),
    (r"\b(duration|how long|months|period)\b",
     "PM Internship Scheme internships run for 12 months. ATLAS checks your "
     "availability before recommending a role."),
    (r"\b(apply|application|how do i|limit)\b",
     "You can hold up to 3 active applications at a time. Open any internship "
     "card and press Apply Now. You can track status in My Applications."),
    (r"\b(offer|accept|deadline|window)\b",
     "Once an offer is made you have 14 days to accept it. You can hold a "
     "maximum of 2 active offers at a time."),
    (r"\b(verified|trust|genuine|fake|scam)\b",
     "Listings with a green Verified Employer badge are curated trust signals "
     "checked against company registration data. Prefer verified listings."),
    (r"\b(match|score|percent|why|reason)\b",
     "Your match percentage combines skill similarity (60%), location fit "
     "(20%) and sector fit (20%), with an equity uplift per the scheme's "
     "affirmative-action policy. Open View Match Reasoning on any card for "
     "the full breakdown."),
]

GREETING = ("Namaste! I am the ATLAS assistant. Ask me about internships "
            "(for example: 'Python internships in Pune'), stipend, eligibility, "
            "application limits, or how matching works.")


def _search_internships(query: str, internships: list[dict], limit: int = 3) -> list[dict]:
    words = [w for w in re.findall(r"[a-z]+", query.lower()) if len(w) > 2]
    scored = []
    for j in internships:
        haystack = " ".join([j["title"], j["company"], j["sector"], j["location"],
                             j["state"], " ".join(j["skills_required"])]).lower()
        hits = sum(1 for w in words if w in haystack)
        if hits:
            scored.append((hits, j))
    scored.sort(key=lambda t: (-t[0], -t[1]["verified"]))
    return [j for _, j in scored[:limit]]


def answer(query: str, internships: list[dict]) -> dict:
    q = query.strip().lower()
    if not q or re.fullmatch(r"(hi|hello|hey|namaste|help)[!. ]*", q):
        return {"reply": GREETING, "internships": []}

    for pattern, reply in FAQ:
        if re.search(pattern, q):
            return {"reply": reply, "internships": []}

    found = _search_internships(q, internships)
    if found:
        lines = [f"{j['title']} at {j['company']} ({j['location']}, "
                 f"Rs {j['stipend']}/month)" for j in found]
        return {
            "reply": "Here is what I found in the current listings: "
                     + "; ".join(lines)
                     + ". Open Explore Internships to view details and apply.",
            "internships": [j["id"] for j in found],
        }
    return {
        "reply": "I could not find matching internships for that. Try skill or "
                 "city keywords (for example 'AutoCAD Pune'), or ask about "
                 "stipend, eligibility, offers, or how matching works.",
        "internships": [],
    }
