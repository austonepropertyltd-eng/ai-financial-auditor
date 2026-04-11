from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from helper.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="USD")
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    description = Column(Text)
    category = Column(String, nullable=False)  # income, expense, transfer, etc.
    subcategory = Column(String)
    account_type = Column(String)  # checking, savings, credit_card, etc.
    reference_number = Column(String, unique=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="transactions")
    anomalies = relationship("Anomaly", back_populates="transaction")
    tax_records = relationship("TaxRecord", back_populates="transaction")