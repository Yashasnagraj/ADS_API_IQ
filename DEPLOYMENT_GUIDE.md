# Render Deployment Guide

This guide will help you deploy the MarketingIQ platform to Render in two parts:
1. Backend API (FastAPI)
2. Frontend Web App (React/Vite)

## Prerequisites

- A Render account (https://render.com)
- Your GitHub repository connected to Render
- All environment variables ready (Google Ads credentials, etc.)

---

## Part 1: Deploy Backend API

### Step 1: Create Web Service on Render

1. Log in to your Render dashboard
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:

**Basic Settings:**
- **Name:** `marketingiq-api`
- **Region:** Choose closest to your users (e.g., Oregon, Frankfurt)
- **Branch:** `main` (or your deployment branch)
- **Root Directory:** `api`
- **Runtime:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `chmod +x start.sh && ./start.sh`

**Instance Type:**
- Free tier to start (can upgrade later)

### Step 2: Configure Environment Variables

Add these environment variables in the Render dashboard:

**Required:**
```
GOOGLE_ADS_DEVELOPER_TOKEN=your_actual_developer_token
GOOGLE_ADS_CLIENT_ID=your_actual_client_id
GOOGLE_ADS_CLIENT_SECRET=your_actual_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_actual_refresh_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=your_actual_customer_id
```

**Database:**
```
DATABASE_URL=your_database_url_or_sqlite_default
```

**API Configuration:**
```
API_VERSION=v1
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=["*"]
PAGINATION_DEFAULT_LIMIT=100
PAGINATION_MAX_LIMIT=1000
```

### Step 3: Deploy

1. Click **"Create Web Service"**
2. Render will automatically build and deploy
3. Wait for the build to complete (5-10 minutes)
4. Once deployed, you'll get a URL like: `https://marketingiq-api.onrender.com`

### Step 4: Test Backend

Test your backend API:
```bash
# Health check
curl https://marketingiq-api.onrender.com/health

# API docs
open https://marketingiq-api.onrender.com/docs
```

Expected response:
```json
{
  "status": "healthy",
  "database": "healthy",
  "version": "v1"
}
```

---

## Part 2: Deploy Frontend

### Step 1: Create Static Site on Render

1. In Render dashboard, click **"New +"** → **"Static Site"**
2. Connect the same GitHub repository
3. Configure the service:

**Basic Settings:**
- **Name:** `marketingiq-frontend`
- **Region:** Same as backend
- **Branch:** `main`
- **Root Directory:** `marketingiq-platform/web`
- **Build Command:** `npm install && npm run build`
- **Publish Directory:** `dist`

### Step 2: Configure Environment Variables

Add this environment variable:
```
VITE_API_URL=https://marketingiq-api.onrender.com
```

Replace with your actual backend URL from Step 1.

### Step 3: Configure Routing (SPA)

Render will handle this automatically with the settings in `render.yaml`, but ensure:
- All routes redirect to `/index.html` for React Router to work

### Step 4: Deploy

1. Click **"Create Static Site"**
2. Render will build and deploy
3. Wait for deployment (5-10 minutes)
4. You'll get a URL like: `https://marketingiq-frontend.onrender.com`

### Step 5: Test Frontend

1. Open the frontend URL in your browser
2. Verify it can connect to the backend
3. Test the dashboards and filters

---

## Database Setup (Important!)

### Option 1: SQLite (Development/Small Scale)
- Default in the code
- Database file stored in the container
- **Warning:** Data will be lost on container restart on free tier
- Good for testing only

### Option 2: PostgreSQL (Production Recommended)

1. In Render, create a **PostgreSQL** database:
   - Click **"New +"** → **"PostgreSQL"**
   - Name: `marketingiq-db`
   - Plan: Free (or paid for production)

2. Copy the **Internal Database URL**

3. Update backend environment variable:
   ```
   DATABASE_URL=postgresql://user:password@host/database
   ```

4. Restart the backend service

---

## Post-Deployment Configuration

### Update CORS Origins (Security)

Once frontend is deployed, update backend CORS:

In backend environment variables, change:
```
CORS_ORIGINS=["https://marketingiq-frontend.onrender.com"]
```

Replace with your actual frontend URL.

### Custom Domain (Optional)

1. In Render dashboard, go to Settings
2. Add custom domain
3. Update DNS records as instructed
4. Render provides free SSL certificates

---

## Monitoring & Logs

### View Logs
- Render Dashboard → Your Service → Logs tab
- Real-time logs for debugging

### Health Checks
- Backend: `/health` endpoint
- Render automatically monitors this

### Metrics
- Render Dashboard shows:
  - CPU usage
  - Memory usage
  - Response times
  - Error rates

---

## Troubleshooting

### Backend Issues

**Build fails:**
- Check `requirements.txt` has all dependencies
- Verify Python version (3.11.0)
- Check logs for specific errors

**Runtime crashes:**
- Check environment variables are set
- Verify database connection
- Check logs: `/api/v1/logs`

**Database errors:**
- If using PostgreSQL, verify connection string
- Check migrations ran successfully

### Frontend Issues

**Build fails:**
- Verify `package.json` dependencies
- Check Node version (18.17.0)
- Look for TypeScript errors

**API connection fails:**
- Verify `VITE_API_URL` is set correctly
- Check CORS settings on backend
- Open browser console for errors

**Routing issues:**
- Ensure SPA routing is configured
- Check `render.yaml` routes settings

---

## Scaling & Performance

### Backend Scaling
- Upgrade to paid plan for:
  - More CPU/memory
  - Multiple instances
  - Auto-scaling
  - No cold starts

### Database Scaling
- Start with free PostgreSQL
- Upgrade for:
  - More storage
  - Better performance
  - Automated backups

### Frontend CDN
- Static sites automatically use Render's global CDN
- Fast loading worldwide

---

## Costs

### Free Tier Limits:
- **Backend:** Spins down after 15 min of inactivity (cold starts)
- **Frontend:** Always available (static)
- **Database:** 1GB PostgreSQL free

### Recommended Paid Setup:
- Backend: $7/month (Starter)
- Database: $7/month (Starter)
- Frontend: Free (static)
- **Total: ~$14/month**

---

## Security Checklist

- [ ] Set `DEBUG=false` in production
- [ ] Use PostgreSQL (not SQLite) for production
- [ ] Configure proper CORS origins
- [ ] Secure environment variables in Render
- [ ] Enable HTTPS (automatic on Render)
- [ ] Set up monitoring and alerts
- [ ] Regular backups of database
- [ ] Review logs regularly

---

## Next Steps After Deployment

1. **Add customers to database:**
   - Use the warehouse initialization scripts
   - Import customer data

2. **Test all dashboards:**
   - Data dashboard
   - Insights dashboard
   - Optimization dashboard
   - Forecasting dashboard
   - Alerts dashboard

3. **Configure alerts:**
   - Set up email notifications
   - Configure thresholds

4. **Monitor performance:**
   - Check response times
   - Monitor error rates
   - Review logs

---

## Quick Commands for Manual Deployment

If you prefer to deploy manually without `render.yaml`:

### Backend:
```bash
cd api
pip install -r requirements.txt
./start.sh
```

### Frontend:
```bash
cd marketingiq-platform/web
npm install
npm run build
npm run preview -- --host 0.0.0.0 --port 10000
```

---

## Support

- **Render Docs:** https://render.com/docs
- **Project Issues:** Check logs and health endpoints
- **Database Issues:** Verify connection strings

---

## Summary

You've now deployed:
1. Backend API at: `https://marketingiq-api.onrender.com`
2. Frontend at: `https://marketingiq-frontend.onrender.com`
3. Database (optional PostgreSQL)

Your multi-customer Google Ads platform is live!
