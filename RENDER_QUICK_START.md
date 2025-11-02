# Render.com Deployment Quick Start

## Prerequisites Checklist
- [ ] Render.com account created
- [ ] Repository pushed to GitHub/GitLab/Bitbucket
- [ ] Database ready (SQLite file or PostgreSQL connection string)

## Deployment Steps

### 1. Deploy Backend (FastAPI)

**Option A: Using Blueprint (Easiest)**
1. Go to Render Dashboard → New → Blueprint
2. Connect your repository
3. Render will detect `render.yaml`
4. Review and deploy `marketingiq-api` service

**Option B: Manual Setup**
1. Go to Render Dashboard → New → Web Service
2. Connect repository
3. Configure:
   - Name: `marketingiq-api`
   - Environment: `Python 3`
   - Root Directory: `api`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --bind 0.0.0.0:$PORT --workers 2 --worker-class uvicorn.workers.UvicornWorker`
4. Set environment variables (see below)
5. Deploy

### 2. Deploy Frontend (React)

**Option A: Using Blueprint**
- If using `render.yaml`, the frontend service will be created automatically

**Option B: Manual Setup**
1. Go to Render Dashboard → New → Static Site
2. Connect repository
3. Configure:
   - Name: `marketingiq-web`
   - Root Directory: `marketingiq-platform/web`
   - Build Command: `npm install && npm run build`
   - Publish Directory: `dist`
4. Set environment variables (see below)
5. Deploy

## Environment Variables

### Backend (`marketingiq-api`)
```
DATABASE_URL=sqlite:///./marketing_warehouse.db
DEBUG=false
LOG_LEVEL=INFO
API_VERSION=v1
CORS_ORIGINS=https://marketingiq-web.onrender.com
```

### Frontend (`marketingiq-web`)
```
VITE_API_BASE_URL=https://marketingiq-api.onrender.com/api/v1
VITE_DATA_API_URL=https://marketingiq-api.onrender.com
VITE_AGENT_API_URL=https://marketingiq-api.onrender.com/api
VITE_CHATBOT_API_URL=https://your-chatbot-api.onrender.com/api
```

## Post-Deployment Verification

1. **Backend Health Check**
   ```bash
   curl https://marketingiq-api.onrender.com/health
   ```

2. **API Documentation**
   Visit: `https://marketingiq-api.onrender.com/docs`

3. **Frontend**
   Visit: `https://marketingiq-web.onrender.com`

## Important Notes

- ⚠️ Replace placeholder URLs with your actual Render URLs
- ⚠️ For production, consider PostgreSQL instead of SQLite
- ⚠️ Update CORS_ORIGINS with your frontend URL
- ⚠️ Vite env vars are baked at build time - rebuild after changes

## Troubleshooting

- **Build fails**: Check logs in Render dashboard
- **CORS errors**: Update CORS_ORIGINS env var and redeploy
- **API not accessible**: Verify backend is running and URL is correct
- **Env vars not working**: For Vite, rebuild after updating vars

See `RENDER_DEPLOYMENT_GUIDE.md` for detailed instructions.

