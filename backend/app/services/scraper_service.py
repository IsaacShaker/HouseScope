"""
Property scraper service
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.property import Property
from app.scrapers.redfin_scraper import RedfinScraper
import logging

logger = logging.getLogger(__name__)


class PropertyScraperService:
    """Service to manage property scraping and storage"""
    
    def __init__(self, db: Session):
        self.db = db
        self.scrapers = {
            'redfin': RedfinScraper(rate_limit=3.0, headless=False)
        }
    
    def search_and_save_properties(
        self,
        city: str,
        state: str,
        sources: Optional[List[str]] = None,
        max_price: Optional[int] = None,
        min_beds: Optional[int] = None,
        min_baths: Optional[float] = None,
        property_type: Optional[str] = None
    ) -> dict:
        """Search for properties across sources and save to database"""
        if sources is None:
            sources = list(self.scrapers.keys())
        
        results = {
            'total_found': 0,
            'total_saved': 0,
            'by_source': {}
        }
        
        for source_name in sources:
            if source_name not in self.scrapers:
                logger.warning(f"Unknown scraper source: {source_name}")
                continue
            
            logger.info(f"Scraping {source_name} for {city}, {state}")
            scraper = self.scrapers[source_name]
            
            try:
                # Search for properties
                properties = scraper.search_properties(
                    city=city,
                    state=state,
                    max_price=max_price,
                    min_beds=min_beds,
                    min_baths=min_baths,
                    property_type=property_type
                )
                
                saved_count = 0
                for prop_data in properties:
                    try:
                        existing = self.db.query(Property).filter(
                            Property.address == prop_data['address'],
                            Property.city == prop_data['city'],
                            Property.state == prop_data['state']
                        ).first()
                        
                        if existing:
                            if existing.price != prop_data['price']:
                                existing.price = prop_data['price']
                                existing.scraped_at = prop_data['scraped_at']
                                logger.info(f"Updated price for {prop_data['address']}")
                        else:
                            new_property = Property(**prop_data)
                            self.db.add(new_property)
                            saved_count += 1
                            logger.info(f"Saved new property: {prop_data['address']}")
                        
                    except Exception as e:
                        logger.error(f"Error saving property: {e}")
                        continue
                
                self.db.commit()
                
                results['by_source'][source_name] = {
                    'found': len(properties),
                    'saved': saved_count
                }
                results['total_found'] += len(properties)
                results['total_saved'] += saved_count
                
                logger.info(f"{source_name}: Found {len(properties)}, Saved {saved_count}")
                
            except Exception as e:
                logger.error(f"Error scraping {source_name}: {e}")
                results['by_source'][source_name] = {
                    'error': str(e)
                }
                continue
        
        return results
    
    def get_properties(
        self,
        city: Optional[str] = None,
        state: Optional[str] = None,
        max_price: Optional[int] = None,
        min_beds: Optional[int] = None,
        min_baths: Optional[float] = None,
        property_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Property]:
        """Get properties from database with filters"""
        query = self.db.query(Property)
        
        if city:
            query = query.filter(Property.city.ilike(f"%{city}%"))
        if state:
            query = query.filter(Property.state == state.upper())
        if max_price:
            query = query.filter(Property.price <= max_price)
        if min_beds:
            query = query.filter(Property.beds >= min_beds)
        if min_baths:
            query = query.filter(Property.baths >= min_baths)
        if property_type:
            query = query.filter(Property.property_type == property_type.lower())
        
        query = query.order_by(Property.scraped_at.desc())
        
        return query.offset(offset).limit(limit).all()
    
    def get_property_by_id(self, property_id: int) -> Optional[Property]:
        """Get a specific property by ID"""
        return self.db.query(Property).filter(Property.id == property_id).first()
    
    def delete_old_properties(self, days: int = 30) -> int:
        """Delete properties older than specified days"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted = self.db.query(Property).filter(
            Property.scraped_at < cutoff_date
        ).delete()
        
        self.db.commit()
        logger.info(f"Deleted {deleted} properties older than {days} days")
        return deleted
