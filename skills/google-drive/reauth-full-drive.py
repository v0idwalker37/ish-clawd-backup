#!/usr/bin/env python3
"""Re-authorize with full Drive access for shared drives"""
from google_auth_oauthlib.flow import Flow
import json

# Load credentials
with open('/Users/moltbot/clawd/skills/google-drive/credentials.json', 'r') as f:
    CLIENT_CONFIG = json.load(f)

# Full Drive scope needed for shared drives
SCOPES = ['https://www.googleapis.com/auth/drive']

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
print("🔐 DRIVE API - FULL ACCESS (for Shared Drives)")
print("="*80)
print(f"\n{auth_url}\n")
print("⚠️  Select: void@ungouge.ai")
print("⚠️  This grants access to ALL Drive files including shared drives")
print("="*80)
print(f"\nState: {state}\n")
