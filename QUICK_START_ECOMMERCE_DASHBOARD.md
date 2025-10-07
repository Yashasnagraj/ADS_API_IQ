# Quick Start: E-Commerce Dashboard 🚀

## Start in 3 Steps:

### 1. Start Backend API
```bash
cd D:\ADS_API\api
uvicorn app.main:app --reload --port 8001
```

**Wait for:** `INFO:     Uvicorn running on http://0.0.0.0:8001`

---

### 2. Start Frontend
```bash
cd D:\ADS_API\marketingiq-platform\web
npm start
```

**Wait for:** `webpack compiled successfully`

---

### 3. Open Dashboard
```
http://localhost:3001/dashboard
```

---

## What You'll See:

### **Header (6 KPI Cards):**
- 💰 Total Revenue with trend ↑/↓
- 🛒 Total Orders with trend
- 👥 Conversion Rate with trend
- 📦 Average Order Value with trend
- 🔁 Returning Customer %
- ⚠️ Refund Rate %

### **Funnel:**
Visitors → Product Views → Cart → Checkout → Purchase
(with drop-off % at each stage)

### **Charts:**
- Channel Performance (Spend + ROAS)
- Customer Segments (New vs Returning)
- 7-Day Revenue Forecast

### **Table:**
- Product Performance (sorted by revenue)

### **Alerts:**
- Anomaly Detection (mobile CVR drop, etc.)

---

## Test the API Directly:

```bash
# Get complete overview
curl http://localhost:8001/api/v1/ecommerce/overview?customer_id=6265362093

# Get just KPIs
curl http://localhost:8001/api/v1/ecommerce/kpis?customer_id=6265362093

# Get funnel data
curl http://localhost:8001/api/v1/ecommerce/funnel?customer_id=6265362093

# Get channel performance
curl http://localhost:8001/api/v1/ecommerce/channels?customer_id=6265362093
```

---

## Troubleshooting:

### **Dashboard shows no data?**
1. Check backend is running on port 8001
2. Verify customer_id has data in database
3. Check browser console for errors

### **API returns 404?**
1. Make sure you're using correct URL: `http://localhost:8001/api/v1/ecommerce/overview`
2. Check API is running: `curl http://localhost:8001/health`

### **Frontend build errors?**
1. Clear build: `rm -rf dist/`
2. Rebuild: `npm run build`
3. Check webpack output for specific errors

---

## Key Features:

✅ **All data from Google Ads API** (except mock products)
✅ **Real-time refresh** (click Refresh button)
✅ **Customer filtering** (changes when you switch customer)
✅ **AI insights** (explains trends and recommends actions)
✅ **Anomaly detection** (catches issues early)
✅ **Responsive design** (works on mobile)

---

## Next Steps:

1. **Show your boss** - http://localhost:3001/dashboard
2. **Export report** - Click "Export Report" button (PDF coming soon)
3. **Drill down** - Click on any chart/metric for details (coming soon)
4. **Customize** - Modify components in `src/components/ecommerce/`

---

## Documentation:

- **Full Implementation Guide:** `ECOMMERCE_DASHBOARD_IMPLEMENTATION.md`
- **API Docs:** http://localhost:8001/docs
- **Component Docs:** See inline comments in each `.tsx` file

---

**You're all set! Your e-commerce dashboard is ready to impress.** 🎉
