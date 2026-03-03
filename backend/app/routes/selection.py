# Select interviewer and send email; schedule interview (date/time) and send with Accept/Reject
from datetime import date, time, datetime, timedelta, timezone
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel, field_validator

from app.database import get_db
from app.models import Interviewer, Interview
from app.models.candidate import Candidate
from app.services.email_service import send_interviewer_selection_email, send_scheduled_interview_email
from app.services.matching_service import get_ranked_matches
from app.services.s3_service import get_presigned_download_url

router = APIRouter(prefix="/selection", tags=["selection"])


class SelectInterviewerRequest(BaseModel):
    candidate_id: int
    interviewer_id: int
    send_email: bool = True


class ScheduleInterviewRequest(BaseModel):
    candidate_id: int
    interviewer_id: int
    date: str  # YYYY-MM-DD
    time: str  # HH:mm or HH:mm:ss
    custom_message: Optional[str] = None

    @field_validator("date")
    @classmethod
    def date_not_past(cls, v: str) -> str:
        if not v:
            raise ValueError("Date is required")
        try:
            d = datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Invalid date format; use YYYY-MM-DD")
        if d < date.today():
            raise ValueError("Cannot select a past date")
        return v

    @field_validator("time")
    @classmethod
    def time_required(cls, v: str) -> str:
        if not (v and v.strip()):
            raise ValueError("Time is required")
        v = v.strip()
        for fmt in ("%H:%M", "%H:%M:%S"):
            try:
                datetime.strptime(v, fmt)
                return v
            except ValueError:
                continue
        raise ValueError("Invalid time format; use HH:mm or HH:mm:ss")


def _load_interviewers_with_skills(db: Session):
    return db.query(Interviewer).options(joinedload(Interviewer.skills)).all()


@router.post("/select")
def select_interviewer(
    body: SelectInterviewerRequest,
    db: Session = Depends(get_db),
):
    """
    Mark interviewer as selected for candidate. Optionally send email to interviewer
    with candidate details, match score, skills, and resume text.
    """
    candidate = (
        db.query(Candidate)
        .options(joinedload(Candidate.skills))
        .filter(Candidate.id == body.candidate_id)
        .first()
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    interviewer = db.query(Interviewer).filter(Interviewer.id == body.interviewer_id).first()
    if not interviewer:
        raise HTTPException(status_code=404, detail="Interviewer not found")

    email_sent = False
    if body.send_email:
        interviewers = _load_interviewers_with_skills(db)
        matches = get_ranked_matches(candidate, interviewers, include_explanation=False)
        match_for_interviewer = next((m for m in matches if m["interviewer_id"] == body.interviewer_id), None)
        match_score = match_for_interviewer["score"] if match_for_interviewer else 0.0
        matched_skills = match_for_interviewer.get("matched_skills", []) if match_for_interviewer else []
        candidate_skills = [s.skill for s in candidate.skills]

        resume_download_url = (
            get_presigned_download_url(candidate.resume_path, expires_in=86400)
            if candidate.resume_path else None
        )
        email_sent = send_interviewer_selection_email(
            interviewer_email=interviewer.email,
            interviewer_name=interviewer.name,
            candidate_name=candidate.name,
            candidate_email=candidate.email,
            candidate_skills=candidate_skills,
            match_score=match_score,
            matched_skills=matched_skills,
            resume_text=candidate.resume_text,
            resume_download_url=resume_download_url,
        )

    return {
        "ok": True,
        "candidate_id": body.candidate_id,
        "interviewer_id": body.interviewer_id,
        "interviewer_name": interviewer.name,
        "interviewer_email": interviewer.email,
        "email_sent": email_sent,
    }


def _parse_time(t: str) -> time:
    t = t.strip()
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            dt = datetime.strptime(t, fmt)
            return dt.time()
        except ValueError:
            continue
    raise ValueError("Invalid time")


@router.post("/schedule")
def schedule_interview(
    body: ScheduleInterviewRequest,
    db: Session = Depends(get_db),
):
    """
    Create interview record with date/time and send email to interviewer
    with Accept/Reject buttons. Token valid 24 hours.
    """
    candidate = (
        db.query(Candidate)
        .options(joinedload(Candidate.skills))
        .filter(Candidate.id == body.candidate_id)
        .first()
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    interviewer = db.query(Interviewer).filter(Interviewer.id == body.interviewer_id).first()
    if not interviewer:
        raise HTTPException(status_code=404, detail="Interviewer not found")

    interview_date = datetime.strptime(body.date, "%Y-%m-%d").date()
    interview_time = _parse_time(body.time)
    secure_token = uuid.uuid4().hex
    token_expiry = datetime.now(timezone.utc) + timedelta(hours=24)

    interview = Interview(
        interviewer_id=body.interviewer_id,
        candidate_id=body.candidate_id,
        date=interview_date,
        time=interview_time,
        status="PENDING",
        custom_message=body.custom_message or None,
        secure_token=secure_token,
        token_expiry=token_expiry,
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)

    interviewers = _load_interviewers_with_skills(db)
    matches = get_ranked_matches(candidate, interviewers, include_explanation=False)
    match_for_interviewer = next((m for m in matches if m["interviewer_id"] == body.interviewer_id), None)
    match_score = match_for_interviewer["score"] if match_for_interviewer else 0.0
    matched_skills = match_for_interviewer.get("matched_skills", []) if match_for_interviewer else []
    candidate_skills = [s.skill for s in candidate.skills]
    resume_download_url = (
        get_presigned_download_url(candidate.resume_path, expires_in=86400)
        if candidate.resume_path else None
    )

    email_sent = send_scheduled_interview_email(
        interviewer_email=interviewer.email,
        interviewer_name=interviewer.name,
        candidate_name=candidate.name,
        candidate_email=candidate.email,
        interview_date=body.date,
        interview_time=body.time,
        secure_token=secure_token,
        custom_message=body.custom_message,
        candidate_skills=candidate_skills,
        match_score=match_score,
        matched_skills=matched_skills,
        resume_download_url=resume_download_url,
    )

    return {
        "ok": True,
        "interview_id": interview.id,
        "candidate_id": body.candidate_id,
        "interviewer_id": body.interviewer_id,
        "interviewer_name": interviewer.name,
        "interviewer_email": interviewer.email,
        "date": body.date,
        "time": body.time,
        "email_sent": email_sent,
    }
