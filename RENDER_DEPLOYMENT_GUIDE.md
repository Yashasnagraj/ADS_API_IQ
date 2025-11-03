# Render.com Deployment Guide

This guide will help you deploy both the FastAPI backend and React frontend to Render.com.

## Overview

- **Backend**: FastAPI application in `api/` directory
- **Frontend**: React application in `marketingiq-platform/web/` directory
- **Database**: SQLite database (`marketing_warehouse.db`) in root directory

## Prerequisites

1. GitHub repository with your code
2. Render.com account (free tier available)
3. Environment variables from `.env` and `.env.meta` files

---

## Step 1: Prepare Your Repository

Make sure your repository includes:
- ✅ `api/` directory with FastAPI code
- ✅ `marketingiq-platform/web/` directory with React code
- ✅ `marketing_warehouse.db` (if you want to use existing data)
- ✅ `render.yaml` (already created)
- ✅ `api/requirements.txt`
- ✅ `marketingiq-platform/web/package.json`

---

## Step 2: Deploy Backend Service

### Option A: Using render.yaml (Backend Only)

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml` and create the backend service
5. **Note:** Frontend must be deployed separately (see Step 3)

### Option B: Manual Setup

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:

```
Name: marketingiq-api
Region: Oregon (or closest to you)
Branch: main (or your deployment branch)
Root Directory: api
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: chmod +x start.sh && ./start.sh
```

### Environment Variables for Backend

Add these in Render Dashboard → Environment tab:

**Required:**
```bash
DATABASE_URL=sqlite:///./marketing_warehouse.db
API_VERSION=v1
DEBUG=false
LOG_LEVEL=INFO
PAGINATION_DEFAULT_LIMIT=100
PAGINATION_MAX_LIMIT=1000
```

**CORS (set after frontend is deployed):**
```bash
CORS_ORIGINS=https://your-frontend-name.onrender.com
```
Replace `your-frontend-name` with your actual frontend service name.

**Google Ads API Credentials (from your .env file):**
```bash
GOOGLE_ADS_DEVELOPER_TOKEN=your_token_here
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=your_customer_id
```

**Meta Ads API Credentials (from your .env.meta file):**
```bash
META_ACCESS_TOKEN=your_access_token
META_AD_ACCOUNT_ID=act_your_account_id
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
```

### Deploy Backend

Click **"Create Web Service"** and wait 5-10 minutes.

Your backend will be live at: `https://marketingiq-api.onrender.com`

**Note:** Make sure to copy `marketing_warehouse.db` to the `api/` directory or it will be created automatically.

---

## Step 3: Deploy Frontend Service

### Deploy Frontend Manually

**Note:** Render's `render.yaml` blueprint doesn't support static sites, so the frontend must be deployed separately.

### Manual Setup

1. In Render Dashboard, click **"New +"** → **"Static Site"**
2. Connect your GitHub repository
3. Configure the service:

```
Name: marketingiq-frontend
Region: Same as backend (Oregon)
Branch: main (or your deployment branch)
Root Directory: marketingiq-platform/web
Build Command: npm install && npm run build
Publish Directory: dist
```

### Environment Variables for Frontend

Add these in Render Dashboard → Environment tab:

**Required (set after backend is deployed):**
```bash
VITE_API_BASE_URL=https://marketingiq-api.onrender.com/api/v1
VITE_DATA_API_URL=https://marketingiq-api.onrender.com
VITE_AGENT_API_URL=https://marketingiq-api.onrender.com/api
```

**Optional (if chatbot service is deployed):**
```bash
VITE_CHATBOT_API_URL=https://your-chatbot-service.onrender.com/api
```

**Important:** Replace `marketingiq-api` with your actual backend service name!

### Deploy Frontend

Click **"Create Static Site"** and wait 5-10 minutes.

Your frontend will be live at: `https://marketingiq-frontend.onrender.com`

---

## Step 4: Update CORS Configuration

After both services are deployed:

1. Go to your backend service in Render Dashboard
2. Navigate to **Environment** tab
3. Update `CORS_ORIGINS`:
   ```bash
   CORS_ORIGINS=https://marketingiq-frontend.onrender.com
   ```
4. Save (this will trigger an automatic redeploy)

---

## Step 5: Verify Deployment

### Test Backend

```bash
# Health check
curl https://marketingiq-api.onrender.com/health

# API documentation
open https://marketingiq-api.onrender.com/docs

# Get customers
curl https://marketingiq-api.onrender.com/api/v1/customers
```

Expected response for `/health`:
```json
{
  "status": "healthy",
  "database": "healthy",
  "version": "v1"
}
```

### Test Frontend

1. Open your frontend URL in a browser
2. Open Developer Tools (F12) → Console
3. Check for any errors
4. Navigate through the dashboards
5. Verify data loads from backend

