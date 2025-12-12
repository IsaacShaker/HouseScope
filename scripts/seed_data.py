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
from app.models.category import Category

def seed_sample_data():
    """Seed database with sample data"""
    db = SessionLocal()
    
    try:
        user = User(
            email="demo@housescope.com",
            hashed_password=hash_password("demo123"),
            full_name="Demo User",
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.flush()
        
        # Create default categories
        default_categories = [
            "income", "salary", "groceries", "rent", "mortgage", 
            "utilities", "transportation", "gas", "dining", "entertainment",
            "healthcare", "insurance", "shopping", "personal", "other"
        ]
        categories_objs = [
            Category(user_id=user.id, name=cat) for cat in default_categories
        ]
        db.add_all(categories_objs)
        
        # Create sample accounts
        # For a $350k house: needs ~$70k down payment (20%), good income/DTI
        checking = Account(
            user_id=user.id,
            account_type="checking",
            institution_name="Chase Bank",
            account_name="Main Checking",
            balance=Decimal("12500.00"),
            last_synced=datetime.utcnow()
        )
        
        savings = Account(
            user_id=user.id,
            account_type="savings",
            institution_name="Chase Bank",
            account_name="High Yield Savings",
            balance=Decimal("45000.00"),
            interest_rate=Decimal("4.5"),
            last_synced=datetime.utcnow()
        )
        
        investment = Account(
            user_id=user.id,
            account_type="investment",
            institution_name="Vanguard",
            account_name="Brokerage Account",
            balance=Decimal("28000.00"),
            last_synced=datetime.utcnow()
        )
        
        credit = Account(
            user_id=user.id,
            account_type="credit",
            institution_name="Chase",
            account_name="Freedom Unlimited",
            balance=Decimal("-850.00"),
            credit_limit=Decimal("15000.00"),
            interest_rate=Decimal("19.99"),
            last_synced=datetime.utcnow()
        )
        
        db.add_all([checking, savings, investment, credit])
        db.flush()
        
        # Create sample transactions
        # Annual income ~$95k to afford $350k house comfortably
        transactions = []
        
        # Generate 90 days of transactions
        for i in range(90):
            date = datetime.now() - timedelta(days=i)
            
            # Bi-weekly paycheck (every 14 days) - $3,653 = $95k/year
            if i % 14 == 0:
                trans = Transaction(
                    account_id=checking.id,
                    date=date.date(),
                    amount=Decimal("3653.00"),
                    category="salary",
                    merchant="Tech Corp LLC",
                    description="Salary - Direct Deposit"
                )
                transactions.append(trans)
            
            # Monthly rent on day 1 of each ~30 day period
            if i % 30 == 1:
                trans = Transaction(
                    account_id=checking.id,
                    date=date.date(),
                    amount=Decimal("-1650.00"),
                    category="rent",
                    merchant="Property Management Co",
                    description="Monthly Rent"
                )
                transactions.append(trans)
            
            # Monthly utilities
            if i % 30 == 3:
                transactions.extend([
                    Transaction(
                        account_id=checking.id,
                        date=date.date(),
                        amount=Decimal("-120.00"),
                        category="utilities",
                        merchant="Electric Company",
                        description="Electric Bill"
                    ),
                    Transaction(
                        account_id=checking.id,
                        date=date.date(),
                        amount=Decimal("-65.00"),
                        category="utilities",
                        merchant="Internet Provider",
                        description="Internet Service"
                    ),
                ])
            
            # Monthly subscriptions
            if i % 30 == 5:
                transactions.extend([
                    Transaction(
                        account_id=credit.id,
                        date=date.date(),
                        amount=Decimal("-15.99"),
                        category="entertainment",
                        merchant="Netflix",
                        description="Streaming Subscription"
                    ),
                    Transaction(
                        account_id=credit.id,
                        date=date.date(),
                        amount=Decimal("-12.99"),
                        category="entertainment",
                        merchant="Spotify",
                        description="Music Subscription"
                    ),
                ])
            
            # Groceries 2x per week
            if i % 3 == 0:
                amount = Decimal(str(random.uniform(-80, -150)))
                trans = Transaction(
                    account_id=credit.id,
                    date=date.date(),
                    amount=amount,
                    category="groceries",
                    merchant=random.choice(["Whole Foods", "Trader Joe's", "Giant Eagle"]),
                    description="Grocery shopping"
                )
                transactions.append(trans)
            
            # Gas every week
            if i % 7 == 0:
                amount = Decimal(str(random.uniform(-40, -65)))
                trans = Transaction(
                    account_id=credit.id,
                    date=date.date(),
                    amount=amount,
                    category="gas",
                    merchant=random.choice(["Shell", "BP", "Sheetz"]),
                    description="Gas"
                )
                transactions.append(trans)
            
            # Dining out occasionally
            if i % 4 == 0:
                amount = Decimal(str(random.uniform(-25, -85)))
                trans = Transaction(
                    account_id=credit.id,
                    date=date.date(),
                    amount=amount,
                    category="dining",
                    merchant=random.choice(["Chipotle", "Panera", "Local Restaurant", "Starbucks"]),
                    description="Dining out"
                )
                transactions.append(trans)
            
            # Monthly savings transfer
            if i % 30 == 7:
                trans = Transaction(
                    account_id=checking.id,
                    date=date.date(),
                    amount=Decimal("-1000.00"),
                    category="personal",
                    merchant="Transfer",
                    description="Savings transfer"
                )
                transactions.append(trans)
            
            # Monthly investment contribution
            if i % 30 == 8:
                trans = Transaction(
                    account_id=checking.id,
                    date=date.date(),
                    amount=Decimal("-500.00"),
                    category="personal",
                    merchant="Vanguard",
                    description="Investment contribution"
                )
                transactions.append(trans)
            
            # Occasional shopping
            if i % 12 == 0:
                amount = Decimal(str(random.uniform(-50, -200)))
                trans = Transaction(
                    account_id=credit.id,
                    date=date.date(),
                    amount=amount,
                    category="shopping",
                    merchant=random.choice(["Amazon", "Target", "Best Buy"]),
                    description="Shopping"
                )
                transactions.append(trans)
        
        db.add_all(transactions)
        
        # Create sample properties
        properties = [
            Property(
                source="manual",
                address="1247 Maple Avenue",
                city="Pittsburgh",
                state="PA",
                zip_code="15232",
                price=Decimal("350000.00"),
                beds=3,
                baths=2.0,
                sqft=1800,
                year_built=2015,
                property_type="house",
                estimated_rent=Decimal("2100.00")
            ),
            Property(
                source="manual",
                address="892 Highland Park Dr",
                city="Pittsburgh",
                state="PA",
                zip_code="15206",
                price=Decimal("285000.00"),
                beds=2,
                baths=2.0,
                sqft=1400,
                year_built=2018,
                property_type="townhouse",
                estimated_rent=Decimal("1850.00")
            ),
            Property(
                source="manual",
                address="3456 Penn Avenue",
                city="Pittsburgh",
                state="PA",
                zip_code="15201",
                price=Decimal("425000.00"),
                beds=4,
                baths=2.5,
                sqft=2200,
                year_built=2020,
                property_type="house",
                estimated_rent=Decimal("2600.00")
            ),
            Property(
                source="manual",
                address="567 Walnut Street Unit 301",
                city="Pittsburgh",
                state="PA",
                zip_code="15232",
                price=Decimal("225000.00"),
                beds=2,
                baths=1.5,
                sqft=1100,
                year_built=2010,
                property_type="condo",
                estimated_rent=Decimal("1600.00")
            ),
            Property(
                source="manual",
                address="1829 Beechwood Blvd",
                city="Pittsburgh",
                state="PA",
                zip_code="15217",
                price=Decimal("395000.00"),
                beds=3,
                baths=2.5,
                sqft=2000,
                year_built=2017,
                property_type="house",
                estimated_rent=Decimal("2400.00")
            ),
        ]
        
        db.add_all(properties)
        
        db.commit()
        print("Sample data seeded successfully")
        print("Demo credentials - Email: demo@housescope.com, Password: demo123")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_sample_data()
