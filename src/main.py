import argparse
import os
import shutil

from loguru import logger

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
    "-lim",
    "--limit",
    type=int,
    help="limit data to result",
    dest="limit",
)

parser.add_argument(
    "-lo"
    "--local",
    action='store_true',
    help="Run only local and dont upload files",
    dest="local",
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
        local_art = art.create(item,args.grid)
        if not args.local:
            item["url"] = gapi.save_to_drive(local_art)
        del art
    if not args.local:
        gapi.write_destination_spreadsheet(data)

    if os.path.exists("./temp"):
        shutil.rmtree("./temp")
