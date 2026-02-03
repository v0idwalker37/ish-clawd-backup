#!/usr/bin/env python3
"""
Check Gmail inbox for recent unread emails.
Usage: gmail-check.py [hours_back] [max_results]
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64

SKILL_DIR = Path(__file__).parent.parent
TOKEN_FILE = SKILL_DIR / "token.json"

def get_service():
    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE))
    return build('gmail', 'v1', credentials=creds)

def decode_body(payload):
    """Extract email body from payload."""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                if 'data' in part['body']:
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
    if 'body' in payload and 'data' in payload['body']:
        return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    return ""

def main():
    hours_back = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    service = get_service()
    
    # Calculate timestamp for X hours ago
    time_threshold = datetime.now() - timedelta(hours=hours_back)
    query = f'is:unread after:{int(time_threshold.timestamp())}'
    
    # Exclude specific senders if configured
    # query += ' -from:allisontrask@gmail.com'  # Example exclusion
    
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=max_results
    ).execute()
    
    messages = results.get('messages', [])
    
    if not messages:
        print(f"No unread emails in the last {hours_back} hours.")
        return
    
    print(f"\n📧 {len(messages)} unread email(s) from last {hours_back} hours:\n")
    
    for msg in messages:
        # Get full message details
        message = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()
        
        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
        from_addr = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
        
        # Get snippet (preview)
        snippet = message.get('snippet', '')
        
        print(f"From: {from_addr}")
        print(f"Subject: {subject}")
        print(f"Date: {date}")
        print(f"Preview: {snippet[:200]}...")
        print(f"Message ID: {msg['id']}")
        print("-" * 80)

if __name__ == '__main__':
    main()
