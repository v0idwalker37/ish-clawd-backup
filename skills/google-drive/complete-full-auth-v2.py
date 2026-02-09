#!/usr/bin/env python3
"""Complete full Drive OAuth flow - fixed"""
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import json
import urllib.parse

# Load credentials
with open('/Users/moltbot/clawd/skills/google-drive/credentials.json', 'r') as f:
    CLIENT_CONFIG = json.load(f)

# Extract just the code from URL
code = "4/0ASc3gC01ZXZAJtb1qFhAv9RIcmDge7_5jn1_e3JPAg4HFHre5LcsosmFDlPXHrESKxxGdA"

SCOPES = ['https://www.googleapis.com/auth/drive']

# Create flow
flow = Flow.from_client_config(CLIENT_CONFIG, scopes=SCOPES)
flow.redirect_uri = 'http://localhost:8080/'

# Fetch token using just the code
print("🔄 Exchanging authorization code...")
flow.fetch_token(code=code)

creds = flow.credentials

# Save token
token_path = '/Users/moltbot/clawd/skills/google-drive/token.json'
with open(token_path, 'w') as token:
    token.write(creds.to_json())

print(f"✅ Full Drive token saved")

# Test
service = build('drive', 'v3', credentials=creds)
about = service.about().get(fields="user").execute()
print(f"✅ Authorized as: {about['user']['emailAddress']}")

drives = service.drives().list().execute()
print(f"✅ Can access {len(drives.get('drives', []))} shared drives:")
for drive in drives.get('drives', []):
    print(f"   - {drive.get('name')}")
