# Pydantic schemas for Candidate and Matching (Python 3.9 compatible)
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class CandidateSkillResponse(BaseModel):
    skill: str
    confidence: Optional[float] = None

    class Config:
        from_attributes = True


class CandidateCreate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


class CandidateResponse(BaseModel):
    id: int
    name: Optional[str] = None
    email: Optional[str] = None
    resume_text: Optional[str] = None  # extracted text only
    resume_path: Optional[str] = None  # S3 path for resume file
    resume_download_url: Optional[str] = None  # presigned URL when S3 configured
    skills: List[CandidateSkillResponse] = []

    class Config:
        from_attributes = True


# Match result for one interviewer
class MatchResult(BaseModel):
    interviewer_id: int
    name: str
    email: str
    skills: str
    score: float  # 0-100
    matched_skills: List[str]
    explanation: Optional[str] = None


class MatchExplanation(BaseModel):
    text: str
