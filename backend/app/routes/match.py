# POST /match - find best interviewers by skills only
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.interviewer import MatchRequest, MatchResultItem
from app.services.matching import find_best_interviewers

router = APIRouter(prefix="/match", tags=["match"])


@router.post("", response_model=List[MatchResultItem])
def match_interviewers(
    body: MatchRequest,
    db: Session = Depends(get_db),
):
    """
    Find top 5 interviewers that have at least one required skill.
    Score = skill_match_count * 10.
    """
    results = find_best_interviewers(
        db=db,
        required_skills=body.skills,
        top_n=5,
    )
    return [MatchResultItem(**r) for r in results]
