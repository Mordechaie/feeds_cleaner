# models/rule.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from models.base import Base

class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    raw_pattern = Column(String, nullable=False)       # The pattern to match against
    clean_name = Column(String, nullable=True)         # What to rename it to
    account = Column(String, nullable=True)            # Account to assign if matched
    is_active = Column(Boolean, default=True)          # Toggle rules without deleting
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<Rule(raw_pattern='{self.raw_pattern}', clean_name='{self.clean_name}')>"