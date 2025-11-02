# Quick Render Deployment Steps

Follow these steps to deploy your MarketingIQ platform to Render.

## Prerequisites Checklist

- [ ] Render account created at https://render.com
- [ ] GitHub repository connected to Render
- [ ] Google Ads API credentials ready
- [ ] Database choice decided (SQLite for testing, PostgreSQL for production)

---

## Step 1: Deploy Backend API (Do This First!)

### 1.1 Create Web Service

1. Go to Render Dashboard: https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository (authorize if needed)
4. Select your repository: `ADS_API`

### 1.2 Configure Service Settings

Fill in these settings:

```
Name: marketingiq-api
Region: Oregon (or closest to you)
Branch: main (or your branch name)
Root Directory: api
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: chmod +x start.sh && ./start.sh
Instance Type: Free
```

### 1.3 Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add these:

**Google Ads Configuration (REQUIRED):**
```
GOOGLE_ADS_DEVELOPER_TOKEN=<your-developer-token>
GOOGLE_ADS_CLIENT_ID=<your-client-id>
GOOGLE_ADS_CLIENT_SECRET=<your-client-secret>
GOOGLE_ADS_REFRESH_TOKEN=<your-refresh-token>
GOOGLE_ADS_LOGIN_CUSTOMER_ID=<your-customer-id>
```

**API Configuration:**
```
API_VERSION=v1
DEBUG=false
LOG_LEVEL=INFO
```

**Database (Optional - see Step 1.4):**
```
DATABASE_URL=sqlite:///./google_ads_data.db
```

**CORS:**
```
CORS_ORIGINS=["*"]
```

**Pagination:**
```
PAGINATION_DEFAULT_LIMIT=100
PAGINATION_MAX_LIMIT=1000
```

### 1.4 (Optional) Add PostgreSQL Database

For production, add a database:

1. In Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. Name: `marketingiq-db`
3. Plan: Free (or paid for production)
4. Click **"Create Database"**
5. Copy the **Internal Database URL**
6. In your backend service, update `DATABASE_URL` environment variable

### 1.5 Deploy Backend

1. Click **"Create Web Service"**
2. Wait 5-10 minutes for build and deployment
3. Once deployed, you'll see: ✅ **Live** with a URL
4. Copy your backend URL (e.g., `https://marketingiq-api.onrender.com`)

### 1.6 Test Backend

Open these URLs in your browser:

```
Health Check:
https://your-backend-url.onrender.com/health

API Documentation:
https://your-backend-url.onrender.com/docs
```

**Expected Health Check Response:**
```json
{
  "status": "healthy",
  "database": "healthy",
  "version": "v1"
}
```

✅ **Backend is live!** Save your backend URL for the next step.

---

## Step 2: Deploy Frontend (After Backend is Working)

### 2.1 Create Static Site

1. In Render Dashboard, click **"New +"** → **"Static Site"**
2. Select the same GitHub repository
3. Click **"Connect"**

### 2.2 Configure Service Settings

Fill in these settings:

```
Name: marketingiq-frontend
Region: Same as backend (Oregon)
Branch: main
Root Directory: marketingiq-platform/web
Build Command: npm install && npm run build
Publish Directory: dist
```

### 2.3 Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**:

```
VITE_API_BASE_URL=<YOUR-BACKEND-URL>/api/v1
```

**Important:** Replace `<YOUR-BACKEND-URL>` with your actual backend URL from Step 1.5.

Example:
```
VITE_API_BASE_URL=https://marketingiq-api.onrender.com/api/v1
```

### 2.4 Deploy Frontend

1. Click **"Create Static Site"**
2. Wait 5-10 minutes for build and deployment
3. Once deployed, you'll see: ✅ **Live** with a URL
4. Your frontend URL (e.g., `https://marketingiq-frontend.onrender.com`)

### 2.5 Test Frontend

1. Open your frontend URL in browser
2. Test the dashboard
3. Check browser console for any errors
4. Verify data loads from backend

---

## Step 3: Update Backend CORS (Security)

Now that frontend is deployed, secure your backend:

1. Go to your **backend service** in Render
2. Go to **Environment** tab
3. Update `CORS_ORIGINS`:

```
CORS_ORIGINS=["https://your-frontend-url.onrender.com"]
```

4. Click **"Save Changes"**
5. Backend will automatically redeploy

