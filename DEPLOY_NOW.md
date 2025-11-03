# 🚀 Deploy to Render RIGHT NOW - Quick Guide

## ⚡ Backend Deployment (5 Minutes)

### 1. Go to Render Dashboard
👉 https://dashboard.render.com

### 2. Create Web Service
- Click **"New +"** → **"Web Service"**
- Connect your GitHub repo
- Select repository

### 3. Fill Settings (Copy-Paste These)

```
Name: marketingiq-api
Region: Oregon
Branch: main (or ai-intelligence-upgrade)
Root Directory: api
Runtime: Python 3

Build Command:
pip install -r requirements.txt && cp ../marketing_warehouse.db ./marketing_warehouse.db || echo "Using default DB"

Start Command:
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000} --workers 2
```

### 4. Environment Variables (Click "Advanced")

Copy-paste these ONE BY ONE:

```
PORT
10000

DATABASE_URL
sqlite:///./marketing_warehouse.db

API_VERSION
v1

DEBUG
false

LOG_LEVEL
INFO

CORS_ORIGINS
["*"]

PAGINATION_DEFAULT_LIMIT
100

PAGINATION_MAX_LIMIT
1000
```

### 5. Click "Create Web Service"

Wait 5-10 minutes. You'll get a URL like:
```
https://marketingiq-api.onrender.com
```

### 6. Test Backend

Open in browser:
```
https://your-backend-url.onrender.com/health
https://your-backend-url.onrender.com/docs
```

**Expected:**
```json
{"status": "healthy", "database": "healthy", "version": "v1"}
```

✅ **Backend Done!** Copy your backend URL for next step.

---

## ⚡ Frontend Deployment (5 Minutes)

### 1. Create Static Site
- Click **"New +"** → **"Static Site"**
- Same GitHub repo

### 2. Fill Settings

```
Name: marketingiq-frontend
Region: Same as backend (Oregon)
Branch: main (or ai-intelligence-upgrade)
Root Directory: marketingiq-platform/web

Build Command:
npm install && npm run build

Publish Directory:
dist
```

### 3. Environment Variable (Click "Advanced")

**IMPORTANT:** Replace with YOUR actual backend URL:

```
VITE_API_BASE_URL
https://your-actual-backend-url.onrender.com/api/v1
```

Example:
```
VITE_API_BASE_URL
https://marketingiq-api.onrender.com/api/v1
```

### 4. Click "Create Static Site"

Wait 5-10 minutes. You'll get a URL like:
```
https://marketingiq-frontend.onrender.com
```

### 5. Test Frontend

Open in browser and check:
- [ ] Dashboard loads
- [ ] No CORS errors in console (F12)
- [ ] Customer dropdown works
- [ ] Data displays

✅ **Frontend Done!**

---

## 🔒 Final Step - Secure CORS (1 Minute)

### Update Backend CORS

1. Go to backend service in Render
2. Click **"Environment"** tab
3. Find `CORS_ORIGINS`
4. Change from `["*"]` to:
   ```
   ["https://your-frontend-url.onrender.com"]
   ```
5. Click **"Save Changes"**

Backend will auto-redeploy (1 minute).

---

## ✅ You're Live!

**Your URLs:**
- 🎨 Frontend: `https://your-frontend-url.onrender.com`
- 🔧 API: `https://your-backend-url.onrender.com`
- 📚 API Docs: `https://your-backend-url.onrender.com/docs`

---

## 🔍 Troubleshooting

### Backend Shows "Exited with status 127"
**In Render Dashboard → Your Service → Settings:**
- Make sure Start Command is EXACTLY:
  ```
  uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000} --workers 2
  ```
- Check Root Directory is `api`
- Click "Manual Deploy"

### Frontend Can't Connect to Backend
- Verify `VITE_API_BASE_URL` includes `/api/v1` at the end
- Check backend `/health` endpoint works
- Open browser console (F12) for errors
- Verify CORS is set correctly

### Database Errors
- In Render Shell, run: `ls -la marketing_warehouse.db`
- Check `DATABASE_URL` is: `sqlite:///./marketing_warehouse.db`
- Verify database file is in Git: `git ls-files marketing_warehouse.db`

### Cold Start (First Request Slow)
- Free tier spins down after 15 min
- First request takes 30-60 seconds
- Subsequent requests are fast
- Upgrade to $7/month to eliminate cold starts

---

## 📊 View Logs

**Backend Logs:**
Render Dashboard → marketingiq-api → Logs tab

**Frontend Logs:**
Browser Console (F12) → Console tab

---

## 💰 Cost Summary

**Free Tier (Current):**
- Backend: Free (cold starts)
- Frontend: Free (static)
- Database: Included
- **Total: $0/month**

**Recommended Production:**
- Backend: $7/month (no cold starts)
- Frontend: Free
- PostgreSQL: $7/month (persistent)
- **Total: $14/month**

---

## 🎯 Quick Test Checklist

After deployment, test these:

### Backend:
- [ ] `/health` returns healthy
- [ ] `/api/v1/customers` returns data
- [ ] `/docs` shows API documentation
- [ ] No errors in logs

### Frontend:
- [ ] Homepage loads
- [ ] Data Dashboard shows campaigns
- [ ] Insights Dashboard shows insights
- [ ] Customer filter works
- [ ] No console errors

### Integration:
- [ ] Frontend can fetch from backend
- [ ] No CORS errors
- [ ] Filters update data correctly
- [ ] All dashboards functional

---

## 🔄 Auto-Deploy Setup

Render automatically deploys when you push to GitHub:

```bash
# Make changes locally
git add .
git commit -m "Update feature"
git push

# Render auto-deploys in 5-10 minutes
```

---

## 📞 Need Help?

1. **Check Logs First:**
   - Backend: Render Dashboard → Logs
   - Frontend: Browser Console (F12)

2. **Common Issues:**
   - Exit 127: Wrong start command
   - Database not found: Check build logs
   - CORS errors: Update CORS_ORIGINS
   - Cold start: Wait 60 seconds

3. **Render Docs:**
   - https://render.com/docs

---

## 🎉 Success!

You now have a fully deployed multi-customer Google Ads analytics platform!

**Share your URLs:**
- Show clients the dashboard
- Demo AI insights
- Test campaign optimization

**Next Steps:**
- Add custom domain (optional)
- Upgrade to paid tier for production
- Set up monitoring/alerts
- Add more customers

---

**Created:** $(date)
**Platform:** Render.com
**Stack:** FastAPI + React + SQLite
