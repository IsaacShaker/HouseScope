# HouseScope Development Plan

## Project Overview
HouseScope is a full-stack financial analysis and real estate evaluation platform that helps users assess their financial health and identify affordable housing opportunities through data-driven analysis.

## Core Components

### 1. Finance Dashboard
**Purpose**: Provide comprehensive personal financial analysis
**Features**:
- Net worth calculation (assets - liabilities)
- Income tracking and categorization
- Expense analysis with category breakdown
- Savings rate computation
- Emergency fund assessment (months of coverage)
- Cash flow visualization

### 2. Home Affordability Engine
**Purpose**: Determine safe home purchase price ranges
**Features**:
- DTI (Debt-to-Income) ratio calculation
- Maximum monthly payment affordability
- Down payment analysis (recommended: 20%)
- Cash reserve requirements (6-12 months expenses)
- Property tax and insurance estimates
- PMI calculations for <20% down
- Safe price range recommendations

### 3. Deal Analyzer with Live Scraping
**Purpose**: Real-time property evaluation against market data
**Features**:
- Web scraping of regional listings (Zillow, Realtor.com, etc.)
- **HomeBuyerScore**: Evaluates properties for primary residence
  - Price vs. affordability range
  - Location quality metrics
  - Property condition indicators
  - Monthly payment sustainability
- **InvestorScore**: Evaluates investment potential
  - Cap rate analysis
  - Cash-on-cash return
  - 1% rule compliance (rent ≥ 1% of purchase price)
  - Appreciation potential indicators
  - Rental market strength

## Technology Stack

### Backend
- **Framework**: FastAPI (async support, auto-docs, modern)
- **Language**: Python 3.10+
- **Database**: PostgreSQL (dev) / SQLite (local testing)
- **Web Scraping**: 
  - BeautifulSoup4 (parsing)
  - Selectolax (high-performance alternative)
  - Requests / httpx (HTTP client)
- **Financial Integration**: Plaid API (Sandbox for dev)

### Frontend
- **Option A**: Lightweight React with Vite
- **Option B**: HTML/JS with Tailwind CSS
- **Visualization**: Chart.js or Recharts
- **HTTP Client**: Axios or Fetch API

### DevOps & Tools
- **Version Control**: Git
- **Environment Management**: venv or conda
- **API Documentation**: FastAPI auto-generated Swagger/OpenAPI
- **Testing**: pytest, unittest
- **Code Quality**: pylint, black, flake8

## Development Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Set up repository structure
- [ ] Initialize FastAPI backend
- [ ] Configure database schema
- [ ] Set up basic authentication
- [ ] Create project documentation

### Phase 2: Finance Dashboard (Week 3-4)
- [ ] Implement Plaid integration (Sandbox)
- [ ] Build transaction ingestion pipeline
- [ ] CSV import functionality
- [ ] Calculate core financial metrics
- [ ] Create visualization endpoints
- [ ] Build dashboard UI

### Phase 3: Home Affordability Engine (Week 5-6)
- [ ] DTI calculation logic
- [ ] Monthly payment affordability formulas
- [ ] Property cost estimation models
- [ ] Cash reserve analysis
- [ ] Safe price range algorithm
- [ ] Affordability UI with sliders

### Phase 4: Deal Analyzer - Scraping (Week 7-8)
- [ ] Build web scraper framework
- [ ] Implement site-specific scrapers (Zillow, Realtor.com)
- [ ] Parse listing data (price, beds, baths, sqft, location)
- [ ] Store listings in database
- [ ] Create scraper scheduling system
- [ ] Add rate limiting and error handling

### Phase 5: Deal Analyzer - Scoring (Week 9-10)
- [ ] HomeBuyerScore algorithm
- [ ] InvestorScore algorithm
- [ ] Rental income estimation models
- [ ] Comparative market analysis
- [ ] Property ranking system
- [ ] Deal alerts and notifications

### Phase 6: Integration & Polish (Week 11-12)
- [ ] Connect all components
- [ ] Build unified dashboard
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] Documentation completion
- [ ] Deployment preparation

## Key Algorithms & Formulas

### Financial Metrics
```
Net Worth = Total Assets - Total Liabilities
Savings Rate = (Monthly Income - Monthly Expenses) / Monthly Income
Emergency Buffer = Cash Reserves / Monthly Expenses (in months)
DTI Ratio = Monthly Debt Payments / Gross Monthly Income
```

### Affordability Calculations
```
Max Monthly Payment = (Monthly Income × 0.28) - Existing Debt Payments
Max Home Price = (Max Monthly Payment × 12 × 30) / (Annual Interest Rate + Property Tax Rate)
Recommended Down Payment = Home Price × 0.20
Required Cash Reserves = Monthly Expenses × 6
```

### HomeBuyerScore (0-100)
```
Score = (
  Affordability Match (40%) +
  Location Quality (25%) +
  Property Value (20%) +
  Long-term Sustainability (15%)
)
```

### InvestorScore (0-100)
```
Score = (
  Cap Rate (30%) +
  Cash-on-Cash Return (25%) +
  1% Rule Compliance (20%) +
  Market Strength (15%) +
  Appreciation Potential (10%)
)

Cap Rate = (Annual Rental Income - Annual Expenses) / Property Price
Cash-on-Cash Return = Annual Cash Flow / Total Cash Invested
```

