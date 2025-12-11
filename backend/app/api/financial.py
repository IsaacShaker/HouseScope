"""
Financial Metrics API endpoints.
Provides comprehensive financial analysis using FinancialCalculator and AffordabilityService.
"""
from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.financial import UserFinancial
from app.api.auth import get_current_user
from app.services.financial_calculator import FinancialCalculator
from app.services.affordability_service import AffordabilityService

router = APIRouter(prefix="/financial", tags=["Financial Metrics"])


@router.get("/dashboard")
def get_financial_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get comprehensive financial dashboard data.
    
    Returns:
    - Net worth (assets - liabilities)
    - Monthly income
    - Monthly expenses
    - Savings rate
    - Emergency fund buffer
    - Debt-to-income ratio
    - Cash flow trends
    """
    # Get user's accounts
    accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
    
    if not accounts:
        return {
            "net_worth": 0,
            "assets": 0,
            "liabilities": 0,
            "monthly_income": 0,
            "monthly_expenses": 0,
            "savings_rate": 0,
            "emergency_buffer_months": 0,
            "dti_ratio": 0,
            "message": "No accounts found. Add accounts to see financial metrics.",
        }
    
    # Get transactions for the last 90 days
    ninety_days_ago = datetime.now() - timedelta(days=90)
    account_ids = [acc.id for acc in accounts]
    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.account_id.in_(account_ids),
            Transaction.date >= ninety_days_ago,
        )
        .all()
    )
    
    # Calculate metrics using FinancialCalculator
    calculator = FinancialCalculator(accounts, transactions)
    
    net_worth = calculator.calculate_net_worth()
    monthly_income = calculator.calculate_monthly_income()
    monthly_expenses = calculator.calculate_monthly_expenses()
    savings_rate = calculator.calculate_savings_rate()
    emergency_buffer = calculator.calculate_emergency_buffer()
    dti_ratio = calculator.calculate_dti_ratio()
    
    # Get category breakdown
    expense_breakdown = calculator.get_expense_breakdown()
    income_breakdown = calculator.get_income_breakdown()
    
    return {
        "net_worth": round(net_worth, 2),
        "assets": round(calculator.total_assets, 2),
        "liabilities": round(calculator.total_liabilities, 2),
        "monthly_income": round(monthly_income, 2),
        "monthly_expenses": round(monthly_expenses, 2),
        "savings_rate": round(savings_rate * 100, 2),  # Return as percentage
        "emergency_buffer_months": round(emergency_buffer, 1),
        "dti_ratio": round(dti_ratio * 100, 2),  # Return as percentage
        "expense_breakdown": {k: round(v, 2) for k, v in expense_breakdown.items()},
        "income_breakdown": {k: round(v, 2) for k, v in income_breakdown.items()},
        "account_count": len(accounts),
        "transaction_count": len(transactions),
    }


@router.get("/affordability")
def get_home_affordability(
    down_payment_percent: float = Query(20.0, ge=0, le=100, description="Down payment percentage"),
    interest_rate: Optional[float] = Query(None, ge=0, le=20, description="Annual interest rate (%)"),
    loan_term_years: int = Query(30, ge=5, le=30, description="Loan term in years"),
    property_tax_rate: Optional[float] = Query(None, ge=0, le=5, description="Annual property tax rate (%)"),
    insurance_rate: Optional[float] = Query(None, ge=0, le=5, description="Annual insurance rate (%)"),
    hoa_monthly: float = Query(0, ge=0, description="Monthly HOA fees"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Calculate home affordability based on current financial situation.
    
    Returns:
    - Maximum affordable home price
    - Recommended safe price range
    - Required down payment
    - Monthly payment breakdown (PITI + PMI)
    - Cash reserve requirements
    - Affordability warnings and recommendations
    """
    # Get user's financial data
    accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
    
    if not accounts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No accounts found. Add accounts to calculate affordability.",
        )
    
    # Get transactions for income/expense calculation
    ninety_days_ago = datetime.now() - timedelta(days=90)
    account_ids = [acc.id for acc in accounts]
    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.account_id.in_(account_ids),
            Transaction.date >= ninety_days_ago,
        )
        .all()
    )
    
    # Calculate financial metrics
    calculator = FinancialCalculator(accounts, transactions)
    monthly_income = calculator.calculate_monthly_income()
    monthly_expenses = calculator.calculate_monthly_expenses()
    available_cash = calculator.total_assets
    
    # Get user's stored financial info (if exists)
    user_financial = db.query(UserFinancial).filter(UserFinancial.user_id == current_user.id).first()
    existing_debt_payments = user_financial.monthly_debt_payment if user_financial else 0
    
    # Calculate affordability using AffordabilityService
    affordability_service = AffordabilityService()
    
    max_price = affordability_service.calculate_max_home_price(
        monthly_income=monthly_income,
        monthly_debt_payments=existing_debt_payments,
        down_payment_percent=down_payment_percent / 100,  # Convert to decimal
        interest_rate=interest_rate / 100 if interest_rate else None,  # Convert to decimal
        loan_term_years=loan_term_years,
        property_tax_rate=property_tax_rate / 100 if property_tax_rate else None,
        insurance_rate=insurance_rate / 100 if insurance_rate else None,
        hoa_monthly=hoa_monthly,
    )
    
    # Calculate monthly payment breakdown
    payment_breakdown = affordability_service.calculate_monthly_payment(
        home_price=max_price,
        down_payment_percent=down_payment_percent / 100,
        interest_rate=interest_rate / 100 if interest_rate else None,
        loan_term_years=loan_term_years,
        property_tax_rate=property_tax_rate / 100 if property_tax_rate else None,
        insurance_rate=insurance_rate / 100 if insurance_rate else None,
        hoa_monthly=hoa_monthly,
    )
    
    # Calculate safe price range (conservative estimate)
    safe_max_price = affordability_service.calculate_safe_price_range(
        monthly_income=monthly_income,
        available_cash=available_cash,
        monthly_expenses=monthly_expenses,
        monthly_debt_payments=existing_debt_payments,
        down_payment_percent=down_payment_percent / 100,
        interest_rate=interest_rate / 100 if interest_rate else None,
    )
    
    # Required down payment
    down_payment_amount = max_price * (down_payment_percent / 100)
    safe_down_payment = safe_max_price * (down_payment_percent / 100)
    
    # Cash reserve requirements (6 months of expenses)
    required_reserves = monthly_expenses * 6
    total_cash_needed = down_payment_amount + required_reserves
    safe_cash_needed = safe_down_payment + required_reserves
    
    # Warnings and recommendations
    warnings = []
    recommendations = []
    
    if down_payment_percent < 20:
        warnings.append("Down payment less than 20% requires PMI, increasing monthly costs")
        recommendations.append("Consider saving for a 20% down payment to avoid PMI")
    
    if available_cash < total_cash_needed:
        warnings.append(f"Insufficient cash reserves. Need ${total_cash_needed:,.2f}, have ${available_cash:,.2f}")
        recommendations.append("Build emergency fund before purchasing")
    
    dti_ratio = calculator.calculate_dti_ratio()
    if dti_ratio > 0.43:
        warnings.append(f"DTI ratio ({dti_ratio*100:.1f}%) exceeds recommended 43%")
        recommendations.append("Reduce debt payments before purchasing")
    
    if calculator.calculate_emergency_buffer() < 6:
        warnings.append(f"Emergency fund covers only {calculator.calculate_emergency_buffer():.1f} months")
        recommendations.append("Build 6+ months of emergency reserves")
    
    return {
        "max_home_price": round(max_price, 2),
        "safe_home_price": round(safe_max_price, 2),
        "recommended_range": {
            "min": round(safe_max_price * 0.8, 2),
            "max": round(safe_max_price, 2),
        },
        "down_payment": {
            "percent": down_payment_percent,
            "amount": round(down_payment_amount, 2),
            "safe_amount": round(safe_down_payment, 2),
        },
        "monthly_payment": {
            "total": round(payment_breakdown["total"], 2),
            "principal_interest": round(payment_breakdown["principal_interest"], 2),
            "property_tax": round(payment_breakdown["property_tax"], 2),
            "insurance": round(payment_breakdown["insurance"], 2),
            "pmi": round(payment_breakdown["pmi"], 2),
            "hoa": round(payment_breakdown["hoa"], 2),
        },
        "cash_requirements": {
            "down_payment": round(down_payment_amount, 2),
            "closing_costs": round(max_price * 0.03, 2),  # Estimate 3%
            "emergency_reserves": round(required_reserves, 2),
            "total_needed": round(total_cash_needed + (max_price * 0.03), 2),
            "available": round(available_cash, 2),
        },
        "financial_health": {
            "monthly_income": round(monthly_income, 2),
            "monthly_expenses": round(monthly_expenses, 2),
            "monthly_debt": round(existing_debt_payments, 2),
            "dti_ratio": round(dti_ratio * 100, 2),
            "emergency_buffer_months": round(calculator.calculate_emergency_buffer(), 1),
        },
        "warnings": warnings,
        "recommendations": recommendations,
    }


