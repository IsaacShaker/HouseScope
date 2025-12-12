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

## 🚀 Features

### Finance Dashboard
- 📊 Net worth calculation and tracking
- 💵 Income and expense analysis
- 💰 Savings rate computation
- 🚨 Emergency fund assessment
- 📈 Interactive financial visualizations
- 🔗 Plaid API integration for automatic bank sync
- 📄 CSV import for manual data entry

### Affordability Calculator
- 🏡 Maximum home price calculation
- 📉 DTI (Debt-to-Income) ratio analysis
- 💳 Monthly payment breakdown (PITI + PMI)
- 💸 Down payment requirements
- 🏦 Cash reserve recommendations
- 🎯 Safe price range estimation

### Property Deal Analyzer
- 🔍 Real-time property scraping (Zillow, Realtor.com)
- ⭐ **HomeBuyerScore**: Rates properties for primary residence (0-100)
  - Affordability match
  - Location quality
  - Property value
  - Long-term sustainability
- 💼 **InvestorScore**: Rates properties for investment potential (0-100)
  - Cap rate analysis
  - Cash-on-cash return
  - 1% rule compliance
  - Market strength
  - Appreciation potential
- 🎨 Visual property cards with scores
- 🔎 Advanced filtering and sorting
- 🚗 **Commute Time Filter**: Filter properties by commute requirements
  - Support for multiple roommates
  - Different destinations for each person
  - Multiple transportation modes (driving, walking, bicycling, transit)
  - Uses free OpenStreetMap & OSRM APIs (no API key required!)
  - Display commute times on property cards

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL / SQLite
- **ORM**: SQLAlchemy
- **Authentication**: JWT tokens with bcrypt
- **Web Scraping**: BeautifulSoup4, Selectolax
- **Financial Integration**: Plaid API

### Frontend
- **Framework**: React 18 with Vite
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Charts**: Chart.js / Recharts
- **Styling**: Tailwind CSS (optional)

### DevOps
- **Testing**: pytest, pytest-cov
- **Code Quality**: black, flake8, pylint
- **Version Control**: Git

---

## 📁 Repository Structure

```
HouseScope/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API route handlers
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   ├── scrapers/       # Web scraping modules
│   │   └── core/           # Core functionality
│   ├── tests/              # Backend tests
│   ├── main.py             # Application entry point
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   └── services/      # API services
│   └── package.json       # Node dependencies
│
├── docs/                  # Documentation
│   ├── DEVELOPMENT_PLAN.md
│   ├── ARCHITECTURE.md
│   └── STRUCTURE.md
│
├── scripts/               # Utility scripts
└── data/                  # Local data storage
```

See [`docs/STRUCTURE.md`](docs/STRUCTURE.md) for detailed repository structure.

---

## 🏁 Getting Started

### Prerequisites

- Python 3.10 or higher
- Node.js 18+ and npm
- Git
- (Optional) PostgreSQL for production

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/IsaacShaker/HouseScope.git
cd HouseScope
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copy environment template
cp ../.env.example .env

# Edit .env and add your configuration
# Required: SECRET_KEY
# Optional: PLAID_CLIENT_ID, PLAID_SECRET

# Initialize database
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

**Environment Variables:**
- `SECRET_KEY`: Required for JWT authentication
- `PLAID_CLIENT_ID` & `PLAID_SECRET`: Optional, for bank account integration


#### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Create environment file
echo "VITE_API_URL=http://localhost:8000/api" > .env
```

### Running the Application

#### Start Backend Server

```bash
cd backend
source venv/bin/activate  # Activate venv if not already active
python main.py
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will be available at http://localhost:5173

---

## 📚 Documentation

- **[Development Plan](DEVELOPMENT_PLAN.md)**: Comprehensive project plan, phases, algorithms
- **[Architecture](docs/ARCHITECTURE.md)**: System architecture, components, data flows
- **[Structure](docs/STRUCTURE.md)**: Repository structure and directory explanations

---

## 🔑 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

#### Required

