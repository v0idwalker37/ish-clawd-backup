#!/usr/bin/env python3
"""
Check iCloud email via IMAP.
Usage: icloud-check.py [hours_back] [max_results]
"""

import sys
import json
import imaplib
import email
from datetime import datetime, timedelta
from pathlib import Path
from email.header import decode_header

SKILL_DIR = Path(__file__).parent.parent
CONFIG_FILE = SKILL_DIR / "config.json"

def get_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)['icloud']

def decode_subject(subject):
    """Decode email subject."""
    decoded = decode_header(subject)
    parts = []
    for content, encoding in decoded:
        if isinstance(content, bytes):
            parts.append(content.decode(encoding or 'utf-8', errors='ignore'))
        else:
            parts.append(content)
    return ''.join(parts)

def main():
    hours_back = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    config = get_config()
    
    # Connect to iCloud IMAP
    mail = imaplib.IMAP4_SSL(config['imap_server'], config['imap_port'])
    
    # Login (remove @icloud.com as iCloud expects just username)
    username = config['primary_email'].replace('@icloud.com', '')
    password = config['app_password'].replace('-', '')  # Remove dashes
    
    try:
        mail.login(username, password)
    except Exception as e:
        print(f"❌ Login failed: {e}")
        sys.exit(1)
    
    # Select inbox
    mail.select('INBOX')
    
    # Calculate date for search
    date_threshold = datetime.now() - timedelta(hours=hours_back)
    date_str = date_threshold.strftime('%d-%b-%Y')
    
    # Search for unread emails since date
    status, messages = mail.search(None, f'UNSEEN SINCE {date_str}')
    
    if status != 'OK' or not messages[0]:
        print(f"No unread iCloud emails in the last {hours_back} hours.")
        mail.close()
        mail.logout()
        return
    
    email_ids = messages[0].split()
    
    if not email_ids:
        print(f"No unread iCloud emails in the last {hours_back} hours.")
        mail.close()
        mail.logout()
        return
    
    # Limit results
    email_ids = email_ids[-max_results:]
    
    print(f"\n📧 {len(email_ids)} unread iCloud email(s) from last {hours_back} hours:\n")
    
    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, '(RFC822)')
        
        if status != 'OK':
            continue
        
        # Handle unexpected fetch response formats
        raw = None
        for part in msg_data:
            if isinstance(part, tuple) and len(part) == 2 and isinstance(part[1], bytes):
                raw = part[1]
                break
        if raw is None:
            continue
        
        msg = email.message_from_bytes(raw)
        
        subject = decode_subject(msg.get('Subject', '(No Subject)'))
        from_addr = msg.get('From', 'Unknown')
        date = msg.get('Date', '')
        
        # Get body preview
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
        else:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        
        preview = body[:200] if body else "(No preview)"
        
        print(f"From: {from_addr}")
        print(f"Subject: {subject}")
        print(f"Date: {date}")
        print(f"Preview: {preview}...")
        print("-" * 80)
    
    mail.close()
    mail.logout()

if __name__ == '__main__':
    main()
