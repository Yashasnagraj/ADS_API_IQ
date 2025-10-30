"""
Generate Meta (Facebook) Access Token

This script helps you generate a new long-lived access token for Meta Marketing API.

Steps:
1. Go to Meta Graph API Explorer: https://developers.facebook.com/tools/explorer/
2. Select your app from dropdown
3. Add permissions: ads_read, ads_management, read_insights
4. Click "Generate Access Token"
5. Copy the SHORT-LIVED token
6. Run this script with that token to get a LONG-LIVED token

Usage:
    python generate_meta_token.py
"""

import sys
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')


def load_config():
    """Load Meta app credentials"""
    env_path = Path(__file__).parent / '.env.meta'

    if not env_path.exists():
        print("❌ .env.meta not found")
        return None

    load_dotenv(env_path)

    return {
        'app_id': os.getenv('META_APP_ID'),
        'app_secret': os.getenv('META_APP_SECRET'),
        'ad_account_id': os.getenv('META_AD_ACCOUNT_ID')
    }


def exchange_token(short_token, app_id, app_secret):
    """Exchange short-lived token for long-lived token"""

    print("\n🔄 Exchanging token for long-lived version...")

    url = "https://graph.facebook.com/v19.0/oauth/access_token"
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': app_id,
        'client_secret': app_secret,
        'fb_exchange_token': short_token
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if 'access_token' in data:
            long_token = data['access_token']
            expires_in = data.get('expires_in', 'Unknown')

            print(f"✅ Got long-lived token!")
            print(f"   Expires in: {expires_in} seconds (~{int(expires_in)//86400} days)")

            return long_token
        else:
            print(f"❌ Error: {data.get('error', {}).get('message', 'Unknown error')}")
            return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_token(token, ad_account_id):
    """Test the token by fetching account info"""

    print("\n🧪 Testing token...")

    url = f"https://graph.facebook.com/v19.0/{ad_account_id}"
    params = {
        'fields': 'id,name,account_status,currency,timezone_name',
        'access_token': token
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if 'error' in data:
            print(f"❌ Token test failed: {data['error']['message']}")
            return False

        print(f"✅ Token works!")
        print(f"   Account: {data.get('name', 'N/A')}")
        print(f"   Status: {data.get('account_status', 'N/A')}")
        print(f"   Currency: {data.get('currency', 'N/A')}")

        return True

    except Exception as e:
        print(f"❌ Error testing token: {e}")
        return False


def update_env_file(token):
    """Update .env.meta with new token"""

    env_path = Path(__file__).parent / '.env.meta'

    try:
        with open(env_path, 'r') as f:
            lines = f.readlines()

        with open(env_path, 'w') as f:
            for line in lines:
                if line.startswith('META_ACCESS_TOKEN='):
                    f.write(f'META_ACCESS_TOKEN={token}\n')
                else:
                    f.write(line)

        print(f"\n✅ Updated .env.meta with new token")
        return True

    except Exception as e:
        print(f"❌ Error updating file: {e}")
        return False


def main():
    print("=" * 70)
    print("META ACCESS TOKEN GENERATOR")
    print("=" * 70)

    # Load config
    config = load_config()

    if not config or not all(config.values()):
        print("\n❌ Error loading configuration from .env.meta")
        return

    print(f"\n📱 App ID: {config['app_id']}")
    print(f"📊 Ad Account: {config['ad_account_id']}")

    print("\n" + "=" * 70)
    print("STEP 1: Get Short-Lived Token from Graph API Explorer")
    print("=" * 70)
    print("\n1. Go to: https://developers.facebook.com/tools/explorer/")
    print(f"2. Select your app: {config['app_id']}")
    print("3. Add these permissions:")
    print("   ✓ ads_read")
    print("   ✓ ads_management")
    print("   ✓ read_insights")
    print("4. Click 'Generate Access Token'")
    print("5. Authorize the permissions")
    print("6. Copy the generated token")

    print("\n" + "=" * 70)

    # Get short-lived token from user
    print("\nPaste your SHORT-LIVED token here:")
    short_token = input("> ").strip()

    if not short_token:
        print("❌ No token provided")
        return

    # Exchange for long-lived token
    long_token = exchange_token(short_token, config['app_id'], config['app_secret'])

    if not long_token:
        print("\n❌ Failed to exchange token")
        return

    # Test the token
    if not test_token(long_token, config['ad_account_id']):
        print("\n❌ Token test failed")
        return

    # Update .env.meta
    if update_env_file(long_token):
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Token updated")
        print("=" * 70)
        print("\nYou can now run:")
        print("   python warehouse_meta_ads_etl.py --days=30")
        print("=" * 70)
    else:
        print("\n⚠️  Token works but couldn't update file")
        print(f"   Please manually update META_ACCESS_TOKEN in .env.meta")
        print(f"\n   New token: {long_token}")


if __name__ == "__main__":
    main()
