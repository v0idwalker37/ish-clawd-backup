#!/usr/bin/env python3
"""Upload v2 professional PDF"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

creds = Credentials.from_authorized_user_file('/Users/moltbot/clawd/skills/google-drive/token.json')
service = build('drive', 'v3', credentials=creds)

master_folder_id = "1EUoTqChGklzW-jxfvXqLnynlrudbL_Ux"

file_metadata = {
    'name': '📄 V2 - Bathroom Remodel (Professional Design).pdf',
    'parents': [master_folder_id]
}

media = MediaFileUpload(
    '/Users/moltbot/clawd/projects/ungouge-app/output/branded-pdf-proof/bathroom-remodel-professional-v2.pdf',
    mimetype='application/pdf'
)

file = service.files().create(
    body=file_metadata,
    media_body=media,
    fields='id, webViewLink',
    supportsAllDrives=True
).execute()

print(f"✅ Uploaded!")
print(f"📂 {file.get('webViewLink')}")
