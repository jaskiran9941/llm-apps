"""Gmail API helper functions for reading emails."""
import os.path
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service(account_name='default'):
    """Authenticate and return Gmail API service.

    Args:
        account_name: Name identifier for the account (used for separate token files)

    Returns:
        Gmail API service instance
    """
    creds = None
    token_file = f'token_{account_name}.json'

    # Token file stores user's access and refresh tokens
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)

        # Save credentials for next run
        with open(token_file, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def get_account_email(service):
    """Get the email address of the authenticated account."""
    try:
        profile = service.users().getProfile(userId='me').execute()
        return profile.get('emailAddress', 'Unknown')
    except Exception as e:
        print(f"Error getting account email: {e}")
        return 'Unknown'

def list_configured_accounts():
    """List all configured Gmail accounts by looking at token files."""
    import glob
    token_files = glob.glob('token_*.json')
    accounts = []

    for token_file in token_files:
        account_name = token_file.replace('token_', '').replace('.json', '')
        accounts.append(account_name)

    return accounts

def get_emails(service, max_results=100, query=''):
    """Fetch emails from Gmail.

    Args:
        service: Gmail API service instance
        max_results: Maximum number of emails to fetch
        query: Gmail search query (e.g., 'from:amazon.com')

    Returns:
        List of email messages with content
    """
    try:
        # Get list of messages
        results = service.users().messages().list(
            userId='me',
            maxResults=max_results,
            q=query
        ).execute()

        messages = results.get('messages', [])

        email_data = []
        for message in messages:
            # Get full message details
            msg = service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()

            # Extract headers
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')

            # Extract body - try text/plain first, then HTML
            body = ''

            def extract_body_recursive(parts):
                """Recursively extract body from email parts."""
                text_body = ''
                html_body = ''

                for part in parts:
                    mime_type = part.get('mimeType', '')

                    # Handle nested multipart
                    if 'parts' in part:
                        nested_text, nested_html = extract_body_recursive(part['parts'])
                        if nested_text:
                            text_body = nested_text
                        if nested_html:
                            html_body = nested_html

                    # Extract text/plain
                    elif mime_type == 'text/plain' and 'data' in part.get('body', {}):
                        text_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')

                    # Extract text/html
                    elif mime_type == 'text/html' and 'data' in part.get('body', {}):
                        html_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')

                return text_body, html_body

            # Try to extract body
            if 'parts' in msg['payload']:
                text_body, html_body = extract_body_recursive(msg['payload']['parts'])
                body = text_body if text_body else html_body
            elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
                body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8', errors='ignore')

            email_data.append({
                'id': message['id'],
                'subject': subject,
                'from': sender,
                'date': date,
                'body': body[:5000]  # Increased limit to capture more content
            })

        return email_data

    except Exception as e:
        print(f"Error fetching emails: {e}")
        return []
