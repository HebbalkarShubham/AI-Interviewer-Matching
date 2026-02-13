# Matching service: find_best_interviewers by skills only (ORM only)
from sqlalchemy.orm import Session, joinedload

from app.models import Interviewer, InterviewerSkill


def _normalize_skill(s: str) -> str:
    return s.strip().lower() if s else ""


def find_best_interviewers(
    db: Session,
    required_skills: list[str],
    top_n: int = 5,
) -> list[dict]:
    """
    Find top interviewers by:
    - having at least one required skill
    - score = skill_match_count * 10
    - sorted by score descending, return top_n.
    """
    if not required_skills:
        return []

    req_skills_normalized = [_normalize_skill(s) for s in required_skills if _normalize_skill(s)]
    if not req_skills_normalized:
        return []

    # Load interviewers with skills (ORM only)
    interviewers = (
        db.query(Interviewer)
        .options(joinedload(Interviewer.skills))
        .all()
    )

    results = []
    for inv in interviewers:
        inv_skill_names = [_normalize_skill(s.skill_name) for s in inv.skills]
        matched_skills = [s for s in req_skills_normalized if s in inv_skill_names]
        skill_match_count = len(matched_skills)

        if skill_match_count == 0:
            continue

        score = skill_match_count * 10
        display_matched = []
        for ms in matched_skills:
            for s in inv.skills:
                if _normalize_skill(s.skill_name) == ms:
                    display_matched.append(s.skill_name)
                    break
            else:
                display_matched.append(ms)

        results.append({
            "name": inv.name,
            "email": inv.email,
            "score": score,
            "matched_skills": display_matched,
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_n]
