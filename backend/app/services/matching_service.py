# Candidate-based matching: score candidate vs each interviewer by skill overlap (ORM)
# Used by GET /candidates/{id}/matches. Interviewer now has .skills as relationship.
import re
from app.models import Interviewer
from app.models.candidate import Candidate
from app.services.ai_service import explain_match


def normalize_skill(s: str) -> str:
    return s.lower().strip() if s else ""


def get_interviewer_skill_list(interviewer: Interviewer) -> list[str]:
    """Get list of skill names from interviewer (new: InterviewerSkill relationship)."""
    if hasattr(interviewer, "skills"):
        # New model: interviewer.skills is list of InterviewerSkill
        if isinstance(interviewer.skills, list):
            return [normalize_skill(s.skill_name) for s in interviewer.skills]
        # Legacy: skills was a comma-separated string
        if isinstance(interviewer.skills, str):
            parts = re.split(r"[,;]", interviewer.skills)
            return [normalize_skill(p) for p in parts if p.strip()]
    return []


def get_interviewer_skills_display(interviewer: Interviewer) -> str:
    """String of skills for display in MatchResult."""
    names = get_interviewer_skill_list(interviewer)
    return ", ".join(names) if names else ""


def get_candidate_skill_list(candidate: Candidate) -> list[str]:
    return [normalize_skill(s.skill) for s in candidate.skills]


def compute_match_score(candidate_skills: list[str], interviewer_skills: list[str]) -> tuple[float, list[str]]:
    if not candidate_skills:
        return 0.0, []
    cand_set = set(candidate_skills)
    intr_set = set(interviewer_skills)
    matched = list(cand_set & intr_set)
    score = (len(matched) / len(cand_set)) * 100.0
    return round(score, 1), matched


def get_ranked_matches(
    candidate: Candidate,
    interviewers: list[Interviewer],
    include_explanation: bool = True,
) -> list[dict]:
    """
    For a candidate, score against each interviewer by skill overlap.
    Works with new Interviewer model (skills as relationship).
    """
    cand_skills = get_candidate_skill_list(candidate)
    results = []

    for inv in interviewers:
        inv_skills = get_interviewer_skill_list(inv)
        score, matched = compute_match_score(cand_skills, inv_skills)
        if score <= 0:
            continue
        explanation = None
        if include_explanation:
            explanation = explain_match(cand_skills, inv_skills, score)

        results.append({
            "interviewer_id": inv.id,
            "name": inv.name,
            "email": inv.email,
            "skills": get_interviewer_skills_display(inv),
            "score": score,
            "matched_skills": matched,
            "explanation": explanation,
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results
