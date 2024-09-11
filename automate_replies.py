import os
import base64
import openai
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

KEYWORD_LABEL_MAPPING = {
    'invoice': 'INVOICE_LABEL',
    'meetings': 'MEETING_LABEL',
}

openai.api_key = os.getenv('OPENAI_API_KEY')

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

def get_email_content(service, msg_id):
    msg = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()
    raw_data = msg['raw']
    decoded_data = base64.urlsafe_b64decode(raw_data).decode('utf-8')
    return decoded_data

def generate_reply(email_content):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": email_content}
        ]
    )
    return response.choices[0].message['content']

def create_message(to, subject, body):
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject
    message.attach(MIMEText(body, 'plain'))
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return raw_message

def send_reply(service, msg_id, reply_body):
    original_msg = service.users().messages().get(userId='me', id=msg_id).execute()
    headers = original_msg['payload']['headers']
    to = next(header['value'] for header in headers if header['name'] == 'From')
    subject = "Re: " + next(header['value'] for header in headers if header['name'] == 'Subject')
    reply_message = create_message(to, subject, reply_body)
    service.users().messages().send(userId='me', body={'raw': reply_message}).execute()

def main():
    service = authenticate_gmail()
    for keyword, label_name in KEYWORD_LABEL_MAPPING.items():
        label_id = get_label_id(service, label_name)
        if label_id:
            print(f"Searching for emails containing '{keyword}'...")
            emails = search_emails(service, f'{keyword}')
            for msg_id in emails:
                print(f"Fetching content for email ID: {msg_id}")
                email_content = get_email_content(service, msg_id)
                print(f"Generating reply for email ID: {msg_id}")
                reply = generate_reply(email_content)
                print(f"Sending reply to email ID: {msg_id}")
                send_reply(service, msg_id, reply)
                print(f"Labeling email ID: {msg_id}")
                add_label(service, msg_id, label_id)
        else:
            print(f"Skipping '{keyword}' as label '{label_name}' was not found.")

if __name__ == '__main__':
    main()
