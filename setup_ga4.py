"""
Google Analytics 4 (GA4) Setup and Validation Script

This script:
1. Validates GA4 credentials (service account JSON key)
2. Tests connection to GA4 property
3. Fetches property metadata
4. Creates GA4Property record in database
5. Verifies API access and permissions

Usage:
    python setup_ga4.py

Requirements:
    - .env.ga4 file with GA4_PROPERTY_ID, GA4_CREDENTIALS_PATH, CUSTOMER_ID
    - Service account JSON key file
    - Service account must have "Viewer" access to GA4 property
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest
from google.oauth2 import service_account
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from api.app.db.database import SessionLocal, engine
from api.app.db import models

# Create all tables
models.Base.metadata.create_all(bind=engine)


def load_config():
    """Load configuration from .env.ga4"""
    env_path = Path(__file__).parent / '.env.ga4'

    if not env_path.exists():
        print("\n❌ ERROR: .env.ga4 file not found!")
        print(f"   Expected location: {env_path}")
        print("\n📝 Please create .env.ga4 with the following content:")
        print("=" * 70)
        print("# GA4 Property ID (from Google Analytics)")
        print("GA4_PROPERTY_ID=123456789")
        print()
        print("# Path to service account JSON key file")
        print("GA4_CREDENTIALS_PATH=D:\\ADS_API\\credentials\\ga4-service-account.json")
        print()
        print("# Your internal customer ID")
        print("CUSTOMER_ID=1")
        print("=" * 70)
        sys.exit(1)

    load_dotenv(env_path)

    property_id = os.getenv('GA4_PROPERTY_ID')
    credentials_path = os.getenv('GA4_CREDENTIALS_PATH')
    customer_id = os.getenv('CUSTOMER_ID')

    # Validate required fields
    if not property_id:
        print("❌ ERROR: GA4_PROPERTY_ID not found in .env.ga4")
        sys.exit(1)

    if not credentials_path:
        print("❌ ERROR: GA4_CREDENTIALS_PATH not found in .env.ga4")
        sys.exit(1)

    if not customer_id:
        print("❌ ERROR: CUSTOMER_ID not found in .env.ga4")
        sys.exit(1)

    # Check if credentials file exists
    if not os.path.exists(credentials_path):
        print(f"\n❌ ERROR: Credentials file not found!")
        print(f"   Expected location: {credentials_path}")
        print("\n📝 Please:")
        print("   1. Download the service account JSON key from Google Cloud Console")
        print(f"   2. Place it at: {credentials_path}")
        sys.exit(1)

    return {
        'property_id': property_id,
        'credentials_path': credentials_path,
        'customer_id': int(customer_id)
    }


def create_ga4_client(credentials_path):
    """Create GA4 Analytics Data API client"""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )

        client = BetaAnalyticsDataClient(credentials=credentials)
        return client, credentials
    except Exception as e:
        print(f"\n❌ ERROR: Failed to create GA4 client")
        print(f"   Reason: {str(e)}")
        print("\n📝 Please check:")
        print("   1. The JSON key file is valid and not corrupted")
        print("   2. The service account has proper permissions")
        sys.exit(1)


def validate_ga4_access(client, property_id):
    """Validate access to GA4 property by running a simple query"""
    try:
        # Run a simple report to test access
        request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[{"start_date": "yesterday", "end_date": "yesterday"}],
            metrics=[{"name": "sessions"}],
            dimensions=[{"name": "date"}]
        )

        response = client.run_report(request)

        # Get property metadata from response
        property_info = {
            'property_id': property_id,
            'property_name': f"GA4 Property {property_id}",  # Default name
            'currency_code': response.property_quota.tokens_per_hour if hasattr(response, 'property_quota') else 'USD'
        }

        return True, property_info

    except Exception as e:
        error_msg = str(e)

        if "PERMISSION_DENIED" in error_msg or "403" in error_msg:
            print("\n❌ ERROR: Permission Denied")
            print("   The service account does not have access to this GA4 property.")
            print("\n📝 To fix this:")
            print("   1. Go to https://analytics.google.com")
            print("   2. Click 'Admin' → 'Property Access Management'")
            print("   3. Click '+' → 'Add users'")
            print("   4. Add your service account email with 'Viewer' role")
            print("   5. Wait 5-10 minutes for changes to propagate")

        elif "NOT_FOUND" in error_msg or "404" in error_msg:
            print("\n❌ ERROR: Property Not Found")
            print(f"   GA4 Property ID '{property_id}' does not exist or is not accessible.")
            print("\n📝 Please check:")
            print("   1. The Property ID is correct")
            print("   2. You're using a GA4 property (not Universal Analytics)")
            print("   3. The property exists and is active")

        else:
            print(f"\n❌ ERROR: Failed to access GA4 property")
            print(f"   Reason: {error_msg}")

        return False, None


def save_to_database(config, credentials, property_info):
    """Save GA4 property connection to database"""
    db = SessionLocal()
    try:
        # Check if customer exists
        customer = db.query(models.Customer).filter(
            models.Customer.customer_id == config['customer_id']
        ).first()

        if not customer:
            print(f"\n⚠️  WARNING: Customer ID {config['customer_id']} not found in database")
            print("   Creating a default customer record...")

            customer = models.Customer(
                customer_id=config['customer_id'],
                customer_name=f"Customer {config['customer_id']}",
                descriptive_name="Default Customer",
                status="ENABLED"
            )
            db.add(customer)
            db.commit()
            print(f"   ✅ Customer {config['customer_id']} created")

        # Check if GA4 property already exists
        existing = db.query(models.GA4Property).filter(
            models.GA4Property.property_id == config['property_id']
        ).first()

        # Load service account email from JSON
        with open(config['credentials_path'], 'r') as f:
            sa_data = json.load(f)
            service_account_email = sa_data.get('client_email', 'unknown')

        if existing:
            print(f"\n📝 Updating existing GA4 property record...")
            existing.property_name = property_info['property_name']
            existing.customer_id = config['customer_id']
            existing.service_account_email = service_account_email
            existing.credentials_path = config['credentials_path']
            existing.is_active = True
            existing.last_sync_at = None  # Reset sync timestamp
            db.commit()
            print("   ✅ GA4 property record updated")
        else:
            print(f"\n📝 Creating new GA4 property record...")
            ga4_property = models.GA4Property(
                property_id=config['property_id'],
                customer_id=config['customer_id'],
                property_name=property_info['property_name'],
                display_name=property_info['property_name'],
                service_account_email=service_account_email,
                credentials_path=config['credentials_path'],
                currency_code='USD',
                is_active=True
            )
            db.add(ga4_property)
            db.commit()
            print("   ✅ GA4 property record created")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: Failed to save to database")
        print(f"   Reason: {str(e)}")
        return False

    finally:
        db.close()


def main():
    """Main setup flow"""
    print("=" * 70)
    print("GOOGLE ANALYTICS 4 SETUP")
    print("=" * 70)

    # Step 1: Load configuration
    print("\n📋 Step 1: Loading configuration...")
    config = load_config()
    print(f"   Property ID: {config['property_id']}")
    print(f"   Credentials: {config['credentials_path']}")
    print(f"   Customer ID: {config['customer_id']}")
    print("   ✅ Configuration loaded")

    # Step 2: Create GA4 client
    print("\n🔐 Step 2: Authenticating with GA4...")
    client, credentials = create_ga4_client(config['credentials_path'])

    # Load service account info
    with open(config['credentials_path'], 'r') as f:
        sa_data = json.load(f)
        service_account_email = sa_data.get('client_email', 'unknown')

    print(f"   Service Account: {service_account_email}")
    print("   ✅ Authentication successful")

    # Step 3: Validate GA4 access
    print("\n🔍 Step 3: Validating GA4 property access...")
    success, property_info = validate_ga4_access(client, config['property_id'])

    if not success:
        sys.exit(1)

    print(f"   ✅ Successfully connected to GA4 Property")
    print(f"   Property Name: {property_info['property_name']}")

    # Step 4: Save to database
    print("\n💾 Step 4: Saving connection to database...")
    if not save_to_database(config, credentials, property_info):
        sys.exit(1)

    # Success!
    print("\n" + "=" * 70)
    print("✅ GA4 SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print(f"\n📊 GA4 Property Connected:")
    print(f"   Property ID: {config['property_id']}")
    print(f"   Property Name: {property_info['property_name']}")
    print(f"   Customer ID: {config['customer_id']}")
    print(f"   Service Account: {service_account_email}")

    print("\n📝 Next Steps:")
    print("   1. Run ETL to extract GA4 data:")
    print("      python ga4_etl.py")
    print()
    print("   2. Start the API server:")
    print("      cd api && uvicorn app.main:app --reload")
    print()
    print("   3. View API docs:")
    print("      http://localhost:8000/docs")
    print()


if __name__ == "__main__":
    main()
