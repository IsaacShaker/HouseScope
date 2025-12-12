"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Union
from datetime import datetime, date
from decimal import Decimal


# ============================================================================
# Authentication Schemas
# ============================================================================

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Account Schemas
# ============================================================================

class AccountBase(BaseModel):
    account_type: str
    institution_name: str
    account_name: Optional[str] = None
    balance: Decimal = Field(default=Decimal("0"))
    credit_limit: Optional[Decimal] = None
    interest_rate: Optional[float] = None


class AccountCreate(AccountBase):
    plaid_account_id: Optional[str] = None


class AccountUpdate(BaseModel):
    account_type: Optional[str] = None
    institution_name: Optional[str] = None
    account_name: Optional[str] = None
    balance: Optional[Decimal] = None
    credit_limit: Optional[Decimal] = None
    interest_rate: Optional[float] = None


class AccountResponse(AccountBase):
    id: int
    user_id: int
    last_synced: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Transaction Schemas
# ============================================================================

class TransactionBase(BaseModel):
    date: date
    amount: Decimal
    category: Optional[str] = None
    merchant: Optional[str] = None
    description: Optional[str] = None


class TransactionCreate(TransactionBase):
    account_id: int


class TransactionUpdate(BaseModel):
    account_id: Optional[int] = None
    date: Optional[Union[date, str]] = None
    amount: Optional[Decimal] = None
    category: Optional[str] = None
    merchant: Optional[str] = None
    description: Optional[str] = None


class TransactionResponse(TransactionBase):
    id: int
    account_id: int
    
    class Config:
        from_attributes = True


# ============================================================================
# Financial Dashboard Schemas
# ============================================================================

class FinancialMetrics(BaseModel):
    net_worth: Decimal
    monthly_income: Decimal
    monthly_expenses: Decimal
    savings_rate: float
    emergency_buffer_months: float
    dti_ratio: float
    calculated_at: datetime


class ExpenseBreakdown(BaseModel):
    category: str
    amount: Decimal
    percentage: float


class FinancialDashboard(BaseModel):
    metrics: FinancialMetrics
    expense_breakdown: List[ExpenseBreakdown]
    accounts: List[AccountResponse]


# ============================================================================
# Affordability Schemas
# ============================================================================

class AffordabilityInput(BaseModel):
    monthly_income: Decimal
    existing_debt: Decimal = Field(default=Decimal("0"))
    down_payment_pct: float = Field(default=0.20, ge=0, le=1)
    interest_rate: float = Field(default=0.07)
    loan_term_years: int = Field(default=30)


class MonthlyPaymentBreakdown(BaseModel):
    principal_interest: Decimal
    property_tax: Decimal
    insurance: Decimal
    pmi: Decimal
    total: Decimal


class AffordabilityResult(BaseModel):
    max_home_price: Decimal
    safe_price_range_min: Decimal
    safe_price_range_max: Decimal
    down_payment_amount: Decimal
    loan_amount: Decimal
    monthly_payment_breakdown: MonthlyPaymentBreakdown
    dti_ratio: float
    recommended_cash_reserves: Decimal


# ============================================================================
# Property Schemas
# ============================================================================

class PropertyBase(BaseModel):
    address: str
    city: str
    state: str
    zip_code: str
    price: Decimal
    beds: int
    baths: float
    sqft: int
    year_built: Optional[int] = None
    property_type: str


class PropertyCreate(PropertyBase):
    source: str = "manual"
    listing_url: Optional[str] = None
    image_url: Optional[str] = None
    estimated_rent: Optional[Decimal] = None


class PropertyResponse(PropertyBase):
    id: int
    source: str
    listing_url: Optional[str]
    image_url: Optional[str]
    scraped_at: datetime
    homebuyer_score: Optional[int]
    investor_score: Optional[int]
    estimated_rent: Optional[Decimal]
    
    class Config:
        from_attributes = True


class PropertyScore(BaseModel):
    property_id: int
    homebuyer_score: int
    investor_score: int
    score_details: dict


# ============================================================================
# Plaid Schemas
# ============================================================================

class PlaidLinkRequest(BaseModel):
    user_id: int


class PlaidLinkResponse(BaseModel):
    link_token: str


class PlaidExchangeRequest(BaseModel):
    public_token: str


class PlaidExchangeResponse(BaseModel):
    success: bool
    accounts_synced: int


# ============================================================================
# CSV Import Schemas
# ============================================================================

class CSVImportRequest(BaseModel):
    account_id: int
    file_data: str  # Base64 encoded CSV


class CSVImportResponse(BaseModel):
    success: bool
    transactions_imported: int
    errors: List[str] = []


# ============================================================================
# Category Schemas
# ============================================================================

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)


class CategoryUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)


class CategoryResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True
