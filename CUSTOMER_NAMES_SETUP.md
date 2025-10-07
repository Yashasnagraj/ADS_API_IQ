# Customer Names Setup Guide

## ✅ What Was Done

Added customer names to the system so you can show **"Communn.io"** instead of **"6265362093"** on your web pages.

---

## 📊 Customer Mapping

| Customer ID | Customer Name |
|------------|---------------|
| 6265362093 | Communn.io |
| 5032737756 | Emcee Sons |
| 7613138874 | VANAVASI KALYANA |

---

## 🗄️ Database Changes

### 1. Created `customers` Table

```sql
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    descriptive_name TEXT,
    currency_code TEXT DEFAULT 'INR',
    time_zone TEXT DEFAULT 'Asia/Kolkata',
    status TEXT DEFAULT 'ENABLED',
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### 2. Populated with Customer Names

Run this script to add/update customer names:

```bash
python add_customer_names.py
```

**Output:**
```
[✓] Added: Communn.io (ID: 6265362093)
[✓] Added: Emcee Sons (ID: 5032737756)
[✓] Added: VANAVASI KALYANA (ID: 7613138874)
```

---

## 🔌 API Changes

### Updated Endpoints

**1. GET /customers**

Returns list of customers with names:

```json
{
  "customers": [
    {
      "customer_id": 6265362093,
      "customer_name": "Communn.io",
      "campaigns_count": 15
    },
    {
      "customer_id": 5032737756,
      "customer_name": "Emcee Sons",
      "campaigns_count": 8
    },
    {
      "customer_id": 7613138874,
      "customer_name": "VANAVASI KALYANA",
      "campaigns_count": 12
    }
  ],
  "total": 3
}
```

**2. GET /customers/{customer_id}/summary**

Returns customer summary with name:

```json
{
  "customer_id": 6265362093,
  "customer_name": "Communn.io",
  "campaigns_count": 15,
  "metrics": {
    "clicks": 1234,
    "impressions": 45678,
    "cost": 12345.67,
    "conversions": 89
  }
}
```

---

## 🧪 Testing

### Test the API

```bash
python test_customer_names.py
```

**Expected Output:**
```
✓ Found 3 customers:

  • Communn.io
    ID: 6265362093
    Campaigns: 15

  • Emcee Sons
    ID: 5032737756
    Campaigns: 8

  • VANAVASI KALYANA
    ID: 7613138874
    Campaigns: 12
```

### Manual API Test

1. Start the API server:
```bash
cd api
uvicorn app.main:app --reload
```

2. Open in browser:
```
http://localhost:8000/customers
```

3. You should see customer names instead of just IDs!

---

## 💻 Frontend Integration

### JavaScript Example

Fetch customers with names:

```javascript
fetch('http://localhost:8000/customers')
  .then(res => res.json())
  .then(data => {
    data.customers.forEach(customer => {
      console.log(`${customer.customer_name} (ID: ${customer.customer_id})`);
      // Shows: "Communn.io (ID: 6265362093)"
    });
  });
```

### Dropdown/Select Example

```html
<select id="customerSelector">
  <option value="">Select Customer</option>
  <!-- Populated from API -->
</select>

<script>
fetch('/customers')
  .then(res => res.json())
  .then(data => {
    const select = document.getElementById('customerSelector');

    data.customers.forEach(customer => {
      const option = document.createElement('option');
      option.value = customer.customer_id;
      option.textContent = customer.customer_name; // Shows "Communn.io"
      select.appendChild(option);
    });
  });
</script>
```

---

## 🔄 Adding New Customers

### Method 1: Update the Script

Edit `add_customer_names.py`:

```python
CUSTOMER_NAMES = {
    6265362093: "Communn.io",
    5032737756: "Emcee Sons",
    7613138874: "VANAVASI KALYANA",
    1234567890: "New Customer Name"  # Add new customer
}
```

Then run:
```bash
python add_customer_names.py
```

### Method 2: Direct SQL

```bash
python -c "import sqlite3; conn = sqlite3.connect('google_ads_data.db'); conn.execute('INSERT OR REPLACE INTO customers (customer_id, customer_name) VALUES (1234567890, \"New Customer\")'); conn.commit()"
```

### Method 3: ETL Pipeline Integration

The ETL pipeline can be updated to automatically fetch customer names from Google Ads API:

Edit `google_ads_etl_pipeline.py`, add this function:

```python
def sync_customer_names(self):
    """Fetch customer names from Google Ads API and update database"""
    query = """
        SELECT
            customer_client.id,
            customer_client.descriptive_name
        FROM customer_client
        WHERE customer_client.status = 'ENABLED'
    """

    response = self.ga_service.search(customer_id=self.manager_id, query=query)

    for row in response:
        customer_id = row.customer_client.id
        customer_name = row.customer_client.descriptive_name

        self.cursor.execute("""
            INSERT OR REPLACE INTO customers
            (customer_id, customer_name, descriptive_name, status)
            VALUES (?, ?, ?, 'ENABLED')
        """, (customer_id, customer_name, customer_name))

    self.conn.commit()
```

---

## 📁 Files Modified/Created

### Created:
- ✅ `add_customer_names.py` - Script to populate customer names
- ✅ `test_customer_names.py` - Test script for verification
- ✅ `CUSTOMER_NAMES_SETUP.md` - This documentation

### Modified:
- ✅ `api/app/db/models.py` - Added `Customer` model
- ✅ `api/app/routes/customers.py` - Updated to use customer names

---

## ✅ Verification Checklist

- [x] Customer table created
- [x] Customer names populated
- [x] API endpoints updated
- [x] Customer model added
- [x] Test script created

---

## 🎯 Result

**Before:**
```
Customer Selector:
- Customer 6265362093
- Customer 5032737756
- Customer 7613138874
```

**After:**
```
Customer Selector:
- Communn.io
- Emcee Sons
- VANAVASI KALYANA
```

---

## 🚀 Next Steps

1. ✅ Run `python add_customer_names.py` (if not done already)
2. ✅ Start API server: `cd api && uvicorn app.main:app --reload`
3. ✅ Test: `python test_customer_names.py`
4. ✅ Update your frontend to fetch from `/customers` endpoint
5. ✅ Use `customer_name` field instead of displaying `customer_id`

---

## 📞 Support

If you need to:
- **Add more customers:** Edit `add_customer_names.py` and re-run
- **Change a name:** Update in `CUSTOMER_NAMES` dictionary and re-run
- **Test changes:** Run `python test_customer_names.py`

---

**Setup Complete! Your web page will now show customer names instead of IDs.** ✅
