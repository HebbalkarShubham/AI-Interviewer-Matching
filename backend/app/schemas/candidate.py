# Pydantic schemas for Candidate and Matching (Python 3.14 compatible)
from __future__ import annotations

from pydantic import BaseModel


class CandidateSkillResponse(BaseModel):
    skill: str
    confidence: float | None = None

    class Config:
        from_attributes = True


class CandidateCreate(BaseModel):
    name: str | None = None
    email: str | None = None


class CandidateResponse(BaseModel):
    id: int
    name: str | None
    email: str | None
    resume_text: str | None = None  # extracted text only
    resume_path: str | None = None  # S3 path for resume file
    resume_download_url: str | None = None  # presigned URL when S3 configured
    skills: list[CandidateSkillResponse] = []

    class Config:
        from_attributes = True


# Match result for one interviewer
class MatchResult(BaseModel):
    interviewer_id: int
    name: str
    email: str
    skills: str
    score: float  # 0-100
    matched_skills: list[str]
    explanation: str | None = None


class MatchExplanation(BaseModel):
    text: str
