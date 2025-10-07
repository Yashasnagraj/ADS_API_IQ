# Netlify Deployment Guide 🚀

## Prerequisites

1. **Netlify Account**: Sign up at https://www.netlify.com
2. **GitHub Repository**: Your code should be pushed to GitHub
3. **Backend API**: Deploy your FastAPI backend somewhere (Railway, Render, Fly.io, etc.)

---

## Step 1: Push Code to GitHub

```bash
cd D:\ADS_API

# Add all files
git add .

# Commit changes
git commit -m "Add E-Commerce Performance Dashboard with Netlify deployment config"

# Push to GitHub
git push origin master
```

---

## Step 2: Deploy Backend API First

Your backend (FastAPI) needs to be deployed before the frontend.

### Option A: Railway (Recommended - Free tier available)

1. Go to https://railway.app
2. Connect your GitHub account
3. Create new project → Deploy from GitHub
4. Select your repository
5. Add environment variables:
   ```
   PORT=8000
   DATABASE_URL=sqlite:///./google_ads_data.db
   ```
6. Deploy!
7. Copy your backend URL (e.g., `https://your-app.railway.app`)

### Option B: Render

1. Go to https://render.com
2. Create new Web Service
3. Connect GitHub repo
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn api.app.main:app --host 0.0.0.0 --port $PORT`
6. Deploy and copy URL

### Option C: Fly.io

```bash
cd api
fly launch
fly deploy
```

**Save your backend URL** - you'll need it for Netlify!

---

## Step 3: Deploy Frontend to Netlify

### Method 1: Netlify UI (Easiest)

1. **Login to Netlify**: https://app.netlify.com

2. **Click "Add new site" → "Import an existing project"**

3. **Connect to GitHub**:
   - Authorize Netlify to access your GitHub
   - Select your repository: `ADS_API`

4. **Configure build settings**:
   - **Base directory**: Leave empty (netlify.toml handles this)
   - **Build command**: `cd marketingiq-platform/web && npm install && npm run build`
   - **Publish directory**: `marketingiq-platform/web/dist`
   - Click "Show advanced" → "New variable"

5. **Add environment variables**:
   ```
   Key: REACT_APP_API_URL
   Value: https://your-backend-api.railway.app/api/v1
   ```

   ```
   Key: NODE_VERSION
   Value: 18
   ```

6. **Click "Deploy site"**

7. **Wait for deployment** (2-3 minutes)

8. **Your site is live!** 🎉
   - Netlify will give you a URL like: `https://random-name-123456.netlify.app`

---

### Method 2: Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Deploy
cd D:\ADS_API
netlify deploy --prod

# Follow prompts:
# - Build command: cd marketingiq-platform/web && npm install && npm run build
# - Publish directory: marketingiq-platform/web/dist
```

---

## Step 4: Configure Custom Domain (Optional)

1. In Netlify dashboard, go to **Domain settings**
2. Click **Add custom domain**
3. Follow instructions to update DNS records

---

## Step 5: Set Environment Variables in Netlify

**IMPORTANT:** You must configure these in Netlify UI:

1. Go to **Site settings** → **Environment variables**

2. Add these variables:

   | Key | Value | Description |
   |-----|-------|-------------|
   | `REACT_APP_API_URL` | `https://your-backend.railway.app/api/v1` | Backend API endpoint |
   | `REACT_APP_DATA_API_URL` | `https://your-backend.railway.app` | Data API base URL |
   | `NODE_VERSION` | `18` | Node.js version |

3. Click **Save**

4. **Trigger redeploy**: Go to **Deploys** → **Trigger deploy** → **Deploy site**

---

## Step 6: Verify Deployment

1. **Visit your Netlify URL**: `https://your-site.netlify.app`

2. **Check landing page**: `https://your-site.netlify.app/`

3. **Check dashboard**: `https://your-site.netlify.app/dashboard`

4. **Open browser console** (F12):
   - Should NOT see CORS errors
   - Should see API calls to your backend
   - Check Network tab for API responses

