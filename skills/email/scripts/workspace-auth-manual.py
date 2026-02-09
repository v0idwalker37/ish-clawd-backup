#!/usr/bin/env python3
"""
Manual OAuth flow for Google Workspace - works from any device.
Prints a URL, you paste back the code.
"""

import os
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, '..', 'workspace-config.json')
TOKEN_PATH = os.path.join(SCRIPT_DIR, '..', 'workspace-token.json')

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
REDIRECT_URI = 'http://localhost:8080/'

def main():
    # Load client credentials from config
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    
    gmail_config = config['gmail']
    
    # Create credentials dict
    client_config = {
        "installed": {
            "client_id": gmail_config['client_id'],
            "client_secret": gmail_config['client_secret'],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI]
        }
    }
    
    # Create flow
    flow = Flow.from_client_config(client_config, scopes=SCOPES, redirect_uri=REDIRECT_URI)
    
    # Generate auth URL
    auth_url, _ = flow.authorization_url(prompt='consent')
    
    print("=" * 60)
    print("Google Workspace OAuth - Manual Flow")
    print("=" * 60)
    print()
    print("1. Open this URL in your browser:")
    print()
    print(auth_url)
    print()
    print("2. Sign in as: void@ungouge.ai")
    print()
    print("3. After approving, you'll be redirected to localhost")
    print("   (the page won't load - that's OK)")
    print()
    print("4. Copy the FULL URL from your browser's address bar")
    print("   It will look like: http://localhost:8080/?code=4/xxx...&scope=...")
    print()
    
    redirect_response = input("Paste the full redirect URL here: ").strip()
    
    # Extract the authorization response
    flow.fetch_token(authorization_response=redirect_response)
    creds = flow.credentials
    
    # Save the token
    with open(TOKEN_PATH, 'w') as f:
        f.write(creds.to_json())
    
    print()
    print("=" * 60)
    print(f"✅ Success! Token saved.")
    print("=" * 60)

if __name__ == '__main__':
    main()
