from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime, text, NVARCHAR
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

from .base import Base
from .association import job_resume_association


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(String, unique=True, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
        index=True,
    )


    raw_resume_association = relationship(
        "ProcessedResume", back_populates="raw_resume", uselist=False
    )


class ProcessedResume(Base):
    __tablename__ = "processed_resumes"

    resume_id = Column(
        String,
        ForeignKey("resumes.resume_id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    personal_data = Column(JSON, nullable=False)
    experiences = Column(JSON, nullable=True)
    projects = Column(JSON, nullable=True)
    skills = Column(JSON, nullable=True)
    research_work = Column(JSON, nullable=True)
    achievements = Column(JSON, nullable=True)
    education = Column(JSON, nullable=True)
    extracted_keywords = Column(JSON, nullable=True)
    processed_at = Column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
        index=True,
    )

    raw_resume = relationship("Resume", back_populates="raw_resume_association")

    processed_jobs = relationship(
        "ProcessedJob",
        secondary=job_resume_association,
        back_populates="processed_resumes",
    )