# models/rule.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from models.base import Base

class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pattern = Column(String, nullable=False)           # What to look for in the description
    clean_name = Column(String, nullable=False)        # Human-readable merchant name
    account_number = Column(String, nullable=False)    # e.g. "6005"
    account_name = Column(String, nullable=False)      # e.g. "Wages"
    is_active = Column(Boolean, default=True)          # Toggle without deleting
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<Rule(pattern='{self.pattern}', clean_name='{self.clean_name}', account_number='{self.account_number}')>"