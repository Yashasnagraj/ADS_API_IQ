# MarketingIQ Platform - Run Guide

## Quick Start (Easiest Method)

### Windows

**Double-click one of these files:**

```
run_all_services.bat        (Batch script - most compatible)
run_all_services.ps1        (PowerShell - better output)
```

This will automatically start:
1. ✅ SQLite Data API (Port 8004)
2. ✅ ADK Chatbot API (Port 8003)
3. ✅ React Dashboard (Port 3000)

Then navigate to: **http://localhost:3000**

---

## What Gets Started

| Service | Port | Description | Window Title |
|---------|------|-------------|--------------|
| **SQLite Data API** | 8004 | Serves Google Ads data from SQLite database | 🗄️ SQLite Data API - Port 8004 |
| **ADK Chatbot API** | 8003 | Multi-agent chatbot interface | 💬 ADK Chatbot API - Port 8003 |
| **React Dashboard** | 3000 | Main web interface | ⚛️ React Dashboard - Port 3000 |

---

## Prerequisites

Before running, ensure you have:

### 1. Python 3.8+ installed
```bash
python --version
# Should show: Python 3.8.x or higher
```

### 2. Node.js 16+ installed
```bash
node --version
# Should show: v16.x.x or higher
```

### 3. Backend dependencies installed
```bash
pip install -r requirements.txt
```

Required packages:
- fastapi
- uvicorn
- pydantic
- requests
- google-adk
- loguru

### 4. Frontend dependencies installed
```bash
cd marketingiq-platform/web
npm install
```

### 5. Database populated
```bash
# Run ETL pipeline to populate database
python google_ads_etl_pipeline.py
```

This creates `google_ads_data.db` with your Google Ads data.

---

## Starting Services

### Option 1: All-in-One Launcher (Recommended)

**Windows Batch:**
```bash
run_all_services.bat
```

**PowerShell:**
```bash
.\run_all_services.ps1
```

**Features:**
- ✅ Checks prerequisites
- ✅ Validates ports are available
- ✅ Starts all 3 services
- ✅ Opens browser automatically
- ✅ Shows service URLs

### Option 2: Manual Start

**Terminal 1 - Data API:**
```bash
python api_sqlite.py
```

**Terminal 2 - Chatbot API:**
```bash
cd google-ads-multiagent/adk
python chatbot_api.py
```

**Terminal 3 - React Dashboard:**
```bash
cd marketingiq-platform/web
npm start
```

### Option 3: Individual Service Scripts

**Start Data API:**
```bash
# Create if needed
python api_sqlite.py
```

**Start Chatbot:**
```bash
cd google-ads-multiagent/adk
start_chatbot.bat
```

**Start Frontend:**
```bash
cd marketingiq-platform/web
npm start
```

---

## Stopping Services

### Option 1: Stop Script
```bash
stop_all_services.bat
```

This forcefully terminates all services.

### Option 2: Manual Stop
Close each service window individually.

### Option 3: Task Manager
Kill processes listening on ports 3000, 8003, 8004:
```bash
# Find processes
netstat -ano | findstr ":3000 :8003 :8004"

# Kill by PID
taskkill /F /PID <PID>
```

---

## Verifying Services Are Running

### Check All Services
```bash
# Windows Command Prompt
netstat -ano | findstr ":3000 :8003 :8004"

# PowerShell
Get-NetTCPConnection -LocalPort 3000,8003,8004
```

### Health Checks

**Data API:**
```bash
curl http://localhost:8004/health
```

**Chatbot API:**
```bash
curl http://localhost:8003/health
```

**Dashboard:**
Open browser to http://localhost:3000

### Test Chatbot
```bash
cd google-ads-multiagent/adk
python test_chatbot.py
```

---

## Using the Platform

### 1. Access Dashboard
Open browser to: **http://localhost:3000**

### 2. Select Customer (Optional)
- Use the customer dropdown in the global filter bar
- All dashboards and chatbot will scope to that customer

### 3. Use the Chatbot
Click the **💬 chat icon** in the bottom-right corner.

**Try these queries:**
- "Show top performing campaigns"
- "What keywords are underperforming?"
- "How should I optimize my budget?"
- "Analyze my performance trends"
- "Forecast next month's spend"
- "Are there any issues with my campaigns?"

### 4. Explore Dashboards
Navigate using the sidebar:
- 📊 Data Dashboard - Campaign/Keyword/AdGroup data
- 💡 Insights - Trends and anomalies
- ⚡ Optimization - Bid/Budget recommendations
- 🔮 Forecasting - Performance predictions
- 🚨 Alerts - Threshold monitoring

---

## Troubleshooting

### Port Already in Use

**Error:**
```
Address already in use: Port 3000/8003/8004
```

**Solution:**
```bash
# Stop all services first
stop_all_services.bat

# Or find and kill the specific process
netstat -ano | findstr :3000
taskkill /F /PID <PID>
```

