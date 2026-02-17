import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Backend root (parent of app/)
_BACKEND_ROOT = Path(__file__).resolve().parent.parent


class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    # Uploads: store under backend folder so path works from any cwd
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    # Absolute path for uploads (backend/uploads)
    UPLOAD_ABS_PATH = _BACKEND_ROOT / os.getenv("UPLOAD_DIR", "uploads")
    # SMTP (optional - for sending email when interviewer is selected)
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT") or "587")
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM = os.getenv("EMAIL_FROM", "")
    # AWS S3 (for resume uploads)
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET = os.getenv("S3_BUCKET", "")
    # Base URL for links in emails (e.g. Accept/Reject interview) - no trailing slash
    APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8000")


settings = Settings()
