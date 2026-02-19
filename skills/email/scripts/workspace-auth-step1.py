#!/usr/bin/env python3
"""Step 1: Generate auth URL and save to file"""
import json
from google_auth_oauthlib.flow import Flow

with open('../workspace-config.json') as f:
    config = json.load(f)

gmail_config = config['gmail']
client_config = {
    'installed': {
        'client_id': gmail_config['client_id'],
        'client_secret': gmail_config['client_secret'],
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'redirect_uris': ['http://localhost:8080/']
    }
}

flow = Flow.from_client_config(
    client_config, 
    scopes=['https://www.googleapis.com/auth/gmail.readonly'], 
    redirect_uri='http://localhost:8080/'
)

auth_url, state = flow.authorization_url(prompt='consent')

# Save state for step 2
with open('../workspace-auth-state.json', 'w') as f:
    json.dump({'state': state, 'flow_config': client_config}, f)

# Save URL to file
with open('../workspace-auth-url.txt', 'w') as f:
    f.write(auth_url)

print("Auth URL saved to: workspace-auth-url.txt")
print("\nNext steps:")
print("1. Open the URL in that file")
print("2. Sign in as void@ungouge.ai")
print("3. Copy the full redirect URL from your browser")
print("4. Give it to Ish to complete the auth")
