"""
Tests for Affordability Service
"""

import pytest
from decimal import Decimal
from app.services.affordability_service import AffordabilityService


class TestAffordabilityService:
    """Test suite for AffordabilityService"""
    
    def test_calculate_max_monthly_payment(self):
        """Test maximum monthly payment calculation"""
        max_payment = AffordabilityService.calculate_max_monthly_payment(
            monthly_income=Decimal("5000.00"),
            existing_debt=Decimal("300.00"),
            dti_limit=0.28
        )
        
        # Expected: (5000 * 0.28) - 300 = 1400 - 300 = 1100
        assert max_payment == Decimal("1100.00")
    
    def test_calculate_max_monthly_payment_negative(self):
        """Test max payment doesn't go negative"""
        max_payment = AffordabilityService.calculate_max_monthly_payment(
            monthly_income=Decimal("2000.00"),
            existing_debt=Decimal("1000.00"),
            dti_limit=0.28
        )
        
        # Should never be negative
        assert max_payment >= Decimal("0")
    
    def test_calculate_mortgage_payment(self):
        """Test mortgage payment calculation"""
        payment = AffordabilityService.calculate_mortgage_payment(
            principal=Decimal("200000.00"),
            annual_interest_rate=0.07,
            loan_term_years=30
        )
        
        # Payment should be reasonable (between $1000-$2000)
        assert Decimal("1000.00") < payment < Decimal("2000.00")
        
        # Rough check: for 7% over 30 years, payment should be ~$1330
        assert Decimal("1300.00") < payment < Decimal("1400.00")
    
    def test_calculate_mortgage_payment_zero_interest(self):
        """Test mortgage with zero interest rate"""
        payment = AffordabilityService.calculate_mortgage_payment(
            principal=Decimal("240000.00"),
            annual_interest_rate=0.0,
            loan_term_years=30
        )
        
        # Expected: 240000 / (30 * 12) = 240000 / 360 = 666.67
        expected = Decimal("240000.00") / Decimal("360")
        assert abs(payment - expected) < Decimal("1.00")
    
    def test_calculate_property_tax(self):
        """Test property tax calculation"""
        tax = AffordabilityService.calculate_property_tax(
            home_price=Decimal("200000.00"),
            tax_rate=0.012  # 1.2%
        )
        
        # Expected: (200000 * 0.012) / 12 = 2400 / 12 = 200
        assert tax == Decimal("200.00")
    
    def test_calculate_insurance(self):
        """Test insurance calculation"""
        insurance = AffordabilityService.calculate_insurance(
            home_price=Decimal("200000.00"),
            insurance_rate=0.005  # 0.5%
        )
        
        # Expected: (200000 * 0.005) / 12 = 1000 / 12 = 83.33
        expected = Decimal("200000.00") * Decimal("0.005") / Decimal("12")
        assert abs(insurance - expected) < Decimal("0.01")
    
    def test_calculate_pmi_with_20_percent_down(self):
        """Test PMI is zero with 20% down payment"""
        pmi = AffordabilityService.calculate_pmi(
            loan_amount=Decimal("160000.00"),
            down_payment_pct=0.20,
            pmi_rate=0.005
        )
        
        assert pmi == Decimal("0")
    
    def test_calculate_pmi_with_10_percent_down(self):
        """Test PMI is calculated with 10% down payment"""
        pmi = AffordabilityService.calculate_pmi(
            loan_amount=Decimal("180000.00"),
            down_payment_pct=0.10,
            pmi_rate=0.005
        )
        
        # Expected: (180000 * 0.005) / 12 = 900 / 12 = 75
        assert pmi > Decimal("0")
        expected = Decimal("180000.00") * Decimal("0.005") / Decimal("12")
        assert abs(pmi - expected) < Decimal("0.01")
    
    def test_calculate_monthly_payment_breakdown(self):
        """Test complete monthly payment breakdown"""
        breakdown = AffordabilityService.calculate_monthly_payment_breakdown(
            home_price=Decimal("250000.00"),
            down_payment_pct=0.20,
            interest_rate=0.07,
            loan_term_years=30
        )
        
        # Check all components exist
        assert "principal_interest" in breakdown
        assert "property_tax" in breakdown
        assert "insurance" in breakdown
        assert "pmi" in breakdown
        assert "total" in breakdown
        
        # All should be positive
        assert breakdown["principal_interest"] > Decimal("0")
        assert breakdown["property_tax"] > Decimal("0")
        assert breakdown["insurance"] > Decimal("0")
        assert breakdown["pmi"] == Decimal("0")  # 20% down = no PMI
        
        # Total should equal sum of components
        calculated_total = (
            breakdown["principal_interest"] +
            breakdown["property_tax"] +
            breakdown["insurance"] +
            breakdown["pmi"]
        )
        assert abs(breakdown["total"] - calculated_total) < Decimal("0.01")
    
    def test_calculate_max_home_price(self):
        """Test maximum home price calculation"""
        max_price = AffordabilityService.calculate_max_home_price(
            max_monthly_payment=Decimal("1500.00"),
            down_payment_pct=0.20,
            interest_rate=0.07,
            loan_term_years=30
        )
        
        # Should return a reasonable price
        assert Decimal("150000.00") < max_price < Decimal("300000.00")
        
        # Verify by calculating payment for this price
        breakdown = AffordabilityService.calculate_monthly_payment_breakdown(
            max_price,
            0.20,
            0.07,
            30
        )
        
        # Payment should be close to target
        assert abs(breakdown["total"] - Decimal("1500.00")) < Decimal("50.00")
    
    def test_get_affordability_range(self):
        """Test complete affordability analysis"""
        result = AffordabilityService.get_affordability_range(
            monthly_income=Decimal("5000.00"),
            existing_debt=Decimal("350.00"),
            down_payment_pct=0.20,
            interest_rate=0.07
        )
        
        # Check all fields exist
        assert "max_home_price" in result
        assert "safe_price_range_min" in result
        assert "safe_price_range_max" in result
        assert "down_payment_amount" in result
        assert "loan_amount" in result
        assert "monthly_payment_breakdown" in result
        assert "dti_ratio" in result
        assert "recommended_cash_reserves" in result
        
        # Verify relationships
        assert result["safe_price_range_min"] < result["safe_price_range_max"]
        assert result["safe_price_range_max"] == result["max_home_price"]
        
        # Safe min should be 80% of max
        expected_min = result["max_home_price"] * Decimal("0.80")
        assert abs(result["safe_price_range_min"] - expected_min) < Decimal("1.00")
        
        # Down payment should be correct percentage
        expected_down = result["max_home_price"] * Decimal("0.20")
        assert abs(result["down_payment_amount"] - expected_down) < Decimal("1.00")
        
        # Loan amount should be price minus down payment
        expected_loan = result["max_home_price"] - result["down_payment_amount"]
        assert abs(result["loan_amount"] - expected_loan) < Decimal("1.00")
        
        # DTI should be reasonable
        assert 0 <= result["dti_ratio"] <= 50
    
    def test_affordability_with_high_debt(self):
        """Test affordability with high existing debt"""
        result = AffordabilityService.get_affordability_range(
            monthly_income=Decimal("3000.00"),
            existing_debt=Decimal("1200.00"),  # High debt
            down_payment_pct=0.20,
            interest_rate=0.07
        )
        
        # Should still return valid results
        assert result["max_home_price"] > Decimal("0")
        
        # But price should be lower due to high debt
        # With $3000 income and $1200 debt, max housing payment is very limited
        assert result["max_home_price"] < Decimal("200000.00")
