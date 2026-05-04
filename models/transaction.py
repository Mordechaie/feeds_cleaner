# models/transaction.py
from sqlalchemy import Column, Integer, String, Float, Date, Boolean, DateTime
from sqlalchemy.sql import func
from models.base import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)                # Transaction date
    raw_description = Column(String, nullable=False)   # Original bank description
    clean_description = Column(String, nullable=True)  # After normalization
    amount = Column(Float, nullable=False)             # Transaction amount
    account = Column(String, nullable=True)            # Matched chart of accounts category
    source = Column(String, nullable=True)             # e.g. "Chase", "Amex", "BofA"
    transaction_type = Column(String, nullable=True)   # e.g. ACH_DEBIT, DEBIT_CARD
    is_cleaned = Column(Boolean, default=False)        # Has it been processed yet?
    is_matched = Column(Boolean, default=False)        # Was an account found for it?
    created_at = Column(DateTime, default=func.now())
    transaction_type = Column(String, nullable=True)   # e.g. ACH_DEBIT, DEBIT_CARD
    def __repr__(self):
        return f"<Transaction(date='{self.date}', raw_description='{self.raw_description}', amount={self.amount})>"