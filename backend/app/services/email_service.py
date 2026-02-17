# Send email (e.g. when interviewer is selected or interview scheduled)
import html
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Optional, Union

from app.config import settings


def _base_url() -> str:
    return (settings.APP_BASE_URL or "").rstrip("/")


def send_email(
    to_email: str,
    subject: str,
    body_html: str,
    attachment_path: Optional[Union[str, Path]] = None,
    attachment_filename: Optional[str] = None,
) -> bool:
    """
    Send email via SMTP. Returns True on success.
    Optionally attach a file (e.g. resume PDF).
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email
    msg.attach(MIMEText(body_html, "html"))

    if attachment_path:
        path = Path(attachment_path)
        if path.is_file():
            name = attachment_filename or path.name
            with open(path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", "attachment", filename=name)
            msg.attach(part)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, to_email, msg.as_string())
        return True
    except Exception:
        return False


def send_interviewer_selection_email(
    interviewer_email: str,
    interviewer_name: str,
    candidate_name: str,
    candidate_email: Optional[str],
    *,
    candidate_skills: Union[List[str], str] = (),
    match_score: float = 0.0,
    matched_skills: Union[List[str], str] = (),
    resume_text: Optional[str] = None,
    resume_file_path: Optional[Union[str, Path]] = None,
    resume_download_url: Optional[str] = None,
) -> bool:
    """Send notification to interviewer with candidate details and resume (text + optional S3 download link)."""
    subject = f"Interview Assignment: Candidate {candidate_name or 'Unknown'}"
    name = html.escape(interviewer_name or "Interviewer")
    candidate = html.escape(candidate_name or "N/A")
    cand_email = html.escape(candidate_email or "N/A")
    skills_str = ", ".join(matched_skills) if isinstance(matched_skills, list) else (matched_skills or "N/A")
    skills_str = html.escape(skills_str)
    score = f"{match_score:.1f}" if match_score is not None else "N/A"
    cand_skills_str = ", ".join(candidate_skills) if isinstance(candidate_skills, list) else (candidate_skills or "N/A")
    cand_skills_str = html.escape(cand_skills_str)

    resume_section = ""
    if resume_download_url:
        resume_section += f"""
        <tr>
          <td style="padding-top:12px;">
            <b>Resume file:</b>
            <a href="{html.escape(resume_download_url)}" style="color:#2563eb;">Download resume (PDF/file)</a>
            <span style="color:#888;font-size:11px;"> (link valid 24 hours)</span>
          </td>
        </tr>"""
    body = f"""
    <!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
</head>

<body style="margin:0;padding:0;background:#f5f6fa;font-family:Arial,Helvetica,sans-serif;">

  <table align="center" width="600" cellpadding="0" cellspacing="0"
         style="background:white;margin-top:40px;border-radius:8px;padding:30px;box-shadow:0 2px 8px rgba(0,0,0,0.1);">

    <tr>
      <td align="center">
        <h2 style="color:#2c3e50;margin-bottom:10px;">
          🎯 Interview Panel Assignment
        </h2>
      </td>
    </tr>

    <tr>
      <td style="padding:20px 0;color:#333;font-size:14px;line-height:1.6;">

        Hi <b>{name}</b>,<br><br>

        You have been selected as the <b>Interviewer</b> for the following candidate.

        <br><br>

        <table width="100%" cellpadding="8" cellspacing="0"
               style="border:1px solid #eee;background:#fafafa;font-size:13px;">
          <tr>
            <td><b>Candidate Name</b></td>
            <td>{candidate}</td>
          </tr>
          <tr>
            <td><b>Candidate Email</b></td>
            <td>{cand_email}</td>
          </tr>
          <tr>
            <td><b>Candidate Skills</b></td>
            <td>{cand_skills_str}</td>
          </tr>
          <tr>
            <td><b>Matched Skills (with you)</b></td>
            <td>{skills_str}</td>
          </tr>
          <tr>
            <td><b>Match Score</b></td>
            <td>{score}%</td>
          </tr>
          {resume_section}
        </table>

        <br>

        Please connect with HR for scheduling the interview.

        <br><br>

        Thanks,<br>
        <b>AI Interview Matching System</b>

      </td>
    </tr>

    <tr>
      <td align="center" style="font-size:12px;color:#888;padding-top:20px;">
        This is an automated email. Please do not reply.
      </td>
    </tr>

  </table>

</body>
</html>
"""
    attach_path = Path(resume_file_path) if resume_file_path else None
    attach_name = attach_path.name if attach_path and attach_path.is_file() else None
    return send_email(
        interviewer_email,
        subject,
        body,
        attachment_path=attach_path,
        attachment_filename=attach_name,
    )


def send_scheduled_interview_email(
    interviewer_email: str,
    interviewer_name: str,
    candidate_name: str,
    candidate_email: Optional[str],
    interview_date: str,
    interview_time: str,
    secure_token: str,
    custom_message: Optional[str] = None,
    *,
    candidate_skills: Union[List[str], str] = (),
    match_score: float = 0.0,
    matched_skills: Union[List[str], str] = (),
    resume_download_url: Optional[str] = None,
) -> bool:
    """Send scheduled interview notification to interviewer with Accept/Reject buttons."""
    base = _base_url()
    accept_link = f"{base}/api/interviews/respond?token={html.escape(secure_token)}&action=accept"
    reject_link = f"{base}/api/interviews/respond?token={html.escape(secure_token)}&action=reject"

    subject = f"Scheduled Interview: {candidate_name or 'Candidate'} – {interview_date} at {interview_time}"
    name = html.escape(interviewer_name or "Interviewer")
    candidate = html.escape(candidate_name or "N/A")
    cand_email = html.escape(candidate_email or "N/A")
    skills_str = ", ".join(matched_skills) if isinstance(matched_skills, list) else (matched_skills or "N/A")
    skills_str = html.escape(skills_str)
    score = f"{match_score:.1f}" if match_score is not None else "N/A"
    cand_skills_str = ", ".join(candidate_skills) if isinstance(candidate_skills, list) else (candidate_skills or "N/A")
    cand_skills_str = html.escape(cand_skills_str)
    date_esc = html.escape(interview_date)
    time_esc = html.escape(interview_time)
    custom_esc = html.escape(custom_message) if custom_message else ""

    resume_section = ""
    if resume_download_url:
        resume_section += f"""
        <tr>
          <td style="padding-top:12px;">
            <b>Resume:</b>
            <a href="{html.escape(resume_download_url)}" style="color:#2563eb;">Download resume</a>
            <span style="color:#888;font-size:11px;"> (link valid 24 hours)</span>
          </td>
        </tr>"""

    body = f"""
    <!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
