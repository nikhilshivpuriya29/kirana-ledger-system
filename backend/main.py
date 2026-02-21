from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
from database import db, COLLECTIONS
from batch_scheduler import BatchJobScheduler

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("Starting Bahi-Khata Digital API")
    db.connect_db()
    BatchJobScheduler.initialize_scheduler()
    logger.info("Database and batch scheduler initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Bahi-Khata Digital API")
    BatchJobScheduler.shutdown_scheduler()
    db.close_db()
    logger.info("Cleanup completed")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Bahi-Khata Digital API",
    description="Rural Retail Credit & Ledger Management System API",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routes
from routes import auth, customers, ledger, analytics

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(customers.router, prefix="/api/v1/customers", tags=["Customers"])
app.include_router(ledger.router, prefix="/api/v1/ledger", tags=["Ledger"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Bahi-Khata Digital API",
        "status": "running",
        "version": "0.1.0",
        "endpoints": {
            "auth": "/api/v1/auth",
            "customers": "/api/v1/customers",
            "ledger": "/api/v1/ledger",
            "analytics": "/api/v1/analytics",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "bahi-khata-backend"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
