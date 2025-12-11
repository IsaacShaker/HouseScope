# HouseScope - Getting Started Checklist

Use this checklist to set up and start developing HouseScope.

## ✅ Initial Setup

### 1. Environment Setup
- [ ] Verify Python 3.10+ is installed (`python --version`)
- [ ] Verify Node.js 18+ is installed (`node --version`)
- [ ] Verify Git is installed (`git --version`)
- [ ] Clone repository (if not already done)

### 2. Backend Setup
- [ ] Navigate to `backend/` directory
- [ ] Create virtual environment: `python -m venv venv`
- [ ] Activate virtual environment:
  - Linux/Mac: `source venv/bin/activate`
  - Windows: `venv\Scripts\activate`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Install dev dependencies: `pip install -r requirements-dev.txt`
- [ ] Copy `.env.example` to `backend/.env`
- [ ] Generate SECRET_KEY (or use default for development)
- [ ] Initialize database: `python ../scripts/init_db.py`
- [ ] (Optional) Seed sample data: `python ../scripts/seed_data.py`
- [ ] Test backend: `python main.py` (should start on port 8000)
- [ ] Visit http://localhost:8000/docs to see API documentation

### 3. Frontend Setup
- [ ] Navigate to `frontend/` directory
- [ ] Install dependencies: `npm install`
- [ ] Create `.env` file: `echo "VITE_API_URL=http://localhost:8000/api" > .env`
- [ ] Test frontend: `npm run dev` (should start on port 5173)
- [ ] Visit http://localhost:5173 to see app

### 4. Verify Setup
- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:5173
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] No errors in terminal
- [ ] Database file created at `data/housescope.db`

## 📚 Review Documentation

- [ ] Read `README.md` - Project overview
- [ ] Read `DEVELOPMENT_PLAN.md` - Full development plan
- [ ] Read `PROJECT_SUMMARY.md` - What's been built so far
- [ ] Review `docs/ARCHITECTURE.md` - System design
- [ ] Review `docs/STRUCTURE.md` - Repository organization
- [ ] Review `docs/API.md` - API reference
- [ ] Review `docs/QUICKSTART.md` - Quick setup guide

## 🎯 Phase 2 Development - Finance Dashboard

### Authentication API (Start Here!)

#### Backend Implementation
- [ ] Create `backend/app/api/auth.py`
- [ ] Implement `POST /api/auth/register` endpoint
- [ ] Implement `POST /api/auth/login` endpoint
- [ ] Implement token refresh logic
- [ ] Add JWT dependency for protected routes
- [ ] Write tests in `tests/test_api/test_auth.py`
- [ ] Test endpoints with Swagger UI

#### Frontend Implementation
- [ ] Create `frontend/src/pages/Login.jsx`
- [ ] Create `frontend/src/pages/Register.jsx`
- [ ] Create `frontend/src/services/authService.js`
- [ ] Implement login form
- [ ] Implement registration form
- [ ] Add token storage (localStorage)
- [ ] Add protected route wrapper
- [ ] Test login/register flow

### Accounts API

#### Backend Implementation
- [ ] Create `backend/app/api/accounts.py`
- [ ] Implement `GET /api/accounts` - List accounts
- [ ] Implement `POST /api/accounts` - Create account
- [ ] Implement `PUT /api/accounts/{id}` - Update account
- [ ] Implement `DELETE /api/accounts/{id}` - Delete account
- [ ] Write tests in `tests/test_api/test_accounts.py`
- [ ] Test endpoints

#### Frontend Implementation
- [ ] Create `frontend/src/components/AccountList.jsx`
- [ ] Create `frontend/src/services/accountService.js`
- [ ] Display accounts on dashboard
- [ ] Add account creation form
- [ ] Add edit/delete functionality

### Transactions API

#### Backend Implementation
- [ ] Create `backend/app/api/transactions.py`
- [ ] Implement `GET /api/transactions` with filters
- [ ] Implement `POST /api/transactions` - Create transaction
- [ ] Implement `POST /api/transactions/import` - CSV import
- [ ] Create `backend/app/services/csv_importer.py`
- [ ] Write CSV parsing logic
- [ ] Write tests
- [ ] Test with sample CSV from `data/sample_transactions.csv`

#### Frontend Implementation
- [ ] Create `frontend/src/components/TransactionTable.jsx`
- [ ] Create `frontend/src/components/TransactionForm.jsx`
- [ ] Create `frontend/src/components/CSVUpload.jsx`
- [ ] Display transactions with filters
- [ ] Add manual transaction entry
- [ ] Add CSV import UI

### Financial Dashboard API

#### Backend Implementation
- [ ] Create `backend/app/api/financials.py`
- [ ] Implement `GET /api/financials/dashboard` endpoint
- [ ] Use existing `FinancialCalculator` service
- [ ] Add caching for performance (optional)
- [ ] Write tests
- [ ] Test with sample data

