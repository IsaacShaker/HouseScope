# HouseScope 🏠💰

**Personal Finance & Real Estate Analysis Platform**

HouseScope is a full-stack application that helps users understand their financial health and identify affordable housing opportunities through data-driven analysis. The platform combines financial data integration, real-time property scraping, and intelligent scoring algorithms to empower smart home-buying decisions.

---

## 🎯 Project Overview

HouseScope consists of three integrated components:

1. **Finance Dashboard**: Track net worth, income, expenses, savings rate, and emergency funds
2. **Home Affordability Engine**: Calculate safe home price ranges based on DTI, cash reserves, and monthly affordability
3. **Deal Analyzer with Live Scraping**: Score properties using HomeBuyerScore and InvestorScore metrics

---

## Features

### Finance Dashboard
- Net worth calculation and tracking
- Income and expense analysis with category breakdown
- Savings rate computation and emergency fund assessment
- Interactive financial visualizations
- CSV import for transaction data

### Affordability Calculator
- Maximum home price calculation based on income and debts
- DTI (Debt-to-Income) ratio analysis
- Monthly payment breakdown including PITI and PMI
- Down payment and cash reserve recommendations
- Safe price range estimation

### Property Analysis
- Property scraping from Redfin
- Commute time analysis with multiple destinations
- Support for different transportation modes (driving, walking, bicycling, transit)
- Property filtering and comparison tools
- Visual property cards with key metrics

---

## Technology Stack

**Backend:** FastAPI, Python 3.10+, SQLAlchemy, SQLite

**Frontend:** React 18, Vite, React Router, Axios, Chart.js, Tailwind CSS

**Testing:** pytest, pytest-cov

---

## Project Structure

```
HouseScope/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── models/   # Database models
│   │   ├── services/ # Business logic
│   │   ├── scrapers/ # Web scraping
│   │   └── core/     # Config & database
│   └── tests/
├── frontend/         # React frontend
│   └── src/
│       ├── components/
│       ├── pages/
│       └── services/
└── scripts/          # Database utilities
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### Installation

### Installation

#### 1. Clone Repository

```bash
git clone https://github.com/IsaacShaker/HouseScope.git
cd HouseScope
```

#### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

#### 3. Frontend Setup

```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000/api" > .env
```

### Running the Application

**Backend:**
```bash
cd backend
source venv/bin/activate
python main.py
```
API: http://localhost:8000 | Docs: http://localhost:8000/docs

**Frontend:**
```bash
cd frontend
npm run dev
```
App: http://localhost:5173

---

## Testing

```bash
cd backend
pytest --cov=app
```

---

## Database Models

- **User** - Authentication and user accounts
- **Account** - Financial accounts
- **Transaction** - Income and expense records
- **Category** - Transaction categories
- **Property** - Real estate listings
- **UserFinancial** - Calculated financial metrics

---

## API Endpoints

**Authentication:** `/api/auth/register`, `/api/auth/login`

**Financial:** `/api/accounts`, `/api/transactions`, `/api/categories`, `/api/financials/dashboard`

**Affordability:** `/api/affordability/calculate`

**Properties:** `/api/properties`, `/api/properties/scrape`

Full documentation: http://localhost:8000/docs

---

## Status

### Current Features
- User authentication
- Financial dashboard with transaction tracking
- Affordability calculator
- Property scraping (Redfin)
- Commute time analysis
- Interactive visualizations

### Future Enhancements
- Additional property sources
- Advanced filtering
- Historical trend analysis

---

**Repository**: [github.com/IsaacShaker/HouseScope](https://github.com/IsaacShaker/HouseScope)