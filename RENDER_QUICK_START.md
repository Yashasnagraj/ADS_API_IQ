# Quick Start: Render.com Deployment

## 🚀 Fast Deployment Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "Prepare for Render deployment"
git push
```

### 2. Deploy via Render Blueprint (Easiest)

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will auto-detect `render.yaml` and create both services

### 3. Set Environment Variables

#### Backend (`marketingiq-api`)

**Required:**
- `DATABASE_URL=sqlite:///./marketing_warehouse.db`
- `API_VERSION=v1`
- `DEBUG=false`
- `LOG_LEVEL=INFO`

**After frontend deploys, add:**
- `CORS_ORIGINS=https://marketingiq-frontend.onrender.com`

**From your `.env` file:**
- `GOOGLE_ADS_DEVELOPER_TOKEN`
- `GOOGLE_ADS_CLIENT_ID`
- `GOOGLE_ADS_CLIENT_SECRET`
- `GOOGLE_ADS_REFRESH_TOKEN`
- `GOOGLE_ADS_LOGIN_CUSTOMER_ID`

**From your `.env.meta` file:**
- `META_ACCESS_TOKEN`
- `META_AD_ACCOUNT_ID`
- `META_APP_ID`
- `META_APP_SECRET`

#### Frontend (`marketingiq-frontend`)

**After backend deploys, add:**
- `VITE_API_BASE_URL=https://marketingiq-api.onrender.com/api/v1`
- `VITE_DATA_API_URL=https://marketingiq-api.onrender.com`
- `VITE_AGENT_API_URL=https://marketingiq-api.onrender.com/api`

### 4. Test

**Backend:**
```bash
curl https://marketingiq-api.onrender.com/health
```

**Frontend:**
Open `https://marketingiq-frontend.onrender.com` in browser

---

## 📝 What Was Changed

✅ **CORS Configuration**: Now uses environment variables  
✅ **Chat API URL**: Uses environment variable instead of hardcoded localhost  
✅ **Start Script**: Improved for Render deployment  
✅ **render.yaml**: Created for automated deployment  
✅ **Deployment Guide**: Complete documentation created

---

## ⚠️ Important Notes

1. **Replace service names**: `marketingiq-api` and `marketingiq-frontend` with your actual service names
2. **CORS**: Must be set AFTER frontend is deployed
3. **Environment Variables**: Vite variables must start with `VITE_`
4. **Database**: SQLite files reset on free tier restarts (consider PostgreSQL for production)

---

## 📚 Full Documentation

See `RENDER_DEPLOYMENT_GUIDE.md` for complete details.

