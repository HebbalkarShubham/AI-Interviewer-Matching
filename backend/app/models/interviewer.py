# Interviewer models - interviewers (name, email, level, experience_range) + interviewer_skills
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Interviewer(Base):
    __tablename__ = "interviewers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    level = Column(String(255), nullable=True)  # e.g. "Senior", "Lead", "Senior Lead"
    experience_range = Column(String(255), nullable=True)  # e.g. "0-2", "3-5", "5-10", "10+"

    skills = relationship(
        "InterviewerSkill",
        back_populates="interviewer",
        cascade="all, delete-orphan",
    )


class InterviewerSkill(Base):
    __tablename__ = "interviewer_skills"

    id = Column(Integer, primary_key=True, index=True)
    interviewer_id = Column(
        Integer,
        ForeignKey("interviewers.id", ondelete="CASCADE"),
        nullable=False,
    )
    skill_name = Column(String(255), nullable=False)
    skill_type = Column(String(32), nullable=False)  # "Primary" or "Secondary"

    interviewer = relationship("Interviewer", back_populates="skills")
