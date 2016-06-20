from imgurpython import ImgurClient
import os
import logging
import re

IMGUR_ID = os.environ.get("IMGUR_ID")
IMGUR_SECRET = os.environ.get("IMGUR_SECRET")

def clean_path(path):
    return re.sub(r"\W*$", "", re.sub(r"^\W*", '', path))


class Imgur():

    def __init__(self):
        self.imgur_client = ImgurClient(IMGUR_ID, IMGUR_SECRET)
        
    def save_from_url(self, image_url):
        logging.debug("trying to save %s" % image_url)
        response = self.imgur_client.upload_from_url(clean_path(image_url))
        return str(response['link'])

    def save_from_file(self, file_path):
        logging.debug("trying to save file %s" % file_path)
        response = self.imgur_client.upload_from_path(file_path)
        return (str(response['link']))
