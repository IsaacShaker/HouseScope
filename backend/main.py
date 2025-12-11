"""
HouseScope Backend - FastAPI Main Application
Entry point for the FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base

# Import routers
# from app.api import auth, accounts, transactions, financials, affordability, properties, admin

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Personal finance and real estate analysis platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["Authentication"])
# app.include_router(accounts.router, prefix=f"{settings.API_PREFIX}/accounts", tags=["Accounts"])
# app.include_router(transactions.router, prefix=f"{settings.API_PREFIX}/transactions", tags=["Transactions"])
# app.include_router(financials.router, prefix=f"{settings.API_PREFIX}/financials", tags=["Financials"])
# app.include_router(affordability.router, prefix=f"{settings.API_PREFIX}/affordability", tags=["Affordability"])
# app.include_router(properties.router, prefix=f"{settings.API_PREFIX}/properties", tags=["Properties"])
# app.include_router(admin.router, prefix=f"{settings.API_PREFIX}/admin", tags=["Admin"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to HouseScope API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
