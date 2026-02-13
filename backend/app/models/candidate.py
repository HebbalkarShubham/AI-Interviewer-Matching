# Candidate model - name, email, resume on S3, extracted text and skills for matching
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    # S3 path (object key) where resume file is stored (e.g. resumes/uuid/filename.pdf)
    resume_path = Column(String(512), nullable=True)
    # Extracted text from resume; used for AI skills and display
    resume_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    skills = relationship("CandidateSkill", back_populates="candidate", cascade="all, delete-orphan")


class CandidateSkill(Base):
    """Skills extracted by AI for a candidate."""
    __tablename__ = "candidate_skills"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    skill = Column(String(255), nullable=False)
    # Optional confidence 0-1 from extraction
    confidence = Column(Float, nullable=True)

    candidate = relationship("Candidate", back_populates="skills")
