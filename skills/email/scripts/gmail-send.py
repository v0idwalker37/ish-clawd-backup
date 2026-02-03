#!/usr/bin/env python3
"""
Send an email via Gmail.
Usage: gmail-send.py <to> <subject> <body>
"""

import sys
import base64
from email.mime.text import MIMEText
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SKILL_DIR = Path(__file__).parent.parent
TOKEN_FILE = SKILL_DIR / "token.json"

def get_service():
    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE))
    return build('gmail', 'v1', credentials=creds)

def create_message(to, subject, body, from_addr=None):
    """Create email message."""
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    if from_addr:
        message['from'] = from_addr
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw}

def main():
    if len(sys.argv) < 4:
        print("Usage: gmail-send.py <to> <subject> <body>")
        sys.exit(1)
    
    to = sys.argv[1]
    subject = sys.argv[2]
    body = sys.argv[3]
    
    service = get_service()
    message = create_message(to, subject, body)
    
    try:
        sent = service.users().messages().send(
            userId='me',
            body=message
        ).execute()
        
        print(f"✅ Email sent successfully!")
        print(f"   To: {to}")
        print(f"   Subject: {subject}")
        print(f"   Message ID: {sent['id']}")
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
