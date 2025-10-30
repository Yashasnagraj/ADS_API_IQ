"""
Generate a new Google Ads API refresh token
Run this script and follow the prompts
"""
from google_auth_oauthlib.flow import InstalledAppFlow
import os
from dotenv import load_dotenv

# Load current credentials
load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_ADS_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_ADS_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    print("[ERROR] GOOGLE_ADS_CLIENT_ID and GOOGLE_ADS_CLIENT_SECRET must be set in .env")
    exit(1)

# Google Ads API scope
SCOPES = ['https://www.googleapis.com/auth/adwords']

# Create OAuth2 flow
flow = InstalledAppFlow.from_client_config(
    client_config={
        "installed": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8080/"]
        }
    },
    scopes=SCOPES
)

print("\n" + "="*60)
print("Google Ads API - Refresh Token Generator")
print("="*60)
print("\n[INFO] This will open your browser for authentication.")
print("[INFO] Sign in with your Google Ads account.")
print("[INFO] Grant permissions when prompted.\n")

# Run the OAuth flow
credentials = flow.run_local_server(
    port=8080,
    prompt='consent',
    success_message='Authorization successful! You can close this window.'
)

# Display the refresh token
print("\n" + "="*60)
print("[SUCCESS] Refresh token generated successfully!")
print("="*60)
print(f"\nYour new refresh token:\n{credentials.refresh_token}\n")
print("="*60)
print("\n[ACTION REQUIRED] Update your .env file:")
print(f"\nGOOGLE_ADS_REFRESH_TOKEN={credentials.refresh_token}\n")
print("="*60)
