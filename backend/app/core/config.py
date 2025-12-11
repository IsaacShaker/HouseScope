"""
Application configuration management
Loads settings from environment variables
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "HouseScope"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/housescope.db"
    
    # Plaid API
    PLAID_CLIENT_ID: str = ""
    PLAID_SECRET: str = ""
    PLAID_ENV: str = "sandbox"
    PLAID_COUNTRY_CODES: str = "US"
    PLAID_PRODUCTS: str = "transactions"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Web Scraping
    SCRAPER_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    SCRAPER_RATE_LIMIT: int = 2
    SCRAPER_MAX_RETRIES: int = 3
    SCRAPER_TIMEOUT: int = 10
    
    # Default Mortgage Assumptions
    DEFAULT_INTEREST_RATE: float = 0.07
    DEFAULT_LOAN_TERM_YEARS: int = 30
    DEFAULT_PROPERTY_TAX_RATE: float = 0.012
    DEFAULT_INSURANCE_RATE: float = 0.005
    DEFAULT_PMI_RATE: float = 0.005
    
    # Regional Settings
    DEFAULT_REGION: str = "Pittsburgh, PA"
    DEFAULT_STATE: str = "PA"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/housescope.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