---

## Step 4: Verify Everything Works

### Test the Full Stack:

1. Open frontend URL
2. Navigate through all dashboards:
   - Data Dashboard
   - Insights Dashboard
   - Optimization Dashboard
   - Forecasting Dashboard
   - Alerts Dashboard
3. Test customer filtering
4. Test date range selection
5. Check that all API calls succeed

### Check Logs:

**Backend Logs:**
- Render Dashboard → marketingiq-api → Logs
- Look for any errors

**Frontend Logs:**
- Browser Developer Tools (F12) → Console
- Check for API connection errors

---

## Troubleshooting

### Backend Not Working?

**503 Service Unavailable:**
- Wait a few minutes (cold start on free tier)
- Check logs for build errors

**Environment Variable Missing:**
- Go to Environment tab
- Verify all required variables are set
- Redeploy if needed

**Database Connection Error:**
- If using PostgreSQL, verify DATABASE_URL is correct
- Check database is running

### Frontend Not Connecting to Backend?

**API Errors in Console:**
- Verify `VITE_API_BASE_URL` is set correctly
- Check backend CORS settings
- Ensure backend is healthy (`/health` endpoint)

**Page Not Found (404):**
- Check `Root Directory` is set to `marketingiq-platform/web`
- Verify `Publish Directory` is `dist`

**Build Fails:**
- Check logs for TypeScript errors
- Verify `package.json` is correct
- Try building locally first

---

## URLs Summary

After successful deployment, you should have:

```
Backend API:        https://marketingiq-api.onrender.com
API Docs:           https://marketingiq-api.onrender.com/docs
Health Check:       https://marketingiq-api.onrender.com/health
Frontend:           https://marketingiq-frontend.onrender.com
Database (if used): marketingiq-db.internal
```

---

## Important Notes

### Free Tier Limitations:

- **Backend:**
  - Spins down after 15 minutes of inactivity
  - Cold start takes 30-60 seconds
  - 512 MB RAM
  - Shared CPU

- **Frontend:**
  - Always available (static site)
  - 100 GB bandwidth/month

- **Database:**
  - 1 GB storage (PostgreSQL)
  - Expires after 90 days on free tier

### Upgrading (Recommended for Production):

- Backend: $7/month (Starter) - No cold starts
- Database: $7/month (Starter) - 10 GB, no expiration
- Frontend: Free (sufficient)

**Total: ~$14/month for production**

---

## Next Steps

1. **Load Data:**
   - Run your ETL scripts to populate the database
   - Add customer data

2. **Test Features:**
   - Multi-customer filtering
   - All dashboards
   - AI insights
   - Alerts

3. **Configure Custom Domain (Optional):**
   - Render Settings → Custom Domain
   - Add your domain
   - Update DNS records
   - Free SSL included

4. **Set Up Monitoring:**
   - Enable email alerts in Render
   - Monitor logs regularly
   - Check performance metrics

5. **Secure Production:**
   - Use strong passwords
   - Rotate API keys regularly
   - Review CORS settings
   - Enable 2FA on Render account

---

## Support Resources

- **Render Documentation:** https://render.com/docs
- **Render Community:** https://community.render.com
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Vite Docs:** https://vitejs.dev

---

## Quick Commands Reference

### Local Development:

```bash
# Backend
cd api
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd marketingiq-platform/web
npm install
npm run dev
```

### Manual Build Test:

```bash
# Test backend build
cd api
pip install -r requirements.txt
chmod +x start.sh
./start.sh

# Test frontend build
cd marketingiq-platform/web
npm install
npm run build
npm run preview
```

---

## Deployment Checklist

- [ ] Backend deployed and healthy
- [ ] Frontend deployed and accessible
- [ ] Environment variables set correctly
- [ ] Database connected (if using PostgreSQL)
- [ ] CORS configured properly
- [ ] All dashboards loading
- [ ] Customer filtering working
- [ ] API calls succeeding
- [ ] Logs reviewed for errors
- [ ] Performance acceptable

---

## You're Done!

Your MarketingIQ platform is now live on Render! 🎉

**Access your app:**
- Frontend: `https://your-frontend-url.onrender.com`
- API: `https://your-backend-url.onrender.com`

For ongoing maintenance and updates, just push to your GitHub repository and Render will automatically redeploy.
