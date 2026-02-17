# Interview model - scheduled interview with token for accept/reject
from datetime import date, time
from sqlalchemy import Column, Integer, String, Date, Time, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    interviewer_id = Column(Integer, ForeignKey("interviewers.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    status = Column(String(32), nullable=False, default="PENDING")  # PENDING, ACCEPTED, REJECTED
    custom_message = Column(Text, nullable=True)
    secure_token = Column(String(64), nullable=False, unique=True, index=True)
    token_expiry = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    interviewer = relationship("Interviewer", backref="interviews")
    candidate = relationship("Candidate", backref="interviews")
