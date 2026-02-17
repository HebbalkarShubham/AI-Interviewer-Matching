# Interview respond (accept/reject by token from email link)
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.database import get_db
from app.models import Interview
from app.services.email_service import send_interview_response_notification

router = APIRouter(prefix="/interviews", tags=["interviews"])


def _is_expired(expiry) -> bool:
    if not expiry:
        return False
    exp = expiry if expiry.tzinfo else expiry.replace(tzinfo=timezone.utc)
    return exp < datetime.now(timezone.utc)


@router.get("/respond", response_class=HTMLResponse)
def respond_to_interview(
    token: str = Query(..., description="Secure token from email"),
    action: str = Query(..., description="accept or reject"),
    db: Session = Depends(get_db),
):
    """
    Called when interviewer clicks Accept or Reject in email.
    Validates token and expiry, updates interview status, notifies HR.
    Interviewer can change their choice; HR gets an email each time.
    Returns a minimal page with the message.
    """
    if action not in ("accept", "reject"):
        raise HTTPException(status_code=400, detail="action must be 'accept' or 'reject'")

    interview = (
        db.query(Interview)
        .options(
            joinedload(Interview.interviewer),
            joinedload(Interview.candidate),
        )
        .filter(Interview.secure_token == token)
        .first()
    )
    if not interview:
        return _html_page("Invalid link", "This link is invalid or has already been used.", "error")

    if _is_expired(interview.token_expiry):
        return _html_page("Link expired", "This link has expired. Please contact HR to reschedule.", "error")

    interview.status = "ACCEPTED" if action == "accept" else "REJECTED"
    db.commit()

    notify_to = settings.SMTP_USER or settings.EMAIL_FROM
    if notify_to:
        interview_date_str = interview.date.isoformat() if hasattr(interview.date, "isoformat") else str(interview.date)
        interview_time_str = (
            interview.time.strftime("%H:%M") if hasattr(interview.time, "strftime") else str(interview.time)
        )
        send_interview_response_notification(
            to_email=notify_to,
            interviewer_name=interview.interviewer.name if interview.interviewer else "N/A",
            interviewer_email=interview.interviewer.email if interview.interviewer else "N/A",
            candidate_name=interview.candidate.name if interview.candidate else None,
            candidate_email=interview.candidate.email if interview.candidate else None,
            interview_date=interview_date_str,
            interview_time=interview_time_str,
            accepted=(action == "accept"),
        )

    if action == "accept":
        return _done_page("This interview is Accepted.", "You can close this tab.")
    return _done_page("You have rejected this interview.", "You can close this tab.")


def _done_page(message: str, sub: str) -> HTMLResponse:
    """Minimal success page: one line + close hint, no buttons."""
    html_content = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"/><title>Done</title></head>
<body style="margin:0;padding:2rem;background:#f5f6fa;font-family:Arial,sans-serif;text-align:center;">
  <p style="font-size:1.1rem;color:#333;">{message}</p>
  <p style="font-size:0.9rem;color:#666;">{sub}</p>
</body>
</html>
"""
    return HTMLResponse(content=html_content)


def _html_page(title: str, message: str, kind: str) -> HTMLResponse:
    """Minimal error page for invalid/expired links only."""
    color = "#3b82f6" if kind == "info" else "#ef4444"
    html_content = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"/><title>{title}</title></head>
<body style="margin:0;padding:0;background:#f5f6fa;font-family:Arial,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;">
  <div style="background:white;padding:2rem;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,0.1);max-width:420px;text-align:center;">
    <h2 style="color:{color};margin-top:0;">{title}</h2>
    <p style="color:#333;line-height:1.6;">{message}</p>
  </div>
</body>
</html>
"""
    return HTMLResponse(content=html_content)
