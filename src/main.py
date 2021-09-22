import argparse

from loguru import logger
from reportlab.graphics import renderPDF, renderPM

from art import Art
from google_api import GoogleAPI
from settings import Settings

parser = argparse.ArgumentParser(description="Creating arts to use on events")
parser.add_argument(
    "-s",
    "--settings",
    type=str,
    help="toml file with settings parameters",
    default="./settings.toml",
    dest="settings",
)

parser.add_argument(
    "-g",
    "--grid",
    action='store_true',
    help="draw a line grid 50x50 on output picture",
    dest="grid",
)

parser.add_argument(
    "-l",
    "--limit",
    type=int,
    help="limit data to result",
    dest="limit",
)

if __name__ == "__main__":
    args = parser.parse_args()
    toml_settings = Settings()
    toml_settings.load_settings(args.settings)
    
    GOOGLE = toml_settings.get_setting("google")
    IMAGE = toml_settings.get_setting("image")

    gapi = GoogleAPI(GOOGLE,limit=args.limit)
    data = gapi.read_source_spreadsheet()
    for item in data:
        art = Art(IMAGE)
        item["url"] = gapi.save_to_drive(art.create(item,args.grid))
        del art
    gapi.write_destination_spreadsheet(data)
