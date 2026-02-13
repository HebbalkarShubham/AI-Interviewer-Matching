# Pydantic schemas for Interviewer API (skills only, no availability)
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class InterviewerSkillCreate(BaseModel):
    skill_name: str
    skill_type: str  # "Primary" or "Secondary"


class InterviewerSkillResponse(BaseModel):
    id: int
    skill_name: str
    skill_type: str

    model_config = ConfigDict(from_attributes=True)


class InterviewerCreate(BaseModel):
    name: str
    email: str
    level: str | None = None
    experience_range: str | None = None  # e.g. "0-2", "3-5", "5-10"
    skills: list[InterviewerSkillCreate] = []


class InterviewerResponse(BaseModel):
    id: int
    name: str
    email: str
    level: str | None
    experience_range: str | None
    skills: list[InterviewerSkillResponse] = []

    model_config = ConfigDict(from_attributes=True)


# --- Match endpoint schemas (skills only) ---
class MatchRequest(BaseModel):
    skills: list[str]


class MatchResultItem(BaseModel):
    name: str
    email: str
    score: int
    matched_skills: list[str]
