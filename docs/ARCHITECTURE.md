# HouseScope - Component Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (React + Vite Frontend)                      │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                │ HTTP/REST API
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                     API GATEWAY LAYER                           │
│                      (FastAPI Router)                           │
│  ┌──────────┬──────────┬─────────────┬──────────┬──────────┐   │
│  │   Auth   │ Financial│ Affordability│Properties│  Admin   │   │
│  │ Endpoints│Endpoints │  Endpoints   │Endpoints │Endpoints │   │
│  └──────────┴──────────┴─────────────┴──────────┴──────────┘   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                       SERVICE LAYER                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Core Business Logic Services                │   │
│  ├─────────────────┬──────────────────┬───────────────────┤   │
│  │ Financial       │ Affordability    │ Deal Analysis     │   │
│  │ Calculator      │ Service          │ Service           │   │
│  │                 │                  │                   │   │
│  │ - Net worth     │ - DTI ratio      │ - HomeBuyerScore │   │
│  │ - Cash flow     │ - Max payment    │ - InvestorScore  │   │
│  │ - Savings rate  │ - Safe range     │ - Comparisons    │   │
│  └─────────────────┴──────────────────┴───────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            External Integration Services                 │   │
│  ├─────────────────┬──────────────────┬───────────────────┤   │
│  │ Plaid Service   │ Transaction Svc  │ CSV Importer      │   │
│  │                 │                  │                   │   │
│  │ - Auth link     │ - Categorization │ - Parse CSV       │   │
│  │ - Sync accounts │ - Aggregation    │ - Validation      │   │
│  │ - Transactions  │ - Analysis       │ - Import          │   │
│  └─────────────────┴──────────────────┴───────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 Web Scraping Services                    │   │
│  ├─────────────────┬──────────────────┬───────────────────┤   │
│  │ Scraper Manager │ Zillow Scraper   │ Realtor Scraper   │   │
│  │                 │                  │                   │   │
│  │ - Orchestration │ - Parse listings │ - Parse listings  │   │
│  │ - Scheduling    │ - Extract data   │ - Extract data    │   │
│  │ - Rate limiting │ - Store results  │ - Store results   │   │
│  └─────────────────┴──────────────────┴───────────────────┘   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                        DATA LAYER                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  ORM Models (SQLAlchemy)                 │   │
│  ├────────┬──────────┬──────────────┬──────────┬──────────┤   │
│  │  User  │ Account  │ Transaction  │ Property │Financial │   │
│  └────────┴──────────┴──────────────┴──────────┴──────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            Database (PostgreSQL / SQLite)                │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     EXTERNAL SERVICES                           │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │   Plaid API      │         │  Web Properties  │             │
│  │   (Sandbox)      │         │  (Zillow, etc.)  │             │
│  └──────────────────┘         └──────────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

## Component Specifications

### 1. Frontend Components

#### 1.1 Authentication Module
**Components**: `Login.jsx`, `Register.jsx`
**Purpose**: User authentication and registration
**Features**:
- Email/password login
- User registration
- JWT token management
- Protected route handling

#### 1.2 Finance Dashboard Module
**Components**: 
- `FinanceDashboard.jsx` (main container)
- `NetWorthChart.jsx`
- `ExpenseBreakdown.jsx`
- `CashFlowChart.jsx`
- `AccountList.jsx`
- `TransactionTable.jsx`

**Purpose**: Display comprehensive financial overview
**Key Visualizations**:
- Net worth over time (line chart)
- Income vs. expenses (bar chart)
- Expense categories (pie chart)
- Savings rate trend
- Emergency buffer gauge

**Data Flow**:
```
User → FinanceDashboard → financialService.getMetrics() → API → Service → DB
```

#### 1.3 Affordability Calculator Module
**Components**:
- `Affordability.jsx`
- `AffordabilityForm.jsx`
- `PriceRangeDisplay.jsx`
- `MonthlyBreakdown.jsx`

