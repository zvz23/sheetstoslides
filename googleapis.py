from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os


SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly','https://www.googleapis.com/auth/presentations', 'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']

def get_creds():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def create_presentation(creds, title):
    try:
        service = build('slides', 'v1', credentials=creds)

        body = {
            'title': title
        }
        presentation = service.presentations() \
            .create(body=body).execute()
        presentation_id = presentation.get('presentationId')
        print(f"Created presentation with ID:"
              f"{presentation_id}")
        return presentation_id

    except HttpError as error:
        print(f"An error occurred: {error}")
        print("presentation not created")
        return error

def get_rows_with_bold_name(creds, sheet_id):
    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.get(spreadsheetId=sheet_id,
                                    ranges='C:F', includeGridData=True).execute()
        rows = result['sheets'][0]['data'][0]['rowData']
        instagram = []
        for i, row in enumerate(rows):
            if i == 0:
                continue
            is_bold = row['values'][0]['effectiveFormat']['textFormat']['bold']
            if is_bold:
                instagram.append({
                    'name': row['values'][0]['userEnteredValue']['stringValue'],
                    'instagram_url': row['values'][2]['userEnteredValue']['stringValue'],
                    'submission': None
                })
                try:
                    instagram[-1]['submission'] = row['values'][3]['userEnteredValue']['stringValue'].strip()
                except:
                    pass
        return instagram
    except HttpError as err:
        print(err)









