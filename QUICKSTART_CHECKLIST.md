# Quick Start Checklist

Use this checklist to set up the MarketingIQ platform on your laptop.

---

## ✅ Pre-Setup Checklist

Before you begin, make sure you have:

- [ ] Python 3.8+ installed - Run: `python --version`
- [ ] Node.js 18+ installed - Run: `node --version`
- [ ] Git installed - Run: `git --version`
- [ ] Google Ads Manager Account access
- [ ] Google Ads API Developer Token
- [ ] Google Cloud Project with Ads API enabled
- [ ] OAuth 2.0 Client ID & Secret
- [ ] Gemini API Key from https://makersuite.google.com/app/apikey

---

## 🚀 Setup Steps (30 minutes)

### Step 1: ETL Pipeline (5 minutes)

```bash
# Install dependencies
pip install -r requirements.txt

# Configure credentials
cp google-ads.yaml.template google-ads.yaml
# Edit google-ads.yaml with your API credentials

# Generate refresh token (first time only)
python generate_refresh_token.py

# Run ETL to populate database
python warehouse_etl.py
```

**✓ Verify:** Check that `google_ads_data.db` file was created

---

### Step 2: Data API (5 minutes)

```bash
cd api

# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate
# OR (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "DATABASE_URL=sqlite:///../google_ads_data.db" > .env
echo "CORS_ORIGINS=[\"http://localhost:3001\",\"http://localhost:3000\"]" >> .env

# Start API (in a new terminal)
uvicorn app.main:app --reload --port 8000
```

**✓ Verify:** Open http://localhost:8000/health in browser

---

### Step 3: Multi-Agent System (10 minutes)

```bash
cd google-ads-multiagent

# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate
# OR (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure .env
cp .env.example .env
# Edit .env and add:
#   - Google Ads API credentials
#   - GEMINI_API_KEY
#   - DATABASE_PATH=../google_ads_data.db

# Start Agent API (in a new terminal)
python agent_api.py
```

**✓ Verify:** Open http://localhost:8001/health in browser

---

### Step 4: Frontend Dashboard (10 minutes)

```bash
cd marketingiq-platform/web

# Install Node.js dependencies
npm install --legacy-peer-deps

# Create .env file
echo "REACT_APP_API_URL=http://localhost:8000/api/v1" > .env
echo "REACT_APP_AGENT_API_URL=http://localhost:8001" >> .env

# Start frontend (in a new terminal)
npm start
```

**✓ Verify:** Browser should open to http://localhost:3001 with dashboard

---

## 🎯 Daily Usage

### Easy Start (Recommended)

**Windows:**
```bash
START_ALL.bat
```

**Mac/Linux:**
```bash
./start_all.sh
```

This starts all 3 services automatically!

---

### Manual Start (4 terminals)

**Terminal 1 - Data API:**
```bash
cd api
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Agent API:**
```bash
cd google-ads-multiagent
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
python agent_api.py
```

**Terminal 3 - Frontend:**
```bash
cd marketingiq-platform/web
npm start
```

**Terminal 4 - ETL (optional, to refresh data):**
```bash
python warehouse_etl.py
```

---

## 🧪 Test Everything Works

### 1. Check APIs are running

Open these URLs in your browser:
- Data API: http://localhost:8000/health → Should return `{"status":"healthy"}`
- Agent API: http://localhost:8001/health → Should return `{"status":"healthy","agents":5}`
- Dashboard: http://localhost:3001 → Should show MarketingIQ dashboard

### 2. Check database has data

```bash
python -c "import sqlite3; conn = sqlite3.connect('google_ads_data.db'); print('Campaigns:', conn.execute('SELECT COUNT(*) FROM campaigns_performance').fetchone()[0])"
```

Should print number of campaigns (> 0)

### 3. Test dashboard loads data

1. Open http://localhost:3001
2. Navigate to different sections (Campaigns, Keywords, etc.)
3. Open browser console (F12) - should see no errors
4. Try the chat feature to talk to AI agents

---

## 🐛 Common Issues

### "Module not found"
```bash
pip install -r requirements.txt  # For Python
npm install --legacy-peer-deps  # For Node.js
```

### "Authentication failed"
- Check `google-ads.yaml` has correct credentials
- Regenerate refresh token: `python generate_refresh_token.py`
- Verify developer token is approved (not test mode)

### "Port already in use"
**Windows:**
```bash
netstat -ano | findstr :8000
taskkill /PID <process_id> /F
```

**Mac/Linux:**
```bash
lsof -ti:8000 | xargs kill -9
```

### CORS errors in browser
- Make sure Data API is running on port 8000
- Make sure Agent API is running on port 8001
- Check `api/.env` has CORS_ORIGINS configured

### "process is not defined" in frontend
```bash
cd marketingiq-platform/web
rm -rf node_modules dist
npm install --legacy-peer-deps
npm start
```

---

## 📚 Documentation

- **Complete Guide:** See `README.md`
- **ETL Only:** See `ETL_SETUP_GUIDE.md`
- **Full Platform Setup:** See `SETUP_GUIDE_FOR_BOSS.md`
- **API Docs:** http://localhost:8000/docs and http://localhost:8001/docs

---

## 🎉 You're Done!

Access your dashboard at: **http://localhost:3001**

**Services running:**
- Data API: http://localhost:8000
- Agent API: http://localhost:8001
- Dashboard: http://localhost:3001

**To stop everything:**
- Close all terminal windows
- Or run: `./stop_all.sh` (Mac/Linux)

---

## 📞 Need Help?

1. Check the **Troubleshooting** section in README.md
2. Look at API documentation at `/docs` endpoints
3. Check terminal logs for error messages
4. Verify all prerequisites are installed correctly

---

**Last Updated:** October 2024
