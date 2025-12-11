"""
Tests for Financial Calculator Service
"""

import pytest
from decimal import Decimal
from app.services.financial_calculator import FinancialCalculator


class TestFinancialCalculator:
    """Test suite for FinancialCalculator service"""
    
    def test_calculate_net_worth(self, db, sample_accounts):
        """Test net worth calculation"""
        calculator = FinancialCalculator(db)
        user_id = sample_accounts["checking"].user_id
        
        net_worth = calculator.calculate_net_worth(user_id)
        
        # Expected: 5000 (checking) + 15000 (savings) - 2500 (credit) = 17500
        assert net_worth == Decimal("17500.00")
    
    def test_calculate_monthly_income(self, db, sample_transactions):
        """Test monthly income calculation"""
        calculator = FinancialCalculator(db)
        user_id = sample_transactions[0].account.user_id
        
        monthly_income = calculator.calculate_monthly_income(user_id, months=1)
        
        # Should find the salary transaction
        assert monthly_income > Decimal("0")
        assert monthly_income == Decimal("3500.00")
    
    def test_calculate_monthly_expenses(self, db, sample_transactions):
        """Test monthly expense calculation"""
        calculator = FinancialCalculator(db)
        user_id = sample_transactions[0].account.user_id
        
        monthly_expenses = calculator.calculate_monthly_expenses(user_id, months=1)
        
        # Should be positive (expenses are stored as negative)
        assert monthly_expenses > Decimal("0")
    
    def test_calculate_savings_rate(self, db):
        """Test savings rate calculation"""
        calculator = FinancialCalculator(db)
        
        # Test case: $3500 income, $2100 expenses
        # Savings rate = (3500 - 2100) / 3500 * 100 = 40%
        rate = calculator.calculate_savings_rate(
            Decimal("3500.00"),
            Decimal("2100.00")
        )
        
        assert rate == 40.0
    
    def test_calculate_savings_rate_zero_income(self, db):
        """Test savings rate with zero income"""
        calculator = FinancialCalculator(db)
        
        rate = calculator.calculate_savings_rate(
            Decimal("0"),
            Decimal("1000.00")
        )
        
        assert rate == 0.0
    
    def test_calculate_emergency_buffer(self, db, sample_accounts):
        """Test emergency buffer calculation"""
        calculator = FinancialCalculator(db)
        user_id = sample_accounts["checking"].user_id
        
        # Monthly expenses: $2000
        buffer = calculator.calculate_emergency_buffer(
            user_id,
            Decimal("2000.00")
        )
        
        # Cash available: 5000 + 15000 = 20000
        # Buffer: 20000 / 2000 = 10 months
        assert buffer == 10.0
    
    def test_calculate_dti_ratio(self, db, sample_accounts):
        """Test DTI ratio calculation"""
        calculator = FinancialCalculator(db)
        user_id = sample_accounts["checking"].user_id
        
        # Monthly income: $5000
        dti = calculator.calculate_dti_ratio(
            user_id,
            Decimal("5000.00")
        )
        
        # Credit debt: 2500 * 0.03 = 75
        # DTI: (75 / 5000) * 100 = 1.5%
        assert dti > 0
        assert dti < 10  # Should be reasonable
    
    def test_get_expense_breakdown(self, db, sample_transactions):
        """Test expense breakdown by category"""
        calculator = FinancialCalculator(db)
        user_id = sample_transactions[0].account.user_id
        
        breakdown = calculator.get_expense_breakdown(user_id, months=1)
        
        # Should have categories
        assert len(breakdown) > 0
        
        # Each item should have required fields
        for item in breakdown:
            assert "category" in item
            assert "amount" in item
            assert "percentage" in item
            assert item["amount"] > 0
            assert 0 <= item["percentage"] <= 100
        
        # Percentages should sum to ~100%
        total_pct = sum(item["percentage"] for item in breakdown)
        assert 99 <= total_pct <= 101  # Allow small rounding errors
    
    def test_compute_all_metrics(self, db, sample_accounts, sample_transactions):
        """Test computing all metrics at once"""
        calculator = FinancialCalculator(db)
        user_id = sample_accounts["checking"].user_id
        
        metrics = calculator.compute_all_metrics(user_id)
        
        # Check all expected keys are present
        assert "net_worth" in metrics
        assert "monthly_income" in metrics
        assert "monthly_expenses" in metrics
        assert "savings_rate" in metrics
        assert "emergency_buffer_months" in metrics
        assert "dti_ratio" in metrics
        assert "calculated_at" in metrics
        
        # Verify values are reasonable
        assert metrics["net_worth"] > Decimal("0")
        assert metrics["monthly_income"] >= Decimal("0")
        assert metrics["monthly_expenses"] >= Decimal("0")
        assert 0 <= metrics["savings_rate"] <= 100
        assert metrics["emergency_buffer_months"] >= 0
        assert metrics["dti_ratio"] >= 0
