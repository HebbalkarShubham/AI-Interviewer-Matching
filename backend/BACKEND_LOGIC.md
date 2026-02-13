# Backend Logic – File-by-File Explanation

This document explains **every backend file** and how they work together in the **AI Interviewer Matching System**.

---

## 1. Project structure (overview)

```
backend/app/
├── main.py              # App entry, CORS, lifespan, routers
├── config.py            # Settings from .env
├── database.py          # SQLAlchemy engine, session, get_db
├── models/              # DB tables (ORM)
│   ├── interviewer.py   # Interviewer, InterviewerSkill
│   └── candidate.py     # Candidate, CandidateSkill
├── schemas/             # Pydantic request/response shapes
│   ├── interviewer.py
│   └── candidate.py
├── routes/              # API endpoints
│   ├── interviewers.py  # CRUD interviewers
│   ├── candidates.py    # Upload resume, get candidate, get matches
│   ├── match.py         # POST /match (skills only)
│   └── selection.py     # Select interviewer + send email
└── services/            # Business logic (no HTTP)
    ├── ai_service.py        # OpenAI: extract skills, explain match
    ├── matching.py          # find_best_interviewers (skills only)
    ├── matching_service.py  # Candidate vs interviewers (skill overlap %)
    ├── resume_service.py    # Save file, extract text from PDF
    └── email_service.py     # SMTP: send email to interviewer
```

**Request flow (high level):**  
`HTTP request` → **route** (validates body with **schemas**) → **service** (logic) + **models** (DB) → **schemas** (response) → `HTTP response`.

---

## 2. Root / config / database

### `app/main.py`

- **Role:** FastAPI app entry point.
- **What it does:**
  1. **Path fix:** Adds the `backend` folder to `sys.path` so `import app...` works no matter which directory you run the server from.
  2. **Lifespan:** On startup, runs `Base.metadata.create_all(bind=engine)` to create all tables (dev only; use Alembic in production). On shutdown it does nothing.
  3. **CORS:** Allows requests from `http://localhost:5173` and `http://127.0.0.1:5173` (React dev server).
  4. **Routers:** Mounts four routers so you get:
     - `/interviewers` → `interviewers.router`
     - `/candidates` → `candidates.router`
     - `/selection` → `selection.router`
     - `/match` → `match.router`
  5. **Root route:** `GET /` returns a simple JSON message and points to docs.

All “logic” here is wiring; no business rules.

---

### `app/config.py`

- **Role:** Central place for configuration (env vars).
- **What it does:**
  - Loads `.env` via `load_dotenv()`.
  - Defines `Settings` with:
    - **DATABASE_URL** – MySQL connection string (from env).
    - **OPENAI_API_KEY** – Used by `ai_service` for skill extraction and explanations.
    - **UPLOAD_DIR** – Name of upload folder, default `"uploads"`.
    - **UPLOAD_ABS_PATH** – Absolute path to that folder under the backend root so uploads and PDF reading work regardless of current working directory.
  - Exposes a single `settings` instance.

No business logic; only configuration.

---

### `app/database.py`

- **Role:** SQLAlchemy engine and session management.
- **What it does:**
  - **engine:** `create_engine(settings.DATABASE_URL, pool_pre_ping=True)` – one connection pool to MySQL.
  - **SessionLocal:** Session factory bound to that engine (autocommit/autoflush off).
  - **Base:** Declarative base for all ORM models.
  - **get_db():** Generator that creates a session, yields it to the route, then closes it. Used as a FastAPI dependency so every request gets a clean session and it’s always closed.

No business logic; only DB connection and session lifecycle.

---

## 3. Models (database tables)

Models define **tables** and **relationships**. They are used by routes and services to read/write the DB. No HTTP or Pydantic here.

### `app/models/interviewer.py`

- **Role:** Defines the “interviewer” side of the DB: one main table and two related tables.

**Interviewer (table: `interviewers`)**

- `id` – PK  
- `name`, `email` – required, email unique  
- `level` – e.g. "Senior", "Lead"  
- `experience_range` – string (e.g. "0-2", "3-5", "5-10")  
- **Relationship:** `skills` → list of `InterviewerSkill`, `cascade="all, delete-orphan"` so deleting an interviewer deletes its skills.

**InterviewerSkill (table: `interviewer_skills`)**

- `id` – PK  
- `interviewer_id` – FK to `interviewers.id`, CASCADE on delete  
- `skill_name` – e.g. "Python", "AWS"  
- `skill_type` – "Primary" or "Secondary"  
- **Relationship:** `interviewer` → one `Interviewer`

So: one interviewer has many skills. Used by interviewer CRUD and by the **match** logic (skills only).

---

### `app/models/candidate.py`

