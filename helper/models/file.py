from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, LargeBinary
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from helper.database import Base

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String, nullable=False)
    file_hash = Column(String, unique=True, nullable=False)
    status = Column(String, default="uploaded")  # uploaded, processing, processed, error
    processing_result = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="files")
    anomalies = relationship("Anomaly", back_populates="file")