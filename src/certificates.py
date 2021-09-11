import os

from loguru import logger
from PIL import Image, ImageDraw, ImageFont


def create(person_name, cert_date):

    logger.info(f"Creating Certicate to {person_name}")
    font_cert = ImageFont.truetype("assets/fonts/VT323-Regular.ttf", 80)
    font_date = ImageFont.truetype("assets/fonts/VT323-Regular.ttf", 40)
    certificate_imgs = Image.open("assets/imgs/certificate.png")

    draw = ImageDraw.Draw(certificate_imgs)

    if len(person_name)>28:
       person_name= f"{person_name.split()[0]} {person_name.split()[-1]}"
    draw.text((0, 450), person_name.center(33), ("#ffffff"), font=font_cert, spacing=10)
    draw.text((150, 700), cert_date, ("#ffffff"), font=font_date)

    os.makedirs("certificates", exist_ok=True)

    file_name = "certificates/{}.png".format(person_name.replace(" ", "_"))

    certificate_imgs.save(file_name)

    return file_name
