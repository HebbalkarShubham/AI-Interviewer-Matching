# FastAPI app entry - CORS, routers, static frontend
# Ensure backend dir is on path so "app" is found when run from any cwd
import sys
from pathlib import Path

_backend = Path(__file__).resolve().parent.parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base
from app import models  # noqa: F401 - register models with Base
from app.routes import interviewers, candidates, selection, match

# Directory for React production build (copy frontend/dist here for deployment)
STATIC_DIR = _backend / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (for dev; use Alembic in production)
    Base.metadata.create_all(bind=engine)
    yield
    # shutdown if needed
    pass


app = FastAPI(
    title="AI Interviewer Matching System",
    description="Upload resume, match with interviewers, select and notify.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS: same-origin in prod; allow dev origins and any origin for hackathon
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes under /api (frontend uses BASE = '/api')
app.include_router(interviewers.router, prefix="/api")
app.include_router(candidates.router, prefix="/api")
app.include_router(selection.router, prefix="/api")
app.include_router(match.router, prefix="/api")

# Serve React production build: "/" -> index.html, "/assets/*" -> static assets
# Mount static last so /api takes precedence
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="frontend")
else:
    # No static build: still serve API and a simple root message (e.g. dev backend-only)
    @app.get("/")
    def root():
        return {"message": "AI Interviewer Matching API", "docs": "/docs"}
