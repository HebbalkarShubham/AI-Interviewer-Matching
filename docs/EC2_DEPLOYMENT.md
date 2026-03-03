# Running AI-Interviewer-Matching on EC2

Step-by-step guide to run this project on an AWS EC2 instance (Amazon Linux 2 or Ubuntu).

---

## 1. Launch an EC2 instance

1. In **AWS Console** → EC2 → **Launch instance**.
2. **Name:** e.g. `ai-interviewer-matching`.
3. **AMI:** Amazon Linux 2023 or Ubuntu 22.04 LTS.
4. **Instance type:** e.g. `t3.small` (or `t2.micro` for light use).
5. **Key pair:** Create or select a `.pem` key and download it (you need it to SSH).
6. **Network / Security group:**
   - Create or edit a security group.
   - **Inbound rules:**
     - **SSH:** Type = SSH, Port 22, Source = Your IP (or `0.0.0.0/0` for any IP; less secure).
     - **App:** Type = Custom TCP, Port **8000**, Source = `0.0.0.0/0` (so you can open `http://<EC2_PUBLIC_IP>:8000`).
7. **Storage:** 8–20 GB is enough.
8. Launch the instance and note the **public IP** (or use an Elastic IP).

---

## 2. Connect via SSH

From your laptop (replace with your key path and IP):

- **Amazon Linux:** default user is `ec2-user`.
- **Ubuntu:** default user is `ubuntu`.

```bash
# Amazon Linux
ssh -i /path/to/your-key.pem ec2-user@<EC2_PUBLIC_IP>

# Ubuntu
ssh -i /path/to/your-key.pem ubuntu@<EC2_PUBLIC_IP>
```

---

## 3. Get the project on the server

**Option A – Clone (if the repo is public or you use SSH/HTTPS with credentials):**

```bash
cd ~
git clone https://github.com/YOUR_ORG/AI-Interviewer-Matching.git
cd AI-Interviewer-Matching
```

**Option B – Upload from your machine (e.g. from Windows with PowerShell):**

From your **local** project directory (not on EC2):

```powershell
scp -i C:\path\to\your-key.pem -r . ec2-user@<EC2_PUBLIC_IP>:~/AI-Interviewer-Matching/
```

Then on EC2:

```bash
cd ~/AI-Interviewer-Matching
```

---

## 4. One-time setup on EC2

From the **project root** on the server:

```bash
cd ~/AI-Interviewer-Matching
bash setup.sh
```

This script will:

- Install Python 3, pip, venv, MySQL (MariaDB on Amazon Linux), and Node.js 18.
- Create `backend/venv` and install Python dependencies.
- Build the frontend and copy it to `backend/static`.

If `setup.sh` is not executable:

```bash
chmod +x setup.sh run.sh
bash setup.sh
```

---

## 5. Configure MySQL on the server

**Amazon Linux 2 / Amazon Linux 2023 (MariaDB):**

```bash
sudo mysql
```

**Ubuntu (MySQL):**

```bash
sudo mysql
# or
sudo mysql -u root -p
```

Then in the MySQL shell:

```sql
CREATE DATABASE interviewer_matching;
CREATE USER 'appuser'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON interviewer_matching.* TO 'appuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Use the same database name, user, and password in `backend/.env` in the next step.

---

## 6. Create `backend/.env` on EC2

The app does **not** deploy `.env` from Git (for security). Create it on the server:

```bash
cd ~/AI-Interviewer-Matching/backend
nano .env
```

Paste and adjust (use the DB user/password from step 5 and your real keys):

```env
# Database (required)
DATABASE_URL=mysql+pymysql://appuser:your_secure_password@localhost:3306/interviewer_matching

# OpenAI (required for skill extraction and match explanation)
OPENAI_API_KEY=sk-your-openai-key

# Base URL for links in emails – use your EC2 public URL, no trailing slash
APP_BASE_URL=http://<EC2_PUBLIC_IP>:8000

# Optional: SMTP (for sending email when interviewer is selected)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=noreply@example.com

