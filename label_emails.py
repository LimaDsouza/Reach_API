import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

KEYWORD_LABEL_MAPPING = {
    'invoice': 'INVOICE_LABEL',
    'meeting': 'MEETING_LABEL',
}

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def search_emails(service, query):
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    return [msg['id'] for msg in messages]

def add_label(service, msg_id, label_id):
    service.users().messages().modify(
        userId='me',
        id=msg_id,
        body={'addLabelIds': [label_id]}
    ).execute()

def get_label_id(service, label_name):
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    for label in labels:
        if label['name'].lower() == label_name.lower():
            return label['id']
    print(f"Label '{label_name}' not found.")
    return None

def main():
    service = authenticate_gmail()
    for keyword, label_name in KEYWORD_LABEL_MAPPING.items():
        label_id = get_label_id(service, label_name)
        if label_id:
            print(f"Searching for emails containing '{keyword}'...")
            emails = search_emails(service, f'{keyword}')
            for msg_id in emails:
                print(f"Labeling email ID: {msg_id}")
                add_label(service, msg_id, label_id)
        else:
            print(f"Skipping '{keyword}' as label '{label_name}' was not found.")

if __name__ == '__main__':
    main()
import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

KEYWORD_LABEL_MAPPING = {
    'invoice': 'INVOICE_LABEL',
    'meeting': 'MEETING_LABEL',
}

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def search_emails(service, query):
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    return [msg['id'] for msg in messages]

def add_label(service, msg_id, label_id):
    service.users().messages().modify(
        userId='me',
        id=msg_id,
        body={'addLabelIds': [label_id]}
    ).execute()

def get_label_id(service, label_name):
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    for label in labels:
        if label['name'].lower() == label_name.lower():
            return label['id']
    print(f"Label '{label_name}' not found.")
    return None

def main():
    service = authenticate_gmail()
    for keyword, label_name in KEYWORD_LABEL_MAPPING.items():
        label_id = get_label_id(service, label_name)
        if label_id:
            print(f"Searching for emails containing '{keyword}'...")
            emails = search_emails(service, f'{keyword}')
            for msg_id in emails:
                print(f"Labeling email ID: {msg_id}")
                add_label(service, msg_id, label_id)
        else:
            print(f"Skipping '{keyword}' as label '{label_name}' was not found.")

if __name__ == '__main__':
    main()