</head>
<body style="margin:0;padding:0;background:#f5f6fa;font-family:Arial,Helvetica,sans-serif;">
  <table align="center" width="600" cellpadding="0" cellspacing="0"
         style="background:white;margin-top:40px;border-radius:8px;padding:30px;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
    <tr>
      <td align="center">
        <h2 style="color:#2c3e50;margin-bottom:10px;">Interview Scheduled</h2>
      </td>
    </tr>
    <tr>
      <td style="padding:20px 0;color:#333;font-size:14px;line-height:1.6;">
        Hi <b>{name}</b>,<br><br>
        An interview has been scheduled with you for the following candidate.
        <br><br>
        <table width="100%" cellpadding="8" cellspacing="0" style="border:1px solid #eee;background:#fafafa;font-size:13px;">
          <tr><td><b>Candidate</b></td><td>{candidate}</td></tr>
          <tr><td><b>Candidate Email</b></td><td>{cand_email}</td></tr>
          <tr><td><b>Date</b></td><td>{date_esc}</td></tr>
          <tr><td><b>Time</b></td><td>{time_esc}</td></tr>
          <tr><td><b>Candidate Skills</b></td><td>{cand_skills_str}</td></tr>
          <tr><td><b>Matched Skills</b></td><td>{skills_str}</td></tr>
          <tr><td><b>Match Score</b></td><td>{score}%</td></tr>
          {resume_section}
        </table>
        {f'<p style="margin-top:12px;"><b>Message:</b> {custom_esc}</p>' if custom_esc else ''}
        <p style="margin-top:20px;">Please confirm or decline this interview:</p>
        <p style="margin:12px 0;">
          <a href="{accept_link}" style="display:inline-block;margin-right:12px;padding:10px 20px;background:#22c55e;color:white;text-decoration:none;border-radius:6px;font-weight:600;">Accept</a>
          <a href="{reject_link}" style="display:inline-block;padding:10px 20px;background:#ef4444;color:white;text-decoration:none;border-radius:6px;font-weight:600;">Reject</a>
        </p>
        <p style="font-size:12px;color:#888;">(Links expire in 24 hours.)</p>
        <br>
        Thanks,<br><b>AI Interview Matching System</b>
      </td>
    </tr>
  </table>
</body>
</html>
"""
    return send_email(interviewer_email, subject, body)


def send_interview_response_notification(
    to_email: str,
    *,
    interviewer_name: str,
    interviewer_email: str,
    candidate_name: Optional[str] = None,
    candidate_email: Optional[str] = None,
    interview_date: str,
    interview_time: str,
    accepted: bool,
) -> bool:
    """
    Notify the system (e.g. SMTP_USER / HR) when an interviewer accepts or rejects an interview.
    Includes all interviewer and interview details.
    """
    action = "accepted" if accepted else "rejected"
    subject = f"Interview {action.capitalize()}: {interviewer_name} – {interview_date} at {interview_time}"
    name = html.escape(interviewer_name or "Interviewer")
    i_email = html.escape(interviewer_email or "N/A")
    cand_name = html.escape(candidate_name or "N/A")
    cand_email = html.escape(candidate_email or "N/A")
    date_esc = html.escape(interview_date)
    time_esc = html.escape(interview_time)
    color = "#22c55e" if accepted else "#ef4444"
    body = f"""
    <!DOCTYPE html>
<html>
<head><meta charset="UTF-8"/></head>
<body style="margin:0;padding:0;background:#f5f6fa;font-family:Arial,sans-serif;">
  <table align="center" width="600" cellpadding="0" cellspacing="0"
         style="background:white;margin:40px auto;border-radius:8px;padding:30px;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
    <tr>
      <td>
        <h2 style="color:{color};margin-top:0;">
          Interview {action.capitalize()}
        </h2>
        <p style="color:#333;font-size:14px;line-height:1.6;">
          This interviewer has <strong>{action}</strong> the interview with the following details.
        </p>
        <table width="100%" cellpadding="10" cellspacing="0" style="border:1px solid #eee;background:#fafafa;font-size:13px;">
          <tr><td><b>Interviewer Name</b></td><td>{name}</td></tr>
          <tr><td><b>Interviewer Email</b></td><td>{i_email}</td></tr>
          <tr><td><b>Candidate Name</b></td><td>{cand_name}</td></tr>
          <tr><td><b>Candidate Email</b></td><td>{cand_email}</td></tr>
          <tr><td><b>Interview Date</b></td><td>{date_esc}</td></tr>
          <tr><td><b>Interview Time</b></td><td>{time_esc}</td></tr>
        </table>
        <p style="font-size:12px;color:#888;margin-top:20px;">AI Interview Matching System</p>
      </td>
    </tr>
  </table>
</body>
</html>
"""
    return send_email(to_email, subject, body)
