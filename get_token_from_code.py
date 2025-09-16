#!/usr/bin/env python3
"""
Extract refresh token from authorization code.
"""

import requests
import sys

CLIENT_ID = "27301795624-e2iccuor7ba1shjmrt87b58f0iitf2rv.apps.googleusercontent.com"
CLIENT_SECRET = "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"

def main():
    print("Google Ads API - Get Refresh Token from Authorization Code")
    print("=" * 60)

    print("\nPaste the authorization code from the URL (the part after 'code=')")
    print("Example: If URL is http://localhost:8080/?code=4/0AX4XfWi...&scope=...")
    print("Then paste: 4/0AX4XfWi...")

    auth_code = input("\nEnter authorization code: ").strip()

    # Remove any trailing parameters if user pasted too much
    if '&' in auth_code:
        auth_code = auth_code.split('&')[0]

    # Exchange authorization code for tokens
    token_url = "https://oauth2.googleapis.com/token"

    data = {
        'code': auth_code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': 'http://localhost:8080',
        'grant_type': 'authorization_code'
    }

    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()

        tokens = response.json()

        if 'refresh_token' in tokens:
            refresh_token = tokens['refresh_token']
            print("\n" + "=" * 60)
            print("SUCCESS! Your refresh token is:")
            print("\n" + refresh_token)
            print("\n" + "=" * 60)
            print("\nNow update your google-ads.yaml file:")
            print(f"""
developer_token: ouYOcEpDiQOJCTs-Rkc1mA
client_id: {CLIENT_ID}
client_secret: {CLIENT_SECRET}
refresh_token: {refresh_token}
use_proto_plus: True
""")
        else:
            print("\nNo refresh token in response. Tokens received:")
            print(tokens)

    except requests.exceptions.RequestException as e:
        print(f"\nError exchanging code for tokens: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    main()