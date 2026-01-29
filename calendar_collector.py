import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta

class CalendarCollector:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        self.service = self._authenticate()
    
    def _authenticate(self):
        creds = None
        
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        return build('calendar', 'v3', credentials=creds)
    
    def fetch_events(self, days_ahead=7):
        now = datetime.utcnow().isoformat() + 'Z'
        end_date = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'
        
        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=end_date,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return events_result.get('items', [])