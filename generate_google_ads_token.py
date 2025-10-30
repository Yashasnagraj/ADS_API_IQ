"""
Generate Google Ads API Refresh Token

This script helps you generate a new refresh token for Google Ads API.

Usage:
    python generate_google_ads_token.py
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# OAuth2 scope for Google Ads API
SCOPES = ['https://www.googleapis.com/auth/adwords']

def generate_refresh_token():
    """Generate refresh token using OAuth2 flow"""

    client_id = os.getenv('GOOGLE_ADS_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_ADS_CLIENT_SECRET')

    if not client_id or not client_secret:
        print("❌ ERROR: GOOGLE_ADS_CLIENT_ID or GOOGLE_ADS_CLIENT_SECRET not found in .env")
        return

    print("=" * 70)
    print("GOOGLE ADS API - REFRESH TOKEN GENERATOR")
    print("=" * 70)
    print(f"\n📋 Configuration:")
    print(f"   Client ID: {client_id}")
    print(f"   Client Secret: {'*' * len(client_secret)}")

    # Create OAuth2 credentials
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"]
        }
    }

    print("\n🔐 Starting OAuth2 flow...")
    print("\n⚠️  IMPORTANT:")
    print("   1. A browser window will open")
    print("   2. Sign in with your Google Ads account")
    print("   3. Grant access to the application")
    print("   4. You'll be redirected to localhost (may show error - that's OK)")
    print("   5. Copy the FULL URL from the browser address bar")
    print("\nPress Enter to continue...")
    input()

    try:
        # Run OAuth2 flow
        flow = InstalledAppFlow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri='http://localhost'
        )

        # This will open a browser for authorization
        credentials = flow.run_local_server(
            port=8080,
            prompt='consent',
            success_message='Authorization successful! You can close this window.'
        )

        refresh_token = credentials.refresh_token

        print("\n" + "=" * 70)
        print("✅ SUCCESS! Refresh Token Generated")
        print("=" * 70)
        print(f"\n🔑 Your new refresh token:")
        print(f"\n   {refresh_token}\n")

        print("📝 Next steps:")
        print("   1. Copy the refresh token above")
        print("   2. Update your .env file:")
        print(f"      GOOGLE_ADS_REFRESH_TOKEN={refresh_token}")
        print("   3. Update your google-ads.yaml file with the same token")
        print("\n" + "=" * 70)

        # Option to auto-update .env
        update = input("\n❓ Do you want to auto-update .env file? (yes/no): ").lower()

        if update == 'yes' or update == 'y':
            # Read current .env
            with open(env_path, 'r') as f:
                lines = f.readlines()

            # Update refresh token line
            updated = False
            for i, line in enumerate(lines):
                if line.startswith('GOOGLE_ADS_REFRESH_TOKEN='):
                    lines[i] = f'GOOGLE_ADS_REFRESH_TOKEN={refresh_token}\n'
                    updated = True
                    break

            # Write back
            if updated:
                with open(env_path, 'w') as f:
                    f.writelines(lines)
                print("✅ Updated .env file successfully!")
            else:
                print("⚠️  Could not find GOOGLE_ADS_REFRESH_TOKEN in .env")
                print("   Please add it manually")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    generate_refresh_token()
