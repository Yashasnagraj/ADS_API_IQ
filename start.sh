#!/bin/bash
# Render startup script for MarketingIQ API

echo "Starting MarketingIQ Google Ads API..."

# Run database migrations/setup if needed
python -c "from app.db.database import engine, Base; Base.metadata.create_all(bind=engine); print('Database tables created')"

# Start the FastAPI application with uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2
