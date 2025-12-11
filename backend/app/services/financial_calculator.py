"""
Financial Calculator Service
Computes key financial metrics from user transaction data
"""

from decimal import Decimal
from typing import Dict, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.account import Account
from app.models.transaction import Transaction


class FinancialCalculator:
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_assets_liabilities(self, user_id: int) -> tuple[Decimal, Decimal]:
        """
        Calculate user's assets and liabilities separately
        Returns (assets, liabilities)
        """
        accounts = self.db.query(Account).filter(Account.user_id == user_id).all()
        
        assets = Decimal("0")
        liabilities = Decimal("0")
        
        for account in accounts:
            if account.account_type in ["checking", "savings", "investment"]:
                assets += account.balance
            elif account.account_type in ["credit", "loan"]:
                liabilities += abs(account.balance)
        
        return assets, liabilities
    
    def calculate_net_worth(self, user_id: int) -> Decimal:
        """
        Calculate user's net worth (assets - liabilities)
        
        Assets: checking, savings accounts (positive balance)
        Liabilities: credit cards, loans (negative balance or debt accounts)
        """
        assets, liabilities = self.calculate_assets_liabilities(user_id)
        return assets - liabilities
    
    def calculate_monthly_income(self, user_id: int, months: int = 3) -> Decimal:
        """
        Calculate average monthly income over the last N months
        Income = positive transactions in checking/savings accounts
        """
        start_date = datetime.now() - timedelta(days=months * 30)
        
        result = self.db.query(func.sum(Transaction.amount)).join(Account).filter(
            Account.user_id == user_id,
            Account.account_type.in_(["checking", "savings"]),
            Transaction.date >= start_date.date(),
            Transaction.amount > 0,
            Transaction.category.in_(["salary", "income", "paycheck", "deposit"])
        ).scalar()
        
        total_income = result or Decimal("0")
        return total_income / Decimal(str(months))
    
    def calculate_monthly_expenses(self, user_id: int, months: int = 3) -> Decimal:
        """
        Calculate average monthly expenses over the last N months
        Expenses = negative transactions (excluding transfers)
        """
        start_date = datetime.now() - timedelta(days=months * 30)
        
        result = self.db.query(func.sum(Transaction.amount)).join(Account).filter(
            Account.user_id == user_id,
            Account.account_type.in_(["checking", "credit"]),
            Transaction.date >= start_date.date(),
            Transaction.amount < 0,
            ~Transaction.category.in_(["transfer", "payment"])
        ).scalar()
        
        total_expenses = abs(result or Decimal("0"))
        return total_expenses / Decimal(str(months))
    
    def calculate_savings_rate(self, monthly_income: Decimal, monthly_expenses: Decimal) -> float:
        """
        Calculate savings rate as percentage
        Savings Rate = (Income - Expenses) / Income
        """
        if monthly_income <= 0:
            return 0.0
        
        savings = monthly_income - monthly_expenses
        return float((savings / monthly_income) * 100)
    
    def calculate_emergency_buffer(self, user_id: int, monthly_expenses: Decimal) -> float:
        """
        Calculate emergency buffer in months
        Buffer = Total Liquid Cash / Monthly Expenses
        """
        liquid_accounts = self.db.query(func.sum(Account.balance)).filter(
            Account.user_id == user_id,
            Account.account_type.in_(["checking", "savings"])
        ).scalar()
        
        total_cash = liquid_accounts or Decimal("0")
        
        if monthly_expenses <= 0:
            return 0.0
        
        return float(total_cash / monthly_expenses)
    
    def calculate_dti_ratio(self, user_id: int, monthly_income: Decimal) -> float:
        """
        Calculate Debt-to-Income ratio
        DTI = Total Monthly Debt Payments / Gross Monthly Income
        """
        # Get monthly debt payments (credit cards, loans)
        debt_accounts = self.db.query(Account).filter(
            Account.user_id == user_id,
            Account.account_type.in_(["credit", "loan"])
        ).all()
        
        # Estimate monthly payment (simple: 3% of balance for credit, 1% for loans)
        monthly_debt = Decimal("0")
        for account in debt_accounts:
            if account.account_type == "credit":
                monthly_debt += abs(account.balance) * Decimal("0.03")
            else:  # loan
                monthly_debt += abs(account.balance) * Decimal("0.01")
        
        if monthly_income <= 0:
            return 0.0
        
        return float((monthly_debt / monthly_income) * 100)
    
    def get_expense_breakdown(self, user_id: int, months: int = 3) -> List[Dict]:
        """
        Get expense breakdown by category
        Returns list of {category, amount, percentage}
        """
        start_date = datetime.now() - timedelta(days=months * 30)
        
        results = self.db.query(
            Transaction.category,
            func.sum(Transaction.amount).label("total")
        ).join(Account).filter(
            Account.user_id == user_id,
            Transaction.date >= start_date.date(),
            Transaction.amount < 0
        ).group_by(Transaction.category).all()
        
        # Calculate total expenses
        total_expenses = sum(abs(row.total) for row in results)
        
        if total_expenses == 0:
            return []
        
        breakdown = []
        for row in results:
            amount = abs(row.total)
            breakdown.append({
                "category": row.category or "Uncategorized",
                "amount": amount,
                "percentage": float((amount / total_expenses) * 100)
            })
        
        # Sort by amount descending
        breakdown.sort(key=lambda x: x["amount"], reverse=True)
        
        return breakdown
    
    def get_income_breakdown(self, user_id: int, months: int = 3) -> List[Dict]:
        """
        Get income breakdown by category
        Returns list of {category, amount, percentage}
        """
        start_date = datetime.now() - timedelta(days=months * 30)
        
        results = self.db.query(
            Transaction.category,
            func.sum(Transaction.amount).label("total")
        ).join(Account).filter(
            Account.user_id == user_id,
            Transaction.date >= start_date.date(),
            Transaction.amount > 0
        ).group_by(Transaction.category).all()
        
        # Calculate total income
        total_income = sum(row.total for row in results)
        
        if total_income == 0:
            return []
        
        breakdown = []
        for row in results:
            amount = row.total
            breakdown.append({
                "category": row.category or "Uncategorized",
                "amount": amount,
                "percentage": float((amount / total_income) * 100)
            })
        
        # Sort by amount descending
        breakdown.sort(key=lambda x: x["amount"], reverse=True)
        
        return breakdown
    
    def compute_all_metrics(self, user_id: int) -> Dict:
        """
        Compute all financial metrics at once
        Returns comprehensive financial snapshot
        """
        monthly_income = self.calculate_monthly_income(user_id)
        monthly_expenses = self.calculate_monthly_expenses(user_id)
        net_worth = self.calculate_net_worth(user_id)
        
        return {
            "net_worth": net_worth,
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "savings_rate": self.calculate_savings_rate(monthly_income, monthly_expenses),
            "emergency_buffer_months": self.calculate_emergency_buffer(user_id, monthly_expenses),
            "dti_ratio": self.calculate_dti_ratio(user_id, monthly_income),
            "calculated_at": datetime.utcnow()
        }
