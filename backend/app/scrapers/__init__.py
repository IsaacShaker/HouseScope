"""
Scraper package initialization
"""

from .base_scraper import BaseScraper
from .redfin_scraper import RedfinScraper


__all__ = [
    "BaseScraper",
    "RedfinScraper",
]
