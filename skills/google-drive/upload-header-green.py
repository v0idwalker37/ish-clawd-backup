#!/usr/bin/env python3
"""Upload green text header PDF to Drive for Jason's review"""

import os
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Paths
TOKEN_PATH = '/Users/moltbot/clawd/skills/google-drive/token.json'
PDF_PATH = '/Users/moltbot/clawd/projects/ungouge-app/output/branded-pdf-proof/HEADER-GREEN-FINAL.pdf'
FOLDER_ID = '1EUoTqChGklzW-jxfvXqLnynlrudbL_Ux'  # Shared drives/Ungouge.ai/Ungouge master repo/

# Load credentials
creds = Credentials.from_authorized_user_file(TOKEN_PATH)
service = build('drive', 'v3', credentials=creds)

# Upload file
file_metadata = {
    'name': 'HEADER-GREEN-FINAL.pdf',
    'parents': [FOLDER_ID]
}

media = MediaFileUpload(PDF_PATH, mimetype='application/pdf', resumable=True)

file = service.files().create(
    body=file_metadata,
    media_body=media,
    fields='id, name, webViewLink',
    supportsAllDrives=True
).execute()

print(f"✅ Uploaded: {file.get('name')}")
print(f"📎 Link: {file.get('webViewLink')}")
print(f"🆔 File ID: {file.get('id')}")
