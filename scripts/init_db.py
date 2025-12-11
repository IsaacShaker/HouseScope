#!/usr/bin/env python3
"""
Database initialization script
Creates all tables and optionally seeds sample data
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.database import Base, engine
from app.models import User, Account, Transaction, Property, UserFinancial

def init_database():
    """Initialize database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully!")
    print(f"  - users")
    print(f"  - accounts")
    print(f"  - transactions")
    print(f"  - properties")
    print(f"  - user_financials")

if __name__ == "__main__":
    init_database()
