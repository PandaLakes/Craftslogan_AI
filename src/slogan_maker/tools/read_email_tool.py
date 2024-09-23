import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class GmailTool:
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    def __init__(self):
        self.creds = None
        self.token_path = os.path.join(os.path.dirname(__file__), 'token.json')
        self.credentials_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
        self.email_content = None
        self.service = None

    def authenticate_gmail(self):
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open(self.token_path, 'w') as token:
                token.write(self.creds.to_json())
        self.service = build('gmail', 'v1', credentials=self.creds)

    def get_latest_email(self):
        if self.service is None:
            self.authenticate_gmail()

        results = self.service.users().messages().list(userId='me', q='is:unread subject:slogan').execute()
        messages = results.get('messages', [])

        if not messages:
            return None

        latest_email = None
        latest_date = 0

        for email in messages:
            msg_id = email['id']
            message = self.service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            payload = message['payload']
            headers = payload.get('headers')
            parts = payload.get('parts')

            subject = ''
            for header in headers:
                if header['name'] == 'Subject':
                    subject = header['value']
                    break

            if parts:
                for part in parts:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'] and part['body']['data']
                        text = base64.urlsafe_b64decode(data).decode()
                        break
            else:
                data = payload['body'] and payload['body']['data']
                text = base64.urlsafe_b64decode(data).decode()

            internal_date = int(message['internalDate'])
            if internal_date > latest_date:
                latest_date = internal_date
                latest_email = {'subject': subject, 'body': text}

        self.email_content = latest_email
        return latest_email
