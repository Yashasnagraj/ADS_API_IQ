"""
Meta (Facebook) Ads Setup Script

Validates Meta Marketing API connection and sets up ad account in database.

Prerequisites:
1. Create .env.meta file with credentials (copy from .env.meta.example)
2. Install dependencies: pip install facebook-business

Usage:
    python setup_meta_ads.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount

# Add project root and api directory to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'api'))

from api.app.db.database import SessionLocal, engine
from api.app.db import models

# Create all tables
models.Base.metadata.create_all(bind=engine)


def load_config():
    """Load configuration from .env.meta"""
    env_path = Path(__file__).parent / '.env.meta'

    if not env_path.exists():
        print("❌ ERROR: .env.meta file not found!")
        print("")
        print("Please create .env.meta file:")
        print("  1. Copy .env.meta.example to .env.meta")
        print("  2. Fill in your Meta credentials")
        print("")
        print("Need help? See META_ADS_SETUP_GUIDE.md")
        sys.exit(1)

    load_dotenv(env_path)

    app_id = os.getenv('META_APP_ID')
    app_secret = os.getenv('META_APP_SECRET')
    access_token = os.getenv('META_ACCESS_TOKEN')
    ad_account_id = os.getenv('META_AD_ACCOUNT_ID')
    customer_id = os.getenv('CUSTOMER_ID')
    api_version = os.getenv('META_API_VERSION', 'v19.0')

    if not all([app_id, app_secret, access_token, ad_account_id, customer_id]):
        print("❌ ERROR: Missing required configuration in .env.meta")
        print("")
        print("Required fields:")
        print("  - META_APP_ID")
        print("  - META_APP_SECRET")
        print("  - META_ACCESS_TOKEN")
        print("  - META_AD_ACCOUNT_ID")
        print("  - CUSTOMER_ID")
        sys.exit(1)

    # Validate ad account ID format
    if not ad_account_id.startswith('act_'):
        print("❌ ERROR: META_AD_ACCOUNT_ID must start with 'act_'")
        print(f"   Got: {ad_account_id}")
        print(f"   Expected format: act_123456789")
        sys.exit(1)

    return {
        'app_id': app_id,
        'app_secret': app_secret,
        'access_token': access_token,
        'ad_account_id': ad_account_id,
        'customer_id': int(customer_id),
        'api_version': api_version
    }


def validate_meta_connection(config):
    """
    Validate Meta Marketing API connection

    Returns:
        dict: Ad account details if successful
    """
    try:
        # Initialize Facebook Ads API
        FacebookAdsApi.init(
            app_id=config['app_id'],
            app_secret=config['app_secret'],
            access_token=config['access_token'],
            api_version=config['api_version']
        )

        print(f"   Testing connection to {config['ad_account_id']}...")

        # Fetch ad account details
        ad_account = AdAccount(config['ad_account_id'])
        account_info = ad_account.api_get(fields=[
            'name',
            'account_id',
            'account_status',
            'currency',
            'timezone_name',
            'business',
        ])

        return {
            'account_id': config['ad_account_id'],
            'account_name': account_info.get('name', 'Unknown'),
            'account_status': str(account_info.get('account_status', 'UNKNOWN')),
            'currency': account_info.get('currency', 'USD'),
            'timezone_name': account_info.get('timezone_name', 'UTC'),
            'business_id': account_info.get('business', {}).get('id') if account_info.get('business') else None
        }

    except Exception as e:
        print(f"   ❌ Connection failed: {str(e)}")
        print("")
        print("Common issues:")
        print("  1. Invalid access token (expired or incorrect)")
        print("  2. App doesn't have Marketing API permissions")
        print("  3. Access token doesn't have access to this ad account")
        print("  4. Ad account ID format incorrect (must be act_123456789)")
        print("")
        print("Solutions:")
        print("  - Regenerate access token: https://developers.facebook.com/tools/explorer")
        print("  - Check app permissions in: https://developers.facebook.com/apps")
        print("  - Verify ad account access in: https://business.facebook.com/settings/ad-accounts")
        sys.exit(1)


def save_account_to_db(config, account_info):
    """Save Meta ad account to database"""
    db = SessionLocal()

    try:
        # Check if customer exists
        customer = db.query(models.Customer).filter(
            models.Customer.customer_id == config['customer_id']
        ).first()

        if not customer:
            print(f"\n⚠️  WARNING: Customer {config['customer_id']} not found in database")
            print(f"   Creating customer record...")

            customer = models.Customer(
                customer_id=config['customer_id'],
                customer_name=account_info['account_name'],
                descriptive_name=f"Meta Ads: {account_info['account_name']}",
                currency_code=account_info['currency'],
                status='ENABLED'
            )
            db.add(customer)
            db.commit()
            print(f"   ✅ Customer created")

        # Check if account already exists
        existing = db.query(models.MetaAdAccount).filter(
            models.MetaAdAccount.account_id == account_info['account_id']
        ).first()

        if existing:
            # Update existing record
            existing.account_name = account_info['account_name']
            existing.account_status = account_info['account_status']
            existing.currency = account_info['currency']
            existing.timezone_name = account_info['timezone_name']
            existing.business_id = account_info['business_id']
            existing.access_token = config['access_token']
            existing.is_active = True
            existing.updated_at = datetime.now()

            print(f"\n✅ Updated existing ad account in database")
        else:
            # Create new record
            meta_account = models.MetaAdAccount(
                account_id=account_info['account_id'],
                customer_id=config['customer_id'],
                account_name=account_info['account_name'],
                account_status=account_info['account_status'],
                currency=account_info['currency'],
                timezone_name=account_info['timezone_name'],
                business_id=account_info['business_id'],
                access_token=config['access_token'],
                is_active=True,
                installed_at=datetime.now()
            )
            db.add(meta_account)

            print(f"\n✅ Saved ad account to database")

        db.commit()

    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR saving to database: {str(e)}")
        sys.exit(1)
    finally:
        db.close()


def main():
    """Main setup flow"""
    print("=" * 70)
    print("META ADS ACCOUNT SETUP")
    print("=" * 70)

    # Load configuration
    print("\n📋 Loading configuration from .env.meta...")
    config = load_config()

    print(f"   App ID: {config['app_id']}")
    print(f"   Ad Account ID: {config['ad_account_id']}")
    print(f"   Customer ID: {config['customer_id']}")
    print(f"   API Version: {config['api_version']}")

    # Validate connection
    print(f"\n🔐 Validating Meta API access...")
    account_info = validate_meta_connection(config)

    print(f"\n✅ Connected to Meta Ad Account:")
    print(f"   Account ID: {account_info['account_id']}")
    print(f"   Account Name: {account_info['account_name']}")
    print(f"   Status: {account_info['account_status']}")
    print(f"   Currency: {account_info['currency']}")
    print(f"   Timezone: {account_info['timezone_name']}")
    if account_info['business_id']:
        print(f"   Business ID: {account_info['business_id']}")

    # Save to database
    print(f"\n💾 Saving to database...")
    save_account_to_db(config, account_info)

    # Success message
    print("\n" + "=" * 70)
    print("✅ SETUP COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print(f"\n📝 Next Steps:")
    print(f"   1. Run ETL pipeline: python meta_ads_etl.py")
    print(f"   2. Start API server: cd api && uvicorn app.main:app --reload")
    print(f"   3. Test endpoint: http://localhost:8000/api/v1/meta/integration/status?customer_id={config['customer_id']}")
    print(f"   4. View docs: http://localhost:8000/docs")
    print()


if __name__ == "__main__":
    main()