## Data Models

### User
- user_id (PK)
- email
- hashed_password
- created_at
- last_login

### Account
- account_id (PK)
- user_id (FK)
- account_type (checking, savings, credit, loan)
- institution_name
- balance
- plaid_account_id
- last_synced

### Transaction
- transaction_id (PK)
- account_id (FK)
- date
- amount
- category
- merchant
- description

### Property
- property_id (PK)
- source (zillow, realtor, manual)
- address
- city, state, zip
- price
- beds, baths
- sqft
- year_built
- property_type
- listing_url
- scraped_at
- homebuyer_score
- investor_score

### UserFinancials
- financial_id (PK)
- user_id (FK)
- calculated_at
- net_worth
- monthly_income
- monthly_expenses
- savings_rate
- emergency_buffer_months
- dti_ratio

## API Endpoint Structure

### Authentication
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`

### Financial Data
- `POST /api/plaid/link` - Initialize Plaid Link
- `POST /api/plaid/exchange` - Exchange public token
- `GET /api/accounts` - Get all accounts
- `GET /api/transactions` - Get transactions (with filters)
- `POST /api/transactions/import` - Import CSV
- `GET /api/financials/dashboard` - Get computed metrics

### Affordability
- `GET /api/affordability/calculate` - Calculate safe price range
- `POST /api/affordability/scenario` - Test custom scenarios

### Properties
- `GET /api/properties` - List properties (with filters)
- `GET /api/properties/{id}` - Get property details
- `POST /api/properties/scrape` - Trigger scraping job
- `GET /api/properties/deals` - Get top-scored deals

### Admin
- `GET /api/admin/scraper/status` - Scraper health
- `POST /api/admin/scraper/run` - Manual scrape trigger

## Security Considerations

1. **Authentication**: JWT tokens with refresh mechanism
2. **API Keys**: Store Plaid credentials in environment variables
3. **Rate Limiting**: Prevent scraper abuse and API overload
4. **Data Privacy**: Encrypt sensitive financial data at rest
5. **Input Validation**: Sanitize all user inputs
6. **CORS**: Configure properly for production

## Testing Strategy

1. **Unit Tests**: Test individual functions and calculations
2. **Integration Tests**: Test API endpoints and database interactions
3. **Scraper Tests**: Mock HTML responses, test parsers
4. **E2E Tests**: Full user workflows
5. **Performance Tests**: Load testing for scraping and analytics

## Deployment Considerations

### Development
- Local SQLite database
- Plaid Sandbox environment
- Local development server
- Mock scraping data for testing

### Production (Future)
- PostgreSQL on managed service (e.g., Supabase, AWS RDS)
- Plaid Production API
- Docker containerization
- Cloud hosting (AWS, DigitalOcean, Render)
- Scheduled scraping jobs (Celery + Redis)
- CDN for static assets

## Success Metrics

1. **Functionality**: All three core components working end-to-end
2. **Accuracy**: Financial calculations verified against test cases
3. **Performance**: Scraping completes <5min for 100 listings
4. **Usability**: Clean UI with intuitive navigation
5. **Code Quality**: >80% test coverage, documented code

## Potential Challenges & Solutions

### Challenge 1: Web Scraping Reliability
- **Issue**: Sites may block scrapers or change HTML structure
- **Solution**: Implement robust error handling, rotating user agents, respect robots.txt, have fallback parsers

### Challenge 2: Data Accuracy
- **Issue**: Financial calculations must be precise
- **Solution**: Extensive unit testing, cross-reference with online calculators, peer review

### Challenge 3: Plaid Integration Complexity
- **Issue**: OAuth flow and token management
- **Solution**: Follow Plaid documentation carefully, use official SDKs, test in Sandbox thoroughly

### Challenge 4: Rental Income Estimation
- **Issue**: No direct rental data for many properties
- **Solution**: Use rental estimate APIs (Zillow), comparable analysis, or manual input option

## Extensions & Future Enhancements

1. **Mobile App**: React Native or Flutter version
2. **Property Alerts**: Email/SMS notifications for new deals
3. **Advanced Analytics**: ML-based price predictions
4. **Comparison Tool**: Side-by-side property comparison
5. **Mortgage Calculator**: Detailed amortization schedules
6. **Tax Implications**: Capital gains, property tax projections
7. **Multi-User**: Household financial management
8. **Social Features**: Share deals, community insights

## Resources & References

- [Plaid API Documentation](https://plaid.com/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [BeautifulSoup4 Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Chart.js Documentation](https://www.chartjs.org/)
- [Real Estate Investing Formulas](https://www.biggerpockets.com/blog/real-estate-formulas)
- [DTI Ratio Guidelines](https://www.consumerfinance.gov/ask-cfpb/what-is-a-debt-to-income-ratio-why-is-the-43-debt-to-income-ratio-important-en-1791/)

## License
This project is for educational purposes as part of ECE 1895.

---

**Last Updated**: December 10, 2025
**Project Duration**: ~12 weeks
**Status**: Planning Phase
