# Meta Developer Setup Guide - Step by Step

**What to do in Meta Business Manager & Developer Portal**

This guide shows you exactly what to click and configure in Meta's platforms to get API access.

---

## Overview

You need 4 things from Meta:
1. **App ID** - From Meta Developer Portal
2. **App Secret** - From Meta Developer Portal
3. **Access Token** - Generated via Graph API Explorer
4. **Ad Account ID** - From Meta Ads Manager

---

## Part 1: Meta Business Manager Setup (5 minutes)

### Step 1: Access Business Manager

1. Go to: **https://business.facebook.com**
2. Log in with your Facebook account
3. If you don't have a Business Manager:
   - Click **Create Account**
   - Enter your business name
   - Fill in your details
   - Click **Submit**

### Step 2: Verify Your Ad Account is Connected

1. In Business Manager, click **⚙️ Business Settings** (bottom left)
2. Click **Accounts** → **Ad Accounts** (left sidebar)
3. You should see your ad account listed
4. **Copy the Ad Account ID** (format: 1234567890)
   - You'll need to add `act_` prefix later → `act_1234567890`

**If no ad account:**
1. Click **Add** → **Create a New Ad Account**
2. Fill in details and create
3. Copy the Account ID

---

## Part 2: Create Meta App (10 minutes)

### Step 1: Go to Meta for Developers

1. Open: **https://developers.facebook.com**
2. Log in with the same Facebook account
3. Click **My Apps** (top right)

### Step 2: Create New App

1. Click **Create App** button (green button)
2. Select use case: **Other**
   - Click **Next**
3. Select app type: **Business**
   - Click **Next**
4. Fill in app details:
   - **App Name**: `MarketingIQ Meta API` (or your choice)
   - **App Contact Email**: Your email
   - **Business Account**: Select your business (or create new)
5. Click **Create App**
6. Complete security check if prompted

### Step 3: Copy App Credentials

After app is created:

1. You'll see the app dashboard
2. Left sidebar → Click **Settings** → **Basic**
3. You'll see:
   - **App ID**: `1234567890123456`
     - **COPY THIS** → This is your `META_APP_ID`
   - **App Secret**: Click **Show** button
     - Enter your Facebook password
     - **COPY THIS** → This is your `META_APP_SECRET`
     - ⚠️ Keep this secret! Never share or commit to git

**Save these somewhere safe:**
```
META_APP_ID=1234567890123456
META_APP_SECRET=abc123def456ghi789jkl
```

### Step 4: Add Marketing API Product

1. Left sidebar → Click **Add Product** (under Products)
2. Find **Marketing API** in the list
3. Click **Set Up** button
4. Marketing API will now appear in left sidebar
5. No configuration needed here for now

### Step 5: Configure App Settings

1. Left sidebar → **Settings** → **Basic**
2. Scroll down to **App Domains**
3. Add: `localhost` (for development)
4. Scroll down to **Platform**
5. Click **+ Add Platform**
6. Select **Website**
7. Site URL: `http://localhost:8000`
8. Click **Save Changes** (bottom right)

---

## Part 3: Generate Access Token (5 minutes)

### Step 1: Open Graph API Explorer

1. Go to: **https://developers.facebook.com/tools/explorer/**
2. Top right → Select your app from dropdown (not "Graph API Explorer")
   - Should show: `MarketingIQ Meta API` or whatever you named it

### Step 2: Add Permissions

1. Click **Permissions** tab (below the app selector)
2. Search and check these permissions:
   - ✅ `ads_read`
   - ✅ `ads_management`
   - ✅ `read_insights`
3. OR manually add them:
   - Click **Add a Permission**
   - Type: `ads_read` → Check it
   - Type: `ads_management` → Check it
   - Type: `read_insights` → Check it

### Step 3: Generate Token

1. Click **Generate Access Token** button
2. A popup appears → Click **Continue**
3. Facebook login popup:
   - Select which ad accounts to give access to
   - ✅ Check your ad account
   - Click **Next**
4. Review permissions:
   - Should show: "Manage your ads", "Read insights", etc.
   - Click **Done**
5. You'll be back at Graph API Explorer
6. The access token appears in the **Access Token** field
   - It's a LONG string starting with `EAAE...`
   - **COPY THIS TOKEN** (but don't save it yet - it's short-lived)

### Step 4: Test the Token (Optional)

1. In Graph API Explorer, keep the token in the field
2. Query field: Change to `/act_YOUR_ACCOUNT_ID`
   - Replace `YOUR_ACCOUNT_ID` with your ad account ID
   - Example: `/act_1234567890`
3. Click **Submit**
4. Should return JSON with account info:
   ```json
   {
     "id": "act_1234567890",
     "name": "My Ad Account"
   }
   ```
5. If error → Check permissions or ad account ID

---

## Part 4: Configure Your Project (2 minutes)

### Step 1: Create `.env.meta` File

