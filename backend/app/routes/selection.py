# Select interviewer and send email
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel

from app.database import get_db
from app.models import Interviewer
from app.models.candidate import Candidate
from app.services.email_service import send_interviewer_selection_email
from app.services.matching_service import get_ranked_matches
from app.services.s3_service import get_presigned_download_url

router = APIRouter(prefix="/selection", tags=["selection"])


class SelectInterviewerRequest(BaseModel):
    candidate_id: int
    interviewer_id: int
    send_email: bool = True


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
