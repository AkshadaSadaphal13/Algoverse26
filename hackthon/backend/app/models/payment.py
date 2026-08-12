from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    payer_wallet = Column(String, nullable=True)
    receiver_wallet = Column(String, nullable=True)
    amount_usdc = Column(Float, nullable=True)
    asset_id = Column(Integer, nullable=True)
    network = Column(String, nullable=False, default="testnet")
    payment_status = Column(String, nullable=False, default="pending")
    transaction_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)
    settled_at = Column(DateTime(timezone=True), nullable=True)

    job = relationship("Job", back_populates="payments")
