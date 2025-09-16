#!/usr/bin/env python3
"""
Generate OAuth2 refresh token for Google Ads API.
This script will open a browser for authentication and return a refresh token.
"""

import json
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

# Google Ads API OAuth2 scope
SCOPES = ['https://www.googleapis.com/auth/adwords']

def main():
    """Generate and display refresh token for Google Ads API."""
    
    # Path to the OAuth client secret JSON file
    client_secrets_file = './oauth_client.json'
    
    try:
        # Load client secrets
        with open(client_secrets_file, 'r') as f:
            client_config = json.load(f)
        
        # Create flow from client secrets
        flow = InstalledAppFlow.from_client_config(
            client_config,
            scopes=SCOPES
        )
        
        try:
            # Try to run local server for OAuth flow (opens browser automatically)
            print("Opening browser for authentication...")
            print("If the browser doesn't open automatically, please visit the URL shown below.")
            credentials = flow.run_local_server(
                port=8080,
                success_message='Authentication successful! You can close this window.',
                open_browser=True
            )
        except Exception as e:
            # Fallback to console flow if local server fails
            print(f"\nLocal server failed: {e}")
            print("Falling back to console authentication flow...")
            credentials = flow.run_console()
        
        # Display the refresh token
        print("\n" + "="*60)
        print("SUCCESS! Your refresh token is:")
        print("="*60)
        print(credentials.refresh_token)
        print("="*60)
        print("\nPaste this refresh token into your google-ads.yaml file.")
        print("Keep this token secure and do not share it.")
        
    except FileNotFoundError:
        print(f"Error: Could not find {client_secrets_file}")
        print("Please ensure you have downloaded the OAuth client secret JSON from Google Cloud Console")
        print("and saved it as 'oauth_client.json' in the current directory.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()