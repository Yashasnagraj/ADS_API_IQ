# Netlify Setup - Ready to Deploy! ✅

## ✅ Build Settings Confirmed

Your Netlify build settings are **correctly configured**:

```
Base directory:     /
Build command:      cd marketingiq-platform/web && npm install && npm run build
Publish directory:  marketingiq-platform/web/dist
Build status:       Active ✅
```

**This matches the netlify.toml configuration - you're ready to deploy!**

---

## ⚠️ CRITICAL: Add Environment Variables

**Before deploying**, you MUST add environment variables in Netlify:

### **Step 1: Go to Environment Variables**

1. In Netlify dashboard, click on your site
2. Go to: **Site settings** → **Environment variables**
3. Click: **Add a variable** → **Add a single variable**

---

### **Step 2: Add These Variables**

#### **Variable 1: REACT_APP_API_URL** (REQUIRED)

```
Key:   REACT_APP_API_URL
Value: https://your-backend-api-url.com/api/v1
```

**⚠️ IMPORTANT:**
- Replace `https://your-backend-api-url.com` with your **actual backend URL**
- If using Railway: `https://your-app.railway.app/api/v1`
- If using Render: `https://your-app.onrender.com/api/v1`
- Make sure to include `/api/v1` at the end!

**How to get backend URL:**
- **If using Railway**: Go to https://railway.app → Your project → Copy the URL
- **If using Render**: Go to https://render.com → Your web service → Copy the URL
- **If backend not deployed yet**: Deploy it first (see below)

---

#### **Variable 2: NODE_VERSION** (REQUIRED)

```
Key:   NODE_VERSION
Value: 18
```

This ensures Netlify uses Node.js 18 for building your app.

---

#### **Variable 3: REACT_APP_DATA_API_URL** (Optional)

```
Key:   REACT_APP_DATA_API_URL
Value: https://your-backend-api-url.com
```

Same as Variable 1, but **without** `/api/v1` at the end.

---

### **Step 3: Save Variables**

After adding all variables:
1. Click **Save**
2. Netlify will prompt you to redeploy
3. Click **Trigger deploy** → **Deploy site**

---

## 🚨 Deploy Backend First!

**Your frontend won't work without the backend API!**

### **Option A: Railway (Recommended - Free Tier)**

1. **Go to Railway**: https://railway.app

2. **Sign in with GitHub**

3. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose: `Yashasnagraj/ADS_API_IQ`
   - Click "Deploy Now"

4. **Configure Settings**:
   - Click on your service
   - Go to **Settings** tab
   - **Root Directory**: `api`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. **Add Environment Variables**:
   - Go to **Variables** tab
   - Add:
     ```
     PORT = 8000
     DATABASE_URL = sqlite:///./google_ads_data.db
     ```

6. **Deploy**:
   - Railway will automatically deploy
   - Wait 2-3 minutes
   - **Copy your backend URL** (e.g., `https://ads-api-production.up.railway.app`)

7. **Test Backend**:
   - Visit: `https://your-app.railway.app/health`
   - Should return: `{"status": "healthy", "database": "healthy"}`

---

### **Option B: Render (Alternative)**

1. **Go to Render**: https://render.com

2. **New Web Service**:
   - Connect your GitHub: `Yashasnagraj/ADS_API_IQ`
   - Name: `ads-api`

3. **Settings**:
   - **Root Directory**: `api`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Environment Variables**:
   ```
   DATABASE_URL = sqlite:///./google_ads_data.db
   ```

5. **Create Web Service**
   - Wait for deployment (~5 minutes)
   - Copy URL: `https://ads-api.onrender.com`

---

## 🔧 Update Backend CORS

**After deploying backend**, update CORS to allow Netlify:

### **Edit `api/app/main.py`**:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",              # Local development
        "https://your-site.netlify.app",      # Your Netlify URL (add after deploy)
        "https://*.netlify.app",              # All Netlify preview URLs
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

**Then:**
1. Commit the change
2. Push to GitHub: `git push`
3. Railway/Render will auto-deploy the update

---

## 📋 Complete Deployment Checklist