In your project folder `D:\ADS_API\`:

1. Copy the example file:
   ```bash
   copy .env.meta.example .env.meta
   ```

2. Open `.env.meta` in any text editor

3. Fill in the values:
   ```env
   # From Step 3 (Meta App)
   META_APP_ID=1234567890123456
   META_APP_SECRET=abc123def456ghi789jkl

   # Leave blank for now - we'll generate this next
   META_ACCESS_TOKEN=

   # From Step 2 (Business Manager)
   # IMPORTANT: Add "act_" prefix!
   META_AD_ACCOUNT_ID=act_1234567890

   # Usually 1 for single customer
   CUSTOMER_ID=1

   # Optional - leave as is
   META_API_VERSION=v19.0
   ```

4. **Save the file**

### Step 2: Generate Long-Lived Token

Now run our script to convert the short-lived token to a long-lived one:

```bash
python generate_meta_token.py
```

**Follow the prompts:**

```
======================================================================
META ACCESS TOKEN GENERATOR
======================================================================

App ID: 1234567890123456
Ad Account: act_1234567890

======================================================================
STEP 1: Get Short-Lived Token from Graph API Explorer
======================================================================

1. Go to: https://developers.facebook.com/tools/explorer/
2. Select your app: 1234567890123456
3. Add these permissions:
   ✓ ads_read
   ✓ ads_management
   ✓ read_insights
4. Click 'Generate Access Token'
5. Authorize the permissions
6. Copy the generated token

======================================================================

Paste your SHORT-LIVED token here:
>
```

**Paste the token you copied from Graph API Explorer** (the EAAE... string)

Press Enter.

**Output should be:**
```
🔄 Exchanging token for long-lived version...
✅ Got long-lived token!
   Expires in: 5184000 seconds (~60 days)

🧪 Testing token...
✅ Token works!
   Account: Your Ad Account Name
   Status: 1
   Currency: USD

✅ Updated .env.meta with new token

======================================================================
✅ SUCCESS! Token updated
======================================================================

You can now run:
   python warehouse_meta_ads_etl.py --days=30
======================================================================
```

**Done!** Your `.env.meta` now has a long-lived token (valid for 60 days).

---

## Part 5: Test the Setup (2 minutes)

### Run ETL Pipeline

```bash
python warehouse_meta_ads_etl.py --days=30
```

**Expected output:**
```
======================================================================
META ADS → WAREHOUSE ETL PIPELINE
======================================================================

📋 Configuration:
   Customer ID: 1
   Meta Ad Account: act_1234567890
   Days: 30

🔌 Connecting to warehouse...
   ✅ Connected

🔐 Initializing Meta API...
✅ Meta Marketing API initialized

📊 Fetching campaigns from Meta API...
   ✅ Fetched 15 campaigns

📊 Fetching campaign insights (last 30 days)...
   ✅ Fetched 450 daily insight records for 15 campaigns

💾 Loading data into warehouse...
   ✅ Loaded 15 campaigns
   ✅ Loaded 450 performance records

======================================================================
✅ META ADS ETL COMPLETED
======================================================================
```

**If successful** → You're done! ✅

---

## Common Issues & Fixes

### Issue: "Invalid OAuth access token"

**Cause:** Token expired or wrong token copied

**Fix:**
1. Go back to Graph API Explorer
2. Generate new token
3. Run `python generate_meta_token.py` again
4. Paste the fresh token

---

### Issue: "Ad account not found"

**Cause:** Wrong ad account ID or missing "act_" prefix

**Fix:**
1. Go to: https://adsmanager.facebook.com
2. Look at URL: `https://adsmanager.facebook.com/adsmanager/manage/campaigns?act=1234567890`
3. Copy the number after `act=`
4. In `.env.meta`, set: `META_AD_ACCOUNT_ID=act_1234567890` (with "act_" prefix)

---

### Issue: "Insufficient permissions"

**Cause:** Missing required permissions when generating token

**Fix:**
1. Go to Graph API Explorer
2. Click **Permissions** tab
3. Make sure these are checked:
   - ✅ ads_read
   - ✅ ads_management
   - ✅ read_insights
4. Click **Generate Access Token** again
5. Run `python generate_meta_token.py` with new token

---

### Issue: "App not configured for Business"

**Cause:** App type is wrong

**Fix:**
1. Go to https://developers.facebook.com/apps
2. Click your app
3. **Settings** → **Basic**
4. Check **Category**: Should be "Business"
5. If wrong, you may need to create a new app (select "Business" type)

---

### Issue: "This ad account is not accessible"

**Cause:** Your Facebook account doesn't have access to the ad account

**Fix:**
1. Go to: https://business.facebook.com/settings/ad-accounts
2. Find the ad account
3. Click on it
4. **People** tab → Make sure you're listed
5. Your role should be **Admin** or **Advertiser**
6. If not listed, ask the Business Manager admin to add you

---

## Token Expiration & Renewal

### Short-Lived Token
- **Lifespan:** 1-2 hours
- **When you get it:** Graph API Explorer (first time)

### Long-Lived Token
- **Lifespan:** 60 days
- **When you get it:** After running `generate_meta_token.py`
- **Renewal:** Run the script again every 60 days

### Never-Expiring Token (Production Setup)

For production, use a **System User** token that never expires:

#### Step 1: Create System User
1. Go to: https://business.facebook.com/settings/system-users
2. Click **Add** button
3. Name: `MarketingIQ API System User`
4. Role: **Admin**
5. Click **Create System User**

