# Simple Render Deployment (With Existing Database)

Since you already have `marketing_warehouse.db` with all your data, deployment is simpler. No ETL pipeline needed!

## What You're Deploying:

- ✅ **Backend API** (`api/` folder) - FastAPI app
- ✅ **Database** (`marketing_warehouse.db`) - Your existing data
- ✅ **Frontend** (`marketingiq-platform/web/`) - React dashboard

---

## Step 1: Prepare Your Database File

### Option A: Commit Database to Git (Easiest)

```bash
# Make sure the database file is tracked
git add marketing_warehouse.db
git commit -m "Add production database"
git push
```

**Note:** If your `.gitignore` blocks `.db` files, temporarily remove that rule.

### Option B: Upload After Deployment

You'll upload the database file directly to Render after deployment.

---

## Step 2: Deploy Backend

### 2.1 Create Web Service on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your repository

### 2.2 Configure Backend

```
Name: marketingiq-api
Region: Oregon (or closest)
Branch: main
Root Directory: api
Runtime: Python 3

Build Command:
pip install -r requirements.txt

Start Command:
chmod +x start.sh && ./start.sh
```

### 2.3 Environment Variables

**Required - Add These:**

```
DATABASE_URL=sqlite:///./marketing_warehouse.db
API_VERSION=v1
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=["*"]
PAGINATION_DEFAULT_LIMIT=100
PAGINATION_MAX_LIMIT=1000
```

**Note:** You don't need Google Ads API credentials since you're using the pre-built database!

### 2.4 Deploy

Click **"Create Web Service"** and wait 5-10 minutes.

Your backend will be live at: `https://marketingiq-api.onrender.com`

### 2.5 (If Option B) Upload Database

If you didn't commit the database to Git:

1. In Render Dashboard → Your Service → Shell
2. Upload `marketing_warehouse.db` via Render's file upload
3. Place it in the `/opt/render/project/src/` directory

---

## Step 3: Test Backend

```bash
# Health check
curl https://your-backend-url.onrender.com/health

# Get customers
curl https://your-backend-url.onrender.com/api/v1/customers

# API documentation
open https://your-backend-url.onrender.com/docs
```

Expected response for `/health`:
```json
{
  "status": "healthy",
  "database": "healthy",
  "version": "v1"
}
```

---

## Step 4: Deploy Frontend

### 4.1 Create Static Site

1. Click **"New +"** → **"Static Site"**
2. Select same repository

### 4.2 Configure Frontend

```
Name: marketingiq-frontend
Region: Same as backend
Branch: main
Root Directory: marketingiq-platform/web

Build Command:
npm install && npm run build

Publish Directory:
dist
```

### 4.3 Environment Variable

**Add this ONE variable:**

```
VITE_API_BASE_URL=https://your-backend-url.onrender.com/api/v1
```

Replace `your-backend-url` with your actual backend URL from Step 2.

### 4.4 Deploy

Click **"Create Static Site"** and wait 5-10 minutes.

Your frontend will be live at: `https://marketingiq-frontend.onrender.com`

---

## Step 5: Final Security Update

### Update CORS in Backend

1. Go to backend service in Render
2. Environment tab
3. Update `CORS_ORIGINS`:

```
CORS_ORIGINS=["https://your-frontend-url.onrender.com"]
```

4. Save (will auto-redeploy)

---

## Important Notes About SQLite on Render

### ⚠️ Free Tier Limitations:

- **Ephemeral Storage:** On free tier, files are reset when the container restarts
- **Database Resets:** Your `marketing_warehouse.db` will be restored to the Git version on each deploy/restart
- **Not for Production:** SQLite on free tier is good for demos/testing only

### 💡 Solutions:

**Option 1: Paid Plan with Persistent Disk ($7/month)**
- Add persistent disk storage
- Database persists across restarts
- Better for production

**Option 2: PostgreSQL Database (Recommended)**
- Free tier: 1GB storage
- Persistent data
- Better performance

**Option 3: Read-Only Demo**
- Use existing database as read-only
- Perfect if you're just showcasing the platform

---

## Environment Variables Summary

### Backend (`marketingiq-api`)
```bash
DATABASE_URL=sqlite:///./marketing_warehouse.db
API_VERSION=v1
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=["https://your-frontend-url.onrender.com"]
PAGINATION_DEFAULT_LIMIT=100
PAGINATION_MAX_LIMIT=1000
```

### Frontend (`marketingiq-frontend`)
```bash
VITE_API_BASE_URL=https://your-backend-url.onrender.com/api/v1
```

---

## Verification Checklist

- [ ] Backend deployed and shows "Live"
- [ ] `/health` endpoint returns healthy status
- [ ] `/api/v1/customers` returns customer data
- [ ] API docs accessible at `/docs`
- [ ] Frontend deployed and shows "Live"
- [ ] Frontend loads without errors
- [ ] Dashboards display data from backend
- [ ] Customer filtering works
- [ ] No CORS errors in browser console

---

## Testing Your Deployment

### 1. Test Backend API

```bash
# Replace with your actual backend URL
BACKEND_URL="https://marketingiq-api.onrender.com"

# Health check
curl $BACKEND_URL/health

# Get customers list
curl $BACKEND_URL/api/v1/customers

# Get campaigns for customer
curl "$BACKEND_URL/api/v1/campaigns?customer_id=5032737756"
```

### 2. Test Frontend

1. Open frontend URL in browser
2. Open Developer Tools (F12) → Console
3. Navigate to each dashboard:
   - Data Dashboard
   - Insights Dashboard
   - Optimization Dashboard
   - Forecasting Dashboard
   - Alerts Dashboard
4. Select different customers from dropdown
5. Verify data loads correctly

---

## Troubleshooting

### Backend Issues

**"Database not found" Error:**
- Check `DATABASE_URL` is set correctly
- Verify `marketing_warehouse.db` is in repository
- Check build logs for copy errors

**"No data returned":**
- Check database file exists: `ls -la marketing_warehouse.db`
- Verify database has data locally first
- Check API endpoint URLs

**Cold Start (503 Error):**
- Free tier spins down after 15 min
- Wait 30-60 seconds and retry
- First request after sleep is slow

### Frontend Issues

**"Failed to fetch" Errors:**
- Verify `VITE_API_BASE_URL` is correct
- Check backend is healthy
- Look for CORS errors in console

**Blank Page:**
- Check browser console for errors
- Verify build succeeded in Render logs
- Check `dist` folder was published

**Data Not Loading:**
- Verify backend API is accessible
- Check network tab in dev tools
- Ensure customer data exists in database

---

## Migration to PostgreSQL (Later)

When you want to move from SQLite to PostgreSQL:

1. **Export SQLite data:**
```bash
sqlite3 marketing_warehouse.db .dump > warehouse_dump.sql
```

2. **Create PostgreSQL on Render**

3. **Import data:**
```bash
# Convert and import (some manual tweaking needed)
psql $DATABASE_URL < warehouse_dump.sql
```

4. **Update DATABASE_URL** in backend environment

---

## You're Done! 🎉

Your platform is now live with:
- ✅ Backend API with your warehouse data
- ✅ Frontend dashboard
- ✅ All features working

**Access your platform:**
- Frontend: `https://your-frontend-url.onrender.com`
- API: `https://your-backend-url.onrender.com`
- API Docs: `https://your-backend-url.onrender.com/docs`

For ongoing updates: Just push to GitHub and Render auto-deploys!
