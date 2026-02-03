#!/usr/bin/env python3
"""
Gmail OAuth2 authentication flow.
Generates a token file for API access.
"""

import json
import os
import sys
from pathlib import Path

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("ERROR: Missing required packages. Installing...")
    os.system("pip3 install --user google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    print("\nPackages installed. Please run this script again.")
    sys.exit(1)

SKILL_DIR = Path(__file__).parent.parent
CONFIG_FILE = SKILL_DIR / "config.json"
TOKEN_FILE = SKILL_DIR / "token.json"

def main():
    # Load config
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    
    gmail_config = config['gmail']
    
    creds = None
    
    # Check if token already exists
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), gmail_config['scopes'])
    
    # If no valid credentials, get them
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("Starting OAuth2 flow...")
            print("\nA browser window will open for you to authorize access.")
            print("Sign in with: jasontrask@gmail.com")
            
            # Create client config for OAuth flow
            client_config = {
                "installed": {
                    "client_id": gmail_config['client_id'],
                    "client_secret": gmail_config['client_secret'],
                    "redirect_uris": ["http://localhost"],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            }
            
            flow = InstalledAppFlow.from_client_config(
                client_config,
                gmail_config['scopes']
            )
            
            creds = flow.run_local_server(port=0)
        
        # Save credentials
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        
        print(f"\n✅ Authentication successful!")
        print(f"Token saved to: {TOKEN_FILE}")
    
    # Test the connection
    print("\nTesting Gmail API access...")
    service = build('gmail', 'v1', credentials=creds)
    profile = service.users().getProfile(userId='me').execute()
    
    print(f"✅ Connected to Gmail!")
    print(f"   Email: {profile['emailAddress']}")
    print(f"   Total messages: {profile['messagesTotal']}")
    print(f"   Threads: {profile['threadsTotal']}")

if __name__ == '__main__':
    main()