---

## Troubleshooting

### Issue: "Failed to fetch" or CORS errors

**Solution:** Configure CORS in your backend

Edit `api/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "https://your-site.netlify.app",  # Add your Netlify URL
        "https://*.netlify.app"  # Allow all Netlify preview URLs
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

Redeploy backend after this change.

---

### Issue: API calls go to localhost instead of production

**Solution:** Make sure environment variables are set in Netlify

1. Netlify dashboard → **Site settings** → **Environment variables**
2. Add `REACT_APP_API_URL` with your backend URL
3. Trigger redeploy

---

### Issue: 404 on page refresh

**Already handled!** The `netlify.toml` file includes redirect rules for SPA:

```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

---

### Issue: Build fails on Netlify

**Check build logs:**

1. Go to **Deploys** tab
2. Click on failed deploy
3. Read error message

**Common fixes:**

- **Node version mismatch**: Set `NODE_VERSION=18` in environment variables
- **Missing dependencies**: Check `package.json` includes all packages
- **Build command wrong**: Should be `cd marketingiq-platform/web && npm install && npm run build`

---

## Files Created for Deployment

1. **`netlify.toml`** (root directory)
   - Build configuration
   - Redirect rules
   - Security headers

2. **Updated `src/config/api.ts`**
   - Environment-aware API URLs
   - Falls back to localhost in development
   - Uses production URLs when deployed

---

## Deployment Checklist

### Before Deploying:

- [ ] Backend API deployed and accessible
- [ ] Backend CORS configured to allow Netlify domain
- [ ] All code committed to GitHub
- [ ] `netlify.toml` in root directory
- [ ] API config supports environment variables

### During Deployment:

- [ ] Connected GitHub repository to Netlify
- [ ] Set build command and publish directory
- [ ] Added all environment variables
- [ ] Triggered initial deploy

### After Deployment:

- [ ] Visited site URL and verified it loads
- [ ] Checked browser console for errors
- [ ] Tested all dashboard pages
- [ ] Verified API calls work (Network tab)
- [ ] Tested with different customer filters

---

## Continuous Deployment

**Automatic deployments are enabled!**

Every time you push to GitHub:
1. Netlify detects the push
2. Runs the build command
3. Deploys the new version
4. Your site updates automatically! 🎉

To deploy manually:
- Netlify dashboard → **Deploys** → **Trigger deploy**

---

## Custom Build Settings

If you need to change build settings later:

1. Netlify dashboard → **Site settings** → **Build & deploy**
2. Update:
   - Build command
   - Publish directory
   - Environment variables
3. Save and trigger redeploy

---

## Preview Deployments

Netlify creates preview URLs for:
- Pull requests
- Branch deploys
- Deploy previews

Each preview gets its own URL like:
`https://deploy-preview-123--your-site.netlify.app`

---

## Production URLs

After deployment, you'll have:

- **Production site**: `https://your-site.netlify.app`
- **Landing page**: `https://your-site.netlify.app/`
- **Dashboard**: `https://your-site.netlify.app/dashboard`
- **Campaigns**: `https://your-site.netlify.app/data/campaigns`
- **Keywords**: `https://your-site.netlify.app/data/keywords`

Share the dashboard URL with your boss! 📊

---

## Backend Deployment Notes

Remember to also deploy your FastAPI backend. It won't work with just the frontend.

**Quick backend deploy options:**

1. **Railway** (easiest): https://railway.app
2. **Render**: https://render.com
3. **Fly.io**: https://fly.io
4. **Google Cloud Run**
5. **AWS Lambda** (with Mangum adapter)

Choose the one that fits your needs and budget!

---

## Next Steps

1. **Deploy backend** (if not done)
2. **Push code to GitHub**
3. **Deploy to Netlify**
4. **Set environment variables**
5. **Test the live site**
6. **Share with your boss!** 🎉

---

**Need help?** Check Netlify docs: https://docs.netlify.com
