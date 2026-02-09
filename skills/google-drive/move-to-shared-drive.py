#!/usr/bin/env python3
"""Move blog PDFs to Ungouge shared drive"""
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

print("🔍 Finding Ungouge shared drive...")

# List all shared drives
drives = service.drives().list().execute()

print(f"\nFound {len(drives.get('drives', []))} shared drives:")
for drive in drives.get('drives', []):
    print(f"  - {drive.get('name')} (ID: {drive.get('id')})")

# Find Ungouge.ai shared drive
ungouge_drive = None
for drive in drives.get('drives', []):
    if 'ungouge' in drive.get('name', '').lower():
        ungouge_drive = drive
        break

if not ungouge_drive:
    print("\n❌ Could not find 'Ungouge.ai' shared drive")
    print("Available drives:", [d.get('name') for d in drives.get('drives', [])])
    exit(1)

drive_id = ungouge_drive.get('id')
print(f"\n✅ Found: {ungouge_drive.get('name')}")

# Search for "Ungouge master repo" folder
print("\n🔍 Searching for 'Ungouge master repo' folder...")

query = f"name contains 'master' and mimeType='application/vnd.google-apps.folder' and '{drive_id}' in parents"
results = service.files().list(
    q=query,
    driveId=drive_id,
    corpora='drive',
    includeItemsFromAllDrives=True,
    supportsAllDrives=True,
    fields='files(id, name)'
).execute()

master_folder = None
for folder in results.get('files', []):
    if 'master' in folder.get('name', '').lower() and 'repo' in folder.get('name', '').lower():
        master_folder = folder
        break

if not master_folder:
    print("❌ Could not find 'Ungouge master repo' folder")
    print("Available folders:", [f.get('name') for f in results.get('files', [])])
    exit(1)

folder_id = master_folder.get('id')
print(f"✅ Found: {master_folder.get('name')} (ID: {folder_id})")

# Create "Blog Posts (PDFs)" subfolder
print("\n📂 Creating 'Blog Posts (PDFs)' folder...")
blog_folder_metadata = {
    'name': 'Blog Posts (PDFs)',
    'mimeType': 'application/vnd.google-apps.folder',
    'parents': [folder_id]
}

blog_folder = service.files().create(
    body=blog_folder_metadata,
    fields='id, name',
    supportsAllDrives=True
).execute()

blog_folder_id = blog_folder.get('id')
print(f"✅ Created: {blog_folder.get('name')}")

# Upload PDFs
pdf_dir = Path('/Users/moltbot/clawd/projects/ungouge-app/output/blog-pdfs')
pdf_files = sorted(pdf_dir.glob('*.pdf'))

print(f"\n📤 Uploading {len(pdf_files)} PDFs...\n")

for pdf_file in pdf_files:
    file_metadata = {
        'name': pdf_file.name,
        'parents': [blog_folder_id]
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
print(f"\n📂 Location: Shared drives/Ungouge.ai/Ungouge master repo/Blog Posts (PDFs)")
print(f"📂 Folder link: https://drive.google.com/drive/folders/{blog_folder_id}")

# Delete old folder from My Drive
print("\n🗑️  Cleaning up old folder from My Drive...")
with open('/Users/moltbot/clawd/skills/google-drive/uploaded-blog-pdfs.json', 'r') as f:
    old_data = json.load(f)
    old_folder_id = old_data.get('folder_id')
    
if old_folder_id:
    service.files().delete(fileId=old_folder_id).execute()
    print("✅ Old folder deleted")

print("\n✅ All done!")
