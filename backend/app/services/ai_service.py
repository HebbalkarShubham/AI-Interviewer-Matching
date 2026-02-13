# OpenAI integration - extract skills, vision (images), match explanation
import base64
import json
import logging
import re
from openai import OpenAI

from app.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

# Fallback: common skills to detect when OpenAI is unavailable (e.g. quota exceeded)
_COMMON_SKILLS = [
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin",
    "React", "Angular", "Vue", "Node.js", "Django", "Flask", "FastAPI", "Spring", "Express",
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "AWS", "Azure", "GCP", "Docker", "Kubernetes",
    "Git", "Linux", "REST", "GraphQL", "Machine Learning", "TensorFlow", "PyTorch", "Data Analysis",
    "Agile", "Scrum", "JIRA", "CI/CD", "Testing", "API", "Microservices", "HTML", "CSS", "R",
]


def extract_text_with_vision(file_bytes: bytes, mime_type: str) -> str:
    """
    Use OpenAI Vision (GPT-4o-mini) to extract all text from an image resume.
    Supports PNG, JPEG, GIF, WebP. Use for image files (e.g. scanned resume, screenshot).
    """
    if not client or not file_bytes:
        return ""
    allowed = ("image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp")
    if mime_type not in allowed:
        if "png" in mime_type or "image" in mime_type:
            mime_type = "image/png"
        else:
            mime_type = "image/jpeg"
    b64 = base64.standard_b64encode(file_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{b64}"
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all text from this resume image. Preserve structure (sections, bullet points, line breaks). Return only the extracted text, no commentary or headings like 'Extracted text:'.",
                        },
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
            max_tokens=4096,
        )
        out = response.choices[0].message.content
        return (out or "").strip()
    except Exception as e:
        logging.warning("Vision text extraction failed: %s", e)
        return ""


def _extract_skills_fallback(resume_text: str) -> list[dict]:
    """
    When OpenAI is unavailable (quota, key missing), extract skills by matching
    common tech/professional terms in the resume. Returns same format as AI.
    """
    if not resume_text or not resume_text.strip():
        return []
    text_lower = resume_text.lower()
    found = []
    seen = set()
    for skill in _COMMON_SKILLS:
        if skill.lower() in seen:
            continue
        pattern = r"(?<![a-zA-Z])" + re.escape(skill) + r"(?![a-zA-Z])"
        if re.search(pattern, text_lower, re.IGNORECASE):
            found.append({"skill": skill, "confidence": 0.7})
            seen.add(skill.lower())
    return found


def _normalize_skill_item(item) -> dict | None:
    """Convert API response item to {skill, confidence}. Handles 'skill' or 'name' key, or plain string."""
    if isinstance(item, str) and item.strip():
        return {"skill": item.strip(), "confidence": None}
    if isinstance(item, dict):
        name = item.get("skill") or item.get("name") or item.get("title")
        if name is None and len(item) == 1:
            name = next((v for v in item.values() if isinstance(v, str)), None)
        if name and str(name).strip():
            conf = item.get("confidence")
            if conf is not None and not isinstance(conf, (int, float)):
                conf = None
            return {"skill": str(name).strip(), "confidence": conf}
    return None


def extract_name_email_from_resume(resume_text: str) -> dict:
    """
    Extract candidate name and email from resume text.
    Returns {"name": str | None, "email": str | None}. Uses OpenAI when available, else regex fallback for email.
    """
    if not resume_text or not resume_text.strip():
        return {"name": None, "email": None}

    # Fallback: regex for email (common in resumes)
    email_re = re.compile(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    )
    fallback_email = None
    m = email_re.search(resume_text)
    if m:
        fallback_email = m.group(0).strip()

    if not client:
        # Name fallback: use first non-empty line that looks like a name (no @, reasonable length)
        fallback_name = None
        for line in resume_text.splitlines():
            line = line.strip()
            if not line or "@" in line or len(line) > 80:
                continue
            if line.lower().startswith(("resume", "curriculum", "cv", "http", "www")):
                continue
            fallback_name = line[:255]
            break
        return {"name": fallback_name, "email": fallback_email}

    prompt = """From this resume text, extract the candidate's full name and email address.
Return only a JSON object with two keys: "name" (string, the person's name) and "email" (string, email address).
If not found, use null for that key. Example: {"name": "John Doe", "email": "john@example.com"}

Resume text:
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You extract name and email from resumes. Reply only with valid JSON."},
                {"role": "user", "content": prompt + resume_text[:4000]},
            ],
            temperature=0.1,
        )
        text = (response.choices[0].message.content or "").strip()
        if not text:
            return {"name": None, "email": fallback_email}
        if "```" in text:
            text = text.split("```")[1]
        if text.strip().lower().startswith("json"):
            text = text.strip()[4:].strip()
        data = json.loads(text)
        name = data.get("name") if isinstance(data.get("name"), str) else None
        email = data.get("email") if isinstance(data.get("email"), str) else None
        if name:
            name = name.strip()[:255] or None
        if email:
            email = email.strip()[:255] or None
        return {
            "name": name or None,
            "email": email or fallback_email,
        }
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logging.warning("Name/email extraction failed: %s", e)
    except Exception as e:
        logging.warning("Name/email extraction failed: %s", e)
    return {"name": None, "email": fallback_email}


def extract_skills_from_resume(resume_text: str) -> list[dict]:
    """
    Use OpenAI to extract skills from resume text.
    If API fails (e.g. 429 quota) or key is missing, falls back to keyword matching.
    Returns list of {"skill": str, "confidence": float}.
    """
    if not resume_text or not resume_text.strip():
        return []

    def use_fallback(reason: str) -> list[dict]:
        logging.warning("Using fallback skill extraction: %s", reason)
        return _extract_skills_fallback(resume_text)

    if not client:
        return use_fallback("OPENAI_API_KEY not set")

    prompt = """Extract technical and professional skills from this resume text.
Return a JSON array of objects with "skill" (string) and "confidence" (number 0-1).
Only include clear skills. Example: [{"skill": "Python", "confidence": 0.9}, {"skill": "React", "confidence": 0.85}].

Resume text:
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You extract skills from resumes. Reply only with valid JSON array."},
                {"role": "user", "content": prompt + resume_text[:6000]},
            ],
            temperature=0.2,
        )
        text = (response.choices[0].message.content or "").strip()
        if not text:
            return use_fallback("empty AI response")
        if "```" in text:
            text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
        data = json.loads(text)
        if not isinstance(data, list):
            return use_fallback("AI response was not a list")
        out = []
        for item in data:
            normalized = _normalize_skill_item(item)
            if normalized:
                out.append(normalized)
        return out if out else use_fallback("AI returned no skills")
    except json.JSONDecodeError as e:
        return use_fallback(f"invalid JSON: {e}")
    except Exception as e:
        return use_fallback(str(e))


def explain_match(candidate_skills: list[str], interviewer_skills: list[str], score: float) -> str:
    """
    Generate a short AI explanation for why this interviewer matches the candidate.
    """
    if not client:
        return f"Match score: {score:.0f}% based on {len(candidate_skills)} candidate skills and interviewer skills."

    cand = ", ".join(candidate_skills[:15]) or "None listed"
    intr = ", ".join(interviewer_skills[:15]) or "None"

    prompt = f"""In 1-2 sentences, explain why this interviewer (skills: {intr}) is a good match for a candidate with skills: {cand}. Match score: {score:.0f}%. Be concise and professional."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return f"Strong match ({score:.0f}%) based on overlapping skills."
