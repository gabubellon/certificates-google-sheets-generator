"""[summary]
Returns:
    [type]: [description]
"""
import os
from datetime import datetime
from inspect import formatargvalues

from loguru import logger
from PIL import Image, ImageDraw, ImageFont

from draw import Draw


class Art:
    def __init__(self, settings):
        self.settings = settings
        self.art = self.load_art()
        self.fields = self.parse_fields()

    def get_settings(self, setting, default=None):
        return self.settings.get(setting, default)

    def load_art(self):
        logger.info("loading art...")
        size = self.get_settings("size", None)
        if size:
            return Image.open(self.get_settings("path")).resize(size)
        return Image.open(self.get_settings("path"))

    def parse_fields(self):
        logger.info("loadding art...")
        return self.get_settings("fields", None)

    def create(self,values,draw_grid=False):
        logger.info("creating art...")
        for field in self.get_settings("fields", None):
            self.execute(field, values,draw_grid)
        return self.save(values)

    def execute(self, field, values,draw_grid=False):
        draw = Draw(self.art, field.get("settings"))
        item = self.get_item(values, field.get("source_id"), field)
        if item:
            if field.get("type") == "text":
                draw.write_text(item,draw_grid)
            elif field.get("type") == "image":
                draw.draw_image(item)

    @staticmethod
    def get_item(values, field_value, field):
        if not field:
            return values.get(field_value)

        return (
            values.get(field_value)
            if field.get("from_source", False)
            else field.get("default_value")
        )

    def save(self, values):
        logger.info("saving art...")
        filename = self.parse_filename(values)
        self.art.save(filename)
        return filename

    def parse_filename(self, values):
        prefix = []
        for field_prefix in self.get_settings("fields_prefix", []):
            prefix.append(self.get_item(values, field_prefix, None))
        prefix = "_".join([str(item) for item in prefix]).replace(" ", "_")

        suffix = self.get_settings("file_suffix", "art")

        if self.get_settings("date_on_filename", False):
            date_str = datetime.now().strftime("%Y%m%d%H%M%S")
            suffix = f"{suffix}_{date_str}"

        os.makedirs(self.get_settings("local_path", "./output"), exist_ok=True)

        return os.path.join(
            self.get_settings("local_path", "./output"),
            f"{prefix}_{suffix}.png",
        )
