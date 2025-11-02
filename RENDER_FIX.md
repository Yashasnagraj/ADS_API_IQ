# Render Deployment Fix

## Issues Fixed:

1. **Exit Status 127** - Changed from using `start.sh` to direct uvicorn command
2. **Database Path** - Updated config to use relative path for Render deployment
3. **Build Command** - Added fallback for database copy

## Updated Configuration:

### In Render Dashboard:

**Start Command:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000} --workers 2
```

**Build Command:**
```bash
pip install -r requirements.txt && cp ../marketing_warehouse.db ./marketing_warehouse.db || echo "Database not found"
```

## Deploy Instructions:

### If you're using Render Dashboard UI:

1. Go to your service settings
2. Update **Start Command** to:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000} --workers 2
   ```
3. Save changes
4. Manual deploy or wait for auto-deploy

### If you're using `render.yaml`:

1. The file is already updated in your repo
2. Commit and push:
   ```bash
   git add api/render.yaml api/app/core/config.py
   git commit -m "Fix Render deployment configuration"
   git push
   ```
3. Render will auto-deploy

## Environment Variables (Make Sure These Are Set):

```
PORT=10000
DATABASE_URL=sqlite:///./marketing_warehouse.db
API_VERSION=v1
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=["*"]
PAGINATION_DEFAULT_LIMIT=100
PAGINATION_MAX_LIMIT=1000
```

## Testing After Deploy:

```bash
# Replace with your actual URL
curl https://your-service.onrender.com/health

# Should return:
# {"status": "healthy", "database": "healthy", "version": "v1"}
```

## If Still Having Issues:

### Check Render Logs for:

1. **Database file location:**
   - Build log should show: "Database copied" or "Database not found"
   - Runtime should show which database file it's using

2. **Import errors:**
   - Make sure all Python dependencies installed
   - Check if `app.main:app` is accessible

3. **Port binding:**
   - Uvicorn should bind to 0.0.0.0:10000
   - Check PORT environment variable is set

### Manual Debug in Render Shell:

1. Go to your service → Shell tab
2. Run:
   ```bash
   ls -la marketing_warehouse.db
   python -c "from app.main import app; print('App loaded')"
   python -c "from app.db.database import engine; print(engine.url)"
   ```

## Alternative Simpler Start Command (If above fails):

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

This uses Python module syntax which can be more reliable.
