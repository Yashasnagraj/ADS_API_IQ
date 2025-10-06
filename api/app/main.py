"""
MarketingIQ Google Ads REST API
Main application entry point
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.db.database import engine, Base
from app.routes import campaigns, ad_groups, keywords, search_terms, ml_features, metrics, customers

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting MarketingIQ Google Ads API")
    # Create tables if they don't exist (for SQLAlchemy models)
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    logger.info("Shutting down MarketingIQ Google Ads API")

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    description="Production-grade REST API for Google Ads ETL data access",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"/api/{settings.API_VERSION}/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=False,  # Must be False when allow_origins is ["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(customers.router, prefix=f"/api/{settings.API_VERSION}")
app.include_router(campaigns.router, prefix=f"/api/{settings.API_VERSION}")
app.include_router(ad_groups.router, prefix=f"/api/{settings.API_VERSION}")
app.include_router(keywords.router, prefix=f"/api/{settings.API_VERSION}")
app.include_router(search_terms.router, prefix=f"/api/{settings.API_VERSION}")
app.include_router(ml_features.router, prefix=f"/api/{settings.API_VERSION}")
app.include_router(metrics.router, prefix=f"/api/{settings.API_VERSION}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.API_VERSION,
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        # Test database connection
        from app.db.database import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "version": settings.API_VERSION
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )