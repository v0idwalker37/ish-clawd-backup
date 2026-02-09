#!/usr/bin/env python3
"""Generate final authorization URL with correct credentials"""
from google_auth_oauthlib.flow import Flow
import json

# Load correct credentials
with open('/Users/moltbot/clawd/skills/google-drive/credentials.json', 'r') as f:
    CLIENT_CONFIG = json.load(f)

SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Create flow
flow = Flow.from_client_config(CLIENT_CONFIG, scopes=SCOPES)
flow.redirect_uri = 'http://localhost:8080/'

# Generate authorization URL
auth_url, state = flow.authorization_url(
    access_type='offline',
    include_granted_scopes='true',
    prompt='consent'
)

print("\n" + "="*80)
print("🔐 DRIVE API AUTHORIZATION (Correct Credentials)")
print("="*80)
print(f"\n{auth_url}\n")
print("⚠️  Select: void@ungouge.ai")
print("="*80)
print(f"\nState: {state}\n")
