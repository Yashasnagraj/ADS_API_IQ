# Deploy MarketingIQ Backend API to Render

This guide walks you through deploying the FastAPI backend to Render's free tier.

---

## 🚀 Quick Deploy Steps

### 1. Push Code to GitHub

```bash
cd D:\ADS_API
git add .
git commit -m "Add Render deployment configuration"
git push origin master
```

### 2. Create Render Account

1. Go to https://render.com
2. Sign up with your **GitHub account** (easiest option)
3. Authorize Render to access your repositories

### 3. Create New Web Service

1. **Click "New +"** → **"Web Service"**
2. **Connect your repository:** `Yashasnagraj/ADS_API_IQ`
3. **Configure the service:**

   - **Name:** `marketingiq-api` (or any name you prefer)
   - **Region:** Oregon (Free) or any region
   - **Branch:** `master`
   - **Root Directory:** `api`
   - **Runtime:** Python 3
   - **Build Command:**
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command:**
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```

4. **Environment Variables** (click "Advanced"):
   - `PYTHON_VERSION` = `3.11`
   - `DEBUG` = `false`
   - `LOG_LEVEL` = `INFO`

5. **Plan:** Select **Free** ($0/month)

6. **Click "Create Web Service"**

### 4. Wait for Deployment

- Render will build and deploy your API (takes 2-5 minutes)
- Watch the logs in real-time
- Once deployed, you'll see **"Your service is live"** ✅

### 5. Get Your API URL

Your API will be available at:
```
https://marketingiq-api.onrender.com
```

Or whatever name you chose:
```
https://YOUR-SERVICE-NAME.onrender.com
```

### 6. Test Your API

Open in browser:
```
https://marketingiq-api.onrender.com/health
```

Should return:
```json
{
  "status": "healthy",
  "database": "healthy",
  "version": "v1"
}
```

API Docs:
```
https://marketingiq-api.onrender.com/docs
```

---

## 🔧 Update Netlify Environment Variables

Once your backend is deployed:

1. **Go to Netlify Dashboard** → Your site → **Site settings** → **Environment variables**

2. **Add/Update:**
   - **Key:** `REACT_APP_API_URL`
   - **Value:** `https://marketingiq-api.onrender.com/api/v1`

3. **Redeploy frontend:**
   - Go to **Deploys** tab
   - Click **Trigger deploy** → **Clear cache and deploy site**

---

## ⚠️ Important Notes

### Free Tier Limitations

- **Spins down after 15 minutes of inactivity**
- First request after spin-down takes ~30 seconds to wake up
- 750 hours/month free (enough for one service 24/7)

### Database Persistence

- SQLite database is stored on disk
- **Data persists** across deployments
- Located at: `api/google_ads_data.db`

### CORS Configuration

Already configured in `app/main.py` to allow all origins:
```python
allow_origins=["*"]
```

This works for development. For production, update to:
```python
allow_origins=[
    "https://marketingkk.netlify.app",
    "https://your-custom-domain.com"
]
```

---

## 🐛 Troubleshooting

### Build Fails

**Check logs in Render dashboard for errors**

Common issues:
- Missing dependencies → Update `requirements.txt`
- Python version → Ensure `PYTHON_VERSION=3.11` in env vars
- Import errors → Check all Python imports are correct

### Service Won't Start

**Check start command logs**

Make sure start command is:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Database Errors

If you see database connection errors, it means the SQLite file isn't being created.

**Solution:** Ensure the lifespan event in `app/main.py` creates tables:
```python
Base.metadata.create_all(bind=engine)
```

### API Returns 404

**Check the URL structure:**
- ✅ Correct: `https://marketingiq-api.onrender.com/api/v1/campaigns`
- ❌ Wrong: `https://marketingiq-api.onrender.com/campaigns`

All endpoints are prefixed with `/api/v1/`

---

## 📊 Monitoring

### View Logs

1. Go to Render Dashboard → Your service
2. Click **Logs** tab
3. See real-time logs

### Check Health

```bash
curl https://marketingiq-api.onrender.com/health
```

### API Metrics

Render provides:
- Request count
- Response time
- Error rate
- Memory usage

Available in the **Metrics** tab

---

## 🔄 Continuous Deployment

Render auto-deploys when you push to GitHub:

```bash
git add .
git commit -m "Update API"
git push origin master
```

Render will automatically:
1. Detect the push
2. Build the new version
3. Deploy (zero-downtime)

---

## 🆙 Upgrade Options

If you need better performance:

### Paid Plans

- **Starter ($7/month):**
  - Always-on (no spin-down)
  - 512MB RAM
  - Better CPU

- **Standard ($25/month):**
  - 2GB RAM
  - More CPU
  - Custom domains

### Database Upgrade

For production, consider PostgreSQL:

1. Create **Render PostgreSQL** database (free tier available)
2. Update `DATABASE_URL` env var
3. Install `psycopg2-binary` in requirements.txt
4. Update SQLAlchemy connection string

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Web service created on Render
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Environment variables set
- [ ] Service deployed successfully
- [ ] Health endpoint returns 200 OK
- [ ] API docs accessible at `/docs`
- [ ] Netlify env var `REACT_APP_API_URL` updated
- [ ] Frontend redeployed on Netlify
- [ ] Test full flow: Frontend → Backend → Database

---

## 🎯 Final URLs

After deployment, you should have:

**Backend API:**
- Base: `https://marketingiq-api.onrender.com`
- Health: `https://marketingiq-api.onrender.com/health`
- Docs: `https://marketingiq-api.onrender.com/docs`
- API: `https://marketingiq-api.onrender.com/api/v1/`

**Frontend:**
- Main: `https://marketingkk.netlify.app`
- Dashboard: `https://marketingkk.netlify.app/dashboard`

---

## 🆘 Need Help?

- **Render Docs:** https://render.com/docs
- **Render Community:** https://community.render.com
- **FastAPI Docs:** https://fastapi.tiangolo.com

---

**Your backend is ready to deploy! Follow the steps above to get it live on Render.**