**Purpose**: Calculate and display home buying affordability
**Features**:
- Input sliders (income, debts, down payment %)
- Real-time calculation
- Safe price range display
- Monthly payment breakdown
- Scenario comparison

**Calculations**:
```javascript
maxMonthlyPayment = (monthlyIncome * 0.28) - existingDebtPayments
maxHomePrice = calculateWithMortgage(maxMonthlyPayment, interestRate, loanTerm)
```

#### 1.4 Property Listings Module
**Components**:
- `Properties.jsx` (list view)
- `PropertyCard.jsx`
- `PropertyDetail.jsx`
- `ScoreDisplay.jsx`
- `FilterPanel.jsx`

**Purpose**: Browse and analyze property listings
**Features**:
- Filterable property list
- Sort by score, price, location
- HomeBuyerScore and InvestorScore badges
- Property details modal
- Favorite/watchlist functionality

#### 1.5 Common Components
**Components**:
- `Navbar.jsx` - Navigation bar with user menu
- `Sidebar.jsx` - Side navigation
- `Card.jsx` - Reusable card container
- `Button.jsx` - Styled button component
- `Input.jsx` - Form input component
- `Loader.jsx` - Loading spinner

### 2. Backend Components

#### 2.1 Authentication Service
**File**: `app/core/security.py`
**Responsibilities**:
- Password hashing (bcrypt)
- JWT token generation and verification
- User session management

**Key Functions**:
```python
def hash_password(password: str) -> str
def verify_password(plain_password: str, hashed: str) -> bool
def create_access_token(user_id: int) -> str
def decode_token(token: str) -> dict
```

#### 2.2 Plaid Integration Service
**File**: `app/services/plaid_service.py`
**Responsibilities**:
- Plaid Link token creation
- Public token exchange
- Account syncing
- Transaction retrieval

**Key Functions**:
```python
def create_link_token(user_id: int) -> str
def exchange_public_token(public_token: str) -> str
def sync_accounts(user_id: int, access_token: str) -> List[Account]
def fetch_transactions(access_token: str, start_date: date, end_date: date) -> List[Transaction]
```

**Data Flow**:
```
Frontend → Create Link → User Auth → Exchange Token → Store Access Token → Sync Data
```

#### 2.3 Financial Calculator Service
**File**: `app/services/financial_calculator.py`
**Responsibilities**:
- Calculate net worth
- Compute savings rate
- Determine emergency buffer
- Analyze cash flow
- Calculate DTI ratio

**Key Functions**:
```python
def calculate_net_worth(user_id: int) -> Decimal
def calculate_monthly_income(user_id: int, months: int = 3) -> Decimal
def calculate_monthly_expenses(user_id: int, months: int = 3) -> Decimal
def calculate_savings_rate(income: Decimal, expenses: Decimal) -> float
def calculate_emergency_buffer(cash: Decimal, monthly_expenses: Decimal) -> float
def calculate_dti(monthly_debt: Decimal, monthly_income: Decimal) -> float
```

#### 2.4 Affordability Service
**File**: `app/services/affordability_service.py`
**Responsibilities**:
- Calculate maximum home price
- Determine monthly payment capacity
- Estimate property taxes and insurance
- Calculate PMI if applicable
- Generate safe price range

**Key Functions**:
```python
def calculate_max_monthly_payment(
    monthly_income: Decimal,
    existing_debt: Decimal,
    dti_limit: float = 0.28
) -> Decimal

def calculate_home_price(
    monthly_payment: Decimal,
    down_payment_pct: float,
    interest_rate: float,
    loan_term_years: int = 30
) -> Decimal

def calculate_monthly_payment(
    home_price: Decimal,
    down_payment_pct: float,
    interest_rate: float,
    loan_term_years: int = 30
) -> Dict[str, Decimal]  # Returns breakdown: principal, interest, tax, insurance, PMI

def get_affordability_range(user_id: int) -> Dict[str, Any]
```

