# 🚀 Complete Setup Guide - MarketingIQ Platform

**For Boss/Team Member with Cursor Pro**

This guide will help you set up the entire MarketingIQ Google Ads Analytics Platform on your machine.

---

## 📋 Prerequisites

Before starting, make sure you have:

- ✅ **Cursor Pro** (already installed)
- ✅ **Git** installed
- ✅ **Node.js 18+** installed ([Download](https://nodejs.org/))
- ✅ **Python 3.11+** installed ([Download](https://www.python.org/downloads/))
- ✅ **Google Ads API credentials** (developer token, client ID, client secret, refresh token)

---

## 🎯 Quick Start (5 Steps)

### Step 1: Clone the Repository

Open terminal/command prompt:

```bash
git clone https://github.com/Yashasnagraj/ADS_API_IQ.git
cd ADS_API_IQ
```

### Step 2: Setup Backend API

```bash
# Navigate to API directory
cd api

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Google Ads API Credentials

Create `.env` file in the `api/` directory:

```bash
# Copy the example file
cp .env.example .env
```

Edit `api/.env` with your Google Ads credentials:

```env
# Google Ads API Configuration
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token_here
GOOGLE_ADS_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_ADS_CLIENT_SECRET=your_client_secret_here
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token_here
GOOGLE_ADS_LOGIN_CUSTOMER_ID=1234567890

# API Configuration
API_VERSION=v1
DEBUG=true
LOG_LEVEL=INFO

# Database
DATABASE_URL=sqlite:///./google_ads_data.db

# CORS Origins (for development)
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001","http://127.0.0.1:3000","http://127.0.0.1:3001"]
```

**⚠️ IMPORTANT:** Replace all `your_*_here` values with actual Google Ads API credentials.

### Step 4: Run Data ETL Pipeline

Fetch Google Ads data and populate the database:

```bash
# Still in the api/ directory with venv activated
cd ..
python etl_pipeline.py
```

This will:
- Connect to Google Ads API
- Fetch campaigns, ad groups, keywords, search terms
- Generate ML features and quality scores
- Store everything in `google_ads_data.db`

**Expected output:**
```
✓ Fetched 25 campaigns
✓ Fetched 150 ad groups
✓ Fetched 500 keywords
✓ Generated ML features
✓ Database populated successfully
```

### Step 5: Start Backend API

```bash
cd api
python -m uvicorn app.main:app --reload --port 8000
```

**Backend should be running at:** `http://localhost:8000`

**Test it:** Open browser → `http://localhost:8000/health`

Should see:
```json
{
  "status": "healthy",
  "database": "healthy",
  "version": "v1"
}
```

**View API docs:** `http://localhost:8000/docs`

---

## 🎨 Frontend Setup

**Open a NEW terminal** (keep backend running):

```bash
# Navigate to frontend
cd marketingiq-platform/web

# Install dependencies
npm install --legacy-peer-deps

# Start development server
npm start
```

**Frontend will open at:** `http://localhost:3001`

---

## 🧪 Verify Everything Works

### 1. Check Backend API

Open: `http://localhost:8000/docs`

Try these endpoints:
- `GET /api/v1/campaigns` - Should return campaigns
- `GET /api/v1/metrics/summary` - Should return KPIs
- `GET /api/v1/ecommerce/overview` - Should return e-commerce data

### 2. Check Frontend Dashboard

Open: `http://localhost:3001`

You should see:
- ✅ Landing page with metrics
- ✅ Command center dashboard
- ✅ E-commerce performance dashboard at `/dashboard`
- ✅ Data explorer at `/data/campaigns`

### 3. Test API Connection

Open browser console (F12) on frontend:
- ❌ If you see CORS errors → Backend not running
- ❌ If you see "process is not defined" → Clear cache (Ctrl+Shift+R)
- ✅ Should see successful API calls

---

## 📁 Project Structure

```
ADS_API_IQ/
│
├── api/                          # Backend FastAPI
│   ├── app/
│   │   ├── routes/              # API endpoints
│   │   ├── schemas/             # Pydantic models
│   │   ├── services/            # Business logic
│   │   ├── db/                  # Database models
│   │   └── main.py              # FastAPI app
│   ├── requirements.txt         # Python dependencies
│   ├── .env                     # API credentials (create this!)
│   └── start.sh                 # Production startup script
│
├── marketingiq-platform/web/    # Frontend React
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── hooks/               # Custom hooks
│   │   ├── config/              # API configuration
│   │   └── App.tsx              # Main app
│   ├── package.json             # Node dependencies
│   └── webpack.config.js        # Build configuration
│
├── etl_pipeline.py              # Google Ads data fetcher
├── google_ads_data.db           # SQLite database (auto-created)
└── SETUP_GUIDE_FOR_BOSS.md     # This file
```

---

## 🔑 Getting Google Ads API Credentials

If you don't have Google Ads API credentials yet:

### 1. Developer Token

1. Go to [Google Ads API Center](https://ads.google.com/aw/apicenter)
2. Apply for developer token
3. Wait for approval (can take 24-48 hours)

### 2. OAuth2 Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project: "MarketingIQ API"
3. Enable **Google Ads API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Application type: **Desktop app**
6. Copy **Client ID** and **Client Secret**

### 3. Refresh Token

Run this Python script to get refresh token:

```python
# generate_refresh_token.py
from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'

flow = InstalledAppFlow.from_client_config(
    {
        "installed": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uris": ["http://localhost:8080"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    },
    scopes=["https://www.googleapis.com/auth/adwords"],
)

flow.run_local_server(port=8080)
credentials = flow.credentials
print(f"Refresh Token: {credentials.refresh_token}")
```

Run:
```bash
pip install google-auth-oauthlib
python generate_refresh_token.py
```

Copy the refresh token to your `.env` file.

---

## 🛠️ Using Cursor Pro Features

### 1. Open Project in Cursor

```bash
cursor .
```

Or: File → Open Folder → Select `ADS_API_IQ`

### 2. Use Cursor Chat (Ctrl+L)

Ask Cursor to help you:
- "Explain how the ETL pipeline works"
- "Show me all API endpoints"
- "Debug why my API is returning empty data"
- "Add a new endpoint for getting top performing keywords"

### 3. Use Cursor Composer (Ctrl+Shift+I)

For multi-file edits:
- "Add customer filtering to all dashboards"
- "Create a new report for campaign performance"
- "Refactor the ecommerce service to use async functions"

### 4. Quick Commands

- **Ctrl+K**: Inline code generation
- **Ctrl+L**: Chat with Cursor
- **Ctrl+Shift+I**: Composer for complex tasks
- **Ctrl+P**: Quick file search

### 5. Ask Cursor to Run Commands

In Cursor chat:
```
Can you run the ETL pipeline and show me the output?
```

```
Start the backend server in the background
```

```
Install missing dependencies and start the frontend
```

---

## 🐛 Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```bash
# Backend
cd api
pip install -r requirements.txt

# Frontend
cd marketingiq-platform/web
npm install --legacy-peer-deps
```

### Issue: "Database is locked"

**Solution:**
```bash
# Stop all running servers
# Delete the database
rm google_ads_data.db
# Run ETL again
python etl_pipeline.py
```

### Issue: "Google Ads API authentication failed"

**Solution:**
- Check `.env` file has correct credentials
- Verify developer token is approved
- Refresh token might be expired → generate new one
- Check customer ID is correct (10 digits, no dashes)

### Issue: Frontend shows "process is not defined"

**Solution:**
```bash
# Hard refresh browser
Ctrl + Shift + R

# Or clear cache and restart dev server
cd marketingiq-platform/web
rm -rf node_modules dist
npm install --legacy-peer-deps
npm start
```

### Issue: CORS errors in browser

**Solution:**
- Make sure backend is running on `http://localhost:8000`
- Check `api/app/main.py` has CORS configured
- Backend should show in terminal: "Application startup complete"

### Issue: No data in dashboards

**Solution:**
1. Check if database exists: `ls google_ads_data.db`
2. Run ETL pipeline: `python etl_pipeline.py`
3. Verify data in database:
   ```bash
   sqlite3 google_ads_data.db
   SELECT COUNT(*) FROM campaigns_performance;
   .exit
   ```

---

## 📊 Available Dashboards

Once everything is running, you can access:

### 1. **Landing Page** - `http://localhost:3001/`
- Overview metrics
- Trend charts
- Quick insights

### 2. **Command Center** - `http://localhost:3001/`
- Real-time KPIs
- AI predictions
- Multi-metric analysis

### 3. **E-Commerce Dashboard** - `http://localhost:3001/dashboard`
- Revenue & orders
- Conversion funnel
- Channel performance
- Product analysis
- Customer segmentation
- 7-day forecast
- Anomaly detection

### 4. **Data Explorer**
- Campaigns: `http://localhost:3001/data/campaigns`
- Ad Groups: `http://localhost:3001/data/adgroups`
- Keywords: `http://localhost:3001/data/keywords`
- Search Terms: `http://localhost:3001/data/search-terms`

### 5. **Multi-Agent System** - `http://localhost:3001/agents`
- Data Agent
- Insight Agent
- Optimization Agent
- Forecasting Agent
- Alert Agent

---

## 🔄 Daily Workflow

### Morning Setup

```bash
# Terminal 1: Start Backend
cd api
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Start Frontend
cd marketingiq-platform/web
npm start

# Terminal 3: Run ETL (to fetch fresh data)
python etl_pipeline.py
```

### Update Data

```bash
# Run ETL pipeline to fetch latest Google Ads data
python etl_pipeline.py
```

### Make Code Changes

Use Cursor Pro:
1. Open file in Cursor
2. Select code section
3. Press `Ctrl+K` for inline edit
4. Or use `Ctrl+L` for chat-based changes

### Test Changes

- Backend changes: Server auto-reloads (with `--reload` flag)
- Frontend changes: Webpack auto-reloads in browser

---

## 🚀 Production Deployment

### Backend (Render.com)

Follow: `RENDER_DEPLOYMENT.md`

Quick steps:
1. Push code to GitHub
2. Go to https://render.com
3. Create Web Service from GitHub repo
4. Configure:
   - Root: `api`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (same as .env)
6. Deploy

### Frontend (Netlify)

Already configured! Just push to GitHub:
```bash
git push origin master
```

Netlify auto-deploys from: `netlify.toml`

**Live URL:** https://marketingkk.netlify.app

---

## 📞 Support

### Ask Cursor Pro

Use Cursor's AI to help:
- "How do I add a new API endpoint?"
- "Explain the ecommerce insights service"
- "Debug why my dashboard is showing empty data"
- "Create a new component for displaying alerts"

### Check Documentation

- **Frontend:** `marketingiq-platform/web/README.md`
- **Backend:** `api/README.md`
- **ETL:** `ETL_PIPELINE.md`
- **Deployment:** `RENDER_DEPLOYMENT.md`, `NETLIFY_BUILD_FIX.md`

### Common Cursor Commands

```
cursor: show me all API endpoints

cursor: explain how customer filtering works

cursor: create a new dashboard component for budget analysis

cursor: debug the ETL pipeline authentication

cursor: add logging to the ecommerce service
```

---

## ✅ Setup Checklist

- [ ] Git repository cloned
- [ ] Node.js 18+ installed
- [ ] Python 3.11+ installed
- [ ] Backend virtual environment created
- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with Google Ads credentials
- [ ] ETL pipeline executed successfully
- [ ] Backend running at `http://localhost:8000`
- [ ] Backend health check returns 200 OK
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Frontend running at `http://localhost:3001`
- [ ] Dashboards loading with data
- [ ] No CORS errors in browser console
- [ ] API calls successful in Network tab

---

## 🎯 Quick Commands Reference

### Backend
```bash
# Start server
cd api && python -m uvicorn app.main:app --reload --port 8000

# Run ETL
python etl_pipeline.py

# Check database
sqlite3 google_ads_data.db "SELECT COUNT(*) FROM campaigns_performance;"
```

### Frontend
```bash
# Start dev server
cd marketingiq-platform/web && npm start

# Build for production
npm run build

# Clean install
rm -rf node_modules && npm install --legacy-peer-deps
```

### Git
```bash
# Pull latest changes
git pull origin master

# Check status
git status

# View recent commits
git log --oneline -10
```

---

## 🔐 Environment Variables Summary

### Backend (`api/.env`)
```env
GOOGLE_ADS_DEVELOPER_TOKEN=<your_token>
GOOGLE_ADS_CLIENT_ID=<your_client_id>
GOOGLE_ADS_CLIENT_SECRET=<your_secret>
GOOGLE_ADS_REFRESH_TOKEN=<your_refresh_token>
GOOGLE_ADS_LOGIN_CUSTOMER_ID=<your_customer_id>
DEBUG=true
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./google_ads_data.db
```

### Frontend (Netlify - Production)
```env
REACT_APP_API_URL=https://your-backend.onrender.com/api/v1
NODE_VERSION=18
```

---

## 🎓 Learning Resources

### FastAPI
- Docs: https://fastapi.tiangolo.com
- Tutorial: https://fastapi.tiangolo.com/tutorial/

### React
- Docs: https://react.dev
- MUI: https://mui.com

### Google Ads API
- Docs: https://developers.google.com/google-ads/api/docs/start
- Python client: https://github.com/googleads/google-ads-python

### SQLite
- Docs: https://www.sqlite.org/docs.html
- Browser: https://sqlitebrowser.org

---

## 🚦 System Status

After setup, verify:

### Backend Health
```bash
curl http://localhost:8000/health
```

### Frontend Status
Open browser → `http://localhost:3001`

### Database Stats
```bash
sqlite3 google_ads_data.db << EOF
SELECT 'Campaigns: ' || COUNT(*) FROM campaigns_performance;
SELECT 'Ad Groups: ' || COUNT(*) FROM adgroups_performance;
SELECT 'Keywords: ' || COUNT(*) FROM keywords_performance;
SELECT 'Search Terms: ' || COUNT(*) FROM search_terms;
.exit
EOF
```

---

## 💡 Pro Tips with Cursor

1. **Use Cursor Rules**: Create `.cursorrules` file for project-specific instructions
2. **Index codebase**: Let Cursor index the entire project for better suggestions
3. **Use @ mentions**: `@file` to reference specific files in chat
4. **Multi-file edits**: Use Composer (Ctrl+Shift+I) for changes across multiple files
5. **Terminal integration**: Ask Cursor to run commands directly

---

**🎉 You're all set! Everything should be running now.**

**Need help?** Ask Cursor Pro or check the troubleshooting section above.

**Happy coding! 🚀**
