# ATLAS — Complete Pitch Brief
**SIH25033 · AI-Based Smart Allocation Engine for the PM Internship Scheme · Ministry of Corporate Affairs**

> ATLAS: **AI-Driven Talent Linking & Allocation System**
> Tagline: *The Weight of Talent, Rightly Placed.*

---

## 1. The one-liner

> "The government isn't short of internships — it loses 9 out of 10 students between 'applied' and 'joined'. That's not a listings problem, it's a matching problem. ATLAS solves allocation, not recommendation."

## 2. The problem (memorize these numbers)

| Stage | National figure |
|---|---|
| Opportunities posted | **1.27 lakh** |
| Applications received | **6.21 lakh** |
| Offers made | **82,000+** |
| Offers accepted | **28,000+** |
| Actually joined | **~8,700** |
| Real conversion | **~11%** |

Why students drop out (government-acknowledged): location mismatch, 12-month duration vs semester life, role mismatch, expectation mismatch, process friction (e-KYC, offer windows), no discovery guidance, no trust signals. The official brief **mandates affirmative action** — fairness is a requirement, not a feature.

**Live proof:** our Live Data dashboard pulls these figures from data.gov.in in real time — profiles **3,38,115** → opportunities **1,27,508** → offers **82,077** → accepted **28,141**. The government's own open data confirms the funnel on stage.

---

## 3. What ATLAS is

Three portals on one platform, one shared database:

| URL | Who | What they do |
|---|---|---|
| `/student` | Students (self signup, email + mandatory mobile) | Profile (form or chat assistant or resume upload), AI recommendations with explanations, unlimited applications, offer accept/decline, notifications, documents, skill analytics, FAQ + grievances, multilingual UI (EN/हिन्दी/தமிழ்), personalized chatbot |
| `/company` | Companies (individual sign-ins; 30 real PMIS participants seeded) | Post internships (admin-verified), view applicants with computed match %, skills, mobile, resume; shortlist → offer → track acceptance |
| `/admin` | Single fixed credential | Approve/reject new companies, verify/suspend listings, run the allocation engine, allocation results, **Fairness audit tab**, all students/applications, grievance resolution, Live Data dashboard |

**The connected flow (this is the 3-minute demo):**
Company posts → listing "Pending" → Admin verifies → badge appears → Student gets recommended, applies (resume attached) → Company's bell rings → shortlists → sends offer → Student's bell rings, accepts within the 14-day window → Admin runs the allocation engine over everyone → Fairness tab shows the equity audit.

---

## 4. The matching pipeline (the core IP)

**Rules first → semantic similarity → fairness weighting → global optimization → plain-language explanation.**

### Stage 1 — Hard-filter gate (`backend/matching/filters.py`)
Pure deterministic rules run **before any AI**: qualification level, duration availability, location willingness (preferred city, home state, or "Any"), capacity. A pair that fails never reaches scoring. This mirrors how government allocation must work — policy is not negotiable by a model.

### Stage 2 — Semantic skill matching (`backend/matching/embeddings.py`)
TF-IDF vectorization with **character n-grams (3–5)** over skill text, compared by **cosine similarity**. N-grams make "Data Analysis" ≈ "Data Analytics" without exact keyword overlap. Deterministic, fast, fully explainable. Production upgrade path: sentence-transformer embeddings in **pgvector** — same cosine metric, one module swapped.

### Stage 3 — Fairness-weighted composite scoring (`backend/matching/scoring.py`)
`total = (0.6·skill + 0.2·location + 0.2·sector) × fairness_boost`
Boost: **+5% first-generation**, **+3% tier-2 / +5% tier-3 college**. Never negative — nobody's score is ever reduced. Implements the brief's affirmative-action mandate. All weights are policy parameters, not hard-coded magic.

### Stage 4 — Hungarian algorithm allocation (`backend/matching/allocate.py`)
Internships expand into capacity slots; `scipy.optimize.linear_sum_assignment` (Kuhn–Munkres) solves the **entire student × seat matrix simultaneously** for the globally optimal assignment. No first-come-first-served bias: one student may get their #2 so three others get their #1.