**Formulas**:
```python
# Mortgage Payment (Principal + Interest)
M = P * [r(1+r)^n] / [(1+r)^n - 1]
where:
  M = monthly payment
  P = principal (loan amount)
  r = monthly interest rate
  n = number of payments

# DTI Ratio
DTI = (Total Monthly Debt Payments) / (Gross Monthly Income)

# Safe Home Price
Max Price = (Max Monthly Payment * 12 * 30) / (Interest Rate + Tax Rate + Insurance Rate)
```

#### 2.5 Deal Analyzer Service
**File**: `app/services/deal_analyzer.py`
**Responsibilities**:
- Calculate HomeBuyerScore
- Calculate InvestorScore
- Compare properties
- Identify top deals

**Key Functions**:
```python
def calculate_homebuyer_score(
    property_price: Decimal,
    user_affordability_range: Dict,
    property_details: Dict
) -> int  # 0-100

def calculate_investor_score(
    property_price: Decimal,
    estimated_rent: Decimal,
    property_details: Dict
) -> int  # 0-100

def calculate_cap_rate(
    annual_income: Decimal,
    annual_expenses: Decimal,
    property_price: Decimal
) -> float

def calculate_cash_on_cash(
    annual_cash_flow: Decimal,
    total_cash_invested: Decimal
) -> float

def check_one_percent_rule(
    monthly_rent: Decimal,
    property_price: Decimal
) -> bool

def get_top_deals(
    user_id: int,
    limit: int = 20,
    score_type: str = "homebuyer"
) -> List[Property]
```

**HomeBuyerScore Algorithm**:
```python
score = (
    affordability_match * 0.40 +  # How well it fits budget (0-100)
    location_quality * 0.25 +      # School ratings, crime, amenities
    property_value * 0.20 +        # Price per sqft vs. market avg
    sustainability * 0.15          # Manageable monthly payment
)
```

**InvestorScore Algorithm**:
```python
score = (
    cap_rate_score * 0.30 +        # Normalized cap rate (0-100)
    coc_return_score * 0.25 +      # Cash-on-cash return normalized
    one_percent_rule * 0.20 +      # Pass=100, Fail=0
    market_strength * 0.15 +       # Rental demand indicators
    appreciation_potential * 0.10   # Historical price trends
)
```

#### 2.6 Web Scraping Components

##### 2.6.1 Base Scraper
**File**: `app/scrapers/base_scraper.py`
**Purpose**: Abstract base class for all scrapers
```python
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    def __init__(self, region: str):
        self.region = region
        self.headers = {
            'User-Agent': 'Mozilla/5.0 ...'
        }
    
    @abstractmethod
    def scrape_listings(self, max_pages: int = 5) -> List[Dict]:
        """Scrape property listings"""
        pass
    
    @abstractmethod
    def parse_property(self, html: str) -> Dict:
        """Parse individual property details"""
        pass
    
    def save_to_db(self, properties: List[Dict]):
        """Save scraped properties to database"""
        pass
```

##### 2.6.2 Zillow Scraper
**File**: `app/scrapers/zillow_scraper.py`
**Responsibilities**:
- Scrape Zillow listings
- Parse property details
- Handle pagination

**Key Features**:
- Respect robots.txt
- Rate limiting (2-3 requests/second)
- Error handling and retries
- Extract: price, beds, baths, sqft, address, photos

##### 2.6.3 Realtor Scraper
**File**: `app/scrapers/realtor_scraper.py`
**Similar structure to Zillow scraper**

##### 2.6.4 Scraper Manager
**File**: `app/scrapers/scraper_manager.py`
**Responsibilities**:
- Orchestrate all scrapers
- Schedule periodic scraping
- Manage rate limits across scrapers
- Handle failures and logging

