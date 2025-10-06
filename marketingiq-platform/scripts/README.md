# MarketingIQ Dashboard Verification Scripts

This directory contains scripts and patches to verify and fix dashboard data integrity issues.

## Files Overview

### Verification Script
- **`verify_dashboards.py`** - Automated verification script that checks:
  - Database vs API metric consistency
  - Metric calculation correctness (CTR, CPC, CPA, ROAS)
  - Type validation (numbers vs strings)
  - Currency formatting (INR vs USD)

### Patch Files
- **`patches/01_backend_db_connection.patch`** - Replaces mock data with database queries
- **`patches/02_remove_mock_fallback_example.patch`** - Example of removing frontend mock fallbacks

### Helper Scripts
- **`apply_quick_fixes.sh`** - Backup script and preparation for manual fixes

---

## Quick Start

### Prerequisites
```bash
# Install Python dependencies
pip install requests

# Ensure database exists
ls ../../google_ads_data.db

# Ensure backend API is running (default: http://localhost:8001)
cd ../server
python api.py
```

### Run Verification
```bash
# From marketingiq-platform directory
cd marketingiq-platform

# Run verification script
python scripts/verify_dashboards.py

# Or with custom configuration
DB_PATH=../google_ads_data.db API_BASE_URL=http://localhost:8001 python scripts/verify_dashboards.py
```

### Expected Output (Before Fixes)
```
[INFO] Starting Dashboard Verification
[INFO] API: http://localhost:8001
[INFO] DB: ../../google_ads_data.db

[INFO] Testing endpoint: /metrics/campaigns
[ERROR] ✗ /metrics/campaigns - metrics mismatch

============================================================
VERIFICATION SUMMARY
============================================================
Total Tests:     4
Passed:          0
Failed:          4
Warnings:        2
============================================================

METRIC MISMATCHES:
  Endpoint: /metrics/campaigns
    - impressions: DB=125430 API=250890
    - clicks: DB=6234 API=12450
    - cost: DB=45230.50 API=89450.23
```

### Expected Output (After Fixes)
```
[INFO] Starting Dashboard Verification
[INFO] API: http://localhost:8001
[INFO] DB: ../../google_ads_data.db

[INFO] Testing endpoint: /metrics/campaigns
[SUCCESS] ✓ /metrics/campaigns - metrics match

[INFO] Testing endpoint: /metrics/keywords
[SUCCESS] ✓ /metrics/keywords - metrics match

============================================================
VERIFICATION SUMMARY
============================================================
Total Tests:     4
Passed:          4
Failed:          0
Warnings:        0
============================================================

Report generated: reports/dashboard_verification_20251001_143052.json
```

---

## Applying Fixes

### Step 1: Backend Database Integration

**Apply patch manually** (patch files are for reference - requires code review):

```bash
# Review the patch
cat scripts/patches/01_backend_db_connection.patch

# IMPORTANT: Don't blindly apply patches!
# Read the patch and manually implement changes in server/api.py
```

**Key changes needed**:
1. Add database connection function
2. Replace all `mock_data` references with SQL queries
3. Add `customer_id` filter support
4. Convert cost from micros to rupees
5. Calculate metrics from DB aggregations

**Test after changes**:
```bash
# Start updated backend
cd server
python api.py

# Verify endpoints return real data
curl http://localhost:8001/campaigns?customer_id=123
curl http://localhost:8001/metrics/campaigns?customer_id=123
```

### Step 2: Remove Frontend Mock Fallbacks

**Files to update** (8 components):
1. `web/src/agents/optimization_agent/KeywordOptimizer.tsx`
2. `web/src/agents/optimization_agent/CampaignSimulator.tsx`
3. `web/src/agents/insight_agent/InsightsSummary.tsx`
4. `web/src/agents/insight_agent/AnomalyDetection.tsx`
5. `web/src/agents/forecasting_agent/ScenarioSimulator.tsx`
6. `web/src/agents/forecasting_agent/CTRForecast.tsx`
7. `web/src/agents/data_agent/CampaignsDashboard.tsx`
8. `web/src/agents/alert_agent/ThresholdsMonitor.tsx`

