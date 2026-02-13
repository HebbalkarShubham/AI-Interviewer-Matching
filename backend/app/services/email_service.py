# Send email (e.g. when interviewer is selected)
import html
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

from app.config import settings


def send_email(
    to_email: str,
    subject: str,
    body_html: str,
    attachment_path: str | Path | None = None,
    attachment_filename: str | None = None,
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
    candidate_email: str | None,
    *,
    candidate_skills: list[str] | str = (),
    match_score: float = 0.0,
    matched_skills: list[str] | str = (),
    resume_text: str | None = None,
    resume_file_path: str | Path | None = None,
    resume_download_url: str | None = None,
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