- **Role:** Defines the “candidate” side: one table for the candidate and one for AI-extracted skills.

**Candidate (table: `candidates`)**

- `id` – PK  
- `name`, `email` – optional (often filled later)  
- `resume_path` – path to uploaded file (e.g. `uploads/abc.pdf`)  
- `resume_text` – raw text extracted from the PDF (for AI and debugging)  
- `created_at` – set by DB  
- **Relationship:** `skills` → list of `CandidateSkill`, cascade delete

**CandidateSkill (table: `candidate_skills`)**

- `id` – PK  
- `candidate_id` – FK to `candidates.id`, CASCADE on delete  
- `skill` – skill name (e.g. "Python")  
- `confidence` – optional 0–1 from OpenAI  

So: one candidate has many skills (from resume extraction). Used by upload, get candidate, and **candidate-based matching** (candidate vs interviewers).

---

### `app/models/__init__.py`

- **Role:** Re-exports models so other code can do `from app.models import Interviewer, Candidate, ...` and so that `main.py`’s `import app.models` registers all tables with `Base.metadata` for `create_all`.

---

## 4. Schemas (request/response shapes)

Schemas are **Pydantic** models. They validate incoming JSON and shape outgoing JSON. They don’t talk to the DB; they just define “what the API accepts and returns”.

### `app/schemas/interviewer.py`

- **Role:** All request/response types for interviewers and for the **match** endpoint.

**Create (request body):**

- **InterviewerSkillCreate** – `skill_name`, `skill_type`  
- **InterviewerCreate** – `name`, `email`, `level`, `experience_range`, `skills[]`

**Response:**

- **InterviewerSkillResponse** – `id`, `skill_name`, `skill_type`  
- **InterviewerResponse** – interviewer fields + `skills[]` (with `from_attributes=True` so you can build from ORM objects)

**Match endpoint:**

- **MatchRequest** – `skills` (list of strings)  
- **MatchResultItem** – `name`, `email`, `score`, `matched_skills[]`

So: interviewer CRUD and POST /match are fully typed and validated here.

---

### `app/schemas/candidate.py`

- **Role:** Request/response for candidates and for “candidate match results” (when you match a candidate to interviewers by resume skills).

**Candidate:**

- **CandidateSkillResponse** – `skill`, `confidence`  
- **CandidateCreate** – optional name/email (not heavily used in current flow)  
- **CandidateResponse** – candidate fields + `skills[]` (list of skill + confidence)

**Candidate matches (GET /candidates/{id}/matches):**

- **MatchResult** – `interviewer_id`, `name`, `email`, `skills` (string for display), `score` (0–100), `matched_skills[]`, `explanation` (AI text)

So: upload response, get candidate, and “ranked interviewers for this candidate” are all defined here.

---

## 5. Routes (API endpoints)

Routes receive HTTP, validate input with schemas, call services/models, and return schema-shaped JSON. They contain **minimal** logic; the “how” is in services and models.

### `app/routes/interviewers.py`

- **Role:** Full CRUD for interviewers (skills only, no availability).

**Helpers:**

- `_interviewer_to_response(inv)` – builds `InterviewerResponse` from an `Interviewer` ORM object (including `skills` list).

**Endpoints:**

- **GET /interviewers** – List all interviewers; uses `joinedload` for `skills`; returns list of `InterviewerResponse`.
- **POST /interviewers** – Body = `InterviewerCreate`. Creates one `Interviewer`, then creates rows in `interviewer_skills` (ORM only). Returns the new interviewer.
- **GET /interviewers/{id}** – One interviewer by id, same response shape.
- **PUT /interviewers/{id}** – Replace interviewer fields and **replace** all skills (delete existing, insert from body). Returns updated interviewer.
- **DELETE /interviewers/{id}** – Delete interviewer (DB cascade deletes skills).

So: all interviewer data is managed through these endpoints with the two-table structure (interviewers + interviewer_skills).

---

### `app/routes/candidates.py`

- **Role:** Upload resume, get one candidate, get “ranked interviewers” for that candidate (by resume skills).

**Helpers:**

- `_load_interviewers_with_skills(db)` – loads all interviewers with `Interviewer.skills` eager-loaded (for matching).
- `candidate_to_response(c)` – builds `CandidateResponse` from `Candidate` (with its `skills` list).

**Endpoints:**

- **POST /candidates/upload**  
  - Input: multipart file (e.g. PDF).  
  - Steps: read file → check size (5MB) → `save_upload_file` → `extract_text_from_file` → create `Candidate` + `CandidateSkill` rows (skills from `extract_skills_from_resume`).  
  - Returns: `CandidateResponse` (id, resume_path, extracted skills, etc.).  
  - Errors: try/except with clear HTTP 400/500 and message (e.g. “Failed to save file”, “Failed to save candidate”).

