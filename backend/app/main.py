# FastAPI app entry - CORS, routers, startup
# Ensure backend dir is on path so "app" is found when run from any cwd
import sys
from pathlib import Path

_backend = Path(__file__).resolve().parent.parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app import models  # noqa: F401 - register models with Base
from app.routes import interviewers, candidates, selection, match


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

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routes
app.include_router(interviewers.router)
app.include_router(candidates.router)
app.include_router(selection.router)
app.include_router(match.router)


@app.get("/")
def root():
    return {"message": "AI Interviewer Matching API", "docs": "/docs"}