@router.post("/profile")
def update_financial_profile(
    annual_income: float,
    monthly_debt_payment: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update or create user's financial profile.
    Used for storing additional financial information not captured in accounts.
    """
    user_financial = db.query(UserFinancial).filter(UserFinancial.user_id == current_user.id).first()
    
    if user_financial:
        # Update existing
        user_financial.annual_income = annual_income
        user_financial.monthly_debt_payment = monthly_debt_payment
    else:
        # Create new
        user_financial = UserFinancial(
            user_id=current_user.id,
            annual_income=annual_income,
            monthly_debt_payment=monthly_debt_payment,
        )
        db.add(user_financial)
    
    db.commit()
    db.refresh(user_financial)
    
    return {
        "success": True,
        "message": "Financial profile updated successfully",
        "annual_income": annual_income,
        "monthly_debt_payment": monthly_debt_payment,
    }


@router.get("/profile")
def get_financial_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get user's financial profile.
    """
    user_financial = db.query(UserFinancial).filter(UserFinancial.user_id == current_user.id).first()
    
    if not user_financial:
        return {
            "annual_income": None,
            "monthly_debt_payment": None,
            "message": "No financial profile found. Create one to improve affordability calculations.",
        }
    
    return {
        "annual_income": user_financial.annual_income,
        "monthly_debt_payment": user_financial.monthly_debt_payment,
    }
