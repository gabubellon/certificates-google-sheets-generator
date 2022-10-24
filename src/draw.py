"""[summary]
Returns:
    [type]: [description]
"""
import os

from loguru import logger
from PIL import Image, ImageDraw, ImageFont


class Draw:
    """[summary]"""

    def __init__(self, image, settings):
        """[summary]

        Args:
            image ([type]): [description]
            settings ([type]): [description]

        Returns:
            [type]: [description]
        """
        self.image = image
        self.settings = settings
        self.font = None
        self.xy = None
        self.text = None
        self.im = None

    def write_text(self, text,draw_grid=False):
        logger.info("writing text...")
        self.font = self.build_font()
        self.text = self.split_text(text)
        self.xy = self.parse_xy()
        logger.info(self.text)
        ImageDraw.Draw(self.image).text(
            text=self.text.encode('utf-8').decode('utf-8'),
            **self.build_settings(),
        )
        if draw_grid:
            for x in range(0,self.image.size[0],50):
                ImageDraw.Draw(self.image).line((x,0,x,self.image.size[0]),width=5,fill="#8a817e")
            for y in range(0,self.image.size[1],50):
                ImageDraw.Draw(self.image).line((0,y,self.image.size[1],y),width=5,fill="#8a817e")

    def draw_image(self, image_path):
        logger.info("drawing image...")
        self.xy = self.parse_xy()
        self.im = self.load_im(image_path)
        self.image.paste(self.im, box=self.xy, mask=self.load_mask())

    def load_im(self, image_path):
        logger.info("loading image to copy...")

        image = self.load_image(image_path)

        size = self.get_setting("size", image.size)
        if image.size != size:
            return image.resize(size)
        return image

    def load_mask(self) -> None:
        """[summary]

        Returns:
            [type]: [description]
        """
        logger.info("loading image mask...")
        mask = self.load_image(self.get_setting("mask", None))
        if mask:
            return mask.resize(self.im.size).convert("L")
        return None

    def load_image(self, path):
        """[summary]

        Args:
            path ([type]): [description]

        Returns:
            [type]: [description]
        """
        logger.info("loading image...")
        if path and os.path.exists(path):
            return Image.open(path)
        return None

    def build_font(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        logger.info("buid font mask...")
        font = self.get_setting("font")

        font_size = font.get("size")
        font_file = font.get("file")

        return ImageFont.truetype(font_file, font_size)

    def parse_xy(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        logger.info("parsing xy...")
        return (self.parse_axis(0), self.parse_axis(1))

    # x=0,y=1
    def parse_axis(self, axis):
        """[summary]

        Args:
            axis ([type]): [description]

        Returns:
            [type]: [description]
        """
        logger.info("parsing axis...")
        axis_l = ("x", "y")
        margin_l = ("x_margin", "y_margin")

        param = self.get_setting(axis_l[axis], "center")
        if param == "center":
            return int(self.image.size[axis] / 2) - int(
                self.font.getsize(self.text)[axis] / 2
            )
        if param == "left":
            return self.get_setting(margin_l[axis], 0)
        if param == "right":
            return (
                self.image.size[axis]
                - self.get_setting(margin_l[axis], 0)
                - self.font.getsize(self.text)[axis]
            )
        if param == "up":
            return self.get_setting(margin_l[axis], 0)
        if param == "down":
            return (
                self.image.size[axis]
                - self.get_setting(margin_l[axis], 0)
                - self.font.getsize(self.text)[axis]
            )

        return param + self.get_setting(margin_l[axis], 0)

    def split_text(self, text):
        logger.info("split text...")
        limit = self.get_setting("x_limit", self.image.size[0])
        if self.font.getsize(text)[0] < limit:
            return text

        full_text = []
        
        line = ""
        for word in text.split(" "):
            if len(word) + len(line) < limit - 1:
                line = f"{line} {word} "
            else:
                full_text.append(line)
                line = word
        full_text.append(line)
        return "\n".join(full_text)

    def get_setting(self, setting, default=None):
        return self.settings.get(setting, default)

    def build_settings(self):
        return {
            "xy": self.xy,
            "fill": self.get_setting("fill", "#000000"),
            "font": self.font,
            "spacing": self.get_setting("spacing", 10),
        }
