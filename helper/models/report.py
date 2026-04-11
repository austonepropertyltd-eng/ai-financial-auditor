from sqlalchemy import Column, Integer, String, Float
from helper.core.database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    total = Column(Float)
    average = Column(Float)
    vat = Column(Float)
    wht = Column(Float)
    cit = Column(Float)