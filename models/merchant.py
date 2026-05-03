# models/merchant.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from models.base import Base

class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    raw_name = Column(String, nullable=False)          # Original name from Excel
    clean_name = Column(String, nullable=True)         # Normalized version
    account_number = Column(String, nullable=False) 
    account_name = Column(String, nullable=False)           # Chart of accounts category
    created_at = Column(DateTime, default=func.now())  # When the record was imported

    def __repr__(self):
        return f"<Merchant(raw_name='{self.raw_name}', account='{self.account}')>"