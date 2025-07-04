from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime, text
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

from .base import Base
from .association import job_resume_association

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
        index=True,
    )

    raw_job_association = relationship(
        "ProcessedJob", back_populates="raw_job", uselist=False
    )


class ProcessedJob(Base):
    __tablename__ = "processed_jobs"

    job_id = Column(
        String,
        ForeignKey("jobs.job_id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    job_title = Column(String, nullable=False)
    company_profile = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    date_posted = Column(String, nullable=True)
    employment_type = Column(String, nullable=True)
    job_summary = Column(Text, nullable=False)
    key_responsibilities = Column(JSON, nullable=True)
    qualifications = Column(JSON, nullable=True)
    compensation_and_benfits = Column(JSON, nullable=True)
    application_info = Column(JSON, nullable=True)
    extracted_keywords = Column(JSON, nullable=True)
    processed_at = Column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
        index=True,
    )

    raw_job = relationship("Job", back_populates="raw_job_association")

    # many-to-many relationship in job and resume
    processed_resumes = relationship(
        "ProcessedResume",
        secondary=job_resume_association,
        back_populates="processed_jobs",
    )