### React Not Starting

**Error:**
```
Module not found
```

**Solution:**
```bash
cd marketingiq-platform/web
npm install
npm start
```

### Chatbot Connection Error

**Error in browser:**
```
Failed to connect to chatbot server
```

**Check:**
1. Is chatbot API running?
   ```bash
   curl http://localhost:8003/health
   ```

2. Check console in chatbot window for errors

3. Verify ADK agents loaded:
   Look for "ADK Agents Available: True"

### No Data in Dashboard

**Possible causes:**
1. Database empty - Run ETL pipeline:
   ```bash
   python google_ads_etl_pipeline.py
   ```

2. Data API not running:
   ```bash
   curl http://localhost:8004/campaigns
   ```

3. CORS error - Check browser console

### Python Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
pip install -r requirements.txt
```

For ADK specifically:
```bash
pip install google-adk
```

---

## Development Mode

### Hot Reload

**React (automatically enabled):**
- Changes to `.tsx` files auto-reload
- Just edit and save

**Python APIs (manual restart):**
1. Stop the service (Ctrl+C in terminal)
2. Restart with `python <script>.py`

Or use a tool like `uvicorn` with `--reload`:
```bash
uvicorn chatbot_api:app --reload --port 8003
```

### Debug Mode

**Backend:**
Set environment variable:
```bash
set DEBUG=true
python api_sqlite.py
```

**Frontend:**
Check `src/config/api.ts`:
```typescript
DEBUG: true
```

### View Logs

**Backend:**
- Logs appear in the service terminal window
- For chatbot: Look in ADK Chatbot API window

**Frontend:**
- Press F12 in browser
- Check Console tab

---

## Service URLs Reference

| Service | URL | Documentation |
|---------|-----|---------------|
| React Dashboard | http://localhost:3000 | Main UI |
| Data API Docs | http://localhost:8004/docs | Swagger/OpenAPI |
| Chatbot API Docs | http://localhost:8003/docs | Swagger/OpenAPI |
| Data API Health | http://localhost:8004/health | JSON health status |
| Chatbot Health | http://localhost:8003/health | JSON health status |

---

## Production Deployment

### Environment Variables

Create `.env` file:
```env
# API Configuration
DATA_API_URL=http://localhost:8004
CHATBOT_API_URL=http://localhost:8003

# Database
DATABASE_PATH=google_ads_data.db

# Google Ads API (for ETL)
GOOGLE_ADS_DEVELOPER_TOKEN=your_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
```

### Build Frontend for Production
```bash
cd marketingiq-platform/web
npm run build

# Serve with a static server
npx serve -s build -l 3000
```

### Run Backend in Production
```bash
# Use gunicorn (Linux) or waitress (Windows)
pip install waitress

# Run Data API
waitress-serve --port=8004 api_sqlite:app

# Run Chatbot API
cd google-ads-multiagent/adk
waitress-serve --port=8003 chatbot_api:app
```

---

## File Structure

```
ADS_API/
├── run_all_services.bat           ← Start all (Batch)
├── run_all_services.ps1           ← Start all (PowerShell)
├── stop_all_services.bat          ← Stop all
├── api_sqlite.py                  ← Data API
├── google_ads_data.db             ← Database
├── requirements.txt               ← Python deps
│
├── google-ads-multiagent/
│   └── adk/
│       ├── chatbot_api.py         ← Chatbot API
│       ├── start_chatbot.bat      ← Start chatbot only
│       └── test_chatbot.py        ← Test chatbot
│
└── marketingiq-platform/
    └── web/
        ├── package.json           ← React deps
        ├── src/
        │   ├── config/api.ts      ← API URLs
        │   └── components/
        │       └── chatbot/
        │           └── FloatingChatbot.tsx
        └── public/
```

---

## Support

### Check Service Status
```bash
# Windows
netstat -ano | findstr ":3000 :8003 :8004"

# PowerShell
Get-NetTCPConnection -LocalPort 3000,8003,8004
```

### Test Each Service
```bash
# Data API
curl http://localhost:8004/campaigns

# Chatbot API
curl http://localhost:8003/api/agents

# Frontend
curl http://localhost:3000
```

### Common Issues

1. **Port conflicts** → Run `stop_all_services.bat` first
2. **Module not found** → Run `pip install -r requirements.txt`
3. **No data** → Run ETL pipeline
4. **CORS errors** → Check API is running and CORS is enabled

---

## Quick Reference Commands

```bash
# START ALL
run_all_services.bat

# STOP ALL
stop_all_services.bat

# TEST CHATBOT
cd google-ads-multiagent\adk && python test_chatbot.py

# CHECK PORTS
netstat -ano | findstr ":3000 :8003 :8004"

# VIEW LOGS
# Check the individual service windows

# POPULATE DATABASE
python google_ads_etl_pipeline.py
```

---

**Ready to Start?**

Run: `run_all_services.bat`

Then open: http://localhost:3000 🚀
