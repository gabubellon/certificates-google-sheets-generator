import logging
import os
import socket

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from settings import (
    DRIVE_FOLDER_CERT_ID,
    GOOGLE_SERVICE_ACCOUNT,
    SHEET_CERT_HEADER,
    SHEET_CERT_RANGE,
    SHEET_DATA_HEADER,
    SHEET_DATA_RANGE,
    SHEET_ID,
)

SERVICE_ACCOUNT_FILE = "key.json"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/drive.file",
]


def read_sheets():
    socket.setdefaulttimeout(600)  # set timeout to 10 minutes

    logging.info("Creating Google Connection")

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("sheets", "v4", credentials=credentials)

    logging.info("Reading Google Sheets Data")
    sheet = service.spreadsheets()
    result = (
        sheet.values().get(spreadsheetId=SHEET_ID, range=SHEET_DATA_RANGE).execute()
    )

    logging.info("Returning Sheets Data")
    values = result.get("values", [])
    return [dict(zip(SHEET_DATA_HEADER, item)) for item in values[1:]]


def write_on_sheets(cert_lists):
    socket.setdefaulttimeout(600)  # set timeout to 10 minutes

    logging.info("Creating Google Connection")

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("sheets", "v4", credentials=credentials)

    logging.info(f"Cleanning Sheets")
    service.spreadsheets().values().clear(
        spreadsheetId=SHEET_ID, range=SHEET_CERT_RANGE, body={}
    ).execute()

    cert_lists.insert(0, SHEET_CERT_HEADER)

    logging.info(f"Update Sheets..")
    service.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        valueInputOption="RAW",
        range=SHEET_CERT_RANGE,
        body=dict(majorDimension="ROWS", values=cert_lists),
    ).execute()

    logging.info(f"Sheets Updated.")


def save_file_drive(file_path):
    socket.setdefaulttimeout(600)  # set timeout to 10 minutes
    logging.info("Creating Google Connection")

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    logging.info("Saving File on Google Drive")
    service = build("drive", "v3", credentials=credentials)
    file_metadata = {
        "name": os.path.basename(file_path),
        "parents": [DRIVE_FOLDER_CERT_ID],
    }
    files = service.files()
    media = MediaFileUpload(file_path, resumable=True)
    file = files.create(body=file_metadata, media_body=media, fields="id").execute()

    request_body = {"role": "reader", "type": "anyone"}

    logging.info("Change File Permission")
    response_permission = (
        service.permissions().create(fileId=file.get("id"), body=request_body).execute()
    )

    response_share_link = (
        service.files().get(fileId=file.get("id"), fields="webViewLink").execute()
    )

    logging.info("Returning File Link")
    return response_share_link.get("webViewLink")
