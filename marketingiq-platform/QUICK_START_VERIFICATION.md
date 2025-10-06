# ⚡ Quick Start: Dashboard Verification

**Goal**: Verify all MarketingIQ dashboards use real database data (not mocks) and display INR currency correctly.

---

## 🚀 Run Verification NOW (2 commands)

```bash
# 1. Navigate to project
cd C:\Users\yashr\Desktop\ADS_API\marketingiq-platform

# 2. Run verification
python scripts/verify_dashboards.py
```

**Expected Output**: See if dashboards pass or fail data integrity checks.

---

## 📊 What Was Found

### ✅ GOOD NEWS
1. **Metric formulas are correct** - CTR, CPC, CPA calculations follow Google Ads conventions
2. **No USD ($) found** - No hardcoded dollar signs in code
3. **INR (₹) formatting exists** - Many components already use rupee symbol

### ⚠️ CRITICAL ISSUES
1. **Backend is 100% mock data** - `server/api.py` returns random data, not from database
2. **Frontend has mock fallbacks** - 8 components fall back to fake data when API fails
3. **Inconsistent currency formatting** - Some use formatters, others use inline `toFixed(2)`

---

## 📂 Files Created

| File | Purpose |
|------|---------|
| `scripts/verify_dashboards.py` | Automated verification script |
| `web/src/utils/formatters.ts` | INR currency & metric formatters |
| `reports/DASHBOARD_VERIFICATION_SUMMARY.md` | **← READ THIS FIRST** - Full report |
| `scripts/README.md` | Detailed usage instructions |
| `scripts/patches/*.patch` | Example code fixes |

---

## 🎯 Top 5 Fixes (Priority Order)

### Fix #1: Replace Backend Mock API ⭐ CRITICAL
**File**: `server/api.py`
**Problem**: All 25+ endpoints return random mock data
**Solution**: Connect to `google_ads_data.db` and query real data

**See**: `reports/DASHBOARD_VERIFICATION_SUMMARY.md` → Fix #1
**Patch**: `scripts/patches/01_backend_db_connection.patch`

---

### Fix #2: Remove Frontend Mock Fallbacks ⭐ HIGH
**Files**: 8 components in `web/src/agents/`
**Problem**: Components show fake data when API fails
**Solution**: Remove `mockData` constants and fallbacks

**See**: `reports/DASHBOARD_VERIFICATION_SUMMARY.md` → Fix #2
**Patch**: `scripts/patches/02_remove_mock_fallback_example.patch`

---

### Fix #3: Use formatINR() Everywhere ⭐ MEDIUM
**Files**: 26 locations across dashboards
**Problem**: Inconsistent currency formatting (some ₹, some not)
**Solution**: Import and use `formatINR()` from `utils/formatters.ts`

**Example**:
```typescript
import { formatINR, formatNumber, formatPercentage } from '@/utils/formatters';

// Before: ₹{value.toFixed(2)}
// After:  {formatINR(value)}
```

**See**: `reports/DASHBOARD_VERIFICATION_SUMMARY.md` → Fix #3

---

### Fix #4: Verify API Returns Numbers ⭐ MEDIUM
**File**: `server/api.py`
**Problem**: Could accidentally return strings instead of numbers
**Solution**: Ensure `jsonify()` gets `int()` and `float()` types

**Example**:
```python
# ✅ Correct
return jsonify({
    'impressions': int(row['impressions']),
    'cost': float(row['cost_micros']) / 1_000_000
})

# ❌ Wrong
return jsonify({
    'impressions': str(row['impressions']),  # Don't stringify!
    'cost': f"{row['cost']:.2f}"  # Don't use f-strings for numbers!
})
```

**See**: `reports/DASHBOARD_VERIFICATION_SUMMARY.md` → Fix #4

---

### Fix #5: Convert Cost Micros to Rupees ⭐ MEDIUM
**Files**: ETL pipeline OR `server/api.py`
**Problem**: Google Ads stores cost as micros (1 ₹ = 1,000,000 micros)
**Solution**: Convert once in ETL or API layer

**Example**:
```python
# In API or ETL
cost_rupees = row['cost_micros'] / 1_000_000
```

**See**: `reports/DASHBOARD_VERIFICATION_SUMMARY.md` → Fix #5

---

## 📖 Read These (In Order)

1. **THIS FILE** ← You are here
2. **`reports/DASHBOARD_VERIFICATION_SUMMARY.md`** ← Full analysis & fixes
3. **`scripts/README.md`** ← How to run verification & apply fixes

---

## ⚙️ How to Apply Fixes

### Option A: Automated Verification (Already Done ✅)
```bash
python scripts/verify_dashboards.py
```
Generates report showing what's broken.

### Option B: Manual Fixes (Do This Next)

1. **Read full report**:
   ```bash
   cat reports/DASHBOARD_VERIFICATION_SUMMARY.md
   ```

2. **Review patches**:
   ```bash
   cat scripts/patches/01_backend_db_connection.patch
   cat scripts/patches/02_remove_mock_fallback_example.patch
   ```

3. **Apply fixes manually** (don't use `git apply` - patches are examples)
   - Edit `server/api.py` per Fix #1
   - Edit 8 frontend components per Fix #2
   - Update currency formatting per Fix #3

4. **Re-run verification**:
   ```bash
   python scripts/verify_dashboards.py
   ```

5. **Iterate until** all tests pass (0 failures)

---

## 🧪 Testing Checklist

After fixes, verify:

- [ ] Run `python scripts/verify_dashboards.py` → 0 failures
- [ ] Start backend: `cd server && python api.py`
- [ ] Check API returns real data: `curl http://localhost:8001/campaigns`
- [ ] Start frontend: `cd web && npm start`
- [ ] Open browser dev tools (F12) → No console errors
- [ ] Check dashboards show real data (not random/mock)
- [ ] Verify currency shows ₹ symbol
- [ ] Check CTR/CPC/CPA calculations are correct

---

## 🆘 Common Issues

### "Database not found"
```bash
# Check if DB exists
ls C:\Users\yashr\Desktop\ADS_API\google_ads_data.db

# Update path in verification script if needed
DB_PATH=../google_ads_data.db python scripts/verify_dashboards.py
```

### "API not responding"
```bash
# Start backend first
cd server
python api.py  # Should say "Running on http://0.0.0.0:8001"
```

### "Metric mismatch"
Small differences (< 0.1%) are OK due to rounding. Large differences mean mock data is still being used.

---

## 📞 Next Steps

1. **Read**: `reports/DASHBOARD_VERIFICATION_SUMMARY.md` (detailed report)
2. **Implement**: Fix #1 (backend DB connection) - CRITICAL
3. **Implement**: Fix #2 (remove mock fallbacks) - HIGH
4. **Test**: Re-run verification script
5. **Deploy**: Once all tests pass

---

**Generated**: 2025-10-01
**Verification Script**: `scripts/verify_dashboards.py`
**Main Report**: `reports/DASHBOARD_VERIFICATION_SUMMARY.md`