```env
SECRET_KEY=your-secret-key-here
PLAID_CLIENT_ID=your-plaid-client-id
PLAID_SECRET=your-plaid-secret-sandbox
```

#### Optional

- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `API_PORT`: Backend port (default: 8000)
- `PLAID_ENV`: Plaid environment (sandbox, development, production)
- Mortgage defaults (interest rate, tax rate, insurance rate)

See `.env.example` for all available options.

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest                          # Run all tests
pytest --cov=app               # Run with coverage
pytest tests/test_services/    # Run specific test directory
```

### Frontend Tests

```bash
cd frontend
npm test
```

---

## 🗃️ Database Schema

Key models:

- **User**: User accounts and authentication
- **Account**: Bank accounts (linked via Plaid or manual)
- **Transaction**: Financial transactions
- **Property**: Real estate listings
- **UserFinancial**: Calculated financial snapshots

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for detailed schema.

---

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - Create new user
- `POST /api/auth/login` - User login

### Financial Data
- `GET /api/accounts` - Get all accounts
- `GET /api/transactions` - Get transactions
- `GET /api/financials/dashboard` - Get financial metrics
- `POST /api/plaid/link` - Initialize Plaid connection

### Affordability
- `GET /api/affordability/calculate` - Calculate affordability range

### Properties
- `GET /api/properties` - List properties
- `GET /api/properties/{id}` - Get property details
- `POST /api/properties/scrape` - Trigger scraping

Full API documentation: http://localhost:8000/docs (when server is running)

---

## 🎯 Development Roadmap

### Phase 1: Foundation ✅ (Weeks 1-2)
- [x] Repository structure
- [x] Backend setup
- [x] Database models
- [x] Configuration management

### Phase 2: Finance Dashboard (Weeks 3-4)
- [ ] Plaid integration
- [ ] Financial calculations
- [ ] Dashboard UI
- [ ] CSV import

### Phase 3: Affordability Engine (Weeks 5-6)
- [ ] Affordability algorithms
- [ ] Calculator UI
- [ ] Scenario testing

### Phase 4: Property Scraping (Weeks 7-8)
- [ ] Web scraper framework
- [ ] Site-specific scrapers
- [ ] Scraper scheduling

### Phase 5: Deal Scoring (Weeks 9-10)
- [ ] HomeBuyerScore algorithm
- [ ] InvestorScore algorithm
- [ ] Property ranking

### Phase 6: Integration & Polish (Weeks 11-12)
- [ ] End-to-end integration
- [ ] Testing
- [ ] Documentation
- [ ] Deployment preparation

---

## 🤝 Contributing

This is an academic project for ECE 1895. Contributions and feedback are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is for educational purposes as part of ECE 1895.

---

## 🙏 Acknowledgments

- **Plaid**: Financial data connectivity platform
- **FastAPI**: Modern Python web framework
- **React**: Frontend framework
- **Chart.js**: Data visualization library

---

## 📧 Contact

**Project**: HouseScope  
**Course**: ECE 1895  
**Repository**: [github.com/IsaacShaker/HouseScope](https://github.com/IsaacShaker/HouseScope)

---

## 📌 Important Notes

### Plaid Sandbox

This project uses Plaid's Sandbox environment for development. To get started:

1. Sign up at [plaid.com](https://plaid.com)
2. Get sandbox credentials (client_id and secret)
3. Add to `.env` file
4. Use sandbox credentials for testing

### Web Scraping Ethics

- Respect `robots.txt`
- Implement rate limiting (2-3 requests/second)
- Cache aggressively
- Identify your scraper with proper User-Agent
- Only scrape public data

### Security Best Practices

- Never commit `.env` files
- Use strong SECRET_KEY in production
- Enable HTTPS in production
- Regularly update dependencies
- Validate all user inputs

---

## 🎓 Learning Objectives

This project demonstrates:

- Full-stack web development
- RESTful API design
- Database modeling and ORM usage
- Financial calculations and algorithms
- Web scraping techniques
- Data visualization
- Authentication and security
- Testing and code quality
- Project structure and documentation

---

**Built with ❤️ for ECE 1895**