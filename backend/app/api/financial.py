"""
Financial Metrics API endpoints.
Provides comprehensive financial analysis using FinancialCalculator and AffordabilityService.
"""
from typing import Optional
from datetime import datetime, timedelta
from decimal import Decimal

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
    """Get comprehensive financial dashboard data"""
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
    
    calculator = FinancialCalculator(db)
    
    assets, liabilities = calculator.calculate_assets_liabilities(current_user.id)
    net_worth = calculator.calculate_net_worth(current_user.id)
    monthly_income = calculator.calculate_monthly_income(current_user.id)
    monthly_expenses = calculator.calculate_monthly_expenses(current_user.id)
    
    savings_rate = calculator.calculate_savings_rate(monthly_income, monthly_expenses)
    emergency_buffer = calculator.calculate_emergency_buffer(current_user.id, monthly_expenses)
    dti_ratio = calculator.calculate_dti_ratio(current_user.id, monthly_income)
    
    expense_breakdown_list = calculator.get_expense_breakdown(current_user.id, months=1)
    income_breakdown_list = calculator.get_income_breakdown(current_user.id)
    
    expense_breakdown = {item["category"]: item["amount"] for item in expense_breakdown_list}
    income_breakdown = {item["category"]: item["amount"] for item in income_breakdown_list}
    account_ids = [acc.id for acc in accounts]
    ninety_days_ago = datetime.now() - timedelta(days=90)
    transaction_count = (
        db.query(Transaction)
        .filter(
            Transaction.account_id.in_(account_ids),
            Transaction.date >= ninety_days_ago,
        )
        .count()
    )
    
    return {
        "net_worth": round(net_worth, 2),
        "assets": round(assets, 2),
        "liabilities": round(liabilities, 2),
        "monthly_income": round(monthly_income, 2),
        "monthly_expenses": round(monthly_expenses, 2),
        "savings_rate": round(savings_rate, 2),  # Already as percentage
        "emergency_buffer_months": round(emergency_buffer, 1),
        "dti_ratio": round(dti_ratio, 2),  # Already as percentage
        "expense_breakdown": {k: round(v, 2) for k, v in expense_breakdown.items()},
        "income_breakdown": {k: round(v, 2) for k, v in income_breakdown.items()},
        "account_count": len(accounts),
        "transaction_count": transaction_count,
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
    """Calculate home affordability based on current financial situation"""
    accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
    
    if not accounts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No accounts found. Add accounts to calculate affordability.",
        )
    
    calculator = FinancialCalculator(db)
    monthly_income = calculator.calculate_monthly_income(current_user.id)
    monthly_expenses = calculator.calculate_monthly_expenses(current_user.id)
    assets, liabilities = calculator.calculate_assets_liabilities(current_user.id)
    available_cash = assets
    
    user_financial = db.query(UserFinancial).filter(UserFinancial.user_id == current_user.id).first()
    existing_debt_payments = Decimal(str(user_financial.monthly_debt_payment)) if user_financial else Decimal("0")
    
    interest_rate_decimal = interest_rate / 100 if interest_rate else None
    
    max_monthly_payment = AffordabilityService.calculate_max_monthly_payment(
        monthly_income,
        existing_debt_payments,
        dti_limit=0.28
    )
    
    max_monthly_payment_for_mortgage = max_monthly_payment - Decimal(str(hoa_monthly or 0))
    
    max_price = AffordabilityService.calculate_max_home_price(
        max_monthly_payment_for_mortgage,
        down_payment_percent / 100,
        interest_rate_decimal,
        loan_term_years
    )
    
    safe_max_price = max_price * Decimal("0.8")
    
    payment_breakdown = AffordabilityService.calculate_monthly_payment_breakdown(
        max_price,
        down_payment_percent / 100,
        interest_rate_decimal,
        loan_term_years
    )
    payment_breakdown["hoa"] = Decimal(str(hoa_monthly or 0))
    payment_breakdown["total"] = payment_breakdown["total"] + payment_breakdown["hoa"]
    
    # Required down payment
    down_payment_amount = max_price * Decimal(str(down_payment_percent / 100))
    safe_down_payment = safe_max_price * Decimal(str(down_payment_percent / 100))
    
    # Cash reserve requirements (6 months of expenses)
    required_reserves = monthly_expenses * 6
    closing_costs = max_price * Decimal("0.03")  # Estimate 3% closing costs
    total_cash_needed = down_payment_amount + required_reserves + closing_costs
    
    # Warnings and recommendations
    warnings = []
    recommendations = []
    
    if down_payment_percent < 20:
        warnings.append("Down payment less than 20% requires PMI, increasing monthly costs")
        recommendations.append("Consider saving for a 20% down payment to avoid PMI")
    
    if available_cash < total_cash_needed:
        warnings.append(f"Insufficient cash reserves. Need ${total_cash_needed:,.2f}, have ${available_cash:,.2f}")
        recommendations.append("Build emergency fund before purchasing")
    
    dti_ratio = calculator.calculate_dti_ratio(current_user.id, monthly_income)
    if dti_ratio > 43:  # Already as percentage
        warnings.append(f"DTI ratio ({dti_ratio:.1f}%) exceeds recommended 43%")
        recommendations.append("Reduce debt payments before purchasing")
    
    emergency_buffer = calculator.calculate_emergency_buffer(current_user.id, monthly_expenses)
    if emergency_buffer < 6:
        warnings.append(f"Emergency fund covers only {emergency_buffer:.1f} months")
        recommendations.append("Build 6+ months of emergency reserves")
    
    return {
        "max_home_price": float(round(max_price, 2)),
        "safe_home_price": float(round(safe_max_price, 2)),
        "recommended_range": {
            "min": float(round(safe_max_price * Decimal("0.8"), 2)),
            "max": float(round(safe_max_price, 2)),
        },
        "down_payment": {
            "percent": down_payment_percent,
            "amount": float(round(down_payment_amount, 2)),
            "safe_amount": float(round(safe_down_payment, 2)),
        },
        "monthly_payment": {
            "total": float(round(payment_breakdown["total"], 2)),
            "principal_interest": float(round(payment_breakdown["principal_interest"], 2)),
            "property_tax": float(round(payment_breakdown["property_tax"], 2)),
            "insurance": float(round(payment_breakdown["insurance"], 2)),
            "pmi": float(round(payment_breakdown["pmi"], 2)),
            "hoa": float(round(payment_breakdown["hoa"], 2)),
        },
        "cash_requirements": {
            "down_payment": float(round(down_payment_amount, 2)),
            "closing_costs": float(round(closing_costs, 2)),
            "emergency_reserves": float(round(required_reserves, 2)),
            "total_needed": float(round(total_cash_needed, 2)),
            "available": float(round(available_cash, 2)),
        },
        "financial_health": {
            "monthly_income": float(round(monthly_income, 2)),
            "monthly_expenses": float(round(monthly_expenses, 2)),
            "monthly_debt": float(round(existing_debt_payments, 2)),
            "dti_ratio": round(dti_ratio, 2),  # Already as percentage
            "emergency_buffer_months": round(emergency_buffer, 1),
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
        user_financial.annual_income = annual_income
        user_financial.monthly_debt_payment = monthly_debt_payment
    else:
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
