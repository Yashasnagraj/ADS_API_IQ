# Google Ads API Setup Guide 🚀

## Complete Setup Instructions for New Users

---

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Python Requirements](#python-requirements)
3. [Google Ads Account Setup](#google-ads-account-setup)
4. [Google Cloud Project Setup](#google-cloud-project-setup)
5. [API Credentials](#api-credentials)
6. [Configuration Files](#configuration-files)
7. [Testing Your Setup](#testing-your-setup)
8. [Troubleshooting](#troubleshooting)

---

## 📌 Prerequisites

### System Requirements
- **Python**: 3.8 or higher (3.10+ recommended)
- **Operating System**: Windows, macOS, or Linux
- **Memory**: At least 4GB RAM
- **Storage**: 500MB free space for data extraction

### Account Requirements
- ✅ **Google Ads Account** (Manager or Client account)
- ✅ **Google Cloud Account** (for API access)
- ✅ **Billing enabled** on Google Cloud (API is free up to limits)

---

## 🐍 Python Requirements

### 1. Install Python Libraries

Create a `requirements.txt` file:

```txt
google-ads==28.0.0
pandas==2.0.3
sqlite3
google-auth-oauthlib==1.0.0
google-auth==2.22.0
requests==2.31.0
```

Install using pip:

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install google-ads
pip install pandas
pip install google-auth-oauthlib
pip install google-auth
pip install requests
```

### 2. Verify Installation

```python
import google.ads.googleads
print(f"Google Ads API version: {google.ads.googleads.__version__}")
```

---

## 📊 Google Ads Account Setup

### 1. Types of Accounts

#### **Manager Account (MCC)**
- Can manage multiple client accounts
- Cannot have its own campaigns
- Used for agencies or businesses with multiple accounts
- Example ID: `123-456-7890`

#### **Client Account**
- Contains actual campaigns, keywords, and ads
- Can be standalone or under a manager account
- Example ID: `987-654-3210`

### 2. Find Your Customer ID

1. **Login to Google Ads**: https://ads.google.com
2. **Look at the top right corner** of the interface
3. **Click on your account name** - the Customer ID is displayed
4. **Remove hyphens** when using in code: `123-456-7890` → `1234567890`

![Customer ID Location](https://support.google.com/google-ads/answer/1704344)

### 3. Account Hierarchy

```
Manager Account (MCC)
├── Client Account 1
│   ├── Campaign A
│   │   ├── Ad Group 1
│   │   │   ├── Keyword 1
│   │   │   └── Keyword 2
│   │   └── Ad Group 2
│   └── Campaign B
└── Client Account 2
```

---

## ☁️ Google Cloud Project Setup

### Step 1: Create a Google Cloud Project

1. **Go to**: https://console.cloud.google.com
2. **Click** "Select a project" → "New Project"
3. **Enter** project name (e.g., "google-ads-api-project")
4. **Click** "Create"
5. **Note your Project ID** (you'll need this)

### Step 2: Enable Google Ads API

1. **In Google Cloud Console**, go to "APIs & Services" → "Library"
2. **Search for** "Google Ads API"
3. **Click** on Google Ads API
4. **Click** "ENABLE"
5. **Wait** for activation (may take 2-3 minutes)

### Step 3: Create OAuth 2.0 Credentials

1. **Go to** "APIs & Services" → "Credentials"
2. **Click** "Create Credentials" → "OAuth client ID"
3. **If prompted**, configure OAuth consent screen:
   - User Type: "External"
   - App name: Your app name
   - User support email: Your email
   - Developer contact: Your email
4. **Application type**: "Desktop app" or "Web application"
5. **Name**: "Google Ads API Client"
6. **Click** "Create"
7. **Download** the credentials JSON file

---

## 🔑 API Credentials

### 1. Developer Token

#### How to Get a Developer Token:

1. **Login to Google Ads**: https://ads.google.com
2. **Click** Tools & Settings (⚙️) → Setup → API Center
3. **If no API Center**, you need to apply:
   - Go to: https://developers.google.com/google-ads/api/docs/get-started/dev-token
   - Fill out the application form
   - Select "Test Account" for immediate access
4. **Copy your Developer Token** (looks like: `ouYOcEpDiQOJCTs-Rkc1mA`)

#### Token Access Levels:
- **Test Account Access**: Immediate, works only with test accounts
- **Basic Access**: Takes 1-2 days, works with real accounts
- **Standard Access**: For high-volume usage

### 2. OAuth2 Credentials

From your downloaded JSON file, extract:

```json
{
  "installed": {
    "client_id": "27301795624-xxxxx.apps.googleusercontent.com",
    "client_secret": "GOCSPX-xxxxxxxxxxxxx",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  }
}
```

### 3. Refresh Token

#### Generate Refresh Token:

1. **Save this script** as `get_refresh_token.py`:

```python
#!/usr/bin/env python3
from google_auth_oauthlib.flow import Flow

# Replace with your credentials
CLIENT_ID = "your-client-id.apps.googleusercontent.com"
CLIENT_SECRET = "your-client-secret"

SCOPES = ["https://www.googleapis.com/auth/adwords"]

flow = Flow.from_client_config(
    {
        "installed": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    },
    scopes=SCOPES,
)

flow.redirect_uri = "http://localhost:8080"

auth_url, _ = flow.authorization_url(
    access_type="offline",
    prompt="consent",
)

print(f"1. Open this URL in your browser:\n{auth_url}\n")
print("2. Authorize the application")
print("3. Copy the full redirect URL")

auth_response = input("Paste the redirect URL here: ").strip()

flow.fetch_token(authorization_response=auth_response)
refresh_token = flow.credentials.refresh_token

print(f"\nYour refresh token:\n{refresh_token}")
```

2. **Run the script**: `python get_refresh_token.py`
3. **Follow the prompts** and authorize access
4. **Save the refresh token**

---

## 📁 Configuration Files

### 1. Create `google-ads.yaml`

```yaml
developer_token: YOUR_DEVELOPER_TOKEN_HERE
client_id: YOUR_CLIENT_ID.apps.googleusercontent.com
client_secret: YOUR_CLIENT_SECRET
refresh_token: YOUR_REFRESH_TOKEN
use_proto_plus: True

# If using a manager account to access client accounts:
login_customer_id: YOUR_MANAGER_ACCOUNT_ID

# Optional: Specify API version
version: v21
```

### 2. Configuration Parameters Explained

| Parameter | Description | Example | Required |
|-----------|-------------|---------|----------|
| `developer_token` | API access token from Google Ads | `ouYOcEpDiQOJCTs-Rkc1mA` | ✅ Yes |
| `client_id` | OAuth2 client ID | `12345-xxx.apps.googleusercontent.com` | ✅ Yes |
| `client_secret` | OAuth2 client secret | `GOCSPX-xxxxx` | ✅ Yes |
| `refresh_token` | Long-lived auth token | `1//0gxxxxx` | ✅ Yes |
| `use_proto_plus` | Use Proto Plus messages | `True` | ✅ Yes |
| `login_customer_id` | Manager account ID (if applicable) | `1234567890` | ❓ If using MCC |

### 3. File Structure

```
your_project/
├── google-ads.yaml              # API configuration
├── client_secret_xxx.json       # OAuth2 credentials (keep secure!)
├── requirements.txt             # Python dependencies
├── extract_google_ads.py        # Data extraction script
├── google_ads_etl_pipeline.py   # ETL pipeline
├── google_ads_data.db          # SQLite database (generated)
└── extracted_data/             # CSV exports (generated)
    ├── campaigns.csv
    ├── keywords.csv
    └── ...
```

---

## 🧪 Testing Your Setup

### 1. Test Authentication

Create `test_connection.py`:

```python
#!/usr/bin/env python3
from google.ads.googleads.client import GoogleAdsClient

try:
    # Load configuration
    client = GoogleAdsClient.load_from_storage("google-ads.yaml")
    print("✅ Successfully loaded configuration!")

    # Get service
    ga_service = client.get_service("GoogleAdsService")
    print("✅ Successfully connected to Google Ads API!")

    # Test query (replace with your customer ID)
    customer_id = "YOUR_CUSTOMER_ID"
    query = "SELECT customer.id, customer.descriptive_name FROM customer LIMIT 1"

    response = ga_service.search(customer_id=customer_id, query=query)
    for row in response:
        print(f"✅ Account found: {row.customer.descriptive_name} (ID: {row.customer.id})")

except Exception as e:
    print(f"❌ Error: {e}")
```

### 2. List Accessible Accounts

```python
#!/usr/bin/env python3
from google.ads.googleads.client import GoogleAdsClient

client = GoogleAdsClient.load_from_storage("google-ads.yaml")
customer_service = client.get_service("CustomerService")

accessible_customers = customer_service.list_accessible_customers()
print("Accessible accounts:")
for resource_name in accessible_customers.resource_names:
    customer_id = resource_name.split('/')[-1]
    print(f"  - Customer ID: {customer_id}")
```

---

## 🔧 Troubleshooting

### Common Errors and Solutions

#### 1. "Invalid grant: Bad Request"
**Problem**: Refresh token is invalid or expired
**Solution**:
- Generate a new refresh token using `get_refresh_token.py`
- Ensure you're using the correct Google account
- Check that OAuth2 consent screen is configured

#### 2. "Google Ads API has not been used in project"
**Problem**: API not enabled in Google Cloud
**Solution**:
- Go to: https://console.developers.google.com/apis/api/googleads.googleapis.com/overview?project=YOUR_PROJECT_ID
- Click "Enable API"
- Wait 2-3 minutes for activation

#### 3. "The client library configuration is missing required 'use_proto_plus' key"
**Problem**: Missing configuration parameter
**Solution**: Add `use_proto_plus: True` to your `google-ads.yaml`

#### 4. "Metrics cannot be requested for a manager account"
**Problem**: Trying to get metrics from MCC account
**Solution**:
- Use a client account ID instead
- Add `login_customer_id: YOUR_MANAGER_ID` to config
- Query client accounts under the manager

#### 5. "USER_PERMISSION_DENIED"
**Problem**: Account doesn't have access
**Solution**:
- Verify the Google account has access to the Google Ads account
- Check account linking in Google Ads UI
- Ensure developer token is approved for the account

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Your code here
```

---

## 📚 Additional Resources

### Official Documentation
- **Google Ads API Docs**: https://developers.google.com/google-ads/api/docs/start
- **GAQL Reference**: https://developers.google.com/google-ads/api/docs/query/overview
- **Python Client Library**: https://github.com/googleads/google-ads-python
- **API Rate Limits**: https://developers.google.com/google-ads/api/docs/rate-limits

### Useful Tools
- **GAQL Query Builder**: https://developers.google.com/google-ads/api/docs/query/playground
- **Google Ads Editor**: https://ads.google.com/home/tools/ads-editor/
- **OAuth2 Playground**: https://developers.google.com/oauthplayground/

### Community Support
- **Stack Overflow**: Tag with `google-ads-api`
- **Google Ads API Forum**: https://groups.google.com/g/adwords-api
- **GitHub Issues**: https://github.com/googleads/google-ads-python/issues

---

## ✅ Setup Checklist

- [ ] Python 3.8+ installed
- [ ] Google Ads account created
- [ ] Google Cloud project created
- [ ] Google Ads API enabled
- [ ] OAuth2 credentials created
- [ ] Developer token obtained
- [ ] Refresh token generated
- [ ] `google-ads.yaml` configured
- [ ] Python libraries installed
- [ ] Test connection successful
- [ ] First data extraction completed

---

## 🎯 Next Steps

Once setup is complete:

1. **Run the ETL pipeline**: `python google_ads_etl_pipeline.py`
2. **Query the database**: Use SQLite to explore `google_ads_data.db`
3. **Export to CSV**: Check `extracted_data/` folder
4. **Build ML models**: Use the `ml_features` table
5. **Schedule regular updates**: Set up cron job or task scheduler

---

## 📝 Security Best Practices

1. **Never commit credentials** to version control
2. **Add to `.gitignore`**:
   ```
   google-ads.yaml
   client_secret*.json
   *.db
   extracted_data/
   ```
3. **Use environment variables** for production:
   ```python
   import os
   developer_token = os.environ.get('GOOGLE_ADS_DEV_TOKEN')
   ```
4. **Rotate refresh tokens** periodically
5. **Limit API access** to specific IP addresses if possible
6. **Monitor API usage** in Google Cloud Console

---

*Last Updated: 2025-09-15*
*Guide Version: 1.0*
*Compatible with Google Ads API v21*