#### Step 2: Assign Ad Account Access
1. Click on the system user you just created
2. Click **Add Assets**
3. Select **Ad Accounts**
4. Check your ad account
5. Toggle **Full control** to ON
6. Click **Save Changes**

#### Step 3: Generate Token
1. Click **Generate New Token**
2. Select your app: `MarketingIQ Meta API`
3. Check permissions:
   - ✅ ads_read
   - ✅ ads_management
   - ✅ read_insights
4. Click **Generate Token**
5. **Copy the token** (this is a LONG string)
   - ⚠️ Save it immediately! You can't see it again
6. Paste it in `.env.meta`:
   ```env
   META_ACCESS_TOKEN=<paste_system_user_token_here>
   ```

**Benefits:**
- ✅ Never expires
- ✅ No need to regenerate every 60 days
- ✅ Better for production/automation

---

## Quick Reference: Where to Find Everything

| What you need | Where to find it |
|---------------|------------------|
| **App ID** | https://developers.facebook.com/apps → Your App → Settings → Basic |
| **App Secret** | Same as above, click "Show" |
| **Access Token** | https://developers.facebook.com/tools/explorer/ → Generate Access Token |
| **Ad Account ID** | https://adsmanager.facebook.com → URL bar → `act=1234567890` |
| **System User Token** | https://business.facebook.com/settings/system-users → Generate New Token |
| **Business Manager** | https://business.facebook.com |
| **Verify Token** | https://developers.facebook.com/tools/debug/accesstoken/ |

---

## Complete Setup Checklist

- [ ] Logged into Facebook Business Manager
- [ ] Verified ad account is connected
- [ ] Copied ad account ID (without "act_" prefix)
- [ ] Created Meta app at developers.facebook.com
- [ ] Copied App ID
- [ ] Copied App Secret
- [ ] Added Marketing API product to app
- [ ] Went to Graph API Explorer
- [ ] Selected my app in dropdown
- [ ] Added permissions: ads_read, ads_management, read_insights
- [ ] Generated access token
- [ ] Copied short-lived token
- [ ] Created `.env.meta` file
- [ ] Filled in App ID, App Secret, Ad Account ID (with "act_" prefix)
- [ ] Ran `python generate_meta_token.py`
- [ ] Pasted short-lived token when prompted
- [ ] Got success message with long-lived token
- [ ] Ran `python warehouse_meta_ads_etl.py --days=30`
- [ ] ETL completed successfully
- [ ] Data loaded into marketing_warehouse.db

---

## Screenshots Guide (What to Look For)

### Meta Developer Portal - Create App
```
[Create App Button]
→ Select "Other"
→ Select "Business"
→ Enter app name
→ Select business
→ [Create App]
```

### App Dashboard - Get Credentials
```
Left sidebar: Settings → Basic

┌─────────────────────────────────────┐
│ App ID: 1234567890123456            │  ← COPY THIS
│                                     │
│ App Secret: [Show]  ← Click this   │
│ (After clicking Show)               │
│ abc123def456... [Hide]              │  ← COPY THIS
└─────────────────────────────────────┘
```

### Graph API Explorer - Generate Token
```
Top right: [Graph API Explorer ▼] → Select YOUR APP

Permissions tab:
☐ ads_read          ← Check these
☐ ads_management    ← Check these
☐ read_insights     ← Check these

[Generate Access Token] ← Click this

Access Token field:
┌─────────────────────────────────────────────────┐
│ EAAExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx...         │ ← COPY THIS
└─────────────────────────────────────────────────┘
```

### Business Manager - Get Ad Account ID
```
Business Settings → Accounts → Ad Accounts

Ad Account Name          Ad Account ID
My Ad Account           1234567890        ← COPY THIS
                                          → Add "act_" → act_1234567890
```

---

## Final `.env.meta` File Should Look Like:

```env
# Meta App Credentials
META_APP_ID=1234567890123456
META_APP_SECRET=abc123def456ghi789jkl

# Access Token (long-lived, auto-filled by generate_meta_token.py)
META_ACCESS_TOKEN=EAAExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Ad Account ID (with "act_" prefix)
META_AD_ACCOUNT_ID=act_1234567890

# Internal Customer ID
CUSTOMER_ID=1

# API Version
META_API_VERSION=v19.0
```

---

## Need Help?

### Test Your Token
Paste your access token here to check if it's valid:
https://developers.facebook.com/tools/debug/accesstoken/

### Meta Developer Support
- Community: https://developers.facebook.com/community/
- Docs: https://developers.facebook.com/docs/marketing-api
- Status: https://developers.facebook.com/status/

### Common Meta Error Codes
- **Error 190**: Invalid token → Regenerate token
- **Error 200**: Missing permissions → Add required permissions
- **Error 100**: Invalid parameter → Check ad account ID format
- **Error 17**: Limit reached → API rate limit, wait and retry

---

**That's it!** You should now have everything configured in Meta Developer Portal. 🎉

**Next:** Run `python warehouse_meta_ads_etl.py --days=30` to start pulling data!
