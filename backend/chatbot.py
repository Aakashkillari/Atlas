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
     "Open any internship card and press Apply Now. You can apply to as many "
     "internships as you like and track every status in My Applications."),
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


def answer(query: str, internships: list[dict], student: dict | None = None,
           applications: list[dict] | None = None,
           recommender=None) -> dict:
    q = query.strip().lower()
    if not q or re.fullmatch(r"(hi|hello|hey|namaste|vanakkam|help)[!. ]*", q):
        greeting = GREETING
        if student:
            greeting = (f"Namaste {student['name'].split(' ')[0]}! " + GREETING)
        return {"reply": greeting, "internships": []}

    # ---- personalised intents (need a signed-in / selected student) ----
    if student:
        if re.search(r"\b(recommend|suggest|for me|best (job|internship)|"
                     r"match(es)? for me|jobs? for me|internships? for me)\b", q):
            if recommender is None:
                return {"reply": "Recommendations are unavailable right now.", "internships": []}
            rec = recommender(student)
            if rec["cold_start"] or not rec["recommendations"]:
                return {"reply": f"{student['name'].split(' ')[0]}, your profile needs a few "
                                 "more skills before I can match you reliably. Open Profile "
                                 "and add your skills, then ask me again!", "internships": []}
            lines = []
            ids = []
            for r in rec["recommendations"][:3]:
                j = r["internship"]
                ids.append(j["id"])
                lines.append(f"{j['title']} at {j['company']} ({j['location']}, "
                             f"{round(r['total_score'] * 100)}% match)")
            return {"reply": f"Based on your profile ({', '.join(student['skills'][:3])}), "
                             f"my top matches for you: " + "; ".join(lines) +
                             ". Open the Dashboard for the full reasoning and to apply.",
                    "internships": ids}

        if re.search(r"\b(my profile|about me|who am i|my details|my skills)\b", q):
            return {"reply": f"Here is what I know: {student['name']}, {student['qualification']}, "
                             f"skills {', '.join(student['skills']) or 'none listed'}, prefers "
                             f"{', '.join(student['preferred_locations'])} in "
                             f"{', '.join(student['preferred_sectors']) or 'any sector'}."
                             + (" You qualify for the scheme's equity uplift."
                                if student["first_generation"] or student["college_tier"] >= 2 else ""),
                    "internships": []}

        if re.search(r"\b(my application|my status|my offer|track|applied|"
                     r"application status|status of)\b", q) \
                or re.search(r"\b(which|what|how many)\b.*\bappl", q):
            if not applications:
                return {"reply": "You have not applied to any internships yet. Apply "
                                 "from the Dashboard or Explore Internships; there is "
                                 "no cap on applications.",
                        "internships": []}
            lines = [f"{a['internship']['title']} at {a['internship']['company']} "
                     f"({a['internship']['location']}): {a['status']}"
                     for a in applications[:6]]
            companies = sorted({a["internship"]["company"] for a in applications})
            offers = sum(1 for a in applications if a["status"] == "Offer Sent")
            accepted = sum(1 for a in applications if a["status"] == "Accepted")
            extra = ""
            if offers:
                extra += f" You have {offers} offer(s) awaiting your response."
            if accepted:
                extra += " Congratulations on your accepted offer!"
            return {"reply": f"You have applied to {len(applications)} internship(s) "
                             f"across {', '.join(companies)}. Details: "
                             + "; ".join(lines) + "." + extra,
                    "internships": [a["internship"]["id"] for a in applications[:5]]}

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
