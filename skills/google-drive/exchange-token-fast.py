#!/usr/bin/env python3
"""Quick token exchange"""
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import json

with open('/Users/moltbot/clawd/skills/google-drive/credentials.json', 'r') as f:
    CLIENT_CONFIG = json.load(f)

code = "4/0ASc3gC1HO_VNHOP4FSm-i0TkPtf1_RC2ExMtPsloxYV1-Xkgn0soJhI7s0GgGELNmBGeiA"

flow = Flow.from_client_config(CLIENT_CONFIG, scopes=['https://www.googleapis.com/auth/drive'])
flow.redirect_uri = 'http://localhost:8080/'
flow.fetch_token(code=code)

with open('/Users/moltbot/clawd/skills/google-drive/token.json', 'w') as token:
    token.write(flow.credentials.to_json())

service = build('drive', 'v3', credentials=flow.credentials)
about = service.about().get(fields="user").execute()
drives = service.drives().list().execute()

print(f"✅ {about['user']['emailAddress']}")
print(f"✅ {len(drives.get('drives', []))} shared drives")
