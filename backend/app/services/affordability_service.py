"""
Affordability Service
Calculates home affordability based on financial data
"""

from decimal import Decimal
from typing import Dict
import math
from app.core.config import settings


class AffordabilityService:
    
    @staticmethod
    def calculate_max_monthly_payment(
        monthly_income: Decimal,
        existing_debt: Decimal,
        dti_limit: float = 0.28
    ) -> Decimal:
        """
        Calculate maximum monthly housing payment based on DTI ratio
        Standard: Housing costs should not exceed 28% of gross income
        """
        max_housing_payment = (monthly_income * Decimal(str(dti_limit))) - existing_debt
        return max(max_housing_payment, Decimal("0"))
    
    @staticmethod
    def calculate_mortgage_payment(
        principal: Decimal,
        annual_interest_rate: float,
        loan_term_years: int
    ) -> Decimal:
        """
        Calculate monthly mortgage payment (principal + interest)
        Formula: M = P * [r(1+r)^n] / [(1+r)^n - 1]
        """
        if annual_interest_rate == 0:
            return principal / Decimal(str(loan_term_years * 12))
        
        monthly_rate = annual_interest_rate / 12
        num_payments = loan_term_years * 12
        
        # Calculate mortgage payment
        numerator = monthly_rate * math.pow(1 + monthly_rate, num_payments)
        denominator = math.pow(1 + monthly_rate, num_payments) - 1
        
        monthly_payment = principal * Decimal(str(numerator / denominator))
        
        return monthly_payment
    
    @staticmethod
    def calculate_property_tax(home_price: Decimal, tax_rate: float) -> Decimal:
        """Calculate monthly property tax"""
        annual_tax = home_price * Decimal(str(tax_rate))
        return annual_tax / Decimal("12")
    
    @staticmethod
    def calculate_insurance(home_price: Decimal, insurance_rate: float) -> Decimal:
        """Calculate monthly homeowners insurance"""
        annual_insurance = home_price * Decimal(str(insurance_rate))
        return annual_insurance / Decimal("12")
    
    @staticmethod
    def calculate_pmi(
        loan_amount: Decimal,
        down_payment_pct: float,
        pmi_rate: float
    ) -> Decimal:
        """
        Calculate monthly PMI (Private Mortgage Insurance)
        PMI is required if down payment < 20%
        """
        if down_payment_pct >= 0.20:
            return Decimal("0")
        
        annual_pmi = loan_amount * Decimal(str(pmi_rate))
        return annual_pmi / Decimal("12")
    
    @staticmethod
    def calculate_monthly_payment_breakdown(
        home_price: Decimal,
        down_payment_pct: float,
        interest_rate: float,
        loan_term_years: int = 30
    ) -> Dict[str, Decimal]:
        """
        Calculate detailed monthly payment breakdown
        Returns dict with principal_interest, property_tax, insurance, pmi, total
        """
        down_payment = home_price * Decimal(str(down_payment_pct))
        loan_amount = home_price - down_payment
        
        # Calculate components
        principal_interest = AffordabilityService.calculate_mortgage_payment(
            loan_amount,
            interest_rate,
            loan_term_years
        )
        
        property_tax = AffordabilityService.calculate_property_tax(
            home_price,
            settings.DEFAULT_PROPERTY_TAX_RATE
        )
        
        insurance = AffordabilityService.calculate_insurance(
            home_price,
            settings.DEFAULT_INSURANCE_RATE
        )
        
        pmi = AffordabilityService.calculate_pmi(
            loan_amount,
            down_payment_pct,
            settings.DEFAULT_PMI_RATE
        )
        
        total = principal_interest + property_tax + insurance + pmi
        
        return {
            "principal_interest": principal_interest,
            "property_tax": property_tax,
            "insurance": insurance,
            "pmi": pmi,
            "total": total
        }
    
    @staticmethod
    def calculate_max_home_price(
        max_monthly_payment: Decimal,
        down_payment_pct: float,
        interest_rate: float,
        loan_term_years: int = 30
    ) -> Decimal:
        """
        Calculate maximum affordable home price
        Works backwards from monthly payment to find max price
        """
        # Use iterative approach to find home price
        # Start with rough estimate
        estimated_price = max_monthly_payment * Decimal("200")  # Rough starting point
        
        # Iterate to converge on actual price
        for _ in range(10):
            breakdown = AffordabilityService.calculate_monthly_payment_breakdown(
                estimated_price,
                down_payment_pct,
                interest_rate,
                loan_term_years
            )
            
            difference = max_monthly_payment - breakdown["total"]
            
            # Adjust estimate
            adjustment = difference * Decimal("200")
            estimated_price += adjustment
            
            # Break if close enough
            if abs(difference) < Decimal("10"):
                break
        
        return estimated_price
    
    @staticmethod
    def get_affordability_range(
        monthly_income: Decimal,
        existing_debt: Decimal,
        down_payment_pct: float = 0.20,
        interest_rate: float = None
    ) -> Dict:
        """
        Calculate complete affordability analysis
        Returns max price, safe range, payment breakdown, etc.
        """
        if interest_rate is None:
            interest_rate = settings.DEFAULT_INTEREST_RATE
        
        # Calculate max monthly payment
        max_monthly_payment = AffordabilityService.calculate_max_monthly_payment(
            monthly_income,
            existing_debt
        )
        
        # Calculate max home price
        max_home_price = AffordabilityService.calculate_max_home_price(
            max_monthly_payment,
            down_payment_pct,
            interest_rate
        )
        
        # Conservative safe range: 80-100% of max
        safe_min = max_home_price * Decimal("0.80")
        safe_max = max_home_price
        
        # Calculate breakdown for max price
        breakdown = AffordabilityService.calculate_monthly_payment_breakdown(
            max_home_price,
            down_payment_pct,
            interest_rate
        )
        
        down_payment_amount = max_home_price * Decimal(str(down_payment_pct))
        loan_amount = max_home_price - down_payment_amount
        
        # Calculate DTI ratio
        dti_ratio = float((breakdown["total"] / monthly_income) * 100)
        
        # Recommended cash reserves (6 months expenses + closing costs)
        closing_costs = max_home_price * Decimal("0.03")  # ~3% of home price
        monthly_housing = breakdown["total"]
        recommended_reserves = (monthly_housing * Decimal("6")) + closing_costs
        
        return {
            "max_home_price": max_home_price,
            "safe_price_range_min": safe_min,
            "safe_price_range_max": safe_max,
            "down_payment_amount": down_payment_amount,
            "loan_amount": loan_amount,
            "monthly_payment_breakdown": breakdown,
            "dti_ratio": dti_ratio,
            "recommended_cash_reserves": recommended_reserves
        }
