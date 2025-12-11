# Quick Start Guide for HouseScope

This guide will help you get HouseScope up and running quickly.

## Prerequisites

- Python 3.10+ installed
- Node.js 18+ and npm installed
- Git installed
- Terminal/command line access

## Quick Setup (5 minutes)

### 1. Clone and Navigate

```bash
git clone https://github.com/IsaacShaker/HouseScope.git
cd HouseScope
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (use defaults for quick start)
cp ../.env.example .env

# Initialize database
python ../scripts/init_db.py

# (Optional) Seed sample data
python ../scripts/seed_data.py
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000/api" > .env
```

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # If not already active
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 5. Access the Application

- **Frontend**: http://localhost:5173
- **API Documentation**: http://localhost:8000/docs
- **API**: http://localhost:8000

## Demo Credentials (if you seeded data)

- **Email**: demo@housescope.com
- **Password**: demo123

## What to Do Next

1. **Review Documentation**:
   - Read [`DEVELOPMENT_PLAN.md`](../DEVELOPMENT_PLAN.md) for project details
   - Check [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) for system design

2. **Start Development**:
   - Phase 1 (Foundation) is complete
   - Begin Phase 2 (Finance Dashboard)
   - Follow the roadmap in the development plan

3. **Configure Plaid** (for bank integration):
   - Sign up at https://plaid.com
   - Get sandbox credentials
   - Add to `.env` file:
     ```
     PLAID_CLIENT_ID=your_client_id
     PLAID_SECRET=your_secret
     ```

4. **Run Tests**:
   ```bash
   cd backend
   pytest
   ```

## Common Issues

### Python Module Not Found
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

### Database Errors
- Delete `data/housescope.db` and run `init_db.py` again

### Port Already in Use
- Backend: Change `API_PORT` in `.env`
- Frontend: Change port in `vite.config.js`

### Frontend Can't Connect to Backend
- Verify backend is running on port 8000
- Check CORS settings in `.env`

## Next Steps

Refer to the main [README.md](../README.md) for:
- Detailed feature documentation
- API endpoint reference
- Development roadmap
- Testing guide

## Need Help?

- Check the documentation in the `docs/` folder
- Review code comments
- Open an issue on GitHub

Happy coding! 🚀