### Stage 5 — Explanation (`backend/matching/explain.py`)
Template-generated from the actual sub-scores: *"Strong on Python, SQL. Gap on Cloud Computing. Pune is a preferred location. Equity uplift applied per the scheme's affirmative-action mandate."* Deterministic — an LLM never invents reasoning about scores.

**Supporting intelligence:** cold-start fallback (thin profiles get eligible, popular, verified listings instead of noisy similarity), resume skill extraction (pypdf + skill vocabulary → one-click "add to profile"), retrieval-based chatbot grounded in the signed-in student's own profile/applications + live listings (optional LLM providers — Claude, Grok, GLM-on-NVIDIA, Gemini — behind env flags with silent template fallback).

---

## 5. Tech stack and why

| Layer | Choice | Why |
|---|---|---|
| Backend | **Python + FastAPI** | scipy/scikit-learn in-process; automatic validation; fast to build |
| ML/allocation | **scikit-learn (TF-IDF, cosine) + scipy (Hungarian)** | Deterministic, auditable, zero GPU, explainable to a ministry |
| Database | **PostgreSQL on Neon** (SQLite fallback for offline dev) | Serverless, persistent, pgvector-ready; same code runs both via one `DATABASE_URL` switch |
| Files | **Resume PDFs stored as BYTEA in the DB** | Survives ephemeral hosting; one backup story; fine at 5 MB × hundreds |
| Auth | **PBKDF2 (200k iterations, per-user salt) + DB-backed session tokens** | Real password hashing; per-portal persistent sessions |
| Frontend | Vanilla JS + hand-rolled design system (SVG icon set, design tokens) | Zero build step, instant load, judges can read the source; React/TS migration is the Phase 2 scaffold |
| Live data | **data.gov.in Open Government Data API** (4 PMIS datasets) | Real government statistics, cached 6h + committed snapshot fallback |
| Hosting | **Render** (web) + **Neon** (DB) | Public URL, auto-deploy from GitHub, free tier |
| i18n | Full EN/Hindi/Tamil dictionaries, persisted choice | Accessibility mandate of the scheme |

**Deliberately NOT used:** deep learning (unexplainable for allocation), LangChain (unnecessary dependency), synthetic student data (DPDP honesty — students self-register).

---

## 6. Internals worth knowing (30-second answers)

- **Schema:** students, companies, internships (status: Pending/Verified/Suspended), users (role: student/company/admin), sessions, applications (status flow: Applied → Shortlisted → Offer Sent → Accepted/Declined/Rejected), allocations (with full score breakdown per match), documents (with PDF bytes), notifications, complaints.
- **Every state change emits a notification** (apply → company; shortlist/offer → student; verify/approve → company; allocation → students). Bell counts are real unread counts.
- **Trust chain:** company account approved by admin → listing verified by admin → badge shown to students. Two gates.
- **Live data plumbing:** 4 dataset UUIDs from data.gov.in merged into a state-wise funnel; throttled requests (sample-key rate limits), 6-hour cache, committed JSON snapshot as offline fallback → the demo cannot break.
- **Sessions:** per-portal tokens (student/company/admin stay signed in simultaneously); only a real 401 signs out — server cold starts show "Reconnecting…" and retry.
- **Application cap removed by design** — global optimization does the triage, not the student. It's one policy parameter if the ministry wants 3.

---

## 7. Data honesty (say this proudly)

1. **Statistics: live government data** — data.gov.in API, Parliament-reply datasets, queried on stage.
2. **Companies: real PMIS participants** — TCS, Infosys, L&T, Maruti Suzuki, Mahindra, Eicher, Max Life, Alembic, Jubilant FoodWorks, HDFC Bank, ONGC, NTPC… sourced from PIB releases (no public API names partners; aggregate data only).
3. **Students: zero synthetic records** — real signups only, because student PII is Aadhaar-linked and DPDP-protected. Production onboards via DigiLocker (API Setu).

---

## 8. Judge Q&A (rehearse these)

