# HouseScope - Repository Structure

```
HouseScope/
├── README.md                          # Project overview and setup instructions
├── DEVELOPMENT_PLAN.md                # Detailed development plan and architecture
├── .gitignore                         # Git ignore file
├── .env.example                       # Example environment variables
│
├── backend/                           # Python FastAPI backend
│   ├── requirements.txt               # Python dependencies
│   ├── requirements-dev.txt           # Development dependencies
│   ├── pytest.ini                     # Pytest configuration
│   ├── .env                           # Environment variables (git-ignored)
│   ├── main.py                        # FastAPI application entry point
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   │
│   │   ├── api/                       # API routes
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                # Authentication endpoints
│   │   │   ├── accounts.py            # Account management endpoints
│   │   │   ├── transactions.py        # Transaction endpoints
│   │   │   ├── financials.py          # Financial dashboard endpoints
│   │   │   ├── affordability.py       # Affordability calculation endpoints
│   │   │   ├── properties.py          # Property listing endpoints
│   │   │   └── admin.py               # Admin endpoints
│   │   │
│   │   ├── models/                    # Database models (SQLAlchemy)
│   │   │   ├── __init__.py
│   │   │   ├── user.py                # User model
│   │   │   ├── account.py             # Account model
│   │   │   ├── transaction.py         # Transaction model
│   │   │   ├── property.py            # Property model
│   │   │   └── financial.py           # User financial snapshot model
│   │   │
│   │   ├── services/                  # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── plaid_service.py       # Plaid API integration
│   │   │   ├── financial_calculator.py # Financial metrics calculations
│   │   │   ├── affordability_service.py # Affordability calculations
│   │   │   ├── deal_analyzer.py       # Property scoring algorithms
│   │   │   ├── transaction_service.py # Transaction processing
│   │   │   └── csv_importer.py        # CSV import functionality
│   │   │
│   │   ├── scrapers/                  # Web scraping modules
│   │   │   ├── __init__.py
│   │   │   ├── base_scraper.py        # Abstract base scraper class
│   │   │   ├── zillow_scraper.py      # Zillow scraper
│   │   │   ├── realtor_scraper.py     # Realtor.com scraper
│   │   │   ├── scraper_manager.py     # Orchestrates all scrapers
│   │   │   └── utils.py               # Scraping utilities
│   │   │
│   │   ├── core/                      # Core functionality
│   │   │   ├── __init__.py
│   │   │   ├── config.py              # Configuration management
│   │   │   ├── database.py            # Database connection and session
│   │   │   ├── security.py            # JWT, password hashing, auth
│   │   │   ├── dependencies.py        # FastAPI dependencies
│   │   │   └── schemas.py             # Pydantic models for validation
│   │   │
│   │   └── utils/                     # Utility functions
│   │       ├── __init__.py
│   │       ├── validators.py          # Input validation helpers
│   │       └── formatters.py          # Data formatting utilities
│   │
│   └── tests/                         # Backend tests
│       ├── __init__.py
│       ├── conftest.py                # Pytest fixtures
│       ├── test_api/                  # API endpoint tests
│       ├── test_services/             # Service layer tests
│       └── test_scrapers/             # Scraper tests
│
├── frontend/                          # React frontend
│   ├── package.json                   # Node dependencies
│   ├── vite.config.js                 # Vite configuration
│   ├── index.html                     # HTML entry point
│   ├── .env                           # Frontend environment variables
│   │
│   ├── public/                        # Static assets
│   │   └── favicon.ico
│   │
│   └── src/
│       ├── main.jsx                   # React entry point
│       ├── App.jsx                    # Main App component
│       ├── index.css                  # Global styles
│       │
│       ├── components/                # Reusable components
│       │   ├── layout/
│       │   │   ├── Navbar.jsx
│       │   │   ├── Sidebar.jsx
│       │   │   └── Footer.jsx
│       │   ├── charts/
│       │   │   ├── NetWorthChart.jsx
│       │   │   ├── ExpenseBreakdown.jsx
│       │   │   └── CashFlowChart.jsx
│       │   ├── property/
│       │   │   ├── PropertyCard.jsx
│       │   │   ├── PropertyDetails.jsx
│       │   │   └── ScoreDisplay.jsx
│       │   └── common/
│       │       ├── Button.jsx
│       │       ├── Card.jsx
│       │       ├── Input.jsx
│       │       └── Loader.jsx
│       │
│       ├── pages/                     # Page components
│       │   ├── Dashboard.jsx          # Main dashboard
│       │   ├── FinanceDashboard.jsx   # Financial overview
│       │   ├── Affordability.jsx      # Affordability calculator
│       │   ├── Properties.jsx         # Property listings
│       │   ├── PropertyDetail.jsx     # Single property view
│       │   ├── Settings.jsx           # User settings
│       │   └── Login.jsx              # Login/Register page
│       │
│       ├── services/                  # API services
│       │   ├── api.js                 # Axios configuration
│       │   ├── authService.js         # Authentication API calls
│       │   ├── financialService.js    # Financial data API calls
│       │   └── propertyService.js     # Property API calls
│       │
│       └── utils/                     # Frontend utilities
│           ├── formatters.js          # Number/currency formatting
│           └── constants.js           # Constants and enums
│
├── docs/                              # Documentation
│   ├── API.md                         # API documentation
│   ├── ARCHITECTURE.md                # System architecture
│   ├── DATABASE.md                    # Database schema
│   ├── DEPLOYMENT.md                  # Deployment guide
│   └── SCRAPING.md                    # Scraping documentation
│
├── scripts/                           # Utility scripts
│   ├── init_db.py                     # Database initialization
│   ├── seed_data.py                   # Seed sample data
│   ├── run_scraper.py                 # Manual scraper runner
│   └── backup_db.sh                   # Database backup script
│
└── data/                              # Data storage (git-ignored)
    ├── sample_transactions.csv        # Sample CSV data
    └── housescope.db                  # SQLite database (dev)
```

