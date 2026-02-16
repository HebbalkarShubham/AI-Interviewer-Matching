# EC2 deployment

Deploy React + FastAPI on one AWS EC2 instance, port 8000. Frontend and backend are served together; no CORS issues.

**→ First time setting up the environment on EC2?** Use **[EC2_SETUP_GUIDE.md](EC2_SETUP_GUIDE.md)** for a single, step-by-step checklist (from “open EC2 terminal” to “app running”).

---

## A. Folder structure (after build)

```
AI-Interviewer-Matching/
├── frontend/
│   ├── src/
│   ├── dist/              ← npm run build output (do not deploy this folder)
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── app/
│   │   ├── main.py        ← serves API + static frontend
│   │   ├── routes/
│   │   └── ...
│   ├── static/            ← copy of frontend/dist (created by setup or copy step)
│   │   ├── index.html
│   │   └── assets/
│   ├── .env               ← your config (create on EC2)
│   ├── venv/              ← created by setup.sh
│   └── requirements.txt
├── setup.sh               ← one-time: install Python, MySQL, Node, build frontend
├── run.sh                 ← start server
└── DEPLOYMENT.md
```

---

## B. How FastAPI serves the app

- **`/`** → React `index.html` (SPA)
- **`/assets/*`** → React JS/CSS (Vite build output)
- **`/api/*`** → Backend APIs (e.g. `/api/interviewers`, `/api/candidates`)

The frontend already uses `BASE = '/api'`, so all API calls go to the same origin → no CORS issues.

---

## C. Build and copy (local machine)

**Option 1 – Build and copy locally (then deploy only backend + static):**

```bash
cd frontend
npm ci
npm run build
```

Then copy the build into the backend:

```bash
# From project root (Windows: use xcopy or copy; Linux/Mac: cp)
rm -rf backend/static
cp -r frontend/dist backend/static
```

**Option 2 – Let setup.sh do it on EC2:**  
On the server, `setup.sh` runs `npm run build` in `frontend/` and copies `frontend/dist` to `backend/static` for you.

---

## D. EC2 deployment steps (beginner-friendly)

1. **Launch an EC2 instance**
   - AMI: Amazon Linux 2 or Ubuntu 22.04
   - Instance type: e.g. t2.micro (free tier) or t3.small
   - Security group: allow **Inbound** TCP port **8000** (and 22 for SSH)
   - Storage: 8–10 GB is enough

2. **SSH into the instance**
   ```bash
   ssh -i your-key.pem ec2-user@YOUR_EC2_IP
   ```
   (Ubuntu user is often `ubuntu` instead of `ec2-user`.)

3. **Install Git and clone the repo**
   ```bash
   sudo yum install -y git   # Amazon Linux
   # or: sudo apt install -y git   # Ubuntu
   git clone https://github.com/YOUR_USER/AI-Interviewer-Matching.git
   cd AI-Interviewer-Matching
   ```

4. **Create backend `.env` on the server**
   ```bash
   cp backend/.env.example backend/.env
   nano backend/.env
   ```
   Set at least:
   - `DATABASE_URL=mysql+pymysql://USER:PASSWORD@127.0.0.1:3306/employee`
   - `OPENAI_API_KEY=...`
   (Add AWS, SMTP, etc. if you use them.)

5. **One-time setup**
   ```bash
   bash setup.sh
   ```
   This installs Python, pip, venv, MySQL, Node, builds the frontend, and copies it to `backend/static`.

6. **Create MySQL database and user** (if not already done)
   ```bash
   sudo mysql
   ```
   In MySQL:
   ```sql
   CREATE DATABASE employee;
   CREATE USER 'appuser'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL ON employee.* TO 'appuser'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```
   Update `backend/.env` so `DATABASE_URL` uses this user and password.

7. **Start the app**
   ```bash
   bash run.sh
   ```
   Leave this terminal open, or run in background:
   ```bash
   nohup bash run.sh > app.log 2>&1 &
   ```

