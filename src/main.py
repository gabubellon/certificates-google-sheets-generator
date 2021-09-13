import sys

from loguru import logger

import certificates
import google_api


def create_certificate(certificate_date):
    logger.info(f"Getting data to certificates")
    values = google_api.read_sheets()
    cert_lists = []

    for item in values:
        try:
            name = " ".join([name.capitalize() for name in item.get("NAME").split()])
            email = item.get("EMAIL")
            file_name = certificates.create(name, certificate_date)
            file_url = google_api.save_file_drive(file_name)
            cert_lists.append([name, email, file_url])
        except:
            logger.info(f"Error or generate certificate")
        

    google_api.write_on_sheets(cert_lists)


if __name__ == "__main__":
    create_certificate(sys.argv[1])