```python
class ScraperManager:
    def __init__(self):
        self.scrapers = [
            ZillowScraper(region="Pittsburgh, PA"),
            RealtorScraper(region="Pittsburgh, PA")
        ]
    
    async def run_all_scrapers(self):
        """Run all scrapers asynchronously"""
        tasks = [scraper.scrape_listings() for scraper in self.scrapers]
        results = await asyncio.gather(*tasks)
        return results
    
    def schedule_scraping(self, interval_hours: int = 24):
        """Schedule periodic scraping"""
        pass
```

#### 2.7 Database Models

##### User Model
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    accounts = relationship("Account", back_populates="user")
    financials = relationship("UserFinancial", back_populates="user")
```

##### Account Model
```python
class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plaid_account_id = Column(String, unique=True)
    account_type = Column(String)  # checking, savings, credit, loan
    institution_name = Column(String)
    balance = Column(Numeric(12, 2))
    last_synced = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")
```

##### Transaction Model
```python
class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    date = Column(Date, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    category = Column(String)
    merchant = Column(String)
    description = Column(String)
    
    # Relationships
    account = relationship("Account", back_populates="transactions")
```

##### Property Model
```python
class Property(Base):
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True)
    source = Column(String)  # zillow, realtor, manual
    address = Column(String, nullable=False)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    price = Column(Numeric(12, 2))
    beds = Column(Integer)
    baths = Column(Numeric(3, 1))
    sqft = Column(Integer)
    year_built = Column(Integer)
    property_type = Column(String)  # house, condo, townhouse
    listing_url = Column(String)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    homebuyer_score = Column(Integer)
    investor_score = Column(Integer)
    estimated_rent = Column(Numeric(12, 2))
```

##### UserFinancial Model
```python
class UserFinancial(Base):
    __tablename__ = "user_financials"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    calculated_at = Column(DateTime, default=datetime.utcnow)
    net_worth = Column(Numeric(12, 2))
    monthly_income = Column(Numeric(12, 2))
    monthly_expenses = Column(Numeric(12, 2))
    savings_rate = Column(Numeric(5, 2))  # Percentage
    emergency_buffer_months = Column(Numeric(4, 1))
    dti_ratio = Column(Numeric(5, 2))  # Percentage
    
    # Relationships
    user = relationship("User", back_populates="financials")
```

## Data Flow Diagrams

### User Registration & Plaid Connection Flow
```
1. User registers → POST /api/auth/register
2. Backend creates user → Returns JWT token
3. Frontend stores token → Redirects to dashboard
4. User clicks "Connect Bank" → POST /api/plaid/link
5. Backend generates link_token → Returns to frontend
6. Frontend opens Plaid Link → User selects bank
7. User authenticates → Plaid returns public_token
8. Frontend sends public_token → POST /api/plaid/exchange
9. Backend exchanges for access_token → Stores securely
10. Backend syncs accounts → Fetches transactions
11. Backend calculates metrics → Stores in user_financials
12. Frontend polls → GET /api/financials/dashboard
13. Dashboard displays data → User sees financial overview
```

### Property Scraping & Scoring Flow
```
1. Scheduled job triggers → ScraperManager.run_all_scrapers()
2. Each scraper runs → Fetches listings (rate-limited)
3. Parse HTML → Extract property data
4. Save to properties table → Deduplicate by address
5. For each property → Calculate scores
   a. If user_id provided → Calculate HomeBuyerScore
   b. Always calculate → InvestorScore
6. Update property record → Store scores
7. User visits Properties page → GET /api/properties?sort=homebuyer_score
8. Backend queries DB → Returns top-scored properties
9. Frontend displays → PropertyCard components
```

### Affordability Calculation Flow
```
1. User visits Affordability page
2. Frontend fetches user financials → GET /api/financials/dashboard
3. Pre-fills form with current data
4. User adjusts sliders (income, debts, down payment %)
5. On change → POST /api/affordability/calculate
6. Backend receives parameters:
   - monthly_income
   - existing_debt
   - down_payment_pct
   - interest_rate (current market rate)