8. **Open in browser**
   ```
   http://YOUR_EC2_IP:8000
   ```
   You should see the React app; APIs are under `/api/*`.

---

## E. setup.sh (what it does)

- Detects OS (Amazon Linux / Ubuntu) and installs:
  - Python 3, pip, venv
  - MySQL (MariaDB on Amazon Linux, MySQL on Ubuntu)
  - Node.js 18 (for `npm run build`)
- Creates `backend/venv` and installs `backend/requirements.txt`
- Builds frontend (`npm ci` + `npm run build`) and copies `frontend/dist` → `backend/static`

Run once after clone: **`bash setup.sh`**

---

## F. run.sh (what it does)

- Changes to `backend/`
- Loads `backend/.env` (if present)
- Activates `backend/venv`
- Runs: **`uvicorn app.main:app --host 0.0.0.0 --port 8000`**

So everything (frontend + backend) is on port 8000. Start with: **`bash run.sh`**

---

## G. Quick checklist

| Step              | Command / action                          |
|-------------------|-------------------------------------------|
| Open port 8000    | EC2 Security Group → Inbound → TCP 8000   |
| Clone repo        | `git clone ...` then `cd AI-Interviewer-Matching` |
| Configure env     | `cp backend/.env.example backend/.env` and edit |
| One-time setup    | `bash setup.sh`                           |
| Create DB (once)  | `sudo mysql` → create DB and user         |
| Start server      | `bash run.sh`                             |
| Use app           | `http://EC2_IP:8000`                      |

---

## H. Automated pipeline (GitHub Actions)

On every **push to the deployment branch**, the workflow builds the frontend and deploys to EC2.

**What it does:**
1. Checkout code, install frontend deps, run `npm run build`
2. Copy `frontend/dist` → `backend/static`
3. Rsync project to EC2 (excluding `backend/venv`, `backend/.env`, `node_modules`, `.git`)
4. SSH to EC2, restart app: `pkill uvicorn` then `nohup bash run.sh &`

**Required GitHub secrets** (Repo → Settings → Secrets and variables → Actions):

| Secret        | Description |
|---------------|-------------|
| `EC2_HOST`    | EC2 public IP or hostname (e.g. `3.110.45.67` or `ec2-xx-xx.compute.amazonaws.com`) |
| `EC2_SSH_KEY` | Full contents of your `.pem` private key (the one you use for `ssh -i key.pem`) |
| `EC2_USER`    | Optional. SSH user: `ec2-user` (Amazon Linux) or `ubuntu` (Ubuntu). Defaults to `ec2-user` if not set. |

**One-time on EC2:** Pipeline expects the repo at `~/AI-Interviewer-Matching` and that you’ve run `setup.sh` once (so `venv` and `.env` exist). Pipeline does **not** overwrite `backend/.env` or `backend/venv`.

**Manual run:** Actions → Deploy to EC2 → Run workflow.

**Branch:** Trigger is set in `.github/workflows/deploy.yml` (e.g. `branches: [deployment]`). Change it there if you use a different branch.

---

## Troubleshooting

- **Port 8000 not loading:** Check Security Group allows inbound TCP 8000 from your IP or 0.0.0.0/0.
- **API 404:** Ensure routers are under `/api` (they are in `main.py`). Frontend must use `BASE = '/api'` (already set in `frontend/src/api.js`).
- **Database connection error:** Check `backend/.env` `DATABASE_URL`, and that MySQL is running: `sudo systemctl status mariadb` or `sudo systemctl status mysql`.
- **No static files:** Ensure `backend/static` exists and contains `index.html` and `assets/` (run `setup.sh` or copy `frontend/dist` → `backend/static`).
- **Pipeline deploy fails:** Check `EC2_HOST`, `EC2_SSH_KEY` (and `EC2_USER` if not `ec2-user`). Ensure EC2 security group allows SSH (22) from GitHub’s IPs or 0.0.0.0/0. Ensure the repo exists on EC2 at `~/AI-Interviewer-Matching` and `setup.sh` has been run once.
