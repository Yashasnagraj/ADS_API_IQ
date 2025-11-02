# Render.com Deployment Guide

This guide walks you through deploying both the FastAPI backend and React frontend to Render.com.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Deployment Overview](#deployment-overview)
3. [Step 1: Deploy FastAPI Backend](#step-1-deploy-fastapi-backend)
4. [Step 2: Deploy React Frontend](#step-2-deploy-react-frontend)
5. [Environment Variables](#environment-variables)
6. [Database Setup](#database-setup)
7. [Post-Deployment](#post-deployment)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- A Render.com account (sign up at https://render.com)
- Your repository pushed to GitHub/GitLab/Bitbucket
- Database file (`marketing_warehouse.db`) or database connection string

---

## Deployment Overview

You'll deploy two services:
1. **FastAPI Backend** (`api/` directory) - Web service
2. **React Frontend** (`marketingiq-platform/web/` directory) - Static site

---

## Step 1: Deploy FastAPI Backend

### Option A: Using render.yaml (Recommended)

1. **Ensure render.yaml is in your repository root**
   - The `render.yaml` file should be committed to your repository

2. **Create a new Web Service**
   - Go to Render Dashboard → New → Blueprint
   - Connect your repository
   - Render will detect the `render.yaml` file
   - Select the `marketingiq-api` service
   - Click "Apply"

### Option B: Manual Setup

1. **Create a new Web Service**
   - Go to Render Dashboard → New → Web Service
   - Connect your GitHub/GitLab repository

2. **Configure the service:**
   - **Name**: `marketingiq-api`
   - **Environment**: `Python 3`
   - **Region**: Choose closest to your users (e.g., `Oregon`)
   - **Branch**: `main` (or your deployment branch)
   - **Root Directory**: `api`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app.main:app --bind 0.0.0.0:$PORT --workers 2 --worker-class uvicorn.workers.UvicornWorker`

3. **Set Environment Variables** (see [Environment Variables](#environment-variables) section)

4. **Deploy**
   - Click "Create Web Service"
   - Wait for the build to complete
   - Note the service URL (e.g., `https://marketingiq-api.onrender.com`)

---

## Step 2: Deploy React Frontend

### Option A: Using render.yaml (Recommended)

1. **If using render.yaml**, Render will create both services automatically
   - After deploying the backend, the frontend service will be created
   - Update environment variables in the Render dashboard

### Option B: Manual Setup

1. **Create a new Static Site**
   - Go to Render Dashboard → New → Static Site
   - Connect your GitHub/GitLab repository

2. **Configure the service:**
   - **Name**: `marketingiq-web`
   - **Environment**: `Static`
   - **Region**: Same as backend
   - **Branch**: `main` (or your deployment branch)
   - **Root Directory**: `marketingiq-platform/web`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

3. **Set Environment Variables** (see [Environment Variables](#environment-variables) section)

4. **Deploy**
   - Click "Create Static Site"
   - Wait for the build to complete
   - Note the service URL (e.g., `https://marketingiq-web.onrender.com`)

---

## Environment Variables

### FastAPI Backend Environment Variables

Set these in the Render dashboard for the `marketingiq-api` service:

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `DATABASE_URL` | Database connection string | `sqlite:///./marketing_warehouse.db` (for SQLite) or PostgreSQL URL |
| `DEBUG` | Debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `API_VERSION` | API version | `v1` |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `https://marketingiq-web.onrender.com` |

**Important Notes:**
- For SQLite: Use absolute path or consider PostgreSQL for production
- For PostgreSQL: Create a PostgreSQL database in Render and use its connection string
- `CORS_ORIGINS` must include your frontend URL

### React Frontend Environment Variables

Set these in the Render dashboard for the `marketingiq-web` service:

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `VITE_API_BASE_URL` | Backend API base URL | `https://marketingiq-api.onrender.com/api/v1` |
| `VITE_DATA_API_URL` | Data API URL | `https://marketingiq-api.onrender.com` |
| `VITE_AGENT_API_URL` | Agent API URL | `https://marketingiq-api.onrender.com/api` |
| `VITE_CHATBOT_API_URL` | Chatbot API URL | `https://your-chatbot-api.onrender.com/api` (if applicable) |

**Important:** 
- All Vite environment variables must be prefixed with `VITE_`
- These are baked into the build at build time
- After updating env vars, trigger a new deployment

---

## Database Setup

### Option 1: SQLite (Development/Testing)

If using SQLite:
1. Upload your `marketing_warehouse.db` file to Render
2. Set `DATABASE_URL` to an absolute path: `sqlite:////opt/render/project/src/marketing_warehouse.db`
3. **Note**: SQLite on Render may have limitations; consider PostgreSQL for production

### Option 2: PostgreSQL (Recommended for Production)

1. **Create a PostgreSQL Database**
   - Go to Render Dashboard → New → PostgreSQL
   - Choose a name (e.g., `marketingiq-db`)
   - Note the connection string

2. **Initialize the Database**
   - Set `DATABASE_URL` in your API service to the PostgreSQL connection string
   - The app will create tables on startup (via `Base.metadata.create_all()`)
   - Or run migrations manually if you have them

3. **Update Connection String Format**
   - Render provides: `postgresql://user:pass@host/dbname`
   - Your app should work with this format

---

## Post-Deployment

### 1. Verify Backend Health

Check the health endpoint:
```bash
curl https://marketingiq-api.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "healthy",
  "version": "v1"
}
```

### 2. Test API Documentation

Visit: `https://marketingiq-api.onrender.com/docs`

### 3. Verify Frontend

Visit your frontend URL and check:
- API calls are working
- No CORS errors in browser console
- Data loads correctly

### 4. Update CORS Settings

If you see CORS errors:
1. Go to your API service settings
2. Update `CORS_ORIGINS` to include your frontend URL:
   ```
   https://marketingiq-web.onrender.com
   ```
3. Redeploy the API service

---

## Troubleshooting

### Backend Issues

**Problem**: Build fails
- **Solution**: Check build logs, ensure all dependencies are in `requirements.txt`
- Verify Python version compatibility

**Problem**: Service crashes on startup
- **Solution**: Check logs in Render dashboard
- Verify `DATABASE_URL` is set correctly
- Check that all environment variables are set

**Problem**: Database connection errors
- **Solution**: 
  - For SQLite: Verify file path is correct and accessible
  - For PostgreSQL: Verify connection string format
  - Check database is running and accessible

**Problem**: CORS errors
- **Solution**: 
  - Ensure `CORS_ORIGINS` includes your frontend URL
  - Check middleware configuration in `main.py`
  - Redeploy after updating env vars

### Frontend Issues

**Problem**: Build fails
- **Solution**: Check build logs
- Verify Node.js version (Render usually auto-detects)
- Ensure all dependencies are in `package.json`

**Problem**: API calls fail
- **Solution**: 
  - Verify `VITE_API_BASE_URL` is set correctly
  - Check browser console for errors
  - Ensure backend is running and accessible
  - Verify CORS is configured correctly

**Problem**: Environment variables not working
- **Solution**: 
  - Remember: Vite env vars must be prefixed with `VITE_`
  - Rebuild after updating env vars
  - Check build logs to verify vars are included

### General Issues

**Problem**: Services not connecting
- **Solution**: 
  - Verify URLs are correct
  - Check service status in Render dashboard
  - Review logs for both services

**Problem**: Slow performance
- **Solution**: 
  - Consider upgrading to a paid plan
  - Optimize database queries
  - Enable caching where possible

---

## Additional Configuration

### Custom Domain

1. In Render dashboard, go to your service settings
2. Click "Custom Domains"
3. Add your domain
4. Update DNS records as instructed

### Auto-Deploy

Render automatically deploys on push to your main branch. To change this:
1. Go to service settings
2. Update "Auto-Deploy" settings

### Environment-Specific Deployments

Consider creating separate services for:
- `marketingiq-api-staging` (for testing)
- `marketingiq-api-prod` (for production)

Use different branches or manual deployments for each.

---

## Quick Reference

### Backend URLs
- API: `https://marketingiq-api.onrender.com`
- Docs: `https://marketingiq-api.onrender.com/docs`
- Health: `https://marketingiq-api.onrender.com/health`

### Frontend URL
- Web: `https://marketingiq-web.onrender.com`

### Important Files
- Backend config: `api/app/core/config.py`
- Frontend config: `marketingiq-platform/web/src/config/api.ts`
- Deployment config: `render.yaml`

---

## Support

For Render-specific issues, check:
- Render Documentation: https://render.com/docs
- Render Community: https://community.render.com

For application-specific issues, check your application logs in the Render dashboard.

