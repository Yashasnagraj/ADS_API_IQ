# Restart Dev Server to See Changes

## The Issue
Your browser is showing **cached old code**. The changes are saved, but the browser hasn't loaded the new version.

## Quick Fix - Hard Refresh Browser

### Chrome/Edge:
```
Press: Ctrl + Shift + R
OR
Press: Ctrl + F5
```

### Firefox:
```
Press: Ctrl + Shift + R
```

### Using DevTools:
1. Press `F12` to open DevTools
2. Right-click the **Refresh button** (next to address bar)
3. Select **"Empty Cache and Hard Reload"**

---

## If Hard Refresh Doesn't Work - Restart Dev Server

### Step 1: Stop Dev Server
1. Go to the terminal running the dev server
2. Press `Ctrl + C` to stop it

### Step 2: Start Dev Server Again
```bash
cd D:\ADS_API\marketingiq-platform\web
npm start
```

### Step 3: Wait for Server to Start
You'll see:
```
webpack compiled successfully
```

### Step 4: Refresh Browser
- Open: `http://localhost:3000/dashboard`
- Hard refresh: `Ctrl + Shift + R`

---

## Verify the Fix

### Check These Values in Command Center:

1. **Total Cost** (not "Total Revenue")
   - Should show real value from API
   - Try switching customers - value should change

2. **Active Campaigns**
   - Should show real count (not 45)
   - Check against Campaigns Dashboard

3. **Conversion Rate**
   - Should show real percentage
   - May be different from 4.23%

4. **Quick Insights**
   - Should show real campaign names
   - Not "Summer Sale" (that was fake)

---

## Still Showing Old Values?

### Check React DevTools:
1. Install React DevTools extension
2. Open DevTools → Components tab
3. Find `UnifiedDashboard` component
4. Check `metricsData` prop
5. Verify it has real values from API

### Check Network Tab:
1. Open DevTools (F12)
2. Go to Network tab
3. Refresh page
4. Look for `/metrics/summary` request
5. Click it → Preview tab
6. Verify response has real data

### Check Console for Errors:
1. Open DevTools (F12)
2. Go to Console tab
3. Look for red error messages
4. Share any errors you see

---

## Files That Were Changed

These files have the new code:

✅ `web/src/components/dashboard/UnifiedDashboard.tsx`
- Line 76-77: Added useFilters and useMetricsSummary imports
- Line 108-112: Added real data fetching
- Line 114-176: Replaced mock KPIs with real data
- Line 178-223: Replaced mock insights with real data
- Line 225-258: Replaced mock chart data with real data

---

## Expected vs Actual

### Old (Mock) Values:
```
Total Revenue: ₹24,56,789
Active Campaigns: 45
Conversion Rate: 4.23%
Avg. CPC: ₹2.18
```

### New (Real) Values:
```
Total Cost: ₹[your actual spend]
Active Campaigns: [your actual count]
Conversion Rate: [your actual rate]%
Avg. CPC: ₹[your actual CPC]
```

The real values will be **different for each customer** you select.

---

## Debugging Steps

If you still see old values after hard refresh:

1. **Check customer is selected:**
   - Top of page should show customer dropdown
   - Select a customer (e.g., "Communn.io")

2. **Check API is running:**
   ```bash
   curl http://localhost:8000/customers
   ```
   Should return list of customers

3. **Check metrics API:**
   ```bash
   curl "http://localhost:8000/metrics/summary?customer_id=6265362093"
   ```
   Should return real metrics data

4. **Check browser console:**
   - F12 → Console
   - Look for API errors or failed requests

---

**If you've tried all this and still see old values, let me know what you see in the browser console!**