**Q: "Where's the AI? TF-IDF is old."**
A: The AI is the pipeline, not one model. Government allocation needs deterministic, auditable, explainable scoring — a deep model is a black box we couldn't defend in an RTI request. TF-IDF + n-grams gives semantic matching that is fully explainable, and the embedding step is one swappable module (sentence-transformers + pgvector is the drop-in upgrade). We chose auditability first.

**Q: "Why Hungarian algorithm instead of just recommending?"**
A: Recommendation isn't allocation. Give everyone their top choice and one internship gets 500 claimants — today's failure. Hungarian solves the whole matrix at once for the globally best assignment. Fair across everyone, not fast for the first click.

**Q: "Will O(n³) scale to 6 lakh applicants?"**
A: You never run one national matrix — you shard by region/sector, exactly how the scheme is administered. Min-cost-flow solvers handle millions of nodes. The architecture stays; the solver upgrades. Phase 3 engineering, not a design flaw.

**Q: "How do you know it isn't biased?"** *(open the Fairness tab)*
A: A plain algorithm quietly ranks first-generation and small-college students lower because their profiles are written simply — same ability, plainer words. ATLAS adds a small uplift (+5% first-gen, +3–5% tier-2/3), exactly as the brief mandates, and **never reduces anyone's score** — like grace marks for students who studied by candlelight; they still had to know the answers. This tab is the audit: grey bar = average score before adjustment, green = after. Fair means the gap shrinks, nobody pushed down. Every match stores its exact uplift, so any allocation can be explained and challenged. No black boxes.

**Q: "Who decided 5%?"**
A: We set it for the prototype; in production it's a versioned policy parameter the ministry controls. The algorithm follows policy, it doesn't make policy.

**Q: "Where did your data come from?"**
A: Three honest layers — live data.gov.in statistics, PIB-named real partner companies, and zero synthetic students because real student data is legally protected; production uses DigiLocker. *(Then open Live Data.)*

**Q: "Why trust the match percentage?"**
A: Click "View match reasoning" — every score decomposes into skill/location/sector sub-scores with a deterministic explanation generated from the numbers. Reproducible on demand.

**Q: "Is the chatbot ChatGPT?"**
A: No — retrieval over our own database by default: it knows your profile, your applications, live listings, scheme rules. Zero hallucination, zero network dependency. Optional LLM connectors (Claude/Grok/GLM/Gemini) exist behind flags for a government-empanelled or on-prem model.

**Q: "Why no application cap when the scheme has 3?"**
A: The cap rations a portal that can't triage. With global optimization, wider preference expression improves allocation. It's one parameter — set 3 for compliance, unlimited for better matching.

**Q: "Security?"**
A: PBKDF2-hashed passwords (200k iterations, per-user salt), DB-backed sessions, role checks enforced server-side on every endpoint (students edit only their own profile; companies see only their own applicants; admin statuses require the admin token), resume access restricted to owner/company/admin, secrets in env vars — never in the repo.

**Q: "What's Phase 2/3?"**
A: Phase 2 — sentence-transformers + pgvector, React/TS frontend on our Clean Architecture scaffold, company RBAC refinement, notification emails. Phase 3 — PM Internship portal integration, DigiLocker/e-KYC via API Setu, regional languages beyond Hindi/Tamil, sharded solvers at national scale.

**Trap to avoid:** never say "deep learning" or "neural network" — one probing question collapses it. The story is: *boring, explainable ML, composed into a system government can actually trust.*

---

## 9. Demo cheat sheet

| Portal | URL | Login |
|---|---|---|
| Student | `/student` | your own signup (mobile mandatory) |
| Company | `/company` | `hr@infosys.example.in` / `company@1234` (any of 30 seeded; or self-register → admin approval) |
| Admin | `/admin` | `admin@gmail.com` / `admin@1234` |

**Pre-demo ritual:** open the Render URL 5 minutes early (free tier cold start ~40s); open Live Data once so the cache is warm; keep localhost running as backup.

**3-minute arc:** problem numbers → student signs up via chat intake → recommendations with reasoning → apply → company shortlists, sends offer (bell rings live) → student accepts → admin runs allocation → Fairness tab → Live Data dashboard → close: *"Every other solution treats this as a listing problem. We treat it as what it is — a fairness and trust problem, solved with real allocation science."*