7. Backend calculates:
   - DTI ratio
   - Max monthly payment
   - Max home price
   - Monthly breakdown
   - Safe range (80%-100% of max)
8. Returns JSON → Frontend updates display
9. Charts update in real-time
```

## Technology Choices Rationale

### FastAPI vs Flask
**Choice**: FastAPI
**Reasons**:
- Async support (better for web scraping)
- Automatic API documentation (Swagger UI)
- Type hints and validation (Pydantic)
- Modern, high performance
- Better for concurrent scraping tasks

### BeautifulSoup vs Selectolax
**Choice**: Both (BeautifulSoup primary, Selectolax for performance-critical)
**Reasons**:
- BeautifulSoup: More forgiving parser, better documentation
- Selectolax: 5-10x faster for large-scale scraping
- Use BeautifulSoup for development, optimize with Selectolax later

### React vs Plain HTML/JS
**Choice**: React with Vite
**Reasons**:
- Component reusability
- Better state management
- Rich ecosystem (Chart.js, React Router)
- Modern development experience
- Vite: Fast development server, optimized builds

### PostgreSQL vs SQLite
**Choice**: SQLite for dev, PostgreSQL for production
**Reasons**:
- SQLite: Zero setup, perfect for development
- PostgreSQL: Better for production, concurrent access, JSON support
- Easy migration path with SQLAlchemy

## Security Considerations

### Authentication
- JWT tokens with expiration (1 hour access, 7 day refresh)
- HTTP-only cookies for token storage
- bcrypt for password hashing (cost factor 12)

### API Security
- Rate limiting: 100 requests/minute per user
- CORS: Whitelist frontend domain only
- Input validation: Pydantic schemas on all endpoints

### Data Security
- Plaid access tokens encrypted at rest
- Environment variables for all secrets
- No sensitive data in logs

### Scraping Ethics
- Respect robots.txt
- Rate limit: max 2-3 requests/second
- User-Agent identification
- Cache aggressively to reduce requests

## Performance Optimization

### Backend
- Database query optimization (indexes on foreign keys, frequently queried fields)
- Caching: Redis for frequently accessed data (financial metrics)
- Async endpoints for I/O-bound operations
- Connection pooling for database

### Frontend
- Lazy loading for charts
- Pagination for property listings
- Debounce on affordability calculator inputs
- Code splitting for route-based components

### Scraping
- Parallel scraping with asyncio
- Request throttling to avoid IP bans
- Incremental updates (only new listings)
- Background job scheduling (Celery)

## Testing Strategy

### Unit Tests
- Financial calculation functions
- Score algorithms
- Input validators
- Utility functions

### Integration Tests
- API endpoints (all routes)
- Database operations
- Plaid integration (mocked)

### Scraper Tests
- HTML parsing with fixtures
- Error handling
- Rate limiting behavior

### E2E Tests
- User registration flow
- Bank connection flow
- Property search and filter
- Affordability calculation

## Deployment Architecture (Future)

```
┌──────────────┐
│   CloudFlare │ (CDN, DDoS protection)
└──────┬───────┘
       │
┌──────▼───────┐
│  Load Bal.   │ (Nginx/AWS ALB)
└──────┬───────┘
       │
   ┌───┴────┐
   │        │
┌──▼──┐  ┌──▼──┐
│API 1│  │API 2│ (FastAPI instances)
└──┬──┘  └──┬──┘
   │        │
   └────┬───┘
        │
   ┌────▼─────┐
   │PostgreSQL│ (Managed DB)
   └──────────┘

Background Workers:
┌──────────┐
│ Celery   │ (Scraping jobs)
│ Workers  │
└─────┬────┘
      │
   ┌──▼───┐
   │Redis │ (Job queue, cache)
   └──────┘
```

---

This architecture provides a solid foundation for building HouseScope with clear separation of concerns, scalability, and maintainability.
