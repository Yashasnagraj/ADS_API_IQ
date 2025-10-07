# ⚡ Quick Start - For Boss

**Get MarketingIQ running in 5 minutes**

---

## 🚀 Super Quick Setup (Windows)

```bash
# 1. Clone repository
git clone https://github.com/Yashasnagraj/ADS_API_IQ.git
cd ADS_API_IQ

# 2. Run automated setup
setup.bat

# 3. Add your Google Ads credentials
# Edit: api/.env (copy from api/.env.example)

# 4. Fetch Google Ads data
python etl_pipeline.py

# 5. Start everything (open 2 terminals)

# Terminal 1:
start-backend.bat

# Terminal 2:
start-frontend.bat
```

**Done!** Open: `http://localhost:3001`

---

## 🚀 Super Quick Setup (Mac/Linux)

```bash
# 1. Clone repository
git clone https://github.com/Yashasnagraj/ADS_API_IQ.git
cd ADS_API_IQ

# 2. Run automated setup
chmod +x setup.sh
./setup.sh

# 3. Add your Google Ads credentials
# Edit: api/.env (copy from api/.env.example)

# 4. Fetch Google Ads data
python etl_pipeline.py

# 5. Start everything (open 2 terminals)

# Terminal 1:
chmod +x start-backend.sh
./start-backend.sh

# Terminal 2:
chmod +x start-frontend.sh
./start-frontend.sh
```

**Done!** Open: `http://localhost:3001`

---

## 🔑 Google Ads API Credentials

You need these 5 things in `api/.env`:

```env
GOOGLE_ADS_DEVELOPER_TOKEN=abc123xyz
GOOGLE_ADS_CLIENT_ID=123-abc.apps.googleusercontent.com
GOOGLE_ADS_CLIENT_SECRET=GOCSPX-abc123
GOOGLE_ADS_REFRESH_TOKEN=1//abc123xyz
GOOGLE_ADS_LOGIN_CUSTOMER_ID=1234567890
```

**Where to get them:**
1. **Developer Token**: [Google Ads API Center](https://ads.google.com/aw/apicenter)
2. **Client ID & Secret**: [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
3. **Refresh Token**: Run `python generate_refresh_token.py` (see setup guide)
4. **Customer ID**: From Google Ads account (top right, Account → Settings)

---

## ✅ Verify It's Working

### 1. Backend Health Check
Open: `http://localhost:8000/health`

Should see:
```json
{"status": "healthy", "database": "healthy"}
```

### 2. API Documentation
Open: `http://localhost:8000/docs`

Try endpoint: `GET /api/v1/campaigns`

### 3. Frontend Dashboard
Open: `http://localhost:3001`

Should see:
- Landing page with metrics
- E-commerce dashboard
- Data explorer

### 4. Check Data
```bash
sqlite3 google_ads_data.db "SELECT COUNT(*) FROM campaigns_performance;"
```

Should return: `25` (or however many campaigns you have)

---

## 🎯 Available Dashboards

| Dashboard | URL | Description |
|-----------|-----|-------------|
| **Landing** | http://localhost:3001 | Overview & KPIs |
| **E-Commerce** | http://localhost:3001/dashboard | Full business dashboard |
| **Campaigns** | http://localhost:3001/data/campaigns | Campaign explorer |
| **Keywords** | http://localhost:3001/data/keywords | Keyword analysis |
| **Agents** | http://localhost:3001/agents | AI agent system |

---

## 🛠️ Using Cursor Pro

### Open Project
```bash
cursor .
```

### Ask Cursor (Ctrl+L)
- "Show me all API endpoints"
- "Explain the e-commerce dashboard"
- "How do I add a new chart?"
- "Debug why my dashboard is empty"

### Generate Code (Ctrl+K)
Select code → Press `Ctrl+K` → Type what you want

### Multi-File Edit (Ctrl+Shift+I)
For changes across multiple files

---

## 🐛 Common Issues

### "No data in dashboard"
```bash
python etl_pipeline.py
```

### "CORS error"
Backend not running. Start it:
```bash
cd api
python -m uvicorn app.main:app --reload
```

### "process is not defined"
Hard refresh: `Ctrl + Shift + R`

### "Module not found"
```bash
# Backend
cd api && pip install -r requirements.txt

# Frontend
cd marketingiq-platform/web && npm install --legacy-peer-deps
```

---

## 📞 Need Help?

1. **Read full guide**: `SETUP_GUIDE_FOR_BOSS.md`
2. **Ask Cursor**: Press `Ctrl+L` and ask your question
3. **Check logs**: Terminal output shows errors
4. **View documentation**: All `.md` files in root directory

---

## 🎓 Key Files

| File | Purpose |
|------|---------|
| `api/.env` | Google Ads credentials |
| `etl_pipeline.py` | Fetch Google Ads data |
| `google_ads_data.db` | SQLite database |
| `api/app/main.py` | Backend API |
| `marketingiq-platform/web/src/App.tsx` | Frontend app |

---

## 🔄 Daily Workflow

```bash
# Morning: Fetch fresh data
python etl_pipeline.py

# Start backend (Terminal 1)
start-backend.bat

# Start frontend (Terminal 2)
start-frontend.bat

# Make changes with Cursor
cursor .

# Changes auto-reload in browser
```

---

## 🚀 Deploy to Production

### Backend (Render)
See: `RENDER_DEPLOYMENT.md`

Quick:
1. Go to https://render.com
2. Connect GitHub repo
3. Deploy from `api/` folder
4. Get URL: `https://marketingiq-api.onrender.com`

### Frontend (Netlify)
**Already deployed!**
- URL: https://marketingkk.netlify.app
- Auto-deploys on git push

---

**That's it! You're ready to go! 🎉**

**For detailed instructions, see:** `SETUP_GUIDE_FOR_BOSS.md`