**Example patch**:
```bash
# Review example
cat scripts/patches/02_remove_mock_fallback_example.patch

# Apply similar changes to all 8 components
```

**Changes needed**:
- Remove `const mockData = { ... }` declarations
- Remove `.catch()` handlers that set mock data
- Replace `setData(mockData)` with error state
- Add proper loading/error UI

### Step 3: Standardize Currency Formatting

**Import formatter utility**:
```typescript
import { formatINR, formatNumber, formatPercentage } from '@/utils/formatters';
```

**Find & replace patterns**:
```typescript
// Before:
₹{(value).toFixed(2)}
{value.toLocaleString()}
formatter={(value: any) => `₹${Number(value).toFixed(2)}`}

// After:
{formatINR(value)}
{formatNumber(value)}
formatter={(value: any) => formatINR(value)}
```

**Files to update** (search for `toFixed` in tsx files):
```bash
cd web/src
grep -rn "toFixed" . | grep -E "\.tsx:" | cut -d: -f1 | sort -u
```

---

## Verification Report

After applying fixes, the verification script generates a JSON report:

**Location**: `reports/dashboard_verification_YYYYMMDD_HHMMSS.json`

**Report Structure**:
```json
{
  "timestamp": "2025-10-01T14:30:52",
  "endpoints_tested": [
    {
      "endpoint": "/metrics/campaigns",
      "status": "OK",
      "db_metrics": {
        "impressions": 125430,
        "clicks": 6234,
        "cost": 45230.50,
        "ctr": 4.97
      },
      "api_metrics": {
        "impressions": 125430,
        "clicks": 6234,
        "cost": 45230.50,
        "ctr": 4.97
      }
    }
  ],
  "metric_mismatches": [],
  "type_issues": [],
  "summary": {
    "total_tests": 4,
    "passed": 4,
    "failed": 0,
    "warnings": 0
  }
}
```

---

## Common Issues & Solutions

### Issue: Database connection failed
```
[ERROR] Failed to connect to database: no such table: campaigns_performance
```

**Solution**: Check database schema and table names
```bash
sqlite3 ../../google_ads_data.db
.tables
.schema campaigns_performance
```

### Issue: API not responding
```
[ERROR] API call failed [/metrics/campaigns]: Connection refused
```

**Solution**: Ensure backend is running
```bash
cd ../server
python api.py  # Should start on port 8001
```

### Issue: Metric mismatch due to rounding
```
Endpoint: /metrics/campaigns
  - ctr: DB=4.97 API=4.98
```

**Solution**: This is acceptable if difference < 0.1% (check TOLERANCE in script)

### Issue: Type errors (strings instead of numbers)
```
TYPE ISSUES:
  /metrics/campaigns - impressions: expected number, got string
```

**Solution**: Ensure API returns numeric types:
```python
# Wrong
return jsonify({'impressions': str(impressions)})

# Correct
return jsonify({'impressions': int(impressions)})
```

---

## Testing Checklist

After applying all fixes, verify:

- [ ] Verification script passes (0 failures)
- [ ] All endpoints return data from database
- [ ] No mock fallbacks in frontend components
- [ ] Currency displayed as ₹ (INR) consistently
- [ ] Metrics calculated correctly (CTR, CPC, CPA)
- [ ] API returns numeric types (not strings)
- [ ] Cost values in rupees (not micros)
- [ ] Loading states show spinner
- [ ] Error states show retry button
- [ ] No console errors in browser dev tools

---

## References

- **Main Report**: `../reports/DASHBOARD_VERIFICATION_SUMMARY.md`
- **Formatter Utility**: `../web/src/utils/formatters.ts`
- **Backend API**: `../server/api.py`

---

## Support

For issues or questions:
1. Check the main report: `reports/DASHBOARD_VERIFICATION_SUMMARY.md`
2. Review patch examples in `scripts/patches/`
3. Run verification script for detailed diagnostics

**Last Updated**: 2025-10-01
