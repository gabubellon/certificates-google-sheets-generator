import logging
import os

from PIL import Image, ImageDraw, ImageFont


def create(person_name, cert_date):

    logging.info(f"Creating Certicate to {person_name}")
    font_cert = ImageFont.truetype("assets/fonts/VT323-Regular.ttf", 38)
    certificate_imgs = Image.open("assets/imgs/certificate.png")

    draw = ImageDraw.Draw(certificate_imgs)

    draw.text((30, 700), cert_date, ("#ffffff"), font=font_cert)
    draw.text((300, 450), person_name, ("#ffffff"), font=font_cert, spacing=10)

    os.makedirs("certificates", exist_ok=True)

    file_name = "certificates/{}.png".format(person_name.replace(" ", "_"))

    certificate_imgs.save(file_name)

    return file_name