- **GET /candidates/{candidate_id}** – Fetch candidate by id, return `CandidateResponse` (404 if not found).

- **GET /candidates/{candidate_id}/matches**  
  - Loads candidate and all interviewers (with skills).  
  - Calls **matching_service.get_ranked_matches(candidate, interviewers)** (skill-overlap score 0–100%, optional AI explanation).  
  - Returns list of `MatchResult` (interviewer_id, name, email, skills string, score, matched_skills, explanation).

So: resume → candidate + skills; then “best interviewers for this candidate” by skill overlap (and optionally AI explanation).

---

### `app/routes/match.py`

- **Role:** “Find best interviewers” by **required skills only** (no candidate involved).

- **POST /match**  
  - Body: `MatchRequest` – `skills[]`.  
  - Calls **services/matching.find_best_interviewers(db, skills, top_n=5)**.  
  - Returns list of `MatchResultItem`: `name`, `email`, `score`, `matched_skills[]` (top 5).

So: matching by skills only; no day/time or availability.

---

### `app/routes/selection.py`

- **Role:** “Select” an interviewer for a candidate and optionally send an email.

- **POST /selection/select**  
  - Body: `candidate_id`, `interviewer_id`, `send_email` (default true).  
  - Loads candidate and interviewer (404 if missing).  
  - If `send_email`, calls **email_service.send_interviewer_selection_email(...)**.  
  - Returns ok, ids, interviewer name/email, and whether the email was sent.

No DB write besides what might be inside email (e.g. logging); it’s “selection + notification”.

---

## 6. Services (business logic)

Services contain the **core logic**. They use **models** (ORM) and **config**; they do **not** know about HTTP, FastAPI, or Pydantic (except that they return dicts/lists that routes then pass to response schemas).

### `app/services/ai_service.py`

- **Role:** All OpenAI usage: extract skills from text and generate short match explanations.

- **extract_skills_from_resume(resume_text)**  
  - If no API key or empty text, returns `[]`.  
  - Sends a prompt asking for a JSON array of `{ "skill", "confidence" }`.  
  - Parses the response (handles markdown code blocks), returns list of dicts.  
  - On any error, returns `[]`.

- **explain_match(candidate_skills, interviewer_skills, score)**  
  - If no client, returns a simple fallback string.  
  - Otherwise asks OpenAI for a 1–2 sentence explanation of why this interviewer fits the candidate (given the skill lists and score).  
  - Used by **matching_service** when building candidate-match results (GET /candidates/{id}/matches).

So: AI is only here; resume extraction and “why this match” both go through this module.

---

### `app/services/matching.py`

- **Role:** Implement **find_best_interviewers**: filter by required skills, score, sort, return top N. Used by **POST /match**.

**Logic:**

1. Normalize required skills (strip, lower).
2. Load all interviewers with `skills` (ORM, joinedload).
3. For each interviewer:
   - Build list of their skill names (normalized).
   - Count how many required skills they have → `skill_match_count`; if 0, skip.
   - **Score** = `skill_match_count * 10`.
   - Keep for result: name, email, score, matched_skills (original casing from DB).
4. Sort by score descending, take first `top_n` (default 5).

Returns list of dicts; route converts them to `MatchResultItem`. No raw SQL; only ORM and in-memory filtering/sorting.

---

### `app/services/matching_service.py`

- **Role:** “Match a **candidate** (from resume) to **interviewers**” by skill overlap. Used by **GET /candidates/{id}/matches**.

**Logic:**

1. **get_interviewer_skill_list(inv)** – From an `Interviewer`, returns list of normalized skill names. Handles both:
   - New model: `inv.skills` is a list of `InterviewerSkill` → use `skill_name`.
   - Legacy: `inv.skills` was a string → split by comma/semicolon.
2. **get_interviewer_skills_display(inv)** – Same source but returns a single string (e.g. for `MatchResult.skills`).
3. **get_candidate_skill_list(candidate)** – Normalized list of candidate’s skills from `candidate.skills`.
4. **compute_match_score(candidate_skills, interviewer_skills)** – Set intersection; score = (number of matched / number of candidate skills) * 100; returns (score, list of matched skill names).
5. **get_ranked_matches(candidate, interviewers, include_explanation)** – For each interviewer, compute score and matched list; optionally call **ai_service.explain_match**; build dict with interviewer_id, name, email, skills string, score, matched_skills, explanation; sort by score desc and return.

So: “candidate from resume” vs “all interviewers” by skill overlap + optional AI explanation.

---

### `app/services/resume_service.py`

- **Role:** Save uploaded file and extract text from it (for storage and for AI).

