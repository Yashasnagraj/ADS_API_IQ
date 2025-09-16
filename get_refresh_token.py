#!/usr/bin/env python3
"""
Script to obtain a refresh token for Google Ads API.
Follow the instructions to authenticate and get your refresh token.
"""

import sys
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request

CLIENT_ID = "27301795624-e2iccuor7ba1shjmrt87b58f0iitf2rv.apps.googleusercontent.com"
CLIENT_SECRET = "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"

SCOPES = ["https://www.googleapis.com/auth/adwords"]

def main():
    """Generate a refresh token for Google Ads API access."""

    print("Google Ads API - Refresh Token Generator")
    print("=" * 50)

    # Create the flow using the client secrets
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

    # Set the redirect URI
    flow.redirect_uri = "http://localhost:8080"

    # Generate the authorization URL
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",
    )

    print("\n1. Open this URL in your browser:")
    print(f"\n{auth_url}\n")
    print("2. Authorize the application")
    print("3. You'll be redirected to localhost:8080")
    print("4. Copy the entire URL from your browser's address bar")
    print("5. Paste it here and press Enter:\n")

    # Get the authorization response URL from the user
    auth_response = input("Paste the full redirect URL here: ").strip()

    try:
        # Exchange the authorization code for tokens
        flow.fetch_token(authorization_response=auth_response)

        # Get the refresh token
        refresh_token = flow.credentials.refresh_token

        if refresh_token:
            print("\n" + "=" * 50)
            print("SUCCESS! Your refresh token is:")
            print("\n" + refresh_token)
            print("\n" + "=" * 50)
            print("\nTo use this token:")
            print("1. Open google-ads.yaml")
            print("2. Replace 'PASTE_REFRESH_TOKEN_HERE' with the token above")
            print("3. Save the file")
            print("\nYour google-ads.yaml should look like:")
            print(f"""
developer_token: ouYOcEpDiQOJCTs-Rkc1mA
client_id: {CLIENT_ID}
client_secret: {CLIENT_SECRET}
refresh_token: {refresh_token}
use_proto_plus: True
""")
        else:
            print("\nError: No refresh token received.")
            print("Make sure you included 'access_type=offline' in the request.")

    except Exception as e:
        print(f"\nError obtaining refresh token: {e}")
        print("\nMake sure you:")
        print("1. Copied the ENTIRE URL from your browser")
        print("2. Included everything after 'http://localhost:8080'")
        sys.exit(1)

if __name__ == "__main__":
    main()