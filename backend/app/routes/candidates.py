# Candidate API - upload resume to S3, extract skills, get matches
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Candidate, CandidateSkill
from app.schemas.candidate import (
    CandidateResponse,
    CandidateSkillResponse,
    MatchResult,
)
from app.services.matching_service import get_ranked_matches
from app.services.resume_service import extract_text_from_upload
from app.services.ai_service import extract_skills_from_resume, extract_name_email_from_resume
from app.services.s3_service import upload_resume_to_s3, get_presigned_download_url, is_s3_configured
from app.models import Interviewer

router = APIRouter(prefix="/candidates", tags=["candidates"])


def _load_interviewers_with_skills(db: Session) -> list:
    """Load interviewers with skills relationship for candidate matching."""
    return db.query(Interviewer).options(joinedload(Interviewer.skills)).all()


def candidate_to_response(c: Candidate) -> CandidateResponse:
    """Map Candidate model to response with skills and optional resume download URL."""
    skills = [
        CandidateSkillResponse(skill=s.skill, confidence=s.confidence)
        for s in c.skills
    ]
    download_url = get_presigned_download_url(c.resume_path) if c.resume_path else None
    return CandidateResponse(
        id=c.id,
        name=c.name,
        email=c.email,
        resume_text=c.resume_text,
        resume_path=c.resume_path,
        resume_download_url=download_url,
        skills=skills,
    )


@router.post("/upload", response_model=CandidateResponse)
async def upload_resume(
    file: UploadFile = File(...),
    name: str | None = Form(None),
    email: str | None = Form(None),
    db: Session = Depends(get_db),
):
    """
    Upload a resume (PDF or text) to S3. Stores candidate name, email, and resume path.
    Extracts text, calls AI to get skills. Name and email are optional form fields.
    """
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {e!s}")
    if len(content) > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(status_code=400, detail="File too large")

    filename = file.filename or "resume.pdf"
    content_type = file.content_type or ""

    # Upload file to S3 first (if configured)
    resume_path = upload_resume_to_s3(content, filename, content_type or None)
    if not resume_path and is_s3_configured():
        # S3 is configured but upload failed (error already logged in s3_service)
        pass  # continue without resume_path; candidate still saved with resume_text

    text = extract_text_from_upload(content, filename, content_type)
    if not text.strip():
        text = "(No text extracted from file)"

    # Name and email: use form values if provided, else extract from resume text
    extracted = extract_name_email_from_resume(text)
    final_name = (name and name.strip()) or extracted.get("name")
    final_email = (email and email.strip()) or extracted.get("email")

    try:
        candidate = Candidate(
            name=final_name[:255] if final_name else None,
            email=final_email[:255] if final_email else None,
            resume_text=text,
            resume_path=resume_path,
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)

        extracted = extract_skills_from_resume(text)
        for item in extracted:
            skill_name = item.get("skill") if isinstance(item, dict) else str(item)
            conf = item.get("confidence") if isinstance(item, dict) else None
            if skill_name:
                cs = CandidateSkill(candidate_id=candidate.id, skill=skill_name, confidence=conf)
                db.add(cs)
        db.commit()
        candidate = db.query(Candidate).filter(Candidate.id == candidate.id).first()
        return candidate_to_response(candidate)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save candidate: {e!s}")


@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Get candidate by ID."""
    c = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate_to_response(c)


@router.get("/{candidate_id}/matches", response_model=list[MatchResult])
def get_matches(candidate_id: int, db: Session = Depends(get_db)):
    """
    Get ranked list of interviewers matched to this candidate.
    Returns score (0-100), matched skills, and AI explanation per interviewer.
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    interviewers = _load_interviewers_with_skills(db)
    results = get_ranked_matches(candidate, interviewers, include_explanation=True)
    return [MatchResult(**r) for r in results]
