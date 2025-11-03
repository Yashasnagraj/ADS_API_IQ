#!/bin/bash
# Render startup script for MarketingIQ API

echo "Starting MarketingIQ Google Ads API..."

# Navigate to api directory (already in api directory from build command)
# Ensure we're in the right directory
cd "$(dirname "$0")" || cd /opt/render/project/src/api || true

# Copy database file if it exists in parent directory
if [ -f "../marketing_warehouse.db" ]; then
    echo "Copying database file to api directory..."
    cp ../marketing_warehouse.db ./marketing_warehouse.db || true
fi

# Run database migrations/setup if needed
python -c "from app.db.database import engine, Base; Base.metadata.create_all(bind=engine); print('Database tables created')"

# Start the FastAPI application
# Try gunicorn first (better for production), fallback to uvicorn if gunicorn fails
if command -v gunicorn &> /dev/null; then
    echo "Starting with gunicorn..."
    exec gunicorn app.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} --timeout 120
else
    echo "Starting with uvicorn..."
    exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2
fi