### **Backend (Do First):**

- [ ] Deploy backend to Railway/Render
- [ ] Test health endpoint: `https://your-backend.com/health`
- [ ] Copy backend URL
- [ ] Update CORS in backend code
- [ ] Redeploy backend

### **Frontend (Do Second):**

- [ ] Add `REACT_APP_API_URL` in Netlify
- [ ] Add `NODE_VERSION` in Netlify
- [ ] Trigger deploy in Netlify
- [ ] Wait for build to complete (2-3 minutes)
- [ ] Visit your Netlify URL
- [ ] Test dashboard: `/dashboard`

### **Verification:**

- [ ] Landing page loads
- [ ] Dashboard shows data (not errors)
- [ ] Browser console (F12) - no CORS errors
- [ ] Network tab shows successful API calls
- [ ] Customer filter works
- [ ] All charts render correctly

---

## 🎯 After Deployment

### **Your URLs:**

**Frontend (Netlify):**
```
https://your-site.netlify.app
```

**Backend (Railway/Render):**
```
https://your-backend.railway.app
```

### **Dashboard Pages:**

- Landing: `https://your-site.netlify.app/`
- E-Commerce Dashboard: `https://your-site.netlify.app/dashboard`
- Campaigns: `https://your-site.netlify.app/data/campaigns`
- Keywords: `https://your-site.netlify.app/data/keywords`

---

## 🐛 Troubleshooting

### **Issue: Build fails with "Node version not supported"**

**Solution:**
- Make sure `NODE_VERSION = 18` is set in Netlify environment variables
- Trigger redeploy

---

### **Issue: "Failed to fetch" or CORS errors**

**Solution:**
1. Check backend CORS allows your Netlify URL
2. Make sure backend is deployed and healthy
3. Verify `REACT_APP_API_URL` points to correct backend

**Test backend:**
```bash
curl https://your-backend.railway.app/health
```

---

### **Issue: Dashboard shows no data**

**Solution:**
1. Open browser console (F12)
2. Check Network tab for API calls
3. Verify API calls are going to production URL (not localhost)
4. Check if backend returns data:
   ```bash
   curl https://your-backend.railway.app/api/v1/ecommerce/kpis?customer_id=6265362093
   ```

---

### **Issue: 404 on page refresh**

**Already fixed!** `netlify.toml` includes SPA redirect rules:
```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

---

## ✅ Quick Deploy Summary

1. **Deploy backend** (Railway: 5 min)
2. **Copy backend URL**
3. **Add to Netlify env vars** (1 min)
4. **Trigger Netlify deploy** (3 min)
5. **Test your site** (1 min)

**Total time: ~10 minutes** ⏱️

---

## 🎉 Success Criteria

You'll know it's working when:

✅ Netlify build completes successfully
✅ Site loads without errors
✅ Dashboard shows real data (not mock data)
✅ No CORS errors in console
✅ API calls succeed in Network tab
✅ Charts render with data
✅ Customer filter changes data

---

## 📞 Need Help?

**Documentation:**
- `NETLIFY_DEPLOYMENT_GUIDE.md` - Full deployment guide
- `DEPLOYMENT_SUMMARY.md` - Quick summary
- Netlify Docs: https://docs.netlify.com
- Railway Docs: https://docs.railway.app

**Check:**
- Browser console (F12) for errors
- Network tab for failed API calls
- Netlify deploy logs for build errors

---

## 🚀 Ready to Deploy!

**Your current status:**
- ✅ Code pushed to GitHub
- ✅ Netlify build settings configured
- ✅ netlify.toml ready
- ⏳ **Next: Add environment variables**
- ⏳ **Then: Deploy!**

**Let's go! 🎉**

---

## 📝 Environment Variables Summary

**Copy-paste these into Netlify:**

```
REACT_APP_API_URL = https://your-backend-url.railway.app/api/v1
NODE_VERSION = 18
```

**Replace `https://your-backend-url.railway.app` with your actual backend URL!**

---

**Everything is ready. Deploy your backend, add the env vars, and you're live! 🚀**
