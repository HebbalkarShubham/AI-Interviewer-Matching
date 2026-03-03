# AI Interviewer Matching System

Match candidates (from resume) with interviewers by skills. Uses OpenAI to extract skills and explain matches; optional email when an interviewer is selected.

## Stack

- **Backend:** FastAPI, MySQL, SQLAlchemy, OpenAI
- **Frontend:** React (Vite), React Router

## Features

- Upload resume (PDF) → extract text → AI extracts skills
- Store interviewers with comma-separated skills
- Match candidate to interviewers by skill overlap (score 0–100%)
- Rank and show match percentage
- AI-generated explanation per match
- Select interviewer and send email notification

## Setup

### 1. MySQL

Create a database (MySQL Workbench, CLI, or any client):

```sql
CREATE DATABASE interviewer_matching;
```

### 2. Backend

Works with **Python 3.9–3.14** (Pydantic 2.12+ provides 3.14 wheels).

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set:

- `DATABASE_URL` – MySQL connection string (e.g. `mysql+pymysql://user:password@host:3306/dbname`)
- `OPENAI_API_KEY` – required for skill extraction and explanations
- `SMTP_*`, `EMAIL_FROM` – optional, for sending email when interviewer is selected
- `AWS_*`, `S3_BUCKET` – optional, for storing resumes on S3

Run the API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Tables are created on startup.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The app proxies `/api` to `http://localhost:8000`.

## Usage

1. **Interviewers:** Go to **Interviewers** → Add interviewers with name, email, and skills (e.g. `Python, React, SQL`).
2. **Upload:** Go to **Upload Resume** → Choose a PDF → Upload. Skills are extracted via OpenAI and you’re redirected to the candidate’s match page.
3. **Matches:** View ranked interviewers with score %, matched skills, and AI explanation. Click **Select & Send Email** to notify the interviewer (if SMTP is configured).

## Project structure

```
backend/
  app/
    main.py          # FastAPI app, CORS, routes
    config.py       # Settings from env
    database.py     # SQLAlchemy engine and session
    models/         # Interviewer, Candidate, CandidateSkill
    schemas/        # Pydantic request/response
    routes/         # interviewers, candidates, selection
    services/       # ai_service, matching_service, email_service, resume_service
  requirements.txt

frontend/
  src/
    App.jsx         # Routes
    api.js          # API client
    components/     # Layout
    pages/          # Home, Upload, CandidateMatches, Interviewers
  package.json
```

## API overview

- `GET/POST /interviewers` – list, create
- `GET/PUT/DELETE /interviewers/{id}` – get, update, delete
- `POST /candidates/upload` – upload file (multipart), returns candidate with skills
- `GET /candidates/{id}` – get candidate
- `GET /candidates/{id}/matches` – ranked match results with score and explanation
- `POST /selection/select` – body: `candidate_id`, `interviewer_id`, `send_email`; sends email to interviewer

## Deploying to EC2

**Full step-by-step:** See **[docs/EC2_DEPLOYMENT.md](docs/EC2_DEPLOYMENT.md)** for launching the instance, running `setup.sh`, configuring MySQL and `.env`, and starting the app.

The GitHub workflow (`.github/workflows/deploy.yml`) syncs code to EC2 but **excludes** `backend/.env` for security. So S3 uploads and email **will not work** on EC2 until the server has a `backend/.env` file.

**Option A – Manual:** SSH to EC2 and create `~/AI-Interviewer-Matching/backend/.env` with the same variables as locally (e.g. `DATABASE_URL`, `OPENAI_API_KEY`, `SMTP_*`, `EMAIL_FROM`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET`, `AWS_REGION`). Then restart the app (or redeploy).

**Option B – GitHub secret:** Encode your local `.env` as base64 (e.g. `base64 -w0 backend/.env` on Linux, or use an online encoder) and add a repository secret **EC2_ENV_FILE** with that value. On each deploy, the workflow will write it to `backend/.env` on the server so S3 and email work without manual SSH.
