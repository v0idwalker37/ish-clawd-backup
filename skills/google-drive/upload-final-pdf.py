#!/usr/bin/env python3
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

creds = Credentials.from_authorized_user_file('/Users/moltbot/clawd/skills/google-drive/token.json')
service = build('drive', 'v3', credentials=creds)

file_metadata = {
    'name': '📄 FINAL - Bathroom Remodel (Professional Typography).pdf',
    'parents': ["1EUoTqChGklzW-jxfvXqLnynlrudbL_Ux"]
}

media = MediaFileUpload(
    '/Users/moltbot/clawd/projects/ungouge-app/output/branded-pdf-proof/bathroom-remodel-FINAL.pdf',
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
