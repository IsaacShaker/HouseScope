"""
Pytest configuration and fixtures
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models import User, Account, Transaction
from app.core.security import hash_password
from datetime import datetime, timedelta
from decimal import Decimal


# Create test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_user(db):
    """Create a sample user for testing"""
    user = User(
        email="test@example.com",
        hashed_password=hash_password("testpass123"),
        created_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def sample_accounts(db, sample_user):
    """Create sample accounts for testing"""
    checking = Account(
        user_id=sample_user.id,
        account_type="checking",
        institution_name="Test Bank",
        balance=Decimal("5000.00"),
        last_synced=datetime.utcnow()
    )
    
    savings = Account(
        user_id=sample_user.id,
        account_type="savings",
        institution_name="Test Bank",
        balance=Decimal("15000.00"),
        last_synced=datetime.utcnow()
    )
    
    credit = Account(
        user_id=sample_user.id,
        account_type="credit",
        institution_name="Test Credit",
        balance=Decimal("-2500.00"),
        last_synced=datetime.utcnow()
    )
    
    db.add_all([checking, savings, credit])
    db.commit()
    db.refresh(checking)
    db.refresh(savings)
    db.refresh(credit)
    
    return {"checking": checking, "savings": savings, "credit": credit}


@pytest.fixture
def sample_transactions(db, sample_accounts):
    """Create sample transactions for testing"""
    checking = sample_accounts["checking"]
    
    transactions = []
    
    # Income transaction
    income = Transaction(
        account_id=checking.id,
        date=(datetime.now() - timedelta(days=10)).date(),
        amount=Decimal("3500.00"),
        category="salary",
        merchant="Employer",
        description="Paycheck"
    )
    transactions.append(income)
    
    # Expense transactions
    expenses = [
        Transaction(
            account_id=checking.id,
            date=(datetime.now() - timedelta(days=i)).date(),
            amount=Decimal(f"-{50 + i * 10}.00"),
            category="groceries" if i % 2 == 0 else "utilities",
            merchant=f"Merchant {i}",
            description=f"Purchase {i}"
        )
        for i in range(1, 10)
    ]
    transactions.extend(expenses)
    
    db.add_all(transactions)
    db.commit()
    
    return transactions
