from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(36), unique=True, nullable=False, index=True)
    original_filename = Column(String, nullable=False)
    stored_filename = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    audio_duration_seconds = Column(Float, nullable=True)
    usage_minutes = Column(Float, nullable=True)
    price_usdc = Column(Float, nullable=True)
    payment_status = Column(String, nullable=False, default="pending")
    processing_status = Column(String, nullable=False, default="uploaded")
    result_summary = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    payments = relationship("Payment", back_populates="job")
