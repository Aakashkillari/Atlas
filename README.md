# ATLAS — AI-Based Smart Allocation for the PM Internship Scheme

**SIH25033** · Smart India Hackathon

> Every existing solution treats this as a listing problem. ATLAS treats it as what it
> actually is: a **matching, fairness, and trust problem** — rules first, ranking second.

## The four-stage matching pipeline

| Stage | What it does | Where |
|---|---|---|
| 1. Hard-filter gate | Policy rules (qualification, duration, location willingness) run **before** any AI | `backend/matching/filters.py` |
| 2. Semantic matching | TF-IDF + cosine similarity over skills — meaning, not keywords | `backend/matching/embeddings.py` |
| 3. Fairness-weighted scoring | 0.6·skill + 0.2·location + 0.2·sector, with an equity uplift for first-generation / tier-2-3 students (the brief's affirmative-action mandate) | `backend/matching/scoring.py` |
| 4. Optimal allocation | Hungarian algorithm solves the whole pool at once — no first-come bias | `backend/matching/allocate.py` |

Plus: **template-based explanations** for every match (`explain.py`), a **cold-start
fallback** for thin profiles, **verified-employer badges**, and a searchable, paginated
tricolor dashboard.

## Run it

```bash
pip install -r requirements.txt
cd backend
python seed.py          # 200 students, 50 internships (deterministic)
uvicorn app:app --reload
```

Open **http://127.0.0.1:8000** — Student Portal for browsing + personalised explained
matches; Admin tab to run the full Hungarian allocation and inspect every score breakdown.

## API

- `GET /api/internships?search=&page=&page_size=` — search + pagination
- `GET /api/students` · `GET /api/students/{id}`
- `GET /api/students/{id}/recommendations` — top-N with sub-scores, explanation, cold-start fallback
- `POST /api/allocate` — run the full pipeline; `GET /api/allocation` — last result

## Production path (demo → real)

- SQLite → **PostgreSQL + pgvector** (same cosine metric, `<=>` operator)
- TF-IDF → **sentence-transformer embeddings**
- Template explanations → optional **LLM-generated** explanations (same function signature)
- Static frontend → React (design handoff pending)
