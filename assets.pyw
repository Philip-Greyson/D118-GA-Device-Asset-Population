"""Script to populate the Asset ID field of devices in Google Admin from a spreadsheet of Asset IDs and Serial Numbers.

https://github.com/Philip-Greyson/D118-GA-Device-Asset-Population

Needs the google-api-python-client, google-auth-httplib2 and the google-auth-oauthlib
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
"""

# google module imports
import json
import os  # needed to get environement variables
from datetime import *
from re import A
from typing import get_type_hints

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Google API Scopes that will be used. If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/admin.directory.device.chromeos']

INPUT_FILE_NAME = 'input.csv'  # name of the file used for input
ASSET_COLUMN_NAME = 'U_MBA_DEVICE.DEVICE_NUMBER'  # text of the column header that has the asset ID information in it
SERIAL_COLUMN_NAME = 'U_MBA_DEVICE.SERIAL_NUMBER'  # text of the column header that has the serial number in it
DELIMITER_CHAR = ','  # character used for delimiting the fields. comma for .csv traditionally

if __name__ == '__main__':  # main file execution
    with open('assetLog.txt', 'w') as log:
        # Get credentials from json file, ask for permissions on scope or use existing token.json approval, then build the "service" connection to Google API
        creds = None
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        service = build('admin', 'directory_v1', credentials=creds)

        # first generate a dictionary of all the serial number and Google device ID pairings for the given OU, so we dont have to look up individual serial numbers to update later
        deviceIDDict = {}  # dict holding the google admin internal ID for the devices by serial number

        print('INFO: Compiling list of all devices in Google Admin, this may take a while')
        print('INFO: Compiling list of all devices in Google Admin, this may take a while', file=log)

        deviceListToken = ''  # blank primer for multi-page query results
        deviceQuery = ''  # you can reduce the number of chromebooks processed by using a query to narrow down the results, see here for options: https://developers.google.com/admin-sdk/directory/v1/list-query-operators
        # deviceResults = service.chromeosdevices().list(customerId='my_customer',query=deviceQuery).execute()
        while deviceListToken is not None:
            if deviceListToken == '':
                deviceResults = service.chromeosdevices().list(customerId='my_customer',query=deviceQuery).execute()  # first time run, it doesnt like having any pageToken defined for some reason
            else:
                deviceResults = service.chromeosdevices().list(customerId='my_customer',pageToken=deviceListToken,query=deviceQuery).execute()  # subsequent runs with the pageToken defined
            
            deviceListToken = deviceResults.get('nextPageToken')
            devices = deviceResults.get('chromeosdevices', [])  # separate just the devices list from the rest of the result
            for device in devices:
                serial = device.get('serialNumber')
                deviceId = device.get('deviceId')
                # print(f'{serial}:{deviceId}')  # debug
                deviceIDDict.update({serial : deviceId})  # add the serial : device ID to the dict
        
        print('INFO: Starting the Asset ID update process')
        print('INFO: Starting the Asset ID update process', file=log)
        with open(INPUT_FILE_NAME, 'r') as inFile:
            firstLine = inFile.readline().split(DELIMITER_CHAR)
            # print(firstLine)  # debug
            assetIndex = firstLine.index(ASSET_COLUMN_NAME)  # get the index of the column that contains the asset ID info
            columnIndex = firstLine.index(SERIAL_COLUMN_NAME)
            for lineNum, line in enumerate(inFile.readlines()):  # go through each line
                try:
                    assetId = line.strip().split(DELIMITER_CHAR)[assetIndex]
                    serialNum = line.strip().split(DELIMITER_CHAR)[columnIndex]
                    deviceId = deviceIDDict.get(serialNum)  # get the internal GA device ID that matches the serial number we are processing
                    print(f'DBUG: Line {lineNum+1}: Serial {serialNum} - Asset {assetId}, GA ID {deviceId}')
                    print(f'DBUG: Line {lineNum+1}: Serial {serialNum} - Asset {assetId}, GA ID {deviceId}', file=log)

                    service.chromeosdevices().update(customerId='my_customer',deviceId = deviceId, body={'annotatedAssetId':assetId}).execute()  # do the update for the current device ID adding the asset ID
                except Exception as er:
                    print(f'ERROR on line {lineNum+1}: {er}')
                    print(f'ERROR on line {lineNum+1}: {er}', file=log)

                



