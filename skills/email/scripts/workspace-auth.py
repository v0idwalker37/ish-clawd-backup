#!/usr/bin/env python3
"""
OAuth flow for Google Workspace (void@ungouge.ai)
Run this interactively to authorize and save token.
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, '..', 'workspace-config.json')
TOKEN_PATH = os.path.join(SCRIPT_DIR, '..', 'workspace-token.json')

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    # Load client credentials from config
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    
    gmail_config = config['gmail']
    
    # Create credentials dict in the format google expects
    client_config = {
        "installed": {
            "client_id": gmail_config['client_id'],
            "client_secret": gmail_config['client_secret'],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8080/"]
        }
    }
    
    print("=" * 50)
    print("Google Workspace OAuth Authorization")
    print("=" * 50)
    print()
    print("IMPORTANT: When the browser opens, sign in as:")
    print("  → void@ungouge.ai")
    print()
    
    # Run the OAuth flow
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=8080)
    
    # Save the token
    with open(TOKEN_PATH, 'w') as f:
        f.write(creds.to_json())
    
    print()
    print("=" * 50)
    print(f"✅ Token saved to: {TOKEN_PATH}")
    print("=" * 50)

if __name__ == '__main__':
    main()
