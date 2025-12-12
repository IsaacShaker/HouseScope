"""
Base scraper class for property scraping
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import time
import logging

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for all property scrapers"""
    
    def __init__(self, rate_limit: float = 1.0):
        """Initialize scraper"""
        self.rate_limit = rate_limit
        self.last_request_time = 0
    
    def _wait_for_rate_limit(self):
        """Wait if needed to respect rate limit"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Get the name of the scraping source"""
        pass
    
    @abstractmethod
    def search_properties(
        self,
        city: str,
        state: str,
        max_price: Optional[int] = None,
        min_beds: Optional[int] = None,
        min_baths: Optional[float] = None,
        property_type: Optional[str] = None
    ) -> List[Dict]:
        """Search for properties"""
        pass
    
    def _normalize_property(self, raw_data: Dict) -> Dict:
        """Normalize property data to standard format"""
        return {
            'source': self.get_source_name(),
            'address': raw_data.get('address', ''),
            'city': raw_data.get('city', ''),
            'state': raw_data.get('state', ''),
            'zip_code': raw_data.get('zip_code', ''),
            'price': raw_data.get('price', 0),
            'beds': raw_data.get('beds', 0),
            'baths': raw_data.get('baths', 0.0),
            'sqft': raw_data.get('sqft', 0),
            'year_built': raw_data.get('year_built'),
            'property_type': raw_data.get('property_type', 'house'),
            'listing_url': raw_data.get('listing_url', ''),
            'image_url': raw_data.get('image_url', ''),
        }