#### Frontend Implementation
- [ ] Create `frontend/src/pages/FinanceDashboard.jsx`
- [ ] Create `frontend/src/components/charts/NetWorthChart.jsx`
- [ ] Create `frontend/src/components/charts/ExpenseBreakdown.jsx`
- [ ] Create `frontend/src/components/charts/CashFlowChart.jsx`
- [ ] Create `frontend/src/services/financialService.js`
- [ ] Install Chart.js: `npm install chart.js react-chartjs-2`
- [ ] Implement dashboard layout
- [ ] Add visualizations
- [ ] Display key metrics

### Plaid Integration (Optional for Phase 2)

#### Backend Implementation
- [ ] Sign up for Plaid account (https://plaid.com)
- [ ] Get sandbox credentials
- [ ] Add credentials to `.env`
- [ ] Create `backend/app/services/plaid_service.py`
- [ ] Implement link token creation
- [ ] Implement token exchange
- [ ] Implement account sync
- [ ] Implement transaction fetch
- [ ] Create `backend/app/api/plaid.py`
- [ ] Write tests (with mocked Plaid)

#### Frontend Implementation
- [ ] Install Plaid Link: `npm install react-plaid-link`
- [ ] Create `frontend/src/components/PlaidLink.jsx`
- [ ] Implement connection flow
- [ ] Handle successful connection
- [ ] Trigger account sync

## 🧪 Testing Checklist

### Backend Tests
- [ ] Run all tests: `cd backend && pytest`
- [ ] Check coverage: `pytest --cov=app`
- [ ] Aim for >80% coverage
- [ ] Fix any failing tests
- [ ] Add tests for new features

### Frontend Tests
- [ ] Run tests: `cd frontend && npm test`
- [ ] Test user flows manually
- [ ] Test on different browsers
- [ ] Check responsive design

## 📝 Code Quality

### Backend
- [ ] Run black formatter: `black .`
- [ ] Run flake8 linter: `flake8 app`
- [ ] Run pylint: `pylint app`
- [ ] Fix any warnings
- [ ] Add docstrings to functions
- [ ] Add type hints

### Frontend
- [ ] Run ESLint: `npm run lint`
- [ ] Fix any warnings
- [ ] Add JSDoc comments
- [ ] Follow React best practices

## 🚀 Deployment Preparation (Future)

- [ ] Update `DATABASE_URL` for PostgreSQL
- [ ] Set strong `SECRET_KEY` in production
- [ ] Configure CORS for production domain
- [ ] Set up proper logging
- [ ] Add error monitoring (Sentry)
- [ ] Set up CI/CD pipeline
- [ ] Configure environment variables in hosting platform
- [ ] Test in production-like environment

## 📊 Progress Tracking

### Phase 1: Foundation ✅
- [x] Repository structure
- [x] Backend setup
- [x] Frontend setup
- [x] Database models
- [x] Core services (Financial Calculator, Affordability)
- [x] Configuration
- [x] Documentation

### Phase 2: Finance Dashboard (Current)
- [ ] Authentication
- [ ] Account management
- [ ] Transaction management
- [ ] Financial dashboard
- [ ] CSV import
- [ ] Plaid integration (optional)

### Phase 3: Affordability Engine
- [ ] Affordability API endpoints
- [ ] Calculator UI
- [ ] Scenario testing

### Phase 4: Property Scraping
- [ ] Scraper framework
- [ ] Zillow scraper
- [ ] Realtor scraper
- [ ] Scraper scheduling

### Phase 5: Deal Scoring
- [ ] HomeBuyerScore algorithm
- [ ] InvestorScore algorithm
- [ ] Property ranking

### Phase 6: Integration & Polish
- [ ] End-to-end integration
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] Final documentation

## 💡 Tips for Success

1. **Work incrementally** - Complete one feature at a time
2. **Test as you go** - Write tests before moving to next feature
3. **Commit often** - Small, focused commits with clear messages
4. **Use the docs** - FastAPI auto-generates API docs at `/docs`
5. **Ask for help** - Use the comprehensive documentation provided
6. **Stay organized** - Follow the phase structure
7. **Document changes** - Update docs when adding features

## 🎓 Learning Resources

- FastAPI Tutorial: https://fastapi.tiangolo.com/tutorial/
- React Documentation: https://react.dev/
- SQLAlchemy Docs: https://docs.sqlalchemy.org/
- Plaid Quickstart: https://plaid.com/docs/quickstart/
- Chart.js Guide: https://www.chartjs.org/docs/

## 📞 Need Help?

- Review the documentation in `docs/` folder
- Check `PROJECT_SUMMARY.md` for implementation details
- Look at existing code for patterns
- Use FastAPI `/docs` for API testing
- Open issues on GitHub

---

**Start with authentication - it's the foundation for everything else!** 🚀

Mark items as complete and track your progress. Good luck!
