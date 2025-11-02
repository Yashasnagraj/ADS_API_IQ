#!/bin/bash
# Render startup script for MarketingIQ API
# This script ensures database tables are created before starting the server

echo "Starting MarketingIQ Google Ads API..."

# Create database tables if they don't exist
python -c "from app.db.database import engine, Base; Base.metadata.create_all(bind=engine); print('Database tables created/verified')"

# Start the FastAPI application with gunicorn
# Render sets the PORT environment variable automatically
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -

