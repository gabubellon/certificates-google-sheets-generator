import io
import os
import socket
import tempfile

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from loguru import logger

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/drive.file",
]


class GoogleAPI:
    def __init__(self, settings,limit=None, timeout=600):
        self.settings = settings
        self.credentials = self.load_credentials()
        self.build_source_spreadsheet()
        self.build_destination_spreadsheet()
        self.build_destination_drive()
        self.limit = limit
        socket.setdefaulttimeout(timeout if timeout else 600)  # set timeout to 10 minutes

    def get_settings(self, setting, default=None):
        return self.settings.get(setting, default)

    def load_credentials(self):
        return service_account.Credentials.from_service_account_file(
            self.get_settings("json_key_path", "./key.json"), scopes=SCOPES
        )

    # build("sheets", "v4", credentials=credentials)
    def build_service(self, type, version):
        return build(type, version, credentials=self.credentials)

    def build_source_spreadsheet(self):
        self.source_id = self.get_settings("sheets").get("source").get("id")
        self.source_range = self.get_settings("sheets").get("source").get("range")
        self.source_fields = self.get_settings("sheets").get("source").get("fields")

    def build_destination_spreadsheet(self):
        self.destination_id = self.get_settings("sheets").get("destination").get("id")
        self.destination_range = (
            self.get_settings("sheets").get("destination").get("range")
        )

    def build_destination_drive(self):
        self.drive_id = self.get_settings("drive").get("destination").get("id")
        self.remove_local = (
            self.get_settings("drive").get("destination").get("remove_local", False)
        )

    def build_spreadsheet_header(self, to_destination=False):
        if to_destination:
            return [
                field.get("id")
                for field in self.source_fields
                if field.get("to_destination", True)
            ]
        return [field.get("id") for field in self.source_fields]

    def read_spreadsheet(self, spreadsheet_id, spreadsheet_range, spreadsheet_header):
        sheet = self.build_service("sheets", "v4").spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=spreadsheet_id, range=spreadsheet_range)
            .execute()
        )

        values = result.get("values", [])

        data = [dict(zip(spreadsheet_header, item)) for item in values[1:]]

        if self.limit:
            data = data[0:self.limit]
            
        for field in self.source_fields:
            if field.get("file_from_drive"):
                for item in data:
                    url = item.get(field.get("id"))
                    local_file = self.load_from_drive(url.split("id=")[1])
                    item[field.get("id")] = local_file
        return data

    def read_source_spreadsheet(self):
        logger.info("reading Source Spreadsheet...")
        return self.read_spreadsheet(
            self.source_id, self.source_range, self.build_spreadsheet_header()
        )

    def write_spreadsheet(self, spreadsheet_id, spreadsheet_range, values):
        sheet = self.build_service("sheets", "v4").spreadsheets()

        sheet.values().clear(
            spreadsheetId=spreadsheet_id, range=spreadsheet_range, body={}
        ).execute()
        headers = self.build_spreadsheet_header(to_destination=True) + list(
            set(list(values[0].keys())) - set(self.build_spreadsheet_header())
        )

        data = [[item.get(header) for header in headers] for item in values]
        data.insert(0, headers)

        sheet.values().update(
            spreadsheetId=spreadsheet_id,
            valueInputOption="RAW",
            range=spreadsheet_range,
            body=dict(majorDimension="ROWS", values=data),
        ).execute()

    def write_destination_spreadsheet(self, values):
        logger.info("writing on destination spreadsheet...")
        return self.write_spreadsheet(
            self.destination_id, self.destination_range, values
        )

    def save_to_drive(self, file_path):
        logger.info("saving on destination drive...")
        service = self.build_service("drive", "v3")
        file_metadata = {
            "name": os.path.basename(file_path),
            "parents": [self.drive_id],
        }

        media = MediaFileUpload(file_path, resumable=True)
        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )

        request_body = {"role": "reader", "type": "anyone"}

        response_permission = (
            service.permissions()
            .create(fileId=file.get("id"), body=request_body)
            .execute()
        )

        response_share_link = (
            service.files().get(fileId=file.get("id"), fields="webViewLink").execute()
        )

        if self.remove_local:
            os.remove(file_path)

        return response_share_link.get("webViewLink")

    def load_from_drive(self, file_id):
        logger.info("loading from drive...")
        files = self.build_service("drive", "v3").files()

        # https://drive.google.com/open?id=1UjAD4ZQzouFPB_m64RplH2lnVPjqrbZL
        file_name = f"./temp/{next(tempfile._get_candidate_names())}.png"

        os.makedirs("./temp/", exist_ok=True)

        request = files.get_media(fileId=file_id)
        fh = io.FileIO(file_name, mode="wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            (
                status,
                done,
            ) = downloader.next_chunk()

        return file_name
