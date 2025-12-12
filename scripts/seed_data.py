#!/usr/bin/env python3
"""
Seed database with sample data for testing
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import User, Account, Transaction, Property

def seed_sample_data():
    """Seed database with sample data"""
    db = SessionLocal()
    
    try:
        print("Seeding sample data...")
        
        # Create sample user
        user = User(
            email="demo@housescope.com",
            hashed_password=hash_password("demo123"),
            full_name="Demo User",
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.flush()
        print(f"✓ Created user: {user.email}")
        
        # Create sample accounts
        checking = Account(
            user_id=user.id,
            account_type="checking",
            institution_name="Sample Bank",
            balance=Decimal("5000.00"),
            last_synced=datetime.utcnow()
        )
        
        savings = Account(
            user_id=user.id,
            account_type="savings",
            institution_name="Sample Bank",
            balance=Decimal("15000.00"),
            last_synced=datetime.utcnow()
        )
        
        credit = Account(
            user_id=user.id,
            account_type="credit",
            institution_name="Credit Card Co",
            balance=Decimal("-2500.00"),
            last_synced=datetime.utcnow()
        )
        
        db.add_all([checking, savings, credit])
        db.flush()
        print(f"✓ Created {3} accounts")
        
        # Create sample transactions
        categories = ["salary", "groceries", "rent", "utilities", "entertainment", "transport"]
        merchants = ["Employer", "Grocery Store", "Landlord", "Electric Co", "Netflix", "Gas Station"]
        
        transactions = []
        for i in range(30):
            date = datetime.now() - timedelta(days=i)
            
            # Income transaction every 15 days
            if i % 15 == 0:
                trans = Transaction(
                    account_id=checking.id,
                    date=date.date(),
                    amount=Decimal("3500.00"),
                    category="salary",
                    merchant="Employer",
                    description="Paycheck"
                )
                transactions.append(trans)
            
            # Random expense
            else:
                category = random.choice(categories[1:])
                merchant = random.choice(merchants[1:])
                amount = Decimal(str(random.uniform(-200, -20)))
                
                trans = Transaction(
                    account_id=checking.id if random.random() > 0.3 else credit.id,
                    date=date.date(),
                    amount=amount,
                    category=category,
                    merchant=merchant,
                    description=f"{category.capitalize()} purchase"
                )
                transactions.append(trans)
        
        db.add_all(transactions)
        print(f"✓ Created {len(transactions)} transactions")
        
        # Create sample properties
        properties = [
            Property(
                source="manual",
                address="123 Main St",
                city="Pittsburgh",
                state="PA",
                zip_code="15213",
                price=Decimal("250000.00"),
                beds=3,
                baths=2.0,
                sqft=1500,
                year_built=2010,
                property_type="house",
                estimated_rent=Decimal("1800.00")
            ),
            Property(
                source="manual",
                address="456 Oak Ave",
                city="Pittsburgh",
                state="PA",
                zip_code="15232",
                price=Decimal("180000.00"),
                beds=2,
                baths=1.5,
                sqft=1100,
                year_built=2015,
                property_type="condo",
                estimated_rent=Decimal("1400.00")
            ),
            Property(
                source="manual",
                address="789 Elm St",
                city="Pittsburgh",
                state="PA",
                zip_code="15224",
                price=Decimal("320000.00"),
                beds=4,
                baths=2.5,
                sqft=2000,
                year_built=2018,
                property_type="house",
                estimated_rent=Decimal("2200.00")
            ),
        ]
        
        db.add_all(properties)
        print(f"✓ Created {len(properties)} sample properties")
        
        db.commit()
        print("\n✅ Sample data seeded successfully!")
        print("\nDemo User Credentials:")
        print("  Email: demo@housescope.com")
        print("  Password: demo123")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_sample_data()
