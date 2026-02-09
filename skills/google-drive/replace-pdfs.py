#!/usr/bin/env python3
"""Replace broken PDFs with proper ones"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pathlib import Path

# Load token
creds = Credentials.from_authorized_user_file('/Users/moltbot/clawd/skills/google-drive/token.json')
service = build('drive', 'v3', credentials=creds)

# Find and delete old folder
folder_id = "1Wca1ScDEl041vWPUWMIRBXzs5v5nfah8"

print("🗑️  Deleting old broken PDFs folder...")
service.files().delete(fileId=folder_id, supportsAllDrives=True).execute()
print("✅ Deleted")

# Find master repo folder
print("\n📂 Finding Ungouge master repo...")
drive_id = "0ACiEH5kzCpB8Uk9PVA"
master_folder_id = "1EUoTqChGklzW-jxfvXqLnynlrudbL_Ux"

# Create new folder
blog_folder_metadata = {
    'name': 'Blog Posts (PDFs)',
    'mimeType': 'application/vnd.google-apps.folder',
    'parents': [master_folder_id]
}

blog_folder = service.files().create(
    body=blog_folder_metadata,
    fields='id, name',
    supportsAllDrives=True
).execute()

new_folder_id = blog_folder.get('id')
print(f"✅ Created new folder: {new_folder_id}")

# Upload REAL PDFs
pdf_dir = Path('/Users/moltbot/clawd/projects/ungouge-app/output/blog-pdfs-fixed')
pdf_files = sorted(pdf_dir.glob('*.pdf'))

print(f"\n📤 Uploading {len(pdf_files)} REAL PDFs...\n")

for pdf_file in pdf_files:
    file_metadata = {
        'name': pdf_file.name,
        'parents': [new_folder_id]
    }
    
    media = MediaFileUpload(str(pdf_file), mimetype='application/pdf')
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name',
        supportsAllDrives=True
    ).execute()
    
    print(f"  ✅ {file.get('name')}")

print(f"\n✅ Upload complete!")
print(f"📂 https://drive.google.com/drive/folders/{new_folder_id}")
