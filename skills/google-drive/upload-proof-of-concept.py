#!/usr/bin/env python3
"""Upload branded PDF proof of concept to Drive"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pathlib import Path

# Load token
creds = Credentials.from_authorized_user_file('/Users/moltbot/clawd/skills/google-drive/token.json')
service = build('drive', 'v3', credentials=creds)

# Master repo folder ID
master_folder_id = "1EUoTqChGklzW-jxfvXqLnynlrudbL_Ux"

# PDF file
pdf_file = Path('/Users/moltbot/clawd/projects/ungouge-app/output/branded-pdf-proof/bathroom-remodel-branded.pdf')

print("📤 Uploading branded PDF proof of concept...\n")

# Upload
file_metadata = {
    'name': '📄 PROOF OF CONCEPT - Bathroom Remodel (Branded).pdf',
    'parents': [master_folder_id]
}

media = MediaFileUpload(str(pdf_file), mimetype='application/pdf')

file = service.files().create(
    body=file_metadata,
    media_body=media,
    fields='id, name, webViewLink',
    supportsAllDrives=True
).execute()

print(f"✅ Uploaded: {file.get('name')}")
print(f"📂 Link: {file.get('webViewLink')}")
print(f"\n📍 Location: Shared drives/Ungouge.ai/Ungouge master repo/")