---

## Important Notes

### Free Tier Limitations

- **Cold Starts**: Free tier services spin down after 15 minutes of inactivity. First request after sleep takes 30-60 seconds.
- **Database Storage**: SQLite files on free tier are ephemeral - they reset on container restart. Consider:
  - Upgrading to paid plan ($7/month) for persistent disk
  - Using PostgreSQL (free tier available)
  - Committing database to Git (not recommended for production)

### Production Recommendations

1. **Use PostgreSQL** instead of SQLite for production
2. **Upgrade to paid plan** for better performance and persistence
3. **Set up monitoring** and alerts
4. **Configure custom domains** for better branding
5. **Enable auto-deploy** from specific branches

---

## Troubleshooting

### Backend Issues

**"Database not found" Error:**
- Ensure `marketing_warehouse.db` is in repository root or `api/` directory
- Check `DATABASE_URL` environment variable
- Verify database file permissions

**"Module not found" Error:**
- Check `requirements.txt` includes all dependencies
- Verify build logs for missing packages

**"502 Bad Gateway" or "503 Service Unavailable":**
- Service might be spinning up (wait 30-60 seconds)
- Check build logs for errors
- Verify start command is correct

**CORS Errors:**
- Ensure `CORS_ORIGINS` includes your frontend URL
- Check that URLs match exactly (including https://)
- Verify backend is responding to OPTIONS requests

### Frontend Issues

**"Failed to fetch" Errors:**
- Verify `VITE_API_BASE_URL` is set correctly
- Check backend is healthy and accessible
- Look for CORS errors in browser console

**Blank Page:**
- Check browser console for errors
- Verify build succeeded in Render logs
- Ensure `dist` folder is published correctly

**API Calls Failing:**
- Check network tab in browser dev tools
- Verify backend URL is correct
- Ensure environment variables are set (they're only available at build time)

---

## Environment Variables Summary

### Backend (`marketingiq-api`)

```bash
# Database
DATABASE_URL=sqlite:///./marketing_warehouse.db

# API Configuration
API_VERSION=v1
DEBUG=false
LOG_LEVEL=INFO

# Pagination
PAGINATION_DEFAULT_LIMIT=100
PAGINATION_MAX_LIMIT=1000

# CORS (set after frontend deployment)
CORS_ORIGINS=https://marketingiq-frontend.onrender.com

# Google Ads API (from .env)
GOOGLE_ADS_DEVELOPER_TOKEN=...
GOOGLE_ADS_CLIENT_ID=...
GOOGLE_ADS_CLIENT_SECRET=...
GOOGLE_ADS_REFRESH_TOKEN=...
GOOGLE_ADS_LOGIN_CUSTOMER_ID=...

# Meta Ads API (from .env.meta)
META_ACCESS_TOKEN=...
META_AD_ACCOUNT_ID=...
META_APP_ID=...
META_APP_SECRET=...
```

### Frontend (`marketingiq-frontend`)

```bash
# Backend API URLs (set after backend deployment)
VITE_API_BASE_URL=https://marketingiq-api.onrender.com/api/v1
VITE_DATA_API_URL=https://marketingiq-api.onrender.com
VITE_AGENT_API_URL=https://marketingiq-api.onrender.com/api

# Optional: Chatbot API
VITE_CHATBOT_API_URL=https://your-chatbot-service.onrender.com/api
```

**Important:** Vite environment variables must start with `VITE_` to be available in the frontend build.

---

## Deployment Checklist

- [ ] Repository is connected to Render
- [ ] Backend service created and configured
- [ ] Backend environment variables set
- [ ] Backend deployed successfully
- [ ] Backend health check passes (`/health`)
- [ ] Frontend service created and configured
- [ ] Frontend environment variables set (with correct backend URL)
- [ ] Frontend deployed successfully
- [ ] CORS updated with frontend URL
- [ ] Frontend loads without errors
- [ ] API calls work from frontend
- [ ] No CORS errors in browser console

---

## Next Steps After Deployment

1. **Set up custom domains** (optional)
2. **Configure auto-deploy** from main branch
3. **Set up monitoring** and alerts
4. **Migrate to PostgreSQL** (recommended for production)
5. **Set up CI/CD** pipeline

---

## Support

If you encounter issues:
1. Check Render logs (Dashboard → Your Service → Logs)
2. Check build logs for errors
3. Verify all environment variables are set correctly
4. Test backend API endpoints directly
5. Check browser console for frontend errors

---

## Quick Reference

**Backend URL:** `https://marketingiq-api.onrender.com`  
**Frontend URL:** `https://marketingiq-frontend.onrender.com`  
**API Docs:** `https://marketingiq-api.onrender.com/docs`

**Note:** Replace `marketingiq-api` and `marketingiq-frontend` with your actual service names!

