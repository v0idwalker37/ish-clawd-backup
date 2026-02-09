#!/usr/bin/env python3
"""Complete full Drive OAuth flow"""
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import json

# Load credentials
with open('/Users/moltbot/clawd/skills/google-drive/credentials.json', 'r') as f:
    CLIENT_CONFIG = json.load(f)

SCOPES = ['https://www.googleapis.com/auth/drive']

# The callback URL from Jason
auth_response = "http://localhost:8080/?state=mbt5vyOZhtTxJSumKcTImayjB8WyR9&code=4/0ASc3gC01ZXZAJtb1qFhAv9RIcmDge7_5jn1_e3JPAg4HFHre5LcsosmFDlPXHrESKxxGdA&scope=https://www.googleapis.com/auth/drive%20https://www.googleapis.com/auth/drive.file"

# Create flow
flow = Flow.from_client_config(CLIENT_CONFIG, scopes=SCOPES)
flow.redirect_uri = 'http://localhost:8080/'

# Exchange code for token
print("🔄 Exchanging authorization code for full Drive access...")
flow.fetch_token(authorization_response=auth_response)

creds = flow.credentials

# Save token (overwrite previous limited one)
token_path = '/Users/moltbot/clawd/skills/google-drive/token.json'
with open(token_path, 'w') as token:
    token.write(creds.to_json())

print(f"✅ Full Drive token saved to {token_path}")

# Test the connection
try:
    service = build('drive', 'v3', credentials=creds)
    about = service.about().get(fields="user").execute()
    print(f"✅ Authorized as: {about['user']['emailAddress']}")
    
    # Test shared drive access
    drives = service.drives().list().execute()
    print(f"✅ Can access {len(drives.get('drives', []))} shared drives")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
