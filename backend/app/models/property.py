"""
Property database model
"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime
from datetime import datetime
from app.core.database import Base


class Property(Base):
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False)  # zillow, realtor, manual
    address = Column(String, nullable=False)
    city = Column(String, nullable=False, index=True)
    state = Column(String, nullable=False, index=True)
    zip_code = Column(String, nullable=False)
    price = Column(Numeric(12, 2), nullable=False, index=True)
    beds = Column(Integer, nullable=False)
    baths = Column(Numeric(3, 1), nullable=False)
    sqft = Column(Integer, nullable=False)
    year_built = Column(Integer, nullable=True)
    property_type = Column(String, nullable=False)  # house, condo, townhouse
    listing_url = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    homebuyer_score = Column(Integer, nullable=True, index=True)
    investor_score = Column(Integer, nullable=True, index=True)
    estimated_rent = Column(Numeric(12, 2), nullable=True)
    
    def __repr__(self):
        return f"<Property(id={self.id}, address={self.address}, price={self.price})>"
