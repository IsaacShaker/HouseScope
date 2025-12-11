"""
UserFinancial database model - stores calculated financial snapshots
"""

from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class UserFinancial(Base):
    __tablename__ = "user_financials"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    calculated_at = Column(DateTime, default=datetime.utcnow, index=True)
    net_worth = Column(Numeric(12, 2), nullable=False)
    monthly_income = Column(Numeric(12, 2), nullable=False)
    monthly_expenses = Column(Numeric(12, 2), nullable=False)
    savings_rate = Column(Numeric(5, 2), nullable=False)  # Percentage
    emergency_buffer_months = Column(Numeric(4, 1), nullable=False)
    dti_ratio = Column(Numeric(5, 2), nullable=False)  # Percentage
    
    # Relationships
    user = relationship("User", back_populates="financials")
    
    def __repr__(self):
        return f"<UserFinancial(user_id={self.user_id}, net_worth={self.net_worth}, calculated_at={self.calculated_at})>"
