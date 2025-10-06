#!/usr/bin/env python3
"""
Simple script to get Google Ads API refresh token
"""

import webbrowser
from urllib.parse import urlencode

# Your OAuth2 credentials
CLIENT_ID = "27301795624-e2iccuor7ba1shjmrt87b58f0iitf2rv.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"  # For manual copy-paste

print("\n" + "="*70)
print(" GOOGLE ADS API - REFRESH TOKEN GENERATOR ")
print("="*70)
print("\nFollow these steps to get your refresh token:\n")

# Step 1: Generate authorization URL
auth_params = {
    'client_id': CLIENT_ID,
    'redirect_uri': REDIRECT_URI,
    'scope': 'https://www.googleapis.com/auth/adwords',
    'response_type': 'code',
    'access_type': 'offline',
    'prompt': 'consent'
}

auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(auth_params)}"

print("STEP 1: Open this URL in your browser:")
print("-" * 70)
print(auth_url)
print("-" * 70)

# Try to open browser
try:
    webbrowser.open(auth_url)
    print("\n✓ Browser opened automatically")
except:
    print("\n! Please copy and paste the URL above into your browser")

print("\nSTEP 2: Sign in with the Google account that has access to")
print("        Google Ads account: 3341907700")

print("\nSTEP 3: After authorizing, you'll see an authorization code.")
print("        Copy that code and paste it below:\n")

auth_code = input("Enter authorization code: ").strip()

if auth_code:
    print("\nSTEP 4: Exchanging code for refresh token...")

    # Create the curl command to exchange code for token
    import requests

    token_params = {
        'code': auth_code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }

    try:
        response = requests.post('https://oauth2.googleapis.com/token', data=token_params)
        token_data = response.json()

        if 'refresh_token' in token_data:
            refresh_token = token_data['refresh_token']

            print("\n" + "="*70)
            print(" SUCCESS! Your new refresh token is: ")
            print("="*70)
            print(f"\n{refresh_token}\n")
            print("="*70)

            # Update google-ads.yaml
            print("\nUpdating google-ads.yaml...")
            yaml_content = f"""developer_token: ouYOcEpDiQOJCTs-Rkc1mA
client_id: {CLIENT_ID}
client_secret: {CLIENT_SECRET}
refresh_token: {refresh_token}
login_customer_id: 3341907700
"""
            with open('google-ads.yaml', 'w') as f:
                f.write(yaml_content)
            print("✓ google-ads.yaml updated")

            # Update .env file
            print("\nUpdating .env file...")
            env_lines = []
            updated = False

            try:
                with open('.env', 'r') as f:
                    for line in f:
                        if line.startswith('GOOGLE_ADS_REFRESH_TOKEN='):
                            env_lines.append(f'GOOGLE_ADS_REFRESH_TOKEN={refresh_token}\n')
                            updated = True
                        else:
                            env_lines.append(line)

                if not updated:
                    env_lines.append(f'GOOGLE_ADS_REFRESH_TOKEN={refresh_token}\n')

                with open('.env', 'w') as f:
                    f.writelines(env_lines)

            except FileNotFoundError:
                with open('.env', 'w') as f:
                    f.write(f'GOOGLE_ADS_REFRESH_TOKEN={refresh_token}\n')

            print("✓ .env file updated")
            print("\n✅ ALL DONE! You can now run: python google_ads_etl_pipeline.py")

        else:
            print("\n✗ Error getting refresh token:")
            print(token_data)
            if 'error' in token_data:
                print(f"\nError: {token_data['error']}")
                print(f"Description: {token_data.get('error_description', 'N/A')}")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTry running this command manually:")
        print(f"\ncurl -X POST https://oauth2.googleapis.com/token \\")
        print(f"  -d 'code={auth_code}' \\")
        print(f"  -d 'client_id={CLIENT_ID}' \\")
        print(f"  -d 'client_secret={CLIENT_SECRET}' \\")
        print(f"  -d 'redirect_uri={REDIRECT_URI}' \\")
        print(f"  -d 'grant_type=authorization_code'")
else:
    print("\n✗ No authorization code provided. Please try again.")