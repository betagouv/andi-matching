import os
import pickle
import re

import unidecode
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

SPREADSHEET_ID = '187xkbQY_vFCxscWLJ-TjEzgmxQd9qPydcRpKLnVmsBU'
SHEED_ID = '1686694416'
RANGE = 'Config_Matching!A:N'

"""
Deprecated content: Google Drive integration was used in ANDI's first period of
experimentation
"""


def get_data(_config):
    from match import logger  # pylint:disable=import-outside-toplevel
    service = get_service()
    profiles = get_profiles(service)
    logger.info('Obtained %s profiles from google drive', len(profiles))
    return profiles


def key_to_slug(raw_string):
    step1 = unidecode.unidecode(raw_string)
    step2 = re.sub('[^a-zA-Z0-9 ]', '', step1)
    return re.sub(r'\s+', '_', step2).lower()


def get_profiles(service):
    sheet = service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE).execute()
    values = result.get('values', [])
    columns = [s.lower() for s in values[0]]
    raw_profiles = []
    for row in values[1:]:
        raw_profiles.append(dict(zip(columns, row)))

    profiles = {}
    for p in raw_profiles:
        name = ' '.join([p['nom'], p['prenom']])
        slug = key_to_slug(name)
        profiles[slug] = {
            'name': name,
            'lat': p['lat'],
            'lon': p['lon'],
            'max_distance': p['distance'] if 'distance' in p and p['distance'] else 10,
            'sizes': p.get('taille', 'pme').split(' '),
            'romes': p.get('rome', '').split(' '),
            'includes': p['include'].split(' ') if 'include' in p and p['include'] else None,
            'excludes': p['exclude'].split(' ') if 'exclude' in p and p['exclude'] else None,
            'multipliers': {
                'fn': int(p['force naf']),
                'fg': int(p['force geo']),
                'ft': int(p['force taille']),
                'fw': int(p['force pmsmp']),
                'fc': int(p['force contact']),
            }
        }
    return profiles


def get_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # flow = InstalledAppFlow.from_client_config(
            #     credentials, SCOPES)
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('sheets', 'v4', credentials=creds)
