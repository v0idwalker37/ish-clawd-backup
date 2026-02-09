#!/usr/bin/env python3
"""Upload blog PDFs to Google Drive"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pathlib import Path
import json

# Load token
token_path = '/Users/moltbot/clawd/skills/google-drive/token.json'
creds = Credentials.from_authorized_user_file(token_path)

# Build Drive service
service = build('drive', 'v3', credentials=creds)

# PDF directory
pdf_dir = Path('/Users/moltbot/clawd/projects/ungouge-app/output/blog-pdfs')
pdf_files = sorted(pdf_dir.glob('*.pdf'))

print(f"📁 Found {len(pdf_files)} PDFs to upload\n")

# Create a folder for blog posts
folder_metadata = {
    'name': 'Ungouge Blog Posts (PDFs)',
    'mimeType': 'application/vnd.google-apps.folder'
}

folder = service.files().create(body=folder_metadata, fields='id').execute()
folder_id = folder.get('id')

print(f"📂 Created folder: {folder_id}\n")

# Upload each PDF
uploaded = []
for pdf_file in pdf_files:
    file_metadata = {
        'name': pdf_file.name,
        'parents': [folder_id]
    }
    
    media = MediaFileUpload(str(pdf_file), mimetype='application/pdf')
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name, webViewLink'
    ).execute()
    
    uploaded.append(file)
    print(f"✅ {file.get('name')}")

print(f"\n✅ Uploaded {len(uploaded)} PDFs!")
print(f"\n📂 Folder link: https://drive.google.com/drive/folders/{folder_id}")

# Save folder info
with open('/Users/moltbot/clawd/skills/google-drive/uploaded-blog-pdfs.json', 'w') as f:
    json.dump({
        'folder_id': folder_id,
        'folder_link': f'https://drive.google.com/drive/folders/{folder_id}',
        'files': uploaded
    }, f, indent=2)

print("\n✅ Upload complete!")
