# HouseScope API Documentation

Complete API endpoint reference for HouseScope backend.

## Base URL

```
http://localhost:8000/api
```

## Authentication

Most endpoints require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your_token>
```

---

## Authentication Endpoints

### Register User

Create a new user account.

**Endpoint**: `POST /api/auth/register`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response**: `201 Created`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Login

Authenticate and receive access token.

**Endpoint**: `POST /api/auth/login`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response**: `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## Account Endpoints

### Get All Accounts

Retrieve all accounts for the authenticated user.

**Endpoint**: `GET /api/accounts`

**Headers**: `Authorization: Bearer <token>`

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "user_id": 1,
    "account_type": "checking",
    "institution_name": "Sample Bank",
    "balance": "5000.00",
    "last_synced": "2025-12-10T10:30:00Z"
  }
]
```

### Create Account

Manually add an account.

**Endpoint**: `POST /api/accounts`

**Request Body**:
```json
{
  "account_type": "savings",
  "institution_name": "My Bank",
  "balance": "10000.00"
}
```

**Response**: `201 Created`

---

## Transaction Endpoints

### Get Transactions

Retrieve transactions with optional filtering.

**Endpoint**: `GET /api/transactions`

**Query Parameters**:
- `account_id` (optional): Filter by account
- `start_date` (optional): Filter by date range (YYYY-MM-DD)
- `end_date` (optional): Filter by date range (YYYY-MM-DD)
- `category` (optional): Filter by category
- `limit` (optional): Limit results (default: 100)
- `offset` (optional): Pagination offset

**Example**: `GET /api/transactions?account_id=1&limit=50`

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "account_id": 1,
    "date": "2025-12-10",
    "amount": "-45.99",
    "category": "groceries",
    "merchant": "Grocery Store",
    "description": "Weekly shopping"
  }
]
```

### Import Transactions (CSV)

Import transactions from CSV file.

**Endpoint**: `POST /api/transactions/import`

**Request Body**:
```json
{
  "account_id": 1,
  "file_data": "base64_encoded_csv_data"
}
```

**CSV Format**:
```csv
date,amount,category,merchant,description
2025-12-01,3500.00,salary,Employer,Paycheck
2025-12-02,-45.99,groceries,Store,Shopping
```

**Response**: `200 OK`
```json
{
  "success": true,
  "transactions_imported": 45,
  "errors": []
}
```

---

## Financial Dashboard Endpoints

### Get Financial Metrics

Get comprehensive financial dashboard data.

**Endpoint**: `GET /api/financials/dashboard`

**Response**: `200 OK`
```json
{
  "metrics": {
    "net_worth": "17500.00",
    "monthly_income": "3500.00",
    "monthly_expenses": "2100.00",
    "savings_rate": 40.0,
    "emergency_buffer_months": 7.1,
    "dti_ratio": 12.5,
    "calculated_at": "2025-12-10T10:30:00Z"
  },
  "expense_breakdown": [
    {
      "category": "rent",
      "amount": "1200.00",
      "percentage": 57.14
    },
    {
      "category": "groceries",
      "amount": "400.00",
      "percentage": 19.05
    }
  ],
  "accounts": [...]
}
```

---

## Affordability Endpoints

### Calculate Affordability

Calculate home affordability based on financial parameters.

**Endpoint**: `POST /api/affordability/calculate`

**Request Body**:
```json
{
  "monthly_income": "5000.00",
  "existing_debt": "350.00",
  "down_payment_pct": 0.20,
  "interest_rate": 0.07,
  "loan_term_years": 30
}
```

**Response**: `200 OK`
```json
{
  "max_home_price": "285000.00",
  "safe_price_range_min": "228000.00",
  "safe_price_range_max": "285000.00",
  "down_payment_amount": "57000.00",
  "loan_amount": "228000.00",
  "monthly_payment_breakdown": {
    "principal_interest": "1517.28",
    "property_tax": "285.00",
    "insurance": "118.75",
    "pmi": "0.00",
    "total": "1921.03"
  },
  "dti_ratio": 38.42,
  "recommended_cash_reserves": "14526.18"
}
```

---

## Property Endpoints

### Get Properties

List all properties with optional filtering.

**Endpoint**: `GET /api/properties`

**Query Parameters**:
- `city` (optional): Filter by city
- `state` (optional): Filter by state
- `min_price` (optional): Minimum price
- `max_price` (optional): Maximum price
- `beds` (optional): Number of bedrooms
- `sort_by` (optional): Sort field (price, homebuyer_score, investor_score)
- `limit` (optional): Results per page
- `offset` (optional): Pagination offset

**Example**: `GET /api/properties?city=Pittsburgh&sort_by=homebuyer_score&limit=20`

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "source": "zillow",
    "address": "123 Main St",
    "city": "Pittsburgh",
    "state": "PA",
    "zip_code": "15213",
    "price": "250000.00",
    "beds": 3,
    "baths": 2.0,
    "sqft": 1500,
    "year_built": 2010,
    "property_type": "house",
    "listing_url": "https://zillow.com/...",
    "scraped_at": "2025-12-10T08:00:00Z",
    "homebuyer_score": 85,
    "investor_score": 72,
    "estimated_rent": "1800.00"
  }
]
```

### Get Property Details

Get detailed information for a single property.

**Endpoint**: `GET /api/properties/{property_id}`

**Response**: `200 OK`
```json
{
  "id": 1,
  "address": "123 Main St",
  ...
  "score_details": {
    "homebuyer_score": 85,
    "affordability_match": 90,
    "location_quality": 85,
    "property_value": 80,
    "sustainability": 85
  }
}
```

### Trigger Scraping

Manually trigger property scraping (admin only).

**Endpoint**: `POST /api/properties/scrape`

**Request Body**:
```json
{
  "region": "Pittsburgh, PA",
  "max_pages": 5
}
```

**Response**: `202 Accepted`
```json
{
  "message": "Scraping job started",
  "job_id": "abc123"
}
```

---

## Plaid Integration Endpoints

### Create Link Token

Generate Plaid Link token for bank connection.

**Endpoint**: `POST /api/plaid/link`

**Request Body**:
```json
{
  "user_id": 1
}
```

**Response**: `200 OK`
```json
{
  "link_token": "link-sandbox-abc123-xyz789"
}
```

### Exchange Public Token

Exchange Plaid public token for access token.

**Endpoint**: `POST /api/plaid/exchange`

**Request Body**:
```json
{
  "public_token": "public-sandbox-abc123"
}
```

**Response**: `200 OK`
```json
{
  "success": true,
  "accounts_synced": 3
}
```

---

## Admin Endpoints

### Get Scraper Status

Check scraper health and status.

**Endpoint**: `GET /api/admin/scraper/status`

**Response**: `200 OK`
```json
{
  "status": "healthy",
  "last_run": "2025-12-10T08:00:00Z",
  "properties_scraped": 150,
  "errors": []
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error: Email is required"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid authentication credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

- **Default**: 100 requests per minute per user
- **Scraping**: 1 request per minute

Exceeding rate limits returns `429 Too Many Requests`.

---

## Interactive Documentation

For interactive API testing, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide a complete API reference with the ability to test endpoints directly in the browser.