## Directory Explanations

### Backend Structure

**`backend/app/api/`**: Contains all API route handlers, organized by domain (auth, accounts, properties, etc.). Each file defines FastAPI router endpoints.

**`backend/app/models/`**: SQLAlchemy ORM models representing database tables. Each model corresponds to a table and defines relationships.

**`backend/app/services/`**: Business logic layer. Services handle complex operations, external API calls, and calculations. Keeps route handlers thin.

**`backend/app/scrapers/`**: Web scraping modules. Each scraper inherits from `base_scraper.py` and implements site-specific parsing logic.

**`backend/app/core/`**: Core application functionality including configuration, database setup, authentication, and shared schemas.

**`backend/tests/`**: Comprehensive test suite using pytest. Organized to mirror the app structure.

### Frontend Structure

**`frontend/src/components/`**: Reusable UI components organized by category (layout, charts, property, common).

**`frontend/src/pages/`**: Full-page components that represent different routes/views in the application.

**`frontend/src/services/`**: API client modules that handle HTTP requests to the backend.

### Supporting Directories

**`docs/`**: Detailed documentation for various aspects of the project.

**`scripts/`**: Standalone scripts for maintenance, setup, and administrative tasks.

**`data/`**: Local data storage (not committed to git). Contains sample data and development database.

## Key Files

- **`main.py`**: FastAPI application entry point, mounts all routers
- **`requirements.txt`**: Production Python dependencies
- **`package.json`**: Frontend dependencies and scripts
- **`.env.example`**: Template for environment variables
- **`README.md`**: Project overview and quick start guide
- **`DEVELOPMENT_PLAN.md`**: Comprehensive development plan

## Next Steps

1. Set up backend virtual environment and install dependencies
2. Initialize database schema
3. Set up frontend with Vite and install packages
4. Begin Phase 1 development (Foundation)
