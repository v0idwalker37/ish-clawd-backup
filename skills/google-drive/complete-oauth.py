#!/usr/bin/env python3
"""Complete OAuth flow and save Drive API token"""
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import json
import os

# Load credentials
with open('/Users/moltbot/clawd/skills/google-drive/credentials.json', 'r') as f:
    CLIENT_CONFIG = json.load(f)

SCOPES = ['https://www.googleapis.com/auth/drive.file']

# The callback URL from Jason
auth_response = "http://localhost:8080/?state=Q3QERZZy3cy5jraqHgbhmxrkVDtePi&code=4/0ASc3gC3iIXCfOtqlA3BxjNdwlIGJ7ttQpKShVl7fPfDP1xV8JJa93hMzS1NQN8URPuy8nQ&scope=https://www.googleapis.com/auth/drive.file"

# Create flow
flow = Flow.from_client_config(CLIENT_CONFIG, scopes=SCOPES)
flow.redirect_uri = 'http://localhost:8080/'

# Exchange code for token
print("🔄 Exchanging authorization code for access token...")
flow.fetch_token(authorization_response=auth_response)

creds = flow.credentials

# Save token
token_path = '/Users/moltbot/clawd/skills/google-drive/token.json'
with open(token_path, 'w') as token:
    token.write(creds.to_json())

print(f"✅ Token saved to {token_path}")

# Test the connection
try:
    service = build('drive', 'v3', credentials=creds)
    about = service.about().get(fields="user").execute()
    print(f"✅ Successfully authorized as: {about['user']['emailAddress']}")
    print(f"✅ Drive API is ready!")
except Exception as e:
    print(f"❌ Test failed: {e}")