- **ensure_upload_dir()** – Uses `UPLOAD_ABS_PATH` (or `UPLOAD_DIR`) so the directory is under the backend; creates it if needed; returns the Path.
- **save_upload_file(content, filename)** – Generates a unique name (uuid + original extension), writes under that directory, returns a **relative** path string like `"uploads/abc.pdf"` (stored in `Candidate.resume_path`).
- **extract_text_from_pdf(file_path)** – Opens the file (absolute or relative), uses PyPDF2 to get text from each page, joins with newlines; returns empty string on error.
- **extract_text_from_file(file_path, content_type)** – Resolves relative paths against `UPLOAD_ABS_PATH` so the file is found regardless of cwd. If PDF (by content-type or extension), calls `extract_text_from_pdf`; if text-like or .txt/.md, reads as UTF-8; otherwise returns `""`.

So: “where to save”, “how to save”, and “how to get text from PDF/text file” are all here; used only by the upload route.

---

### `app/services/email_service.py`

- **Role:** Send emails (e.g. when an interviewer is selected).

- **send_email(to_email, subject, body_html)** – Uses SMTP (from config: host, port, user, password, from). If SMTP not configured, returns False; on success True.
- **send_interviewer_selection_email(interviewer_email, interviewer_name, candidate_name, candidate_email)** – Builds subject and HTML body (“You have been selected to interview …”) and calls `send_email`.

Used only by **POST /selection/select**. If your `config` doesn’t define SMTP_* and EMAIL_FROM, the function will return False and the API will still return success but report `email_sent: false`.

---

## 7. How the main flows fit together

### A. Resume upload (POST /candidates/upload)

1. **Route** receives file, reads bytes, checks size.
2. **resume_service.save_upload_file** → saves under backend uploads, returns path string.
3. **resume_service.extract_text_from_file** → gets text from PDF (or text file).
4. **Route** creates `Candidate` (resume_path, resume_text) and commits.
5. **ai_service.extract_skills_from_resume(text)** → list of `{ skill, confidence }`.
6. **Route** creates `CandidateSkill` rows and commits; reloads candidate; returns **CandidateResponse**.

So: file → disk + DB candidate + text → AI skills → DB candidate_skills → response.

---

### B. Match by skills (POST /match)

1. **Route** validates body with **MatchRequest** (skills).
2. **matching.find_best_interviewers(db, skills, top_n=5)** loads interviewers (with skills), filters by “has at least one skill”, scores, sorts, takes top 5.
3. **Route** maps results to **MatchResultItem** and returns.

So: no candidate; only “who has these skills and is free at this slot”.

---

### C. Candidate-based matches (GET /candidates/{id}/matches)

1. **Route** loads candidate and all interviewers (with skills).
2. **matching_service.get_ranked_matches(candidate, interviewers)** computes skill-overlap score for each interviewer, optionally **ai_service.explain_match** per row, sorts by score.
3. **Route** returns list of **MatchResult** (interviewer_id, name, email, skills string, score, matched_skills, explanation).

So: “for this candidate (from resume), rank interviewers by skill overlap and explain.”

---

### D. Select interviewer + email (POST /selection/select)

1. **Route** loads candidate and interviewer by id.
2. **email_service.send_interviewer_selection_email** (if send_email true).
3. **Route** returns ok and whether email was sent.

So: selection is “which interviewer for this candidate” + optional notification; no new DB model for “selection” in this codebase.

---

## 8. Summary table

| File | Responsibility |
|------|----------------|
| **main.py** | App, path, CORS, lifespan (create tables), mount routers. |
| **config.py** | DATABASE_URL, OPENAI_API_KEY, UPLOAD_DIR, UPLOAD_ABS_PATH. |
| **database.py** | Engine, SessionLocal, Base, get_db. |
| **models/interviewer.py** | Tables: interviewers, interviewer_skills; relationships. |
| **models/candidate.py** | Tables: candidates, candidate_skills; relationships. |
| **schemas/interviewer.py** | Request/response for interviewer CRUD and for POST /match. |
| **schemas/candidate.py** | Request/response for candidate and for GET .../matches. |
| **routes/interviewers.py** | CRUD interviewers (create/update skills via ORM). |
| **routes/candidates.py** | Upload resume, get candidate, get ranked matches for candidate. |
| **routes/match.py** | POST /match: best interviewers by skills only. |
| **routes/selection.py** | POST /selection/select: select interviewer + send email. |
| **services/ai_service.py** | OpenAI: extract skills from text, explain match. |
| **services/matching.py** | find_best_interviewers (skills only, score, top N). |
| **services/matching_service.py** | Candidate vs interviewers: skill overlap %, rank, explain. |
| **services/resume_service.py** | Save file, extract text from PDF/text. |
| **services/email_service.py** | SMTP: send selection email to interviewer. |

That’s the full backend logic, file by file and flow by flow.
