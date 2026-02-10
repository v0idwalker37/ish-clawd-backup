#!/usr/bin/env python3
"""
Full workspace backup to Google Drive
Creates timestamped zip archive and uploads to shared drive
"""

import os
import json
import zipfile
from datetime import datetime
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Paths
WORKSPACE = Path("/Users/moltbot/clawd")
OPENCLAW_CONFIG = Path("/Users/moltbot/.openclaw")
OPENCLAW_MEMORY = Path("/Users/moltbot/.openclaw/memory")
TOKEN_FILE = WORKSPACE / "skills/google-drive/drive-token.json"

# Google Drive folder ID (will create if needed)
BACKUP_FOLDER_NAME = "Ish-Backup"

def get_drive_service():
    """Authenticate with Google Drive"""
    with open(TOKEN_FILE, 'r') as f:
        token_data = json.load(f)
    
    creds = Credentials.from_authorized_user_info(token_data)
    
    # Refresh if expired
    if creds.expired and creds.refresh_token:
        from google.auth.transport.requests import Request
        creds.refresh(Request())
        # Save refreshed token
        with open(TOKEN_FILE, 'w') as f:
            json.dump(json.loads(creds.to_json()), f)
    
    return build('drive', 'v3', credentials=creds)

def find_or_create_folder(service, folder_name, parent_id='root'):
    """Find existing folder or create new one"""
    # Search for folder
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id != 'root':
        query += f" and '{parent_id}' in parents"
    
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    folders = results.get('files', [])
    
    if folders:
        return folders[0]['id']
    
    # Create folder
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id] if parent_id != 'root' else []
    }
    
    folder = service.files().create(body=folder_metadata, fields='id').execute()
    return folder['id']

def create_backup_zip(timestamp):
    """Create comprehensive backup zip file"""
    backup_name = f"ish-backup-{timestamp}.zip"
    backup_path = WORKSPACE / backup_name
    
    print(f"📦 Creating backup archive: {backup_name}")
    
    # Files to exclude
    exclude_patterns = [
        '__pycache__',
        'node_modules',
        '.DS_Store',
        '*.pyc',
        '.git',  # Don't backup git (too large)
        'venv',
        'env',
        '*.log'
    ]
    
    def should_exclude(path):
        path_str = str(path)
        return any(pattern.replace('*', '') in path_str or path.name.startswith('.') and pattern.startswith('.') for pattern in exclude_patterns)
    
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Backup workspace
        print("  ├─ Workspace files...")
        for root, dirs, files in os.walk(WORKSPACE):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d)]
            
            for file in files:
                file_path = Path(root) / file
                if not should_exclude(file_path) and file != backup_name:
                    arcname = file_path.relative_to(WORKSPACE.parent)
                    zipf.write(file_path, arcname)
        
        # Backup OpenClaw config
        if OPENCLAW_CONFIG.exists():
            print("  ├─ OpenClaw config...")
            for root, dirs, files in os.walk(OPENCLAW_CONFIG):
                dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d)]
                for file in files:
                    file_path = Path(root) / file
                    if not should_exclude(file_path):
                        arcname = Path(".openclaw") / file_path.relative_to(OPENCLAW_CONFIG)
                        zipf.write(file_path, arcname)
        
        # Backup memory databases
        if OPENCLAW_MEMORY.exists():
            print("  ├─ Memory databases...")
            for root, dirs, files in os.walk(OPENCLAW_MEMORY):
                for file in files:
                    file_path = Path(root) / file
                    if not should_exclude(file_path):
                        arcname = Path(".openclaw/memory") / file_path.relative_to(OPENCLAW_MEMORY)
                        zipf.write(file_path, arcname)
    
    size_mb = backup_path.stat().st_size / (1024 * 1024)
    print(f"  └─ Archive created: {size_mb:.1f} MB")
    
    return backup_path

def upload_to_drive(service, file_path, folder_id):
    """Upload file to Google Drive"""
    print(f"☁️  Uploading to Google Drive...")
    
    file_metadata = {
        'name': file_path.name,
        'parents': [folder_id]
    }
    
    media = MediaFileUpload(str(file_path), resumable=True)
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name, size, webViewLink'
    ).execute()
    
    size_mb = int(file.get('size', 0)) / (1024 * 1024)
    print(f"  ✅ Uploaded: {file['name']} ({size_mb:.1f} MB)")
    print(f"  🔗 Link: {file.get('webViewLink', 'N/A')}")
    
    return file

def cleanup_old_backups(service, folder_id, keep_latest=5):
    """Keep only the N most recent backups"""
    print(f"🧹 Cleaning up old backups (keeping latest {keep_latest})...")
    
    query = f"'{folder_id}' in parents and name contains 'ish-backup-' and trashed=false"
    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, createdTime)',
        orderBy='createdTime desc'
    ).execute()
    
    files = results.get('files', [])
    
    if len(files) <= keep_latest:
        print(f"  └─ {len(files)} backups found, no cleanup needed")
        return
    
    # Delete old backups
    for file in files[keep_latest:]:
        service.files().delete(fileId=file['id']).execute()
        print(f"  ├─ Deleted: {file['name']}")
    
    print(f"  └─ Kept {keep_latest} most recent backups")

def main():
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    print("="*60)
    print("🌀 ISH FULL BACKUP TO GOOGLE DRIVE")
    print(f"   Timestamp: {timestamp}")
    print("="*60)
    print()
    
    # Authenticate
    print("🔐 Authenticating with Google Drive...")
    service = get_drive_service()
    print("  ✅ Authenticated")
    print()
    
    # Find or create backup folder
    print(f"📁 Ensuring backup folder exists: {BACKUP_FOLDER_NAME}")
    folder_id = find_or_create_folder(service, BACKUP_FOLDER_NAME)
    print(f"  ✅ Folder ID: {folder_id}")
    print()
    
    # Create backup archive
    backup_path = create_backup_zip(timestamp)
    print()
    
    # Upload to Drive
    file = upload_to_drive(service, backup_path, folder_id)
    print()
    
    # Cleanup old backups
    cleanup_old_backups(service, folder_id, keep_latest=5)
    print()
    
    # Delete local backup file
    print("🗑️  Cleaning up local backup file...")
    backup_path.unlink()
    print("  ✅ Local file deleted")
    print()
    
    print("="*60)
    print("✅ BACKUP COMPLETE")
    print(f"   Link: {file.get('webViewLink', 'Check Google Drive')}")
    print("="*60)

if __name__ == "__main__":
    main()
