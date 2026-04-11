from sqlalchemy import Column, Integer, String, Float
from helper.database import Base

class TaxRecord(Base):
    __tablename__ = "tax_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    tax_year = Column(Integer)
    tax_period = Column(String)
    tax_type = Column(String)
    amount = Column(Float)
    tax_rate = Column(Float)
    taxable_amount = Column(Float)
    tax_amount = Column(Float)