# Optional: AWS S3 (resume uploads)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
S3_BUCKET=your-bucket-name
```

Save and exit (`Ctrl+O`, Enter, `Ctrl+X` in nano).

---

## 7. Start the application

**Foreground (for testing):**

```bash
cd ~/AI-Interviewer-Matching
bash run.sh
```

You should see uvicorn starting. Open **http://\<EC2_PUBLIC_IP\>:8000** in your browser.

**Background (recommended for real use):**

```bash
cd ~/AI-Interviewer-Matching
nohup bash run.sh >> app.log 2>&1 &
```

- Logs go to `~/AI-Interviewer-Matching/app.log`.
- To stop later: `pkill -f 'uvicorn app.main:app'`.

---

## 8. Restart after code or config changes

If you pull new code or change `.env`:

```bash
cd ~/AI-Interviewer-Matching
pkill -f 'uvicorn app.main:app' || true
sleep 2
nohup bash run.sh >> app.log 2>&1 &
```

---

## 9. (Optional) Deploy via GitHub Actions

The repo has a workflow (`.github/workflows/deploy.yml`) that builds the frontend, syncs the project to EC2, and restarts the app. To use it:

1. In GitHub: **Settings** → **Secrets and variables** → **Actions**.
2. Add:
   - **EC2_HOST** – EC2 public IP or hostname.
   - **EC2_SSH_KEY** – Base64 of your `.pem` file (e.g. on Linux: `base64 -w0 your-key.pem`; on Windows you can use an online base64 encoder or PowerShell).
   - **EC2_USER** (optional) – `ec2-user` (Amazon Linux) or `ubuntu` (Ubuntu). Default is `ec2-user`.
   - **EC2_ENV_FILE** (optional) – Base64 of your `backend/.env` so the workflow can write it on the server (S3 and email will work after each deploy).

3. Push to `main` or run the workflow manually from the **Actions** tab. The workflow will sync code and restart the app; the app will be at **http://\<EC2_HOST\>:8000**.

---

## Troubleshooting

### "This site can't be reached" / ERR_CONNECTION_REFUSED

If the instance is running and the deploy workflow succeeded but **http://\<EC2_IP\>:8000** refuses the connection:

1. **Security group (most common)**  
   In EC2 → your instance → **Security** tab → security group → **Edit inbound rules**.  
   Ensure there is a rule: **Type** = Custom TCP, **Port** = **8000**, **Source** = `0.0.0.0/0` (or your IP). Save. Without this, traffic to port 8000 never reaches the instance.

2. **App not running on the instance**  
   The workflow restarts the app over SSH; if that step fails, the job can still succeed (you may see a warning in the workflow run). SSH into the instance and run:
   ```bash
   # Is the app process running?
   pgrep -af uvicorn

   # Can the server reach itself on 8000?
   curl -s -o /dev/null -w "%{http_code}" http://localhost:8000
   ```
   If `pgrep` shows nothing or `curl` fails, the app isn’t running. Start it and then check the log:
   ```bash
   cd ~/AI-Interviewer-Matching && nohup bash run.sh >> app.log 2>&1 &
   tail -50 app.log
   ```
   Fix any errors in `app.log` (e.g. missing `backend/.env`, wrong `DATABASE_URL`, Python/import errors).

| Issue | What to check |
|-------|----------------|
| **Can’t open http://IP:8000** | Security group: allow inbound TCP **8000** from `0.0.0.0/0` (or your IP). Then confirm the app is running (see above). |
| **SSH connection refused** | Security group: allow inbound **22** from your IP. |
| **“Run setup.sh first”** | Run `bash setup.sh` from project root; ensure `backend/venv` exists. |
| **Database connection error** | Check `DATABASE_URL` in `backend/.env`; ensure MySQL is running (`sudo systemctl status mysql` or `mariadb`). |
| **No frontend / blank page** | Ensure `backend/static` exists (from `setup.sh` or deploy). If you only have backend, run frontend build and copy `frontend/dist` to `backend/static`. |
| **OpenAI / SMTP / S3 not working** | Ensure `backend/.env` on EC2 has the correct keys and `APP_BASE_URL` set to `http://<EC2_IP>:8000`. |

---

## Summary

1. Launch EC2 (port 22 + 8000 open).
2. SSH in and get the project (clone or upload).
3. Run `bash setup.sh`.
4. Create MySQL DB and user; create `backend/.env`.
5. Run `bash run.sh` (or `nohup bash run.sh >> app.log 2>&1 &`).
6. Open **http://\<EC2_PUBLIC_IP\>:8000**.

For automated deploys, set GitHub secrets and use the existing deploy workflow.
