"""
Simple Google Ads Refresh Token Generator

Run this in your terminal (not as background task).
It will open a browser for you to authorize.

Usage:
    python get_refresh_token_simple.py
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

# OAuth2 scope
SCOPES = ['https://www.googleapis.com/auth/adwords']

client_id = os.getenv('GOOGLE_ADS_CLIENT_ID')
client_secret = os.getenv('GOOGLE_ADS_CLIENT_SECRET')

print("=" * 70)
print("GOOGLE ADS - REFRESH TOKEN GENERATOR")
print("=" * 70)
print("\nA browser will open in 3 seconds...")
print("Please sign in and authorize access.")
print("\n" + "=" * 70 + "\n")

# Create client config
client_config = {
    "installed": {
        "client_id": client_id,
        "client_secret": client_secret,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost"]
    }
}

try:
    # Run OAuth2 flow - this will open browser automatically
    flow = InstalledAppFlow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri='http://localhost'
    )

    credentials = flow.run_local_server(
        port=8080,
        prompt='consent',
        success_message='✅ Authorization successful! You can close this window and return to the terminal.'
    )

    refresh_token = credentials.refresh_token

    print("\n" + "=" * 70)
    print("✅ SUCCESS!")
    print("=" * 70)
    print(f"\nYour new GOOGLE_ADS_REFRESH_TOKEN:\n")
    print(f"{refresh_token}\n")
    print("=" * 70)
    print("\nNext: Update your .env file with this token")
    print("=" * 70)

    # Auto-update .env
    try:
        with open(env_path, 'r') as f:
            content = f.read()

        # Replace the token
        if 'GOOGLE_ADS_REFRESH_TOKEN=' in content:
            import re
            content = re.sub(
                r'GOOGLE_ADS_REFRESH_TOKEN=.*',
                f'GOOGLE_ADS_REFRESH_TOKEN={refresh_token}',
                content
            )

            with open(env_path, 'w') as f:
                f.write(content)

            print("\n✅ Auto-updated .env file!")
        else:
            print("\n⚠️  Please add this line to your .env file:")
            print(f"   GOOGLE_ADS_REFRESH_TOKEN={refresh_token}")

    except Exception as e:
        print(f"\n⚠️  Could not auto-update .env: {e}")
        print("   Please update manually")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
