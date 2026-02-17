# Interviewer CRUD API - skills only (no availability)
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Interviewer, InterviewerSkill
from app.schemas.interviewer import (
    InterviewerCreate,
    InterviewerResponse,
    InterviewerSkillResponse,
)

router = APIRouter(prefix="/interviewers", tags=["interviewers"])


def _handle_db_error(e: Exception):
    """Return 400 with a clear message for common DB errors."""
    msg = str(e.orig) if hasattr(e, "orig") else str(e)
    if "Data truncated" in msg or "1265" in msg:
        raise HTTPException(
            status_code=400,
            detail="Database column too short for level/experience_range. Run: migrations/fix_interviewer_level_experience_columns.sql",
        )
    if "Duplicate entry" in msg or "1062" in msg or "integrity" in msg.lower():
        raise HTTPException(status_code=400, detail="An interviewer with this email already exists.")
    raise HTTPException(status_code=500, detail=msg or "Database error")


def _interviewer_to_response(inv: Interviewer) -> InterviewerResponse:
    skills = [
        InterviewerSkillResponse(id=s.id, skill_name=s.skill_name, skill_type=s.skill_type)
        for s in inv.skills
    ]
    return InterviewerResponse(
        id=inv.id,
        name=inv.name,
        email=inv.email,
        level=inv.level,
        experience_range=inv.experience_range,
        skills=skills,
    )


@router.get("", response_model=List[InterviewerResponse])
def list_interviewers(db: Session = Depends(get_db)):
    """List all interviewers with skills."""
    interviewers = (
        db.query(Interviewer)
        .options(joinedload(Interviewer.skills))
        .all()
    )
    return [_interviewer_to_response(inv) for inv in interviewers]


@router.post("", response_model=InterviewerResponse)
def create_interviewer(data: InterviewerCreate, db: Session = Depends(get_db)):
    """Create interviewer with skills (ORM only)."""
    try:
        inv = Interviewer(
            name=data.name,
            email=data.email,
            level=data.level,
            experience_range=data.experience_range,
        )
        db.add(inv)
        db.flush()

        for sk in data.skills:
            db.add(
                InterviewerSkill(
                    interviewer_id=inv.id,
                    skill_name=sk.skill_name,
                    skill_type=sk.skill_type,
                )
            )
        db.commit()
        db.refresh(inv)
        inv = (
            db.query(Interviewer)
            .options(joinedload(Interviewer.skills))
            .filter(Interviewer.id == inv.id)
            .first()
        )
        return _interviewer_to_response(inv)
    except (DataError, IntegrityError) as e:
        db.rollback()
        _handle_db_error(e)


@router.get("/{interviewer_id}", response_model=InterviewerResponse)
def get_interviewer(interviewer_id: int, db: Session = Depends(get_db)):
    """Get one interviewer by ID."""
    inv = (
        db.query(Interviewer)
        .options(joinedload(Interviewer.skills))
        .filter(Interviewer.id == interviewer_id)
        .first()
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Interviewer not found")
    return _interviewer_to_response(inv)


@router.put("/{interviewer_id}", response_model=InterviewerResponse)
def update_interviewer(
    interviewer_id: int,
    data: InterviewerCreate,
    db: Session = Depends(get_db),
):
    """Update interviewer; replace skills."""
    inv = db.query(Interviewer).filter(Interviewer.id == interviewer_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Interviewer not found")

    try:
        inv.name = data.name
        inv.email = data.email
        inv.level = data.level
        inv.experience_range = data.experience_range

        # Replace skills (delete existing, add new)
        db.query(InterviewerSkill).filter(InterviewerSkill.interviewer_id == inv.id).delete()
        db.flush()

        for sk in data.skills:
            db.add(
                InterviewerSkill(
                    interviewer_id=inv.id,
                    skill_name=sk.skill_name,
                    skill_type=sk.skill_type,
                )
            )
        db.commit()
        db.refresh(inv)
        inv = (
            db.query(Interviewer)
            .options(joinedload(Interviewer.skills))
            .filter(Interviewer.id == inv.id)
            .first()
        )
        return _interviewer_to_response(inv)
    except (DataError, IntegrityError) as e:
        db.rollback()
        _handle_db_error(e)


@router.delete("/{interviewer_id}")
def delete_interviewer(interviewer_id: int, db: Session = Depends(get_db)):
    """Delete interviewer (cascade deletes skills)."""
    inv = db.query(Interviewer).filter(Interviewer.id == interviewer_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Interviewer not found")
    db.delete(inv)
    db.commit()
    return {"ok": True}
