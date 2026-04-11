from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base


class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.id"))
    anomaly_type = Column(String, nullable=False)  # duplicate, unusual_amount, missing_data, etc.
    severity = Column(String, default="medium")  # low, medium, high, critical
    description = Column(Text, nullable=False)
    confidence_score = Column(Numeric(5, 4))  # 0.0000 to 1.0000
    detected_data = Column(JSON)  # Store the data that triggered the anomaly
    ai_analysis = Column(Text)  # AI-generated explanation
    status = Column(String, default="detected")  # detected, reviewed, resolved, dismissed
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    review_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    file = relationship("File", back_populates="anomalies")
    transaction = relationship("Transaction", back_populates="anomalies")
    reviewer = relationship("User", foreign_keys=[reviewed_by])