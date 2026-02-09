#!/usr/bin/env python3
"""
Check unread emails from Google Workspace (void@ungouge.ai)
Usage: python3 workspace-check.py [hours_back] [limit]
"""

import os
import sys
import json
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(SCRIPT_DIR, '..', 'workspace-token.json')

def get_credentials():
    """Load and refresh credentials."""
    if not os.path.exists(TOKEN_PATH):
        print(f"Error: No token found at {TOKEN_PATH}")
        print("Run workspace-auth.py first to authorize.")
        sys.exit(1)
    
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())
    
    return creds

def check_emails(hours_back=2, limit=10):
    """Check unread emails from the last N hours."""
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    
    # Calculate time threshold
    since = datetime.utcnow() - timedelta(hours=hours_back)
    query = f'is:unread after:{int(since.timestamp())}'
    
    # Search for messages
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=limit
    ).execute()
    
    messages = results.get('messages', [])
    
    if not messages:
        print(f"No unread emails in the last {hours_back} hours.")
        return []
    
    print(f"📧 {len(messages)} unread email(s) from last {hours_back} hours:\n")
    
    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='metadata',
            metadataHeaders=['From', 'Subject', 'Date']
        ).execute()
        
        headers = {h['name']: h['value'] for h in msg_data.get('payload', {}).get('headers', [])}
        snippet = msg_data.get('snippet', '')[:200]
        
        email_info = {
            'id': msg['id'],
            'from': headers.get('From', 'Unknown'),
            'subject': headers.get('Subject', '(no subject)'),
            'date': headers.get('Date', ''),
            'preview': snippet
        }
        emails.append(email_info)
        
        print(f"From: {email_info['from']}")
        print(f"Subject: {email_info['subject']}")
        print(f"Date: {email_info['date']}")
        print(f"Preview: {email_info['preview']}...")
        print(f"Message ID: {email_info['id']}")
        print("-" * 80)
    
    return emails

if __name__ == '__main__':
    hours = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    check_emails(hours, limit)
